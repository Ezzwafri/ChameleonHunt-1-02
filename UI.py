import random
from PIL import ImageTk

class GameLogic:
    def __init__(self, ui):
        self.ui = ui
        self.img_width = 0
        self.img_height = 0
        self.chameleon_x = 0
        self.chameleon_y = 0
        self.click_radius = 30  # Clickable radius
        self.found = False
        self.circle_id = None
        self.attempts = 0
        self.max_attempts = 5
        
    def reset_game(self):
        """Reset the game state for a new round"""
        self.found = False
        self.attempts = 0
        
        # Reset UI elements
        if hasattr(self.ui, 'game_canvas') and self.ui.game_canvas:
            if self.circle_id:
                try:
                    self.ui.game_canvas.delete(self.circle_id)
                except:
                    pass
            self.circle_id = None
            
        # Place chameleon randomly
        margin = 50  # Keep away from edges
        if self.img_width > 0 and self.img_height > 0:
            self.chameleon_x = random.randint(margin, self.img_width - margin)
            self.chameleon_y = random.randint(margin, self.img_height - margin)
            
        # Adjust difficulty
        difficulty = self.ui.difficulty.get()
        if difficulty == "Easy":
            self.click_radius = 50
            self.max_attempts = 8
        elif difficulty == "Medium":
            self.click_radius = 30
            self.max_attempts = 5
        else:  # Hard
            self.click_radius = 15
            self.max_attempts = 3
            
    def handle_click(self, event):
        """Handle mouse clicks on the image"""
        if self.found:
            return
            
        # Get click position
        x, y = event.x, event.y
        
        # Calculate distance to chameleon
        distance = ((x - self.chameleon_x) ** 2 + (y - self.chameleon_y) ** 2) ** 0.5
        
        # Check if chameleon found
        if distance <= self.click_radius:
            self.found = True
            
            # Draw circle around chameleon
            self.circle_id = self.ui.game_canvas.create_oval(
                self.chameleon_x - self.click_radius, 
                self.chameleon_y - self.click_radius,
                self.chameleon_x + self.click_radius, 
                self.chameleon_y + self.click_radius,
                outline="green", width=3
            )
            
            # Stop timer if running
            if self.ui.timer_running:
                self.ui.stop_timer()
            
            # Show full unblurred image when chameleon is found
            if hasattr(self.ui, 'original_image') and self.ui.original_image:
                self.ui.game_image = ImageTk.PhotoImage(self.ui.original_image)
                self.ui.game_canvas.itemconfig(self.ui.image_on_canvas, image=self.ui.game_image)
            
            self.ui.show_message(f"You found the chameleon! Great job!", True)
        else:
            # Wrong click
            self.attempts += 1
            attempts_left = self.max_attempts - self.attempts
            
            if attempts_left <= 0:
                # Game over
                
                # Show full unblurred image first
                if hasattr(self.ui, 'original_image') and self.ui.original_image:
                    self.ui.game_image = ImageTk.PhotoImage(self.ui.original_image)
                    self.ui.game_canvas.itemconfig(self.ui.image_on_canvas, image=self.ui.game_image)
                
                # Then draw circle
                self.circle_id = self.ui.game_canvas.create_oval(
                    self.chameleon_x - self.click_radius, 
                    self.chameleon_y - self.click_radius,
                    self.chameleon_x + self.click_radius, 
                    self.chameleon_y + self.click_radius,
                    outline="red", width=3
                )
                self.ui.show_message(f"Game over! The chameleon was here!", False)
                
                # Stop timer if running
                if self.ui.timer_running:
                    self.ui.stop_timer()
            else:
                hint = ""
                if distance < 100:
                    hint = "Very close! "
                elif distance < 200:
                    hint = "Getting warmer! "
                    
                self.ui.show_message(f"{hint}Keep looking! {attempts_left} attempts left.", False)
