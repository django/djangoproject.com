"""
Generates an SVG roadmap of Django releases, showing mainstream and extended support periods.

Usage:
    python generate_release_roadmap.py --first-release <VERSION> --date <YYYY-MM>

Arguments:
    --first-release    The first release number in Django versioning style, e.g., "4.2"
    --date             The release date of the first release in YYYY-MM format, e.g., "2023-04"

Behavior:
    - Automatically generates 8 consecutive Django releases:
        X.0, X.1, X.2 (LTS), X+1.0, X+1.1, X+1.2 (LTS), X+2.0, X+2.1
    - Mainstream support: 8 months per release
    - Extended support:
        - LTS releases (*.2) have 28 months total extended support
        - Non-LTS releases have 8 months of extended support beyond mainstream
    - Produces an SVG at: ../djangoproject/static/img/release-roadmap.svg
"""

import argparse
import calendar
import datetime as dtime
import json
import os

from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = BASE_DIR
OUTPUT_FILE = os.path.join(
    BASE_DIR, "..", "djangoproject", "static", "img", "release-roadmap.svg"
)


def load_release_data(json_file):
    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)

    processed_data = []
    for item in data:
        item["release_date"] = dtime.datetime.strptime(
            item["release_date"], "%Y-%m-%d"
        ).date()
        item["mainstream_end"] = dtime.datetime.strptime(
            item["mainstream_end"], "%Y-%m-%d"
        ).date()
        item["extended_end"] = dtime.datetime.strptime(
            item["extended_end"], "%Y-%m-%d"
        ).date()
        processed_data.append(item)
    return processed_data


COLORS = {
    "mainstream": "#0C4B33",
    "extended": "#CBFDE9",
    "grid": "#333333",
    "text": "#FFFFFF",
    "text_lts": "#0C4B33",
    "bg": "#000000",
}

CONFIG = {
    "pixels_per_year": 120,
    "bar_height": 20,
    "bar_v_spacing": 20,
    "padding_top": 30,
    "padding_bottom": 20,
    "padding_left": 20,
    "padding_right": 10,
    "font_family": "'Segoe UI', 'Arial'",
    "font_size": 12,
    "font_size_small": 10,
    "font_weight": "bold",
    "font_weight_lts": "600",
    "font_style_lts": "italic",
    "legend_box_size": 14,
    "legend_spacing": 150,
    "text_padding_x": 10,
    "year_line_width": 3,
    "month_line_width": 1,
}


def get_chart_timeline(data, config):

    start_year = data[0]["release_date"].year

    max_end_date = max(d["extended_end"] for d in data)

    end_year = max_end_date.year + 1

    total_years = end_year - start_year
    chart_width = total_years * config["pixels_per_year"]
    svg_width = chart_width + config["padding_left"] + config["padding_right"]

    return start_year, end_year, int(svg_width)


def calculate_dimensions(config, num_releases):

    chart_height = (
        config["padding_top"]
        + config["padding_bottom"]
        + (num_releases * config["bar_height"])
        + ((num_releases - 1) * config["bar_v_spacing"])
    )
    return int(chart_height)


def date_to_x(date, start_year, config):

    pixels_per_year = config["pixels_per_year"]
    pixels_per_block = pixels_per_year / 3.0
    start_x = config["padding_left"]

    year_offset = (date.year - start_year) * pixels_per_year

    if 1 <= date.month <= 4:

        block_num = 0
    elif 5 <= date.month <= 8:

        block_num = 1
    else:

        block_num = 2

    block_x_end = year_offset + ((block_num + 1) * pixels_per_block)

    return start_x + block_x_end


def generate_grids(start_year, end_year, config):

    grid_lines = []
    pixels_per_year = config["pixels_per_year"]
    pixels_per_block = pixels_per_year / 3.0

    for i, year in enumerate(range(start_year, end_year + 1)):
        year_x_start = config["padding_left"] + (i * pixels_per_year)

        for i in range(3):
            grid_lines.append(
                {
                    "x": year_x_start + (i * pixels_per_block),
                    "width": (
                        config["year_line_width"]
                        if i == 0
                        else config["month_line_width"]
                    ),
                    "label": str(year) if i == 0 else None,
                }
            )
    return grid_lines


def generate_releases(data, start_year, config):

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


def generate_legend(config, svg_height):

    legend_y = svg_height - (config["padding_bottom"] / 2)
    legend2_x = config["padding_left"] + config["legend_spacing"]

    legend = {
        "mainstream_box": {
            "x": config["padding_left"],
            "y": legend_y - config["legend_box_size"] + 2,
            "size": config["legend_box_size"],
            "fill": COLORS["mainstream"],
        },
        "mainstream_text": {
            "x": config["padding_left"] + config["legend_box_size"] + 5,
            "y": legend_y,
            "text": "Mainstream Support",
        },
        "extended_box": {
            "x": legend2_x,
            "y": legend_y - config["legend_box_size"] + 2,
            "size": config["legend_box_size"],
            "fill": COLORS["extended"],
        },
        "extended_text": {
            "x": legend2_x + config["legend_box_size"] + 5,
            "y": legend_y,
            "text": "Extended Support",
        },
    }
    return legend


def render_svg():

    data = load_release_data("release-data.json")

    start_year, end_year, svg_width = get_chart_timeline(data, CONFIG)
    svg_height = calculate_dimensions(CONFIG, len(data))

    grid_lines = generate_grids(start_year, end_year, CONFIG)
    releases_processed = generate_releases(data, start_year, CONFIG)

    legend = generate_legend(CONFIG, svg_height)

    env = Environment(loader=FileSystemLoader("."))
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

    outfile = "../djangoproject/static/img/release-roadmap.svg"

    with open(outfile, "w", encoding="utf-8") as f:
        f.write(output_svg)


if __name__ == "__main__":
    render_svg()
