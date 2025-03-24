from gtts import gTTS
import pygame
import os
from queue import Queue
from threading import Thread
import time

class VoiceFeedback:
    def __init__(self):
        pygame.mixer.init()
        self.feedback_queue = Queue()
        self.is_running = True
        self.feedback_thread = Thread(target=self._process_feedback_queue)
        self.feedback_thread.start()
        
    def _process_feedback_queue(self):
        while self.is_running:
            if not self.feedback_queue.empty():
                text = self.feedback_queue.get()
                self._speak(text)
            time.sleep(0.1)
    
    def _speak(self, text: str):
        try:
            tts = gTTS(text=text, lang='en')
            temp_file = "temp_voice.mp3"
            tts.save(temp_file)
            
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            os.remove(temp_file)
        except Exception as e:
            print(f"Error in voice feedback: {str(e)}")
    
    def announce_score(self, score: int, region: str = None):
        text = f"Score {score}"
        if region:
            text += f", {region}"
        self.feedback_queue.put(text)
    
    def announce_game_status(self, remaining: int):
        if remaining == 0:
            self.feedback_queue.put("Game shot and the match!")
        elif remaining <= 100:
            self.feedback_queue.put(f"{remaining} remaining")
    
    def announce_training_feedback(self, feedback: str):
        self.feedback_queue.put(feedback)
    
    def cleanup(self):
        self.is_running = False
        self.feedback_thread.join()
        pygame.mixer.quit()