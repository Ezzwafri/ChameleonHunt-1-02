import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import random

class StoryImages:
    """Class to handle story mode images"""
    def __init__(self):
        self.story_levels = [
            {
                "name": "1",
                "description": "Welcome! Discover and hunt the Ghost Chameleons.",
                "image_data": "Level1.jpg",
                "placeholder_color": "#228B22", 
                "difficulty": "Easy",
            },
            {
                "name": "Colourful Life",
                "description": "Chameleons are adapting! Medium difficulty.",
                "image_data": "Level2.jpg",
                "placeholder_color": "#DEB887",  
                "difficulty": "Medium",
            },
            {
                "name": "Adventure In Jungle",
                "description": "The chase heats up! Medium difficulty.",
                "image_data": "Level3.jpg",
                "placeholder_color": "#708090",  
                "difficulty": "Medium",
            },
            {
                "name": "Inside The Things",
                "description": "They become elusive! Hard difficulty.",
                "image_data": "Level4.jpg",
                "placeholder_color": "#4682B4",  
                "difficulty": "Hard",
            },
            {
                "name": "Messy Room",
                "description": "Trust building, last challenge! Hard difficulty.",
                "image_data": "Level5.jpeg",
                "placeholder_color": "#800080", 
                "difficulty": "Hard",
            }
        ]
        self.current_level = 0

    def get_current_level(self):
        """Get the current story level"""
        return self.story_levels[self.current_level]

    def next_level(self):
        """Move to next level"""
        self.current_level += 1
        return self.current_level < len(self.story_levels)

    def reset_levels(self):
        """Reset to first level"""
        self.current_level = 0