import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class GameLogic:
    def __init__(self, game_ui):
        self.game_ui = game_ui
        self.attempts = 0
        self.max_attempts = self.get_max_attempts()

    def get_max_attempts(self):
        #Set max attempts based on difficulty level
        difficulty = self.game_ui.difficulty.get()
        if difficulty == "Easy":
            return 10
        elif difficulty == "Medium":
            return 7
        else:  # Hard
            return 5

    

    def handle_click(self, event):
        #Handle mouse clicks on the game canvas
        self.attempts += 1
        remaining = self.max_attempts - self.attempts
        
        if remaining > 0:
            self.game_ui.show_message(f"Click #{self.attempts}. {remaining} clicks remaining.", False)
        else:
            self.game_over()

    def game_over(self):
        #Handle game over 
        self.game_ui.show_message("Game Over! Out of attempts!", False)

    def reset_game(self):
        #Reset game state for a new round
        self.attempts = 0
        self.max_attempts = self.get_max_attempts()
        