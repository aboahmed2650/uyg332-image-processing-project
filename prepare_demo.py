"""Create synthetic inputs and a clean copy of the image-processing notebook."""

import argparse
import json
import tempfile
from pathlib import Path

import cv2
import numpy as np


NOTEBOOK = "UYG332Image_Processing_Final_Project.ipynb"


def sample_images():
    rng = np.random.default_rng(332)
    y, x = np.indices((192, 256))
    ramp = (x * 255 / (x.shape[1] - 1)).astype(np.uint8)

    color = cv2.merge((ramp, np.flipud((y * 1.3).astype(np.uint8)), 255 - ramp))
    cv2.circle(color, (80, 82), 40, (40, 200, 220), -1)
    cv2.rectangle(color, (150, 65), (223, 145), (200, 55, 80), -1)

    gray = ((ramp.astype(float) + y) / 2).astype(np.uint8)
    cv2.circle(gray, (94, 93), 44, 180, -1)
    dark = np.clip(gray.astype(float) ** 2 / 400, 0, 255).astype(np.uint8)

    textured = np.full(x.shape, 25, dtype=np.uint8)
    cv2.circle(textured, (128, 96), 80, 150, -1)
    for cx, cy, radius in [(90, 75, 16), (157, 105, 20), (120, 132, 12)]:
        cv2.circle(textured, (cx, cy), radius, 84, -1)
    textured = cv2.GaussianBlur(textured, (7, 7), 1.2)

    circuit = np.full(x.shape, 66, dtype=np.uint8)
    for row in range(28, 180, 30):
        cv2.line(circuit, (16, row), (238, row), 160, 3)
        cv2.circle(circuit, (60 + row // 3, row), 6, 218, -1)
    noise = rng.random(x.shape)
    circuit[noise < 0.04] = 0
    circuit[noise > 0.96] = 255

    low_contrast = np.rint(118 + 8 * np.cos(x / 13) + 5 * np.sin(y / 9)).astype(np.uint8)
    return {
        "tf2_engineer.jpg": color,
        "einstein.tif": gray,
        "pout.tif": dark,
        "moon.tif": textured,
        "pcb.tif": circuit,
        "pollen.tif": low_contrast,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("demo"),
                        help="New directory to create (default: demo)")
    output = parser.parse_args().output.resolve()
    notebook = Path(__file__).with_name(NOTEBOOK)
    if not notebook.is_file():
        parser.error(f"Place this script next to {NOTEBOOK}.")
    if output.exists():
        parser.error(f"{output} already exists. Choose another directory with --output.")
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(dir=output.parent) as staging:
        ready = Path(staging) / "demo"
        ready.mkdir()
        for filename, pixels in sample_images().items():
            if not cv2.imwrite(str(ready / filename), pixels):
                raise OSError(f"Could not write {filename}")
        document = json.loads(notebook.read_text(encoding="utf-8"))
        for cell in document["cells"]:
            if cell["cell_type"] == "code":
                cell["execution_count"] = None
                cell["outputs"] = []
        (ready / NOTEBOOK).write_text(json.dumps(document, ensure_ascii=False, indent=1) + "\n",
                                     encoding="utf-8")
        ready.rename(output)
    print(f"Open {output / NOTEBOOK} in Jupyter and run all cells.")


if __name__ == "__main__":
    main()
