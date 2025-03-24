from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Throw:
    score: int
    multiplier: int
    region: str
    timestamp: datetime
    coordinates: tuple

class X01Game:
    def __init__(self, starting_score: int = 501, double_out: bool = True):
        self.starting_score = starting_score
        self.double_out = double_out
        self.current_score = starting_score
        self.throws: List[Throw] = []
        self.game_over = False
        
    def process_throw(self, prediction_data: dict) -> dict:
        if self.game_over:
            return {"status": "game_over", "message": "Game is already finished"}
            
        throw = self._create_throw(prediction_data)
        
        if self._is_valid_throw(throw):
            self.throws.append(throw)
            self.current_score -= throw.score * throw.multiplier
            
            if self.current_score == 0:
                self.game_over = True
                return {"status": "win", "message": "Game Won!", "throws": len(self.throws)}
                
            return {
                "status": "valid",
                "remaining": self.current_score,
                "throw": throw
            }
            
        return {"status": "invalid", "message": "Invalid throw for current score"}

    def _create_throw(self, prediction_data: dict) -> Throw:
        # Convert your YOLO predictions to a Throw object
        # This will need to be adapted to your specific prediction format
        return Throw(
            score=prediction_data.get("score", 0),
            multiplier=prediction_data.get("multiplier", 1),
            region=prediction_data.get("region", "unknown"),
            timestamp=datetime.now(),
            coordinates=prediction_data.get("coordinates", (0, 0))
        )

    def _is_valid_throw(self, throw: Throw) -> bool:
        potential_score = self.current_score - (throw.score * throw.multiplier)
        if potential_score < 0:
            return False
        if potential_score == 0 and self.double_out and throw.multiplier != 2:
            return False
        return True