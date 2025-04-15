import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import math
import random

class GameUI:
    def __init__(self, window):
        self.window = window
        self.window.title("Chameleon Hunt")
        self.window.geometry("800x600")
        self.window.configure(bg="#ADD8E6")
         
        self.image_file = None
        self.difficulty = tk.StringVar(value="Medium")
        self.chameleon_x = 0
        self.chameleon_y = 0
        self.chameleon_radius = 30  # Radius used for click detection
        self.wrong_clicks = 0
        self.max_wrong_clicks = 5
        self.game_active = False

        # Create images directory if it doesn't exist
        if not os.path.exists("game_images"):
            os.makedirs("game_images")

        # Main frame
        self.frame = tk.Frame(self.window, bg="#ADD8E6")
        self.frame.pack(expand=True, fill="both")

        # Try loading background image
        try:
            bg_img = Image.open("jungle_bg.jpg")
            bg_img = bg_img.resize((800, 600), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_img)
            self.bg_label = tk.Label(self.frame, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            self.frame.configure(bg="#ADD8E6")

        # Game canvas and feedback
        self.game_canvas = tk.Canvas(self.frame, bg="white", highlightthickness=2, highlightbackground="#00CED1")
        self.game_image = None
        self.feedback = tk.Label(self.frame, text="", font=("Arial", 16), bg="#ADD8E6", fg="#FF0000")
        self.attempts_label = tk.Label(self.frame, text="", font=("Arial", 14), bg="#ADD8E6", fg="#FF5733")

        # Build start screen
        self.make_start_screen()

    # ------------------- UI COMPONENTS -------------------
    def make_start_screen(self):
        # clear the frame
        for thing in self.frame.winfo_children():
            if thing != getattr(self, "bg_label", None):  # Keep bg label if exists
                thing.destroy()

        # title frame 
        title_frame = tk.Frame(self.frame, bg="#ADD8E6")
        title_frame.pack(pady=30)
        
        # title
        title = tk.Label(title_frame, text="Chameleon Hunt", font=("Arial", 36, "bold"), fg="#800080", bg="#ADD8E6")
        title.pack()
        
        # welcome message
        welcome = tk.Label(title_frame, text="Can you find the sneaky chameleon?", font=("Arial", 14, "italic"), fg="#008000", bg="#ADD8E6")
        welcome.pack(pady=5)

        # chameleon icon
        chameleon_icon = tk.Label(title_frame, text="🦎", font=("Arial", 30), fg="#008000", bg="#ADD8E6")
        chameleon_icon.pack(pady=10)
        
        # upload button
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

        # Previous Images button
        if len(os.listdir("game_images")) > 0:
            prev_images_btn = tk.Button(
                self.frame,
                text="Use Previous Image",
                command=self.show_previous_images,
                bg="#98FB98",
                fg="black",
                font=("Arial", 16, "bold")
            )
            prev_images_btn.pack(pady=10)

        # difficulty label
        diff_label = tk.Label(self.frame, text="Pick Difficulty:", font=("Arial", 16, "bold"), bg="#ADD8E6", fg="#800080")
        diff_label.pack(pady=10)
        
        # difficulty options
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

        # start button
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
        
        # feedback label
        self.feedback = tk.Label(self.frame, text="", font=("Arial", 16), bg="#ADD8E6", fg="#FF0000")
        self.feedback.pack(pady=15)

    def animate_button(self, button, color, shrink=False):
        button.configure(bg=color)
        if shrink:
            button.configure(relief="raised")
        else:
            button.configure(relief="sunken")

    # ------------------- IMAGE UPLOAD & PREVIOUS IMAGES -------------------
    def upload_pic(self):
        self.image_file = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif;*.tiff;*.webp"),
                ("All files", "*.*")
            ]
        )
        if self.image_file:
            try:
                # Save to game_images folder without resizing
                img = Image.open(self.image_file)
                
                # Create a unique filename based on original
                base_filename = os.path.basename(self.image_file)
                saved_path = os.path.join("game_images", base_filename)
                
                # Save with original extension
                img.save(saved_path)
                
                messagebox.showinfo("Success", "Image uploaded successfully!")
                self.image_file = saved_path
                self.feedback.config(text="Image loaded! Ready to hunt!", fg="#008000")
            except Exception as e:
                messagebox.showerror("Error", f"Could not process image: {str(e)}")
        else:
            self.feedback.config(text="No image picked.", fg="#FF0000")

    def show_previous_images(self):
        images = os.listdir("game_images")
        if not images:
            messagebox.showinfo("No Images", "No previous images found.")
            return
            
        # Create a new window to display image thumbnails
        img_window = tk.Toplevel(self.window)
        img_window.title("Previous Images")
        img_window.geometry("600x400")
        
        # Create a frame with scrollbar
        frame = tk.Frame(img_window)
        frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(frame)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add images to the scrollable frame
        self.thumbnails = []  # Store references to prevent garbage collection
        for i, img_name in enumerate(images):
            try:
                img_path = os.path.join("game_images", img_name)
                img = Image.open(img_path)
                img.thumbnail((100, 100))
                
                photo = ImageTk.PhotoImage(img)
                self.thumbnails.append(photo)
                
                btn = tk.Button(
                    scrollable_frame,
                    image=photo,
                    text=img_name,
                    compound="top",
                    command=lambda path=img_path: self.select_previous_image(path, img_window)
                )
                btn.grid(row=i//3, column=i%3, padx=10, pady=10)
            except Exception as e:
                print(f"Error loading {img_name}: {str(e)}")
    
    def select_previous_image(self, image_path, window):
        window.destroy()
        self.image_file = image_path
        self.feedback.config(text="Image loaded! Ready to hunt!", fg="#008000")

    # ------------------- GAME START -------------------
    def start_game(self):
        if not self.image_file:
            messagebox.showerror("Error", "Upload an image first!")
            return
            
        self.clear_screen()
        self.wrong_clicks = 0
        self.game_active = True
        self.current_image_path = self.image_file

        # Load the image to get dimensions
        try:
            self.original_img = Image.open(self.image_file)
            self.img_width, self.img_height = self.original_img.size
            
            # Determine the best window size based on the image and screen
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            
            # Calculate max dimensions (leaving space for game UI elements)
            max_width = min(screen_width - 50, self.img_width)
            max_height = min(screen_height - 150, self.img_height)
            
            # Calculate window dimensions with padding for UI elements
            window_width = max_width + 20
            window_height = max_height + 100  # Extra space for controls
            
            # Resize the window to match the image with UI space
            self.window.geometry(f"{window_width}x{window_height}")
            
            # Create game frame
            game_frame = tk.Frame(self.frame)
            game_frame.pack(expand=True, fill="both", padx=10, pady=10)
            
            # Create canvas for the image
            self.game_canvas = tk.Canvas(
                game_frame,
                width=max_width,
                height=max_height,
                bg="white",
                highlightthickness=2,
                highlightbackground="#00CED1"
            )
            self.game_canvas.pack(expand=True)
            
            # Display the image at original resolution
            self.game_image = ImageTk.PhotoImage(self.original_img)
            self.image_id = self.game_canvas.create_image(
                max_width/2,  # Center the image
                max_height/2,
                anchor="center",
                image=self.game_image
            )
            
            # Status area
            status_frame = tk.Frame(self.frame, bg="#ADD8E6")
            status_frame.pack(fill="x", pady=5)
            
            self.feedback = tk.Label(status_frame, text="Find the chameleon!", font=("Arial", 16), bg="#ADD8E6", fg="#FF0000")
            self.feedback.pack(side="left", padx=20)
            
            self.attempts_label = tk.Label(status_frame, text=f"Attempts left: {self.max_wrong_clicks}", font=("Arial", 14), bg="#ADD8E6", fg="#FF5733")
            self.attempts_label.pack(side="right", padx=20)
            
            # Quit button
            quit_btn = tk.Button(self.frame, text="Back to Menu", command=self.make_start_screen, bg="#FF6B6B", fg="white")
            quit_btn.pack(pady=5)
            
            # Place chameleon in a random position
            self.chameleon_x = random.randint(50, self.img_width - 50)
            self.chameleon_y = random.randint(50, self.img_height - 50)
            
            # Adjust radius based on difficulty
            if self.difficulty.get() == "Easy":
                self.chameleon_radius = 50
                self.max_wrong_clicks = 7
            elif self.difficulty.get() == "Medium":
                self.chameleon_radius = 30
                self.max_wrong_clicks = 5
            else:  # Hard
                self.chameleon_radius = 20
                self.max_wrong_clicks = 3
            
            # Update attempts display
            self.attempts_label.config(text=f"Attempts left: {self.max_wrong_clicks}")
            
            # Hide the chameleon (it's invisible in the game)
            # The chameleon position is tracked but not drawn visibly
            
            # Bind click event
            self.game_canvas.bind("<Button-1>", self.handle_click)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load game image: {str(e)}")
            self.make_start_screen()

    def clear_screen(self):
        for thing in self.frame.winfo_children():
            if thing != getattr(self, "bg_label", None):
                thing.destroy()

    # ------------------- GAME LOGIC -------------------
    def handle_click(self, event):
        if not self.game_active:
            return
        
        # Get the canvas coordinates
        canvas_x = event.x
        canvas_y = event.y
        
        # Convert canvas coordinates to image coordinates
        # Calculate the offset for the centered image
        canvas_width = self.game_canvas.winfo_width()
        canvas_height = self.game_canvas.winfo_height()
        
        # Calculate offsets if image is smaller or larger than canvas
        x_offset = (canvas_width - self.img_width) / 2 if canvas_width > self.img_width else 0
        y_offset = (canvas_height - self.img_height) / 2 if canvas_height > self.img_height else 0
        
        # Adjust mouse position to image coordinates
        img_x = canvas_x - x_offset
        img_y = canvas_y - y_offset
        
        # Calculate distance to chameleon
        dx = img_x - self.chameleon_x
        dy = img_y - self.chameleon_y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < self.chameleon_radius:
            self.feedback.config(text="You found the chameleon! 🎉")
            self.game_active = False
            
            # Show chameleon location
            chameleon_canvas_x = self.chameleon_x + x_offset
            chameleon_canvas_y = self.chameleon_y + y_offset
            self.game_canvas.create_oval(
                chameleon_canvas_x - self.chameleon_radius,
                chameleon_canvas_y - self.chameleon_radius,
                chameleon_canvas_x + self.chameleon_radius,
                chameleon_canvas_y + self.chameleon_radius,
                outline="#00FF00",
                width=3
            )
            
            # Show win dialog with option to play again
            self.show_game_end_dialog(True)
        else:
            self.wrong_clicks += 1
            attempts_left = self.max_wrong_clicks - self.wrong_clicks
            self.attempts_label.config(text=f"Attempts left: {attempts_left}")
            
            # Add X mark at wrong click location
            self.game_canvas.create_text(
                canvas_x,
                canvas_y,
                text="✗",
                fill="#FF0000",
                font=("Arial", 16, "bold")
            )
            
            if attempts_left <= 0:
                self.feedback.config(text="Game Over! You ran out of attempts.")
                self.game_active = False
                
                # Show where chameleon was
                chameleon_canvas_x = self.chameleon_x + x_offset
                chameleon_canvas_y = self.chameleon_y + y_offset
                
                self.game_canvas.create_oval(
                    chameleon_canvas_x - self.chameleon_radius,
                    chameleon_canvas_y - self.chameleon_radius,
                    chameleon_canvas_x + self.chameleon_radius,
                    chameleon_canvas_y + self.chameleon_radius,
                    outline="#FF0000",
                    width=3
                )
                
                self.game_canvas.create_text(
                    chameleon_canvas_x,
                    chameleon_canvas_y - self.chameleon_radius - 10,
                    text="Chameleon was here!",
                    fill="#FF0000",
                    font=("Arial", 12, "bold")
                )
                
                self.show_game_end_dialog(False)
            else:
                # Give feedback based on distance
                distance_percent = distance / max(self.img_width, self.img_height)
                
                if distance_percent < 0.1:
                    self.feedback.config(text="Very hot! You're close!")
                elif distance_percent < 0.2:
                    self.feedback.config(text="Getting warmer!")
                elif distance_percent < 0.3:
                    self.feedback.config(text="Lukewarm...")
                else:
                    self.feedback.config(text="Cold. Try another area.")

    def show_game_end_dialog(self, win):
        result_window = tk.Toplevel(self.window)
        result_window.title("Game Result")
        result_window.geometry("300x200")
        
        if win:
            result_text = "Congratulations! You found the chameleon!"
            color = "#4CAF50"
        else:
            result_text = "Game Over! You ran out of attempts."
            color = "#F44336"
            
        tk.Label(
            result_window, 
            text=result_text, 
            font=("Arial", 14), 
            fg="white", 
            bg=color,
            wraplength=280
        ).pack(pady=20, fill="x")
        
        button_frame = tk.Frame(result_window)
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Play Again",
            command=lambda: [result_window.destroy(), self.start_game()]
        ).pack(side="left", padx=10)
        
        tk.Button(
            button_frame,
            text="Main Menu",
            command=lambda: [result_window.destroy(), self.make_start_screen()]
        ).pack(side="right", padx=10)

    def replay(self):
        self.image_file = None
        self.game_canvas.delete("all")
        self.game_canvas.pack_forget()
        self.make_start_screen()

# ------------------- MAIN -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = GameUI(root)
    root.mainloop()