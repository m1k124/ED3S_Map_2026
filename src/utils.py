"""Fonctions utilitaires partagees par le projet."""

from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path
from typing import Any


def setup_logging() -> None:
    """Configure des logs terminal sobres et lisibles."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def normalize_text(value: Any) -> str:
    """Normalise une chaine pour comparer des libelles de colonnes."""
    if value is None:
        return ""
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.replace("&", " et ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def ensure_parent_dir(path: Path) -> None:
    """Cree le dossier parent d'un fichier si necessaire."""
    path.parent.mkdir(parents=True, exist_ok=True)


def resolve_path(path_value: str | Path, project_root: Path) -> Path:
    """Retourne un chemin absolu, relatif a la racine projet si besoin."""
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path
    return project_root / path


def is_missing(value: Any) -> bool:
    """Detecte les valeurs vides courantes sans dependre de pandas."""
    if value is None:
        return True
    text = str(value).strip()
    return text == "" or text.lower() in {"nan", "none", "nat", "<na>"}
