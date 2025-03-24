import numpy as np
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from typing import List, Dict
import json

@dataclass
class ThrowMetrics:
    accuracy: float
    consistency: float
    average_score: float
    double_hit_rate: float
    triple_hit_rate: float
    bullseye_rate: float

class ThrowAnalyzer:
    def __init__(self):
        self.throws_history: List[Dict] = []
        self.session_start = datetime.now()
        
    def add_throw(self, throw_data: dict):
        throw_data['timestamp'] = datetime.now().isoformat()
        self.throws_history.append(throw_data)
        
    def calculate_metrics(self) -> ThrowMetrics:
        if not self.throws_history:
            return ThrowMetrics(0, 0, 0, 0, 0, 0)
            
        df = pd.DataFrame(self.throws_history)
        
        # Calculate basic metrics
        accuracy = len(df[df['hit']]) / len(df) if len(df) > 0 else 0
        average_score = df['score'].mean()
        
        # Calculate consistency (lower standard deviation = more consistent)
        consistency = 1 - (df['score'].std() / df['score'].max() if len(df) > 1 else 0)
        
        # Calculate special region hit rates
        double_hits = df[df['region'].str.contains('double', case=False)].shape[0]
        triple_hits = df[df['region'].str.contains('triple', case=False)].shape[0]
        bullseye_hits = df[df['region'].str.contains('bullseye|bulls_eye', case=False)].shape[0]
        
        total_throws = len(df)
        
        return ThrowMetrics(
            accuracy=accuracy,
            consistency=consistency,
            average_score=average_score,
            double_hit_rate=double_hits/total_throws if total_throws > 0 else 0,
            triple_hit_rate=triple_hits/total_throws if total_throws > 0 else 0,
            bullseye_rate=bullseye_hits/total_throws if total_throws > 0 else 0
        )
    
    def generate_heatmap(self) -> np.ndarray:
        """Generate a heatmap of throw locations"""
        heatmap = np.zeros((20, 20))  # Adjust size as needed
        
        for throw in self.throws_history:
            x, y = throw.get('coordinates', (0, 0))
            # Convert coordinates to heatmap indices
            i = int(y * 20)
            j = int(x * 20)
            if 0 <= i < 20 and 0 <= j < 20:
                heatmap[i, j] += 1
                
        return heatmap
    
    def export_session_data(self, filename: str = None):
        if filename is None:
            filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        session_data = {
            'session_start': self.session_start.isoformat(),
            'session_end': datetime.now().isoformat(),
            'metrics': self.calculate_metrics().__dict__,
            'throws': self.throws_history
        }
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)