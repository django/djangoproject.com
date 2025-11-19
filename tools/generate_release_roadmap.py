"""
Generates an SVG roadmap of Django releases,
showing mainstream and extended support periods.

Usage:
    python generate_release_roadmap.py --first-release <VERSION> --date <YYYY-MM>

Arguments:
    --first-release   First release number in Django versioning style, e.g.,"4.2"
    --date            Release date of first release in YYYY-MM format, e.g.,"2023-04"

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
import os

from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_DIR = BASE_DIR

OUTPUT_FILE = os.path.join(
    BASE_DIR, "..", "djangoproject", "static", "img", "release-roadmap.svg"
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
    "pixels_per_year": 180,
    "bar_height": 28,
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


def generate_grids(start_year: int, end_year: int, config: dict) -> list:

    grid_lines = []
    pixels_per_year = config["pixels_per_year"]
    pixels_per_block = pixels_per_year / 3.0

    # Month labels only for the VERY FIRST set of lines
    FIRST_YEAR_MONTH_LABELS = {
        0: None,
        1: "Apr.",
        2: "Aug.",
        3: "Dec.",
    }
    for year_index, year in enumerate(range(start_year, end_year)):
        year_x_start = config["padding_left"] + (year_index * pixels_per_year)

        for line_index in range(4):
            x = year_x_start + (line_index * pixels_per_block)
            # Year label always on first line of each year
            top_label = str(year) if line_index == 0 else None
            # Month labels ONLY for the first year block
            if year_index == 0:
                bottom_label = FIRST_YEAR_MONTH_LABELS[line_index]
            else:
                bottom_label = None
            grid_lines.append(
                {
                    "x": x,
                    "width": (
                        config["year_line_width"]
                        if line_index == 0
                        else config["month_line_width"]
                    ),
                    "top_label": top_label,
                    "bottom_label": bottom_label,
                    "line-color": (
                        COLORS["grid"] if line_index == 0 else COLORS["month-grid"]
                    ),
                }
            )
    return grid_lines


def add_months(date: dtime.date, months: int) -> dtime.date:
    year = date.year + (date.month - 1 + months) // 12
    month = (date.month - 1 + months) % 12 + 1
    day = min(date.day, calendar.monthrange(year, month)[1])
    return dtime.date(year, month, day)


def generate_release_data(first_release: str, first_release_ym: str) -> list:
    """
    Generate 8 Django-style releases starting from a given first release.
    first_release: "4.2"
    first_release_ym: "2023-04"
    """
    major, minor = map(int, first_release.split("."))
    # Parse YYYY-MM → date
    release_date = dtime.datetime.strptime(first_release_ym, "%Y-%m").date()
    releases = []
    for i in range(8):
        curr_major = major + ((minor + i) // 3)
        curr_minor = (minor + i) % 3
        version = f"{curr_major}.{curr_minor}"
        is_lts = curr_minor == 2
        # Mainstream support lasts 8 months
        mainstream_end = add_months(release_date, 8)
        # Extended support
        if is_lts:
            # LTS = 28 months from release date
            extended_end = add_months(release_date, 28)
        else:
            # Non-LTS = 8 months after mainstream ends
            extended_end = add_months(mainstream_end, 8)
        releases.append(
            {
                "name": version,
                "is_lts": is_lts,
                "release_date": release_date,
                "mainstream_end": mainstream_end,
                "extended_end": extended_end,
            }
        )
        # Next release starts 8 months later
        release_date = add_months(release_date, 8)
    return releases


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
        config["padding_top"] + 200
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

    parser = argparse.ArgumentParser(description="Generate Django release roadmap SVG.")
    parser.add_argument(
        "--first-release", required=True, help="First release number, e.g., 4.2"
    )
    parser.add_argument(
        "--date", required=True, help="Release date in YYYY-MM format, e.g., 2023-04"
    )
    args = parser.parse_args()
    data = generate_release_data(args.first_release, args.date)

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

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output_svg)


if __name__ == "__main__":
    render_svg()
