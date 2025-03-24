from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import eventlet
eventlet.monkey_patch()

import cv2
from typing import Dict, List
from ultralytics import YOLO
import logging
import base64
from datetime import datetime
import csv

from game_modes.training import TrainingMode, TrainingTarget
from utils.voice_feedback import VoiceFeedback
from utils.calibration import BoardCalibrator
from utils.data_export import DataExporter
from analytics.throw_analyzer import ThrowAnalyzer
from player.profile_manager import ProfileManager
from game_modes.tournament import Tournament
from analytics.visualizer import DartsVisualizer
from ai_coach.coach import AICoach
from multiplayer.game_server import GameServer
from social.social_manager import SocialManager
eventlet.monkey_patch()

# Set up logging with enhanced format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add a new handler to log to a file
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app = Flask(__name__)
# Enable CORS
CORS(app, resources={r"/*": {
    "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type"],
    "supports_credentials": True
}})

# Configure SocketIO with more stable settings
socketio = SocketIO(
    app,
    cors_allowed_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    async_mode='eventlet',
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=100000000,  # Using integer instead of scientific notation
    engineio_logger=True
)

# Load the YOLO model
model_path = "Dartopia/model/best/best.pt"  # Update this line

model = YOLO(model_path)
model.conf = 0.5  # Adjusted confidence threshold for predictions

logger.info("YOLO model loaded successfully")

# Initialize camera feeds
camera_indices = [0, 1, 2]
cameras: Dict[int, cv2.VideoCapture] = {}
for idx in camera_indices:
    cap = cv2.VideoCapture(idx)
    if cap.isOpened():
        cameras[idx] = cap
        logger.info(f"Camera {idx} initialized")
    else:
        logger.warning(f"Failed to initialize camera {idx}")

# Store latest predictions for each camera
latest_predictions: Dict[int, List[dict]] = {idx: [] for idx in camera_indices}

# Initialize components
voice_feedback = VoiceFeedback()
board_calibrator = BoardCalibrator()
data_exporter = DataExporter()
throw_analyzer = ThrowAnalyzer()
profile_manager = ProfileManager()
visualizer = DartsVisualizer()
ai_coach = AICoach()
game_server = GameServer()
social_manager = SocialManager()
active_tournaments = {}

def calculate_score(predictions: List[dict]) -> dict:
    if not predictions:
        return {"total": 0, "details": []}
        
    score_details = []
    total_score = 0
    
    # First, find the dartboard for reference
    dartboard = None
    for pred in predictions:
        if 'dartboard' in pred['label'].lower():
            dartboard = pred
            break
    
    # Find all darts
    darts = [p for p in predictions if 'dart' in p['label'].lower()]
    
    # Find all scoring regions
    scoring_regions = [p for p in predictions if all(x not in p['label'].lower() for x in ['dart', 'dartboard'])]
    
    for dart in darts:
        dart_x = dart['bbox'][0] + dart['bbox'][2]/2
        dart_y = dart['bbox'][1] + dart['bbox'][3]/2
        score_info = {
            "label": dart['label'],
            "confidence": dart['confidence'],
            "location": dart['bbox'],
            "points": 0,
            "region": "outside"
        }
        
        # Only score if we have a dartboard reference
        if dartboard:
            board_x = dartboard['bbox'][0] + dartboard['bbox'][2]/2
            board_y = dartboard['bbox'][1] + dartboard['bbox'][3]/2
            board_radius = max(dartboard['bbox'][2], dartboard['bbox'][3])/2
            
            # Calculate distance from dart to board center
            dist_to_center = ((dart_x - board_x)**2 + (dart_y - board_y)**2)**0.5
            
            # If dart is within board radius
            if dist_to_center <= board_radius:
                # Find the closest scoring region
                best_region = None
                min_dist = float('inf')
                
                for region in scoring_regions:
                    region_x = region['bbox'][0] + region['bbox'][2]/2
                    region_y = region['bbox'][1] + region['bbox'][3]/2
                    dist = ((dart_x - region_x)**2 + (dart_y - region_y)**2)**0.5
                    
                    if dist < min_dist:
                        min_dist = dist
                        best_region = region
                
                if best_region:
                    region_label = best_region['label'].lower()
                    score_info["region"] = region_label
                    
                    # Calculate points based on region
                    if 'bulls_eye' in region_label or 'bullseye' in region_label:
                        score_info["points"] = 50
                    elif 'bull' in region_label:
                        score_info["points"] = 25
                    elif 'triple' in region_label:
                        try:
                            base = int(''.join(filter(str.isdigit, region_label)))
                            score_info["points"] = base * 3
                        except ValueError:
                            score_info["points"] = 0
                    elif 'double' in region_label:
                        try:
                            base = int(''.join(filter(str.isdigit, region_label)))
                            score_info["points"] = base * 2
                        except ValueError:
                            score_info["points"] = 0
                    else:
                        try:
                            score_info["points"] = int(''.join(filter(str.isdigit, region_label)))
                        except ValueError:
                            score_info["points"] = 0
                    
                    total_score += score_info["points"]
        
        score_details.append(score_info)
    
    # Sort details by points (highest first) and filter out zero scores
    score_details = sorted(score_details, key=lambda x: x["points"], reverse=True)
    score_details = [d for d in score_details if d["points"] > 0]
    
    return {
        "total": total_score,
        "details": score_details
    }

@socketio.on('connect')
def handle_connect():
    logger.info("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    logger.info("Client disconnected")

# Store active training sessions
training_sessions = {}

@socketio.on('start_training')
def handle_training_start(data):
    session_id = data.get('session_id')
    routine_type = TrainingTarget[data.get('routine_type', 'SPECIFIC_NUMBER')]
    specific_numbers = data.get('specific_numbers', [])

    training_session = TrainingMode()
    training_session.set_training_routine(routine_type, specific_numbers)
    training_sessions[session_id] = training_session

    return {'status': 'success', 'first_target': training_session.current_target}

# Add new route for calibration
@socketio.on('calibrate_board')
def handle_calibration(data):
    frame_data = data.get('frame')
    # Convert base64 frame to numpy array
    frame = cv2.imdecode(np.frombuffer(base64.b64decode(frame_data), np.uint8), cv2.IMREAD_COLOR)
    
    if board_calibrator.detect_board_automatically(frame):
        return {'status': 'success', 'message': 'Board detected and calibrated'}
    return {'status': 'error', 'message': 'Could not detect board'}

@socketio.on('request_camera_feed')
def handle_camera_feed(data):
    camera_idx = data.get('camera_idx')
    session_id = data.get('session_id')

    if camera_idx not in cameras:
        socketio.emit('camera_error', {'error': f'Camera {camera_idx} not available'}, room=data.get('sid'))
        return

    cap = cameras[camera_idx]
    training_session = training_sessions.get(session_id)

    logger.info(f"Starting camera feed for camera {camera_idx}")

    while True:  # Main loop for processing camera feed

        ret, frame = cap.read()
        if not ret:
            logger.warning(f"Failed to read frame from camera {camera_idx}")
            socketio.emit('camera_error', {'error': f'Failed to read frame from camera {camera_idx}'}, room=data.get('sid'))
            return  # Use return instead of break to exit the function


        try:
            # Apply calibration if available
            calibrated_frame = board_calibrator.calibrate_frame(frame)
            if calibrated_frame is not None:
                frame = calibrated_frame

            # Perform inference
            results = model(frame)
            predictions = []

            for result in results:
                boxes = result.boxes.xywh.cpu().numpy()
                labels = result.boxes.cls.cpu().numpy()
                confidences = result.boxes.conf.cpu().numpy()
                names = result.names

                for box, label, conf in zip(boxes, labels, confidences):
                    x, y, w, h = box
                    predictions.append({
                        'label': names[int(label)],
                        'confidence': float(conf),
                        'bbox': [float(x - w/2), float(y - h/2), float(w), float(h)]
                    })

            # Only calculate score if we have both darts and regions detected
            score = calculate_score(predictions)  # Calculate score based on predictions

            # Process training session if active
            training_data = None
            if training_session:
                training_data = training_session.process_throw(predictions)

            # Analyze throw
            throw_analyzer.add_throw({
                'predictions': predictions,
                'score': score['total'],
                'hit': bool(score['total'] > 0),
                'coordinates': predictions[0]['bbox'][:2] if predictions else (0, 0),
                'region': score['details'][0]['region'] if score['details'] else 'unknown'
            })

            # Provide voice feedback
            voice_feedback.announce_score(score['total'], score['details'][0]['region'] if score['details'] else None)

            # Export data periodically
            if len(throw_analyzer.throws_history) % 10 == 0:
                data_exporter.export_session({
                    'throws': throw_analyzer.throws_history,
                    'metrics': throw_analyzer.calculate_metrics().__dict__
                })

            # Encode frame as base64
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')

            # Send frame, predictions, score, and training data
            socketio.emit('camera_frame', {
                'camera_idx': camera_idx,
                'frame': frame_base64,
                'predictions': predictions,
                'score': score,
                'training_data': training_data
            }, room=data.get('sid'))

            socketio.sleep(0.05)  # Rate limiting

        except Exception as e:
            logger.error(f"Error processing frame from camera {camera_idx}: {str(e)}")
            socketio.emit('camera_error', {'error': f'Error processing frame: {str(e)}'}, room=data.get('sid'))
            break  # Exit the loop on error


if __name__ == "__main__":
    # Removed redundant app context
    pass
