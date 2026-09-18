"""Error Level Analysis (ELA) image processing utilities."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageEnhance


def compute_ela(
	image_path: str, quality: int = 90, scale: int = 15
) -> tuple[np.ndarray, float]:
	"""Compute an ELA image and mean compression discrepancy.

	The source image is converted to RGB, recompressed as a JPEG, and compared
	with the original. The resulting difference image is brightness-enhanced
	and returned in BGR channel order for OpenCV compatibility.

	Args:
		image_path: Path to the source image.
		quality: JPEG quality used for the temporary recompressed image.
		scale: Retained as part of the public API for caller compatibility.
			The brightness factor is calculated dynamically from the maximum
			observed pixel difference.

	Returns:
		A tuple containing the enhanced ELA image in BGR format and the mean
		discrepancy of the unscaled RGB absolute-difference image.

	Raises:
		FileNotFoundError: If ``image_path`` does not exist.
		OSError: If the image cannot be opened, saved, or read.
		ValueError: If ``quality`` or ``scale`` is invalid.
	"""
	del scale
	if not 0 <= quality <= 100:
		raise ValueError("quality must be between 0 and 100")

	temporary_path = Path("_temp_ela.jpg")
	try:
		with Image.open(image_path) as source:
			original = source.convert("RGB")

		original.save(temporary_path, format="JPEG", quality=quality)

		with Image.open(temporary_path) as recompressed_source:
			recompressed = recompressed_source.convert("RGB")

		difference = ImageChops.difference(original, recompressed)
		extrema = difference.getextrema()
		max_diff = max(channel_max for _, channel_max in extrema)
		scale_factor = 1.0 if max_diff == 0 else 255.0 / max_diff

		enhanced_difference = ImageEnhance.Brightness(difference).enhance(
			scale_factor
		)
		difference_array = np.asarray(difference, dtype=np.float32)
		mean_discrepancy = float(np.mean(difference_array))
		enhanced_array = np.asarray(enhanced_difference, dtype=np.uint8)
		ela_image_bgr = enhanced_array[:, :, ::-1].copy()

		return ela_image_bgr, mean_discrepancy
	except FileNotFoundError:
		raise
	except OSError as error:
		raise OSError(f"Unable to compute ELA for image: {image_path}") from error
	finally:
		try:
			temporary_path.unlink()
		except FileNotFoundError:
			pass
