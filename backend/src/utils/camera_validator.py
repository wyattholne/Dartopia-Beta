import cv2
import numpy as np
from typing import Dict, List, Tuple
import logging

class CameraValidator:
    def __init__(self, cameras: Dict[int, cv2.VideoCapture], model, min_confidence: float = 0.3):
        self.cameras = cameras
        self.model = model
        self.min_confidence = min_confidence
        self.logger = logging.getLogger(__name__)
        self.calibration_history = {idx: [] for idx in cameras.keys()}
        
    # ... implementation as provided ...
