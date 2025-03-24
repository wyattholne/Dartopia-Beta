import pandas as pd
import json
from datetime import datetime
import os
from typing import List, Dict
import matplotlib.pyplot as plt
import seaborn as sns

class DataExporter:
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
        
    def export_session(self, session_data: Dict, format: str = 'json'):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            filename = os.path.join(self.export_dir, f"session_{timestamp}.json")
            with open(filename, 'w') as f:
                json.dump(session_data, f, indent=2)
                
        elif format == 'csv':
            filename = os.path.join(self.export_dir, f"session_{timestamp}.csv")
            df = pd.DataFrame(session_data['throws'])
            df.to_csv(filename, index=False)
    
    def generate_statistics_report(self, session_data: Dict) -> str:
        df = pd.DataFrame(session_data['throws'])
        
        report = f"Session Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 50 + "\n\n"
        
        # Basic statistics
        report += "Basic Statistics:\n"
        report += f"Total Throws: {len(df)}\n"
        report += f"Average Score: {df['score'].mean():.2f}\n"
        report += f"Highest Score: {df['score'].max()}\n"
        report += f"Accuracy: {(df['hit'].sum() / len(df) * 100):.2f}%\n\n"
        
        return report
    
    def generate_visualizations(self, session_data: Dict, output_dir: str = None):
        if output_dir is None:
            output_dir = self.export_dir
            
        df = pd.DataFrame(session_data['throws'])
        
        # Score distribution
        plt.figure(figsize=(10, 6))
        sns.histplot(data=df, x='score')
        plt.title('Score Distribution')
        plt.savefig(os.path.join(output_dir, 'score_distribution.png'))
        plt.close()
        
        # Accuracy over time
        plt.figure(figsize=(10, 6))
        df['hit_rate'] = df['hit'].rolling(window=10).mean()
        sns.lineplot(data=df, y='hit_rate', x=df.index)
        plt.title('Accuracy Over Time (10-throw moving average)')
        plt.savefig(os.path.join(output_dir, 'accuracy_trend.png'))
        plt.close()