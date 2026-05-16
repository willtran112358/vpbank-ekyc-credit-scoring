"""eKYC image checks — face detection, blur, and document edge heuristics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass
class EkycCheckResult:
    passed: bool
    face_detected: bool
    blur_score: float
    document_edge_score: float
    reasons: list[str]


def analyze_id_selfie(image_path: Path) -> EkycCheckResult:
    img = cv2.imdecode(np.fromfile(str(image_path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return EkycCheckResult(False, False, 0.0, 0.0, ["invalid_image"])

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    face_detected = _detect_face(gray)
    edge_score = _document_edge_score(gray)

    reasons: list[str] = []
    if blur_score < 80:
        reasons.append("image_too_blurry")
    if not face_detected:
        reasons.append("face_not_detected")
    if edge_score < 0.02:
        reasons.append("document_edges_weak")

    passed = len(reasons) == 0
    return EkycCheckResult(
        passed=passed,
        face_detected=face_detected,
        blur_score=round(float(blur_score), 2),
        document_edge_score=round(float(edge_score), 4),
        reasons=reasons,
    )


def _detect_face(gray: np.ndarray) -> bool:
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60))
    return len(faces) > 0


def _document_edge_score(gray: np.ndarray) -> float:
    edges = cv2.Canny(gray, 50, 150)
    return float(np.count_nonzero(edges)) / edges.size
