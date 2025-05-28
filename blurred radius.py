import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import random
import numpy as np
import threading
import time

class GameLogic:
    def __init__(self, ui):
        self.ui = ui
        self.img_width = 0
        self.img_height = 0
        self.chameleon_x = 0
        self.chameleon_y = 0
        self.click_radius = 30
        self.found = False
        self.circle_id = None
        self.attempts = 0
        self.max_attempts = 5
        self.game_active = False
        
    def reset_game(self):
        """Reset the game state for a new round"""
        self.found = False
        self.attempts = 0
        self.game_active = True
        
        # Reset UI elements safely
        if hasattr(self.ui, 'game_canvas') and self.ui.game_canvas:
            if self.circle_id:
                try:
                    self.ui.game_canvas.delete(self.circle_id)
                except:
                    pass
            self.circle_id = None
            
        # Place chameleon randomly
        margin = 50
        if self.img_width > 0 and self.img_height > 0:
            self.chameleon_x = random.randint(margin, max(margin + 1, self.img_width - margin))
            self.chameleon_y = random.randint(margin, max(margin + 1, self.img_height - margin))
            
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
        if self.found or not self.game_active:
            return
            
        try:
            # Get click position
            x, y = event.x, event.y
            
            # Calculate distance to chameleon
            distance = ((x - self.chameleon_x) ** 2 + (y - self.chameleon_y) ** 2) ** 0.5
            
            # Check if chameleon found
            if distance <= self.click_radius:
                self.found = True
                self.game_active = False
                
                # Draw circle around chameleon
                self.draw_result_circle("green")
                
                # Stop timer
                self.ui.stop_timer()
                
                # Show full unblurred image
                self.ui.show_final_image()
                
                self.ui.show_message(f"You found the chameleon! Great job!", True)
            else:
                # Wrong click
                self.attempts += 1
                attempts_left = self.max_attempts - self.attempts
                
                if attempts_left <= 0:
                    # Game over
                    self.found = True
                    self.game_active = False
                    
                    # Show full unblurred image first
                    self.ui.show_final_image()
                    
                    # Draw circle
                    self.draw_result_circle("red")
                    
                    self.ui.show_message(f"Game over! The chameleon was here!", False)
                    self.ui.stop_timer()
                else:
                    hint = ""
                    if distance < 100:
                        hint = "Very close! "
                    elif distance < 200:
                        hint = "Getting warmer! "
                        
                    self.ui.show_message(f"{hint}Keep looking! {attempts_left} attempts left.", False)
        except Exception as e:
            print(f"Error in handle_click: {e}")

    def draw_result_circle(self, color):
        """Draw the result circle around chameleon"""
        try:
            if hasattr(self.ui, 'game_canvas') and self.ui.game_canvas:
                self.circle_id = self.ui.game_canvas.create_oval(
                    self.chameleon_x - self.click_radius, 
                    self.chameleon_y - self.click_radius,
                    self.chameleon_x + self.click_radius, 
                    self.chameleon_y + self.click_radius,
                    outline=color, width=3
                )
        except Exception as e:
            print(f"Error drawing circle: {e}")


class GameUI:
    def __init__(self, window):
        self.window = window
        self.window.title("Chameleon Hunt")
        self.window.geometry("800x600") 
        self.image_file = None
        self.difficulty = tk.StringVar(value="Medium")
        self.bg_label = None
        
        # Timer variables
        self.timer_running = False
        self.time_left = 0
        self.timer_id = None
        
        # Blur variables
        self.original_image = None
        self.blurred_image = None
        self.current_display_image = None
        self.clear_radius = 100
        self.blur_level = 5
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        
        # Performance optimization
        self.last_update_time = 0
        self.update_interval = 0.03  # 30ms between updates
        self.blur_cache = {}  # Cache for blur calculations
       
        # Background color 
        self.window.configure(bg="#ADD8E6")
        
        # Main frame
        self.frame = tk.Frame(self.window, bg="#ADD8E6")
        self.frame.pack(expand=True, fill="both")
        
        # Background image
        self.setup_background()
        
        # Create game logic manager
        self.game_logic = GameLogic(self)
            
        # Start screen
        self.make_start_screen()
        
        # Initialize game canvas and feedback label
        self.game_canvas = None
        self.feedback = None

    def setup_background(self):
        """Setup background image with error handling"""
        try:
            bg_img = Image.open("jungle_bg.jpg")  
            bg_img = bg_img.resize((800, 600), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_img)
            self.bg_label = tk.Label(self.frame, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Background image not found: {e}")
            self.frame.configure(bg="#ADD8E6")

    def make_start_screen(self):
        """Create the start screen"""
        # Clear the frame safely
        self.clear_frame()
                
        # Title frame 
        title_frame = tk.Frame(self.frame, bg="#ADD8E6")
        title_frame.pack(pady=30)
        
        # Title
        title = tk.Label(title_frame, text="Chameleon Hunt", font=("Arial", 36, "bold"), fg="#800080", bg="#ADD8E6")
        title.pack()
        
        # Welcome message
        welcome = tk.Label(title_frame, text="Can you find the sneaky chameleon?", font=("Arial", 14, "italic"), fg="#008000", bg="#ADD8E6")
        welcome.pack(pady=5)
        
        # Chameleon icon
        chameleon_icon = tk.Label(title_frame, text="🦎", font=("Arial", 30), fg="#008000", bg="#ADD8E6")
        chameleon_icon.pack(pady=10)
        
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
        
        # Difficulty section
        self.create_difficulty_section()
        
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
        
        # Feedback label
        self.feedback = tk.Label(self.frame, text="", font=("Arial", 16), bg="#ADD8E6", fg="#FF0000")
        self.feedback.pack(pady=15)

    def create_difficulty_section(self):
        """Create difficulty selection section"""
        diff_label = tk.Label(self.frame, text="Pick Difficulty:", font=("Arial", 16, "bold"), bg="#ADD8E6", fg="#800080")
        diff_label.pack(pady=10)
        
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

    def clear_frame(self):
        """Safely clear the frame"""
        for widget in self.frame.winfo_children():
            if widget != getattr(self, "bg_label", None):
                try:
                    widget.destroy()
                except tk.TclError:
                    pass

    def upload_pic(self):
        """Handle image upload"""
        file = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file:
            self.image_file = file
            self.show_feedback("Image loaded! Ready to hunt!", "#008000")
        else:
            self.show_feedback("No image picked.", "#FF0000")

    def show_feedback(self, text, color):
        """Show feedback message safely"""
        try:
            if hasattr(self, 'feedback') and self.feedback and self.feedback.winfo_exists():
                self.feedback.config(text=text, fg=color)
        except Exception as e:
            print(f"Error showing feedback: {e}")

    def start_game(self):
        """Start the game"""
        if not self.image_file:
            messagebox.showerror("Error", "Upload an image first!")
            return
            
        # Clear frame and setup game
        self.clear_frame()
        self.setup_game_ui()
        
        # Load and process image
        if self.load_game_image():
            self.game_logic.reset_game()
            self.set_timer_difficulty()
            self.start_timer()
            self.show_feedback("Move your mouse to reveal parts of the image! Click to guess!", "#800080")
        else:
            self.make_start_screen()

    def setup_game_ui(self):
        """Setup the game UI elements"""
        # Timer frame
        self.timer_frame = tk.Frame(self.frame, bg="#ADD8E6")
        self.timer_frame.pack(pady=5)
        
        self.timer_display = tk.Label(self.timer_frame, text="Time: 0:00", font=("Arial", 18, "bold"), bg="#ADD8E6", fg="#FF5733")
        self.timer_display.pack(padx=10)
        
        # Game canvas
        self.game_canvas = tk.Canvas(self.frame, bg="white", highlightthickness=2, highlightbackground="#00CED1")
        self.game_canvas.pack(fill="both", expand=True)
        
        # Feedback label
        self.feedback = tk.Label(self.frame, text="", font=("Arial", 16), bg="#ADD8E6", fg="#FF0000")
        self.feedback.pack(pady=15)

    def load_game_image(self):
        """Load and process the game image"""
        try:
            # Load original image
            self.original_image = Image.open(self.image_file)
            self.original_image.thumbnail((800, 600))
            
            # Set blur difficulty
            self.set_blur_difficulty()
            
            # Create blurred version
            self.blurred_image = self.original_image.filter(ImageFilter.GaussianBlur(self.blur_level))
            
            # Set initial display as blurred
            self.current_display_image = self.blurred_image.copy()
            self.game_image = ImageTk.PhotoImage(self.current_display_image)
            self.image_on_canvas = self.game_canvas.create_image(0, 0, image=self.game_image, anchor="nw")
            
            # Set image dimensions
            self.game_logic.img_width, self.game_logic.img_height = self.original_image.size
            
            # Bind events with optimized handlers
            self.game_canvas.bind("<Motion>", self.throttled_update_blur)
            self.game_canvas.bind("<Button-1>", self.game_logic.handle_click)
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Image didn't load: {e}")
            return False

    def throttled_update_blur(self, event):
        """Throttled blur update to improve performance"""
        current_time = time.time()
        if current_time - self.last_update_time < self.update_interval:
            return
            
        self.last_update_time = current_time
        self.update_blur(event)

    def update_blur(self, event):
        """Update the dynamic blur based on mouse position"""
        if self.game_logic.found or not self.game_logic.game_active:
            return
            
        try:
            x, y = event.x, event.y
            self.last_mouse_x, self.last_mouse_y = x, y
            
            # Use threading for heavy image processing
            threading.Thread(target=self.apply_dynamic_blur_threaded, args=(x, y), daemon=True).start()
        except Exception as e:
            print(f"Error in update_blur: {e}")

    def apply_dynamic_blur_threaded(self, x, y):
        """Apply dynamic blurring in a separate thread"""
        try:
            if self.original_image is None or self.blurred_image is None:
                return
                
            # Create cache key
            cache_key = (int(x/10)*10, int(y/10)*10, int(self.clear_radius/10)*10)
            
            # Check cache first
            if cache_key in self.blur_cache:
                self.current_display_image = self.blur_cache[cache_key]
            else:
                # Create blurred image with clear area
                self.current_display_image = self.blurred_image.copy()
                
                # Create mask
                mask = Image.new('L', self.original_image.size, 0)
                draw = ImageDraw.Draw(mask)
                
                radius = max(10, min(self.clear_radius, 300))
                draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=255)
                
                # Apply mask
                self.current_display_image.paste(self.original_image, (0, 0), mask)
                
                # Cache the result (limit cache size)
                if len(self.blur_cache) > 50:
                    self.blur_cache.clear()
                self.blur_cache[cache_key] = self.current_display_image.copy()
            
            # Update UI in main thread
            self.window.after(0, self.update_canvas_image)
            
        except Exception as e:
            print(f"Error applying dynamic blur: {e}")

    def update_canvas_image(self):
        """Update the canvas image in the main thread"""
        try:
            if self.current_display_image and hasattr(self, 'image_on_canvas'):
                self.game_image = ImageTk.PhotoImage(self.current_display_image)
                self.game_canvas.itemconfig(self.image_on_canvas, image=self.game_image)
        except Exception as e:
            print(f"Error updating canvas: {e}")

    def show_final_image(self):
        """Show the final unblurred image"""
        try:
            if self.original_image:
                self.game_image = ImageTk.PhotoImage(self.original_image)
                if hasattr(self, 'image_on_canvas'):
                    self.game_canvas.itemconfig(self.image_on_canvas, image=self.game_image)
        except Exception as e:
            print(f"Error showing final image: {e}")

    def set_blur_difficulty(self):
        """Set blur parameters based on difficulty level"""
        difficulty_value = self.difficulty.get()
        if difficulty_value == "Easy":
            self.blur_level = 5
            self.max_clear_radius = 150
            self.min_clear_radius = 80
        elif difficulty_value == "Medium":
            self.blur_level = 8
            self.max_clear_radius = 120
            self.min_clear_radius = 60
        else:  # Hard
            self.blur_level = 12
            self.max_clear_radius = 100
            self.min_clear_radius = 40
        
        self.clear_radius = self.max_clear_radius

    def set_timer_difficulty(self):
        """Set timer duration based on difficulty"""
        difficulty_value = self.difficulty.get()
        if difficulty_value == "Easy":
            self.time_left = 90
            self.initial_time = 90
        elif difficulty_value == "Medium":
            self.time_left = 60
            self.initial_time = 60
        else:  # Hard
            self.time_left = 30
            self.initial_time = 30
        
        self.update_timer_display()

    def start_timer(self):
        """Start the timer"""
        self.timer_running = True
        self.tick_timer()

    def stop_timer(self):
        """Stop the timer"""
        self.timer_running = False
        if self.timer_id:
            try:
                self.window.after_cancel(self.timer_id)
            except:
                pass
            self.timer_id = None

    def tick_timer(self):
        """Update timer each second"""
        try:
            if self.timer_running and self.time_left > 0:
                self.time_left -= 1
                self.update_timer_display()
                self.update_clear_radius()
                self.timer_id = self.window.after(1000, self.tick_timer)
            elif self.timer_running and self.time_left <= 0:
                self.handle_timeout()
        except Exception as e:
            print(f"Error in tick_timer: {e}")

    def handle_timeout(self):
        """Handle timer timeout"""
        self.timer_running = False
        self.game_logic.game_active = False
        
        if hasattr(self, 'timer_display') and self.timer_display:
            self.timer_display.config(text="Time's Up!", fg="#FF0000")
        
        if not self.game_logic.found:
            self.game_logic.found = True
            self.show_final_image()
            self.game_logic.draw_result_circle("red")
            self.show_message("Time's up! The chameleon was here!", False)
            
        messagebox.showinfo("Time's Up!", "Time's up! Game over.")

    def update_timer_display(self):
        """Update the timer display"""
        try:
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
            
            if hasattr(self, 'timer_display') and self.timer_display:
                self.timer_display.config(text=time_string, fg=color)
        except Exception as e:
            print(f"Error updating timer display: {e}")

    def update_clear_radius(self):
        """Update the clear radius based on time remaining"""
        try:
            if hasattr(self, 'initial_time') and hasattr(self, 'max_clear_radius') and hasattr(self, 'min_clear_radius'):
                time_progress = 1 - (self.time_left / self.initial_time)
                radius_range = self.max_clear_radius - self.min_clear_radius
                self.clear_radius = self.max_clear_radius - (radius_range * time_progress)
                self.clear_radius = max(self.clear_radius, self.min_clear_radius)
                
                # Clear cache when radius changes significantly
                self.blur_cache.clear()
        except Exception as e:
            print(f"Error updating clear radius: {e}")

    def show_message(self, msg, success):
        """Show a message to the user"""
        try:
            if hasattr(self, 'feedback') and self.feedback and self.feedback.winfo_exists():
                color = "#008000" if success else "#FF0000"
                self.feedback.config(text=msg, fg=color)
        except Exception as e:
            print(f"Error showing message: {e}")


# Run the game
if __name__ == "__main__":
    window = tk.Tk()
    game = GameUI(window)
    window.mainloop()