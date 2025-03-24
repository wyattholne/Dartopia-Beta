from flask import Blueprint, request, jsonify
from models.game import Game
from database import db

game_bp = Blueprint('game', __name__)

@game_bp.route('/create', methods=['POST'])
def create_game():
    data = request.json
    variant = data.get('variant')
    players = data.get('players')
    
    game = Game(variant=variant)
    db.session.add(game)
    db.session.commit()
    
    game_id = game.id
    # Initialize player states
    for player in players:
        game.add_player(player['id'], player['name'])
    
    return jsonify({
        'gameId': game_id,
        'gameState': game.get_state()
    })

@game_bp.route('/score', methods=['POST'])
def record_score():
    data = request.json
    game_id = data.get('gameId')
    player_id = data.get('playerId')
    score = data.get('score')
    
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
        
    game.record_score(player_id, score)
    db.session.commit()
    
    return jsonify({
        'gameState': game.get_state()
    })
