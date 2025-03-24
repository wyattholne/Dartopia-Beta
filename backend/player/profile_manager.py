from datetime import datetime
import json
import os
from typing import Dict, List, Optional
import numpy as np

class PlayerProfile:
    def __init__(self, player_id: str, name: str):
        self.player_id = player_id
        self.name = name
        self.created_at = datetime.now()
        self.stats = {
            'games_played': 0,
            'total_throws': 0,
            'average_score': 0.0,
            'highest_score': 0,
            'checkouts': [],
            'preferred_doubles': {},
            'accuracy_by_region': {},
            'achievement_badges': set()
        }
        self.training_history: List[Dict] = []
        self.game_history: List[Dict] = []

    def update_stats(self, game_data: Dict):
        self.stats['games_played'] += 1
        self.stats['total_throws'] += len(game_data['throws'])
        
        # Update average score
        scores = [throw['score'] for throw in game_data['throws']]
        self.stats['average_score'] = (
            (self.stats['average_score'] * (self.stats['games_played'] - 1) + 
             np.mean(scores)) / self.stats['games_played']
        )
        
        # Update highest score
        max_score = max(scores)
        if max_score > self.stats['highest_score']:
            self.stats['highest_score'] = max_score
            
        # Update preferred doubles
        for throw in game_data['throws']:
            if 'double' in throw['region'].lower():
                region = throw['region']
                self.stats['preferred_doubles'][region] = \
                    self.stats['preferred_doubles'].get(region, 0) + 1

        # Check for achievements
        self._check_achievements(game_data)

    def _check_achievements(self, game_data: Dict):
        """Check and award achievement badges"""
        # High Score Achievement
        if any(throw['score'] >= 180 for throw in game_data['throws']):
            self.stats['achievement_badges'].add('180_CLUB')
            
        # Consistency Achievement
        recent_scores = [throw['score'] for throw in game_data['throws'][-10:]]
        if len(recent_scores) >= 10 and np.std(recent_scores) < 10:
            self.stats['achievement_badges'].add('CONSISTENT_PLAYER')
            
        # Checkout Achievement
        if game_data.get('checkout_score', 0) >= 100:
            self.stats['achievement_badges'].add('HIGH_CHECKOUT')

class ProfileManager:
    def __init__(self, data_dir: str = "player_data"):
        self.data_dir = data_dir
        self.active_profiles: Dict[str, PlayerProfile] = {}
        os.makedirs(data_dir, exist_ok=True)
        
    def create_profile(self, name: str) -> PlayerProfile:
        player_id = f"player_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        profile = PlayerProfile(player_id, name)
        self.active_profiles[player_id] = profile
        self._save_profile(profile)
        return profile
    
    def load_profile(self, player_id: str) -> Optional[PlayerProfile]:
        if player_id in self.active_profiles:
            return self.active_profiles[player_id]
            
        profile_path = os.path.join(self.data_dir, f"{player_id}.json")
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                data = json.load(f)
                profile = PlayerProfile(data['player_id'], data['name'])
                profile.stats = data['stats']
                profile.training_history = data['training_history']
                profile.game_history = data['game_history']
                self.active_profiles[player_id] = profile
                return profile
        return None
    
    def _save_profile(self, profile: PlayerProfile):
        profile_data = {
            'player_id': profile.player_id,
            'name': profile.name,
            'stats': profile.stats,
            'training_history': profile.training_history,
            'game_history': profile.game_history
        }
        
        with open(os.path.join(self.data_dir, f"{profile.player_id}.json"), 'w') as f:
            json.dump(profile_data, f, indent=2)