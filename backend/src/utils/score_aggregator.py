import numpy as np
from typing import List, Dict
from collections import defaultdict

class ScoreAggregator:
    def __init__(self, confidence_threshold: float = 0.3):
        self.confidence_threshold = confidence_threshold
        self.historical_scores = defaultdict(list)
        
    # ... implementation as provided ...
