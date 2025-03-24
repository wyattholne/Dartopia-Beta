import cv2
import numpy as np
import threading
import time
from typing import Dict, List
from queue import Queue
import logging

class CameraMonitor:
    def __init__(self, cameras: Dict[int, cv2.VideoCapture], model):
        self.cameras = cameras
        self.model = model
        self.frame_queues = {idx: Queue(maxsize=30) for idx in cameras.keys()}
        self.status = {idx: {"active": True, "fps": 0, "issues": []} for idx in cameras.keys()}
        
    # ... implementation as provided ...
