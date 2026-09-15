import tkinter as tk
from tkinter import messagebox


class BacteriaGame:
    def __init__(self, root, size=20, cell_size=40):
        self.root = root
        self.root.title("MoMath Bacteria Puzzle")
        self.size = size
        self.cell_size = cell_size

        # Initial state: One bacterium at the origin (bottom-left for visualization)
        # We'll map (0,0) to the visual bottom-left
        self.cells = set([(0, 0)])

        self.canvas = tk.Canvas(root, width=size * cell_size, height=size * cell_size, bg="white")
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.handle_click)

        self.draw_grid()
        self.update_view()

    def draw_grid(self):
        # Draw the target area (0,0) to (3,3) boundary
        x_start, y_end = self.grid_to_canvas(0, -1)
        x_end, y_start = self.grid_to_canvas(3, 2)
        self.canvas.create_rectangle(x_start, y_start, x_end, y_end,
                                     fill="#ffebee", outline="#ffcdd2", width=2)

    def grid_to_canvas(self, x, y):
        # Flip Y so (0,0) is bottom-left
        x1 = x * self.cell_size
        y1 = (self.size - 1 - y) * self.cell_size
        return x1, y1

    def update_view(self):
        self.canvas.delete("cell")
        for x, y in self.cells:
            x1, y1 = self.grid_to_canvas(x, y)
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size, y1 + self.cell_size,
                                         fill="black", tags="cell")

    def handle_click(self, event):
        # Convert canvas click to grid coords
        grid_x = event.x // self.cell_size
        grid_y = self.size - 1 - (event.y // self.cell_size)

        if (grid_x, grid_y) in self.cells:
            # Check replication rules
            child_a = (grid_x + 1, grid_y)
            child_b = (grid_x, grid_y + 1)

            if child_a not in self.cells and child_b not in self.cells:
                # Perform replication
                self.cells.remove((grid_x, grid_y))
                self.cells.add(child_a)
                self.cells.add(child_b)
                self.update_view()
                self.check_win()
            else:
                print("Space blocked! Cannot replicate.")

    def check_win(self):
        # The goal is to clear the square with corners (0,0) and (3,3)
        # That means no cells with 0 <= x < 3 and 0 <= y < 3
        for x in range(3):
            for y in range(3):
                if (x, y) in self.cells:
                    return
        messagebox.showinfo("Goal Reached!", "The target area is clear!")


if __name__ == "__main__":
    root = tk.Tk()
    game = BacteriaGame(root)
    root.mainloop()