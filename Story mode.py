import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import random
import numpy as np
import io
import base64

class StoryImages:
    """Class to handle story mode images"""
    def __init__(self):
        self.story_levels = [
            {
                "name": "Jungle Adventure",
                "description": "Find the chameleon hiding in the lush jungle canopy",
                "image_data": self.create_jungle_image(),
                "chameleon_color": (34, 139, 34)  # Forest green
            },
            {
                "name": "Desert Oasis",
                "description": "Spot the chameleon camouflaged in the sandy desert",
                "image_data": self.create_desert_image(),
                "chameleon_color": (210, 180, 140)  # Tan
            },
            {
                "name": "Coral Reef",
                "description": "Discover the chameleon among the colorful coral",
                "image_data": self.create_coral_image(),
                "chameleon_color": (255, 127, 80)  # Coral
            },
            {
                "name": "Autumn Forest",
                "description": "Find the chameleon blending with fall leaves",
                "image_data": self.create_autumn_image(),
                "chameleon_color": (255, 140, 0)  # Dark orange
            },
            {
                "name": "Rocky Mountain",
                "description": "Locate the chameleon on the rocky cliff face",
                "image_data": self.create_mountain_image(),
                "chameleon_color": (105, 105, 105)  # Dim gray
            }
        ]
        self.current_level = 0
    
    def create_jungle_image(self):
        """Create a jungle-themed image"""
        img = Image.new('RGB', (800, 600), (34, 139, 34))  # Forest green base
        draw = ImageDraw.Draw(img)
        
        # Add random jungle elements
        for _ in range(100):
            x, y = random.randint(0, 800), random.randint(0, 600)
            size = random.randint(20, 80)
            color = (random.randint(20, 60), random.randint(100, 180), random.randint(20, 60))
            draw.ellipse([x, y, x+size, y+size], fill=color)
        
        # Add some tree-like patterns
        for _ in range(50):
            x = random.randint(0, 800)
            y1, y2 = random.randint(0, 300), random.randint(300, 600)
            width = random.randint(10, 30)
            color = (random.randint(50, 100), random.randint(80, 120), random.randint(30, 70))
            draw.rectangle([x, y1, x+width, y2], fill=color)
        
        return img
    
    def create_desert_image(self):
        """Create a desert-themed image"""
        img = Image.new('RGB', (800, 600), (238, 203, 173))  # Sandy base
        draw = ImageDraw.Draw(img)
        
        # Add sand dunes and rocks
        for _ in range(80):
            x, y = random.randint(0, 800), random.randint(0, 600)
            size = random.randint(30, 100)
            color = (random.randint(200, 250), random.randint(180, 220), random.randint(140, 190))
            draw.ellipse([x, y, x+size, y+size], fill=color)
        
        # Add rocky formations
        for _ in range(30):
            x, y = random.randint(0, 800), random.randint(0, 600)
            size = random.randint(20, 60)
            color = (random.randint(160, 200), random.randint(140, 180), random.randint(100, 140))
            draw.rectangle([x, y, x+size, y+size], fill=color)
        
        return img
    
    def create_coral_image(self):
        """Create a coral reef-themed image"""
        img = Image.new('RGB', (800, 600), (64, 224, 208))  # Turquoise base
        draw = ImageDraw.Draw(img)
        
        # Add coral formations
        for _ in range(120):
            x, y = random.randint(0, 800), random.randint(0, 600)
            size = random.randint(15, 50)
            colors = [(255, 99, 71), (255, 20, 147), (255, 215, 0), (138, 43, 226)]
            color = random.choice(colors)
            draw.ellipse([x, y, x+size, y+size], fill=color)
        
        # Add sea plants
        for _ in range(60):
            x = random.randint(0, 800)
            y1, y2 = random.randint(400, 500), random.randint(500, 600)
            width = random.randint(5, 15)
            color = (random.randint(0, 100), random.randint(100, 200), random.randint(0, 100))
            draw.rectangle([x, y1, x+width, y2], fill=color)
        
        return img
    
    def create_autumn_image(self):
        """Create an autumn forest-themed image"""
        img = Image.new('RGB', (800, 600), (139, 69, 19))  # Brown base
        draw = ImageDraw.Draw(img)
        
        # Add autumn leaves
        colors = [(255, 140, 0), (255, 69, 0), (255, 215, 0), (178, 34, 34)]
        for _ in range(150):
            x, y = random.randint(0, 800), random.randint(0, 600)
            size = random.randint(10, 40)
            color = random.choice(colors)
            draw.ellipse([x, y, x+size, y+size], fill=color)
        
        # Add tree trunks
        for _ in range(40):
            x = random.randint(0, 800)
            y1, y2 = random.randint(0, 200), random.randint(400, 600)
            width = random.randint(15, 35)
            color = (random.randint(101, 139), random.randint(50, 89), random.randint(20, 40))
            draw.rectangle([x, y1, x+width, y2], fill=color)
        
        return img
    
    def create_mountain_image(self):
        """Create a rocky mountain-themed image"""
        img = Image.new('RGB', (800, 600), (105, 105, 105))  # Gray base
        draw = ImageDraw.Draw(img)
        
        # Add rock formations
        for _ in range(100):
            x, y = random.randint(0, 800), random.randint(0, 600)
            size = random.randint(20, 80)
            color = (random.randint(80, 140), random.randint(80, 140), random.randint(80, 140))
            draw.rectangle([x, y, x+size, y+size], fill=color)
        
        # Add some vegetation
        for _ in range(40):
            x, y = random.randint(0, 800), random.randint(0, 600)
            size = random.randint(10, 30)
            color = (random.randint(50, 100), random.randint(100, 150), random.randint(50, 100))
            draw.ellipse([x, y, x+size, y+size], fill=color)
        
        return img
    
    def get_current_level(self):
        """Get the current story level"""
        return self.story_levels[self.current_level]
    
    def next_level(self):
        """Move to next level"""
        self.current_level = (self.current_level + 1) % len(self.story_levels)
        return self.current_level < len(self.story_levels)
    
    def reset_levels(self):
        """Reset to first level"""
        self.current_level = 0

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
        self.story_mode = False
        
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
            
            if self.story_mode:
                self.ui.show_story_success()
            else:
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
                
                if self.story_mode:
                    self.ui.show_story_failure()
                else:
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

class GameUI:
    def __init__(self, window):
        self.window = window
        self.window.title("Chameleon Hunt")
        self.window.geometry("800x600") 
        self.image_file = None
        self.difficulty = tk.StringVar(value="Medium")
        self.bg_label = None
        self.story_images = StoryImages()
        
        # Timer variables
        self.timer_running = False
        self.time_left = 0
        self.timer_id = None
        
        # Blur variables
        self.original_image = None
        self.blurred_image = None
        self.current_display_image = None
        self.clear_radius = 100  # Radius of clear area
        self.blur_level = 5  # Blur intensity
        self.last_mouse_x = 0
        self.last_mouse_y = 0
       
        # background color 
        self.window.configure(bg="#ADD8E6")
        
        # main frame
        self.frame = tk.Frame(self.window, bg="#ADD8E6")
        self.frame.pack(expand=True, fill="both")
        
        # background image
        try:
            bg_img = Image.open("jungle_bg.jpg")  
            bg_img = bg_img.resize((800, 600), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_img)
            self.bg_label = tk.Label(self.frame, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            self.frame.configure(bg="#ADD8E6")
            
        # Create game logic manager
        self.game_logic = GameLogic(self)
            
        # start screen
        self.make_start_screen()
        
        # Initialize game canvas and feedback label
        self.game_canvas = None
        self.feedback = None
        self.create_game_elements()

    def create_game_elements(self):
        # Create game canvas if it doesn't exist
        if not hasattr(self, 'game_canvas') or not self.game_canvas or not self.game_canvas.winfo_exists():
            self.game_canvas = tk.Canvas(self.frame, bg="white", highlightthickness=2, highlightbackground="#00CED1")
            self.game_canvas.pack(fill="both", expand=True)
        
        # Create feedback label if it doesn't exist
        if not hasattr(self, 'feedback') or not self.feedback or not self.feedback.winfo_exists():
            self.feedback = tk.Label(self.frame, text="", font=("Arial", 16), bg="#ADD8E6", fg="#FF0000")
            self.feedback.pack(pady=15)

    def make_start_screen(self):
        # Clear the frame
        for widget in self.frame.winfo_children():
            if widget != getattr(self, "bg_label", None):
                try:
                    widget.destroy()
                except tk.TclError:
                    pass  # Widget already destroyed
                
        # Title frame 
        title_frame = tk.Frame(self.frame, bg="#ADD8E6")
        title_frame.pack(pady=30)
        
        # Title
        title = tk.Label(title_frame, text="Chameleon Hunt", font=("Arial", 36, "bold"), fg="#800080", bg="#ADD8E6")
        title.pack()
        
        # Welcome message
        welcome = tk.Label(title_frame, text="Can you find the sneaky chameleon?", font=("Arial", 14, "italic"), fg="#008000", bg="#ADD8E6")
        welcome.pack(pady=5)
        
        # Placeholder
        chameleon_icon = tk.Label(title_frame, text="🦎", font=("Arial", 30), fg="#008000", bg="#ADD8E6")
        chameleon_icon.pack(pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(self.frame, bg="#ADD8E6")
        buttons_frame.pack(pady=15)
        
        # Story Mode button
        story_btn = tk.Button(
            buttons_frame, 
            text="Story Mode", 
            command=self.start_story_mode,
            bg="#FF69B4",  # Hot pink
            fg="white", 
            font=("Arial", 18, "bold"),
            relief="raised"
        )
        story_btn.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=10)
        
        story_btn.bind("<Enter>", lambda e: self.animate_button(story_btn, "#FF1493"))
        story_btn.bind("<Leave>", lambda e: self.animate_button(story_btn, "#FF69B4", shrink=True))
        
        # Upload button
        upload_btn = tk.Button(
            buttons_frame, 
            text="Upload Image", 
            command=self.upload_pic,
            bg="#FFFF00",  
            fg="black", 
            font=("Arial", 18, "bold"),
            relief="raised"
        )
        upload_btn.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=10)
        
        upload_btn.bind("<Enter>", lambda e: self.animate_button(upload_btn, "#FFD700"))
        upload_btn.bind("<Leave>", lambda e: self.animate_button(upload_btn, "#FFFF00", shrink=True))
        
        # Difficulty label
        diff_label = tk.Label(self.frame, text="Pick Difficulty:", font=("Arial", 16, "bold"), bg="#ADD8E6", fg="#800080")
        diff_label.pack(pady=10)
        
        # Difficulty options
        diffs = ["Easy", "Medium", "Hard"]
        diff_colors = {"Easy": "#DDA0DD", "Medium": "#BA55D3", "Hard": "#9932CC"}
        for d in diffs:
            rb = tk.Radiobutton(
                self.frame, 
                text=d, 
                value=d, 
                variable=self.difficulty, 
                font=("Arial", 14), 
                bg="#ADD8E6", 
                fg=diff_colors[d], 
                selectcolor="#ADD8E6"
            )
            rb.pack()
            
        # Start button
        start_btn = tk.Button(
            self.frame, 
            text="Start Game", 
            command=self.start_game, 
            bg="#32CD32", 
            fg="white", 
            font=("Arial", 18, "bold"),
            relief="raised"
        )
        start_btn.pack(pady=20, ipadx=30, ipady=15)
        
        # Create feedback label
        self.feedback = tk.Label(self.frame, text="", font=("Arial", 16), bg="#ADD8E6", fg="#FF0000")
        self.feedback.pack(pady=15)

    def start_story_mode(self):
        """Start the story mode"""
        self.story_images.reset_levels()
        self.show_story_level_intro()

    def show_story_level_intro(self):
        """Show introduction for current story level"""
        level = self.story_images.get_current_level()
        
        # Clear the frame
        for widget in self.frame.winfo_children():
            if widget != getattr(self, "bg_label", None):
                try:
                    widget.destroy()
                except tk.TclError:
                    pass
        
        # Create intro frame
        intro_frame = tk.Frame(self.frame, bg="#ADD8E6", relief="raised", bd=3)
        intro_frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        # Level title
        title = tk.Label(intro_frame, text=f"Level {self.story_images.current_level + 1}: {level['name']}", 
                        font=("Arial", 24, "bold"), fg="#800080", bg="#ADD8E6")
        title.pack(pady=20)
        
        # Level description
        desc = tk.Label(intro_frame, text=level['description'], 
                       font=("Arial", 16, "italic"), fg="#008000", bg="#ADD8E6")
        desc.pack(pady=10)
        
        # Difficulty display
        diff_text = f"Difficulty: {self.difficulty.get()}"
        diff_label = tk.Label(intro_frame, text=diff_text, 
                             font=("Arial", 14, "bold"), fg="#FF6347", bg="#ADD8E6")
        diff_label.pack(pady=10)
        
        # Start level button
        start_btn = tk.Button(intro_frame, text="Start Level", 
                             command=self.start_story_level,
                             bg="#32CD32", fg="white", 
                             font=("Arial", 18, "bold"), relief="raised")
        start_btn.pack(pady=20, ipadx=30, ipady=15)
        
        # Back to menu button
        back_btn = tk.Button(intro_frame, text="Back to Menu", 
                            command=self.make_start_screen,
                            bg="#FF6347", fg="white", 
                            font=("Arial", 14, "bold"), relief="raised")
        back_btn.pack(pady=10, ipadx=20, ipady=10)

    def start_story_level(self):
        """Start the current story level"""
        level = self.story_images.get_current_level()
        
        # Set story mode flag
        self.game_logic.story_mode = True
        
        # Use the story image
        self.original_image = level['image_data'].copy()
        
        # Add a chameleon to the image
        self.add_chameleon_to_image(level['chameleon_color'])
        
        # Start the game with this image
        self.start_game_with_image()

    def add_chameleon_to_image(self, chameleon_color):
        """Add a camouflaged chameleon to the image"""
        if not self.original_image:
            return
            
        draw = ImageDraw.Draw(self.original_image)
        
        # Generate random position for chameleon
        margin = 60
        width, height = self.original_image.size
        chameleon_x = random.randint(margin, width - margin)
        chameleon_y = random.randint(margin, height - margin)
        
        # Store chameleon position
        self.game_logic.chameleon_x = chameleon_x
        self.game_logic.chameleon_y = chameleon_y
        
        # Draw a subtle chameleon shape (making it blend in)
        size = 25
        
        # Body (oval)
        body_color = tuple(max(0, min(255, c + random.randint(-30, 30))) for c in chameleon_color)
        draw.ellipse([chameleon_x - size//2, chameleon_y - size//3, 
                     chameleon_x + size//2, chameleon_y + size//3], fill=body_color)
        
        # Head (smaller circle)
        head_size = size // 2
        head_color = tuple(max(0, min(255, c + random.randint(-20, 20))) for c in chameleon_color)
        draw.ellipse([chameleon_x - head_size//2, chameleon_y - size//2 - head_size//2,
                     chameleon_x + head_size//2, chameleon_y - size//2 + head_size//2], fill=head_color)
        
        # Tail (curved line)
        tail_color = tuple(max(0, min(255, c + random.randint(-15, 15))) for c in chameleon_color)
        draw.arc([chameleon_x + size//2, chameleon_y - size//4,
                 chameleon_x + size, chameleon_y + size//4], 
                start=0, end=180, fill=tail_color, width=3)

    def start_game_with_image(self):
        """Start game with the loaded image"""
        # Clear the frame
        for widget in self.frame.winfo_children():
            if widget != getattr(self, "bg_label", None):
                try:
                    widget.destroy()
                except tk.TclError:
                    pass
        
        # Create new canvas and feedback label
        self.game_canvas = tk.Canvas(self.frame, bg="white", highlightthickness=2, highlightbackground="#00CED1")
        self.game_canvas.pack(fill="both", expand=True)
        
        # Add timer frame at the top
        self.timer_frame = tk.Frame(self.frame, bg="#ADD8E6")
        self.timer_frame.pack(before=self.game_canvas, pady=5)
        
        # Add timer display
        self.timer_display = tk.Label(self.timer_frame, text="Time: 0:00", font=("Arial", 18, "bold"), bg="#ADD8E6", fg="#FF5733")
        self.timer_display.pack(padx=10)
        
        # Set difficulty-specific blur settings
        self.set_blur_difficulty()
        
        # Set time based on difficulty and start the timer automatically
        self.set_timer_difficulty()
        self.start_timer()
        
        self.feedback = tk.Label(self.frame, text="", font=("Arial", 16), bg="#ADD8E6", fg="#FF0000")
        self.feedback.pack(pady=15)
        
        # Process the image
        try:
            # Resize image if needed
            self.original_image.thumbnail((800, 600))
            
            # Create blurred version
            self.blurred_image = self.original_image.filter(ImageFilter.GaussianBlur(self.blur_level))
            
            # Set initial display as blurred
            self.current_display_image = self.blurred_image.copy()
            self.game_image = ImageTk.PhotoImage(self.current_display_image)
            self.image_on_canvas = self.game_canvas.create_image(0, 0, image=self.game_image, anchor="nw")
            
            # Process the image in game logic
            self.game_logic.img_width, self.game_logic.img_height = self.original_image.size
            
            # Reset game state for new round (but don't reset chameleon position for story mode)
            if not self.game_logic.story_mode:
                self.game_logic.reset_game()
            else:
                # Just reset game flags but keep chameleon position
                self.game_logic.found = False
                self.game_logic.attempts = 0
                if self.game_logic.circle_id:
                    try:
                        self.game_canvas.delete(self.game_logic.circle_id)
                    except:
                        pass
                self.game_logic.circle_id = None
                
                # Set difficulty parameters
                difficulty = self.difficulty.get()
                if difficulty == "Easy":
                    self.game_logic.click_radius = 50
                    self.game_logic.max_attempts = 8
                elif difficulty == "Medium":
                    self.game_logic.click_radius = 30
                    self.game_logic.max_attempts = 5
                else:  # Hard
                    self.game_logic.click_radius = 15
                    self.game_logic.max_attempts = 3
            
            # Feedback
            if self.game_logic.story_mode:
                level = self.story_images.get_current_level()
                self.feedback.config(text=f"Find the chameleon in {level['name']}! Move mouse to reveal.", fg="#800080")
            else:
                self.feedback.config(text="Move your mouse to reveal parts of the image! Click to guess the chameleon location!", fg="#800080")
            
            # Mouse event handlers
            self.game_canvas.bind("<Motion>", self.update_blur)
            self.game_canvas.bind("<Button-1>", self.game_logic.handle_click)

        except Exception as e:
            messagebox.showerror("Error", f"Image didn't load: {e}")
            self.make_start_screen()

    def show_story_success(self):
        """Handle story mode success"""
        level = self.story_images.get_current_level()
        self.show_message(f"Found the chameleon in {level['name']}! Excellent!", True)
        
        # Show next level button after a delay
        self.window.after(2000, self.show_story_completion)

    def show_story_failure(self):
        """Handle story mode failure"""
        level = self.story_images.get_current_level()
        self.show_message(f"The chameleon was hiding in {level['name']}! Try again!", False)
        
        # Show retry button after a delay
        self.window.after(2000, self.show_story_retry)

    def show_story_completion(self):
        """Show story completion options"""
        # Add buttons to the frame
        button_frame = tk.Frame(self.frame, bg="#ADD8E6")
        button_frame.pack(pady=10)
        
        if self.story_images.current_level < len(self.story_images.story_levels) - 1:
            next_btn = tk.Button(button_frame, text="Next Level", 
                               command=self.next_story_level,
                               bg="#32CD32", fg="white", 
                               font=("Arial", 14, "bold"))
            next_btn.pack(side=tk.LEFT, padx=10)
        else:
            # Completed all levels
            complete_btn = tk.Button(button_frame, text="Story Complete!", 
                                   command=self.show_story_complete,
                                   bg="#FFD700", fg="black", 
                                   font=("Arial", 14, "bold"))
            complete_btn.pack(side=tk.LEFT, padx=10)
        
        retry_btn = tk.Button(button_frame, text="Retry Level", 
                             command=self.retry_story_level,
                             bg="#FF6347", fg="white", 
                             font=("Arial", 14, "bold"))
        retry_btn.pack(side=tk.LEFT, padx=10)
        
        menu_btn = tk.Button(button_frame, text="Main Menu", 
                            command=self.return_to_menu,
                            bg="#9370DB", fg="white", 
                            font=("Arial", 14, "bold"))
        menu_btn.pack(side=tk.LEFT, padx=10)

    def show_story_retry(self):
        """Show retry options for story mode"""
        button_frame = tk.Frame(self.frame, bg="#ADD8E6")
        button_frame.pack(pady=10)
        
        retry_btn = tk.Button(button_frame, text="Try Again", 
                             command=self.retry_story_level,
                             bg="#FF6347", fg="white", 
                             font=("Arial", 14, "bold"))
        retry_btn.pack(side=tk.LEFT, padx=10)
        
        menu_btn = tk.Button(button_frame, text="Main Menu", 
                            command=self.return_to_menu,
                            bg="#9370DB", fg="white", 
                            font=("Arial", 14, "bold"))
        menu_btn.pack(side=tk.LEFT, padx=10)

    def next_story_level(self):
        """Move to next story level"""
        self.story_images.next_level()
        self.show_story_level_intro()

    def retry_story_level(self):
        """Retry current story level"""
        self.start_story_level()

    def show_story_complete(self):
        """Show story completion screen"""
        # Clear the frame
        for widget in self.frame.winfo_children():
            if widget != getattr(self, "bg_label", None):
                try:
                    widget.destroy()
                except tk.TclError:
                    pass
        
        # Create completion frame
        complete_frame = tk.Frame(self.frame, bg="#ADD8E6", relief="raised", bd=3)
        complete_frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        # Congratulations title
        title = tk.Label(complete_frame, text="🎉 STORY COMPLETE! 🎉", 
                        font=("Arial", 28, "bold"), fg="#FF1493", bg="#ADD8E6")
        title.pack(pady=30)
        
        # Achievement message
        msg = tk.Label(complete_frame, text="You've mastered all environments!\nYou're a true Chameleon Hunter!", 
                      font=("Arial", 18), fg="#008000", bg="#ADD8E6", justify=tk.CENTER)
        msg.pack(pady=20)
        
        # Stats (you could expand this with actual tracking)
        stats = tk.Label(complete_frame, text=f"Completed {len(self.story_images.story_levels)} levels\nDifficulty: {self.difficulty.get()}", 
                        font=("Arial", 14), fg="#800080", bg="#ADD8E6", justify=tk.CENTER)
        stats.pack(pady=15)
        
        # Buttons
        button_frame = tk.Frame(complete_frame, bg="#ADD8E6")
        button_frame.pack(pady=20)
        
        replay_btn = tk.Button(button_frame, text="Play Again", 
                              command=self.start_story_mode,
                              bg="#32CD32", fg="white", 
                              font=("Arial", 16, "bold"))
        replay_btn.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=10)
        
        menu_btn = tk.Button(button_frame, text="Main Menu", 
                            command=self.return_to_menu,
                            bg="#9370DB", fg="white", 
                            font=("Arial", 16, "bold"))
        menu_btn.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=10)

    def return_to_menu(self):
        """Return to main menu and reset story mode"""
        self.game_logic.story_mode = False
        self.story_images.reset_levels()
        self.make_start_screen()

    def animate_button(self, button, color, shrink=False):
        """Animate button hover effect"""
        if shrink:
            button.config(bg=button.cget('bg'), font=("Arial", 18, "bold"))
        else:
            button.config(bg=color, font=("Arial", 18, "bold"))

    def upload_pic(self):
        file = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file:
            self.image_file = file
            if hasattr(self, 'feedback') and self.feedback and self.feedback.winfo_exists():
                self.feedback.config(text="Image loaded! Ready to hunt!", fg="#008000")
        else:
            if hasattr(self, 'feedback') and self.feedback and self.feedback.winfo_exists():
                self.feedback.config(text="No image picked.", fg="#FF0000")

    def start_game(self):
        if not self.image_file:
            messagebox.showerror("Error", "Upload an image first!")
            return
        
        # Reset story mode flag for custom image games
        self.game_logic.story_mode = False
            
        # Clear the frame
        for widget in self.frame.winfo_children():
            if widget != getattr(self, "bg_label", None):
                try:
                    widget.destroy()
                except tk.TclError:
                    pass  # Widget already destroyed
        
        # Create new canvas and feedback label
        self.game_canvas = tk.Canvas(self.frame, bg="white", highlightthickness=2, highlightbackground="#00CED1")
        self.game_canvas.pack(fill="both", expand=True)
        
        # Add timer frame at the top
        self.timer_frame = tk.Frame(self.frame, bg="#ADD8E6")
        self.timer_frame.pack(before=self.game_canvas, pady=5)
        
        # Add timer display
        self.timer_display = tk.Label(self.timer_frame, text="Time: 0:00", font=("Arial", 18, "bold"), bg="#ADD8E6", fg="#FF5733")
        self.timer_display.pack(padx=10)
        
        # Set difficulty-specific blur settings
        self.set_blur_difficulty()
        
        # Set time based on difficulty and start the timer automatically
        self.set_timer_difficulty()
        self.start_timer()
        
        self.feedback = tk.Label(self.frame, text="", font=("Arial", 16), bg="#ADD8E6", fg="#FF0000")
        self.feedback.pack(pady=15)
        
        # Load the image
        try:
            # Load original image
            self.original_image = Image.open(self.image_file)
            self.original_image.thumbnail((800, 600))
            
            # Create blurred version
            self.blurred_image = self.original_image.filter(ImageFilter.GaussianBlur(self.blur_level))
            
            # Set initial display as blurred
            self.current_display_image = self.blurred_image.copy()
            self.game_image = ImageTk.PhotoImage(self.current_display_image)
            self.image_on_canvas = self.game_canvas.create_image(0, 0, image=self.game_image, anchor="nw")
            
            # Process the image in game logic
            self.game_logic.img_width, self.game_logic.img_height = self.original_image.size
            
            # Reset game state for new round
            self.game_logic.reset_game()
            
            # Feedback
            self.feedback.config(text="Move your mouse to reveal parts of the image! Click to guess the chameleon location!", fg="#800080")
            
            # Mouse event handlers
            self.game_canvas.bind("<Motion>", self.update_blur)
            self.game_canvas.bind("<Button-1>", self.game_logic.handle_click)

        except Exception as e:
            messagebox.showerror("Error", f"Image didn't load: {e}")
            self.make_start_screen()
    
    def set_blur_difficulty(self):
        """Set blur parameters based on difficulty level"""
        difficulty_value = self.difficulty.get()
        if difficulty_value == "Easy":
            self.blur_level = 5
            self.initial_clear_radius = 100  # Start smaller
            self.max_clear_radius = 200     # End larger
        elif difficulty_value == "Medium":
            self.blur_level = 8
            self.initial_clear_radius = 75  # Start smaller
            self.max_clear_radius = 150     # End larger
        else:  # Hard
            self.blur_level = 12
            self.initial_clear_radius = 50  # Start smaller
            self.max_clear_radius = 100     # End larger
        
        # Set current radius to initial value
        self.clear_radius = self.initial_clear_radius
    
    def update_blur(self, event):
        """Update the dynamic blur based on mouse position"""
        if self.game_logic.found:
            return
            
        # Get mouse position
        x, y = event.x, event.y
        self.last_mouse_x, self.last_mouse_y = x, y
        
        # Update the image with a clear circular area around the cursor
        self.apply_dynamic_blur(x, y)
    
    def apply_dynamic_blur(self, x, y):
        """Apply dynamic blurring with a clear area around cursor position"""
        if self.original_image is None or self.blurred_image is None:
            return
            
        try:
            # Create a copy of the blurred image
            self.current_display_image = self.blurred_image.copy()
            
            # Create a blank mask the same size as our image
            mask = Image.new('L', self.original_image.size, 0)
            
            # Draw a white circle at the cursor position
            from PIL import ImageDraw
            draw = ImageDraw.Draw(mask)
            draw.ellipse((x - self.clear_radius, y - self.clear_radius, 
                          x + self.clear_radius, y + self.clear_radius), fill=255)
            
            # Paste the original image onto the blurred one using the mask
            self.current_display_image.paste(self.original_image, (0, 0), mask)
            
            # Update the displayed image
            self.game_image = ImageTk.PhotoImage(self.current_display_image)
            self.game_canvas.itemconfig(self.image_on_canvas, image=self.game_image)
            
        except Exception as e:
            print(f"Error applying dynamic blur: {e}")
    
    def set_timer_difficulty(self):
        """Set timer duration based on difficulty"""
        difficulty_value = self.difficulty.get()
        if difficulty_value == "Easy":
            self.time_left = 90  # 1:30
            self.initial_time = 90
        elif difficulty_value == "Medium":
            self.time_left = 60  # 1:00
            self.initial_time = 60
        else:  # Hard
            self.time_left = 30  # 0:30
            self.initial_time = 30
        
        self.update_timer_display()
    
    def update_timer_display(self):
        """Update the timer display"""
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        time_string = f"Time: {minutes}:{seconds:02d}"
        
        # Change color based on time left
        if self.time_left > 20:
            color = "#32CD32"  # Green
        elif self.time_left > 10:
            color = "#FFA500"  # Orange
        else:
            color = "#FF0000"  # Red
        
        self.timer_display.config(text=time_string, fg=color)
        
        # Update clear radius based on time remaining
        self.update_clear_radius()
    
    def update_clear_radius(self):
        """Update the clear radius based on time remaining - radius INCREASES as time decreases"""
        if hasattr(self, 'initial_time') and hasattr(self, 'initial_clear_radius'):
            # Calculate progress: 0 = start, 1 = end
            time_progress = 1 - (self.time_left / self.initial_time)
            
            # Calculate new radius: starts at initial_clear_radius, INCREASES to max_clear_radius
            radius_range = self.max_clear_radius - self.initial_clear_radius
            self.clear_radius = self.initial_clear_radius + (radius_range * time_progress)
            
            # Ensure we don't go above maximum
            self.clear_radius = min(self.clear_radius, self.max_clear_radius)
            
            # Update the current blur display if mouse is on canvas
            if hasattr(self, 'last_mouse_x') and hasattr(self, 'last_mouse_y'):
                self.apply_dynamic_blur(self.last_mouse_x, self.last_mouse_y)
    
    def start_timer(self):
        """Start the timer automatically when game starts"""
        self.timer_running = True
        self.tick_timer()
    
    def stop_timer(self):
        """Stop the timer"""
        self.timer_running = False
        if self.timer_id:
            self.window.after_cancel(self.timer_id)
            self.timer_id = None
    
    def tick_timer(self):
        """Update timer each second"""
        if self.timer_running and self.time_left > 0:
            self.time_left -= 1
            self.update_timer_display()
            self.timer_id = self.window.after(1000, self.tick_timer)
        elif self.timer_running and self.time_left <= 0:
            self.timer_running = False
            self.timer_display.config(text="Time's Up!", fg="#FF0000")
            
            # End the game by showing the chameleon position
            if not self.game_logic.found:
                # Show unblurred image first when game ends
                if self.original_image:
                    self.game_image = ImageTk.PhotoImage(self.original_image)
                    self.game_canvas.itemconfig(self.image_on_canvas, image=self.game_image)
                
                # Then draw the chameleon circle
                self.game_logic.circle_id = self.game_canvas.create_oval(
                    self.game_logic.chameleon_x - self.game_logic.click_radius, 
                    self.game_logic.chameleon_y - self.game_logic.click_radius,
                    self.game_logic.chameleon_x + self.game_logic.click_radius, 
                    self.game_logic.chameleon_y + self.game_logic.click_radius,
                    outline="red", width=3
                )
                
                if self.game_logic.story_mode:
                    self.show_story_failure()
                else:
                    self.show_message("Time's up! The chameleon was here!", False)
                
                # Set found to true to prevent further clicks
                self.game_logic.found = True
                
            messagebox.showinfo("Time's Up!", "Time's up! Game over.")

    def show_message(self, msg, success):
        if hasattr(self, 'feedback') and self.feedback and self.feedback.winfo_exists():
            if success:
                self.feedback.config(text=msg, fg="#008000")
            else:
                self.feedback.config(text=msg, fg="#FF0000")

# Run the game
if __name__ == "__main__":
    window = tk.Tk()
    game = GameUI(window)
    window.mainloop()
    