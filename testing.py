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
        self.zoom_factor = 1.0

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
        for thing in self.frame.winfo_children():
            if thing != getattr(self, "bg_label", None):  # Keep bg label if exists
                thing.destroy()

        title_frame = tk.Frame(self.frame, bg="#ADD8E6")
        title_frame.pack(pady=30)

        title = tk.Label(title_frame, text="Chameleon Hunt", font=("Arial", 36, "bold"), fg="#800080", bg="#ADD8E6")
        title.pack()

        welcome = tk.Label(title_frame, text="Can you find the sneaky chameleon?", font=("Arial", 14, "italic"), fg="#008000", bg="#ADD8E6")
        welcome.pack(pady=5)

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

        # Difficulty selector
        diff_label = tk.Label(self.frame, text="Pick Difficulty:", font=("Arial", 16, "bold"), bg="#ADD8E6", fg="#800080")
        diff_label.pack(pady=10)

        for d in ["Easy", "Medium", "Hard"]:
            tk.Radiobutton(
                self.frame,
                text=d,
                value=d,
                variable=self.difficulty,
                font=("Arial", 14),
                bg="#ADD8E6",
                fg={"Easy": "#DDA0DD", "Medium": "#BA55D3", "Hard": "#9932CC"}[d],
                selectcolor="#ADD8E6"
            ).pack()

    def animate_button(self, button, color, shrink=False):
        button.configure(bg=color)

    # ------------------- IMAGE UPLOAD & START GAME -------------------
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
                self.start_game(saved_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not process image: {str(e)}")

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
        self.start_game(image_path)

    # ------------------- GAME START -------------------
    def start_game(self, image_path):
        self.clear_screen()
        self.wrong_clicks = 0
        self.game_active = True
        self.current_image_path = image_path
        self.zoom_factor = 1.0

        # Create a scrollable canvas for full resolution images
        container = tk.Frame(self.frame)
        container.pack(fill="both", expand=True)
        
        # Create scrollbars
        h_scrollbar = tk.Scrollbar(container, orient="horizontal")
        v_scrollbar = tk.Scrollbar(container, orient="vertical")
        
        # Create canvas with scrollbars
        self.game_canvas = tk.Canvas(
            container, 
            bg="white",
            highlightthickness=2, 
            highlightbackground="#00CED1",
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set
        )
        
        # Configure scrollbars
        h_scrollbar.config(command=self.game_canvas.xview)
        v_scrollbar.config(command=self.game_canvas.yview)
        
        # Pack scrollbars and canvas
        h_scrollbar.pack(side="bottom", fill="x")
        v_scrollbar.pack(side="right", fill="y")
        self.game_canvas.pack(side="left", fill="both", expand=True)
        
        # Control panel for zoom
        control_frame = tk.Frame(self.frame, bg="#ADD8E6")
        control_frame.pack(fill="x", pady=5)
        
        # Zoom controls
        zoom_frame = tk.Frame(control_frame, bg="#ADD8E6")
        zoom_frame.pack(side="left", padx=10)
        
        tk.Label(zoom_frame, text="Zoom:", bg="#ADD8E6").pack(side="left")
        
        zoom_out_btn = tk.Button(zoom_frame, text="-", command=lambda: self.zoom_image(0.8))
        zoom_out_btn.pack(side="left", padx=2)
        
        zoom_reset_btn = tk.Button(zoom_frame, text="Fit", command=self.fit_image_to_canvas)
        zoom_reset_btn.pack(side="left", padx=2)
        
        zoom_in_btn = tk.Button(zoom_frame, text="+", command=lambda: self.zoom_image(1.2))
        zoom_in_btn.pack(side="left", padx=2)
        
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

        # Load and display image
        try:
            self.original_img = Image.open(image_path)
            self.img_width, self.img_height = self.original_img.size
            
            # Load initial image
            self.update_image()
            
            # Configure canvas for resize events
            self.game_canvas.bind("<Configure>", self.on_canvas_resize)
            
            # Place chameleon in a random position
            self.chameleon_x = random.randint(50, self.img_width - 50)
            self.chameleon_y = random.randint(50, self.img_height - 50)
            
            # Adjust radius based on difficulty
            if self.difficulty.get() == "Easy":
                self.chameleon_radius = 50
            elif self.difficulty.get() == "Medium":
                self.chameleon_radius = 30
            else:  # Hard
                self.chameleon_radius = 20
            
            # Draw chameleon directly on canvas
            self.update_chameleon()
            
            # Bind click event and mouse wheel
            self.game_canvas.bind("<Button-1>", self.handle_click)
            self.game_canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows
            self.game_canvas.bind("<Button-4>", self.on_mousewheel)    # Linux scroll up
            self.game_canvas.bind("<Button-5>", self.on_mousewheel)    # Linux scroll down
            
            # Fit image to canvas initially
            self.window.update_idletasks()  # Let the window update first
            self.fit_image_to_canvas()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load game image: {str(e)}")
            self.make_start_screen()

    def update_image(self):
        """Update the displayed image based on zoom factor"""
        if not hasattr(self, 'original_img'):
            return
            
        # Calculate new dimensions
        new_width = int(self.img_width * self.zoom_factor)
        new_height = int(self.img_height * self.zoom_factor)
        
        # Resize image (only if dimensions are positive)
        if new_width > 0 and new_height > 0:
            resized_img = self.original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.game_image = ImageTk.PhotoImage(resized_img)
            
            # Clear canvas and display image
            self.game_canvas.delete("all")
            self.image_id = self.game_canvas.create_image(0, 0, anchor="nw", image=self.game_image)
            
            # Configure scrollregion
            self.game_canvas.config(scrollregion=(0, 0, new_width, new_height))
            
            # Update chameleon position
            self.update_chameleon()

    def update_chameleon(self):
        """Draw the chameleon on the canvas"""
        scaled_x = self.chameleon_x * self.zoom_factor
        scaled_y = self.chameleon_y * self.zoom_factor
        
        # Delete previous chameleon if exists
        self.game_canvas.delete("chameleon")
        
        # Draw chameleon as a text object
        self.chameleon_id = self.game_canvas.create_text(
            scaled_x, 
            scaled_y,
            text="🦎", 
            font=("Arial", int(20 * self.zoom_factor)),
            fill="green",
            tags=("chameleon",)
        )

    def fit_image_to_canvas(self):
        """Fit the image to the visible canvas area"""
        # Get the current size of the canvas (visible area)
        canvas_width = self.game_canvas.winfo_width()
        canvas_height = self.game_canvas.winfo_height()
        
        # If canvas hasn't been rendered yet, use approximate values
        if canvas_width <= 1:
            canvas_width = self.window.winfo_width() - 30  # Approximate for scrollbars
        if canvas_height <= 1:
            canvas_height = self.window.winfo_height() - 150  # Approximate for controls
        
        # Calculate zoom to fit
        width_ratio = canvas_width / self.img_width
        height_ratio = canvas_height / self.img_height
        
        # Use the smaller ratio to ensure whole image fits
        self.zoom_factor = min(width_ratio, height_ratio) * 0.9  # 90% to ensure margin
        
        # Update the image
        self.update_image()
        
        # Reset scroll position to top-left
        self.game_canvas.xview_moveto(0)
        self.game_canvas.yview_moveto(0)

    def zoom_image(self, factor):
        """Zoom in or out by a factor"""
        # Store current center of view
        canvas_width = self.game_canvas.winfo_width()
        canvas_height = self.game_canvas.winfo_height()
        
        view_x = self.game_canvas.canvasx(canvas_width/2)
        view_y = self.game_canvas.canvasy(canvas_height/2)
        
        # Calculate center as proportion of image
        center_x = view_x / (self.img_width * self.zoom_factor)
        center_y = view_y / (self.img_height * self.zoom_factor)
        
        # Apply zoom factor
        self.zoom_factor *= factor
        
        # Limit zoom range
        self.zoom_factor = max(0.1, min(5.0, self.zoom_factor))
        
        # Update image
        self.update_image()
        
        # Restore view to same center
        new_x = center_x * self.img_width * self.zoom_factor
        new_y = center_y * self.img_height * self.zoom_factor
        
        # Adjust scrollbars to keep same center
        self.game_canvas.xview_moveto(max(0, new_x - canvas_width/2) / (self.img_width * self.zoom_factor))
        self.game_canvas.yview_moveto(max(0, new_y - canvas_height/2) / (self.img_height * self.zoom_factor))

    def on_canvas_resize(self, event):
        """Handle canvas resize events"""
        if event.width > 1 and event.height > 1:
            # Only resize if this is the first real size update
            if not hasattr(self, 'last_canvas_width') or self.last_canvas_width <= 1:
                self.fit_image_to_canvas()
            
            self.last_canvas_width = event.width
            self.last_canvas_height = event.height

    def on_mousewheel(self, event):
        """Handle mousewheel events for zooming"""
        # Determine zoom direction based on event
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
            self.zoom_image(1.1)  # Zoom in
        elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            self.zoom_image(0.9)  # Zoom out

    def clear_screen(self):
        for thing in self.frame.winfo_children():
            if thing != getattr(self, "bg_label", None):
                thing.destroy()

    # ------------------- GAME LOGIC -------------------
    def handle_click(self, event):
        if not self.game_active:
            return
            
        # Get the canvas coordinates (accounting for scrolling)
        canvas_x = self.game_canvas.canvasx(event.x)
        canvas_y = self.game_canvas.canvasy(event.y)
        
        # Calculate distance to chameleon (scaled with zoom)
        scaled_chameleon_x = self.chameleon_x * self.zoom_factor
        scaled_chameleon_y = self.chameleon_y * self.zoom_factor
        scaled_radius = self.chameleon_radius * self.zoom_factor
        
        dx = canvas_x - scaled_chameleon_x
        dy = canvas_y - scaled_chameleon_y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < scaled_radius:
            self.feedback.config(text="You found the chameleon! 🎉")
            self.game_active = False
            
            # Show win dialog with option to play again
            self.show_game_end_dialog(True)
        else:
            self.wrong_clicks += 1
            attempts_left = self.max_wrong_clicks - self.wrong_clicks
            self.attempts_label.config(text=f"Attempts left: {attempts_left}")
            
            if attempts_left <= 0:
                self.feedback.config(text="Game Over! You ran out of attempts.")
                self.game_active = False
                self.show_game_end_dialog(False)
            else:
                self.feedback.config(text="Try again!")

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
            command=lambda: [result_window.destroy(), self.start_game(self.current_image_path)]
        ).pack(side="left", padx=10)
        
        tk.Button(
            button_frame,
            text="Main Menu",
            command=lambda: [result_window.destroy(), self.make_start_screen()]
        ).pack(side="right", padx=10)

# ------------------- MAIN -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = GameUI(root)
    root.mainloop()