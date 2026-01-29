import tkinter as tk
import time as _time


class screenTimer:

    def __init__(self, duration, function=None):
        self.function = function
        self.DURATION_SECONDS = duration

        self.start_time = _time.time()
        self.end_time = self.start_time + self.DURATION_SECONDS
        self.running = True

        self.ALPHA = 1
        self.FONT = ("Segoe UI", 18, "bold")
        self.color = "red"
        self.PADDING_X = 0
        self.PADDING_Y = 0
        self.OFFSET_X = 0
        self.OFFSET_Y = 80

        self.root = None
        self.label = None

    def start(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", self.ALPHA)
        self.root.wm_attributes("-transparentcolor", "#f12e2e")

        self.label = tk.Label(
            self.root,
            text="",
            font=self.FONT,
            fg="white",
            bg="#f12e2e"
        )
        self.label.pack(padx=self.PADDING_X, pady=self.PADDING_Y)

        self.position_bottom_right()
        self.tick()
        self.root.mainloop()

    def stop(self):
        if self.running:
            self.running = False
            if self.root:
                self.root.destroy()

    def get_elapsed(self):
        return int(_time.time() - self.start_time)

    def position_bottom_right(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        x = sw - w - self.OFFSET_X - 200
        y = sh - h - self.OFFSET_Y

        self.root.geometry(f"+{x}+{y}")

    def tick(self):
        if not self.running:
            return

        remaining = int(self.end_time - _time.time())

        if remaining <= 0:
            self.running = False
            if self.function:
                self.function()
            self.root.destroy()
            return

        mm = (remaining // 60) % 60
        ss = remaining % 60
        self.label.config(text=f"TIMER: {mm:02d}:{ss:02d}", fg=self.color)

        self.root.after(200, self.tick)
