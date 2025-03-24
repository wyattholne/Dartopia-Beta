import express from 'express';
import GameController from '../controllers/GameController';

const router = express.Router();

router.post('/create', GameController.createGame);
router.post('/score', GameController.recordScore);
// Add more routes as needed...

export default router;
