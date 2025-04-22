import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class GameLogic:
    def __init__(self, game_ui):
        self.game_ui = game_ui
        self.chameleon_x = 0
        self.chameleon_y = 0
        self.chameleon_radius = 30
        self.attempts = 0
        self.max_attempts = self.get_max_attempts()
        
    def get_max_attempts(self):
        """Set max attempts based on difficulty level"""
        difficulty = self.game_ui.difficulty.get()
        if difficulty == "Easy":
            return 10
        elif difficulty == "Medium":
            return 7
        else:  # Hard
            return 5
    
    def upload_image(self):
        """Enhanced upload image function"""
        file = self.game_ui.image_file
        if file:
            try:
                # Load and process the image
                img = Image.open(file)
                img.thumbnail((800, 550))  # Resize to fit canvas
                
                # Store original image dimensions for calculations
                self.img_width, self.img_height = img.size
                
                # Generate random position for the chameleon
                self.place_chameleon()
                
                # Update feedback
                self.game_ui.feedback.config(text="Image loaded! Ready to hunt!", fg="#008000")
                return True
            except Exception as e:
                self.game_ui.feedback.config(text=f"Error loading image: {e}", fg="#FF0000")
                return False
        else:
            self.game_ui.feedback.config(text="No image selected", fg="#FF0000")
            return False
    
    def place_chameleon(self):
        """Place the chameleon at a random location"""
        # Set margins to ensure chameleon isn't too close to edges
        margin = 50
        self.chameleon_x = random.randint(margin, self.img_width - margin)
        self.chameleon_y = random.randint(margin, self.img_height - margin)
        
        # Adjust chameleon size based on difficulty
        difficulty = self.game_ui.difficulty.get()
        if difficulty == "Easy":
            self.chameleon_radius = 40
        elif difficulty == "Medium":
            self.chameleon_radius = 30
        else:  # Hard
            self.chameleon_radius = 20
    
    def handle_click(self, event):
        """Handle mouse clicks on the game canvas"""
        self.attempts += 1
        
        # Calculate distance from click to chameleon
        distance = ((event.x - self.chameleon_x)**2 + (event.y - self.chameleon_y)**2)**0.5
        
        # Check if chameleon was found
        if distance <= self.chameleon_radius:
            self.show_found_chameleon()
            return
        
        # Check if out of attempts
        if self.attempts >= self.max_attempts:
            self.game_over()
            return
        
        # Provide feedback based on distance
        self.provide_distance_feedback(distance)
    
    def show_found_chameleon(self):
        """Show chameleon and success message"""
        # Draw circle around chameleon
        self.game_ui.game_canvas.create_oval(
            self.chameleon_x - self.chameleon_radius, 
            self.chameleon_y - self.chameleon_radius,
            self.chameleon_x + self.chameleon_radius, 
            self.chameleon_y + self.chameleon_radius,
            outline="green", width=3
        )
        
        # Add chameleon text
        self.game_ui.game_canvas.create_text(
            self.chameleon_x, self.chameleon_y,
            text="🦎", font=("Arial", 24), fill="green"
        )
        
        # Show success message
        attempts_text = f"You found it in {self.attempts} attempts!"
        self.game_ui.show_message(f"You found the chameleon! {attempts_text}", True)
        
        # Disable further clicks
        self.game_ui.game_canvas.unbind("<Button-1>")
        
        messagebox.showinfo("Congratulations!", f"You found the chameleon in {self.attempts} attempts!")
    
    def game_over(self):
        """Handle game over condition"""
        # Show chameleon location
        self.game_ui.game_canvas.create_oval(
            self.chameleon_x - self.chameleon_radius, 
            self.chameleon_y - self.chameleon_radius,
            self.chameleon_x + self.chameleon_radius, 
            self.chameleon_y + self.chameleon_radius,
            outline="red", width=3
        )
        
        self.game_ui.game_canvas.create_text(
            self.chameleon_x, self.chameleon_y,
            text="🦎", font=("Arial", 24), fill="red"
        )
        
        # Show game over message
        self.game_ui.show_message("Game Over! Out of attempts!", False)
    
    def provide_distance_feedback(self, distance):
        """Provide feedback based on click distance"""
        difficulty = self.game_ui.difficulty.get()
        
        # For Easy mode, provide more detailed feedback
        if difficulty == "Easy":
            if distance < 50:
                feedback = "Very hot! You're extremely close!"
            elif distance < 100:
                feedback = "Hot! Getting closer!"
            elif distance < 200:
                feedback = "Warm... Keep looking!"
            else:
                feedback = "Cold... Try a different area."
        
        # For Medium mode, provide moderate feedback
        elif difficulty == "Medium":
            if distance < 75:
                feedback = "Warm! Getting closer!"
            else:
                feedback = "Cold... Keep looking!"
        
        # For Hard mode, provide minimal feedback
        else:
            feedback = f"Attempts left: {self.max_attempts - self.attempts}"
        
        # Update the feedback label
        self.game_ui.show_message(feedback, False)
    
    def reset_game(self):
        """Reset game state for a new round"""
        self.attempts = 0
        self.max_attempts = self.get_max_attempts()
        # Reset chameleon position if image is loaded
        if self.game_ui.image_file:
            self.place_chameleon()