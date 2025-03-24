import cv2
from typing import Dict, Optional
import logging
import numpy as np

class CameraManager:
    def __init__(self, camera_indices: list):
        self.cameras: Dict[int, cv2.VideoCapture] = {}
        self.frame_count = 0
        self.logger = logging.getLogger(__name__)
        
        for idx in camera_indices:
            self.initialize_camera(idx)
    
    def initialize_camera(self, idx: int) -> bool:
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            self.cameras[idx] = cap
            self.logger.info(f"Camera {idx} initialized")
            return True
        self.logger.warning(f"Failed to initialize camera {idx}")
        return False

    def get_frame(self, camera_idx: int, skip_frames: int = 2) -> Optional[np.ndarray]:
        if camera_idx not in self.cameras:
            return None
            
        cap = self.cameras[camera_idx]
        self.frame_count += 1
        
        if self.frame_count % skip_frames != 0:
            return None
            
        ret, frame = cap.read()
        return frame if ret else None

    def release_all(self):
        for cap in self.cameras.values():
            cap.release()