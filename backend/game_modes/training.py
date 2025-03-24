from enum import Enum
from typing import List, Optional
import numpy as np
from datetime import datetime

class TrainingTarget(Enum):
    DOUBLES = "doubles"
    TRIPLES = "triples"
    BULLSEYE = "bullseye"
    SPECIFIC_NUMBER = "specific"

class TrainingMode:
    def __init__(self):
        self.current_target: Optional[str] = None
        self.target_sequence: List[str] = []
        self.throws: List[dict] = []
        self.accuracy: float = 0.0
        self.session_start: datetime = datetime.now()
        
    def set_training_routine(self, routine_type: TrainingTarget, specific_numbers: List[int] = None):
        if routine_type == TrainingTarget.SPECIFIC_NUMBER and specific_numbers:
            self.target_sequence = [str(num) for num in specific_numbers]
        else:
            self.target_sequence = self._generate_routine(routine_type)
        
        self.current_target = self.target_sequence[0]
        self.throws = []
        self.accuracy = 0.0
        self.session_start = datetime.now()

    def _generate_routine(self, routine_type: TrainingTarget) -> List[str]:
        if routine_type == TrainingTarget.DOUBLES:
            return [f"D{i}" for i in range(1, 21)] + ["D25"]
        elif routine_type == TrainingTarget.TRIPLES:
            return [f"T{i}" for i in range(1, 21)]
        elif routine_type == TrainingTarget.BULLSEYE:
            return ["25", "50"] * 10  # Alternating outer and inner bull
        else:
            return [str(i) for i in range(1, 21)] + ["25", "50"]

    def process_throw(self, prediction_data: dict) -> dict:
        throw_result = self._analyze_throw(prediction_data)
        self.throws.append(throw_result)
        self._update_accuracy()
        
        feedback = self._generate_feedback(throw_result)
        
        # Move to next target if current one is hit
        if throw_result["hit"] and len(self.target_sequence) > 1:
            self.target_sequence.pop(0)
            self.current_target = self.target_sequence[0]
        
        return {
            "target": self.current_target,
            "hit": throw_result["hit"],
            "accuracy": self.accuracy,
            "feedback": feedback,
            "throw_details": throw_result
        }

    def _analyze_throw(self, prediction_data: dict) -> dict:
        """Convert YOLO predictions to throw analysis"""
        # Extract the detected region and score from prediction_data
        detected_region = prediction_data.get("region", "")
        detected_score = prediction_data.get("score", 0)
        confidence = prediction_data.get("confidence", 0.0)
        
        # Check if the throw hit the intended target
        hit = self._check_hit(detected_region, self.current_target)
        
        # Calculate deviation from target
        deviation = self._calculate_deviation(detected_region, self.current_target)
        
        return {
            "timestamp": datetime.now(),
            "target": self.current_target,
            "detected_region": detected_region,
            "score": detected_score,
            "confidence": confidence,
            "hit": hit,
            "deviation": deviation
        }

    def _check_hit(self, detected: str, target: str) -> bool:
        """Check if the detected region matches the target"""
        # Handle special cases (doubles, triples, bull)
        if target.startswith('D') and 'double' in detected.lower():
            return str(target[1:]) in detected
        if target.startswith('T') and 'triple' in detected.lower():
            return str(target[1:]) in detected
        if target == "50" and ('bulls_eye' in detected.lower() or 'bullseye' in detected.lower()):
            return True
        if target == "25" and 'bull' in detected.lower():
            return True
        return target in detected

    def _calculate_deviation(self, detected: str, target: str) -> dict:
        """Calculate how far the throw was from the target"""
        # This is a simplified version - you might want to enhance this based on
        # actual coordinate data from your detection system
        return {
            "radial": self._estimate_radial_deviation(detected, target),
            "angular": self._estimate_angular_deviation(detected, target)
        }

    def _estimate_radial_deviation(self, detected: str, target: str) -> float:
        # Implement based on your coordinate system
        # This is a placeholder implementation
        return 0.0

    def _estimate_angular_deviation(self, detected: str, target: str) -> float:
        # Implement based on your coordinate system
        # This is a placeholder implementation
        return 0.0

    def _generate_feedback(self, throw_result: dict) -> str:
        if throw_result["hit"]:
            return f"Excellent! You hit {throw_result['detected_region']}"
        
        deviation = throw_result["deviation"]
        feedback = f"Missed {self.current_target}. "
        
        # Add directional guidance
        if deviation["radial"] > 0:
            feedback += "Try throwing with less force. "
        elif deviation["radial"] < 0:
            feedback += "Try throwing with more force. "
            
        return feedback.strip()

    def _update_accuracy(self):
        hits = sum(1 for throw in self.throws if throw["hit"])
        self.accuracy = hits / len(self.throws) if self.throws else 0.0

    def get_session_summary(self) -> dict:
        return {
            "session_duration": (datetime.now() - self.session_start).seconds,
            "total_throws": len(self.throws),
            "hits": sum(1 for throw in self.throws if throw["hit"]),
            "accuracy": self.accuracy,
            "targets_remaining": len(self.target_sequence),
            "throws_history": self.throws
        }