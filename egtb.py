import bz2
import io
import json
import logging
import multiprocessing as mp
import sys
from argparse import ArgumentParser
from collections import Counter, defaultdict
from datetime import datetime as dt
from itertools import count
from pathlib import Path
from typing import (
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
)

import chess.pgn

logging.getLogger("chess.pgn").setLevel(logging.CRITICAL)

# ---- Constants and shared values ----
# Number of captures to reach 7-man position
# = 32 (starting pieces) - 7 (end pieces) == 25
REQUIRED_CAPTURES_7_MAN = 25

# Piece order for EGTB names
EGTB_PIECE_ORDER = {
    'K': 0,
    'Q': 1,
    'R': 2,
    'B': 3,
    'N': 4,
    'P': 5,
}

# ---- End of: Constants and shared values ----


# ---- DB files pasing routines ----
def next_pgn(fiter: Iterator) -> List[str]:
    """
    Get next 1-game PGN from a PGN database file.

    :param fiter: file iterator
    """
    pgn = []
    while True:
        # Header doesn't have a fixed size
        # Retrieving header line-by-line
        line = next(fiter)
        if line.startswith('['):
            pgn.append(line.strip())
            continue  # proceed getting the next line

        # Header finished

        # PGNs have empty line between header and SAN
        # that was already consumed by `next(fiter)`;
        # Next line in PGN contains game log in SAN
        # (Standard/Short Algebraic Notation)

        # For PGNs that have SAN separated over several lines
        # (Caissa, Mega), run an inside loop that collects this SAN log
        san = ''
        while True:
            line = next(fiter).strip()
            if not line:
                # Consumed a line between SAN and next PGN header;
                # can return complete PGN
                break
            san += line + ' '

        pgn.append(san.strip())

        return pgn


def get_line(
    predicate: Callable[[str], bool], iterable: Union[Iterable, Iterator]
):
    """
    Get line from iterable object that matches the predicate.

    :param predicate: callable predicate to use for matching
    :param iterable: Iterable/Iterator object to search
    """
    for line in iterable:
        if predicate(line):
            return line
    raise RuntimeError('predicate not matched')


def is_abandoned(pgn: List[str]) -> bool:
    """
    Check if game was abandoned (<= 2 half-moves played).

    :param pgn: list with parsed PGN
    """
    try:
        get_line(lambda x: x == '[Termination "Abandoned"]', pgn)
        return True
    except RuntimeError:
        return False


def is_in_elo_range(pgn: List[str], loelo: int, hielo: int) -> bool:
    """
    Determine if both players in the 1-game PGN fall into ELO range.

    :param pgn: list with parsed PGN
    :param loelo: lower ELO threshold
    :param hielo: higher ELO threshold
    """
    # ELO entries are placed on the adjacent lines
    # so it's sufficient to find EloWhite and
    # wind the iterator once more to get BlackElo
    i = iter(pgn)

    try:
        w_elo_line = get_line(lambda x: x.startswith('[WhiteElo'), i)
    except RuntimeError:
        # For PGN files that are missing ELO header
        # Treat this games as those which don't fall in the ELO range
        return False

    # LiChess DB files always contain EloWhite and EloBlack
    # but in some cases, ELO values are unknown.
    # Treat these values as those which don't fall in the ELO range
    try:
        w_elo = int(w_elo_line[11:-2])
    except ValueError:
        return False

    b_elo_line = next(i)
    try:
        b_elo = int(b_elo_line[11:-2])
    except ValueError:
        return False

    return (loelo <= w_elo <= hielo) and (loelo <= b_elo <= hielo)


def get_time_control(pgn: List[str]) -> str:
    """
    Determine time control used in 1-game PGN.

    :param pgn: list with parsed PGN
    """
    try:
        tc_line = get_line(lambda x: x.startswith('[TimeControl'), pgn)
        tc = tc_line[14:-2]
    except RuntimeError:
        # Treat missing time control as slow game
        return 'slow'

    if tc == '-':
        # Infinite time or 1d+ per move (Lichess)
        return 'slow'

    # Time control format: <starting_time>+<increment>
    # Example: 60+0 (1-minute bullet)
    try:
        start, increment = tc.split('+')
        start = int(start)
    except ValueError:
        # Too lazy to parse different Mega timecontrol formats :)
        return 'slow'
    if start <= 60:
        # 1 minute or less
        return 'bullet'
    elif start <= 300:
        # Between 1 and 5 minutes
        return 'blitz'
    elif start <= 900:
        # Between 5 and 15 minutes
        return 'rapid'
    else:
        # More than 15 minutes
        return 'slow'


def parse_compressed_pgn(
    filepath: Path,
    queue: mp.Queue,
    loelo: int,
    hielo: int,
    exclude: List[str],
    workers: int,
):
    """
    Extract games that fall into [loelo:hielo] range from (compressed) PGN.

    :param filepath: path to (compressed) PGN file to analyse
    :param queue: queue to store 1-game PGNs for processing
    :param loelo: lower ELO threshold
    :param hielo: higher ELO threshold
    :param exclude: list with time controls to exclude
    :param workers: number of workers that will consume the queue
    """
    # Check path suffix to determine how to read the file
    suffix = filepath.suffix
    if suffix == '.bz2':
        openfunc, mode = bz2.open, 'rt'
    # Leave the ability to operate on single unpacked PGN file
    elif suffix == '.pgn':
        openfunc, mode = open, 'r'
    else:
        raise RuntimeError(f'Unsupported extension: {suffix}')

    game_counter = count(1)
    # Process file
    with openfunc(filepath, mode, encoding='latin-1') as f:
        while True:
            try:
                pgn = next_pgn(f)
                sys.stdout.write(f'Processed game #{next(game_counter):,}\r')
            except StopIteration:
                # EOF
                break

            # Check the game for ELO range
            # Skip abandoned games
            # Skip excluded time control types
            if is_abandoned(pgn):
                continue
            if not is_in_elo_range(pgn, loelo, hielo):
                continue

            tc = get_time_control(pgn)
            if tc in exclude:
                continue

            # Save game for processing
            queue.put((pgn, tc))

    # Finished file processing
    # Notify all workers by putting in DONE message for each
    for _ in range(workers):
        queue.put('DONE')


# ---- End of: DB files parsing routines ----

# ---- Game analysis routines ----
def egtb_name_from_pieces(pieces: Tuple[str]) -> str:
    """
    Construct EGTB name from the pieces configuration.

    :param pieces: tuple with FEN pieces names
    """
    # Gather pieces for White and Black to construct the name:
    # "ALLCAPS(<more_pieces>)vALLCAPS(<less_pieces>)"
    # Inside each section, pieces are sorted
    # in the following order: KQRBNP
    white_pieces, black_pieces = [], []
    for p in pieces:
        if p.isupper():
            white_pieces.append(p)
        else:
            black_pieces.append(p.upper())

    white = ''.join(sorted(white_pieces, key=EGTB_PIECE_ORDER.get))
    black = ''.join(sorted(black_pieces, key=EGTB_PIECE_ORDER.get))

    if len(white) > len(black):
        return f'{white}v{black}'
    else:
        return f'{black}v{white}'


def play_game(pgn: str, captures: int) -> Optional[str]:
    """
    Process PGN with a move generator to reach needed position.
    Determine EGTB to use based on the pieces left.

    :param pgn: PGN to analyze
    :param captures: number of captures to reach
    """
    # python-chess primary interface loads SAN from a PGN file.
    # Wrap SAN string into StringIO for compatibility with that interface
    pgn = '\n'.join(pgn)
    game = chess.pgn.read_game(io.StringIO(pgn))
    board = game.board()

    # To reach a position, `captures` number of half-moves has to be made.
    # Furthermore, the first capture can only happen on half-move #3
    # (e.g. Scandinavian Defense – 1. e4 d5 2. exd5)
    # This means that the theoretical lower limit of half-moves
    # to reach a `captures` number of captures is at least `captures` + 2.
    # Play mainline for this amount of half-moves before starting analysis.
    mainline = iter(game.mainline_moves())
    for _ in range(captures + 2):
        try:
            board.push(next(mainline))
        except StopIteration:
            # Game shorter than required number of moves to reach 7-piece
            return None

    # From this point, monitor the number of pieces on the board
    while len(board.piece_map()) != 32 - captures:
        try:
            board.push(next(mainline))
        except StopIteration:
            # 7-piece never reached
            return None

    if game.errors:
        # python-chess supresses errors but collects them;
        # if game is invalid, exclude it from analysis
        return None

    # Save current piece composition and make another half-move.
    # If the next half-move reduces the number of pieces on the board,
    # consider this position as being “trivialised” by a lower-order EGTB.
    reached = tuple(p.symbol() for p in board.piece_map().values())

    try:
        board.push(next(mainline))
    except StopIteration:
        # This position is the last one in the PGN.
        # Either checkmate or resignation happened.
        # Consider this position unsuitable for further analysis
        return None

    if len(board.piece_map()) < len(reached):
        # Number of pieces was reduced.
        # Consider this position as one that can be trivialised
        return None

    # Position is sutable for statistics
    return egtb_name_from_pieces(reached)


def analyse_game(
    in_queue: mp.Queue,
    out_queue: mp.Queue,
    captures: int,
):
    """
    Analyse games in PGN queue.
    Determine the ones that reach (non-trivial) 7-man position
    and find out the EGTB that will be used to analyse this position.

    :param in_queue: queue with PGNs
    :param out_queue: queue for analysis results
    :param captures: number of captures to reach
    """
    pair = None
    while True:
        pair = in_queue.get()
        if pair == 'DONE':
            # End of input queue
            break
        pgn, tc = pair

        # Pass the SAN to move generator to determine EGTB name
        # for the position after `captures` number of captures
        egtb = play_game(pgn, captures)
        if egtb is None:
            # EGTB was trivialised or unsuitable.
            # Get next game to analyse.
            continue

        # Send EGTB name and time control
        # to statistics queue
        out_queue.put((tc, egtb))

    # Worker finished processing games in queue.
    # Put the DONE message in the results queue
    # to signal result processing worker that
    # this worker has ended processing.
    out_queue.put('DONE')


# ---- End of: Game analysis routines ----

# ---- Statistics and multiprocessing routines ----
def collect_results(filepath: Path, queue: mp.Queue, workers: int):
    """
    Process results queue and gather statistics.

    :param filepath: path to PGN file; used for choosing JSON name
    :param queue: results queue to process
    :param workers: number of workers; used to determine end-of-queue
    """
    cnt = 0
    timecontrol, egtb = defaultdict(int), defaultdict(int)

    # Process queue until %workers% number of “DONE” are met
    while cnt != workers:
        pair = queue.get()
        if pair == 'DONE':
            cnt += 1
        else:
            # tuple of (timecontrol, EGTB string)
            tc, eg = pair
            timecontrol[tc] += 1
            egtb[eg] += 1

    # Save results to a JSON file
    # collections.Counter is used to put the most frequent EGTB names first
    stats = {
        'timecontrol': timecontrol,
        'EGTB': dict(Counter(egtb).most_common()),
    }

    with open(filepath.with_suffix('.stats.json'), 'w') as f:
        json.dump(stats, f)


def calculate_material_diff(pieces: str) -> int:
    """
    Calculate material difference between two sides.

    :param pieces: EGTB name
    """
    piece_values = {
        'K': 0,  # always present, hence, irrelevant to the result
        'P': 1,
        'N': 3,
        'B': 3,
        'R': 5,
        'Q': 9,
    }

    # EGTB name format: <pieces>v<pieces>
    a, b = pieces.split('v')
    mat_a = sum(piece_values[p] for p in a)
    mat_b = sum(piece_values[p] for p in b)
    return abs(mat_a - mat_b)


def material_diff_sort(egtbs: Dict[str, int]) -> Dict[str, int]:
    """
    Sort EGTB dict by material difference and number of games.

    :param egtbs: dict to sort
    """

    def keyfunc(pair):
        name, cnt = pair
        # Negate count so the bigger number is first
        return calculate_material_diff(name), -cnt

    return dict(sorted(egtbs.items(), key=keyfunc))


def collect_cumulative_results(path: Path, sort_by_material_diff: bool):
    """
    Accumulate results from multiple files.
    Optional: add alternative EGTB statistics where EGTBs are sorted
    by material difference (least to most) first
    and then by number of games (most to least)

    :param path: path that was analysed
    :param sort_by_material_diff: perform material difference sort
    """
    # Check whether directory or a single file were analysed
    if path.is_dir():
        stats_files = path.glob('*.stats.json')
        outfolder = path
    else:
        stats_files = (path.with_suffix('.stats.json'),)
        outfolder = path.parent

    # Accumulate statistics about EGTB and time controls
    timecontrols, egtbs = defaultdict(int), defaultdict(int)
    for file in stats_files:
        with open(file) as f:
            data = json.load(f)
        for k, v in data['timecontrol'].items():
            timecontrols[k] += v
        for k, v in data['EGTB'].items():
            egtbs[k] += v

    # Calculate total games analysed
    total_games = sum(timecontrols.values())

    cumulative = {
        'created': dt.isoformat(dt.now()),
        'total_games': total_games,
        'timecontrol': timecontrols,
    }
    if sort_by_material_diff:
        # Appending this to the dict first in case it exists
        egtb_alt = material_diff_sort(egtbs)
        cumulative['EGTB_material_diff'] = egtb_alt

    cumulative['EGTB_most_games'] = dict(Counter(egtbs).most_common())

    with open(outfolder.joinpath('cumulative-stats.json'), 'w') as f:
        json.dump(cumulative, f)


def analyse(
    filepath: Path,
    loelo: int,
    hielo: int,
    exclude: List[str],
    captures: int,
):
    """
    Launch a multiprocess analysis over compressed PGN file.

    :param filepath: path to compressed PGN file
    :param loelo: Lower ELO threshold for both players
    :param hielo: Higher ELO threshold for both players
    :param exclude: list with time controls to exclude
    :param captures: number of captures to reach
    """
    # Get CPU count to determine the amount of parallel processes
    cpus = mp.cpu_count()

    # Workers:
    # - 1 worker to accumulate statistics
    # - at least 1 worker to parse compressed PGNs
    # - the rest are workers that analyse games but no less than 1
    MAX_ANALYSIS_WORKERS = max(2, cpus - 2)

    # Queues:
    # - 1 queue to accumulate the final results
    # - 1 queue to accumulate 1-game PGNs parsed from the input file
    pgn_queue = mp.Queue(10_000)
    results_queue = mp.Queue(1_000)

    # Create processes
    processes = []

    # - results collector
    processes.append(
        mp.Process(
            target=collect_results,
            args=(filepath, results_queue, MAX_ANALYSIS_WORKERS),
        )
    )

    # - file parser
    processes.append(
        mp.Process(
            target=parse_compressed_pgn,
            args=(
                filepath,
                pgn_queue,
                loelo,
                hielo,
                exclude,
                MAX_ANALYSIS_WORKERS,
            ),
        )
    )

    # - games analysis
    processes.extend(
        [
            mp.Process(
                target=analyse_game, args=(pgn_queue, results_queue, captures)
            )
            for _ in range(MAX_ANALYSIS_WORKERS)
        ]
    )

    # Launch
    for p in processes:
        p.start()

    for p in processes:
        p.join()


# ---- End of: Statistics and multiprocessing routines ----


def main():
    ap = ArgumentParser()
    ap.add_argument(
        'path', type=Path, help='Path to DB file or folder with multiple files'
    )
    ap.add_argument(
        '--loelo', type=int, default=2000, help='Lower ELO threshold'
    )
    ap.add_argument(
        '--hielo', type=int, default=4000, help='Higher ELO threshold'
    )
    ap.add_argument(
        '--exclude',
        nargs='*',
        default=[],
        help=(
            'Exclude certain time controls from analysis, separated by space. '
            'Available options: bullet, blitz, rapid, slow'
        ),
    )
    ap.add_argument(
        '--captures',
        type=int,
        default=REQUIRED_CAPTURES_7_MAN,
        help=(
            'Number of captures to reach desired positions. '
            'Default: 25 (7-man)'
        ),
    )
    ap.add_argument(
        '--sort-by-material-diff',
        action='store_true',
        help='Sort EGTB results by material difference (least to most)',
    )

    args = ap.parse_args()

    if args.loelo >= args.hielo:
        print(
            'Lower ELO threshold cannot be higher than'
            ' or equal to higher ELO threshold.'
        )
        sys.exit(1)

    if not 0 < args.captures < (32 - 2):
        print('Invalid number of captures')
        sys.exit(2)

    if args.path.is_dir():
        files = tuple(args.path.glob('*.pgn.bz2'))
    else:
        files = (args.path,)

    total = len(files)

    for idx, f in enumerate(files, start=1):
        print(
            f'Analysing {f.name} ({idx}/{total}) '
            f'[size:{f.stat().st_size / 1_000_000: .1f} MB]'
        )
        analyse(
            f,
            args.loelo,
            args.hielo,
            args.exclude,
            args.captures,
        )

    print('Computing cumulative results…')
    collect_cumulative_results(args.path, args.sort_by_material_diff)


if __name__ == '__main__':
    main()
