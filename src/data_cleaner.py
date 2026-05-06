"""Standardisation, nettoyage et export des donnees D3S."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any

import pandas as pd

from src.utils import ensure_parent_dir, is_missing, normalize_text


logger = logging.getLogger(__name__)

STANDARD_FIELDS = [
    "poste",
    "ville",
    "departement",
    "region",
    "lieux_poste",
    "etablissements",
    "finess",
    "mois_parution",
    "annee_parution",
    "categorie",
    "type_structure",
    "type_etablissement",
    "latitude",
    "longitude",
    "latitude_finess",
    "longitude_finess",
    "qualite_coordonnees",
    "source_coordonnees",
    "source",
    "observations",
    "texte_source_poste",
    "raison_sociale_finess",
    "qualite_appariement_finess",
]

DEDUP_KEYS = [
    "poste",
    "ville",
    "etablissements",
    "annee_parution",
    "mois_parution",
    "categorie",
]

CATEGORY_CHEF = "Chef d'établissement"
CATEGORY_ADJOINT = "Directeur adjoint"
CATEGORY_ELEVES = "Poste réservé aux élèves directeurs"
CATEGORY_OTHER = "Autre / non précisé"
STRUCTURE_SANITAIRE = "Sanitaire"
STRUCTURE_MEDICO_SOCIAL = "Médico-social"
STRUCTURE_SOCIAL = "Social"
STRUCTURE_UNKNOWN = "Non précisé"
ESTABLISHMENT_EHPAD_SANITAIRE = "EHPAD sanitaire"
ESTABLISHMENT_EHPAD_AUTONOME = "EHPAD autonome"
ESTABLISHMENT_RESIDENCE_AUTONOMIE = "Résidence autonomie"
ESTABLISHMENT_SANITAIRE = "Établissement sanitaire"
ESTABLISHMENT_SOCIAL_CHILDHOOD = "Protection de l'enfance / social"
ESTABLISHMENT_EPMS = "EPMS / EPSMS"
ESTABLISHMENT_HANDICAP_ADULT = "Handicap adulte"
ESTABLISHMENT_HANDICAP_CHILD = "Handicap enfant"
ESTABLISHMENT_UNKNOWN = "Non précisé"


@dataclass
class CleanResult:
    """Resultat du nettoyage des donnees."""

    valid_posts: pd.DataFrame
    missing_coords: pd.DataFrame
    rows_read: int
    valid_count: int
    missing_coords_count: int
    duplicates_removed: int
    column_mapping: dict[str, str | None]


class MissingCoordinatesColumnsError(ValueError):
    """Erreur levee lorsque les colonnes de coordonnees sont absentes."""


def standardize_posts(raw_df: pd.DataFrame, config: dict[str, Any]) -> CleanResult:
    """Nettoie le DataFrame source et separe les lignes cartographiables."""
    rows_read = len(raw_df)
    aliases = config["column_aliases"]
    default_missing = config["default_missing_value"]
    mapping = map_columns(raw_df.columns, aliases)

    if mapping.get("latitude") is None or mapping.get("longitude") is None:
        raise MissingCoordinatesColumnsError(
            "Colonnes latitude/longitude introuvables. Verifiez les alias dans config/settings.yaml."
        )

    df = pd.DataFrame()
    for field in STANDARD_FIELDS:
        source_column = mapping.get(field)
        if source_column is None:
            if field == "type_structure":
                logger.info("Champ 'type_structure' absent: il sera deduit automatiquement.")
            elif field == "type_etablissement":
                logger.info("Champ 'type_etablissement' absent: il sera deduit automatiquement.")
            elif field == "source_coordonnees":
                logger.info("Champ 'source_coordonnees' absent: il sera complete depuis le referentiel FINESS si possible.")
            else:
                logger.warning("Colonne absente pour le champ '%s'. Valeur vide utilisee.", field)
            df[field] = ""
        else:
            df[field] = raw_df[source_column]

    df = clean_text_columns(df)
    df["categorie"] = df["categorie"].apply(normalize_category)
    df["type_structure"] = df.apply(normalize_or_infer_structure_type, axis=1)
    df["type_etablissement"] = df.apply(normalize_or_infer_establishment_type, axis=1)
    df["latitude"] = parse_coordinates(df["latitude"])
    df["longitude"] = parse_coordinates(df["longitude"])
    df["latitude_finess"] = parse_coordinates(df["latitude_finess"])
    df["longitude_finess"] = parse_coordinates(df["longitude_finess"])
    df = apply_best_coordinates(df, config)

    before_dedup = len(df)
    if config.get("deduplicate", True):
        df = deduplicate_posts(df)
    duplicates_removed = before_dedup - len(df)

    coords_mask = df["latitude"].notna() & df["longitude"].notna()
    coords_mask &= df["latitude"].between(-90, 90) & df["longitude"].between(-180, 180)

    valid_posts = df.loc[coords_mask].copy()
    missing_coords = df.loc[~coords_mask].copy()

    if valid_posts.empty:
        raise ValueError("Aucun poste avec coordonnees exploitables apres nettoyage.")

    valid_posts = prepare_for_export(valid_posts, default_missing)
    missing_coords = prepare_for_export(missing_coords, default_missing)
    valid_posts.insert(0, "id", range(1, len(valid_posts) + 1))

    return CleanResult(
        valid_posts=valid_posts,
        missing_coords=missing_coords,
        rows_read=rows_read,
        valid_count=len(valid_posts),
        missing_coords_count=len(missing_coords),
        duplicates_removed=duplicates_removed,
        column_mapping=mapping,
    )


def map_columns(columns: pd.Index, aliases: dict[str, list[str]]) -> dict[str, str | None]:
    """Associe les colonnes source aux champs internes standardises."""
    normalized_columns = {normalize_text(column): str(column) for column in columns}
    mapping: dict[str, str | None] = {}

    for field, field_aliases in aliases.items():
        normalized_aliases = [normalize_text(alias) for alias in [field, *field_aliases]]
        match = find_best_column_match(normalized_aliases, normalized_columns)
        mapping[field] = match
        if match:
            logger.info("Champ '%s' mappe sur la colonne source '%s'.", field, match)
    return mapping


def find_best_column_match(
    normalized_aliases: list[str],
    normalized_columns: dict[str, str],
) -> str | None:
    """Trouve la meilleure colonne par egalite, inclusion puis similarite."""
    for alias in normalized_aliases:
        if alias in normalized_columns:
            return normalized_columns[alias]

    for alias in normalized_aliases:
        if len(alias) < 3:
            continue
        for normalized_column, original_column in normalized_columns.items():
            if alias in normalized_column or normalized_column in alias:
                return original_column

    best_score = 0.0
    best_column: str | None = None
    for alias in normalized_aliases:
        if len(alias) < 4:
            continue
        for normalized_column, original_column in normalized_columns.items():
            score = SequenceMatcher(None, alias, normalized_column).ratio()
            if score > best_score:
                best_score = score
                best_column = original_column
    return best_column if best_score >= 0.86 else None


def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie les champs texte tout en conservant les coordonnees a part."""
    cleaned = df.copy()
    for column in cleaned.columns:
        if column in {"latitude", "longitude", "latitude_finess", "longitude_finess"}:
            continue
        cleaned[column] = cleaned[column].apply(clean_display_value)
    return cleaned


def clean_display_value(value: Any) -> str:
    """Convertit une valeur source en texte propre pour export et affichage."""
    if is_missing(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return " ".join(str(value).replace("\r", "\n").split())


def parse_coordinates(series: pd.Series) -> pd.Series:
    """Convertit des coordonnees utilisant virgule ou point decimal en float."""
    normalized = (
        series.astype("string")
        .str.strip()
        .str.replace(",", ".", regex=False)
        .str.replace(r"\s+", "", regex=True)
    )
    normalized = normalized.str.extract(r"([-+]?\d+(?:\.\d+)?)", expand=False)
    return pd.to_numeric(normalized, errors="coerce")


def apply_best_coordinates(df: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Priorise les coordonnees FINESS puis conserve les coordonnees source en repli."""
    work = df.copy()
    lookup = load_finess_coordinate_lookup(config)
    if lookup:
        finess_keys = work["finess"].apply(clean_finess_identifier)
        ref_coords = finess_keys.map(lookup)
        ref_lat = ref_coords.map(lambda item: item["latitude"] if isinstance(item, dict) else pd.NA)
        ref_lon = ref_coords.map(lambda item: item["longitude"] if isinstance(item, dict) else pd.NA)
        ref_source = ref_coords.map(lambda item: item["source"] if isinstance(item, dict) else "")

        missing_finess_coords = work["latitude_finess"].isna() | work["longitude_finess"].isna()
        work.loc[missing_finess_coords, "latitude_finess"] = pd.to_numeric(
            ref_lat.loc[missing_finess_coords], errors="coerce"
        )
        work.loc[missing_finess_coords, "longitude_finess"] = pd.to_numeric(
            ref_lon.loc[missing_finess_coords], errors="coerce"
        )
        work.loc[missing_finess_coords & ref_source.ne(""), "source_coordonnees"] = ref_source.loc[
            missing_finess_coords & ref_source.ne("")
        ]

    finess_mask = work["latitude_finess"].notna() & work["longitude_finess"].notna()
    work.loc[finess_mask, "latitude"] = work.loc[finess_mask, "latitude_finess"]
    work.loc[finess_mask, "longitude"] = work.loc[finess_mask, "longitude_finess"]
    work.loc[finess_mask, "qualite_coordonnees"] = "Coordonnées FINESS géolocalisées"
    work.loc[finess_mask & work["source_coordonnees"].eq(""), "source_coordonnees"] = "Référentiel FINESS"

    logger.info("Coordonnees FINESS utilisees: %s", int(finess_mask.sum()))
    logger.info("Coordonnees source ou approximatives conservees: %s", int((~finess_mask).sum()))
    return work


def load_finess_coordinate_lookup(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Charge un index FINESS -> coordonnees depuis le cache open data si disponible."""
    path = config.get("finess_reference_csv_path")
    if not path:
        return {}
    if not path.exists():
        logger.warning("Referentiel FINESS introuvable pour les coordonnees: %s", path)
        return {}

    sample = path.read_bytes()[:4096]
    sep = ";" if sample.count(b";") >= sample.count(b",") else ","
    usecols = ["numero_finess_et", "coord", "sourcecoordet"]
    try:
        ref = pd.read_csv(path, sep=sep, dtype=str, usecols=usecols, engine="python", on_bad_lines="skip")
    except ValueError:
        ref = pd.read_csv(path, sep=sep, dtype=str, engine="python", on_bad_lines="skip")

    ref = ref.fillna("")
    if "numero_finess_et" not in ref.columns or "coord" not in ref.columns:
        logger.warning("Referentiel FINESS sans colonnes numero_finess_et/coord: %s", path)
        return {}

    ref["finess_key"] = ref["numero_finess_et"].apply(clean_finess_identifier)
    coords = ref["coord"].apply(parse_finess_coord)
    ref["latitude"] = coords.map(lambda item: item[0])
    ref["longitude"] = coords.map(lambda item: item[1])
    ref = ref.dropna(subset=["latitude", "longitude"])
    ref = ref[(ref["latitude"].between(-90, 90)) & (ref["longitude"].between(-180, 180))]
    ref = ref.drop_duplicates("finess_key", keep="first")

    source_col = "sourcecoordet" if "sourcecoordet" in ref.columns else None
    lookup = {}
    for _, row in ref.iterrows():
        lookup[row["finess_key"]] = {
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "source": clean_display_value(row[source_col]) if source_col else "Référentiel FINESS",
        }
    logger.info("Coordonnees FINESS chargees: %s", len(lookup))
    return lookup


def clean_finess_identifier(value: Any) -> str:
    """Nettoie un numero FINESS pour une jointure fiable."""
    if is_missing(value):
        return ""
    digits = "".join(char for char in str(value) if char.isdigit())
    return digits.zfill(9) if digits else ""


def parse_finess_coord(value: Any) -> tuple[float | None, float | None]:
    """Extrait latitude et longitude depuis la colonne coord du referentiel FINESS."""
    if is_missing(value):
        return None, None
    parts = [part.strip() for part in str(value).replace(";", ",").split(",")]
    if len(parts) < 2:
        return None, None
    lat = pd.to_numeric(parts[0], errors="coerce")
    lon = pd.to_numeric(parts[1], errors="coerce")
    if pd.isna(lat) or pd.isna(lon):
        return None, None
    return float(lat), float(lon)


def normalize_category(value: Any) -> str:
    """Rattache les libelles sources aux quatre categories attendues."""
    normalized = normalize_text(value)
    if not normalized:
        return CATEGORY_OTHER
    if "eleve" in normalized or "reserve" in normalized:
        return CATEGORY_ELEVES
    if "adjoint" in normalized:
        return CATEGORY_ADJOINT
    if "chef" in normalized or "directeur d etablissement" in normalized:
        return CATEGORY_CHEF
    return clean_display_value(value) or CATEGORY_OTHER


def normalize_or_infer_structure_type(row: pd.Series) -> str:
    """Normalise ou deduit le secteur de l'etablissement pour la forme du marqueur."""
    explicit_value = normalize_text(row.get("type_structure", ""))
    if explicit_value:
        if "sanitaire" in explicit_value or "hospital" in explicit_value:
            return STRUCTURE_SANITAIRE
        if "medico" in explicit_value or "médico" in explicit_value:
            return STRUCTURE_MEDICO_SOCIAL
        if "social" in explicit_value:
            return STRUCTURE_SOCIAL

    text = normalize_text(
        " ".join(
            clean_display_value(row.get(field, ""))
            for field in [
                "etablissements",
                "lieux_poste",
                "poste",
                "texte_source_poste",
                "raison_sociale_finess",
            ]
        )
    )

    if not text:
        return STRUCTURE_UNKNOWN

    social_keywords = [
        "mecs",
        "maison d enfants",
        "maison enfants caractere social",
        "foyer de l enfance",
        "foyer departemental enfance",
        "centre departemental enfance",
        "institut departemental enfance",
        "aide sociale enfance",
        "pouponniere",
        "chrs",
        "centre hebergement reinsertion sociale",
        "centre d hebergement",
    ]
    if any(keyword in text for keyword in social_keywords):
        return STRUCTURE_SOCIAL

    sanitaire_keywords = [
        "centre hospitalier",
        "hopital",
        "hospitalier",
        "chu",
        "chr",
        "ch ",
        "clinique",
        "etablissement de sante",
    ]
    if any(keyword in f" {text} " for keyword in sanitaire_keywords):
        return STRUCTURE_SANITAIRE

    medico_social_keywords = [
        "ehpad",
        "ssi ad",
        "ssiad",
        "usld",
        "epms",
        "epsms",
        "ime",
        "iem",
        "itep",
        "mas",
        "fam",
        "foyer de vie",
        "foyer d accueil medicalise",
        "foyer accueil medicalise",
        "foyer occupationnel",
        "esat",
        "sessad",
        "samsah",
        "savs",
        "camsp",
        "cmp p",
        "cmpp",
        "personnes agees",
        "handicap",
        "medico social",
        "medicosocial",
        "residence autonomie",
    ]
    if any(keyword in text for keyword in medico_social_keywords):
        return STRUCTURE_MEDICO_SOCIAL

    return STRUCTURE_UNKNOWN


def normalize_or_infer_establishment_type(row: pd.Series) -> str:
    """Normalise ou deduit un type d'etablissement plus fin pour le filtrage."""
    explicit_value = clean_display_value(row.get("type_etablissement", ""))
    if explicit_value:
        normalized = normalize_text(explicit_value)
        if "ehpad" in normalized and "sanitaire" in normalized:
            return ESTABLISHMENT_EHPAD_SANITAIRE
        if "ehpad" in normalized and ("autonome" in normalized or "public" in normalized):
            return ESTABLISHMENT_EHPAD_AUTONOME
        if "residence autonomie" in normalized or "foyer logement" in normalized:
            return ESTABLISHMENT_RESIDENCE_AUTONOMIE
        return explicit_value

    text = normalize_text(
        " ".join(
            clean_display_value(row.get(field, ""))
            for field in [
                "etablissements",
                "lieux_poste",
                "poste",
                "texte_source_poste",
                "raison_sociale_finess",
            ]
        )
    )
    structure_type = clean_display_value(row.get("type_structure", ""))

    if not text:
        return structure_type or ESTABLISHMENT_UNKNOWN

    if "residence autonomie" in text or "foyer logement" in text:
        return ESTABLISHMENT_RESIDENCE_AUTONOMIE

    if "ehpad" in text:
        if structure_type == STRUCTURE_SANITAIRE:
            return ESTABLISHMENT_EHPAD_SANITAIRE
        return ESTABLISHMENT_EHPAD_AUTONOME

    social_keywords = [
        "mecs",
        "maison d enfants",
        "maison enfants caractere social",
        "foyer de l enfance",
        "foyer departemental enfance",
        "centre departemental enfance",
        "institut departemental enfance",
        "aide sociale enfance",
        "pouponniere",
    ]
    if any(keyword in text for keyword in social_keywords):
        return ESTABLISHMENT_SOCIAL_CHILDHOOD

    if "epms" in text or "epsms" in text:
        return ESTABLISHMENT_EPMS

    adult_disability_keywords = [
        "mas",
        "fam",
        "foyer de vie",
        "foyer d accueil medicalise",
        "foyer accueil medicalise",
        "foyer occupationnel",
        "esat",
        "samsah",
        "savs",
    ]
    if any(keyword in text for keyword in adult_disability_keywords):
        return ESTABLISHMENT_HANDICAP_ADULT

    child_disability_keywords = [
        "ime",
        "iem",
        "itep",
        "sessad",
        "camsp",
        "cmpp",
    ]
    if any(keyword in text for keyword in child_disability_keywords):
        return ESTABLISHMENT_HANDICAP_CHILD

    if structure_type == STRUCTURE_SANITAIRE:
        return ESTABLISHMENT_SANITAIRE

    return structure_type or ESTABLISHMENT_UNKNOWN


def deduplicate_posts(df: pd.DataFrame) -> pd.DataFrame:
    """Dedoublonne sur une cle metier configurable dans le code."""
    work = df.copy()
    helper_columns = []
    for key in DEDUP_KEYS:
        helper = f"__dedup_{key}"
        helper_columns.append(helper)
        work[helper] = work[key].apply(normalize_text)
    return work.drop_duplicates(subset=helper_columns, keep="first").drop(columns=helper_columns)


def prepare_for_export(df: pd.DataFrame, default_missing: str) -> pd.DataFrame:
    """Remplace les textes vides par la valeur par defaut en conservant les coordonnees."""
    prepared = df.copy()
    for column in prepared.columns:
        if column in {"latitude", "longitude"}:
            continue
        prepared[column] = prepared[column].apply(lambda value: default_missing if is_missing(value) else value)
    return prepared


def export_control_csv(clean_result: CleanResult, config: dict[str, Any]) -> None:
    """Exporte les deux CSV de controle demandes."""
    valid_path = config["output_valid_csv_path"]
    missing_path = config["output_missing_coords_csv_path"]
    ensure_parent_dir(valid_path)
    ensure_parent_dir(missing_path)
    clean_result.valid_posts.to_csv(valid_path, index=False, encoding="utf-8-sig")
    clean_result.missing_coords.to_csv(missing_path, index=False, encoding="utf-8-sig")
    logger.info("CSV postes valides: %s", valid_path)
    logger.info("CSV postes sans coordonnees: %s", missing_path)


def geocode_missing_coordinates_placeholder(df: pd.DataFrame) -> pd.DataFrame:
    """Point d'extension futur pour geocoder les lignes sans coordonnees.

    Le geocodage automatique est volontairement desactive: les coordonnees
    utilisees par la carte proviennent uniquement du fichier Excel source.
    """
    return df
