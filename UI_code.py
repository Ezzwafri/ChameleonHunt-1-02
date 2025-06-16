import pygame
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw
from game_functions import GameLogic
from StoryImages_Class import StoryImages
pygame.mixer.init()

class GameUI:
    def __init__(self, window):
        self.sound_on = True 
        self.success_sound = pygame.mixer.Sound("sounds/success.wav")
        self.click_sound = pygame.mixer.Sound("sounds/click.wav")
        self.win_sound = pygame.mixer.Sound("sounds/win.wav")
        self.gameover_sound = pygame.mixer.Sound("sounds/gameover.wav")
        self.window = window
        self.window.title("Chameleon Hunt")
        self.window.geometry("900x765") 
        self.window.resizable(True, True)  
        self.window.minsize(800, 600)
        self.image_file = None
        self.difficulty = tk.StringVar(value="Medium")
        self.bg_label = None
        self.story_images = StoryImages()
        self.current_button_frame = None
        self.current_story_difficulty = "Easy"
        self.points = 0
        self.shop_visible = False
        
        # Timer variables
        self.timer_running = False
        self.time_left = 0
        self.timer_id = None
        self.paused = False
        
        # Blur variables
        self.original_image = None
        self.blurred_image = None
        self.current_display_image = None
        self.clear_radius = 100  # Radius of clear area
        self.blur_level = 5  # Blur intensity
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        
        # Image scaling constants
        self.LANDSCAPE_SIZE = (700, 500)  # For landscape images (width > height)
        self.PORTRAIT_SIZE = (400, 550)   # For portrait images (height > width)
        self.SQUARE_SIZE = (500, 500)     # For square images (width ≈ height)
       
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
        
        # Start with the main menu
        self.make_start_screen()

    def get_standardized_size(self, image):
        """Determine the standardized size based on image orientation"""
        width, height = image.size
        aspect_ratio = width / height
        
        if aspect_ratio > 1.2:  # Landscape (width significantly larger than height)
            return self.LANDSCAPE_SIZE
        elif aspect_ratio < 0.8:  # Portrait (height significantly larger than width)
            return self.PORTRAIT_SIZE
        else:  # Square or near-square
            return self.SQUARE_SIZE

    def resize_image_proportionally(self, image, target_size):
        """Resize image to fit within target size while maintaining aspect ratio"""
        target_width, target_height = target_size
        original_width, original_height = image.size
        
        # Calculate the scaling factor to fit within the target size
        scale_width = target_width / original_width
        scale_height = target_height / original_height
        scale_factor = min(scale_width, scale_height)
        
        # Calculate new dimensions
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        
        return image.resize((new_width, new_height), Image.LANCZOS)

    def make_start_screen(self):
        # Clear the frame
        for widget in self.frame.winfo_children():
            if widget != getattr(self, "bg_label", None):
                try:
                    widget.destroy()
                except tk.TclError:
                    continue
                
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
        story_btn.bind("<Leave>", lambda e: self.animate_button(story_btn, "#FF69B4"))
        
        # Upload button
        upload_btn = tk.Button(
            self.frame, 
            text="Upload Image", 
            command=self.upload_pic,
            bg="#FFFF00",  
            fg="black", 
            font=("Arial", 18, "bold"),
            relief="raised"
        )
        upload_btn.pack(pady=15, ipadx=30, ipady=15)  
        
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
            bg="#FFFF00", 
            fg="black", 
            font=("Arial", 18, "bold"),
            relief="raised"
        )
        start_btn.pack(pady=20, ipadx=30, ipady=15)
        
        start_btn.bind("<Enter>", lambda e: self.animate_button(start_btn, "#FFD700"))
        start_btn.bind("<Leave>", lambda e: self.animate_button(start_btn, "#FFFF00", shrink=True))
        
        # Create feedback label
        self.feedback = tk.Label(self.frame, text="", font=("Arial", 16), bg="#ADD8E6", fg="#FF0000")
        self.feedback.pack(pady=15)
        
        # Sound toggle button (top-right corner)
        self.sound_btn = tk.Button(
        self.frame,
        text="🔊 Sound On",  # Initial label
        command=self.toggle_sound,
        bg="#32CD32",        # Green = sound on
        fg="white",
        font=("Arial", 14, "bold"),
        relief="raised",
        bd=3,
        padx=10,
        pady=5
         )
        self.sound_btn.place(relx=0.99, rely=0.02, anchor="ne")  # Top-right corner
        
    def toggle_shop_menu(self):
         """Toggle the visibility of the shop menu"""
         if self.shop_visible:
             if hasattr(self, 'shop_frame'):
                 self.shop_frame.destroy()
             self.shop_visible = False
         else:
             self.shop_visible = True
             self.shop_frame = tk.Frame(self.frame, bg="#ADD8E6", width=200)
             # Use place() for precise control
             self.shop_frame.place(x=0, y=0, relheight=1, width=200)
             self.shop_frame.lift()  # Bring to front
             tk.Label(self.shop_frame, text="Shop", font=("Arial", 14, "bold"), bg="#ADD8E6").pack(pady=5)
             tk.Label(self.shop_frame, text=f"Points: {self.points}", font=("Arial", 12), bg="#ADD8E6").pack(pady=5)
        
             if self.points >= 20:
                 buy_time_btn = tk.Button(self.shop_frame, text="Buy Add Time (20 pts)", 
                                         command=lambda: self.buy_powerup("time"), 
                                         bg="#32CD32", fg="black", font=("Arial", 10, "bold"))
                 buy_time_btn.pack(pady=5)
             else:
                  tk.Label(self.shop_frame, text="Add Time (20 pts)\nInsufficient Points", 
                        fg="red", bg="#ADD8E6").pack(pady=5)
            
             if self.points >= 15:
                 buy_steps_btn = tk.Button(self.shop_frame, text="Buy Add Steps (15 pts)", 
                                    command=lambda: self.buy_powerup("steps"), 
                                    bg="#FF69B4", fg="black", font=("Arial", 10, "bold"))
                 buy_steps_btn.pack(pady=5)
             else:
                 tk.Label(self.shop_frame, text="Add Steps (15 pts)\nInsufficient Points", 
                        fg="red", bg="#ADD8E6").pack(pady=5)
            
             tk.Button(self.shop_frame, text="Close", command=self.toggle_shop_menu, 
                     bg="#FFA500", fg="black", font=("Arial", 10)).pack(pady=5)
        
    def buy_powerup(self, powerup_type):
        """Handle powerup purchases"""
        if powerup_type == "time" and self.points >= 20:
             self.points -= 20
             self.game_logic.add_time_uses += 1
             self.show_message("Purchased Add Time!", True)
        elif powerup_type == "steps" and self.points >= 15:
            self.points -= 15
            self.game_logic.add_steps_uses += 1
            self.show_message("Purchased Add Steps!", True)
        else:
           self.show_message("Not enough points!", False)
           return
    
        self.update_points_display()
        self.update_powerup_buttons()
        self.toggle_shop_menu()

    def update_points_display(self):
        """Update the points display label"""
        if hasattr(self, 'points_display'):
           self.points_display.config(text=f"Points: {self.points}")
    
    
    def safe_update_widget(self, widget, **kwargs):
         """Safely update widget properties if the widget exists"""
         if widget and widget.winfo_exists():
           try:
              widget.config(**kwargs)
           except tk.TclError:
                pass
    
    def start_story_mode(self):
        """Start the story mode"""
        self.show_story_intro()
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

        # Difficulty display - show the level's difficulty, not the general setting
        diff_text = f"Difficulty: {level['difficulty']}"
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
        
        # Clean up any existing widgets first
        self.clean_up_game_widgets()
        
        
        level = self.story_images.get_current_level()
        
        # Ensure clean state
        self.game_logic = GameLogic(self)
        self.game_logic.story_mode = True
        self.current_story_difficulty = level['difficulty']
        self.image_file = level['image_data']
        self.points = 0  # Ensure points are zero in story mode

        # Set story mode flag and difficulty
        if hasattr(self, 'game_logic'):
           self.game_logic.story_mode = True
        self.current_story_difficulty = level['difficulty']
        self.image_file = level['image_data']  # Set the image file path

        try:
           # Try to open the story image file
           self.original_image = Image.open(level['image_data'])
           print(f"Successfully loaded {level['image_data']}")
        
           # Create or reset game logic with the new image
           if not hasattr(self, 'game_logic') or self.game_logic is None:
               self.game_logic = GameLogic(self)
        
           # Ensure the game logic has access to the loaded image
           self.game_logic.story_mode = True
        
           # Start the game with this image
           self.start_game_with_image()
    
        except Exception as e:
           print(f"Error loading image: {e}")
           # Create a placeholder image if loading fails
           placeholder_color = level['placeholder_color']
           self.original_image = Image.new('RGB', (800, 600), placeholder_color)
           draw = ImageDraw.Draw(self.original_image)
           draw.text((400, 300), f"Could not load {level['image_data']}", fill="white", anchor="mm")
    
           # Create or reset game logic with placeholder image
           if not hasattr(self, 'game_logic') or self.game_logic is None:
              self.game_logic = GameLogic(self)
        
           self.game_logic.story_mode = True
           self.start_game_with_image()

    def start_game_with_image(self):
        """Start game with the loaded image"""
        # Clear the frame
        for widget in self.frame.winfo_children():
            if widget != getattr(self, "bg_label", None):
                try:
                    widget.destroy()
                except tk.TclError:
                    continue
        # Wait a moment to ensure all widgets are destroyed
        self.window.update_idletasks()
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
        self.initial_clear_radius = self.clear_radius

        # Set time based on difficulty and start the timer automatically
        self.set_timer_difficulty()
        self.start_timer()

        self.feedback = tk.Label(self.frame, text="", font=("Arial", 16), bg="#ADD8E6", fg="#FF0000")
        self.feedback.pack(pady=15)

        # Process the image
        try:
            # Ensure we have an original image
            if not hasattr(self, 'original_image') or self.original_image is None:
                raise ValueError("No original image loaded")
        
            # Resize image if needed
            self.original_image.thumbnail((800, 600))

            # Process the image in game logic FIRST - this sets up chameleons
            self.game_logic.img_width, self.game_logic.img_height = self.original_image.size
        
            # Reset game state for new round - this will place chameleons
            success = self.game_logic.reset_game()
            if not success:
                raise ValueError("Failed to reset game")

            # Create blurred version - use the image WITH chameleons for story mode
            if self.game_logic.story_mode:
                # For story mode, blur the image WITH chameleons
                self.blurred_image = self.game_logic.game_image_with_chameleons.filter(ImageFilter.GaussianBlur(self.blur_level))
            else:
                # For normal mode, keep original behavior (blur without chameleons)
                self.blurred_image = self.original_image.filter(ImageFilter.GaussianBlur(self.blur_level))

            # Set initial display as blurred
            self.current_display_image = self.blurred_image.copy()
            self.game_image = ImageTk.PhotoImage(self.current_display_image)
            self.image_on_canvas = self.game_canvas.create_image(0, 0, image=self.game_image, anchor="nw")

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
          print(f"Error in start_game_with_image: {e}")
          messagebox.showerror("Error", f"Image didn't load: {e}")
          self.make_start_screen()

        

    def animate_button(self, button, color, shrink=False):
        """Animate button hover effect"""
        if shrink:
            button.config(bg="#FFFF00", font=("Arial", 18, "bold"))
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
        
        # Clean up any existing widgets first
        self.clean_up_game_widgets()
    
        if not self.image_file:
          messagebox.showerror("Error", "Upload an image first!")
          return
        
    # Clear the frame
        for widget in self.frame.winfo_children():
          if widget != getattr(self, "bg_label", None):
            try:
                widget.destroy()
            except tk.TclError:
                pass  # Widget already destroyed
    
    # Reset pause state
        self.paused = False
    
    # Create new canvas
        self.game_canvas = tk.Canvas(self.frame, bg="white", highlightthickness=2, highlightbackground="#00CED1")
        self.game_canvas.pack(fill="both", expand=True)
    
    # Create control frames
        self.timer_frame = tk.Frame(self.frame, bg="#ADD8E6")
        self.timer_frame.pack(before=self.game_canvas, pady=5)
    
        self.powerup_frame = tk.Frame(self.frame, bg="#ADD8E6")
        self.powerup_frame.pack(before=self.game_canvas, pady=5)
    
        self.button_frame = tk.Frame(self.frame, bg="#ADD8E6")
        self.button_frame.pack(before=self.game_canvas, pady=5)
    
    # Add timer display
        self.timer_display = tk.Label(self.timer_frame, text="Time: 0:00", font=("Arial", 18, "bold"), bg="#ADD8E6", fg="#FF5733")
        self.timer_display.pack(padx=10)
        
        # Only add points and shop for normal mode
        if not self.game_logic.story_mode:
            self.points_display = tk.Label(self.timer_frame, text=f"Points: {self.points}", 
                                  font=("Arial", 14), bg="#ADD8E6", fg="#0000FF")
            self.points_display.pack(padx=10)
        
            shop_btn = tk.Button(self.frame, text="$", command=self.toggle_shop_menu, 
                        bg="#FFD700", fg="black", font=("Arial", 24, "bold"), 
                        relief="raised", width=2, height=1)
            shop_btn.place(x=750, y=10)
    
    # Set difficulty-specific blur settings
        self.set_blur_difficulty()
    
    # Set time based on difficulty and start the timer automatically
        self.set_timer_difficulty()
    
        self.feedback = tk.Label(self.frame, text="Move your mouse to reveal parts of the image! Click to guess the chameleon location!", fg="#800080", font=("Arial", 16), bg="#ADD8E6")
        self.feedback.pack(pady=15)
    
    # Add top-left message label for powerup feedback
        self.top_left_message = tk.Label(self.frame, text="", font=("Arial", 14, "bold"), bg="#ADD8E6", fg="#800080")
        self.top_left_message.place(x=10, y=10)
    
    # Load the image with standardized scaling
        try:
        # Load original image
            raw_image = Image.open(self.image_file)
            
            # Determine the appropriate standardized size based on orientation
            target_size = self.get_standardized_size(raw_image)
            
            # Resize the image proportionally to fit the standardized size
            self.original_image = self.resize_image_proportionally(raw_image, target_size)
            
            # Update canvas size to match the image
            img_width, img_height = self.original_image.size
            self.game_canvas.config(width=img_width, height=img_height)
        
        # Let GameLogic place chameleons first
        # Process the image in game logic
            self.game_logic.img_width, self.game_logic.img_height = self.original_image.size
        
        # Reset game state for new round
            self.game_logic.reset_game()
        
        # IMPORTANT CHANGE: Now we get the image with chameleons from game_logic
            self.original_image = self.game_logic.game_image_with_chameleons  
        
        # Create blurred version AFTER chameleons are placed
            self.blurred_image = self.original_image.filter(ImageFilter.GaussianBlur(self.blur_level))
        
        # Set initial display as blurred
            self.current_display_image = self.blurred_image.copy()
            self.game_image = ImageTk.PhotoImage(self.current_display_image)
            self.image_on_canvas = self.game_canvas.create_image(0, 0, image=self.game_image, anchor="nw")
        
        # Create powerup buttons
            self.create_powerup_buttons()
        
        # Create game control buttons
            self.create_game_buttons()
        
        # Mouse event handlers
            self.game_canvas.bind("<Motion>", self.update_blur)
            self.game_canvas.bind("<Button-1>", self.game_logic.handle_click)

        # Start the timer
            self.start_timer()

        except Exception as e:
            messagebox.showerror("Error", f"Image didn't load: {e}")
            self.replay()
    
    def create_powerup_buttons(self):
        """Create powerup buttons based on available uses"""
        if self.game_logic.story_mode:
              return  # Skip entirely for story mode
        
        self.top_left_message = tk.Label(self.frame, text="", 
                                        font=("Arial", 14, "bold"), 
                                        bg="#ADD8E6", fg="#800080")
        self.top_left_message.place(x=10, y=10)
    
        self.add_time_btn = tk.Button(
           self.powerup_frame, 
           text=f"Add Time ({self.game_logic.add_time_uses})", 
           command=self.game_logic.use_add_time, 
           bg="#32CD32", 
           fg="black", 
           font=("Arial", 12, "bold"), 
           relief="raised"
        )
        self.add_time_btn.pack(side="left", padx=5)
        self.add_time_btn.bind("<Enter>", lambda e: self.add_time_btn.config(bg="#228B22"))
        self.add_time_btn.bind("<Leave>", lambda e: self.add_time_btn.config(bg="#32CD32"))
    
        self.add_steps_btn = tk.Button(
            self.powerup_frame, 
           text=f"Add Steps ({self.game_logic.add_steps_uses})", 
            command=self.game_logic.use_add_steps, 
            bg="#FF69B4", 
            fg="black", 
            font=("Arial", 12, "bold"), 
            relief="raised"
        )
        self.add_steps_btn.pack(side="left", padx=5)
        self.add_steps_btn.bind("<Enter>", lambda e: self.add_steps_btn.config(bg="#FF1493"))
        self.add_steps_btn.bind("<Leave>", lambda e: self.add_steps_btn.config(bg="#FF69B4"))
    
    def create_game_buttons(self):
        """Create game control buttons"""
        self.pause_btn = tk.Button(
            self.button_frame, 
            text="Pause", 
            command=self.toggle_pause, 
            bg="#FFA500", 
            fg="black", 
            font=("Arial", 12, "bold"), 
            relief="raised"
        )
        self.pause_btn.pack(side="left", padx=5)
        self.pause_btn.bind("<Enter>", lambda e: self.pause_btn.config(bg="#FF8C00"))
        self.pause_btn.bind("<Leave>", lambda e: self.pause_btn.config(bg="#FFA500"))
        
        self.main_menu_btn = tk.Button(
            self.button_frame, 
            text="Main Menu", 
            command=self.return_to_main_menu, 
            bg="#00CED1", 
            fg="black", 
            font=("Arial", 12, "bold"), 
            relief="raised"
        )
        self.main_menu_btn.pack(side="left", padx=5)
        self.main_menu_btn.bind("<Enter>", lambda e: self.main_menu_btn.config(bg="#00B7EB"))
        self.main_menu_btn.bind("<Leave>", lambda e: self.main_menu_btn.config(bg="#00CED1"))
        
        replay_btn = tk.Button(
            self.button_frame, 
            text="Replay", 
            command=self.replay, 
            bg="#FFFF00", 
            fg="black", 
            font=("Arial", 12, "bold"), 
            relief="raised"
        )
        replay_btn.pack(side="left", padx=5)
        replay_btn.bind("<Enter>", lambda e: replay_btn.config(bg="#FFD700"))
        replay_btn.bind("<Leave>", lambda e: replay_btn.config(bg="#FFFF00"))
    
    def toggle_sound(self):
        self.sound_on = not self.sound_on
        if self.sound_on:
           self.sound_btn.config(text="🔊 Sound On", bg="#32CD32")
        else:
           self.sound_btn.config(text="🔇 Sound Off", bg="#A9A9A9")
    
    def toggle_pause(self):
        """Toggle game pause state"""
        if self.game_logic.found:
            return
            
        self.paused = not self.paused
        
        if self.paused:
            self.pause_btn.config(text="Resume")
            self.stop_timer()
            self.pause_overlay = tk.Canvas(self.game_canvas, bg="gray", highlightthickness=0)
            self.pause_overlay.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
            self.pause_overlay.create_text(self.game_canvas.winfo_width()//2, 
                                         self.game_canvas.winfo_height()//2,
                                         text="PAUSED", font=("Arial", 48, "bold"),
                                         fill="white")
            self.game_canvas.unbind("<Button-1>")
        else:
            self.pause_btn.config(text="Pause")
            self.start_timer()
            self.update_powerup_buttons()
            if hasattr(self, "pause_overlay") and self.pause_overlay.winfo_exists():
               self.pause_overlay.destroy()
            self.feedback.config(text="Move your mouse to reveal parts of the image! Click to guess the chameleon location!", fg="#800080")
    
    def clean_up_game_widgets(self):
        """Safely destroy game widgets"""
        if hasattr(self, 'game_canvas') and self.game_canvas.winfo_exists():
            try:
                self.game_canvas.unbind("<Motion>")
                self.game_canvas.unbind("<Button-1>")
                self.game_canvas.destroy()
            except:
                pass
            
        if hasattr(self, 'powerup_frame') and self.powerup_frame.winfo_exists():
            try:
                self.powerup_frame.destroy()
            except:
                pass
            
        if hasattr(self, 'button_frame') and self.button_frame.winfo_exists():
            try:
                self.button_frame.destroy()
            except:
                pass
    
    
    
    
    
    def return_to_main_menu(self):
        """Go back to the main menu"""
        # Cancel any running timer
        if self.timer_id:
            self.window.after_cancel(self.timer_id)
            self.timer_id = None
        self.timer_running = False
        
        # Clean up widgets
        self.clean_up_game_widgets()
    
        
        # Clean up image references
        self.original_image = None
        self.blurred_image = None
        self.current_display_image = None
        
        self.image_file = None
        self.paused = False
        self.make_start_screen()
        self.game_logic = GameLogic(self)
    
    def update_powerup_buttons(self):
        """Update the state and appearance of powerup buttons"""
        time_state = "normal" if (self.game_logic.add_time_uses > 0 and not self.paused 
                                and not self.game_logic.found and self.timer_running) else "disabled"
        
        steps_state = "normal" if (self.game_logic.add_steps_uses > 0 and not self.paused 
                                and not self.game_logic.found) else "disabled"
    
        if hasattr(self, 'add_time_btn') and self.add_time_btn.winfo_exists():
             self.add_time_btn.config(
                text=f"Add Time ({self.game_logic.add_time_uses})", 
                state=time_state,
                bg="#32CD32" if time_state == "normal" else "#A9A9A9"
            )
    
        if hasattr(self, 'add_steps_btn') and self.add_steps_btn.winfo_exists():
            self.add_steps_btn.config(
                text=f"Add Steps ({self.game_logic.add_steps_uses})", 
                state=steps_state,
                bg="#FF69B4" if steps_state == "normal" else "#A9A9A9"
            )
    
        self.update_points_display()
    
    def set_blur_difficulty(self):
        """Set blur parameters based on difficulty level"""
        if self.game_logic.story_mode:
           difficulty_value = self.current_story_difficulty
        else:
           difficulty_value = self.difficulty.get()
        if difficulty_value == "Easy":
            self.blur_level = 5
            self.clear_radius = 100
        elif difficulty_value == "Medium":
            self.blur_level = 8
            self.clear_radius = 75
        else:  # Hard
            self.blur_level = 12
            self.clear_radius = 50
    
    def update_blur(self, event):
        """Update the dynamic blur based on mouse position"""
        if self.paused or self.game_logic.found:
            return
            
        # Get mouse position
        x, y = event.x, event.y
        self.last_mouse_x, self.last_mouse_y = x, y
        
        # Update the image with a clear circular area around the cursor
        self.apply_dynamic_blur(x, y)
    
    def apply_dynamic_blur(self, x, y):
        
       """Apply dynamic blurring with a clear area around cursor position"""
      
        
       try:
           # Check if required components still exist
           if not hasattr(self, 'game_canvas') or not self.game_canvas.winfo_exists():
               return
            
           if not hasattr(self, 'blurred_image') or self.blurred_image is None:
               return
            
           if not hasattr(self, 'image_on_canvas'):
               return
           
           self.current_display_image = self.blurred_image.copy()
           mask = Image.new('L', self.blurred_image.size, 0)
           draw = ImageDraw.Draw(mask)
           draw.ellipse((x-self.clear_radius, y-self.clear_radius, 
                     x+self.clear_radius, y+self.clear_radius), 
                    fill=255)
        
              # Story mode vs normal mode:
           if self.game_logic.story_mode:
               # Story Mode: Reveal image WITH chameleons
               if hasattr(self.game_logic, 'game_image_with_chameleons'):
                self.current_display_image.paste(self.game_logic.game_image_with_chameleons, (0,0), mask)
           else:
              # Normal Mode: Original behavior
              if hasattr(self, 'original_image') and self.original_image is not None:
                  self.current_display_image.paste(self.original_image, (0,0), mask)

            
            # Only update if canvas still exists
           if self.game_canvas.winfo_exists():
               self.game_image = ImageTk.PhotoImage(self.current_display_image)
               self.game_canvas.itemconfig(self.image_on_canvas, image=self.game_image)
        
       except Exception as e:
           print(f"Error applying dynamic blur: {e}")
    
    def set_timer_difficulty(self):
        """Set timer duration based on difficulty"""
        if self.game_logic.story_mode:
           difficulty_value = self.current_story_difficulty
        else:  
           difficulty_value = self.difficulty.get()
        if difficulty_value == "Easy":
            self.time_left = 90  # 1:30
        elif difficulty_value == "Medium":
            self.time_left = 60  # 1:00
        else:  # Hard
            self.time_left = 30  # 0:30
        
        self.total_time = self.time_left#  Store it for dynamic blur scaling
        self.update_timer_display()
    
    def update_timer_display(self):
         """Update the timer display with safety checks"""
         if not hasattr(self, 'timer_display') or not self.timer_display.winfo_exists():
            return
        
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
    
         self.safe_update_widget(self.timer_display, text=time_string, fg=color)
    
    def start_timer(self):
        """Start the timer"""
        if self.paused:
            return
            
        self.timer_running = True
        self.tick_timer()
    
    def stop_timer(self):
        """Stop the timer"""
        self.timer_running = False
        if self.timer_id:
            self.window.after_cancel(self.timer_id)
            self.timer_id = None
    
    def tick_timer(self):
        
       """Update timer each second and reduce clear radius over time"""
       if self.timer_running and self.time_left > 0:
          self.time_left -= 1

        # Dynamically adjust blur clear radius
          min_radius = 20
          if not hasattr(self, 'initial_clear_radius'):
             self.initial_clear_radius = self.clear_radius

             if self.game_logic.story_mode:
              difficulty_value = self.current_story_difficulty
             else:
              difficulty_value = self.difficulty.get()
            
             if difficulty_value == "Easy":
              total_time = 90
             elif difficulty_value == "Medium":
              total_time = 60
             else:
              total_time = 30

          ratio = max(self.time_left / self.total_time, 0)
          self.clear_radius = int(min_radius + (self.initial_clear_radius - min_radius) * ratio)

          self.update_timer_display()
          self.apply_dynamic_blur(self.last_mouse_x, self.last_mouse_y)

          self.timer_id = self.window.after(1000, self.tick_timer)

       elif self.timer_running and self.time_left <= 0:
             self.timer_running = False
             self.timer_display.config(text="Time's Up!", fg="#FF0000")

             

             if not self.game_logic.found:
                 if self.original_image:
                    # Show unblurred image
                    self.game_image = ImageTk.PhotoImage(self.game_logic.game_image_with_chameleons)
                    self.game_canvas.itemconfig(self.image_on_canvas, image=self.game_image)
                
                    # Story mode handling
                    if self.game_logic.story_mode:
                        self.game_logic.highlight_chameleons_red()
                        if self.sound_on:
                           self.gameover_sound.play()
                        self.show_story_failure()
                    else:
                      self.game_logic.highlight_chameleons_red()
                      self.show_message("Time's up! You missed some chameleons!", False)
                      if self.sound_on:
                         self.gameover_sound.play()

    def show_story_success(self):
        level = self.story_images.get_current_level()
        level_num = self.story_images.current_level + 1
        
        success_messages = {
            1: f"First Color Ghost documented in {level['name']}!\nIt quickly vanished, but you've made contact.",
            2: f"Second encounter successful in {level['name']}!\nThe Color Ghost seems more aware of your presence.",
            3: f"Third Color Ghost found in {level['name']}!\nIts adaptation skills are remarkable.",
            4: f"Fourth encounter complete in {level['name']}!\nYou sense the Color Ghost is studying you too.",
            5: f"Final Color Ghost documented in {level['name']}!\nSomething feels different this time..."
        }
        
        message = success_messages.get(level_num, f"Color Ghost found in {level['name']}!")
        self.show_message(message, True)
        self.window.after(2500, self.show_story_completion)

    def show_story_failure(self):
        level = self.story_images.get_current_level()
        level_num = self.story_images.current_level + 1
        
        failure_messages = {
            1: f"The Color Ghost slipped away .\nFirst expeditions are always challenging.",
            2: f"Lost the trail.\nThe Color Ghost has learned from your first encounter.",
            3: f"Missed again!\nIts camouflage adaptation is accelerating.",
            4: f"So close!, yet it vanished.\nThe Color Ghost is testing your dedication.",
            5: f"The Color Ghost remains hidden.\nPatience is key to earning trust."
        }
        
        message = failure_messages.get(level_num, f"The Color Ghost escaped!")
        # Clear any existing messages
        self.feedback.config(text="")
         # Create failure overlay
        overlay = tk.Canvas(self.game_canvas, bg="black", highlightthickness=0)
        overlay.place(relx=0.5, rely=0.5, anchor="center", width=self.game_canvas.winfo_width(), height=self.game_canvas.winfo_height())
        overlay.create_rectangle(0, 0, self.game_canvas.winfo_width(), self.game_canvas.winfo_height(), fill="black", stipple="gray50", outline="")
    
        # Add failure text
        overlay.create_text(self.game_canvas.winfo_width()//2, 
                       self.game_canvas.winfo_height()//2 - 50,
                       text="EXPEDITION FAILED",
                       font=("Arial", 24, "bold"),
                       fill="white")
    
        overlay.create_text(self.game_canvas.winfo_width()//2,
                       self.game_canvas.winfo_height()//2,
                       text=message,
                       font=("Arial", 14),
                       fill="white",
                       width=self.game_canvas.winfo_width()-40)
    
        # Schedule the retry menu to appear
        self.window.after(2500, lambda: self.show_story_retry(overlay))

    def show_story_completion(self):
        # Destroy existing button frame if it exists
        if self.current_button_frame:
           try:
               self.current_button_frame.destroy()
           except tk.TclError:
              pass
    
        # Create new button frame
        self.current_button_frame = tk.Frame(self.frame, bg="#ADD8E6")
        self.current_button_frame.pack(pady=10)

        if self.story_images.current_level < len(self.story_images.story_levels) - 1:
           next_btn = tk.Button(self.current_button_frame, text="Next Level",
                           command=self.next_story_level,
                           bg="#32CD32", fg="white",
                           font=("Arial", 14, "bold"))
           next_btn.pack(side=tk.LEFT, padx=10)
        else:
           complete_btn = tk.Button(self.current_button_frame, text="Story Complete!",
                                    command=self.show_story_complete,
                                    bg="#FFD700", fg="black",
                                    font=("Arial", 14, "bold"))
           complete_btn.pack(side=tk.LEFT, padx=10)

        retry_btn = tk.Button(self.current_button_frame, text="Retry Level",
                         command=self.retry_story_level,
                         bg="#FF6347", fg="white",
                         font=("Arial", 14, "bold"))
        retry_btn.pack(side=tk.LEFT, padx=10)

        menu_btn = tk.Button(self.current_button_frame, text="Main Menu",
                        command=self.return_to_main_menu,
                        bg="#9370DB", fg="white",
                        font=("Arial", 14, "bold"))
        menu_btn.pack(side=tk.LEFT, padx=10)

    def show_story_retry(self,overlay=None):
        if overlay:
            try:
               overlay.destroy()
            except:
              pass
        # Destroy existing button frame if it exists
        if self.current_button_frame:
            try:
                self.current_button_frame.destroy()
            except tk.TclError:
                pass
    
        # Create new button frame
        self.current_button_frame = tk.Frame(self.frame, bg="#ADD8E6")
        self.current_button_frame.place(relx=0.5, rely=0.8, anchor="center")
    
        retry_btn = tk.Button(self.current_button_frame, text="Try Again",
                         command=self.retry_story_level,
                         bg="#FF6347", fg="white",
                         font=("Arial", 14, "bold"))
        retry_btn.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=5)
    
        menu_btn = tk.Button(self.current_button_frame, text="Main Menu",
                        command=self.return_to_main_menu,
                        bg="#9370DB", fg="white",
                        font=("Arial", 14, "bold"))
        menu_btn.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=5)

    def next_story_level(self):
        self.story_images.next_level()
        self.show_story_level_intro()

    def retry_story_level(self):
        self.start_story_level()

    def show_story_complete(self):
        """Enhanced story completion with the trust narrative"""
        for widget in self.frame.winfo_children():
            if widget != getattr(self, "bg_label", None):
                try:
                    widget.destroy()
                except tk.TclError:
                    pass

        # Title
        title = tk.Label(self.frame, text="🎉 EXPEDITION COMPLETE! 🎉",
                        font=("Arial", 26, "bold"), fg="#00CED1", bg="#ADD8E6")
        title.pack(pady=20)

        # Story conclusion
        conclusion_text = """🦎 THE COLOR GHOSTS' TRUST 🦎

    After 5 dedicated expeditions, something extraordinary happens...

    RESEARCH STATUS: COMPLETE
    Documentation: Successful
    Relationship: Trusted Observer

    Legend says that other Color Ghosts still roam the world,
    waiting for researchers who show the same dedication
    and respect for nature that you have demonstrated."""

        conclusion_label = tk.Label(self.frame, text=conclusion_text,
                                  font=("Arial", 12), fg="#000080", bg="#ADD8E6",
                                  justify=tk.CENTER, wraplength=700)
        conclusion_label.pack(pady=20)

        # Achievement
        achievement = tk.Label(self.frame, text="🏆 ACHIEVEMENT UNLOCKED: Color Ghost Whisperer",
                             font=("Arial", 14, "bold"), fg="#FFD700", bg="#ADD8E6")
        achievement.pack(pady=15)

        # Stats
        stats = tk.Label(self.frame, text=f"Expeditions Completed: {len(self.story_images.story_levels)}",
                        font=("Arial", 12), fg="#008000", bg="#ADD8E6", justify=tk.CENTER)
        stats.pack(pady=10)

        # Create a button frame at the bottom center
        button_frame = tk.Frame(self.frame, bg="#ADD8E6")
        button_frame.pack(side=tk.BOTTOM, pady=25)

        # New expedition button
        new_expedition_btn = tk.Button(button_frame, text="New Expedition",
                                     command=self.start_story_mode,
                                     bg="#228B22", fg="white",
                                     font=("Arial", 14, "bold"))
        new_expedition_btn.pack(side=tk.LEFT, padx=15, ipadx=15, ipady=8)

        # Menu button
        menu_btn = tk.Button(button_frame, text="Main Menu",
                            command=self.return_to_main_menu,
                            bg="#8B4513", fg="white",
                            font=("Arial", 14, "bold"))
        menu_btn.pack(side=tk.LEFT, padx=15, ipadx=15, ipady=8)

    def show_story_intro(self):
        """Display the story introduction before starting story mode"""
        # Clear the frame
        for widget in self.frame.winfo_children():
            if widget != getattr(self, "bg_label", None):
                try:
                    widget.destroy()
                except tk.TclError:
                    pass

        # Create a main container frame
        main_frame = tk.Frame(self.frame, bg="#ADD8E6")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Title
        title = tk.Label(main_frame, text="THE COLOR GHOST EXPEDITION 🦎",
                        font=("Arial", 24, "bold"), fg="#000080", bg="#ADD8E6")
        title.pack(pady=(10, 20))

        # Story text - broken into smaller paragraphs for better display
        story_text1 = """An animal researcher has discovered new adaptive chameleons 
    called the "Color Ghosts." These mysterious creatures possess 
    extraordinary camouflage abilities that surpass any known species."""

        story_text2 = """Each time the researcher finds one, it quickly escapes and 
    becomes even more adaptive, requiring the hunt to continue 
    in new environments. Through 5 challenging expeditions, 
    you must track these elusive Color Ghosts."""

        story_text3 = """But beware - with each encounter, they become more cunning 
    and harder to spot. Will you earn their trust, or will they 
    remain forever hidden in the wild?"""

        story_text4 = """The legend says that after proving your dedication, 
    the Color Ghosts may finally reveal themselves willingly, 
    allowing for peaceful observation and documentation."""

        story_text5 = """Legendary Color Ghosts still roam the world, 
    waiting for the right researcher to find them..."""

        # Create labels for each paragraph
        for i, text in enumerate([story_text1, story_text2, story_text3, story_text4, story_text5], 1):
            story_label = tk.Label(main_frame, text=text,
                                  font=("Arial", 12), fg="#000080", bg="#ADD8E6",
                                  justify=tk.LEFT, wraplength=650)
            story_label.pack(pady=8, padx=20)

        # Researcher note
        note = tk.Label(main_frame, text="Research Objective: Document all 5 Color Ghost encounters",
                       font=("Arial", 12, "italic"), fg="#8B0000", bg="#ADD8E6")
        note.pack(pady=15)

        # Button frame
        button_frame = tk.Frame(main_frame, bg="#ADD8E6")
        button_frame.pack(pady=20)

        # Begin expedition button
        begin_btn = tk.Button(button_frame, text="Begin Expedition",
                             command=self.start_story_levels,
                             bg="#228B22", fg="white",
                             font=("Arial", 16, "bold"))
        begin_btn.pack(side=tk.LEFT, padx=15, ipadx=20, ipady=10)

        # Back to menu button
        back_btn = tk.Button(button_frame, text="Back to Menu",
                            command=self.return_to_main_menu,
                            bg="#8B4513", fg="white",
                            font=("Arial", 16, "bold"))
        back_btn.pack(side=tk.LEFT, padx=15, ipadx=20, ipady=10)

    def start_story_levels(self):
        """Start the actual story mode gameplay"""
        self.game_logic.story_mode = True
        self.story_images.reset_levels()
        self.show_story_level_intro()

    def show_story_level_intro(self):
        """Enhanced level intro with expedition context"""
        level = self.story_images.get_current_level()
        level_num = self.story_images.current_level + 1
        
        # Clear the frame
        for widget in self.frame.winfo_children():
            if widget != getattr(self, "bg_label", None):
                try:
                    widget.destroy()
                except tk.TclError:
                    pass

        # Expedition header
        header = tk.Label(self.frame, text=f"🔍 EXPEDITION {level_num}/5",
                         font=("Arial", 22, "bold"), fg="#000080", bg="#ADD8E6")
        header.pack(pady=15)

        # Location title
        location_title = tk.Label(self.frame, text=f"📍 Location: {level['name']}",
                                 font=("Arial", 18, "bold"), fg="#8B0000", bg="#ADD8E6")
        location_title.pack(pady=10)

        # Expedition context based on level
        expedition_texts = {
            1: "Your first encounter with the Color Ghosts begins.\nThey are still learning to adapt - this may be your best chance.",
            2: "The Color Ghost has escaped and grown more cautious.\nYour presence is now familiar to them.",
            3: "The chase continues. The Color Ghost's camouflage\nhas improved significantly from your previous encounters.",
            4: "You're getting close. The Color Ghost is now extremely\nadaptive, but patterns in behavior are emerging.",
            5: "Final expedition. The Color Ghost has reached peak\nadaptation, but trust may be building..."
        }

        context_text = expedition_texts.get(level_num, "Continue the expedition...")
        context_label = tk.Label(self.frame, text=context_text,
                                font=("Arial", 14), fg="#000080", bg="#ADD8E6",
                                justify=tk.CENTER)
        context_label.pack(pady=20)

        # Research notes
        notes_text = f"Research Notes:\n{level['description']}"
        notes_label = tk.Label(self.frame, text=notes_text,
                              font=("Arial", 12), fg="#006400", bg="#ADD8E6",
                              justify=tk.CENTER)
        notes_label.pack(pady=15)

        if level_num == 1:
            difficulty_level = "Easy"
        elif level_num in [2, 3]:
            difficulty_level = "Medium"
        else:  # levels 4 and 5
            difficulty_level = "Hard"
    
        difficulty_text = f"Difficulty: {difficulty_level}"
        difficulty_label = tk.Label(self.frame, text=difficulty_text,
                                   font=("Arial", 12, "bold"), fg="#FF6347", bg="#ADD8E6")
        difficulty_label.pack(pady=5)

        # Button frame
        button_frame = tk.Frame(self.frame, bg="#ADD8E6")
        button_frame.pack(pady=25)

        # Start tracking button
        start_btn = tk.Button(button_frame, text="Start Tracking",
                             command=self.start_story_level,
                             bg="#FF6347", fg="white",
                             font=("Arial", 16, "bold"))
        start_btn.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=10)

        # Back button
        back_btn = tk.Button(button_frame, text="Back to Menu",
                            command=self.return_to_main_menu,
                            bg="#8B4513", fg="white",
                            font=("Arial", 16, "bold"))
        back_btn.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=10)

    def show_story_success(self):
        level = self.story_images.get_current_level()
        level_num = self.story_images.current_level + 1
        
        success_messages = {
            1: f"First Color Ghost documented in {level['name']}!\nIt quickly vanished, but you've made contact.",
            2: f"Second encounter successful in {level['name']}!\nThe Color Ghost seems more aware of your presence.",
            3: f"Third Color Ghost found in {level['name']}!\nIts adaptation skills are remarkable.",
            4: f"Fourth encounter complete in {level['name']}!\nYou sense the Color Ghost is studying you too.",
            5: f"Final Color Ghost documented in {level['name']}!\nSomething feels different this time..."
        }
        
        message = success_messages.get(level_num, f"Color Ghost found in {level['name']}!")
        self.show_message(message, True)
        self.window.after(2500, self.show_story_completion)

    def show_message_in_game(self, message):
        """Show a temporary message in the game area"""
        self.top_left_message.config(text=message)
        self.top_left_message.after(3000, lambda: self.top_left_message.config(text=""))

    def show_message(self, msg, success):
        """Show a message in the feedback label"""
        if hasattr(self, 'feedback'):
           if success:
            self.safe_update_widget(self.feedback, text=msg, fg="#008000")
           else:
            self.safe_update_widget(self.feedback, text=msg, fg="#FF0000")

    def replay(self):
        """Restart the game with the same image"""
        # Cancel any running timer
        if self.timer_id:
            self.window.after_cancel(self.timer_id)
            self.timer_id = None
        self.timer_running = False
        self.paused = False
        
        # Start a new game
        self.start_game()


# Main entry point
if __name__ == "__main__":
    window = tk.Tk()
    game = GameUI(window)
    window.mainloop()