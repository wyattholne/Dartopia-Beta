from database import db
from datetime import datetime

class Game(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    variant = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='waiting')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_state(self):
        return {
            'id': self.id,
            'variant': self.variant,
            'status': self.status,
            'players': [player.to_dict() for player in self.players],
            'scores': {player.id: player.current_score for player in self.players},
            'history': [throw.to_dict() for throw in self.throws]
        }
    
    def add_player(self, player_id, player_name):
        player = GamePlayer(
            game_id=self.id,
            player_id=player_id,
            player_name=player_name,
            current_score=501 if self.variant == '501' else 0
        )
        db.session.add(player)
        return player

    def record_score(self, player_id, score_data):
        throw = GameThrow(
            game_id=self.id,
            player_id=player_id,
            points=score_data['points'],
            multiplier=score_data['multiplier'],
            section=score_data['section']
        )
        db.session.add(throw)
        
        player = next(p for p in self.players if p.player_id == player_id)
        player.current_score -= score_data['points'] * score_data['multiplier']
        
        return throw

class GamePlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(36), db.ForeignKey('game.id'))
    player_id = db.Column(db.String(36))
    player_name = db.Column(db.String(100))
    current_score = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.player_id,
            'name': self.player_name,
            'score': self.current_score
        }

class GameThrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(36), db.ForeignKey('game.id'))
    player_id = db.Column(db.String(36))
    points = db.Column(db.Integer)
    multiplier = db.Column(db.Integer)
    section = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'playerId': self.player_id,
            'points': self.points,
            'multiplier': self.multiplier,
            'section': self.section,
            'timestamp': self.timestamp.isoformat()
        }
