import pytest
from models.game import Game, GamePlayer, GameThrow
from database import db

def test_game_creation(test_client):
    """Test creating a new game"""
    response = test_client.post('/api/game/create', json={
        'variant': '501',
        'players': [
            {'id': 'p1', 'name': 'Player 1'},
            {'id': 'p2', 'name': 'Player 2'}
        ]
    })
    assert response.status_code == 200
    assert 'gameId' in response.json

def test_score_recording(test_client, init_game_data):
    """Test recording a score"""
    response = test_client.post('/api/game/score', json={
        'gameId': 'test-game',
        'playerId': 'p1',
        'score': {
            'points': 20,
            'multiplier': 3,
            'section': 20
        }
    })
    assert response.status_code == 200
    assert response.json['gameState']['scores']['p1'] == 441

def test_websocket_connection(socket_client):
    assert socket_client.is_connected()
    received = socket_client.get_received()
    assert len(received) > 0

def test_game_state_updates(socket_client, init_game_data):
    socket_client.emit('throw', {
        'gameId': 'test-game',
        'playerId': 'p1',
        'score': {'points': 20, 'multiplier': 1}
    })
    received = socket_client.get_received()
    assert any(msg['name'] == 'score_update' for msg in received)
