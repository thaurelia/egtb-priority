import json
from argparse import ArgumentParser
from pathlib import Path

LINK_ROOT = 'https://tablebase.lichess.ovh/tables/standard/7'
GIGABYTE = 1_000_000_000


def folder_from_egtb_name(name: str) -> str:
    """
    Determine EGTB folder (Xvy_pawn(less|ful)) from EGTB name

    :param name: EGTB name
    """
    l, r = name.split('v')
    prefix = f'{len(l)}v{len(r)}'
    suffix = '_pawnful' if ('P' in l or 'P' in r) else '_pawnless'
    return prefix + suffix


def generate_table(
    key: str, statsfile: Path, linksfolder: Path, threshold: float
) -> list:
    """
    Generate Markdown tables with download links
    from a JSON file with stats.

    :param key: key in cumulative stats
    :param statsfile: input file with stats
    :param linksfolder: folder to store DL lists with links
    :param threshold: threshold for percentage of games
    """

    with open(statsfile) as f:
        data = json.load(f)

    total = data['total_games']

    egtb_orig = data[key]
    tablerows = [
        '|#|Name|No. of games|Percentage|WDL|WDL (cumulative)|Download|WDL+DTZ|WDL+DTZ (cumulative)|Download|',
        '|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|',
    ]
    links_wdl = []
    links_wdl_dtz = []
    cumulative_wdl = 0
    cumulative_wdl_dtz = 0

    with open('filesizes.json') as f:
        filesizes = json.load(f)

    for idx, val in enumerate(egtb_orig.items(), start=1):
        name, amount = val
        percentage = amount / total * 100
        if percentage <= threshold:
            break
        wdl_size = filesizes[name + '.rtbw']
        dtz_size = filesizes[name + '.rtbz']
        cumulative_wdl += wdl_size
        cumulative_wdl_dtz += wdl_size + dtz_size

        wdl_link = f'{LINK_ROOT}/{folder_from_egtb_name(name)}/{name}.rtbw'
        dtz_link = f'{LINK_ROOT}/{folder_from_egtb_name(name)}/{name}.rtbz'

        links_wdl.append(wdl_link)
        wdl_path = f'{key[5:]}/top-{idx}-wdl.txt'
        wdl_store_as = linksfolder.joinpath(wdl_path)
        with open(wdl_store_as, 'w') as f:
            for lnk in links_wdl:
                f.write(lnk + '\n')

        links_wdl_dtz.append(wdl_link)
        links_wdl_dtz.append(dtz_link)
        wdl_dtz_path = f'{key[5:]}/top-{idx}-wdl-dtz.txt'
        wdl_dtz_store_as = linksfolder.joinpath(wdl_dtz_path)
        with open(wdl_dtz_store_as, 'w') as f:
            for lnk in links_wdl_dtz:
                f.write(lnk + '\n')

        tablerows.append(
            f'|{idx}'
            f'|{name}'
            f'|{amount}'
            f'|{percentage:.2f}%'
            f'|{wdl_size / GIGABYTE:.2f} GB'
            f'|{cumulative_wdl / GIGABYTE:.2f} GB'
            f'|[List](../{wdl_store_as})'
            f'|{(wdl_size + dtz_size) / GIGABYTE:.2f} GB'
            f'|{cumulative_wdl_dtz / GIGABYTE:.2f} GB'
            f'|[List](../{wdl_dtz_store_as})'
        )

    return tablerows


def generate_md_file(db: str):
    """
    Generate final Markdown file with tables.

    :param db: name of the database
    """
    statsfile = Path(f'./json_stats/{db}.json')
    linksfolder = Path(f'./download_lists/{db}')
    mdfile = Path(f'./markdown_tables/{db}.md')

    material_diff = generate_table(
        'EGTB_material_diff', statsfile, linksfolder, 0.0995
    )
    most_games = generate_table(
        'EGTB_most_games', statsfile, linksfolder, 0.995
    )

    with open(mdfile, 'w') as f:
        f.write(f'# {db.capitalize()}\n\n')

        f.write('**Least material imbalance**\n')
        for line in material_diff:
            f.write(line + '\n')

        f.write('<br />\n')

        f.write('\n**Most games**\n')
        for line in most_games:
            f.write(line + '\n')


def main():
    ap = ArgumentParser()
    ap.add_argument('db', choices=('caissa', 'mega', 'lichess'))
    args = ap.parse_args()

    generate_md_file(args.db)


if __name__ == '__main__':
    main()
