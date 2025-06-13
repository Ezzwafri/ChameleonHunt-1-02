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
            self.chameleon_x = random.randint(margin, max(margin + 1, self.img_width - margin))
            self.chameleon_y = random.randint(margin, max(margin + 1, self.img_height - margin))
        else:
            # Default positioning if image dimensions not set yet
            self.chameleon_x = 400
            self.chameleon_y = 300

        # Adjust difficulty parameters depending on mode
        if self.story_mode:
            # Use difficulty from current story level
            difficulty = self.ui.current_story_difficulty
        else:
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
        self.difficulty = tk.StringVar(value="Easy")  # Set default difficulty
        self.bg_label = None
        self.story_images = StoryImages()
        self.current_button_frame = None
        self.current_story_difficulty = "Easy"

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
        self.initial_clear_radius = 100

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
        story_btn.bind("<Leave>", lambda e: self.animate_button(story_btn, "#FF69B4"))

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
        upload_btn.bind("<Leave>", lambda e: self.animate_button(upload_btn, "#FFFF00"))

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
        level = self.story_images.get_current_level()

        # Set story mode flag
        self.game_logic.story_mode = True
    
        # Store current story difficulty for the game logic
        self.current_story_difficulty = level['difficulty']

        # Try to open the story image file
        try:
            self.original_image = Image.open(level['image_data'])
            print(f"Successfully loaded {level['image_data']}")
        except Exception as e:
            # If the image file doesn't exist, create a placeholder image
            print(f"Warning: Could not load {level['image_data']}: {e}")
            print("Creating placeholder image...")
        
            self.original_image = self.create_placeholder_image(level)

        # Start the game with this image
        self.start_game_with_image()

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
        self.initial_clear_radius = self.clear_radius

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

            # Reset game state for new round
            self.game_logic.reset_game()

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

    def animate_button(self, button, color):
        button.config(bg=color)

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

        # Load the image
        try:
            self.original_image = Image.open(self.image_file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
            return

        # Start the game
        self.start_game_with_image()

    def set_blur_difficulty(self):
        if self.game_logic.story_mode:
           difficulty_value = self.current_story_difficulty
        else:
           difficulty_value = self.difficulty.get()
        
        if difficulty_value == "Easy":
           self.blur_level = 5
           self.clear_radius = 120
        elif difficulty_value == "Medium":
           self.blur_level = 8
           self.clear_radius = 100
        else:  # Hard
           self.blur_level = 12
           self.clear_radius = 80

    def update_blur(self, event):
        if self.game_logic.found:
            return

        x, y = event.x, event.y
        self.last_mouse_x, self.last_mouse_y = x, y

        self.apply_dynamic_blur(x, y)

    def apply_dynamic_blur(self, x, y):
        if self.original_image is None or self.blurred_image is None:
            return
        try:
            self.current_display_image = self.blurred_image.copy()
            mask = Image.new('L', self.original_image.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((x - self.clear_radius, y - self.clear_radius,
                          x + self.clear_radius, y + self.clear_radius), fill=255)
            self.current_display_image.paste(self.original_image, (0, 0), mask)
            self.game_image = ImageTk.PhotoImage(self.current_display_image)
            self.game_canvas.itemconfig(self.image_on_canvas, image=self.game_image)
        except Exception as e:
            print(f"Error applying dynamic blur: {e}")

    def set_timer_difficulty(self):
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

        self.update_timer_display()

    def update_timer_display(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        time_string = f"Time: {minutes}:{seconds:02d}"

        if self.time_left > 20:
            color = "#32CD32"  # Green
        elif self.time_left > 10:
            color = "#FFA500"  # Orange
        else:
            color = "#FF0000"  # Red

        self.timer_display.config(text=time_string, fg=color)

    def start_timer(self):
        self.timer_running = True
        self.tick_timer()

    def stop_timer(self):
        self.timer_running = False
        if self.timer_id:
            self.window.after_cancel(self.timer_id)
            self.timer_id = None

    def tick_timer(self):
        """Update timer each second"""
        if self.timer_running and self.time_left > 0:
           self.time_left -= 1

           # Dynamically decrease clear_radius proportional to time left
           min_radius = 20
           total_time = 0
        
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
            
           ratio = max(self.time_left / total_time, 0)
           self.clear_radius = int(min_radius + (self.initial_clear_radius - min_radius) * ratio)

           self.update_timer_display()
           # Refresh blur with new clear radius
           self.apply_dynamic_blur(self.last_mouse_x, self.last_mouse_y)

           self.timer_id = self.window.after(1000, self.tick_timer)
        elif self.timer_running and self.time_left <= 0:
           self.timer_running = False
           self.timer_display.config(text="Time's Up!", fg="#FF0000")
        
           # End the game by showing the chameleon position
           if not self.game_logic.found:
              # Show unblurred image first
              if self.original_image:
                 self.game_image = ImageTk.PhotoImage(self.original_image)
                 self.game_canvas.itemconfig(self.image_on_canvas, image=self.game_image)
            
              # Draw the chameleon circle
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
              self.game_logic.found = True

    def show_message(self, msg, success):
        if hasattr(self, 'feedback') and self.feedback and self.feedback.winfo_exists():
            if success:
                self.feedback.config(text=msg, fg="#008000")
            else:
                self.feedback.config(text=msg, fg="#FF0000")

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
            1: f"The Color Ghost slipped away in {level['name']}.\nFirst expeditions are always challenging.",
            2: f"Lost the trail in {level['name']}.\nThe Color Ghost has learned from your first encounter.",
            3: f"Missed again in {level['name']}!\nIts camouflage adaptation is accelerating.",
            4: f"So close in {level['name']}, yet it vanished.\nThe Color Ghost is testing your dedication.",
            5: f"The Color Ghost remains hidden in {level['name']}.\nPatience is key to earning trust."
        }
        
        message = failure_messages.get(level_num, f"The Color Ghost escaped in {level['name']}!")
        self.show_message(message, False)
        self.window.after(2500, self.show_story_retry)

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
                        command=self.return_to_menu,
                        bg="#9370DB", fg="white",
                        font=("Arial", 14, "bold"))
        menu_btn.pack(side=tk.LEFT, padx=10)

    def show_story_retry(self):
        # Destroy existing button frame if it exists
        if self.current_button_frame:
            try:
                self.current_button_frame.destroy()
            except tk.TclError:
                pass
    
        # Create new button frame
        self.current_button_frame = tk.Frame(self.frame, bg="#ADD8E6")
        self.current_button_frame.pack(pady=10)

        retry_btn = tk.Button(self.current_button_frame, text="Try Again",
                              command=self.retry_story_level,
                              bg="#FF6347", fg="white",
                              font=("Arial", 14, "bold"))
        retry_btn.pack(side=tk.LEFT, padx=10)

        menu_btn = tk.Button(self.current_button_frame, text="Main Menu",
                        command=self.return_to_menu,
                        bg="#9370DB", fg="white",
                        font=("Arial", 14, "bold"))
        menu_btn.pack(side=tk.LEFT, padx=10)

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
                            command=self.return_to_menu,
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
                            command=self.return_to_menu,
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
                            command=self.return_to_menu,
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

    def return_to_menu(self):
        self.game_logic.story_mode = False
        self.story_images.reset_levels()
        self.make_start_screen()

# Run the game
if __name__ == "__main__":
    window = tk.Tk()
    game = GameUI(window)
    window.mainloop()