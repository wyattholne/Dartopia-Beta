import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict
import io
import base64

class DartsVisualizer:
    def __init__(self):
        self.figure_size = (10, 6)
        plt.style.use('seaborn')
        
    def generate_heatmap(self, throws: List[Dict]) -> str:
        """Generate throw distribution heatmap"""
        plt.figure(figsize=self.figure_size)
        
        # Create 2D histogram of throw positions
        x = [t['coordinates'][0] for t in throws]
        y = [t['coordinates'][1] for t in throws]
        
        plt.hist2d(x, y, bins=20, cmap='YlOrRd')
        plt.colorbar(label='Number of throws')
        plt.title('Throw Distribution Heatmap')
        
        # Convert plot to base64 string
        return self._fig_to_base64()
        
    def generate_score_trend(self, throws: List[Dict]) -> str:
        """Generate score trend line plot"""
        plt.figure(figsize=self.figure_size)
        
        scores = [t['score'] for t in throws]
        moving_avg = np.convolve(scores, np.ones(10)/10, mode='valid')
        
        plt.plot(scores, label='Raw scores', alpha=0.5)
        plt.plot(range(9, len(scores)), moving_avg, 
                label='10-throw moving average', linewidth=2)
        
        plt.title('Score Trend')
        plt.xlabel('Throw Number')
        plt.ylabel('Score')
        plt.legend()
        
        return self._fig_to_base64()
        
    def generate_accuracy_by_region(self, throws: List[Dict]) -> str:
        """Generate accuracy breakdown by board region"""
        plt.figure(figsize=self.figure_size)
        
        regions = {}
        for throw in throws:
            region = throw['region']
            hit = throw['hit']
            if region not in regions:
                regions[region] = {'hits': 0, 'total': 0}
            regions[region]['total'] += 1
            if hit:
                regions[region]['hits'] += 1
                
        accuracies = {r: regions[r]['hits']/regions[r]['total'] 
                     for r in regions}
        
        plt.bar(accuracies.keys(), accuracies.values())
        plt.xticks(rotation=45)
        plt.title('Accuracy by Board Region')
        plt.ylabel('Accuracy %')
        
        return self._fig_to_base64()
        
    def _fig_to_base64(self) -> str:
        """Convert matplotlib figure to base64 string"""
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode('utf-8')