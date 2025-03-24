from typing import List, Dict
import logging
import re

logger = logging.getLogger(__name__)

def calculate_score(predictions: List[dict]) -> dict:
    """Calculate dart score based on predictions from multiple cameras"""
    if not predictions:
        return {"total": 0, "details": [], "confidence": 0}
        
    score_details = []
    total_score = 0
    confidence_sum = 0
    
    # Find dartboard for reference
    dartboard = next(
        (pred for pred in sorted(
            (p for p in predictions if 'dartboard' in p['label'].lower()),
            key=lambda x: x['confidence'],
            reverse=True
        )), None)
    
    if not dartboard:
        logger.warning("No dartboard detected in frame")
        return {"total": 0, "details": [], "confidence": 0}

    # Calculate board reference points
    board_center_x = dartboard['bbox'][0] + dartboard['bbox'][2]/2
    board_center_y = dartboard['bbox'][1] + dartboard['bbox'][3]/2
    board_radius = max(dartboard['bbox'][2], dartboard['bbox'][3])/2

    # Process darts and scoring regions
    darts = [p for p in predictions if 'dart' in p['label'].lower()]
    scoring_regions = [p for p in predictions if any(
        region in p['label'].lower() for region in ['single', 'double', 'triple', 'bull']
    )]

    # ... rest of the calculate_score implementation as provided ...
