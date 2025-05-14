
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from game_functions import GameLogic

class GameUI:
    def __init__(self, window):
        self.window = window
        self.window.title("Chameleon Hunt")
        self.window.geometry("800x600") 
        self.image_file = None
        self.difficulty = tk.StringVar(value="Medium")
        self.bg_label = None
       
        # background color 
        self.window.configure(bg="#ADD8E6")
        
        # main frame
        self.frame = tk.Frame(self.window, bg="#ADD8E6")
        self.frame.pack(expand=True, fill="both")
        
        # background image
        try:
            bg_img = Image.open("jungle_bg.jpg")  
            bg_img = bg_img.resize((800, 600), Image.Resampling.LANCZOS)
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
        
        self.feedback = tk.Label(self.frame, text="", font=("Arial", 16), bg="#ADD8E6", fg="#FF0000")
        self.feedback.pack(pady=15)
        
        # Load the image
        try:
            img = Image.open(self.image_file)
            img.thumbnail((800, 600))
            self.game_image = ImageTk.PhotoImage(img)
            self.game_canvas.create_image(0, 0, image=self.game_image, anchor="nw")
            
            # Process the image in game logic
            self.game_logic.img_width, self.game_logic.img_height = img.size
            
            # Reset game state for new round
            self.game_logic.reset_game()
            
            # Feedback
            self.feedback.config(text="Click anywhere on the image!", fg="#800080")
            
            # Click event handler
            self.game_canvas.bind("<Button-1>", self.game_logic.handle_click)

            # Add replay button
            replay_btn = tk.Button(
                self.frame, 
                text="Replay", 
                command=self.replay, 
                bg="#FFFF00", 
                fg="black", 
                font=("Arial", 14, "bold"),
                relief="raised"
            )
            replay_btn.pack(pady=10, ipadx=20, ipady=10)
            replay_btn.bind("<Enter>", lambda e: self.animate_button(replay_btn, "#FFD700"))
            replay_btn.bind("<Leave>", lambda e: self.animate_button(replay_btn, "#FFFF00", shrink=True))

        except Exception as e:
            messagebox.showerror("Error", f"Image didn't load: {e}")
            self.replay()

    def show_message(self, msg, success):
        if hasattr(self, 'feedback') and self.feedback and self.feedback.winfo_exists():
            if success:
                self.feedback.config(text=msg, fg="#008000")
            else:
                self.feedback.config(text=msg, fg="#FF0000")

    def replay(self):
        self.image_file = None
        self.make_start_screen()
        self.game_logic = GameLogic(self)

# Run the game
if __name__ == "__main__":
    window = tk.Tk()
    game = GameUI(window)
    window.mainloop()