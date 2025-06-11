import pygame
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw
from game_functions import GameLogic
pygame.mixer.init()

class GameUI:
    def __init__(self, window):
        self.sound_on = True 
        self.click_sound = pygame.mixer.Sound("sounds/click.wav")
        self.win_sound = pygame.mixer.Sound("sounds/win.wav")
        self.gameover_sound = pygame.mixer.Sound("sounds/gameover.wav")
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
        if self.game_logic.add_time_uses > 0:
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
        
        if self.game_logic.add_steps_uses > 0:
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
    
    def return_to_main_menu(self):
        """Go back to the main menu"""
        # Cancel any running timer
        if self.timer_id:
            self.window.after_cancel(self.timer_id)
            self.timer_id = None
        self.timer_running = False
        
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
        if hasattr(self, 'add_time_btn') and self.add_time_btn.winfo_exists():
            self.add_time_btn.config(
                text=f"Add Time ({self.game_logic.add_time_uses})", 
                state="disabled" if self.paused or self.game_logic.add_time_uses == 0 else "normal",
                bg="#A9A9A9" if self.paused or self.game_logic.add_time_uses == 0 else "#32CD32"
            )
        
        if hasattr(self, 'add_steps_btn') and self.add_steps_btn.winfo_exists():
            self.add_steps_btn.config(
                text=f"Add Steps ({self.game_logic.add_steps_uses})", 
                state="disabled" if self.paused or self.game_logic.add_steps_uses == 0 else "normal",
                bg="#A9A9A9" if self.paused or self.game_logic.add_steps_uses == 0 else "#FF69B4"
            )
    
    def set_blur_difficulty(self):
        """Set blur parameters based on difficulty level"""
        difficulty_value = self.difficulty.get()
        if difficulty_value == "Easy":
            self.blur_level = 5
            self.clear_radius = 150
        elif difficulty_value == "Medium":
            self.blur_level = 8
            self.clear_radius = 100
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
        if self.original_image is None or self.blurred_image is None:
            return
            
        try:
            # Create a copy of the blurred image
            self.current_display_image = self.blurred_image.copy()
            
            # Create a blank mask the same size as our image
            mask = Image.new('L', self.original_image.size, 0)
            
            # Draw a white circle at the cursor position
            draw = ImageDraw.Draw(mask)
            draw.ellipse(
                (x - self.clear_radius, y - self.clear_radius, 
                 x + self.clear_radius, y + self.clear_radius), 
                fill=255
            )
            
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
        elif difficulty_value == "Medium":
            self.time_left = 60  # 1:00
        else:  # Hard
            self.time_left = 30  # 0:30
        
        self.total_time = self.time_left#  Store it for dynamic blur scaling
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
                  self.game_image = ImageTk.PhotoImage(self.original_image)
                  self.game_canvas.itemconfig(self.image_on_canvas, image=self.game_image)

                  self.game_logic.highlight_chameleons_red()
                  self.show_message("Time's up! You missed some chameleons!", False)
                  self.game_logic.found = True

             if self.sound_on:
                 self.gameover_sound.play()
             messagebox.showinfo("Time's Up!", "Time's up! Game over.")


    def show_message_in_game(self, message):
        """Show a temporary message in the game area"""
        self.top_left_message.config(text=message)
        self.top_left_message.after(3000, lambda: self.top_left_message.config(text=""))

    def show_message(self, msg, success):
        """Show a message in the feedback label"""
        if hasattr(self, 'feedback') and self.feedback and self.feedback.winfo_exists():
            if success:
                self.feedback.config(text=msg, fg="#008000")
            else:
                self.feedback.config(text=msg, fg="#FF0000")

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