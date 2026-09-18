"""Image loading, validation, and preprocessing helpers."""

from pathlib import Path

import cv2
import numpy as np


def load_image(image_path: str) -> np.ndarray:
	"""Load an image from ``image_path`` as a BGR NumPy array.

	Args:
		image_path: Path to the image file.

	Returns:
		The decoded image in OpenCV's standard BGR channel order.

	Raises:
		FileNotFoundError: If ``image_path`` does not exist or is not a file.
		ValueError: If the file exists but cannot be decoded as an image.
	"""
	path = Path(image_path)
	if not path.is_file():
		raise FileNotFoundError(f"Image file not found: {image_path}")

	image = cv2.imread(str(path), cv2.IMREAD_COLOR)
	if image is None:
		raise ValueError(f"Unable to decode image file: {image_path}")

	return image


def validate_dimensions(image: np.ndarray, min_size: int = 128) -> bool:
	"""Validate that an image is large enough for feature extraction.

	Args:
		image: Image array whose first two dimensions are height and width.
		min_size: Minimum required height and width in pixels.

	Returns:
		``True`` when both image dimensions meet ``min_size``.

	Raises:
		ValueError: If the image is invalid, ``min_size`` is not positive, or
			either image dimension is smaller than ``min_size``.
	"""
	_validate_image_array(image)
	if min_size <= 0:
		raise ValueError("min_size must be a positive integer")

	height, width = image.shape[:2]
	if height < min_size or width < min_size:
		raise ValueError(
			f"Image dimensions ({width}x{height}) are smaller than the "
			f"minimum size of {min_size}x{min_size}"
		)

	return True


def to_grayscale(image: np.ndarray) -> np.ndarray:
	"""Convert a standard 3-channel BGR image to 8-bit grayscale.

	Args:
		image: A three-channel BGR image.

	Returns:
		A single-channel 8-bit grayscale image.

	Raises:
		ValueError: If ``image`` is not a three-channel 8-bit BGR array.
	"""
	_validate_image_array(image)
	if image.ndim != 3 or image.shape[2] != 3 or image.dtype != np.uint8:
		raise ValueError("image must be a 3-channel uint8 BGR array")

	return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def resize_aspect_ratio(image: np.ndarray, max_dim: int = 1024) -> np.ndarray:
	"""Scale an image down proportionally when either dimension is too large.

	Images that already fit within ``max_dim`` are returned unchanged. Larger
	images are resized with ``cv2.INTER_AREA`` to reduce feature matching cost.

	Args:
		image: Image array to resize.
		max_dim: Maximum allowed height or width in pixels.

	Returns:
		The original image or a proportionally downscaled image.

	Raises:
		ValueError: If the image is invalid or ``max_dim`` is not positive.
	"""
	_validate_image_array(image)
	if max_dim <= 0:
		raise ValueError("max_dim must be a positive integer")

	height, width = image.shape[:2]
	largest_dimension = max(height, width)
	if largest_dimension <= max_dim:
		return image

	scale = max_dim / largest_dimension
	resized_dimensions = (max(1, round(width * scale)), max(1, round(height * scale)))
	return cv2.resize(image, resized_dimensions, interpolation=cv2.INTER_AREA)


def _validate_image_array(image: np.ndarray) -> None:
	"""Raise ``ValueError`` when ``image`` is not a usable array."""
	if not isinstance(image, np.ndarray):
		raise ValueError("image must be a NumPy array")
	if image.ndim not in (2, 3) or image.shape[0] == 0 or image.shape[1] == 0:
		raise ValueError("image must have non-empty height and width dimensions")
