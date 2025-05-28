import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter
import random
import numpy as np

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
        self.clear_radius = 100  # Radius of clear area
        self.blur_level = 5  # Blur intensity
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.initial_clear_radius = self.clear_radius  # To store initial radius for dynamic change
        
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
        
        # Create feedback label
        self.feedback = tk.Label(self.frame, text="", font=("Arial", 16), bg="#ADD8E6", fg="#FF0000")
        self.feedback.pack(pady=15)

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
        self.initial_clear_radius = self.clear_radius  # Save initial clear radius for dynamic adjustments
        
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
            self.replay()
    
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
            
            # Draw a white circle at the cursor position with current clear_radius
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
        elif difficulty_value == "Medium":
            self.time_left = 60  # 1:00
        else:  # Hard
            self.time_left = 30  # 0:30
        
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

            # Dynamically decrease clear_radius proportional to time left
            # The clear radius decreases from initial_clear_radius down to a min of 20 pixels linearly over the time
            min_radius = 20
            total_time = 0
            if self.difficulty.get() == "Easy":
                total_time = 90
            elif self.difficulty.get() == "Medium":
                total_time = 60
            else:
                total_time = 30
            ratio = max(self.time_left / total_time, 0)
            self.clear_radius = int(min_radius + (self.initial_clear_radius - min_radius) * ratio)

            self.update_timer_display()
            # Refresh blur with new clear radius to reflect change immediately
            self.apply_dynamic_blur(self.last_mouse_x, self.last_mouse_y)

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

    def replay(self):
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
        self.make_start_screen()
        self.game_logic = GameLogic(self)


# Run the game
if __name__ == "__main__":
    window = tk.Tk()
    game = GameUI(window)
    window.mainloop()

