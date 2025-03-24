from typing import List, Dict, Optional
from datetime import datetime
import random

class Tournament:
    def __init__(self, name: str, players: List[str]):
        self.name = name
        self.players = players
        self.matches: List[Dict] = []
        self.brackets: Dict = {}
        self.current_round = 0
        self.winner: Optional[str] = None
        self.start_time = datetime.now()
        
    def generate_brackets(self):
        """Generate tournament brackets"""
        players = self.players.copy()
        random.shuffle(players)
        
        # Add byes if necessary
        while len(players) & (len(players) - 1):  # Check if power of 2
            players.append(None)
            
        self.current_round = 1
        round_matches = []
        
        for i in range(0, len(players), 2):
            match = {
                'round': self.current_round,
                'match_number': len(round_matches) + 1,
                'player1': players[i],
                'player2': players[i + 1],
                'score1': 0,
                'score2': 0,
                'winner': None,
                'status': 'pending'
            }
            round_matches.append(match)
            
        self.brackets[self.current_round] = round_matches
        
    def record_match_result(self, match_number: int, score1: int, score2: int):
        """Record the result of a match"""
        match = self._find_match(self.current_round, match_number)
        if not match:
            return False
            
        match['score1'] = score1
        match['score2'] = score2
        match['winner'] = match['player1'] if score1 > score2 else match['player2']
        match['status'] = 'completed'
        
        # Check if round is complete
        if all(m['status'] == 'completed' 
               for m in self.brackets[self.current_round]):
            self._advance_round()
            
        return True
    
    def _advance_round(self):
        """Advance to next round"""
        winners = [m['winner'] for m in self.brackets[self.current_round]]
        
        if len(winners) == 1:
            self.winner = winners[0]
            return
            
        self.current_round += 1
        round_matches = []
        
        for i in range(0, len(winners), 2):
            match = {
                'round': self.current_round,
                'match_number': len(round_matches) + 1,
                'player1': winners[i],
                'player2': winners[i + 1] if i + 1 < len(winners) else None,
                'score1': 0,
                'score2': 0,
                'winner': None,
                'status': 'pending'
            }
            round_matches.append(match)
            
        self.brackets[self.current_round] = round_matches
    
    def _find_match(self, round_number: int, match_number: int) -> Optional[Dict]:
        """Find a specific match in the brackets"""
        round_matches = self.brackets.get(round_number, [])
        for match in round_matches:
            if match['match_number'] == match_number:
                return match
        return None
    
    def get_tournament_status(self) -> Dict:
        """Get current tournament status"""
        return {
            'name': self.name,
            'current_round': self.current_round,
            'total_players': len(self.players),
            'matches_completed': sum(
                sum(1 for m in round_matches if m['status'] == 'completed')
                for round_matches in self.brackets.values()
            ),
            'winner': self.winner,
            'brackets': self.brackets,
            'duration': (datetime.now() - self.start_time).total_seconds()
        }