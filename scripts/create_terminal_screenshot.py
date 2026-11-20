#!/usr/bin/env python3

import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BACKGROUND = "#171717"
HEADER = "#252526"
TEXT = "#D4D4D4"
GREEN = "#4EC9B0"
RED = "#F48771"
YELLOW = "#DCDCAA"


def strip_ansi(text):
    ansi_pattern = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_pattern.sub("", text)


def load_font(size):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    ]

    for font_path in font_paths:
        if Path(font_path).exists():
            return ImageFont.truetype(font_path, size)

    return ImageFont.load_default()


def create_screenshot(log_file, output_file):
    content = Path(log_file).read_text(
        encoding="utf-8",
        errors="replace",
    )

    content = strip_ansi(content)
    lines = content.splitlines()

    # Keep the image manageable for long test executions.
    max_lines = 100
    if len(lines) > max_lines:
        lines = [
            f"... showing last {max_lines} lines of {len(lines)} total lines ..."
        ] + lines[-max_lines:]

    font = load_font(14)
    header_font = load_font(15)

    padding = 20
    line_height = 22
    header_height = 42

    # Wrap long terminal lines.
    max_chars = 110
    wrapped_lines = []

    for line in lines:
        if not line:
            wrapped_lines.append("")
            continue

        wrapped_lines.extend(
            line[i:i + max_chars]
            for i in range(0, len(line), max_chars)
        )

    width = 1200
    height = header_height + padding * 2 + len(wrapped_lines) * line_height

    image = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(image)

    draw.rectangle(
        [(0, 0), (width, header_height)],
        fill=HEADER,
    )

    draw.text(
        (padding, 12),
        "Jenkins Test Execution",
        font=header_font,
        fill=GREEN,
    )

    y = header_height + padding

    for line in wrapped_lines:
        color = TEXT

        if "PASSED" in line or "passed" in line:
            color = GREEN
        elif "FAILED" in line or "failed" in line or "ERROR" in line:
            color = RED
        elif "WARNING" in line or "warning" in line:
            color = YELLOW

        draw.text(
            (padding, y),
            line,
            font=font,
            fill=color,
        )

        y += line_height

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    image.save(output_file)

    print(f"Screenshot created: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Jenkins terminal output into a PNG screenshot."
    )

    parser.add_argument("--input", required=True, help="Input log file")
    parser.add_argument("--output", required=True, help="Output PNG file")

    args = parser.parse_args()

    create_screenshot(args.input, args.output)