import math
import random
from PIL import Image, ImageTk, ImageEnhance, ImageDraw

class GameLogic:
    def __init__(self, game_ui):
        self.game_ui = game_ui
        self.chameleon_positions = []  # Stores positions of chameleons on the image
        self.found_chameleons = []  # Tracks which chameleons have been found
        self.click_count = 0
        self.max_clicks = 10
        self.img_width = 0
        self.img_height = 0
        self.chameleon_image = None  # Base image of the chameleon
        self.chameleon_width = 0
        self.chameleon_height = 0
        self.original_image = None  # User-uploaded original image
        self.game_image_with_chameleons = None  # Composite image with chameleon(s) blended in
        self.difficulty_settings = {  # Settings per difficulty level
            "Easy": {"size_factor": 0.15, "num_chameleons": 3, "opacity": 0.5, "color_match": 0.8},
            "Medium": {"size_factor": 0.12, "num_chameleons": 5, "opacity": 0.15, "color_match": 1.0},
            "Hard": {"size_factor": 0.09, "num_chameleons": 7, "opacity": 0.09, "color_match": 1.2}
        }
        self.load_chameleon_image()

    def load_chameleon_image(self):
        try:
            self.chameleon_image = Image.open("chameleon_silhouette.png")
            self.chameleon_width, self.chameleon_height = self.chameleon_image.size
        except:
            print("Error: chameleon_silhouette.png not found. Creating a placeholder.")
            self.create_placeholder_chameleon()

    
    def reset_game(self):
        try:
            self.original_image = Image.open(self.game_ui.image_file)
            self.original_image.thumbnail((800, 500))
            self.img_width, self.img_height = self.original_image.size
            difficulty = self.game_ui.difficulty.get()
            settings = self.difficulty_settings[difficulty]
            self.click_count = 0
            self.chameleon_positions = []
            self.found_chameleons = [False]  # Reset to only one chameleon
            base_size = min(self.img_width, self.img_height) * settings["size_factor"]
            self.game_image_with_chameleons = self.place_chameleon_center(base_size, settings)
            self.game_ui.game_image = ImageTk.PhotoImage(self.game_image_with_chameleons)
            self.game_ui.game_canvas.create_image(0, 0, image=self.game_ui.game_image, anchor="nw")
            self.game_ui.show_message(f"Find the chameleon! Clicks left: {self.max_clicks}", False)
        except Exception as e:
            print(f"Error resetting game: {e}")

    def get_average_color(self, image, x, y, width, height):
        # Crop a region and return the average color for blending
        crop = image.crop((x, y, x + width, y + height))
        avg_color = crop.resize((1, 1), Image.Resampling.LANCZOS).getpixel((0, 0))
        return avg_color[:3] if len(avg_color) == 4 else avg_color

    def blend_chameleon(self, chameleon, bg_color, opacity, color_match):
        # Blend the chameleon with the background color
        copy = chameleon.copy()
        if opacity < 1.0:
            if len(chameleon.split()) == 4:
                r, g, b, a = chameleon.split()
                a = ImageEnhance.Brightness(a).enhance(opacity)
            else:
                r, g, b = chameleon.split()
                a = Image.new('L', chameleon.size, int(255 * opacity))
            copy = Image.merge('RGBA', (r, g, b, a))

        pixels = copy.load()
        for x in range(copy.width):
            for y in range(copy.height):
                if copy.mode == 'RGBA':
                    r, g, b, a = pixels[x, y]
                    if a == 0: continue
                    if r > 200 and g > 200 and b > 200:
                        r, g, b = int(r * 0.2 + bg_color[0] * 0.8), int(g * 0.2 + bg_color[1] * 0.8), int(b * 0.2 + bg_color[2] * 0.8)
                    else:
                        r, g, b = int(r * (1 - color_match) + bg_color[0] * color_match), int(g * (1 - color_match) + bg_color[1] * color_match), int(b * (1 - color_match) + bg_color[2] * color_match)
                    pixels[x, y] = (r, g, b, a)
        return copy

    def place_chameleon_center(self, size, settings):
        # Place a single chameleon at the center of the image
        self.chameleon_positions.clear()
        self.found_chameleons = [False]
        img = self.original_image.copy()
        width = int(size)
        height = int(size * self.chameleon_height / self.chameleon_width)
        cx, cy = self.img_width // 2, self.img_height // 2
        x, y = cx - width // 2, cy - height // 2
        self.chameleon_positions.append((x, y, x + width, y + height))
        bg_color = self.get_average_color(self.original_image, x, y, width, height)
        resized = self.chameleon_image.resize((width, height), Image.Resampling.LANCZOS)
        match = settings["color_match"] * 0.6
        blended = self.blend_chameleon(resized, bg_color, settings["opacity"], match)
        img.paste(blended, (x, y), blended)
        return img

    def calculate_distance(self, x, y):
        # Calculate distance from click to center of the chameleon box
          return min(
        math.dist((x, y), ((x1 + x2) / 2, (y1 + y2) / 2))
        for x1, y1, x2, y2 in self.chameleon_positions
    )

    def get_feedback(self, distance):
        # Give heatmap-style feedback based on distance
        w = self.chameleon_positions[0][2] - self.chameleon_positions[0][0]
        h = self.chameleon_positions[0][3] - self.chameleon_positions[0][1]
        ref = min(w, h)
        
        if distance < ref:
            return "Hot. Sooo close..."
        elif distance < ref * 2:
            return "Warm. Getting closer."
        else:
            return "Cold. Try a completely different spot."

    def handle_click(self, event):
        # Process a click event: check if chameleon is found or give feedback
        if self.click_count >= self.max_clicks:
            self.game_ui.show_message("Game Over! You're out of clicks. Try again!", False)
            self.highlight_chameleon_red()
            return

        self.click_count += 1
        x, y = event.x, event.y

        for i, (x1, y1, x2, y2) in enumerate(self.chameleon_positions):
            if x1 <= x <= x2 and y1 <= y <= y2:
                if not self.found_chameleons[i]:
                    self.found_chameleons[i] = True
                    self.highlight_chameleon(i)
                    return
                else:
                    self.game_ui.show_message("You already found this chameleon!", True)
                    return
        

        dist = self.calculate_distance(x, y)
        msg = self.get_feedback(dist)
        self.game_ui.show_message(f"{msg} Clicks left: {self.max_clicks - self.click_count}", True)

    def highlight_chameleon_red(self):
    # Highlight all chameleons with a red border when clicks are over
      for x1, y1, x2, y2 in self.chameleon_positions:
        self.game_ui.game_canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=3)
    
    def highlight_chameleon(self, index):
        # Highlight the found chameleon with a rectangle
        if not self.chameleon_positions:
            return
        x1, y1, x2, y2 = self.chameleon_positions[index]
        self.game_ui.game_canvas.create_rectangle(x1, y1, x2, y2, outline="lime", width=3)
        self.game_ui.show_message("You found the chameleon!", True)
