# egtb-priority
Analyse Lichess game database to prioritise Syzygy EGTBs downloads.

## How it was done

[Analysing 2 billion chess games to determine 7-man Syzygy EGTBs priority](./analysing-lichess-game-database.md) – article about this foray

## TLDR

If you're not interested in technical stuff or assumptions made (details in the article), here are some tables:

- **Least Material Imbalance**: EGTBs are first sorted from most to least balanced in terms of material (e.g. “KRPPvKRP” comes before “KQQQvKPP”) and after that, by number of games descending.
- **Most Games**: EGTBs are sorted by number of games only, descending.

Each table provides some game percentage stats, cumulative sizes for WDL-only and WDL+DTZ downloads and download lists for cumulative packages of each type that you can feed into cURL, wget, aria2c etc.

EGTBs that represent less than 1% (Most Games) or 0.1% (LMI) of games are omitted

**N.B.:** 1 GB = 1,000,000,000 bytes.

- [Mega 2021](./markdown_tables/mega.md)
    * ELO: 2300+
    * Eligible games: 106,009 out of 8,456,509 (**1.25%**)
    * Complex time controls (e.g. `40/9000:16/5400:0`) weren't properly parsed; games were classified as `slow`
    * Latest game: Nov 19, 2020
- [Caissa v2020-11-14](./markdown_tables/caissa.md)
    * ELO: 2300+
    * Eligible games: 92,818 out of 4,266,444 (**2.2%**)
    * Time controls: absent; all eligible games considered `slow`
    * Caissa database contains some games with illegal moves; those were excluded from analysis
- [Lichess (Apr 2021)](./markdown_tables/lichess.md)
    * ELO: 2400+ (Glicko-2)
    * Eligible games: 571,816 out of 2,173,068,876 (**0.026%**)
    * Time controls: all except `bullet`


**Top-10 tables from each DB by least material imbalance**

|#|Mega 2021|Caissa|Lichess|
|:----:|:----:|:----:|:----:|
|1|KRPPvKRP|KRPPvKRP|KRPPvKRP|
|2|KPPPvKPP|KBPPvKBP|KPPPvKPP|
|3|KBPPvKBP|KPPPvKPP|KBPPvKBP|
|4|KNPPvKNP|KNPPvKNP|KNPPvKNP|
|5|KNPPvKBP|KNPPvKBP|KNPPvKBP|
|6|KBPPvKNP|KBPPvKNP|KBPPvKNP|
|7|KQPPvKQP|KQPPvKQP|KBPPvKRP|
|8|KBPPvKRP|KBPPvKRP|KPPPvKBP|
|9|KNPPvKRP|KNPPvKRP|KPPPvKNP|
|10|KPPPvKBP|KPPPvKBP|KNPPvKRP|


## Usage

If you want to recalculate these tables with your own set of parameters (e.g. changing ELO thresholds, own DB etc.):

- 500+ GB of space (if using full compressed Lichess DB)
    - Due to `egtb.py` being bottlenecked by IO (i.e. parsing big PGNs, especially compressed) rather than games analysis routines, I recommend splitting work between different script instances / machines if ones DB exceeds, say, 50GB compressed.
    - If one can afford space in case of large DBs, unpacking with `pbzip2` (much faster than `bunzip2`) and running `egtb.py` individually over uncompressed PGNs is about 2-3 times faster than using compressed `bz2` ones. Results then can be combined with `updatestats.py`
- A decent machine; also, not tested on Windows so good luck
- Python 3.6+
- `pip install -r requirements.txt`

```
$ python3 egtb.py -h
usage: egtb.py [-h] [--loelo LOELO] [--hielo HIELO] [--exclude [EXCLUDE [EXCLUDE ...]]] [--captures CAPTURES] [--sort-by-material-diff] path

positional arguments:
  path                  Path to DB file or folder with multiple files

optional arguments:
  -h, --help            show this help message and exit
  --loelo LOELO         Lower ELO threshold
  --hielo HIELO         Higher ELO threshold
  --exclude [EXCLUDE [EXCLUDE ...]]
                        Exclude certain time controls from analysis, separated by space. Available options: bullet, blitz, rapid, slow
  --captures CAPTURES   Number of captures to reach desired positions. Default: 25 (7-man)
  --sort-by-material-diff
                        Sort EGTB results by material difference (least to most)
```

**Usage example:** analyse only rapid and slow games with both players over 2100 ELO:

`python3 egtb.py /path/to/downloaded/lichessdb --loelo 2100 --exclude bullet blitz --sort-by-material-diff`