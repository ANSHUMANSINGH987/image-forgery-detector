"""Tests for the image forgery detection pipeline components."""

import cv2
import numpy as np
import pytest

# References:
# #file:src/preprocessor.py
# #file:src/ela_detector.py
# #file:src/copy_move.py
from src.copy_move import detect_copy_move
from src.ela_detector import compute_ela
from src.preprocessor import to_grayscale, load_image


def test_preprocessor_invalid_path(tmp_path):
	"""Loading a missing image path raises FileNotFoundError."""
	missing_path = tmp_path / "missing-image.jpg"

	with pytest.raises(FileNotFoundError):
		load_image(str(missing_path))


def test_grayscale_conversion():
	"""BGR input is converted to a 100x100 single-channel image."""
	image = np.zeros((100, 100, 3), dtype=np.uint8)

	grayscale = to_grayscale(image)

	assert grayscale.shape == (100, 100)


def test_ela_computation(tmp_path):
	"""ELA returns an 8-bit image and a positive discrepancy score."""
	rng = np.random.default_rng(42)
	image = rng.integers(0, 256, (100, 100, 3), dtype=np.uint8)
	image_path = tmp_path / "dummy.jpg"
	assert cv2.imwrite(str(image_path), image, [cv2.IMWRITE_JPEG_QUALITY, 95])

	ela_image, discrepancy_score = compute_ela(str(image_path))

	assert isinstance(ela_image, np.ndarray)
	assert ela_image.dtype == np.uint8
	assert isinstance(discrepancy_score, float)
	assert discrepancy_score > 0.0


def test_copy_move_synthetic_blank():
	"""A blank image produces no verified copy-move matches."""
	image = np.zeros((200, 200, 3), dtype=np.uint8)

	annotated_image, inlier_count = detect_copy_move(image)

	assert inlier_count == 0
	assert annotated_image.shape == image.shape
