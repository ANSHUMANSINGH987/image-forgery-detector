# CSE3010 Image Forgery Detection CLI

> A lightweight, explainable computer-vision toolkit for investigating image splicing and copy-move manipulation.

This project uses classical forensic techniques rather than a trained machine-learning model. It combines JPEG Error Level Analysis (ELA) with SIFT feature matching and RANSAC geometric verification, then exports a visual comparison canvas for inspection.

The workflow is intentionally transparent: every score, threshold, and annotated match can be traced back to a small Python module.

## What It Detects

### Error Level Analysis

ELA saves the source image as a JPEG at a selected quality level and compares the recompressed pixels with the original pixels. Areas with different compression histories can produce stronger residuals than the surrounding image.

The CLI reports the mean pixel discrepancy and applies this project threshold:

| Score | CLI verdict |
| --- | --- |
| Greater than `3.5` | `SUSPICIOUS (Non-uniform compression)` |
| `3.5` or lower | `CLEAN` |

ELA is a clue, not proof. A high score can also result from a heavily compressed, edited, or repeatedly saved image.

### Copy-Move Detection

Copy-move detection looks for duplicated content within the same image:

1. Convert the BGR image to grayscale.
2. Extract SIFT keypoints and descriptors.
3. Match descriptors against themselves with a brute-force L2 matcher.
4. Apply Lowe's ratio test and discard nearby matches.
5. Use a RANSAC homography to keep geometrically consistent matches.
6. Draw verified matches in red on the output image.

The CLI applies this project threshold:

| Verified inliers | CLI verdict |
| --- | --- |
| `5` or more | `FORGERY DETECTED` |
| Fewer than `5` | `NO CLONING DETECTED` |

These thresholds are practical heuristics, not a legal or scientific certification of authenticity.

## Features

- Pure Python pipeline using OpenCV, NumPy, Pillow, and Matplotlib-compatible dependencies.
- No Torch, TensorFlow, or other heavy machine-learning frameworks.
- Three detection modes: ELA, copy-move, or both.
- Input validation for missing files, unreadable images, and undersized images.
- Aspect-ratio-preserving preprocessing helpers.
- Visual output with original/analyzed panels and a project title banner.
- Focused pytest coverage for the core pipeline.

## Requirements

- Python 3.10 or newer recommended. The project has been developed with Python 3.12.
- OpenCV with SIFT support. The standard `opencv-python` package is used.
- A readable image file such as JPEG, PNG, or another format supported by OpenCV/Pillow.

Install the dependencies from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On macOS or Linux:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Quick Start

Run the complete pipeline on an image:

```powershell
python cli.py --input samples/example.jpg --output outputs/result.jpg --mode full
```

Short options are also available:

```powershell
python cli.py -i samples/example.jpg -o outputs/result.jpg -m full
```

On success, the command prints the input resolution, ELA score, copy-move inlier count, verdicts, and saved output path. The comparison canvas is written to `outputs/result.jpg` unless another path is supplied.

## Command-Line Options

| Option | Default | Description |
| --- | --- | --- |
| `-i`, `--input` | Required | Path to the source image. |
| `-o`, `--output` | `outputs/result.jpg` | Destination for the comparison canvas. Parent directories are created automatically. |
| `-m`, `--mode` | `full` | Select `ela`, `copy-move`, or `full`. |
| `-q`, `--quality` | `90` | JPEG quality used during ELA recompression. Valid range: `0` to `100`. |
| `-d`, `--min-dist` | `40.0` | Minimum pixel distance between candidate copy-move keypoints. |

### ELA-only analysis

```powershell
python cli.py -i samples/example.jpg -o outputs/ela-result.jpg -m ela -q 90
```

### Copy-move-only analysis

```powershell
python cli.py -i samples/example.jpg -o outputs/copy-move-result.jpg -m copy-move -d 40
```

### Full analysis

```powershell
python cli.py -i samples/example.jpg -o outputs/full-result.jpg -m full
```

In `full` mode, both detectors run and both verdicts are printed. The saved comparison canvas uses the final annotated detector image, which is the copy-move result because that stage runs after ELA. The ELA score remains available in the terminal output.

## Reading the Output

The generated canvas contains:

- A black 50-pixel banner with `CSE3010 Lab Project` and the selected analysis mode.
- The original image on the left, labeled `Original Image`.
- The analyzed result on the right, labeled `Analyzed Result`.
- Red lines and endpoint circles for copy-move matches that survived RANSAC.

The output is an inspection aid. Review it together with the terminal score and the source image's provenance.

## Project Layout

```text
image-forgery-detector/
├── cli.py                    # Argparse entry point and workflow orchestration
├── requirements.txt          # Runtime and test dependencies
├── README.md                 # This guide
├── samples/                  # Input images for local experiments
├── outputs/                  # Generated comparison canvases
├── src/
│   ├── __init__.py
│   ├── preprocessor.py       # Loading, validation, grayscale, resizing
│   ├── ela_detector.py       # JPEG residual analysis
│   ├── copy_move.py          # SIFT matching and RANSAC verification
│   └── visualizer.py         # Comparison canvas export
└── tests/
	├── __init__.py
	└── test_pipeline.py      # Core unit tests
```

## Python API

The modules can also be used without the CLI:

```python
from src.copy_move import detect_copy_move
from src.ela_detector import compute_ela
from src.preprocessor import load_image, validate_dimensions
from src.visualizer import save_comparison_canvas

image = load_image("samples/example.jpg")
validate_dimensions(image)

ela_image, ela_score = compute_ela("samples/example.jpg")
copy_move_image, inliers = detect_copy_move(image)

save_comparison_canvas(
	image,
	copy_move_image,
	"outputs/api-result.jpg",
	"Full Analysis",
)
```

Important function contracts:

- `load_image(path)` returns an OpenCV BGR `numpy.ndarray`.
- `validate_dimensions(image)` requires both dimensions to be at least `128` pixels by default.
- `compute_ela(path)` returns `(ela_image_bgr, mean_discrepancy_score)`.
- `detect_copy_move(image)` returns `(annotated_image, verified_inlier_count)`.
- `save_comparison_canvas(...)` creates missing output directories and writes the final image.

## Testing

Run the project test suite from the repository root:

```powershell
python -m pytest -q
```

The tests cover missing-file handling, grayscale conversion, ELA output typing and scoring, and the blank-image copy-move fallback.

## Troubleshooting

### `Image file not found`

Check that the path is correct relative to the directory where the command is running. An absolute path removes ambiguity:

```powershell
python cli.py -i "C:\path\to\image.jpg"
```

### The image is too small

The default preprocessing guard requires at least `128 x 128` pixels for reliable feature extraction. Use a larger source image rather than upscaling a tiny image.

### The output is not where expected

The CLI creates an image canvas, not a PDF report. By default it writes to `outputs/result.jpg`. Use `--output` to choose an explicit path:

```powershell
python cli.py -i samples/example.jpg -o outputs/my-report.jpg
```

### ELA score is unexpectedly high

ELA is sensitive to the source image's JPEG history, quality setting, and prior editing. Compare results at more than one quality level and treat the score as evidence requiring context, not as a standalone verdict.

### No copy-move matches are found

SIFT needs visible, repeatable texture. Blank, smooth, low-resolution, strongly blurred, or heavily compressed images may produce too few keypoints. The detector also intentionally removes matches closer than `--min-dist` pixels.

## Limitations

- This is a forensic screening tool, not an authenticity guarantee.
- JPEG recompression can create false positives in ELA.
- SIFT performance depends on image texture, scale, blur, and resolution.
- Copy-move detection currently visualizes verified inlier matches but does not produce a localized mask or confidence map.
- The current CLI saves one analyzed panel. In full mode, both detector results are printed, while the final panel displays the copy-move annotation.

## Responsible Use

Use the output to guide further investigation. Preserve the original file, record the command and parameters used, and avoid treating an automated verdict as conclusive evidence without independent validation.