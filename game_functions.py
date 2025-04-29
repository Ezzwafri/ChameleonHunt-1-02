import random
import math
import numpy as np
from PIL import Image, ImageTk, ImageDraw

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
            "Easy": {"opacity": 0.6, "size_factor": 0.8},
            "Medium": {"opacity": 0.4, "size_factor": 0.5},
            "Hard": {"opacity": 0.15, "size_factor": 0.3}
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
        """Reset game state and hide chameleon in the image"""
        self.click_count = 0
        
        # Load the uploaded image
        if self.game_ui.image_file:
            self.original_image = Image.open(self.game_ui.image_file).convert("RGBA")
            
            # Apply difficulty settings
            difficulty = self.game_ui.difficulty.get()
            settings = self.difficulty_settings.get(difficulty, self.difficulty_settings["Medium"])
            
            # Resize chameleon based on difficulty
            chameleon_size = int(min(self.img_width, self.img_height) * 0.3 * settings["size_factor"])
            resized_chameleon = self.chameleon_image.resize(
                (chameleon_size, int(chameleon_size * self.chameleon_height / self.chameleon_width)),
                Image.Resampling.LANCZOS
            )
            
            # Choose random position for chameleon
            max_x = self.img_width - resized_chameleon.width
            max_y = self.img_height - resized_chameleon.height
            if max_x > 0 and max_y > 0:
                pos_x = random.randint(0, max_x)
                pos_y = random.randint(0, max_y)
                self.chameleon_pos = (pos_x, pos_y, pos_x + resized_chameleon.width, pos_y + resized_chameleon.height)
                
                # Create a copy of the original image
                blended_image = self.original_image.copy()
                
                # Blend the chameleon into the image with specified opacity
                self.blend_chameleon(blended_image, resized_chameleon, pos_x, pos_y, settings["opacity"])
                
                # Convert to Tkinter PhotoImage and update canvas
                self.game_image_with_chameleon = ImageTk.PhotoImage(blended_image)
                if hasattr(self.game_ui, 'game_canvas') and self.game_ui.game_canvas:
                    self.game_ui.game_canvas.delete("all")
                    self.game_ui.game_canvas.create_image(0, 0, image=self.game_image_with_chameleon, anchor="nw")
    
    def blend_chameleon(self, background, chameleon, x, y, opacity):
        """Blend the chameleon silhouette into the background image"""
        # Create a mask for the chameleon silhouette (black parts only)
        chameleon_array = np.array(chameleon)
        mask = chameleon_array[:, :, 3] > 0  # Alpha channel > 0
        
        # Convert background to numpy array
        bg_array = np.array(background)
        
        # For each pixel in the chameleon silhouette
        for i in range(chameleon.height):
            for j in range(chameleon.width):
                if i + y < background.height and j + x < background.width:
                    # If this pixel is part of the chameleon (black)
                    if mask[i, j]:
                        # Get pixel values
                        chameleon_pixel = chameleon_array[i, j]
                        bg_pixel = bg_array[i + y, j + x]
                        
                        # Create a subtle blend
                        blended = self.calculate_blend(bg_pixel, chameleon_pixel, opacity)
                        
                        # Apply blended pixel
                        bg_array[i + y, j + x] = blended
        
        # Convert back to PIL Image
        background.paste(Image.fromarray(bg_array), (0, 0))
    
    def calculate_blend(self, bg_pixel, chameleon_pixel, opacity):
        """Calculate the blended pixel value"""
        # For black chameleon parts, darken the background slightly and add a subtle hue
        if chameleon_pixel[0] == 0 and chameleon_pixel[1] == 0 and chameleon_pixel[2] == 0:
            # Darken the background pixel
            r = int(bg_pixel[0] * (1 - opacity))
            g = int(bg_pixel[1] * (1 - opacity))
            b = int(bg_pixel[2] * (1 - opacity))
            return np.array([r, g, b, 255], dtype=np.uint8)
        return bg_pixel
    
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
            self.highlight_chameleon()
        elif self.click_count >= self.max_clicks:
            # Player used all attempts
            self.game_ui.show_message("Game over! You couldn't find the chameleon.", False)
            self.highlight_chameleon()
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
    
    def highlight_chameleon(self):
        """Highlight the chameleon position"""
        if self.chameleon_pos and hasattr(self.game_ui, 'game_canvas') and self.game_ui.game_canvas:
            # Draw a highlight rectangle around the chameleon
            self.game_ui.game_canvas.create_rectangle(
                self.chameleon_pos[0], self.chameleon_pos[1],
                self.chameleon_pos[2], self.chameleon_pos[3],
                outline="#FF0000", width=3
            )