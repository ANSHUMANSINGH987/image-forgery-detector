"""Utilities for saving image-analysis comparison canvases."""

import os

import cv2
import numpy as np


def save_comparison_canvas(
	original: np.ndarray,
	processed: np.ndarray,
	output_path: str,
	title: str,
) -> None:
	"""Save original and processed images side by side with a title banner.

	Args:
		original: Original image in grayscale or BGR format.
		processed: Analyzed image in grayscale or BGR format.
		output_path: Destination path for the combined image.
		title: Project-specific title shown in the banner.

	Raises:
		ValueError: If either image is empty or has an unsupported shape.
		OSError: If the combined canvas cannot be written.
	"""
	original_bgr = _as_bgr_image(original)
	processed_bgr = _as_bgr_image(processed)
	target_height = min(original_bgr.shape[0], processed_bgr.shape[0])

	original_resized = _resize_to_height(original_bgr, target_height)
	processed_resized = _resize_to_height(processed_bgr, target_height)
	cv2.putText(
		original_resized,
		"Original Image",
		(10, 30),
		cv2.FONT_HERSHEY_SIMPLEX,
		0.8,
		(255, 255, 255),
		2,
		cv2.LINE_AA,
	)
	cv2.putText(
		processed_resized,
		"Analyzed Result",
		(10, 30),
		cv2.FONT_HERSHEY_SIMPLEX,
		0.8,
		(255, 255, 255),
		2,
		cv2.LINE_AA,
	)

	comparison = np.hstack((original_resized, processed_resized))
	banner = np.zeros((50, comparison.shape[1], 3), dtype=np.uint8)
	cv2.putText(
		banner,
		f"CSE3010 Lab Project: {title}",
		(10, 33),
		cv2.FONT_HERSHEY_SIMPLEX,
		0.8,
		(255, 255, 255),
		2,
		cv2.LINE_AA,
	)
	canvas = np.vstack((banner, comparison))

	parent_directory = os.path.dirname(output_path)
	os.makedirs(parent_directory or ".", exist_ok=True)
	if not cv2.imwrite(output_path, canvas):
		raise OSError(f"Unable to save comparison canvas: {output_path}")


def _as_bgr_image(image: np.ndarray) -> np.ndarray:
	"""Return a non-empty grayscale or BGR image as a 3-channel array."""
	if not isinstance(image, np.ndarray) or image.size == 0:
		raise ValueError("image must be a non-empty NumPy array")
	if image.ndim == 2:
		return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
	if image.ndim == 3 and image.shape[2] == 3:
		return image.copy()
	raise ValueError("image must be a grayscale or 3-channel BGR array")


def _resize_to_height(image: np.ndarray, target_height: int) -> np.ndarray:
	"""Resize an image to a target height while preserving its aspect ratio."""
	if image.shape[0] == target_height:
		return image

	scale = target_height / image.shape[0]
	target_width = max(1, round(image.shape[1] * scale))
	return cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_AREA)
