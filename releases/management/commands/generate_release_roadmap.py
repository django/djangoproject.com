"""
Generates SVG roadmaps of Django releases (light and dark mode), showing mainstream,
extended, and end-of-life support periods with color coding, EOL labels, and a "today" line.

Usage:
  python -m manage generate_release_roadmap

Produces SVGs at:
  ../djangoproject/static/img/release-roadmap.svg
  ../djangoproject/static/img/release-roadmap-dark.svg
"""

import datetime as dtime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent.resolve()
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

OUTPUT_FILE = BASE_DIR / "djangoproject" / "static" / "img" / "release-roadmap.svg"
OUTPUT_FILE_DARK = (
    BASE_DIR / "djangoproject" / "static" / "img" / "release-roadmap-dark.svg"
)

COLORS_LIGHT = {
    "bg": "none",
    "mainstream": "#0C4B33",
    "extended": "#E6A100",
    "eol": "#C0392B",
    "grid": "#000000",
    "month_grid": "#666666",
    "text": "#ffffff",
    "text_dark": "#000000",
    "legend_text": "#000000",
    "text_lts": "#000000",
    "today": "#2563EB",
    "stroke_mainstream": "#0C4B33",
    "stroke_extended": "#E6A100",
    "stroke_eol": "#C0392B",
    "fade_color": "#ffffff",
    "month_stroke": "#ffffff",
}

COLORS_DARK = {
    "bg": "none",
    "mainstream": "#1B7353",
    "extended": "#F5A623",
    "eol": "#E53935",
    "grid": "#ffffff",
    "month_grid": "#888888",
    "text": "#ffffff",
    "text_dark": "#000000",
    "legend_text": "#ffffff",
    "text_lts": "#000000",
    "today": "#60A5FA",
    "stroke_mainstream": "#1B7353",
    "stroke_extended": "#F5A623",
    "stroke_eol": "#E53935",
    "fade_color": "#1f2122",
    "month_stroke": "#1f2122",
}

# Default backwards-compatible dictionary for imports
COLORS = COLORS_LIGHT

CONFIG = {
    "pixels_per_year": 120,
    "bar_height": 32,
    "bar_v_spacing": 10,
    "padding_top": 30,
    "padding_bottom": 20,
    "padding_left": 20,
    "padding_right": 10,
    "font_family": "'Segoe UI', 'Arial'",
    "font_size": 18,
    "font_weight": "bold",
    "font_weight_lts": "600",
    "font_style_lts": "italic",
    "legend_box_size": 16,
    "legend_padding": 50,
    "text_padding_x": 10,
    "year_line_width": 3,
    "month_line_width": 1,
    "today_line_width": 2,
}

# TODO: Once the annual release cycle is established, consider generating
# future releases dynamically instead of maintaining this list manually.
# The annual schedule should make future release and support dates predictable.
RELEASES = [
    {
        "name": "5.2",
        "is_lts": True,
        "release_date": dtime.date(2025, 4, 1),
        "mainstream_end": dtime.date(2025, 12, 1),
        "extended_end": dtime.date(2028, 4, 1),
    },
    {
        "name": "6.0",
        "is_lts": False,
        "release_date": dtime.date(2025, 12, 1),
        "mainstream_end": dtime.date(2026, 8, 1),
        "extended_end": dtime.date(2027, 4, 1),
    },
    {
        "name": "6.1",
        "is_lts": False,
        "release_date": dtime.date(2026, 8, 1),
        "mainstream_end": dtime.date(2027, 4, 1),
        "extended_end": dtime.date(2027, 12, 1),
    },
    {
        "name": "6.2",
        "is_lts": True,
        "release_date": dtime.date(2027, 4, 1),
        "mainstream_end": dtime.date(2027, 12, 1),
        "extended_end": dtime.date(2030, 4, 1),
    },
    {
        "name": "2028",
        "is_lts": False,
        "release_date": dtime.date(2028, 1, 1),
        "mainstream_end": dtime.date(2029, 1, 1),
        "extended_end": dtime.date(2031, 1, 1),
    },
    {
        "name": "2029",
        "is_lts": False,
        "release_date": dtime.date(2029, 1, 1),
        "mainstream_end": dtime.date(2030, 1, 1),
        "extended_end": dtime.date(2032, 1, 1),
    },
    {
        "name": "2030",
        "is_lts": False,
        "release_date": dtime.date(2030, 1, 1),
        "mainstream_end": dtime.date(2031, 1, 1),
        "extended_end": dtime.date(2033, 1, 1),
    },
]


class Command(BaseCommand):
    help = "Generate Django release roadmap SVGs (light and dark mode)."

    def handle(self, *args, **options):
        generate_roadmaps()


def get_chart_timeline(data: list, config: dict):
    start_year = data[0]["release_date"].year
    max_end_date = max(d["extended_end"] for d in data)
    end_year = max_end_date.year + 1

    total_years = end_year - start_year
    chart_width = total_years * config["pixels_per_year"]
    svg_width = chart_width + config["padding_left"] + config["padding_right"]

    return start_year, end_year, int(svg_width)


def calculate_dimensions(config: dict, num_releases: int) -> int:
    chart_height = (
        config["padding_top"]
        + config["padding_bottom"]
        + (num_releases * config["bar_height"])
        + ((num_releases - 1) * config["bar_v_spacing"])
    )
    return int(chart_height)


def date_to_x(date: dtime.date, start_year: int, config: dict) -> float:
    year_offset = (date.year - start_year) * config["pixels_per_year"]
    month_offset = (date.month - 1) / 12 * config["pixels_per_year"]
    return config["padding_left"] + year_offset + month_offset


def generate_today_line(
    today: dtime.date, start_year: int, end_year: int, config: dict
) -> dict | None:
    if start_year <= today.year < end_year:
        return {
            "x": date_to_x(today, start_year, config),
            "label": "Today",
        }
    return None


def generate_grids(start_year: int, end_year: int, config: dict, colors: dict) -> list:
    grid_lines = []
    pixels_per_year = config["pixels_per_year"]

    # TODO: Simplify the grid once the pre-annual release cadence is no longer
    # relevant. Django 6.2 is the last release whose support dates require an
    # April marker. Once 6.2 is no longer shown, the roadmap only needs year lines.
    month_lines = (
        (1, None),
        (4, "April"),
        (8, "August"),
        (12, "December"),
    )
    for year_index, year in enumerate(range(start_year, end_year)):
        year_x_start = config["padding_left"] + (year_index * pixels_per_year)

        for month, month_label in month_lines:
            is_january = month == 1
            x = year_x_start + ((month - 1) / 12 * pixels_per_year)

            grid_lines.append(
                {
                    "x": x,
                    "width": (
                        config["year_line_width"]
                        if is_january
                        else config["month_line_width"]
                    ),
                    "top_label": str(year) if is_january else None,
                    "bottom_label": month_label if year_index == 0 else None,
                    "line-color": (
                        colors["grid"] if is_january else colors["month_grid"]
                    ),
                }
            )
    return grid_lines


def generate_releases(
    data: list, start_year: int, config: dict, today: dtime.date, colors: dict
) -> list:
    releases_processed = []
    for i, release in enumerate(data):
        bar_y = config["padding_top"] + (
            i * (config["bar_height"] + config["bar_v_spacing"])
        )
        text_y_center = bar_y + (config["bar_height"] / 2) + (config["font_size"] / 3)

        x_start = date_to_x(release["release_date"], start_year, config)
        x_end_mainstream = date_to_x(release["mainstream_end"], start_year, config)
        x_end_extended = date_to_x(release["extended_end"], start_year, config)

        is_eol = release["extended_end"] <= today

        if is_eol:
            eol_bar = {
                "x": x_start,
                "y": bar_y,
                "width": x_end_extended - x_start,
                "height": config["bar_height"],
                "fill": colors["eol"],
                "stroke": colors["stroke_eol"],
            }
            version_text = {
                "x": x_start + config["text_padding_x"],
                "y": text_y_center,
                "text": release["name"],
            }
            eol_text = {
                "x": x_start + (x_end_extended - x_start) / 2,
                "y": text_y_center,
                "text": "End of life",
            }
            releases_processed.append(
                {
                    "is_eol": True,
                    "eol_bar": eol_bar,
                    "version_text": version_text,
                    "eol_text": eol_text,
                }
            )
        else:
            mainstream_bar = {
                "x": x_start,
                "y": bar_y,
                "width": x_end_mainstream - x_start,
                "height": config["bar_height"],
                "fill": colors["mainstream"],
                "stroke": colors["stroke_mainstream"],
            }

            extended_bar = {
                "x": x_end_mainstream,
                "y": bar_y,
                "width": x_end_extended - x_end_mainstream,
                "height": config["bar_height"],
                "fill": colors["extended"],
                "stroke": colors["stroke_extended"],
            }

            version_text = {
                "x": x_start + config["text_padding_x"],
                "y": text_y_center,
                "text": release["name"],
            }

            lts_text = None
            if release.get("is_lts", False):
                lts_text = {
                    "x": x_end_mainstream + config["text_padding_x"],
                    "y": text_y_center,
                    "text": "LTS",
                }

            releases_processed.append(
                {
                    "is_eol": False,
                    "mainstream_bar": mainstream_bar,
                    "extended_bar": extended_bar,
                    "version_text": version_text,
                    "lts_text": lts_text,
                }
            )
    return releases_processed


def generate_legend(config: dict, num_releases: int, colors: dict) -> tuple[dict, int]:
    legend_y = (
        config["padding_top"]
        + (num_releases * (config["bar_height"] + config["bar_v_spacing"]))
        + 25
    )
    width = config["legend_box_size"] + 90
    height = config["legend_box_size"] + 24
    x_offset = config["padding_left"] + config["legend_padding"]

    legend = {
        "mainstream_box": {
            "x": x_offset,
            "y": legend_y - config["legend_box_size"] + 2,
            "size": config["legend_box_size"],
            "width": width,
            "height": height,
            "fill": colors["mainstream"],
            "stroke": colors["stroke_mainstream"],
        },
        "mainstream_text": {
            "x": x_offset + config["legend_box_size"] + 5,
            "y": legend_y,
            "fill": "#ffffff",
            "text": ["Mainstream", "Support"],
        },
        "extended_box": {
            "x": x_offset + width + 10,
            "y": legend_y - config["legend_box_size"] + 2,
            "size": config["legend_box_size"],
            "width": width,
            "height": height,
            "fill": colors["extended"],
            "stroke": colors["stroke_extended"],
        },
        "extended_text": {
            "x": x_offset + width + 10 + config["legend_box_size"] + 5,
            "y": legend_y,
            "fill": "#000000",
            "text": ["Extended", "Support"],
        },
        "eol_box": {
            "x": x_offset + (width + 10) * 2,
            "y": legend_y - config["legend_box_size"] + 2,
            "size": config["legend_box_size"],
            "width": width,
            "height": height,
            "fill": colors["eol"],
            "stroke": colors["stroke_eol"],
        },
        "eol_text": {
            "x": x_offset + (width + 10) * 2 + config["legend_box_size"] + 5,
            "y": legend_y,
            "fill": "#ffffff",
            "text": ["End of", "Life"],
        },
    }

    svg_height = int(legend_y + height + config["padding_bottom"])
    return legend, svg_height


def render_svg(theme: str = "light", today: dtime.date | None = None) -> str:
    colors = COLORS_DARK if theme == "dark" else COLORS_LIGHT
    if today is None:
        today = dtime.date.today()

    data = RELEASES

    start_year, end_year, svg_width = get_chart_timeline(data, CONFIG)
    legend, svg_height = generate_legend(CONFIG, len(data), colors)

    grid_lines = generate_grids(start_year, end_year, CONFIG, colors)
    today_line = generate_today_line(today, start_year, end_year, CONFIG)
    releases_processed = generate_releases(data, start_year, CONFIG, today, colors)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("template.svg.jinja")

    return template.render(
        svg_width=svg_width,
        svg_height=svg_height,
        config=CONFIG,
        colors=colors,
        grid_lines=grid_lines,
        today_line=today_line,
        releases=releases_processed,
        legend=legend,
    )


def generate_roadmaps(today: dtime.date | None = None):
    OUTPUT_FILE.write_text(render_svg("light", today=today))
    OUTPUT_FILE_DARK.write_text(render_svg("dark", today=today))
