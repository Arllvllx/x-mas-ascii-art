import math
import random
import tkinter as tk


WIDTH = 960
HEIGHT = 560


class WinterWish:
    def __init__(self, root):
        self.root = root
        self.root.title("A Little Winter Wish")
        self.root.configure(bg="#101722")
        self.root.minsize(720, 600)

        self.canvas = tk.Canvas(
            root,
            bg="#101722",
            highlightthickness=0,
            height=HEIGHT,
        )
        self.canvas.pack(fill="both", expand=True, padx=22, pady=(16, 8))

        footer = tk.Frame(root, bg="#101722")
        footer.pack(fill="x", padx=28, pady=(0, 20))
        self.wish_button = tk.Button(
            footer,
            text="✦  MAKE A WISH  ✦",
            command=self.make_wish,
            bg="#d8ad67",
            fg="#24202a",
            activebackground="#f0cf91",
            activeforeground="#24202a",
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            padx=22,
            pady=11,
            font=("Helvetica", 11, "bold"),
        )
        self.wish_button.pack(side="left")
        self.message = tk.Label(
            footer,
            text="A quiet night, a warm light, and one little wish.",
            bg="#101722",
            fg="#a9b5c5",
            font=("Helvetica", 10),
        )
        self.message.pack(side="left", padx=18)

        self.rng = random.Random()
        self.snow = [
            [self.rng.uniform(30, WIDTH - 30), self.rng.uniform(52, HEIGHT - 25), self.rng.uniform(0.7, 2.0)]
            for _ in range(115)
        ]
        self.sky = [
            (
                self.rng.uniform(24, WIDTH - 24),
                self.rng.uniform(54, 390),
                self.rng.choice(("#71829a", "#9aa9b9", "#d2c49f", "#52667f")),
                self.rng.choice((".", "·", "*", "+")),
                self.rng.choice((8, 9, 11)),
            )
            for _ in range(78)
        ]
        self.tree = self.make_tree()
        self.stars = []
        self.wish_until = 0
        self.canvas.bind("<Configure>", lambda _event: self.draw())
        self.animate()

    def make_wish(self):
        for _ in range(24):
            self.stars.append(
                {
                    "x": self.rng.uniform(100, WIDTH - 100),
                    "y": self.rng.uniform(60, 260),
                    "vx": self.rng.uniform(-1.5, 1.5),
                    "vy": self.rng.uniform(2.2, 4.6),
                    "life": self.rng.randint(45, 85),
                    "tail": self.rng.randint(12, 26),
                }
            )
        self.wish_until = int(self.root.tk.call("clock", "milliseconds")) + 1800
        self.message.configure(text="Your wish is on its way through the winter sky…", fg="#f0cf91")
        self.wish_button.configure(text="✦  WISH GRANTED — AGAIN?  ✦")

    def text(self, x, y, value, color, size=12, anchor="center", weight="normal"):
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        scale = min(width / WIDTH, height / HEIGHT)
        self.canvas.create_text(
            x * width / WIDTH,
            y * height / HEIGHT,
            text=value,
            fill=color,
            font=("Courier New", max(7, round(size * scale)), weight),
            anchor=anchor,
        )

    def rectangle(self, x1, y1, x2, y2, **options):
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        self.canvas.create_rectangle(
            x1 * width / WIDTH,
            y1 * height / HEIGHT,
            x2 * width / WIDTH,
            y2 * height / HEIGHT,
            **options,
        )

    def polygon(self, *coordinates, **options):
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        scaled = []
        for index, value in enumerate(coordinates):
            scaled.append(value * width / WIDTH if index % 2 == 0 else value * height / HEIGHT)
        self.canvas.create_polygon(*scaled, **options)

    def oval(self, x1, y1, x2, y2, **options):
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        self.canvas.create_oval(
            x1 * width / WIDTH,
            y1 * height / HEIGHT,
            x2 * width / WIDTH,
            y2 * height / HEIGHT,
            **options,
        )

    def draw(self):
        self.canvas.delete("all")
        self.rectangle(2, 2, WIDTH - 2, HEIGHT - 2, fill="#111c2a", outline="#354354", width=2)
        self.rectangle(3, 3, WIDTH - 3, 39, fill="#1c2938", outline="")
        for x, color in ((22, "#e9877c"), (39, "#e8c477"), (56, "#87bd9a")):
            self.oval(x, 15, x + 8, 23, fill=color, outline="")
        self.text(78, 20, "NORTHSTAR   /   WINTER NIGHT", "#c2cfdb", 10, anchor="w", weight="bold")
        self.text(930, 20, "EST. 24 DEC  ·  11:59 PM", "#8292a5", 9, anchor="e")

        self.rectangle(4, 40, WIDTH - 4, HEIGHT - 4, fill="#101a29", outline="")
        self.draw_sky()
        self.draw_hills()
        self.draw_cabin()
        self.draw_tree()
        self.draw_snow()
        self.draw_falling_stars()
        self.text(24, HEIGHT - 17, "COLD OUTSIDE  /  COZY INSIDE", "#8795a7", 9, anchor="w")
        self.text(WIDTH - 24, HEIGHT - 17, "PRESS THE BUTTON TO SEND A WISH", "#8795a7", 9, anchor="e")

    def draw_sky(self):
        for x, y, color, glyph, size in self.sky:
            self.text(x, y, glyph, color, size)

        self.text(775, 112, "◌", "#d4cda9", 57)
        self.text(775, 112, "☾", "#f2dfae", 35)
        self.text(775, 151, "a little moon keeping watch", "#9ba7b5", 9)

        for x, y in ((110, 125), (295, 89), (666, 75), (874, 206), (390, 105)):
            self.text(x, y, "✧", "#e9d8a9", 13)

    def draw_hills(self):
        self.polygon(
            0, 398, 110, 330, 220, 408, 355, 350, 470, 412, 620, 334,
            760, 405, 865, 340, WIDTH, 405, WIDTH, HEIGHT, 0, HEIGHT,
            fill="#192b3a", outline="",
        )
        self.polygon(
            0, 452, 152, 393, 290, 448, 433, 388, 590, 449, 748, 386,
            900, 449, WIDTH, 420, WIDTH, HEIGHT, 0, HEIGHT,
            fill="#d5e0df", outline="",
        )
        self.polygon(
            0, 478, 180, 425, 330, 475, 500, 430, 680, 480, 850, 424,
            WIDTH, 465, WIDTH, HEIGHT, 0, HEIGHT,
            fill="#f0f0e5", outline="",
        )

    def draw_cabin(self):
        # A tiny block-built cabin, with a roofline made from ASCII characters.
        self.text(181, 320, "        /\\", "#d7e5e6", 17, anchor="w", weight="bold")
        self.text(181, 340, "       /  \\     .", "#d7e5e6", 17, anchor="w", weight="bold")
        self.text(181, 360, "      /____\\   .", "#d7e5e6", 17, anchor="w", weight="bold")
        self.text(181, 380, "      | [] |", "#bc9270", 17, anchor="w", weight="bold")
        self.text(181, 400, "      |  _  |", "#bc9270", 17, anchor="w", weight="bold")
        self.text(181, 420, "      |_____|", "#bc9270", 17, anchor="w", weight="bold")
        self.text(272, 380, "[]", "#ffcf78", 13, weight="bold")
        self.text(278, 401, "▯", "#583e3d", 16)
        self.text(203, 448, "HOME  SWEET  HOME", "#526575", 9, weight="bold")
        self.text(322, 281, "~", "#82909d", 17)
        self.text(333, 264, "~", "#82909d", 14)
        self.text(342, 247, "~", "#82909d", 11)

    def draw_tree(self):
        center = 574
        for x, y, glyph, color in self.tree:
            self.text(x, y, glyph, color, 13, weight="bold")

        self.text(center, 91, "✦", "#f6d77e", 23, weight="bold")
        self.text(center, 407, "|||", "#88654f", 19, weight="bold")
        self.text(center, 449, "*   *   *   *   *   *   *", "#dfe9df", 12)
        self.text(center, 468, "MERRY  &  BRIGHT", "#b0c1ba", 10, weight="bold")

        for x, y in ((86, 356), (112, 385), (871, 356), (844, 382), (729, 418)):
            self.draw_small_pine(x, y)

    def make_tree(self):
        tree = []
        center = 574
        palette = ("#214b41", "#28604b", "#34735a", "#3e795d", "#6e966a")
        ornaments = ("#e2b965", "#d97c69", "#e4d7a4", "#a8c6b0")
        for row in range(22):
            y = 110 + row * 13
            half_width = 1 + row * 1.38
            for x in range(math.ceil(center - half_width), math.floor(center + half_width) + 1, 13):
                edge = abs(x - center) / max(half_width, 1)
                if self.rng.random() < 0.13 + edge * 0.22:
                    continue
                glyph = self.rng.choice(("*", ".", "+", "v", "Y"))
                color = self.rng.choice(palette)
                if self.rng.random() < 0.045:
                    glyph = self.rng.choice(("o", "@", "*"))
                    color = self.rng.choice(ornaments)
                tree.append((x, y, glyph, color))
        return tree

    def draw_small_pine(self, x, y):
        self.text(x, y - 25, "*", "#61846d", 18, weight="bold")
        self.text(x, y - 12, "/Y\\", "#4e7964", 13, weight="bold")
        self.text(x, y, "/YYY\\", "#386451", 13, weight="bold")
        self.text(x, y + 10, "  |", "#80644f", 11, weight="bold")

    def draw_snow(self):
        for flake in self.snow:
            x, y, speed = flake
            self.text(x, y, "." if speed < 1.4 else "*", "#dce7ed", 9 if speed < 1.4 else 11)

    def draw_falling_stars(self):
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        for star in self.stars:
            x1 = star["x"] * width / WIDTH
            y1 = star["y"] * height / HEIGHT
            x2 = (star["x"] - star["vx"] * star["tail"] * 0.7) * width / WIDTH
            y2 = (star["y"] - star["tail"]) * height / HEIGHT
            self.canvas.create_line(x1, y1, x2, y2, fill="#d8bb7e", width=2, capstyle="round")
            self.text(star["x"], star["y"], "✦", "#fff0bd", 12)

    def animate(self):
        for flake in self.snow:
            flake[0] += self.rng.uniform(-0.45, 0.45)
            flake[1] += flake[2]
            if flake[1] > HEIGHT - 35:
                flake[1] = 45
                flake[0] = self.rng.uniform(25, WIDTH - 25)
            flake[0] %= WIDTH

        for star in self.stars[:]:
            star["x"] += star["vx"]
            star["y"] += star["vy"]
            star["life"] -= 1
            if star["life"] <= 0 or star["y"] > HEIGHT:
                self.stars.remove(star)

        now = int(self.root.tk.call("clock", "milliseconds"))
        if self.wish_until and now > self.wish_until and not self.stars:
            self.wish_until = 0
            self.message.configure(text="A quiet night, a warm light, and one little wish.", fg="#a9b5c5")
            self.wish_button.configure(text="✦  MAKE A WISH  ✦")

        self.draw()
        self.root.after(55, self.animate)


if __name__ == "__main__":
    app = tk.Tk()
    WinterWish(app)
    app.mainloop()