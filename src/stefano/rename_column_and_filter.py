"""Rinomina in italiano le colonne del dataset prodotto dallo script v4 e
filtra le sole Olimpiadi estive 1964-2020.

- I nomi italiani sono quelli di ``src/santina/dataset_indicatori_definitivo.csv``:
  lo script verifica che i due file abbiano lo stesso numero di colonne e che
  la mappatura copra esattamente entrambi gli schemi prima di toccare i dati.
- Il filtro tiene le righe la cui ``edition`` contiene "Summer Olympics" e
  il cui anno e' compreso tra 1964 e 2020.
- La colonna ``Nazione`` viene sempre valorizzata: le righe extra a zero
  medaglie ereditano il nome piu' recente usato dal medagliere per quel NOC;
  per i NOC mai a medaglia il nome arriva da ISO.csv, passando per la
  mappatura NOC->ISO3 dello script v4.

Uso:
    python rename_column_and_filter.py
    python rename_column_and_filter.py --input ... --reference ... --output ...
"""

import argparse
import importlib.util
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_INPUT = PROJECT_ROOT / "test2" / "olympic_medals_with_socioeconomic_indicators_4.csv"
DEFAULT_REFERENCE = PROJECT_ROOT / "src" / "santina" / "dataset_indicatori_definitivo.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "test2" / "dataset_indicatori_definitivo_4.csv"

DATASET_BUILD_DIR = PROJECT_ROOT / "src" / "stefano" / "dataset_build"
GENERATOR_V4_SCRIPT = DATASET_BUILD_DIR / "02_generate_olympic_medals_with_socioeconomic_indicators_4.py"
ISO_CSV = DATASET_BUILD_DIR / "ISO.csv"

FIRST_YEAR = 1964
LAST_YEAR = 2020
SUMMER_LABEL = "Summer Olympics"

# Mappatura esplicita colonna inglese/World Bank -> nome italiano.
# L'ordine segue lo schema dei due file; la coerenza con il file di
# riferimento viene comunque verificata a runtime.
RENAME_MAP = {
    "edition": "Edizione_Olimpiadi",
    "edition_id": "ID_Edizione",
    "year": "Anno",
    "country": "Nazione",
    "country_noc": "Codice_NOC",
    "gold": "Medaglie_Oro",
    "silver": "Medaglie_Argento",
    "bronze": "Medaglie_Bronzo",
    "total": "Totale_Medaglie",
    "paese_olimpiade": "Paese_Ospitante",
    "citta_olimpiade": "Citta_Ospitante",
    "AG.LND.PRCP.MM": "Precipitazioni_Medie_mm",
    "AG.SRF.TOTL.K2": "Superficie_Totale_km2",
    "BX.KLT.DINV.WD.GD.ZS": "Investimenti_Diretti_Esteri_perc_PIL",
    "EN.POP.DNST": "Densita_Popolazione",
    "FP.CPI.TOTL.ZG": "Inflazione_Prezzi_Consumo",
    "MS.MIL.XPND.CN": "Spesa_Militare_Valuta_Locale",
    "MS.MIL.XPND.GD.ZS": "Spesa_Militare_perc_PIL",
    "NE.CON.GOVT.CD": "Spesa_Pubblica_Consumi_USD",
    "NE.DAB.TOTL.CN": "Spesa_Nazionale_Lorda_Valuta_Locale",
    "NE.TRD.GNFS.ZS": "Interscambio_Commerciale_perc_PIL",
    "NV.IND.TOTL.ZS": "Valore_Aggiunto_Industria_perc_PIL",
    "NV.SRV.TOTL.CN": "Valore_Aggiunto_Servizi_Valuta_Locale",
    "NV.SRV.TOTL.ZS": "Valore_Aggiunto_Servizi_perc_PIL",
    "NY.GDP.DEFL.KD.ZG": "Inflazione_Deflatore_PIL",
    "NY.GDP.MKTP.CD": "PIL_Assoluto_USD",
    "NY.GDP.MKTP.CN": "PIL_Valuta_Locale",
    "NY.GDP.MKTP.KD.ZG": "Crescita_PIL_perc_annua",
    "NY.GDP.PCAP.CD": "PIL_Pro_Capite_USD",
    "NY.GNP.MKTP.CN": "RNL_Valuta_Locale",
    "NY.GNP.PCAP.CD": "RNL_Pro_Capite_USD",
    "SE.PRM.ENRR": "Iscrizioni_Scuola_Primaria_perc",
    "SH.DYN.NMRT": "Tasso_Mortalita_Neonatale",
    "SP.DYN.IMRT.IN": "Tasso_Mortalita_Infantile",
    "SP.DYN.LE00.IN": "Aspettativa_di_Vita",
    "SP.POP.1564.TO.ZS": "Popolazione_Eta_Lavorativa_perc",
    "SP.POP.GROW": "Crescita_Demografica_perc",
    "SP.POP.TOTL": "Popolazione_Totale",
    "SP.URB.TOTL": "Popolazione_Urbana",
    "SP.URB.TOTL.IN.ZS": "Tasso_Urbanizzazione_perc",
}


def validate_schemas(input_columns: list[str], reference_columns: list[str]) -> None:
    """Ferma tutto se gli schemi non corrispondono alla mappatura attesa."""
    if len(input_columns) != len(reference_columns):
        raise ValueError(
            f"Numero di colonne diverso: input={len(input_columns)}, "
            f"riferimento={len(reference_columns)}"
        )

    colonne_input_impreviste = set(input_columns) - set(RENAME_MAP.keys())
    if colonne_input_impreviste:
        raise ValueError(f"Colonne del file di input non previste dalla mappatura: {sorted(colonne_input_impreviste)}")

    colonne_riferimento_impreviste = set(reference_columns) - set(RENAME_MAP.values())
    if colonne_riferimento_impreviste:
        raise ValueError(
            f"Colonne del file di riferimento non previste dalla mappatura: {sorted(colonne_riferimento_impreviste)}"
        )


def load_noc_to_iso3() -> dict[str, str | None]:
    """Importa la tabella NOC->ISO3 dallo script v4, senza duplicarla qui."""
    spec = importlib.util.spec_from_file_location("generator_v4", GENERATOR_V4_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.NOC_TO_ISO3


def build_nazione_per_noc(df: pd.DataFrame) -> pd.Series:
    """Nome paese per ogni NOC: dal medagliere, con fallback su ISO.csv.

    Il nome principale e' quello piu' recente usato dal medagliere per quel
    NOC (righe originali, tutte le edizioni). Per i NOC mai a medaglia
    (presenti solo come righe extra a zero medaglie) il nome arriva da
    ISO.csv, risolvendo il codice con la mappatura NOC->ISO3 dello script v4.
    """
    con_nome = df.dropna(subset=["country"]).sort_values("year")
    nome_per_noc = con_nome.groupby("country_noc")["country"].last()

    noc_to_iso3 = load_noc_to_iso3()
    iso_df = pd.read_csv(ISO_CSV, encoding="latin-1", usecols=["name", "alpha-3"])
    iso_to_name = dict(zip(iso_df["alpha-3"], iso_df["name"]))

    senza_nome = set(df["country_noc"].dropna()) - set(nome_per_noc.index)
    fallback = {}
    for noc in sorted(senza_nome):
        iso = noc_to_iso3.get(noc, noc)
        if iso is not None and iso in iso_to_name:
            fallback[noc] = iso_to_name[iso]

    irrisolti = sorted(senza_nome - set(fallback))
    if irrisolti:
        print(f"Attenzione: nessun nome trovato per i NOC {irrisolti}")
    print(f"Nomi paese: {len(nome_per_noc)} dal medagliere, {len(fallback)} da ISO.csv")

    return pd.concat([nome_per_noc, pd.Series(fallback)])


def main(input_file: Path, reference_file: Path, output_file: Path) -> None:
    df = pd.read_csv(input_file, low_memory=False)
    reference_columns = list(pd.read_csv(reference_file, nrows=0).columns)

    print(f"Input: {input_file} ({len(df)} righe, {len(df.columns)} colonne)")
    print(f"Riferimento nomi colonne: {reference_file} ({len(reference_columns)} colonne)")
    validate_schemas(list(df.columns), reference_columns)

    # La mappa dei nomi si costruisce PRIMA del filtro, cosi' un paese che ha
    # vinto medaglie solo fuori dal periodo 1964-2020 mantiene il suo nome.
    nazione_per_noc = build_nazione_per_noc(df)

    # Filtro: solo Olimpiadi estive, anni 1964-2020.
    is_summer = df["edition"].astype("string").str.contains(SUMMER_LABEL, case=False, na=False)
    year = pd.to_numeric(df["year"], errors="coerce")
    df = df.loc[is_summer & year.between(FIRST_YEAR, LAST_YEAR)].copy()
    print(f"Dopo il filtro '{SUMMER_LABEL}' {FIRST_YEAR}-{LAST_YEAR}: {len(df)} righe")

    # Valorizza sempre Nazione: le righe extra a zero medaglie non hanno il
    # nome paese, che viene recuperato dalla mappa per NOC.
    df["country"] = df["country"].fillna(df["country_noc"].map(nazione_per_noc))
    print(f"Righe con Nazione vuota dopo il riempimento: {df['country'].isna().sum()}")

    # Rinomina e riordina le colonne come nel file di riferimento.
    df = df.rename(columns=RENAME_MAP)[reference_columns]

    df.to_csv(output_file, index=False)
    print(f"Salvato: {output_file}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(input_file=args.input, reference_file=args.reference, output_file=args.output)
