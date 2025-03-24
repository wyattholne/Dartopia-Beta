from typing import Dict, Any
import cv2
import logging
from ..models.yolo_model import model  # Adjust import path as needed

logger = logging.getLogger(__name__)

class CameraValidator:
    def __init__(self, cameras: Dict[int, cv2.VideoCapture]):
        self.cameras = cameras

    def validate_camera_feeds(self) -> Dict[int, Dict[str, Any]]:
        """Validate all camera feeds and their positions"""
        validation_results = {}
        
        for idx, cap in self.cameras.items():
            if not cap.isOpened():
                validation_results[idx] = {
                    "status": "error",
                    "message": "Camera not accessible"
                }
                continue

            validation_results[idx] = self._validate_single_camera(cap, idx)

        return validation_results

    def _validate_single_camera(self, cap: cv2.VideoCapture, idx: int) -> Dict[str, Any]:
        """Validate a single camera feed"""
        ret, frame = cap.read()
        if not ret:
            return {
                "status": "error",
                "message": "Failed to read frame"
            }

        results = model(frame)
        predictions = results[0].boxes.data.tolist()
        
        dartboard_detected = any('dartboard' in pred['label'].lower() 
                               for pred in predictions)

        return {
            "status": "ok" if dartboard_detected else "warning",
            "message": "Dartboard detected" if dartboard_detected else "No dartboard detected",
            "frame_size": frame.shape[:2],
            "predictions": len(predictions)
        }
