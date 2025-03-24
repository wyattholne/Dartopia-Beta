import { Request, Response } from 'express';
import { WebSocket } from 'ws';

interface GameState {
  id: string;
  variant: string;
  players: Player[];
  currentPlayer: number;
  scores: Record<number, number>;
  history: Score[];
  status: 'waiting' | 'active' | 'finished';
}

interface Player {
  id: string;
  name: string;
  connection: WebSocket | null;
}

interface Score {
  playerId: string;
  points: number;
  multiplier: number;
  section: number;
  timestamp: Date;
}

class GameController {
  private games: Map<string, GameState> = new Map();

  createGame = async (req: Request, res: Response) => {
    const { variant, players } = req.body;
    const gameId = Math.random().toString(36).substring(7);
    
    const gameState: GameState = {
      id: gameId,
      variant,
      players: players.map((p: any) => ({ ...p, connection: null })),
      currentPlayer: 0,
      scores: players.reduce((acc: any, p: any) => ({ ...acc, [p.id]: 501 }), {}),
      history: [],
      status: 'waiting'
    };

    this.games.set(gameId, gameState);
    return res.json({ gameId, gameState });
  };

  recordScore = async (req: Request, res: Response) => {
    const { gameId, playerId, score } = req.body;
    const game = this.games.get(gameId);

    if (!game) {
      return res.status(404).json({ error: 'Game not found' });
    }

    const newScore: Score = {
      playerId,
      ...score,
      timestamp: new Date()
    };

    game.history.push(newScore);
    game.scores[playerId] -= score.points * score.multiplier;

    // Notify all players
    game.players.forEach(player => {
      if (player.connection) {
        player.connection.send(JSON.stringify({
          type: 'SCORE_UPDATE',
          payload: { gameState: game }
        }));
      }
    });

    return res.json({ gameState: game });
  };

  // Add more game-related methods...
}

export default new GameController();
