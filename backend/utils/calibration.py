import cv2
import numpy as np
from typing import Tuple, List, Optional

class BoardCalibrator:
    def __init__(self):
        self.reference_points = []
        self.calibration_matrix = None
        self.board_dimensions = (45, 45)  # Standard dartboard dimensions in cm
        
    def set_reference_points(self, points: List[Tuple[int, int]]):
        """Set reference points for calibration (corners of the dartboard)"""
        if len(points) != 4:
            raise ValueError("Exactly 4 corner points are required")
        self.reference_points = points
        self._calculate_calibration_matrix()
    
    def _calculate_calibration_matrix(self):
        """Calculate perspective transform matrix"""
        if len(self.reference_points) != 4:
            return
            
        # Define standard dartboard corners in cm
        board_width, board_height = self.board_dimensions
        dst_points = np.float32([
            [0, 0],
            [board_width, 0],
            [board_width, board_height],
            [0, board_height]
        ])
        
        src_points = np.float32(self.reference_points)
        self.calibration_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    
    def calibrate_frame(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Apply calibration transform to frame"""
        if self.calibration_matrix is None:
            return None
            
        height, width = frame.shape[:2]
        return cv2.warpPerspective(
            frame,
            self.calibration_matrix,
            (width, height)
        )
    
    def get_real_coordinates(self, pixel_coords: Tuple[int, int]) -> Tuple[float, float]:
        """Convert pixel coordinates to real-world coordinates (in cm)"""
        if self.calibration_matrix is None:
            return pixel_coords
            
        points = np.float32([pixel_coords]).reshape(-1, 1, 2)
        transformed_points = cv2.perspectiveTransform(points, self.calibration_matrix)
        return tuple(transformed_points[0][0])
    
    def detect_board_automatically(self, frame: np.ndarray) -> bool:
        """Attempt to automatically detect dartboard in frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=100,
            param1=50,
            param2=30,
            minRadius=100,
            maxRadius=300
        )
        
        if circles is not None:
            circle = circles[0][0]
            center = (int(circle[0]), int(circle[1]))
            radius = int(circle[2])
            
            # Calculate corner points based on circle
            self.reference_points = [
                (center[0] - radius, center[1] - radius),
                (center[0] + radius, center[1] - radius),
                (center[0] + radius, center[1] + radius),
                (center[0] - radius, center[1] + radius)
            ]
            
            self._calculate_calibration_matrix()
            return True
            
        return False