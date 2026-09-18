"""SIFT-based copy-move forgery detection."""

import cv2
import numpy as np


def detect_copy_move(
	image: np.ndarray,
	min_distance: float = 40.0,
	ratio_thresh: float = 0.75,
) -> tuple[np.ndarray, int]:
	"""Detect duplicated regions using SIFT matches and RANSAC.

	Args:
		image: Three-channel, 8-bit BGR image.
		min_distance: Minimum spatial separation between matched keypoints.
		ratio_thresh: Lowe ratio-test threshold for nearest-neighbor matches.

	Returns:
		A copy of ``image`` annotated with verified red match lines and the
		number of RANSAC inlier pairs. If fewer than ten keypoints or no
		descriptors are found, the image copy and zero are returned.

	Raises:
		ValueError: If the image or detector parameters are invalid.
	"""
	_validate_input(image, min_distance, ratio_thresh)
	annotated_image = image.copy()
	grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	sift = cv2.SIFT_create()
	keypoints, descriptors = sift.detectAndCompute(grayscale, None)
	if descriptors is None or len(keypoints) < 10:
		return annotated_image, 0

	matcher = cv2.BFMatcher(cv2.NORM_L2)
	match_groups = matcher.knnMatch(descriptors, descriptors, k=3)
	candidate_points: list[tuple[np.ndarray, np.ndarray]] = []

	for matches in match_groups:
		if len(matches) < 3:
			continue

		identity_match, nearest_match, second_nearest_match = matches
		if identity_match.queryIdx != identity_match.trainIdx:
			continue
		if not nearest_match.distance < ratio_thresh * second_nearest_match.distance:
			continue

		point_one = np.asarray(keypoints[nearest_match.queryIdx].pt, dtype=np.float32)
		point_two = np.asarray(keypoints[nearest_match.trainIdx].pt, dtype=np.float32)
		if np.linalg.norm(point_one - point_two) <= min_distance:
			continue

		candidate_points.append((point_one, point_two))

	if len(candidate_points) < 4:
		return annotated_image, 0

	points_one = np.asarray([pair[0] for pair in candidate_points], dtype=np.float32)
	points_two = np.asarray([pair[1] for pair in candidate_points], dtype=np.float32)
	_, inlier_mask = cv2.findHomography(points_one, points_two, cv2.RANSAC, 5.0)
	if inlier_mask is None:
		return annotated_image, 0

	inlier_flags = inlier_mask.ravel().astype(bool)
	for (point_one, point_two), is_inlier in zip(candidate_points, inlier_flags):
		if not is_inlier:
			continue

		start = tuple(np.round(point_one).astype(int))
		end = tuple(np.round(point_two).astype(int))
		cv2.line(annotated_image, start, end, (0, 0, 255), 1)
		cv2.circle(annotated_image, start, 3, (0, 0, 255), -1)
		cv2.circle(annotated_image, end, 3, (0, 0, 255), -1)

	return annotated_image, int(np.count_nonzero(inlier_flags))


def _validate_input(
	image: np.ndarray, min_distance: float, ratio_thresh: float
) -> None:
	"""Validate the image and matching parameters before OpenCV processing."""
	if not isinstance(image, np.ndarray):
		raise ValueError("image must be a NumPy array")
	if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3:
		raise ValueError("image must be a 3-channel uint8 BGR array")
	if image.shape[0] == 0 or image.shape[1] == 0:
		raise ValueError("image must have non-empty height and width")
	if min_distance < 0:
		raise ValueError("min_distance must be non-negative")
	if ratio_thresh <= 0:
		raise ValueError("ratio_thresh must be positive")
