"""Command-line interface for the image forgery detection pipeline."""

import argparse

import cv2

# References:
# #file:src/preprocessor.py
# #file:src/ela_detector.py
# #file:src/copy_move.py
# #file:src/visualizer.py
from src.copy_move import detect_copy_move
from src.ela_detector import compute_ela
from src.preprocessor import load_image, validate_dimensions
from src.visualizer import save_comparison_canvas


def build_parser() -> argparse.ArgumentParser:
	"""Build the command-line argument parser."""
	parser = argparse.ArgumentParser(
		description="Detect image splicing and copy-move forgery artifacts."
	)
	parser.add_argument(
		"-i",
		"--input",
		required=True,
		help="Path to the source image.",
	)
	parser.add_argument(
		"-o",
		"--output",
		default="outputs/result.jpg",
		help="Destination path for the comparison canvas.",
	)
	parser.add_argument(
		"-m",
		"--mode",
		choices=("ela", "copy-move", "full"),
		default="full",
		help="Detection mode to run.",
	)
	parser.add_argument(
		"-q",
		"--quality",
		type=int,
		default=90,
		help="JPEG quality level used for ELA.",
	)
	parser.add_argument(
		"-d",
		"--min-dist",
		type=float,
		default=40.0,
		help="Minimum spatial distance for copy-move matches.",
	)
	return parser


def _print_banner() -> None:
	"""Print the CLI header."""
	print("=" * 60)
	print("CSE3010 Image Forgery Detection CLI")
	print("=" * 60)


def main() -> int:
	"""Run the selected forgery detection workflow."""
	args = build_parser().parse_args()
	_print_banner()

	try:
		image = load_image(args.input)
		validate_dimensions(image)
		channels = 1 if image.ndim == 2 else image.shape[2]
		height, width = image.shape[:2]
		print(f"Input: {args.input}")
		print(f"Resolution: {width}x{height} | Channels: {channels}")

		processed_image = image.copy()
		if args.mode in ("ela", "full"):
			ela_image, discrepancy_score = compute_ela(args.input, args.quality)
			print(f"ELA discrepancy score: {discrepancy_score:.2f}")
			ela_verdict = (
				"SUSPICIOUS (Non-uniform compression)"
				if discrepancy_score > 3.5
				else "CLEAN"
			)
			print(f"ELA verdict: {ela_verdict}")
			processed_image = ela_image

		if args.mode in ("copy-move", "full"):
			copy_move_image, inlier_count = detect_copy_move(image, args.min_dist)
			print(f"Detected inlier matches: {inlier_count}")
			copy_move_verdict = (
				"FORGERY DETECTED" if inlier_count >= 5 else "NO CLONING DETECTED"
			)
			print(f"Copy-move verdict: {copy_move_verdict}")
			processed_image = copy_move_image

		save_comparison_canvas(
			image,
			processed_image,
			args.output,
			f"{args.mode.upper()} Analysis",
		)
		print(f"Inspection report saved to: {args.output}")
		return 0
	except Exception as error:
		print(f"Error: {error}")
		return 1


if __name__ == "__main__":
	raise SystemExit(main())
