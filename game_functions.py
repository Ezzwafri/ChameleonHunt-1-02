import math
from PIL import Image, ImageTk

class GameLogic:
    def __init__(self, game_ui):
        self.game_ui = game_ui
        self.chameleon_pos = None
        self.click_count = 0
        self.max_clicks = 3
        self.img_width = 0
        self.img_height = 0
        self.chameleon_image = None
        self.chameleon_width = 0
        self.chameleon_height = 0
        self.original_image = None
        self.game_image_with_chameleon = None
        self.difficulty_settings = {
            "Easy": {"size_factor": 0.6},
            "Medium": {"size_factor": 0.5},
            "Hard": {"size_factor": 0.3}
        }
        self.load_chameleon_silhouette()
    
    def load_chameleon_silhouette(self):
        try:
            # Load from file path
            self.chameleon_image = Image.open("chameleon_silhouette.png")
            # Get dimensions
            self.chameleon_width, self.chameleon_height = self.chameleon_image.size
        except:
            # If file doesn't exist, print an error message
            print("Error: chameleon_silhouette.png not found. Please make sure the file exists.")
            # Create a minimal placeholder (1x1 pixel) to avoid crashes
            self.chameleon_image = Image.new('RGBA', (1, 1), (0, 0, 0, 255))
            self.chameleon_width, self.chameleon_height = 1, 1
    
    def reset_game(self):
        """Reset game state and place chameleon in the middle of the image"""
        self.click_count = 0
        
        # Load the uploaded image
        if self.game_ui.image_file:
            self.original_image = Image.open(self.game_ui.image_file).convert("RGBA")
            self.img_width, self.img_height = self.original_image.size
            
            # Apply difficulty settings (size only)
            difficulty = self.game_ui.difficulty.get()
            settings = self.difficulty_settings.get(difficulty, self.difficulty_settings["Medium"])
            
            # Resize chameleon based on difficulty
            chameleon_size = int(min(self.img_width, self.img_height) * 0.3 * settings["size_factor"])
            resized_chameleon = self.chameleon_image.resize(
                (chameleon_size, int(chameleon_size * self.chameleon_height / self.chameleon_width)),
                Image.Resampling.LANCZOS
            )
            
            # Place chameleon in the center of the image
            pos_x = (self.img_width - resized_chameleon.width) // 2
            pos_y = (self.img_height - resized_chameleon.height) // 2
            self.chameleon_pos = (pos_x, pos_y, pos_x + resized_chameleon.width, pos_y + resized_chameleon.height)
                
            # Create a copy of the original image
            game_image = self.original_image.copy()
                
            # Simply paste the chameleon onto the image (no blending)
            game_image.paste(resized_chameleon, (pos_x, pos_y), resized_chameleon)
                
            # Convert to Tkinter PhotoImage and update canvas
            self.game_image_with_chameleon = ImageTk.PhotoImage(game_image)
            if hasattr(self.game_ui, 'game_canvas') and self.game_ui.game_canvas:
                self.game_ui.game_canvas.delete("all")
                self.game_ui.game_canvas.create_image(0, 0, image=self.game_image_with_chameleon, anchor="nw")
    
    def handle_click(self, event):
        """Handle player clicks on the image"""
        if not self.chameleon_pos:
            return
        
        x, y = event.x, event.y
        self.click_count += 1
        
        # Check if click is within chameleon bounds
        if (self.chameleon_pos[0] <= x <= self.chameleon_pos[2] and 
            self.chameleon_pos[1] <= y <= self.chameleon_pos[3]):
            # Player found the chameleon!
            self.game_ui.show_message(f"You found the chameleon in {self.click_count} tries!", True)
            self.highlight_chameleon(found=True)
        elif self.click_count >= self.max_clicks:
            # Player used all attempts
            self.game_ui.show_message("Game over! You couldn't find the chameleon.", False)
            self.highlight_chameleon(found=False)
        else:
            # Player still has attempts left
            remaining = self.max_clicks - self.click_count
            self.game_ui.show_message(f"Not there! {remaining} {'tries' if remaining > 1 else 'try'} left.", False)
            
            # Give a hint - tell the player if they're getting closer
            dist = self.calculate_distance(x, y)
            if dist < 100:
                self.game_ui.feedback.config(text=f"Getting warmer! {remaining} {'tries' if remaining > 1 else 'try'} left.", fg="#FF8C00")
    
    def calculate_distance(self, x, y):
        """Calculate distance from click to chameleon center"""
        chameleon_center_x = (self.chameleon_pos[0] + self.chameleon_pos[2]) / 2
        chameleon_center_y = (self.chameleon_pos[1] + self.chameleon_pos[3]) / 2
        return math.sqrt((x - chameleon_center_x)**2 + (y - chameleon_center_y)**2)
    
    def highlight_chameleon(self, found=False):
        """Highlight the chameleon position"""
        if self.chameleon_pos and hasattr(self.game_ui, 'game_canvas') and self.game_ui.game_canvas:
            # Use green border if found, red if not found
            border_color = "#00FF00" if found else "#FF0000"
            
            # Draw a highlight rectangle around the chameleon
            self.game_ui.game_canvas.create_rectangle(
                self.chameleon_pos[0], self.chameleon_pos[1],
                self.chameleon_pos[2], self.chameleon_pos[3],
                outline=border_color, width=3
            )