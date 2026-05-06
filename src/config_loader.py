"""Chargement et validation de la configuration YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.utils import resolve_path


REQUIRED_KEYS = {
    "input_excel_path",
    "sheet_name",
    "output_html_path",
    "output_valid_csv_path",
    "output_missing_coords_csv_path",
    "map_center_lat",
    "map_center_lon",
    "map_zoom",
    "marker_cluster_enabled",
    "deduplicate",
    "title",
    "subtitle",
    "institution_label",
    "default_missing_value",
    "category_colors",
    "column_aliases",
}


def load_config(config_path: str | Path = "config/settings.yaml") -> dict[str, Any]:
    """Charge la configuration et resout les chemins de fichiers."""
    project_root = Path(__file__).resolve().parents[1]
    path = resolve_path(config_path, project_root)
    if not path.exists():
        raise FileNotFoundError(f"Fichier de configuration introuvable: {path}")

    with path.open("r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream) or {}

    missing = sorted(REQUIRED_KEYS - set(config))
    if missing:
        raise ValueError("Parametres manquants dans settings.yaml: " + ", ".join(missing))

    config["project_root"] = project_root
    config["input_excel_path"] = resolve_path(config["input_excel_path"], project_root)
    config["output_html_path"] = resolve_path(config["output_html_path"], project_root)
    config["output_index_html_path"] = resolve_path(
        config.get("output_index_html_path", "output/index.html"), project_root
    )
    config["output_valid_csv_path"] = resolve_path(config["output_valid_csv_path"], project_root)
    config["output_missing_coords_csv_path"] = resolve_path(
        config["output_missing_coords_csv_path"], project_root
    )
    if config.get("finess_reference_csv_path"):
        config["finess_reference_csv_path"] = resolve_path(
            config["finess_reference_csv_path"], project_root
        )
    config["template_path"] = project_root / "templates" / "map_template.html"
    return config
