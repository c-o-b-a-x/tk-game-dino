import tkinter as tk
import random

PLAYER_SIZE = 50
EMOJI_SIZE = 50
ROCK_SIZE = 50
COLLECTIBLE_COUNT = 10
INITIAL_MOVE_STEP = 10
SCORE_MULTIPLIER_INCREMENT = 10
SCORE_PER_DINO_INCREMENT = 5
SPEED_DOUBLE_THRESHOLD = 100
SECRET_SCORE_THRESHOLD = 1000
SECOND_SECRET_SCORE_THRESHOLD = 10000



class Game:
    def handle_death(self):
        self.player_lives -= 1
        self.display_death_message()
        if self.player_lives <= 0:
            self.game_over()
        else:
            self.reset_player_position()
            self.shake_screen()
    def __init__(self, master, player_image):
        self.master = master
        self.master.attributes('-fullscreen', True)
        self.master.bind("<Escape>", self.exit_fullscreen)
        self.master.bind("o", self.add_points)
        self.max_lives = 3  # Set the maximum number of lives
        self.player_lives = self.max_lives  # Initialize the player's lives

        self.canvas = tk.Canvas(master, bg="darkslategray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()

        self.player_image = player_image
        self.emoji_images = [self.load_image(f"images/dino_emoji{i + 1}.png") for i in range(3)]
        self.rock_image = self.load_image("images/rock.png")
        self.secret_image = self.load_image("images/secret.png")
        self.secret2_image = self.load_image("images/secret2.png")

        self.init_game_variables()
        self.setup_game_objects()

        self.master.bind("<KeyPress>", self.start_moving)
        self.master.bind("<KeyRelease>", self.stop_moving)
        self.update_score()
        self.update_bag_hud()
        self.move_player()

        self.secret_message_id = None
        self.secret2_message_id = None
        self.death_message_id = None

    def init_game_variables(self):
        self.collected_counts = {i: 0 for i in range(len(self.emoji_images))}
        self.total_collected = 0
        self.move_step = INITIAL_MOVE_STEP
        self.score_per_dino = SCORE_PER_DINO_INCREMENT
        self.score = 0
        self.player_lives = 1
        self.death_messages = [
            "Ouch! That rock was not a pet!",
            "Oops! I think I saw stars!",
            "I should've dodged that!",
            "Well, that was a smashing experience!",
            "Looks like I crumbled!",
            "That's not how you rock and roll!",
            "Game over, man! Game over!",
            "I've taken rock bottom to a whole new level!",
            "I can't believe I just got schooled by a rock!",
            "That was one hard lesson in gravity!",
            "Rock and roll? More like rock and fall!",
            "And I thought I'd never hit rock bottom!",
        ]
        self.secret_collected = False
        self.secret2_collected = False
        self.moving_direction = None



    def setup_game_objects(self):
        self.player = self.canvas.create_image(self.screen_width // 2, self.screen_height // 2, anchor=tk.CENTER, image=self.player_image)
        self.emojis = [self.create_emoji() for _ in range(COLLECTIBLE_COUNT)]
        self.rocks = [self.create_rock() for _ in range(10)]
        self.secret_item = None
        self.secret2_item = None


    def exit_fullscreen(self, event):
        self.master.attributes('-fullscreen', False)

    def add_points(self, event):
        self.score += 1000
        self.update_score()

    def load_image(self, file_name):
        try:
            return tk.PhotoImage(file=file_name)
        except tk.TclError:
            print(f"Error loading image: {file_name}")
            return None

    def create_emoji(self):
        x = random.randint(0, self.screen_width - EMOJI_SIZE)
        y = random.randint(0, self.screen_height - EMOJI_SIZE)
        emoji_image = random.choice(self.emoji_images)
        emoji = self.canvas.create_image(x, y, anchor=tk.NW, image=emoji_image)
        self.canvas.addtag_withtag(self.emoji_images.index(emoji_image), emoji)
        return emoji

    def create_rock(self):
        x = random.randint(0, self.screen_width - ROCK_SIZE)
        y = random.randint(0, self.screen_height - ROCK_SIZE)
        return self.canvas.create_image(x, y, anchor=tk.NW, image=self.rock_image)

    def spawn_secret_item(self):
        if self.secret_item is None and self.score >= SECRET_SCORE_THRESHOLD and not self.secret_collected:
            x = random.randint(0, self.screen_width - EMOJI_SIZE)
            y = random.randint(0, self.screen_height - EMOJI_SIZE)
            self.secret_item = self.canvas.create_image(x, y, anchor=tk.NW, image=self.secret_image)

    def spawn_secret2_item(self):
        if self.secret2_item is None and self.score >= SECOND_SECRET_SCORE_THRESHOLD and not self.secret2_collected:
            x = random.randint(0, self.screen_width - EMOJI_SIZE)
            y = random.randint(0, self.screen_height - EMOJI_SIZE)
            self.secret2_item = self.canvas.create_image(x, y, anchor=tk.NW, image=self.secret2_image)

    def start_moving(self, event):
        if event.keysym in ["Left", "Right", "Up", "Down", "a", "d", "w", "s"]:
            self.moving_direction = event.keysym

    def stop_moving(self, event):
        if event.keysym in ["Left", "Right", "Up", "Down", "a", "d", "w", "s"]:
            self.moving_direction = None

    def move_player(self):
        # Dynamically calculate move_step based on score
        dynamic_move_step = INITIAL_MOVE_STEP * (1 + self.score // SPEED_DOUBLE_THRESHOLD)
        dynamic_move_step = min(dynamic_move_step, INITIAL_MOVE_STEP * 6)  # Cap speed increase

        if self.moving_direction:
            movement = {
                "Left": (-dynamic_move_step, 0),
                "a": (-dynamic_move_step, 0),
                "Right": (dynamic_move_step, 0),
                "d": (dynamic_move_step, 0),
                "Up": (0, -dynamic_move_step),
                "w": (0, -dynamic_move_step),
                "Down": (0, dynamic_move_step),
                "s": (0, dynamic_move_step),
            }
            dx, dy = movement[self.moving_direction]
            self.canvas.move(self.player, dx, dy)

        self.check_bounds()
        self.check_collisions()
        self.spawn_secret_item()
        self.spawn_secret2_item()
        self.master.after(50, self.move_player)

    def check_bounds(self):
        player_coords = self.canvas.bbox(self.player)
        if player_coords:
            if player_coords[0] < 0:
                self.canvas.move(self.player, -player_coords[0], 0)
            elif player_coords[2] > self.screen_width:
                self.canvas.move(self.player, self.screen_width - player_coords[2], 0)
            if player_coords[1] < 0:
                self.canvas.move(self.player, 0, -player_coords[1])
            elif player_coords[3] > self.screen_height:
                self.canvas.move(self.player, 0, self.screen_height - player_coords[3])

    def check_collisions(self):
        player_coords = self.canvas.bbox(self.player)
        if player_coords is None:
            return 

        for emoji in self.emojis[:]:
            emoji_bbox = self.canvas.bbox(emoji)
            if emoji_bbox and self.rects_overlap(player_coords, emoji_bbox):
                self.collect_emoji(emoji)

        for rock in self.rocks:
            rock_bbox = self.canvas.bbox(rock)
            if rock_bbox and self.rects_overlap(player_coords, rock_bbox):
                self.handle_death()

        if self.secret_item is not None:
            secret_bbox = self.canvas.bbox(self.secret_item)
            if secret_bbox and self.rects_overlap(player_coords, secret_bbox):
                self.collect_secret_item()

        if self.secret2_item is not None:
            secret2_bbox = self.canvas.bbox(self.secret2_item)
            if secret2_bbox and self.rects_overlap(player_coords, secret2_bbox):
                self.collect_secret2_item()

    def collect_emoji(self, emoji):
        tags = self.canvas.gettags(emoji)
        emoji_index = int(tags[0]) if tags else None
        if emoji_index is not None:
            self.collected_counts[emoji_index] += 1
            self.total_collected += 1
            self.score += self.score_per_dino
            if self.total_collected % SCORE_MULTIPLIER_INCREMENT == 0:
                self.score_per_dino += SCORE_PER_DINO_INCREMENT

            self.canvas.delete(emoji)
            self.emojis.remove(emoji)
            self.update_score()
            self.update_bag_hud()
            self.emojis.append(self.create_emoji())

    def collect_secret_item(self):
        self.secret_collected = True
        self.score += 500
        self.canvas.delete(self.secret_item)
        self.secret_item = None
        self.update_score()
        self.add_secret_to_bag()

    def collect_secret2_item(self):
        self.secret2_collected = True
        self.score += 500
        self.canvas.delete(self.secret2_item)
        self.secret2_item = None
        self.update_score()
        self.add_secret2_to_bag()

    def add_secret_to_bag(self):
        secret_item = self.canvas.create_image(self.screen_width - 80, 40 + (len(self.collected_counts) * 60),
                                                anchor=tk.NW, image=self.secret_image)
        self.canvas.tag_bind(secret_item, "<Button-1>", self.display_secret_message)
        self.collected_counts[-1] = secret_item

    def add_secret2_to_bag(self):
        secret2_item = self.canvas.create_image(self.screen_width - 80, 40 + (len(self.collected_counts) * 60) + 60,
                                                 anchor=tk.NW, image=self.secret2_image)
        self.canvas.tag_bind(secret2_item, "<Button-1>", self.display_secret2_message)
        self.collected_counts[-2] = secret2_item

    def display_secret_message(self, event):
        if self.secret_message_id is not None:
            self.canvas.delete(self.secret_message_id)
            self.secret_message_id = None
            return

        message_text = (
            "This secret message has been delayed ill lyk when its ready"
            "\n part 2 kinda explains why (not detailed)"
        )
        self.secret_message_id = self.canvas.create_text(self.screen_width // 2, self.screen_height // 2,
                                                          text=message_text, font=("Helvetica", 36), fill="grey", width=self.screen_width - 100)

    def display_secret2_message(self, event):
        if self.secret2_message_id is not None:
            self.canvas.delete(self.secret2_message_id)
            self.secret2_message_id = None
            return

        message_text = (


            "The secret messages have been delayed until im done writing what I want to say"
        )
        
        self.secret2_message_id = self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 2,
            text=message_text, font=("Helvetica", 24), fill="grey", width=self.screen_width - 100
    )


    def reset_bag(self):
        self.collected_counts = {i: 0 for i in range(len(self.emoji_images))}
        self.secret_collected = False
        self.secret2_collected = False  # Reset second secret collection status
        self.update_bag_hud()

    def display_death_message(self):
        self.death_message_id = self.canvas.create_text(self.screen_width // 2, self.screen_height // 2,
                                                         text=random.choice(self.death_messages), font=("Helvetica", 36), fill="red")
        self.master.after(2000, self.remove_death_message)

    def remove_death_message(self):
        if self.death_message_id:
            self.canvas.delete(self.death_message_id)
            self.death_message_id = None  # Reset the ID after removal

    def reset_player_position(self):
        self.canvas.coords(self.player, self.screen_width // 2, self.screen_height // 2)

    def shake_screen(self):
        original_position = self.canvas.winfo_x(), self.canvas.winfo_y()
        for _ in range(10):
            offset = random.randint(-5, 5)
            self.canvas.place(x=original_position[0] + offset, y=original_position[1] + offset)
        self.canvas.place(x=original_position)

    def game_over(self):
        self.canvas.delete("all")
        last_death_message = random.choice(self.death_messages)
        self.canvas.create_text(self.screen_width // 2, self.screen_height // 2, text=last_death_message,
                                font=("Helvetica", 48), fill="red")
        self.canvas.create_text(self.screen_width // 2, self.screen_height // 2 + 60,
                                text=f"Final Score: {self.score}", font=("Helvetica", 24), fill="white")
        self.restart_button = tk.Button(self.canvas, text="Restart Game", command=self.restart_game)
        self.restart_button.place(relx=0.5, rely=0.5 + 0.1, anchor=tk.CENTER)  # Adjust position of restart button

    def restart_game(self):
        # Clear the canvas
        self.canvas.delete("all")
        
        # Remove any remaining messages and buttons
        self.remove_death_message()
        if self.secret_message_id:
            self.canvas.delete(self.secret_message_id)
            self.secret_message_id = None
        if self.secret2_message_id:
            self.canvas.delete(self.secret2_message_id)
            self.secret2_message_id = None
        if self.death_message_id:
            self.canvas.delete(self.death_message_id)
            self.death_message_id = None

        # Remove the restart button if it's still present
        if hasattr(self, 'restart_button'):
            self.restart_button.place_forget()

        # Reinitialize game variables and set up the game
        self.init_game_variables()
        self.setup_game_objects()
        self.update_score()
        self.update_bag_hud()
        self.move_player()

    def rects_overlap(self, rect1, rect2):
        return not (rect1[2] < rect2[0] or rect1[0] > rect2[2] or rect1[3] < rect2[1] or rect1[1] > rect2[3])

    def update_score(self):
        self.canvas.delete("score")
        self.canvas.create_text(10, 10, anchor=tk.NW, text=f"Score: {self.score}", font=("Helvetica", 20), fill="white", tags="score")

    def update_bag_hud(self):
        self.canvas.delete("bag")
        for i, count in self.collected_counts.items():
            if count > 0 or i == -1 or i == -2:
                emoji_image = self.secret_image if i == -1 else (self.secret2_image if i == -2 else self.emoji_images[i])
                emoji_display = self.canvas.create_image(self.screen_width - 80, 40 + (i * 60), anchor=tk.NW, image=emoji_image)
                self.canvas.create_text(self.screen_width - 40, 40 + (i * 60) + 20, anchor=tk.NW, text=f"{count}", font=("Helvetica", 20), fill="white", tags="bag")

class CharacterSelection:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=800, height=600)
        self.canvas.pack()

        self.character_images = [self.load_image(f"images/player_character{i + 1}.png") for i in range(3)]
        self.selected_character = None

        for image in self.character_images:
            button = tk.Button(self.canvas, image=image, command=lambda img=image: self.select_character(img))
            button.pack(padx=10, pady=5)

        self.start_button = tk.Button(self.canvas, text="Start Game", command=self.start_game)
        self.start_button.pack(pady=10)

    def load_image(self, file_name):
        try:
            return tk.PhotoImage(file=file_name)
        except tk.TclError:
            print(f"Error loading image: {file_name}")
            return None

    def select_character(self, image):
        self.selected_character = image

    def start_game(self):
        if self.selected_character:
            self.canvas.destroy()
            Game(self.master, self.selected_character)

if __name__ == "__main__":
    print ("the secrets are at 1k and 10k points")
    root = tk.Tk()
    character_selection = CharacterSelection(root)
    root.mainloop()