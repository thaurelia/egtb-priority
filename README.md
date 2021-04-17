# egtb-priority
Analyse Lichess game database to prioritise Syzygy EGTBs downloads.

## How it was done

- [Analysing 2 billion chess games to determine 7-man Syzygy EGTBs priority](./analysing-lichess-game-database.md) – article about this foray
- [egtb.py]()
    * Machine: cloud instance with 8 dedicated AMD EPYC 7003 Cores + 600 GB of network storage, Python 3.8.5
    * Time: 3d 8h 46m. I didn't bother with speed too much. Also, what network storage bottlenecks?
    * Cost: <10€. Yay for cloud computing!
    * Parameters: ELO (Glicko-2) thresholds: 2000 lo, 4000 hi; all time controls (bullet, blitz, rapid, slow)

## TLDR

If you're not interested in technical stuff or assumptions made (details in the article), here are some tables:

- **Least Material Imbalance**: EGTBs are first sorted from most to least balanced in terms of material (e.g. “KRPPvKRP” comes before “KQQQvKPP”) and after that, by number of games descending.
- **Most Games**: EGTBs are sorted by number of games only, descending.

Each table provides some game percentage stats, cumulative sizes for WDL-only and WDL+DTZ downloads and download lists for cumulative packages of each type that you can feed into cURL, wget, aria2c etc.

EGTBs that represent less than 1% (Most Games) or 0.1% (LMI) of games are omitted

**N.B.:** 1 GB = 1,000,000,000 bytes.

### Lichess, 2000+ ELO (Glicko-2)

|Time Control|No. of games|
|:----|----:|
|Bullet|12,349,207|
|Blitz|10,596,491|
|Rapid|966,949|
|Slow (30min+, correspondence)|38,294|
|Total|23,950,941|

<br />

**Least material imbalance**

|#|Name|No. of games|Percentage|WDL|WDL (cumulative)|Download (WDL, cumulative)|WDL+DTZ|WDL+DTZ (cumulative)|Download (WDL + DTZ, cumulative)|
|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|
|1|KRPPvKRP|3091564|12.91%|23.26 GB|23.26 GB|[List](./download_lists/material_diff/top-1-wdl.txt)|32.71 GB|32.71 GB|[List](./download_lists/material_diff/top-1-wdl-dtz.txt)
|2|KPPPvKPP|2954602|12.34%|2.11 GB|25.37 GB|[List](./download_lists/material_diff/top-2-wdl.txt)|2.20 GB|34.90 GB|[List](./download_lists/material_diff/top-2-wdl-dtz.txt)
|3|KBPPvKBP|676799|2.83%|30.75 GB|56.12 GB|[List](./download_lists/material_diff/top-3-wdl.txt)|36.31 GB|71.21 GB|[List](./download_lists/material_diff/top-3-wdl-dtz.txt)
|4|KPPPvKBP|376071|1.57%|7.58 GB|63.70 GB|[List](./download_lists/material_diff/top-4-wdl.txt)|9.02 GB|80.23 GB|[List](./download_lists/material_diff/top-4-wdl-dtz.txt)
|5|KBPPvKRP|332809|1.39%|31.61 GB|95.31 GB|[List](./download_lists/material_diff/top-5-wdl.txt)|44.47 GB|124.70 GB|[List](./download_lists/material_diff/top-5-wdl-dtz.txt)
|6|KNPPvKNP|328706|1.37%|29.09 GB|124.39 GB|[List](./download_lists/material_diff/top-6-wdl.txt)|35.62 GB|160.32 GB|[List](./download_lists/material_diff/top-6-wdl-dtz.txt)
|7|KNPPvKBP|310209|1.30%|30.96 GB|155.35 GB|[List](./download_lists/material_diff/top-7-wdl.txt)|38.06 GB|198.38 GB|[List](./download_lists/material_diff/top-7-wdl-dtz.txt)
|8|KBPPvKNP|291995|1.22%|28.73 GB|184.08 GB|[List](./download_lists/material_diff/top-8-wdl.txt)|35.20 GB|233.58 GB|[List](./download_lists/material_diff/top-8-wdl-dtz.txt)
|9|KPPPvKNP|269288|1.12%|6.68 GB|190.76 GB|[List](./download_lists/material_diff/top-9-wdl.txt)|7.58 GB|241.16 GB|[List](./download_lists/material_diff/top-9-wdl-dtz.txt)
|10|KNPPvKRP|189556|0.79%|29.91 GB|220.67 GB|[List](./download_lists/material_diff/top-10-wdl.txt)|42.04 GB|283.20 GB|[List](./download_lists/material_diff/top-10-wdl-dtz.txt)
|11|KQPPvKQP|175622|0.73%|22.63 GB|243.30 GB|[List](./download_lists/material_diff/top-11-wdl.txt)|35.56 GB|318.76 GB|[List](./download_lists/material_diff/top-11-wdl-dtz.txt)
|12|KBPPPvKR|95507|0.40%|6.90 GB|250.20 GB|[List](./download_lists/material_diff/top-12-wdl.txt)|9.59 GB|328.35 GB|[List](./download_lists/material_diff/top-12-wdl-dtz.txt)
|13|KRPPvKRB|91089|0.38%|28.69 GB|278.89 GB|[List](./download_lists/material_diff/top-13-wdl.txt)|34.56 GB|362.91 GB|[List](./download_lists/material_diff/top-13-wdl-dtz.txt)
|14|KRPPvKRN|83573|0.35%|27.83 GB|306.72 GB|[List](./download_lists/material_diff/top-14-wdl.txt)|34.39 GB|397.31 GB|[List](./download_lists/material_diff/top-14-wdl-dtz.txt)
|15|KPPPPvKR|72053|0.30%|1.76 GB|308.48 GB|[List](./download_lists/material_diff/top-15-wdl.txt)|2.41 GB|399.72 GB|[List](./download_lists/material_diff/top-15-wdl-dtz.txt)
|16|KNPPPvKR|52021|0.22%|7.31 GB|315.80 GB|[List](./download_lists/material_diff/top-16-wdl.txt)|10.05 GB|409.76 GB|[List](./download_lists/material_diff/top-16-wdl-dtz.txt)
|17|KPPPPvKB|43646|0.18%|0.63 GB|316.43 GB|[List](./download_lists/material_diff/top-17-wdl.txt)|0.71 GB|410.47 GB|[List](./download_lists/material_diff/top-17-wdl-dtz.txt)
|18|KRBPvKRB|43398|0.18%|80.28 GB|396.71 GB|[List](./download_lists/material_diff/top-18-wdl.txt)|103.18 GB|513.65 GB|[List](./download_lists/material_diff/top-18-wdl-dtz.txt)
|19|KBNPvKRP|38557|0.16%|82.92 GB|479.63 GB|[List](./download_lists/material_diff/top-19-wdl.txt)|115.81 GB|629.46 GB|[List](./download_lists/material_diff/top-19-wdl-dtz.txt)
|20|KPPPPvKN|38362|0.16%|0.44 GB|480.07 GB|[List](./download_lists/material_diff/top-20-wdl.txt)|0.50 GB|629.96 GB|[List](./download_lists/material_diff/top-20-wdl-dtz.txt)
|21|KRRPvKRR|27102|0.11%|20.65 GB|500.72 GB|[List](./download_lists/material_diff/top-21-wdl.txt)|31.02 GB|660.98 GB|[List](./download_lists/material_diff/top-21-wdl-dtz.txt)
|22|KRNPvKRN|24793|0.10%|74.08 GB|574.80 GB|[List](./download_lists/material_diff/top-22-wdl.txt)|103.32 GB|764.30 GB|[List](./download_lists/material_diff/top-22-wdl-dtz.txt)

<br />

**Most games**

|#|Name|No. of games|Percentage|WDL|WDL (cumulative)|Download (WDL, cumulative)|WDL+DTZ|WDL+DTZ (cumulative)|Download (WDL + DTZ, cumulative)|
|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|
|1|KRPPvKRP|3091564|12.91%|23.26 GB|23.26 GB|[List](./download_lists/most_games/top-1-wdl.txt)|32.71 GB|32.71 GB|[List](./download_lists/most_games/top-1-wdl-dtz.txt)
|2|KPPPvKPP|2954602|12.34%|2.11 GB|25.37 GB|[List](./download_lists/most_games/top-2-wdl.txt)|2.20 GB|34.90 GB|[List](./download_lists/most_games/top-2-wdl-dtz.txt)
|3|KRPPvKPP|999843|4.17%|5.05 GB|30.42 GB|[List](./download_lists/most_games/top-3-wdl.txt)|6.18 GB|41.08 GB|[List](./download_lists/most_games/top-3-wdl-dtz.txt)
|4|KBPPvKPP|869527|3.63%|7.97 GB|38.40 GB|[List](./download_lists/most_games/top-4-wdl.txt)|9.03 GB|50.12 GB|[List](./download_lists/most_games/top-4-wdl-dtz.txt)
|5|KRPPPvKP|774795|3.23%|1.09 GB|39.49 GB|[List](./download_lists/most_games/top-5-wdl.txt)|1.24 GB|51.36 GB|[List](./download_lists/most_games/top-5-wdl-dtz.txt)
|6|KRPPPvKR|739299|3.09%|1.08 GB|40.57 GB|[List](./download_lists/most_games/top-6-wdl.txt)|2.45 GB|53.81 GB|[List](./download_lists/most_games/top-6-wdl-dtz.txt)
|7|KBPPvKBP|676799|2.83%|30.75 GB|71.31 GB|[List](./download_lists/most_games/top-7-wdl.txt)|36.31 GB|90.12 GB|[List](./download_lists/most_games/top-7-wdl-dtz.txt)
|8|KPPPPvKP|665772|2.78%|0.34 GB|71.65 GB|[List](./download_lists/most_games/top-8-wdl.txt)|0.35 GB|90.46 GB|[List](./download_lists/most_games/top-8-wdl-dtz.txt)
|9|KNPPvKPP|569516|2.38%|9.69 GB|81.34 GB|[List](./download_lists/most_games/top-9-wdl.txt)|11.24 GB|101.70 GB|[List](./download_lists/most_games/top-9-wdl-dtz.txt)
|10|KQPPvKPP|566557|2.37%|2.11 GB|83.45 GB|[List](./download_lists/most_games/top-10-wdl.txt)|2.54 GB|104.25 GB|[List](./download_lists/most_games/top-10-wdl-dtz.txt)
|11|KBPPPvKP|545210|2.28%|1.49 GB|84.94 GB|[List](./download_lists/most_games/top-11-wdl.txt)|1.63 GB|105.88 GB|[List](./download_lists/most_games/top-11-wdl-dtz.txt)
|12|KPPPvKRP|475001|1.98%|4.65 GB|89.59 GB|[List](./download_lists/most_games/top-12-wdl.txt)|6.48 GB|112.36 GB|[List](./download_lists/most_games/top-12-wdl-dtz.txt)
|13|KQPPPvKP|447438|1.87%|0.19 GB|89.77 GB|[List](./download_lists/most_games/top-13-wdl.txt)|0.26 GB|112.61 GB|[List](./download_lists/most_games/top-13-wdl-dtz.txt)
|14|KPPPvKBP|376071|1.57%|7.58 GB|97.36 GB|[List](./download_lists/most_games/top-14-wdl.txt)|9.02 GB|121.63 GB|[List](./download_lists/most_games/top-14-wdl-dtz.txt)
|15|KBPPvKRP|332809|1.39%|31.61 GB|128.97 GB|[List](./download_lists/most_games/top-15-wdl.txt)|44.47 GB|166.10 GB|[List](./download_lists/most_games/top-15-wdl-dtz.txt)
|16|KNPPvKNP|328706|1.37%|29.09 GB|158.05 GB|[List](./download_lists/most_games/top-16-wdl.txt)|35.62 GB|201.72 GB|[List](./download_lists/most_games/top-16-wdl-dtz.txt)
|17|KRPPPPvK|321379|1.34%|0.03 GB|158.08 GB|[List](./download_lists/most_games/top-17-wdl.txt)|0.04 GB|201.76 GB|[List](./download_lists/most_games/top-17-wdl-dtz.txt)
|18|KNPPPvKP|315025|1.32%|1.73 GB|159.81 GB|[List](./download_lists/most_games/top-18-wdl.txt)|1.92 GB|203.68 GB|[List](./download_lists/most_games/top-18-wdl-dtz.txt)
|19|KNPPvKBP|310209|1.30%|30.96 GB|190.77 GB|[List](./download_lists/most_games/top-19-wdl.txt)|38.06 GB|241.74 GB|[List](./download_lists/most_games/top-19-wdl-dtz.txt)
|20|KRPPvKBP|302241|1.26%|11.44 GB|202.20 GB|[List](./download_lists/most_games/top-20-wdl.txt)|15.68 GB|257.42 GB|[List](./download_lists/most_games/top-20-wdl-dtz.txt)
|21|KBPPvKNP|291995|1.22%|28.73 GB|230.93 GB|[List](./download_lists/most_games/top-21-wdl.txt)|35.20 GB|292.62 GB|[List](./download_lists/most_games/top-21-wdl-dtz.txt)
|22|KRBPvKRP|284899|1.19%|48.38 GB|279.31 GB|[List](./download_lists/most_games/top-22-wdl.txt)|92.45 GB|385.07 GB|[List](./download_lists/most_games/top-22-wdl-dtz.txt)
|23|KPPPvKNP|269288|1.12%|6.68 GB|285.99 GB|[List](./download_lists/most_games/top-23-wdl.txt)|7.58 GB|392.65 GB|[List](./download_lists/most_games/top-23-wdl-dtz.txt)
|24|KRBPPvKP|245476|1.02%|3.07 GB|289.06 GB|[List](./download_lists/most_games/top-24-wdl.txt)|3.91 GB|396.56 GB|[List](./download_lists/most_games/top-24-wdl-dtz.txt)


## Usage

If you're feeling adventurous or want to recalculate these tables with your own set of parameters (e.g. excluding bullet games, changing ELO thresholds, own DB etc.):

- 500+ GB of space (if using full compressed Lichess DB)
- A decent machine; also, not tested on Windows so good luck
- Python3.6+
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