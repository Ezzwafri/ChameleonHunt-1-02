import math
import random
import numpy as np
from PIL import ImageEnhance, Image, ImageFilter, ImageStat,ImageTk

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
            "Easy": {
                "size_factor": 0.15, 
                "num_chameleons": 3, 
                "opacity": 0.8, 
                "color_match": 0.7,
                "complexity_weight": 0.4,
                "color_weight": 0.3,
                "edge_weight": 0.3,
                "min_distance_factor": 0.2
            },
            "Medium": {
                "size_factor": 0.12, 
                "num_chameleons": 5, 
                "opacity": 0.5, 
                "color_match": 0.85,
                "complexity_weight": 0.5,
                "color_weight": 0.3,
                "edge_weight": 0.2,
                "min_distance_factor": 0.15
            },
            "Hard": {
                "size_factor": 0.09, 
                "num_chameleons": 7, 
                "opacity": 0.3, 
                "color_match": 1.0,
                "complexity_weight": 0.6,
                "color_weight": 0.3,
                "edge_weight": 0.1,
                "min_distance_factor": 0.1
            }
        }
        # Initialize attributes
        self.found = False
        self.add_time_uses = 1
        self.add_steps_uses = 1
        self.chameleon_x = 0
        self.chameleon_y = 0
        self.click_radius = 20
        self.last_click_pos = None  # Track the last click position for heatmap visualization
        self.heatmap_indicators = []  # Initialize for tracking indicators
        
        self.load_chameleon_image()

    def load_chameleon_image(self):
        try:
            self.chameleon_image = Image.open("chameleon_silhouette.png")
            self.chameleon_width, self.chameleon_height = self.chameleon_image.size
        except Exception as e:
            print(f"Error: chameleon_silhouette.png not found. {e}")
            
    def reset_game(self):
        try:
            self.original_image = Image.open(self.game_ui.image_file)
            self.original_image.thumbnail((800, 500))
            self.img_width, self.img_height = self.original_image.size
            difficulty = self.game_ui.difficulty.get()
            settings = self.difficulty_settings[difficulty]
            self.click_count = 0
            self.chameleon_positions = []
            self.found_chameleons = []
            self.found = False
            self.last_click_pos = None
            self.heatmap_indicators = []
            
            # Adjust max clicks based on difficulty
            self.max_clicks = 10 + settings["num_chameleons"]
            
            # Reset powerup uses
            self.add_time_uses = 1
            self.add_steps_uses = 1
            
            # Place chameleons strategically
            self.game_image_with_chameleons = self.place_chameleons_smartly(settings)
            
            self.game_ui.game_image = ImageTk.PhotoImage(self.game_image_with_chameleons)
            self.game_ui.game_canvas.create_image(0, 0, image=self.game_ui.game_image, anchor="nw")
            self.game_ui.show_message(f"Find {len(self.chameleon_positions)} chameleon{'s' if len(self.chameleon_positions) > 1 else ''}! Clicks left: {self.max_clicks}", False)
            
            # Update powerup buttons
            if hasattr(self.game_ui, 'update_powerup_buttons'):
                self.game_ui.update_powerup_buttons()
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
        
        except Exception as e:
            print(f"Error resetting game: {e}")
            self.game_ui.show_message("Error loading image. Please try again with a different image.", False)

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

        # Apply adaptive color matching
        pixels = copy.load()
        for x in range(copy.width):
            for y in range(copy.height):
                if copy.mode == 'RGBA':
                    r, g, b, a = pixels[x, y]
                    if a == 0: continue
                    
                    # More sophisticated color blending based on pixel brightness
                    brightness = (r + g + b) / 3
                    blend_factor = color_match
                    
                    # Lighter areas get more background color
                    if brightness > 200:
                        blend_factor = min(1.0, color_match * 1.2)
                    
                    r = int(r * (1 - blend_factor) + bg_color[0] * blend_factor)
                    g = int(g * (1 - blend_factor) + bg_color[1] * blend_factor)
                    b = int(b * (1 - blend_factor) + bg_color[2] * blend_factor)
                    
                    pixels[x, y] = (r, g, b, a)
        return copy

    def calculate_complexity_map(self, img):
        """Calculate a complexity map for the image (higher values = more complex areas)"""
        # Convert to grayscale for edge detection
        if img.mode == 'RGBA':
            gray_img = img.convert('L')
        else:
            gray_img = img.convert('L')
        
        # Apply edge detection filter
        edge_img = gray_img.filter(ImageFilter.FIND_EDGES)
        
        # Apply texture detection (variance of local regions)
        texture_img = gray_img.filter(ImageFilter.RankFilter(7, 4))
        
        # Combine edge and texture info
        edge_data = np.array(edge_img)
        texture_data = np.array(texture_img)
        
        # Create complexity map (higher values = better hiding spots)
        complexity = edge_data * 0.7 + texture_data * 0.3
        
        # Normalize to 0-1 range
        if complexity.max() > 0:
            complexity = complexity / complexity.max()
            
        return complexity
    
    def find_candidate_positions(self, settings, num_positions=20):
        """Find candidate positions for chameleons based on image complexity and difficulty"""
        width = int(min(self.img_width, self.img_height) * settings["size_factor"])
        height = int(width * self.chameleon_height / self.chameleon_width)
        
        # Calculate image complexity
        complexity_map = self.calculate_complexity_map(self.original_image)
        
        # Extract difficulty-specific weights
        complexity_weight = settings["complexity_weight"]
        color_weight = settings["color_weight"]
        edge_weight = settings["edge_weight"]
        
        # Use complexity to find good positions
        candidates = []
        margin = int(width * 0.2)  # Keep away from image edges
        
        # Generate random positions weighted by complexity
        for _ in range(num_positions * 4):  # Generate more than needed to select from
            # Generate random position
            x = random.randint(margin, self.img_width - width - margin)
            y = random.randint(margin, self.img_height - height - margin)
            
            # Calculate average complexity in this region
            region_complexity = np.mean(complexity_map[y:y+height, x:x+width])
            
            # Get color variability score
            region = self.original_image.crop((x, y, x+width, y+height))
            color_stats = ImageStat.Stat(region)
            # Higher standard deviation means more color variation
            color_variability = sum(color_stats.stddev) / 3 if hasattr(color_stats, 'stddev') else 0
            
            # Calculate distance from center (prefer edges over center)
            center_x, center_y = self.img_width / 2, self.img_height / 2
            distance_from_center = math.sqrt((x + width/2 - center_x)**2 + (y + height/2 - center_y)**2)
            max_distance = math.sqrt(center_x**2 + center_y**2)
            edge_factor = distance_from_center / max_distance
            
            # Combined score with dynamic weights based on difficulty
            hiding_score = (
                region_complexity * complexity_weight + 
                (color_variability / 255) * color_weight + 
                edge_factor * edge_weight
            )
            
            candidates.append((x, y, width, height, hiding_score))
        
        # Sort by hiding score and return top positions
        candidates.sort(key=lambda c: c[4], reverse=True)
        return candidates[:num_positions]
    
    def place_chameleons_smartly(self, settings):
        """Place chameleons at smart positions based on image analysis and difficulty"""
        img = self.original_image.copy()
        num_chameleons = settings["num_chameleons"]
        
        # Get candidate positions with difficulty-based parameters
        candidates = self.find_candidate_positions(settings, num_positions=num_chameleons*3)
        
        # Minimum distance between chameleons (varies by difficulty)
        min_distance = min(self.img_width, self.img_height) * settings["min_distance_factor"]
        
        # Select positions ensuring minimum distance between chameleons
        selected_positions = []
        self.chameleon_positions = []
        
        for x, y, width, height, score in candidates:
            # Check if too close to already selected positions
            too_close = False
            for sx, sy, sw, sh in selected_positions:
                distance = math.sqrt((x + width/2 - (sx + sw/2))**2 + (y + height/2 - (sy + sh/2))**2)
                if distance < min_distance:
                    too_close = True
                    break
            
            if not too_close:
                selected_positions.append((x, y, width, height))
                self.chameleon_positions.append((x, y, x + width, y + height))
                
                if len(selected_positions) >= num_chameleons:
                    break
        
        # If we couldn't find enough non-overlapping positions, just use the top scored ones
        if len(selected_positions) < num_chameleons:
            for i in range(len(selected_positions), min(num_chameleons, len(candidates))):
                x, y, width, height, _ = candidates[i]
                selected_positions.append((x, y, width, height))
                self.chameleon_positions.append((x, y, x + width, y + height))
        
        # Initialize found_chameleons list based on final number of chameleons
        self.found_chameleons = [False] * len(self.chameleon_positions)
        
        # Place chameleons at selected positions
        for x, y, width, height in selected_positions:
            bg_color = self.get_average_color(img, x, y, width, height)
            resized = self.chameleon_image.resize((width, height), Image.Resampling.LANCZOS)
            blended = self.blend_chameleon(resized, bg_color, settings["opacity"], settings["color_match"])
            img.paste(blended, (x, y), blended)
            
            # Set a reference point for the first chameleon (for timer expiration)
            if not hasattr(self, 'chameleon_x') or self.chameleon_x == 0:
                self.chameleon_x = x + width/2
                self.chameleon_y = y + height/2
                
        return img

    def calculate_distance(self, x, y):
        # Calculate distance from click to nearest chameleon center
        if not self.chameleon_positions:
            return float('inf')
            
        return min(
            math.dist((x, y), ((x1 + x2) / 2, (y1 + y2) / 2))
            for x1, y1, x2, y2 in self.chameleon_positions
        )

    def get_feedback(self, distance):
        # Give heatmap-style feedback based on distance
        if not self.chameleon_positions:
            return "No chameleons placed yet!"
            
        # Use the average size of chameleons as reference
        ref = 0
        for x1, y1, x2, y2 in self.chameleon_positions:
            ref += max(x2 - x1, y2 - y1)
        ref = ref / len(self.chameleon_positions) / 2
        
        if distance < ref / 2:
            return "🔥 HOT! A chameleon is right under your cursor!"
        elif distance < ref:
            return "✨ VERY WARM! You're just pixels away from a chameleon!"
        elif distance < ref * 2:
            return "👀 WARM! You're in the right area, look carefully..."
        elif distance < ref * 4:
            return "❄️ COOL. You're on the wrong track, try elsewhere."
        else:
            return "🧊 FREEZING! No chameleons hiding anywhere near here."

    def handle_click(self, event):
        # Process a click event: check if chameleon is found or give feedback
        if self.click_count >= self.max_clicks:
            found_count = sum(self.found_chameleons)
            total_count = len(self.found_chameleons)
            self.game_ui.show_message(f"Game Over! You found {found_count} out of {total_count} chameleons.", False)
            self.highlight_chameleons_red()
            return

        self.click_count += 1
        x, y = event.x, event.y
        self.last_click_pos = (x, y)

        # Check if click is on any chameleon
        chameleon_found = False
        for i, (x1, y1, x2, y2) in enumerate(self.chameleon_positions):
            if x1 <= x <= x2 and y1 <= y <= y2:
                if not self.found_chameleons[i]:
                    self.found_chameleons[i] = True
                    self.highlight_chameleon(i)
                    chameleon_found = True
                    
                    # Check if all chameleons are found
                    if all(self.found_chameleons):
                        self.found = True
                        clicks_used = self.click_count
                        efficiency = round((len(self.found_chameleons) / clicks_used) * 100)
                        self.game_ui.show_message(f"You found all {len(self.found_chameleons)} chameleons in {clicks_used} clicks! Efficiency rating: {efficiency}%", True)
                    else:
                        remaining = sum(1 for found in self.found_chameleons if not found)
                        found_so_far = sum(self.found_chameleons)
                        clicks_left = self.max_clicks - self.click_count
                        self.game_ui.show_message(f"You found chameleon #{found_so_far}! Still {remaining} hidden chameleons to find. {clicks_left} clicks remaining.", True)
                    return
                else:
                    self.game_ui.show_message("You already spotted this chameleon! Try looking elsewhere.", True)
                    return
        
        if not chameleon_found:
            dist = self.calculate_distance(x, y)
            msg = self.get_feedback(dist)
            clicks_left = self.max_clicks - self.click_count
            self.game_ui.show_message(f"{msg} Clicks left: {clicks_left}", True)
            self.show_heatmap_indicator(x, y, dist)
        
            # Stop timer if running
            if self.ui.timer_running:
                self.ui.stop_timer()
            
            # Show full unblurred image when chameleon is found
            if hasattr(self.ui, 'original_image') and self.ui.original_image:
                self.ui.game_image = ImageTk.PhotoImage(self.ui.original_image)
                self.ui.game_canvas.itemconfig(self.ui.image_on_canvas, image=self.ui.game_image)

    def show_heatmap_indicator(self, x, y, distance):
        """Show a visual indicator at click position based on distance to nearest chameleon"""
        # Calculate reference distance from average chameleon size
        ref = 0
        for x1, y1, x2, y2 in self.chameleon_positions:
            ref += max(x2 - x1, y2 - y1)
        ref = ref / len(self.chameleon_positions) / 2
        
        # Determine color based on distance
        if distance < ref / 2:
            color = "#ff0000"  # Red - very hot
        elif distance < ref:
            color = "#ff6600"  # Orange - warm
        elif distance < ref * 2:
            color = "#ffcc00"  # Yellow - getting warmer
        elif distance < ref * 4:
            color = "#00ccff"  # Light blue - cool
        else:
            color = "#0066ff"  # Blue - cold
        
        # Create a pulsing circle effect
        size = 20
        
        # Clean up old indicators
        for indicator in self.heatmap_indicators:
            try:
                self.game_ui.game_canvas.delete(indicator)
            except:
                pass
        
        # Create new indicator
        indicator = self.game_ui.game_canvas.create_oval(
            x - size, y - size, x + size, y + size, 
            outline=color, width=2, fill="", tags="heatmap"
        )
        self.heatmap_indicators = [indicator]
        
        # Schedule the indicator to fade out
        self.game_ui.window.after(2000, lambda: self.fade_indicator(indicator))
    
    def fade_indicator(self, indicator):
        """Fade out the heatmap indicator gradually"""
        try:
            self.game_ui.game_canvas.delete(indicator)
            if indicator in self.heatmap_indicators:
                self.heatmap_indicators.remove(indicator)
        except:
            pass  # Indicator might be already deleted
        
    def highlight_chameleons_red(self):
        # Highlight all unfound chameleons with a red border when clicks are over
        for i, (x1, y1, x2, y2) in enumerate(self.chameleon_positions):
            if not self.found_chameleons[i]:
                # Create a pulsing effect for unfound chameleons
                outline = self.game_ui.game_canvas.create_rectangle(
                    x1-3, y1-3, x2+3, y2+3, outline="red", width=4
                )
                self.game_ui.game_canvas.create_rectangle(
                    x1, y1, x2, y2, outline="yellow", width=1
                )
                
                # Create a label showing "Missed!"
                label_x = (x1 + x2) / 2
                label_y = y1 - 15
                self.game_ui.game_canvas.create_text(
                    label_x, label_y, text="Missed!", fill="red", font=("Arial", 12, "bold")
                )
    
    def highlight_chameleon(self, index):
        # Highlight the found chameleon with a rectangle and animation
        if not self.chameleon_positions or index >= len(self.chameleon_positions):
            return
        x1, y1, x2, y2 = self.chameleon_positions[index]
        
        # Create animated highlight
        self.game_ui.game_canvas.create_rectangle(x1, y1, x2, y2, outline="lime", width=3)
        
        # Add a "Found!" label above the chameleon
        label_x = (x1 + x2) / 2
        label_y = y1 - 15
        self.game_ui.game_canvas.create_text(
            label_x, label_y, text="Found!", fill="lime", font=("Arial", 12, "bold")
        )
        
    def use_add_time(self):
        if self.add_time_uses > 0:
            self.add_time_uses -= 1
            self.game_ui.time_left += 15
            self.game_ui.update_timer_display()
            self.game_ui.update_powerup_buttons()
            self.game_ui.show_message_in_game("+15 seconds added!")
            
    def use_add_steps(self):
        if self.add_steps_uses > 0:
            self.add_steps_uses -= 1
            self.max_clicks += 5
            self.game_ui.update_powerup_buttons()
            self.game_ui.show_message_in_game("+5 clicks added!")
