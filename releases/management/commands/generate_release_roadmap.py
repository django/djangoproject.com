"""
Generates an SVG roadmap of Django releases, showing mainstream and extended
support periods based on the hardcoded release schedule in RELEASES.

Usage:
  python -m manage generate_release_roadmap

Produces an SVG at: ../djangoproject/static/img/release-roadmap.svg.
"""

import datetime as dtime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent.resolve()

OUTPUT_FILE = (
    settings.BASE_DIR / "djangoproject" / "static" / "img" / "release-roadmap.svg"
)

COLORS = {
    "mainstream": "#0C4B33",
    "extended": "#CBFDE9",
    "grid": "#000000",
    "month-grid": "#666666",
    "text": "#ffffff",
    "legend_text": "#000000",
    "text_lts": "#0C4B33",
    "bg": "none",
}

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
}

# TODO: Once the annual release cycle is established, consider generating
# future releases dynamically instead of maintaining this list manually.
# The annual schedule should make future release and support dates predictable.
#
# "is_lts" here draws a label on the graphic, and is not Release.is_lts, which
# is always set for a calendar version. The calendar releases below leave it
# off deliberately: under DEP 20 every one of them is supported for three
# years, which their bars already show, so a label on each would say nothing.
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
    help = "Generate Django release roadmap SVG."

    def handle(self, *args, **options):
        render_svg()


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


def generate_grids(start_year: int, end_year: int, config: dict) -> list:

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
                        COLORS["grid"] if is_january else COLORS["month-grid"]
                    ),
                }
            )
    return grid_lines


def generate_releases(data: list, start_year: int, config: dict) -> list:

    releases_processed = []
    for i, release in enumerate(data):
        bar_y = config["padding_top"] + (
            i * (config["bar_height"] + config["bar_v_spacing"])
        )
        text_y_center = bar_y + (config["bar_height"] / 2) + (config["font_size"] / 3)

        x_start = date_to_x(release["release_date"], start_year, config)
        x_end_mainstream = date_to_x(release["mainstream_end"], start_year, config)
        x_end_extended = date_to_x(release["extended_end"], start_year, config)

        mainstream_bar = {
            "x": x_start,
            "y": bar_y,
            "width": x_end_mainstream - x_start,
            "height": config["bar_height"],
            "fill": COLORS["mainstream"],
        }

        extended_bar = {
            "x": x_end_mainstream,
            "y": bar_y,
            "width": x_end_extended - x_end_mainstream,
            "height": config["bar_height"],
            "fill": COLORS["extended"],
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
                "mainstream_bar": mainstream_bar,
                "extended_bar": extended_bar,
                "version_text": version_text,
                "lts_text": lts_text,
            }
        )
    return releases_processed


def generate_legend(config: dict) -> dict:

    legend_y = (
        config["padding_top"] + 260
    )  # Fixed position for legend so that it doesn't conflict with month labels

    width = config["legend_box_size"] + 100
    height = config["legend_box_size"] + 24

    legend = {
        "mainstream_box": {
            "x": config["padding_left"],
            "y": legend_y - config["legend_box_size"] + 2,
            "size": config["legend_box_size"],
            "width": width,
            "height": height,
            "fill": COLORS["mainstream"],
        },
        "mainstream_text": {
            "x": config["padding_left"] + config["legend_box_size"] + 5,
            "y": legend_y,
            "fill": "#ffffff",
            "text": ["Mainstream", "Support"],
        },
        "extended_box": {
            "x": config["padding_left"] + width,
            "y": legend_y - config["legend_box_size"] + 2,
            "size": config["legend_box_size"],
            "width": width,
            "height": height,
            "fill": COLORS["extended"],
        },
        "extended_text": {
            "x": config["padding_left"] + config["legend_box_size"] + width + 8,
            "y": legend_y,
            "fill": "#000000",
            "text": ["Extended", "Support"],
        },
    }

    return legend


def render_svg():

    data = RELEASES

    start_year, end_year, svg_width = get_chart_timeline(data, CONFIG)
    svg_height = calculate_dimensions(CONFIG, len(data))

    grid_lines = generate_grids(start_year, end_year, CONFIG)
    releases_processed = generate_releases(data, start_year, CONFIG)

    legend = generate_legend(CONFIG)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("template.svg.jinja")

    output_svg = template.render(
        svg_width=svg_width,
        svg_height=svg_height,
        config=CONFIG,
        colors=COLORS,
        grid_lines=grid_lines,
        releases=releases_processed,
        legend=legend,
    )

    OUTPUT_FILE.write_text(output_svg)
