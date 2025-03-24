import request from 'supertest';
import { app } from '../app';
import { WebSocket } from 'ws';

describe('Game Tests', () => {
  test('Create new game', async () => {
    const response = await request(app)
      .post('/api/game/create')
      .send({
        variant: '501',
        players: [
          { id: 'p1', name: 'Player 1' },
          { id: 'p2', name: 'Player 2' }
        ]
      });

    expect(response.status).toBe(200);
    expect(response.body.gameId).toBeDefined();
  });

  test('Record score', async () => {
    // First create a game
    const gameResponse = await request(app)
      .post('/api/game/create')
      .send({
        variant: '501',
        players: [{ id: 'p1', name: 'Player 1' }]
      });

    const scoreResponse = await request(app)
      .post('/api/game/score')
      .send({
        gameId: gameResponse.body.gameId,
        playerId: 'p1',
        score: {
          points: 20,
          multiplier: 3,
          section: 20
        }
      });

    expect(scoreResponse.status).toBe(200);
    expect(scoreResponse.body.gameState.scores.p1).toBe(441); // 501 - (20 * 3)
  });
});
