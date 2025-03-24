from typing import Dict, List, Set
from datetime import datetime

class SocialManager:
    def __init__(self):
        self.friends_lists: Dict[str, Set[str]] = {}
        self.pending_requests: Dict[str, Set[str]] = {}
        self.challenges: Dict[str, List[Dict]] = {}
        self.achievements: Dict[str, Set[str]] = {}
        
    def send_friend_request(self, from_id: str, to_id: str) -> bool:
        """Send a friend request"""
        if to_id not in self.pending_requests:
            self.pending_requests[to_id] = set()
        self.pending_requests[to_id].add(from_id)
        return True
        
    def accept_friend_request(self, from_id: str, to_id: str) -> bool:
        """Accept a friend request"""
        if to_id not in self.pending_requests or \
           from_id not in self.pending_requests[to_id]:
            return False
            
        # Add to friends lists
        if from_id not in self.friends_lists:
            self.friends_lists[from_id] = set()
        if to_id not in self.friends_lists:
            self.friends_lists[to_id] = set()
            
        self.friends_lists[from_id].add(to_id)
        self.friends_lists[to_id].add(from_id)
        
        # Remove request
        self.pending_requests[to_id].remove(from_id)
        return True
        
    def send_challenge(self, from_id: str, to_id: str, 
                      game_type: str, stake: Dict = None) -> str:
        """Send a game challenge"""
        challenge_id = f"challenge_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        challenge = {
            'id': challenge_id,
            'from_id': from_id,
            'to_id': to_id,
            'game_type': game_type,
            'stake': stake,
            'status': 'pending',
            'timestamp': datetime.now().isoformat()
        }
        
        if to_id not in self.challenges:
            self.challenges[to_id] = []
        self.challenges[to_id].append(challenge)
        
        return challenge_id
        
    def award_achievement(self, player_id: str, achievement: str):
        """Award an achievement to a player"""
        if player_id not in self.achievements:
            self.achievements[player_id] = set()
        self.achievements[player_id].add(achievement)