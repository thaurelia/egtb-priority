"""
    updatestats.py
    ~~~~
    Tool to combine several stats file into one
"""

import json
from argparse import ArgumentParser
from collections import Counter, defaultdict
from datetime import datetime as dt
from pathlib import Path
from typing import Dict, List


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


def combine(files: List[Path], outfile: Path):
    """
    Calculate cumulative statistics from several JSON files.

    :param files: list with filepaths
    :param outfile: output file to save to
    """
    result = {
        'created': dt.isoformat(dt.now()),
        'total_games': 0,
        'timecontrol': defaultdict(int),
    }
    most_games = defaultdict(int)
    for file in files:
        with open(file) as f:
            data = json.load(f)

        # Total games
        result['total_games'] += data['total_games']

        # Timecontrol
        for k, v in data['timecontrol'].items():
            result['timecontrol'][k] += v

        # EGTBs
        for k, v in data['EGTB_most_games'].items():
            most_games[k] += v

    # Material diff
    result['EGTB_material_diff'] = material_diff_sort(most_games)

    # Most games, sorted by number of games
    result['EGTB_most_games'] = dict(Counter(most_games).most_common())

    # Save
    with open(outfile, 'w') as f:
        json.dump(result, f)


def main():
    ap = ArgumentParser()
    ap.add_argument(
        'files',
        nargs='*',
        default=[],
        help='List of files to combine',
    )

    ap.add_argument(
        '--outfile',
        type=Path,
        default=Path.cwd().joinpath('cumulative.json'),
        help='Output file',
    )

    args = ap.parse_args()

    combine(args.files, args.outfile)


if __name__ == '__main__':
    main()
