import asyncio
from typing import Dict, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Player:
    id: str
    name: str
    socket_id: str
    room: str = None
    ready: bool = False
    
class GameRoom:
    def __init__(self, room_id: str, game_type: str):
        self.room_id = room_id
        self.game_type = game_type
        self.players: Dict[str, Player] = {}
        self.spectators: Set[str] = set()
        self.game_state = {
            'active': False,
            'current_player': None,
            'scores': {},
            'throws': [],
            'round': 0
        }
        
    def add_player(self, player: Player) -> bool:
        if len(self.players) >= 4:  # Max 4 players per room
            return False
        self.players[player.id] = player
        player.room = self.room_id
        return True
        
    def remove_player(self, player_id: str):
        if player_id in self.players:
            player = self.players[player_id]
            player.room = None
            del self.players[player_id]
            
    def start_game(self) -> bool:
        if len(self.players) < 2:
            return False
        if not all(p.ready for p in self.players.values()):
            return False
            
        self.game_state['active'] = True
        self.game_state['current_player'] = list(self.players.keys())[0]
        self.game_state['scores'] = {p_id: 501 for p_id in self.players}
        return True

class GameServer:
    def __init__(self):
        self.rooms: Dict[str, GameRoom] = {}
        self.players: Dict[str, Player] = {}
        
    async def create_room(self, room_id: str, game_type: str) -> GameRoom:
        if room_id in self.rooms:
            return None
            
        room = GameRoom(room_id, game_type)
        self.rooms[room_id] = room
        return room
        
    async def join_room(self, player: Player, room_id: str) -> bool:
        if room_id not in self.rooms:
            return False
            
        room = self.rooms[room_id]
        if room.add_player(player):
            self.players[player.id] = player
            await self._broadcast_room_update(room)
            return True
        return False
        
    async def process_throw(self, player_id: str, throw_data: Dict):
        player = self.players.get(player_id)
        if not player or not player.room:
            return
            
        room = self.rooms[player.room]
        if not room.game_state['active']:
            return
            
        if player_id != room.game_state['current_player']:
            return
            
        # Process throw
        score = throw_data['score']
        room.game_state['scores'][player_id] -= score
        room.game_state['throws'].append({
            'player_id': player_id,
            'score': score,
            'timestamp': datetime.now().isoformat()
        })
        
        # Check for winner
        if room.game_state['scores'][player_id] == 0:
            await self._end_game(room, player_id)
        else:
            # Next player
            players = list(room.players.keys())
            current_idx = players.index(player_id)
            next_idx = (current_idx + 1) % len(players)
            room.game_state['current_player'] = players[next_idx]
            
        await self._broadcast_room_update(room)
        
    async def _end_game(self, room: GameRoom, winner_id: str):
        """Handle game end"""
        room.game_state['active'] = False
        await self._broadcast_game_end(room, winner_id)
        
    async def _broadcast_room_update(self, room: GameRoom):
        """Broadcast room state to all players"""
        # Implementation depends on your websocket setup
        pass
        
    async def _broadcast_game_end(self, room: GameRoom, winner_id: str):
        """Broadcast game end to all players"""
        # Implementation depends on your websocket setup
        pass