import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import random

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
        self.add_time_uses = 0  
        self.add_steps_uses = 0  
        self.points = 0

    def reset_game(self):
        self.found = False
        self.attempts = 0
        if self.circle_id:
            self.ui.game_canvas.delete(self.circle_id)
            self.circle_id = None
        margin = 50
        self.chameleon_x = random.randint(margin, self.img_width - margin)
        self.chameleon_y = random.randint(margin, self.img_height - margin)
        difficulty = self.ui.difficulty.get()
        if difficulty == "Easy":
            self.click_radius = 50
            self.max_attempts = 8
        elif difficulty == "Medium":
            self.click_radius = 30
            self.max_attempts = 5
        else:
            self.click_radius = 15
            self.max_attempts = 3

    def use_add_time(self):
        if self.add_time_uses <= 0 or self.found or not self.ui.timer_running:
            return
        self.add_time_uses -= 1
        difficulty = self.ui.difficulty.get()
        time_to_add = 15 if difficulty == "Easy" else 10 if difficulty == "Medium" else 5
        self.ui.time_left += time_to_add
        self.ui.update_timer_display()
        self.ui.show_message_in_game(f"+ {time_to_add} seconds")
        self.ui.update_points_display()
        self.ui.update_powerup_buttons()

    def use_add_steps(self):
        if self.add_steps_uses <= 0 or self.found:
            return
        self.add_steps_uses -= 1
        steps_to_add = 2 if self.ui.difficulty.get() == "Easy" else 1
        self.max_attempts += steps_to_add
        self.ui.show_message_in_game(f"+ {steps_to_add} steps")
        self.ui.update_points_display()
        self.ui.update_powerup_buttons()

    def handle_click(self, event):
        if self.found or self.ui.paused:
            return
        x, y = event.x, event.y
        distance = ((x - self.chameleon_x) ** 2 + (y - self.chameleon_y) ** 2) ** 0.5
        if distance <= self.click_radius:
            self.found = True
            self.circle_id = self.ui.game_canvas.create_oval(
                self.chameleon_x - self.click_radius, 
                self.chameleon_y - self.click_radius,
                self.chameleon_x + self.click_radius, 
                self.chameleon_y + self.click_radius,
                outline="green", width=3
            )
            if self.ui.timer_running:
                self.ui.stop_timer()
            self.ui.points += 20
            self.ui.show_message("You found the chameleon! Great job!", True)
            self.ui.update_points_display()
            self.ui.toggle_shop_menu()
        else:
            self.attempts += 1
            attempts_left = self.max_attempts - self.attempts
            if attempts_left <= 0:
                self.circle_id = self.ui.game_canvas.create_oval(
                    self.chameleon_x - self.click_radius, 
                    self.chameleon_y - self.click_radius,
                    self.chameleon_x + self.click_radius, 
                    self.chameleon_y + self.click_radius,
                    outline="red", width=3
                )
                self.ui.show_message("Game over! The chameleon was here!", False)
                if self.ui.timer_running:
                    self.ui.stop_timer()
                self.ui.toggle_shop_menu()
            else:
                if distance < 50:
                    self.ui.points += 10
                    self.ui.update_points_display()
                hint = "Very close! " if distance < 100 else "Getting warmer! " if distance < 200 else ""
                self.ui.show_message(f"{hint}Keep looking! {attempts_left} attempts left.", False)

class GameUI:
    def __init__(self, window):
        self.window = window
        self.window.title("Chameleon Hunt")
        self.window.geometry("800x600")
        self.window.configure(bg="#ADD8E6")
        self.image_file = None
        self.difficulty = tk.StringVar(value="Medium")
        self.paused = False
        self.timer_running = False
        self.time_left = 0
        self.timer_id = None
        self.points = 0
        self.shop_visible = False
        
        self.frame = tk.Frame(self.window, bg="#ADD8E6")
        self.frame.pack(expand=True, fill="both")
        
        self.game_logic = GameLogic(self)
        self.make_start_screen()

    def make_start_screen(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        title_frame = tk.Frame(self.frame, bg="#ADD8E6")
        title_frame.pack(pady=30)
        tk.Label(title_frame, text="Chameleon Hunt", font=("Arial", 36, "bold"), fg="#800080", bg="#ADD8E6").pack()
        tk.Label(title_frame, text="Can you find the sneaky chameleon?", font=("Arial", 14, "italic"), fg="#008000", bg="#ADD8E6").pack(pady=5)
        tk.Label(title_frame, text="🦎", font=("Arial", 30), fg="#008000", bg="#ADD8E6").pack(pady=10)
        upload_btn = tk.Button(self.frame, text="Upload Image", command=self.upload_pic, bg="#FFFF00", fg="black", font=("Arial", 18, "bold"), relief="raised")
        upload_btn.pack(pady=15, ipadx=30, ipady=15)
        upload_btn.bind("<Enter>", lambda e: upload_btn.config(bg="#FFD700"))
        upload_btn.bind("<Leave>", lambda e: upload_btn.config(bg="#FFFF00"))
        tk.Label(self.frame, text="Pick Difficulty:", font=("Arial", 16, "bold"), bg="#ADD8E6", fg="#800080").pack(pady=10)
        diff_colors = {"Easy": "#DDA0DD", "Medium": "#BA55D3", "Hard": "#9932CC"}
        for d in ["Easy", "Medium", "Hard"]:
            tk.Radiobutton(self.frame, text=d, value=d, variable=self.difficulty, font=("Arial", 14), bg="#ADD8E6", fg=diff_colors[d], selectcolor="#ADD8E6").pack()
        start_btn = tk.Button(self.frame, text="Start Game", command=self.start_game, bg="#FFFF00", fg="black", font=("Arial", 18, "bold"), relief="raised")
        start_btn.pack(pady=20, ipadx=30, ipady=15)
        start_btn.bind("<Enter>", lambda e: start_btn.config(bg="#FFD700"))
        start_btn.bind("<Leave>", lambda e: start_btn.config(bg="#FFFF00"))
        self.feedback = tk.Label(self.frame, text="", font=("Arial", 16), bg="#ADD8E6", fg="#FF0000")
        self.feedback.pack(pady=15)

    def upload_pic(self):
        file = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file:
            self.image_file = file
            self.feedback.config(text="Image loaded! Ready to hunt!", fg="#008000")
        else:
            self.feedback.config(text="No image picked.", fg="#FF0000")

    def start_game(self):
        if not self.image_file:
            messagebox.showerror("Error", "Upload an image first!")
            return
        if self.shop_visible:
            self.toggle_shop_menu()
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.paused = False
        self.game_canvas = tk.Canvas(self.frame, bg="white", highlightthickness=2, highlightbackground="#00CED1")
        self.game_canvas.pack(side=tk.LEFT, fill="both", expand=True)
        self.timer_frame = tk.Frame(self.frame, bg="#ADD8E6")
        self.timer_frame.pack(before=self.game_canvas, pady=5)
        self.timer_display = tk.Label(self.timer_frame, text="Time: 0:00", font=("Arial", 18, "bold"), bg="#ADD8E6", fg="#FF5733")
        self.timer_display.pack(padx=10)
        self.points_display = tk.Label(self.timer_frame, text=f"Points: {self.points}", font=("Arial", 14), bg="#ADD8E6", fg="#0000FF")
        self.points_display.pack(padx=10)
        self.powerup_frame = tk.Frame(self.frame, bg="#ADD8E6")
        self.powerup_frame.pack(before=self.game_canvas, pady=5)
        self.button_frame = tk.Frame(self.frame, bg="#ADD8E6")
        self.button_frame.pack(before=self.game_canvas, pady=5)
        shop_btn = tk.Button(self.frame, text="$", command=self.toggle_shop_menu, bg="#FFD700", fg="black", font=("Arial", 24, "bold"), relief="raised", width=2, height=1)  # Bigger icon
        shop_btn.place(x=750, y=10)  
        self.set_timer_difficulty()
        self.start_timer()
        self.feedback = tk.Label(self.frame, text="Click anywhere on the image!", font=("Arial", 16), bg="#ADD8E6", fg="#800080")
        self.feedback.pack(pady=15)
        try:
            img = Image.open(self.image_file)
            img.thumbnail((800, 600))
            self.game_image = ImageTk.PhotoImage(img)
            self.game_canvas.create_image(0, 0, image=self.game_image, anchor="nw")
            self.game_logic.img_width, self.game_logic.img_height = img.size
            self.game_logic.reset_game()
            self.create_powerup_buttons()
            self.create_game_buttons()
            self.game_canvas.bind("<Button-1>", self.game_logic.handle_click)
        except Exception as e:
            messagebox.showerror("Error", f"Image didn't load: {e}")
            self.replay()

    def create_powerup_buttons(self):
        self.top_left_message = tk.Label(self.frame, text="", font=("Arial", 14, "bold"), bg="#ADD8E6", fg="#800080")
        self.top_left_message.place(x=10, y=10)
        
        self.add_time_btn = tk.Button(self.powerup_frame, text="Use Add Time", command=self.game_logic.use_add_time, 
                                    bg="#32CD32", fg="black", font=("Arial", 12, "bold"), relief="raised")
        self.add_time_btn.pack(side="left", padx=5)
        self.add_time_btn.bind("<Enter>", lambda e: self.add_time_btn.config(bg="#228B22"))
        self.add_time_btn.bind("<Leave>", lambda e: self.add_time_btn.config(bg="#32CD32"))
        
        self.add_steps_btn = tk.Button(self.powerup_frame, text="Use Add Steps", command=self.game_logic.use_add_steps, 
                                     bg="#FF69B4", fg="black", font=("Arial", 12, "bold"), relief="raised")
        self.add_steps_btn.pack(side="left", padx=5)
        self.add_steps_btn.bind("<Enter>", lambda e: self.add_steps_btn.config(bg="#FF1493"))
        self.add_steps_btn.bind("<Leave>", lambda e: self.add_steps_btn.config(bg="#FF69B4"))

    def create_game_buttons(self):
        self.pause_btn = tk.Button(self.button_frame, text="Pause", command=self.toggle_pause, bg="#FFA500", fg="black", font=("Arial", 12, "bold"), relief="raised")
        self.pause_btn.pack(side="left", padx=5)
        self.pause_btn.bind("<Enter>", lambda e: self.pause_btn.config(bg="#FF8C00"))
        self.pause_btn.bind("<Leave>", lambda e: self.pause_btn.config(bg="#FFA500"))
        self.main_menu_btn = tk.Button(self.button_frame, text="Main Menu", command=self.return_to_main_menu, bg="#00CED1", fg="black", font=("Arial", 12, "bold"), relief="raised")
        self.main_menu_btn.pack(side="left", padx=5)
        self.main_menu_btn.bind("<Enter>", lambda e: self.main_menu_btn.config(bg="#00B7EB"))
        self.main_menu_btn.bind("<Leave>", lambda e: self.main_menu_btn.config(bg="#00CED1"))
        replay_btn = tk.Button(self.button_frame, text="Replay", command=self.replay, bg="#FFFF00", fg="black", font=("Arial", 12, "bold"), relief="raised")
        replay_btn.pack(side="left", padx=5)
        replay_btn.bind("<Enter>", lambda e: replay_btn.config(bg="#FFD700"))
        replay_btn.bind("<Leave>", lambda e: replay_btn.config(bg="#FFFF00"))

    def toggle_pause(self):
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
            if hasattr(self, 'pause_overlay'):
                self.pause_overlay.destroy()
            self.game_canvas.bind("<Button-1>", self.game_logic.handle_click)
        self.update_powerup_buttons()

    def update_powerup_buttons(self):
        time_state = "normal" if self.game_logic.add_time_uses > 0 and not self.paused and not self.game_logic.found and self.timer_running else "disabled"
        steps_state = "normal" if self.game_logic.add_steps_uses > 0 and not self.paused and not self.game_logic.found else "disabled"
        
        self.add_time_btn.config(state=time_state, text=f"Use Add Time [{self.game_logic.add_time_uses}]", bg="#32CD32" if time_state == "normal" else "#A9A9A9")
        self.add_steps_btn.config(state=steps_state, text=f"Use Add Steps [{self.game_logic.add_steps_uses}]", bg="#FF69B4" if steps_state == "normal" else "#A9A9A9")
        self.points_display.config(text=f"Points: {self.points}")

    def return_to_main_menu(self):
        if self.timer_id:
            self.window.after_cancel(self.timer_id)
        self.timer_running = False
        self.paused = False
        if self.shop_visible:
            self.toggle_shop_menu()
        self.image_file = None
        self.make_start_screen()
        self.game_logic = GameLogic(self)

    def toggle_shop_menu(self):
        if self.shop_visible:
            if hasattr(self, 'shop_frame'):
                self.shop_frame.destroy()
            self.shop_visible = False
        else:
            self.shop_visible = True
            self.shop_frame = tk.Frame(self.frame, bg="#ADD8E6", width=200)
            self.shop_frame.pack(side=tk.LEFT, fill="y")
            tk.Label(self.shop_frame, text="Shop", font=("Arial", 14, "bold"), bg="#ADD8E6").pack(pady=5)
            tk.Label(self.shop_frame, text=f"Points: {self.points}", font=("Arial", 12), bg="#ADD8E6").pack(pady=5)
            if self.points >= 20:
                buy_time_btn = tk.Button(self.shop_frame, text="Buy Add Time (20 pts)", command=lambda: self.buy_powerup("time"), 
                                       bg="#32CD32", fg="black", font=("Arial", 10, "bold"))
                buy_time_btn.pack(pady=5)
            else:
                tk.Label(self.shop_frame, text="Add Time (20 pts) - Insufficient Points", fg="red", bg="#ADD8E6").pack(pady=5)
            if self.points >= 15:
                buy_steps_btn = tk.Button(self.shop_frame, text="Buy Add Steps (15 pts)", command=lambda: self.buy_powerup("steps"), 
                                        bg="#FF69B4", fg="black", font=("Arial", 10, "bold"))
                buy_steps_btn.pack(pady=5)
            else:
                tk.Label(self.shop_frame, text="Add Steps (15 pts) - Insufficient Points", fg="red", bg="#ADD8E6").pack(pady=5)
            tk.Button(self.shop_frame, text="Close", command=self.toggle_shop_menu, bg="#FFA500", fg="black", font=("Arial", 10)).pack(pady=5)

    def buy_powerup(self, powerup_type):
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

    def show_message_in_game(self, message):
        self.top_left_message.config(text=message)
        self.top_left_message.after(3000, lambda: self.top_left_message.config(text=""))

    def show_message(self, msg, success):
        self.feedback.config(text=msg, fg="#008000" if success else "#FF0000")

    def set_timer_difficulty(self):
        difficulty = self.difficulty.get()
        self.time_left = 90 if difficulty == "Easy" else 60 if difficulty == "Medium" else 30
        self.update_timer_display()

    def update_timer_display(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        color = "#32CD32" if self.time_left > 20 else "#FFA500" if self.time_left > 10 else "#FF0000"
        self.timer_display.config(text=f"Time: {minutes}:{seconds:02d}", fg=color)

    def start_timer(self):
        if self.paused:
            return
        self.timer_running = True
        self.tick_timer()

    def stop_timer(self):
        self.timer_running = False
        if self.timer_id:
            self.window.after_cancel(self.timer_id)
            self.timer_id = None

    def tick_timer(self):
        if self.timer_running and self.time_left > 0:
            self.time_left -= 1
            self.update_timer_display()
            self.timer_id = self.window.after(1000, self.tick_timer)
        elif self.timer_running and self.time_left <= 0:
            self.timer_running = False
            self.timer_display.config(text="Time's Up!", fg="#FF0000")
            if not self.game_logic.found:
                self.game_logic.circle_id = self.game_canvas.create_oval(
                    self.game_logic.chameleon_x - self.game_logic.click_radius, 
                    self.game_logic.chameleon_y - self.click_radius,
                    self.game_logic.chameleon_x + self.click_radius, 
                    self.game_logic.chameleon_y + self.click_radius,
                    outline="red", width=3
                )
                self.show_message("Time's up! The chameleon was here!", False)
                self.game_logic.found = True
            self.toggle_shop_menu()

    def replay(self):
        if self.timer_id:
            self.window.after_cancel(self.timer_id)
        self.timer_running = False
        self.paused = False
        if self.shop_visible:
            self.toggle_shop_menu()
        self.start_game()

    def update_points_display(self):
        self.points_display.config(text=f"Points: {self.points}")

if __name__ == "__main__":
    window = tk.Tk()
    game = GameUI(window)
    window.mainloop()