"""Versione 4: corregge la mappatura tra codici NOC (CIO) e codici ISO3 (World Bank).

Problemi della versione 3 risolti qui:

1. I file in ``data/csv_wb_paesi`` sono nominati con codici **ISO3** (NLD, DNK, BGR...),
   mentre il medagliere usa codici **NOC** (NED, DEN, BUL...). La v3 li confrontava come
   stringhe: per ~42 paesi la riga-medagliere usciva senza indicatori E veniva generata
   una riga extra a zero medaglie con il codice ISO3 -> duplicati a valle.
2. Falsi amici: BRN e' il Bahrain nel mondo NOC ma il Brunei in ISO3. La v3 agganciava
   gli indicatori del Brunei alle medaglie del Bahrain.
3. Il medagliere codifica l'Unione Sovietica come ``RUS`` + country "Soviet Union":
   la v3 le attaccava gli indicatori della sola Federazione Russa.
4. Le righe extra a zero medaglie erano generate con codici ISO3 invece che NOC.

La correzione centrale e' la tabella ``NOC_TO_ISO3``: ogni NOC viene risolto
esplicitamente nel codice ISO3 del file World Bank corrispondente (o in ``None``
quando il dato non esiste, come per l'URSS). Tutte le decisioni di mappatura
finiscono nel report per essere verificabili.
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_MAIN_FILE = DEFAULT_DATA_DIR / "csv_olimpiadi" / "Olympic_Medal_Tally_History_definitivo.csv"
DEFAULT_SUMMARY_FILE = DEFAULT_DATA_DIR / "csv_olimpiadi" / "Olympic_Games_Summary.csv"
DEFAULT_CLEAN_DIR = DEFAULT_DATA_DIR / "csv_wb_paesi"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "test2"
DEFAULT_YEARS_TO_AGGREGATE = 4

OUTPUT_CSV_NAME = "olympic_medals_with_socioeconomic_indicators_4.csv"
REPORT_NAME = "missing_data_report_4.txt"

REQUIRED_MAIN_COLUMNS = {"edition", "year", "country", "country_noc", "gold", "silver", "bronze", "total"}
REQUIRED_SUMMARY_COLUMNS = {"edition", "year", "country_noc", "city"}
MEDAL_COLUMNS = ["gold", "silver", "bronze", "total"]
OLYMPIC_PLACE_COLUMNS = ["paese_olimpiade", "citta_olimpiade"]
FIXED_NEW_ROW_COLUMNS = {"edition", "year", "country_noc", "gold", "silver", "bronze", "total"}

# ---------------------------------------------------------------------------
# Correzioni al medagliere in input.
# Il tally usa il codice RUS anche per le righe dell'Unione Sovietica: le
# rinominiamo URS, cosi' NON ereditano gli indicatori della Federazione Russa.
# La chiave e' (country_noc, country) per non toccare le righe russe corrette.
# ---------------------------------------------------------------------------
TALLY_NOC_FIXES = {
    ("RUS", "Soviet Union"): "URS",
}

# ---------------------------------------------------------------------------
# Mappatura NOC (CIO) -> ISO3 (nome file World Bank).
# - I NOC identici al proprio ISO3 (ITA, FRA, USA...) non servono qui: vale
#   l'identita', ma SOLO se il NOC non compare in questa tabella.
# - ``None`` = nessun dato World Bank utilizzabile: la riga esce senza
#   indicatori e la scelta viene tracciata nel report. Meglio un buco
#   dichiarato che il dato di un paese sbagliato.
# ---------------------------------------------------------------------------
NOC_TO_ISO3: dict[str, str | None] = {
    # --- codici correnti che differiscono tra CIO e ISO3 ---
    "ALG": "DZA", "ANG": "AGO", "ANT": "ATG", "ARU": "ABW", "ASA": "ASM",
    "BAH": "BHS", "BAN": "BGD", "BAR": "BRB", "BER": "BMU", "BHU": "BTN",
    "BIZ": "BLZ", "BOT": "BWA", "BUL": "BGR", "BUR": "BFA", "CAM": "KHM",
    "CAY": "CYM", "CGO": "COG", "CHA": "TCD", "CHI": "CHL", "CRC": "CRI",
    "CRO": "HRV", "DEN": "DNK", "ESA": "SLV", "FIJ": "FJI", "GAM": "GMB",
    "GBS": "GNB", "GEQ": "GNQ", "GER": "DEU", "GRE": "GRC", "GRN": "GRD",
    "GUA": "GTM", "GUI": "GIN", "HAI": "HTI", "HON": "HND", "INA": "IDN",
    "IRI": "IRN", "ISV": "VIR", "IVB": "VGB", "KSA": "SAU", "KUW": "KWT",
    "LAT": "LVA", "LBA": "LBY", "LES": "LSO", "LIB": "LBN", "MAD": "MDG",
    "MAS": "MYS", "MAW": "MWI", "MGL": "MNG", "MON": "MCO", "MRI": "MUS",
    "MTN": "MRT", "MYA": "MMR", "NCA": "NIC", "NED": "NLD", "NEP": "NPL",
    "NGR": "NGA", "NIG": "NER", "OMA": "OMN", "PAR": "PRY", "PHI": "PHL",
    "PLE": "PSE", "POR": "PRT", "PUR": "PRI", "RSA": "ZAF", "SAM": "WSM",
    "SEY": "SYC", "SIN": "SGP", "SKN": "KNA", "SLO": "SVN", "SOL": "SLB",
    "SRI": "LKA", "SUD": "SDN", "SUI": "CHE", "TAN": "TZA", "TGA": "TON",
    "TOG": "TGO", "TRI": "TTO", "UAE": "ARE", "URU": "URY", "VAN": "VUT",
    "VIE": "VNM", "VIN": "VCT", "ZAM": "ZMB", "ZIM": "ZWE",
    # --- falsi amici: senza queste righe il match "identita'" aggancerebbe
    #     il paese sbagliato ---
    "BRN": "BHR",   # NOC Bahrain  (BRN in ISO3 e' il Brunei!)
    "BRU": "BRN",   # NOC Brunei
    # --- casi particolari World Bank ---
    "KOS": "XKX",   # Kosovo (codice non standard usato dalla World Bank)
    "TPE": "TWN",   # Chinese Taipei: la World Bank non pubblica Taiwan,
                    # quindi di fatto restera' senza indicatori (tracciato nel report)
    # --- NOC storici e squadre speciali ---
    "URS": None,    # Unione Sovietica: nessuna serie WB; NON usare la Russia come proxy
    "GDR": None,    # Germania Est: nessuna serie WB
    "FRG": "DEU",   # Germania Ovest: le serie WB "Germany" pre-1990 sono la Rep. Federale
    "EUA": "DEU",   # Squadra unificata tedesca 1956-1964 (proxy dichiarato)
    "TCH": None,    # Cecoslovacchia: nessuna serie WB
    "YUG": None,    # Jugoslavia: nessuna serie WB
    "SCG": None,    # Serbia e Montenegro
    "AHO": None,    # Antille Olandesi
    "EUN": "RUS",   # Squadra Unificata 1992: proxy Russia (approssimazione dichiarata:
                    # la squadra includeva 12 ex repubbliche sovietiche)
    "ROC": "RUS",   # Russian Olympic Committee (Tokyo 2020): atleti russi
    "IOA": None,    # Atleti Olimpici Indipendenti
    "EOR": None,    # Squadra Olimpica Rifugiati
    "MIX": None,    # Squadre miste delle prime edizioni
    "ANZ": None,    # Australasia (1908-1912)
    "BOH": None,    # Boemia
    "BWI": None,    # Indie Occidentali Britanniche
    "UAR": "EGY",   # Repubblica Araba Unita (1960-1968): di fatto l'Egitto
    "YMD": None,    # Yemen del Sud
    "YAR": None,    # Yemen del Nord
    "RHO": None,    # Rhodesia
    "SAA": None,    # Saar
}

# ---------------------------------------------------------------------------
# Intervalli di validita' per la generazione delle righe extra a zero medaglie.
# Evitano righe fantasma per NOC che in certi anni non esistevano come squadra
# (es. "Russia 1984 con 0 medaglie"). Le righe originali del medagliere non
# sono mai filtrate. I NOC assenti da questa tabella sono considerati sempre
# validi.
# ---------------------------------------------------------------------------
NOC_EXTRA_ROW_VALID_YEARS: dict[str, tuple[int, int]] = {
    "RUS": (1994, 9999),   # Federazione Russa: dai Giochi di Lillehammer 1994
    "EUN": (1992, 1992),   # Squadra Unificata: solo 1992
    "ROC": (2020, 2022),   # Russian Olympic Committee: Tokyo 2020 e Pechino 2022
    "URS": (1952, 1991),
    "GDR": (1968, 1988),
    "FRG": (1968, 1988),
    "EUA": (1956, 1964),
    "UAR": (1960, 1968),   # Repubblica Araba Unita
}


@dataclass
class CountryIndicators:
    """Prepared socioeconomic indicators for one country."""

    dataframe: pd.DataFrame
    indicator_columns: list[str]


@dataclass
class AggregationContext:
    """Reusable data needed while building original and extra Olympic rows."""

    country_data: dict[str, CountryIndicators]
    all_indicator_columns: list[str]
    summary_lookup: dict[tuple[int, str], dict[str, Any]]
    years_to_aggregate: int
    noc_to_file: dict[str, str]
    unmapped_nocs: set[str]
    missing_year_entries: set[tuple[str, int, str, tuple[int, ...]]]


def normalize_code(value: Any) -> str:
    """Return a stripped string code, empty for missing values."""
    if pd.isna(value):
        return ""
    return str(value).strip()


def parse_year(value: Any) -> int:
    """Parse a year value without mutating the source dataframe."""
    parsed = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(parsed):
        raise ValueError(f"Invalid Olympic year: {value!r}")
    return int(parsed)


def olympic_key(year: Any, edition: Any) -> tuple[int, str]:
    """Build the unique Olympic Games key from year and edition."""
    return parse_year(year), normalize_code(edition)


def validate_columns(dataframe: pd.DataFrame, required_columns: set[str], source_path: Path) -> None:
    """Raise a clear error if an input CSV is missing required columns."""
    missing_columns = required_columns.difference(dataframe.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns in {source_path}: {', '.join(sorted(missing_columns))}")


def read_main_file(main_file: Path, report_lines: list[str]) -> pd.DataFrame:
    """Load the medal tally and fix known NOC labelling errors (Soviet rows as RUS)."""
    main_df = pd.read_csv(main_file)
    validate_columns(main_df, REQUIRED_MAIN_COLUMNS, main_file)

    for (wrong_noc, country_name), correct_noc in TALLY_NOC_FIXES.items():
        mask = (main_df["country_noc"] == wrong_noc) & (main_df["country"] == country_name)
        if mask.any():
            main_df.loc[mask, "country_noc"] = correct_noc
            report_lines.append(
                f"Tally fix: {int(mask.sum())} rows with country_noc={wrong_noc} "
                f"and country={country_name!r} remapped to {correct_noc}"
            )

    return main_df


def read_games_summary(summary_file: Path, report_lines: list[str]) -> dict[tuple[int, str], dict[str, Any]]:
    """Load host country and city for each Olympic edition."""
    summary_df = pd.read_csv(summary_file)
    validate_columns(summary_df, REQUIRED_SUMMARY_COLUMNS, summary_file)

    lookup: dict[tuple[int, str], dict[str, Any]] = {}
    duplicate_keys: set[tuple[int, str]] = set()

    for _, row in summary_df.iterrows():
        key = olympic_key(row["year"], row["edition"])
        value = {"paese_olimpiade": row["country_noc"], "citta_olimpiade": row["city"]}
        if key in lookup and lookup[key] != value:
            duplicate_keys.add(key)
            continue
        lookup[key] = value

    for year, edition in sorted(duplicate_keys):
        report_lines.append(
            f"Duplicate Olympic summary rows with conflicting host data ignored for year={year}, edition={edition}"
        )

    return lookup


def read_country_file(country_file: Path) -> CountryIndicators | None:
    """Load one country indicator file and convert indicator values to numeric."""
    country_df = pd.read_csv(country_file)
    if "Year" not in country_df.columns:
        return None

    prepared_df = country_df.copy()
    indicator_columns = [column for column in prepared_df.columns if column != "Year"]
    prepared_df["_year_number"] = pd.to_numeric(
        prepared_df["Year"].astype(str).str.replace("YR", "", regex=False),
        errors="coerce",
    )
    for column in indicator_columns:
        prepared_df[column] = pd.to_numeric(prepared_df[column], errors="coerce")

    return CountryIndicators(dataframe=prepared_df, indicator_columns=indicator_columns)


def read_all_country_files(clean_dir: Path, report_lines: list[str]) -> tuple[dict[str, CountryIndicators], list[str]]:
    """Load each country CSV once, keyed by its ISO3 file stem."""
    country_data: dict[str, CountryIndicators] = {}
    all_indicator_columns: list[str] = []

    for country_file in sorted(clean_dir.glob("*.csv")):
        indicators = read_country_file(country_file)
        if indicators is None:
            report_lines.append(f"{country_file.stem}: missing required Year column in {country_file}")
            continue
        country_data[country_file.stem] = indicators
        for column in indicators.indicator_columns:
            if column not in all_indicator_columns:
                all_indicator_columns.append(column)

    return country_data, all_indicator_columns


def resolve_noc_to_file(
    tally_nocs: set[str],
    available_files: set[str],
    report_lines: list[str],
) -> tuple[dict[str, str], set[str]]:
    """Resolve every NOC to a World Bank file stem via NOC_TO_ISO3, else identity.

    Returns the resolved mapping and the set of NOCs left without indicators.
    Every decision is written to the report so it can be audited.
    """
    noc_to_file: dict[str, str] = {}
    unmapped: set[str] = set()

    # I NOC possono arrivare sia dal medagliere sia dalla tabella di mappatura
    # (paesi senza medaglie ma con dati WB, per le righe extra a zero medaglie).
    reverse_map = {iso: noc for noc, iso in NOC_TO_ISO3.items() if iso}
    extra_nocs = {reverse_map.get(stem, stem) for stem in available_files}

    for noc in sorted(tally_nocs | extra_nocs):
        if noc in NOC_TO_ISO3:
            iso = NOC_TO_ISO3[noc]
            if iso is None:
                unmapped.add(noc)
                report_lines.append(f"Mapping: {noc} -> nessun dato World Bank (scelta esplicita)")
            elif iso in available_files:
                noc_to_file[noc] = iso
                if iso != noc:
                    report_lines.append(f"Mapping: {noc} -> file {iso}.csv")
            else:
                unmapped.add(noc)
                report_lines.append(f"Mapping: {noc} -> {iso} ma il file {iso}.csv non esiste")
        elif noc in available_files:
            # Identita' NOC == ISO3: sicura perche' tutti i codici che
            # differiscono (falsi amici inclusi) sono nella tabella esplicita.
            noc_to_file[noc] = noc
        else:
            unmapped.add(noc)
            report_lines.append(f"Mapping: {noc} -> nessun file World Bank trovato")

    return noc_to_file, unmapped


def previous_years(olympic_year: int, years_to_aggregate: int) -> list[int]:
    """Return the years used for pre-Olympic aggregation."""
    return list(range(olympic_year - years_to_aggregate, olympic_year))


def empty_indicator_values(indicator_columns: list[str]) -> dict[str, Any]:
    """Return NaN values for all socioeconomic indicator columns."""
    return {column: pd.NA for column in indicator_columns}


def aggregate_country_indicators(
    country_noc: str,
    olympic_year: int,
    edition: str,
    context: AggregationContext,
) -> dict[str, Any]:
    """Average available country indicators over the previous Olympic years."""
    file_stem = context.noc_to_file.get(country_noc)
    if file_stem is None:
        return empty_indicator_values(context.all_indicator_columns)

    indicators = context.country_data[file_stem]
    target_years = previous_years(olympic_year, context.years_to_aggregate)
    available_years = set(indicators.dataframe["_year_number"].dropna().astype(int).tolist())
    missing_years = tuple(year for year in target_years if year not in available_years)
    if missing_years:
        context.missing_year_entries.add((country_noc, olympic_year, edition, missing_years))

    window_df = indicators.dataframe[indicators.dataframe["_year_number"].isin(target_years)]
    aggregated_values = empty_indicator_values(context.all_indicator_columns)
    if not window_df.empty and indicators.indicator_columns:
        means = window_df[indicators.indicator_columns].mean(skipna=True)
        for column, value in means.items():
            aggregated_values[column] = value

    return aggregated_values


def get_olympic_place(key: tuple[int, str], summary_lookup: dict[tuple[int, str], dict[str, Any]]) -> dict[str, Any]:
    """Return host country and city, or NaN values if the edition is missing."""
    default_place = {"paese_olimpiade": pd.NA, "citta_olimpiade": pd.NA}
    return summary_lookup.get(key, default_place).copy()


def find_missing_summary_pairs(
    main_df: pd.DataFrame,
    summary_lookup: dict[tuple[int, str], dict[str, Any]],
) -> list[tuple[int, str]]:
    """Find Olympic editions from the main file missing in the summary file."""
    missing_pairs: set[tuple[int, str]] = set()
    for _, row in main_df[["year", "edition"]].drop_duplicates().iterrows():
        key = olympic_key(row["year"], row["edition"])
        if key not in summary_lookup:
            missing_pairs.add(key)
    return sorted(missing_pairs)


def get_pair_derived_columns(main_df: pd.DataFrame) -> set[str]:
    """Find original columns that are functionally determined by year+edition."""
    candidate_columns = [column for column in main_df.columns if column not in FIXED_NEW_ROW_COLUMNS]
    pair_derived_columns: set[str] = set()
    for column in candidate_columns:
        unique_counts = main_df.groupby(["year", "edition"], dropna=False)[column].nunique(dropna=True)
        if (unique_counts <= 1).all():
            pair_derived_columns.add(column)
    return pair_derived_columns


def get_unique_pair_values(group_df: pd.DataFrame, pair_derived_columns: set[str]) -> dict[str, Any]:
    """Extract values that can be copied to added rows for one Olympic edition."""
    values: dict[str, Any] = {}
    for column in pair_derived_columns:
        non_null_values = group_df[column].dropna().unique()
        values[column] = non_null_values[0] if len(non_null_values) == 1 else pd.NA
    return values


def build_original_row(source_row: pd.Series, context: AggregationContext) -> dict[str, Any]:
    """Build one enriched row that already exists in the main dataset."""
    row_dict = source_row.to_dict()
    year, edition = olympic_key(source_row["year"], source_row["edition"])
    country_noc = normalize_code(source_row["country_noc"])

    row_dict.update(get_olympic_place((year, edition), context.summary_lookup))
    row_dict.update(
        aggregate_country_indicators(
            country_noc=country_noc, olympic_year=year, edition=edition, context=context
        )
    )
    return row_dict


def build_extra_row(
    country_noc: str,
    olympic_year: int,
    edition: str,
    source_year_value: Any,
    pair_values: dict[str, Any],
    original_columns: list[str],
    context: AggregationContext,
) -> dict[str, Any]:
    """Build one zero-medal row (keyed by NOC) for a country absent from an edition."""
    row_dict = {column: pd.NA for column in original_columns}
    row_dict.update(pair_values)
    row_dict["year"] = source_year_value
    row_dict["edition"] = edition
    row_dict["country_noc"] = country_noc
    for column in MEDAL_COLUMNS:
        row_dict[column] = 0

    row_dict.update(get_olympic_place((olympic_year, edition), context.summary_lookup))
    row_dict.update(
        aggregate_country_indicators(
            country_noc=country_noc, olympic_year=olympic_year, edition=edition, context=context
        )
    )
    return row_dict


def build_enriched_dataset(main_df: pd.DataFrame, context: AggregationContext) -> pd.DataFrame:
    """Create the final dataset with original and added country-edition rows."""
    output_rows: list[dict[str, Any]] = []

    for _, row in main_df.iterrows():
        output_rows.append(build_original_row(row, context))

    pair_derived_columns = get_pair_derived_columns(main_df)
    # Le righe extra usano SEMPRE codici NOC: sono i paesi con dati World Bank
    # (gia' risolti in resolve_noc_to_file) assenti da una specifica edizione.
    countries_with_indicators = set(context.noc_to_file.keys())

    for (year_value, edition_value), group_df in main_df.groupby(["year", "edition"], sort=False, dropna=False):
        olympic_year, edition = olympic_key(year_value, edition_value)
        present_countries = {
            normalize_code(country) for country in group_df["country_noc"].dropna().tolist()
        }
        # File WB gia' rappresentati in questa edizione tramite la mappatura:
        # se il file RUS.csv e' gia' "usato" da EUN o ROC, non va aggiunta anche
        # una riga Russia a zero medaglie (stesso paese contato due volte).
        present_stems = {
            context.noc_to_file[noc] for noc in present_countries if noc in context.noc_to_file
        }
        pair_values = get_unique_pair_values(group_df, pair_derived_columns)

        # Un solo candidato per file WB: se in un'edizione mancano sia FRG sia
        # GER (Mosca 1980), non vanno create due righe Germania. A parita' di
        # file vince il NOC con intervallo di validita' esplicito, cioe' il
        # codice storicamente corretto per quell'epoca.
        candidates_by_stem: dict[str, str] = {}
        for country_noc in sorted(countries_with_indicators.difference(present_countries)):
            first_year, last_year = NOC_EXTRA_ROW_VALID_YEARS.get(country_noc, (0, 9999))
            if not (first_year <= olympic_year <= last_year):
                continue
            stem = context.noc_to_file[country_noc]
            if stem in present_stems:
                continue
            already_chosen = candidates_by_stem.get(stem)
            if already_chosen is None or (
                country_noc in NOC_EXTRA_ROW_VALID_YEARS
                and already_chosen not in NOC_EXTRA_ROW_VALID_YEARS
            ):
                candidates_by_stem[stem] = country_noc

        for country_noc in sorted(candidates_by_stem.values()):
            output_rows.append(
                build_extra_row(
                    country_noc=country_noc,
                    olympic_year=olympic_year,
                    edition=edition,
                    source_year_value=year_value,
                    pair_values=pair_values,
                    original_columns=list(main_df.columns),
                    context=context,
                )
            )

    output_columns = list(main_df.columns) + OLYMPIC_PLACE_COLUMNS + context.all_indicator_columns
    final_df = pd.DataFrame(output_rows, columns=output_columns)

    # Guardia anti-regressione: la chiave (edizione, NOC) deve essere unica.
    duplicated_keys = final_df.duplicated(subset=["year", "edition", "country_noc"])
    if duplicated_keys.any():
        examples = final_df.loc[duplicated_keys, ["year", "edition", "country_noc"]].head(10)
        raise ValueError(f"Duplicate (year, edition, country_noc) keys in output:\n{examples}")

    return final_df


def build_report_lines(
    initial_report_lines: list[str],
    missing_summary_pairs: list[tuple[int, str]],
    unmapped_nocs: set[str],
    missing_year_entries: set[tuple[str, int, str, tuple[int, ...]]],
) -> list[str]:
    """Format all data-quality messages for the output report."""
    report_lines = list(initial_report_lines)

    for year, edition in missing_summary_pairs:
        report_lines.append(f"Missing Olympic summary match for year={year}, edition={edition}")

    for country_noc in sorted(noc for noc in unmapped_nocs if noc):
        report_lines.append(f"{country_noc}: no World Bank indicators available")

    for country_noc, olympic_year, edition, missing_years in sorted(missing_year_entries):
        years = ", ".join(str(year) for year in missing_years)
        report_lines.append(
            f"{country_noc} - year={olympic_year}, edition={edition}: missing previous years {years}"
        )

    if not report_lines:
        report_lines.append("No missing data found.")

    return report_lines


def write_outputs(final_df: pd.DataFrame, report_lines: list[str], output_dir: Path) -> tuple[Path, Path]:
    """Write the final CSV and missing-data report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_csv = output_dir / OUTPUT_CSV_NAME
    report_file = output_dir / REPORT_NAME
    final_df.to_csv(output_csv, index=False)
    report_file.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    return output_csv, report_file


def parse_args() -> argparse.Namespace:
    """Parse paths and aggregation settings from the command line."""
    parser = argparse.ArgumentParser(
        description="Generate an Olympic medal CSV enriched with socioeconomic indicators (v4, NOC/ISO3 mapping)."
    )
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--main-file", type=Path, default=None)
    parser.add_argument("--summary-file", type=Path, default=None)
    parser.add_argument("--clean-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--years-to-aggregate", type=int, default=DEFAULT_YEARS_TO_AGGREGATE)
    return parser.parse_args()


def main(
    main_file: Path = DEFAULT_MAIN_FILE,
    summary_file: Path = DEFAULT_SUMMARY_FILE,
    clean_dir: Path = DEFAULT_CLEAN_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    years_to_aggregate: int = DEFAULT_YEARS_TO_AGGREGATE,
) -> None:
    """Generate the enriched Olympic medal dataset and missing-data report."""
    report_lines: list[str] = []

    main_df = read_main_file(main_file, report_lines)
    summary_lookup = read_games_summary(summary_file, report_lines)
    country_data, all_indicator_columns = read_all_country_files(clean_dir, report_lines)

    tally_nocs = {normalize_code(noc) for noc in main_df["country_noc"].dropna().tolist()}
    noc_to_file, unmapped_nocs = resolve_noc_to_file(
        tally_nocs=tally_nocs,
        available_files=set(country_data.keys()),
        report_lines=report_lines,
    )

    context = AggregationContext(
        country_data=country_data,
        all_indicator_columns=all_indicator_columns,
        summary_lookup=summary_lookup,
        years_to_aggregate=years_to_aggregate,
        noc_to_file=noc_to_file,
        unmapped_nocs=unmapped_nocs,
        missing_year_entries=set(),
    )

    missing_summary_pairs = find_missing_summary_pairs(main_df, summary_lookup)
    final_df = build_enriched_dataset(main_df, context)
    final_report_lines = build_report_lines(
        initial_report_lines=report_lines,
        missing_summary_pairs=missing_summary_pairs,
        unmapped_nocs=unmapped_nocs,
        missing_year_entries=context.missing_year_entries,
    )
    output_csv, report_file = write_outputs(final_df, final_report_lines, output_dir)

    print(f"CSV written to: {output_csv}")
    print(f"Missing-data report written to: {report_file}")


if __name__ == "__main__":
    args = parse_args()
    main(
        main_file=args.main_file if args.main_file is not None else DEFAULT_MAIN_FILE,
        summary_file=args.summary_file if args.summary_file is not None else DEFAULT_SUMMARY_FILE,
        clean_dir=args.clean_dir if args.clean_dir is not None else DEFAULT_CLEAN_DIR,
        output_dir=args.output_dir,
        years_to_aggregate=args.years_to_aggregate,
    )
