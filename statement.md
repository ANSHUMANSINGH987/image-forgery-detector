# Project Statement: Dual-Domain Image Forgery Detection Engine

## Problem Statement
In an era dominated by generative media and accessible digital image manipulation tools, visual misinformation has grown exponentially. Digital images are frequently forged through two primary mechanisms:
1. **Copy-Move (Cloning):** Copying a texture, object, or region and pasting it into another part of the same image to obscure evidence or duplicate objects.
2. **Splicing & Resaving:** Merging regions from distinct source images with differing compression histories into a single composite image.

Manual inspection fails to detect subtle compression traces or geometrically transformed duplicates. This project establishes a deterministic, mathematically grounded Computer Vision tool to detect, localize, and report digital image tampering without relying on opaque deep learning models.

## Scope of the Project
The tool processes standard digital images (`.jpg`, `.jpeg`, `.png`) to perform:
- **Error Level Analysis (ELA):** Identifies non-uniform compression levels across high-frequency components by recompressing the input at a known quantization factor and amplifying residual differences.
- **Copy-Move Forgery Detection (CMFD):** Extracts Scale-Invariant Feature Transform (SIFT) keypoints, evaluates descriptor correlations using Lowe’s ratio test, isolates spatially non-adjacent pairs, and applies RANSAC homography estimation to verify geometric coherence.
- **Automated Visualization:** Produces a standardized, annotated dual-panel canvas comparing the untouched source image with the highlighted tamper regions.

## Target Users
- **Forensic & Legal Investigators:** Verifying documentary evidence, submitted affidavits, and identity documents.
- **Journalists & Fact-Checkers:** Screening user-submitted imagery before broadcast or publication.
- **Academic Evaluators & Researchers:** Demonstrating low-level image processing, frequency residual analysis, and epipolar/homography geometry in Computer Vision.

## High-Level Features
- **Deterministic CLI Interface:** Rapid forensic pipeline execution via configurable command-line arguments.
- **Dual-Domain Evaluation:** Cross-checks both pixel-level spatial descriptors (SIFT/RANSAC) and frequency compression residuals (ELA).
- **Automated Artifact Generation:** Exports side-by-side diagnostic visual canvases with inspection metadata banners.
- **Modular Architecture:** Fully decoupled preprocessor, detection algorithms, and visualization pipeline tested through automated unit suites.