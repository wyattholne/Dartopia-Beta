import pytest
from app import app, socketio
from database import db, init_db

@pytest.fixture
def test_app():
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test_key'
    })
    with app.app_context():
        init_db(app)
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture
def socket_client(test_app):
    return socketio.test_client(test_app)

@pytest.fixture
def init_game_data(test_app):
    with test_app.app_context():
        game = Game(id='test-game', variant='501')
        db.session.add(game)
        game.add_player('p1', 'Player 1')
        game.add_player('p2', 'Player 2')
        db.session.commit()
        return game
