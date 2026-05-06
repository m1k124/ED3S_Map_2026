"""Generation du fichier HTML autonome a partir du template Jinja2."""

from __future__ import annotations

import json
import logging
from typing import Any

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.utils import ensure_parent_dir


logger = logging.getLogger(__name__)


def render_map_html(posts: pd.DataFrame, config: dict[str, Any]) -> None:
    """Rend la carte HTML avec les donnees integrees en JSON."""
    template_path = config["template_path"]
    if not template_path.exists():
        raise FileNotFoundError(f"Template HTML introuvable: {template_path}")

    records = posts.where(pd.notna(posts), None).to_dict(orient="records")
    posts_json = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
    category_colors_json = json.dumps(config["category_colors"], ensure_ascii=False)

    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        autoescape=select_autoescape(enabled_extensions=("html", "xml")),
    )
    template = env.get_template(template_path.name)
    html = template.render(
        posts_json=posts_json,
        category_colors_json=category_colors_json,
        total_posts=len(records),
        title=config["title"],
        subtitle=config["subtitle"],
        institution_label=config["institution_label"],
        default_missing_value=config["default_missing_value"],
        map_center_lat=config["map_center_lat"],
        map_center_lon=config["map_center_lon"],
        map_zoom=config["map_zoom"],
        marker_cluster_enabled=str(config["marker_cluster_enabled"]).lower(),
    )

    output_path = config["output_html_path"]
    ensure_parent_dir(output_path)
    output_path.write_text(html, encoding="utf-8")
    logger.info("HTML genere: %s", output_path)
