import random
import tkinter as tk
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class RoombaCleanupGame:
    GRID_WIDTH = 14
    GRID_HEIGHT = 14
    CELL_SIZE = 38
    STARTING_TRASH = 24
    POOP_SPAWN_CHANCE = 0.26  # chance each spawn tick
    POOP_SPAWN_INTERVAL_MS = 1300

    COLOR_BG = "#f3f4f6"
    COLOR_GRID = "#d1d5db"
    COLOR_ROOMBA = "#2563eb"
    COLOR_TRASH = "#f59e0b"
    COLOR_POOP = "#7c3f00"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Roomba Cleanup")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width=self.GRID_WIDTH * self.CELL_SIZE,
            height=self.GRID_HEIGHT * self.CELL_SIZE,
            bg=self.COLOR_BG,
            highlightthickness=0,
        )
        self.canvas.pack(padx=12, pady=(12, 6))

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(root, textvariable=self.status_var, font=("Arial", 12, "bold"))
        self.status_label.pack(pady=(0, 8))

        control_text = "Move: Arrow Keys or WASD | Clean all trash, avoid poop"
        self.control_label = tk.Label(root, text=control_text, font=("Arial", 10))
        self.control_label.pack(pady=(0, 10))

        self.player = Point(self.GRID_WIDTH // 2, self.GRID_HEIGHT // 2)
        self.trash: set[Point] = set()
        self.poop: set[Point] = set()

        self.game_over = False
        self.victory = False

        self.root.bind("<KeyPress>", self.handle_keypress)

        self.populate_trash()
        self.update_status()
        self.draw()
        self.root.after(self.POOP_SPAWN_INTERVAL_MS, self.poop_spawn_tick)

    def populate_trash(self) -> None:
        available = [Point(x, y) for x in range(self.GRID_WIDTH) for y in range(self.GRID_HEIGHT)]
        available.remove(self.player)
        random.shuffle(available)

        self.trash = set(available[: self.STARTING_TRASH])

    def handle_keypress(self, event: tk.Event) -> None:
        if self.game_over:
            if event.keysym.lower() == "r":
                self.restart()
            return

        movement = {
            "Up": Point(0, -1),
            "Down": Point(0, 1),
            "Left": Point(-1, 0),
            "Right": Point(1, 0),
            "w": Point(0, -1),
            "s": Point(0, 1),
            "a": Point(-1, 0),
            "d": Point(1, 0),
        }

        delta = movement.get(event.keysym)
        if not delta:
            return

        next_pos = Point(
            min(max(self.player.x + delta.x, 0), self.GRID_WIDTH - 1),
            min(max(self.player.y + delta.y, 0), self.GRID_HEIGHT - 1),
        )

        self.player = next_pos
        self.resolve_player_tile()
        self.update_status()
        self.draw()

    def poop_spawn_tick(self) -> None:
        if not self.game_over and random.random() < self.POOP_SPAWN_CHANCE:
            candidates = [
                Point(x, y)
                for x in range(self.GRID_WIDTH)
                for y in range(self.GRID_HEIGHT)
                if Point(x, y) not in self.poop and Point(x, y) not in self.trash
            ]

            if candidates:
                spawned = random.choice(candidates)
                self.poop.add(spawned)

                if spawned == self.player:
                    self.trigger_game_over()

            self.update_status()
            self.draw()

        self.root.after(self.POOP_SPAWN_INTERVAL_MS, self.poop_spawn_tick)

    def resolve_player_tile(self) -> None:
        if self.player in self.poop:
            self.trigger_game_over()
            return

        if self.player in self.trash:
            self.trash.remove(self.player)
            if not self.trash:
                self.victory = True
                self.game_over = True

    def trigger_game_over(self) -> None:
        self.game_over = True
        self.victory = False

    def update_status(self) -> None:
        if self.game_over:
            if self.victory:
                self.status_var.set("You cleaned everything! Press R to play again.")
            else:
                self.status_var.set("You hit poop. Game over! Press R to restart.")
            return

        self.status_var.set(f"Trash remaining: {len(self.trash)} | Poop on floor: {len(self.poop)}")

    def restart(self) -> None:
        self.player = Point(self.GRID_WIDTH // 2, self.GRID_HEIGHT // 2)
        self.trash.clear()
        self.poop.clear()
        self.game_over = False
        self.victory = False

        self.populate_trash()
        self.update_status()
        self.draw()

    def draw(self) -> None:
        self.canvas.delete("all")

        for x in range(self.GRID_WIDTH):
            for y in range(self.GRID_HEIGHT):
                x1 = x * self.CELL_SIZE
                y1 = y * self.CELL_SIZE
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=self.COLOR_BG,
                    outline=self.COLOR_GRID,
                )

        for tile in self.trash:
            self.draw_tile(tile, self.COLOR_TRASH, "🗑")

        for tile in self.poop:
            self.draw_tile(tile, self.COLOR_POOP, "💩")

        self.draw_tile(self.player, self.COLOR_ROOMBA, "🤖")

        if self.game_over:
            message = "ALL CLEAN!" if self.victory else "GAME OVER"
            self.canvas.create_text(
                (self.GRID_WIDTH * self.CELL_SIZE) // 2,
                (self.GRID_HEIGHT * self.CELL_SIZE) // 2,
                text=message,
                fill="#111827",
                font=("Arial", 26, "bold"),
            )

    def draw_tile(self, point: Point, color: str, icon: str) -> None:
        x1 = point.x * self.CELL_SIZE + 4
        y1 = point.y * self.CELL_SIZE + 4
        x2 = x1 + self.CELL_SIZE - 8
        y2 = y1 + self.CELL_SIZE - 8

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
        self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=icon, font=("Arial", 16))


if __name__ == "__main__":
    app = tk.Tk()
    RoombaCleanupGame(app)
    app.mainloop()
