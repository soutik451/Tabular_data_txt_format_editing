"""
 Data Editor — Interactive 2D Colorplot with Point Editing
=================================================================
Run in VS Code / terminal:  python _editor.py

Features:
  • Opens a file-picker dialog to load a TXT file (space/tab/comma separated)
  • Renders a 2D color plot with colorbar
  • Hover the mouse → status bar shows [row, col] = value
  • LEFT-CLICK on any point → a dialog pops up to type a new value
    – Updates both the in-memory array AND the plot instantly
  • Press  'S'  → saves the edited TXT file  (original_name_edited.txt)
  • Press  'E'  → exports the current plot as a PNG image
  • Press  'C'  → cycle colormap (jet → viridis → plasma → inferno →  → turbo)
  • Press  'R'  → reset to original data (undo all edits)
  • Close the window when done

Requires: numpy, matplotlib  (both ship with Anaconda)
"""

import numpy as np
import matplotlib
matplotlib.use("TkAgg")  # ensure interactive backend for VS Code
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import os
import copy

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
COLORMAPS = ["jet", "viridis", "plasma", "inferno", "", "turbo"]

# ──────────────────────────────────────────────
# Load file
# ──────────────────────────────────────────────
def load_txt_file():
    """Open a file dialog and return (data_array, file_path)."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    file_path = filedialog.askopenfilename(
        title="Select a TXT data file",
        filetypes=[
            ("Text files", "*.txt *.csv *.dat *.asc *.tsv"),
            ("All files", "*.*"),
        ],
    )
    root.destroy()
    if not file_path:
        print("No file selected. Exiting.")
        return None, None

    # Try multiple delimiters
    data = None
    for delimiter in [None, ",", "\t", " "]:
        try:
            data = np.loadtxt(file_path, delimiter=delimiter)
            if data.ndim == 2 and data.shape[0] > 1 and data.shape[1] > 1:
                break
        except Exception:
            continue

    if data is None or data.ndim != 2:
        try:
            # Last resort: genfromtxt handles irregular files
            data = np.genfromtxt(file_path, invalid_raise=False)
        except Exception as e:
            print(f"ERROR: Could not parse file.\n{e}")
            return None, None

    if data.ndim == 1:
        # Single column → reshape to 2D
        side = int(np.sqrt(len(data)))
        if side * side == len(data):
            data = data.reshape(side, side)
        else:
            print("ERROR: 1-D data and not a perfect square — cannot reshape.")
            return None, None

    print(f"Loaded: {file_path}")
    print(f"  Shape : {data.shape[0]} rows × {data.shape[1]} cols")
    print(f"  Range : [{np.nanmin(data):.6f}, {np.nanmax(data):.6f}]")
    return data, file_path


# ──────────────────────────────────────────────
# Main interactive editor
# ──────────────────────────────────────────────
class Editor:
    def __init__(self, data, file_path):
        self.original_data = copy.deepcopy(data)
        self.data = data
        self.file_path = file_path
        self.base_name = os.path.splitext(os.path.basename(file_path))[0]
        self.dir_name = os.path.dirname(file_path)
        self.cmap_idx = 0
        self.edit_count = 0
        self.nrows, self.ncols = data.shape

        # ── Create figure ──
        self.fig, self.ax = plt.subplots(1, 1, figsize=(10, 7))
        self.fig.canvas.manager.set_window_title(" Data Editor")
        self.fig.subplots_adjust(bottom=0.12, top=0.92, left=0.08, right=0.92)

        # ── Plot ──
        self.im = self.ax.imshow(
            self.data,
            aspect="auto",
            cmap=COLORMAPS[self.cmap_idx],
            interpolation="nearest",
            origin="upper",
        )
        self.cbar = self.fig.colorbar(self.im, ax=self.ax, pad=0.02)
        self.cbar.set_label("Amplitude", fontsize=10)
        self.ax.set_title(f"{self.base_name}  ({self.nrows}×{self.ncols})", fontsize=12, fontweight="bold")
        self.ax.set_xlabel("Column", fontsize=10)
        self.ax.set_ylabel("Row", fontsize=10)

        # ── Crosshair lines ──
        self.hline = self.ax.axhline(y=0, color="white", linewidth=0.5, alpha=0.5, visible=False)
        self.vline = self.ax.axvline(x=0, color="white", linewidth=0.5, alpha=0.5, visible=False)

        # ── Marker for last edited point ──
        (self.edit_marker,) = self.ax.plot([], [], "ws", markersize=8, markeredgewidth=1.5,
                                            markerfacecolor="none", visible=False)

        # ── Status text ──
        self.status_text = self.fig.text(
            0.02, 0.02, "", fontsize=9, fontfamily="monospace",
            color="#333333", verticalalignment="bottom",
        )
        self.help_text = self.fig.text(
            0.98, 0.02,
            "CLICK=edit  S=save txt  E=export png  C=colormap  R=reset",
            fontsize=8, fontfamily="monospace", color="#888888",
            verticalalignment="bottom", horizontalalignment="right",
        )

        # ── Connect events ──
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_move)
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)

    # ── Hover ──
    def on_move(self, event):
        if event.inaxes != self.ax:
            self.hline.set_visible(False)
            self.vline.set_visible(False)
            self.status_text.set_text("")
            self.fig.canvas.draw_idle()
            return
        col = int(round(event.xdata))
        row = int(round(event.ydata))
        if 0 <= row < self.nrows and 0 <= col < self.ncols:
            val = self.data[row, col]
            self.status_text.set_text(
                f"Row: {row}  Col: {col}  Value: {val:.6f}   |   Edits: {self.edit_count}"
            )
            self.hline.set_ydata([row])
            self.vline.set_xdata([col])
            self.hline.set_visible(True)
            self.vline.set_visible(True)
        else:
            self.hline.set_visible(False)
            self.vline.set_visible(False)
            self.status_text.set_text("")
        self.fig.canvas.draw_idle()

    # ── Click to edit ──
    def on_click(self, event):
        if event.inaxes != self.ax or event.button != 1:
            return
        col = int(round(event.xdata))
        row = int(round(event.ydata))
        if not (0 <= row < self.nrows and 0 <= col < self.ncols):
            return

        old_val = self.data[row, col]

        # Pop up a dialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        new_val_str = simpledialog.askstring(
            "Edit Value",
            f"Position: Row {row}, Col {col}\n"
            f"Current value: {old_val:.6f}\n\n"
            f"Enter new value:",
            initialvalue=f"{old_val:.6f}",
            parent=root,
        )
        root.destroy()

        if new_val_str is None:
            return  # Cancelled

        try:
            new_val = float(new_val_str)
        except ValueError:
            print(f"  Invalid number: '{new_val_str}' — skipped.")
            return

        # Apply edit
        self.data[row, col] = new_val
        self.edit_count += 1
        print(f"  Edit #{self.edit_count}: [{row}, {col}]  {old_val:.6f} → {new_val:.6f}")

        # Update plot
        self.refresh_plot()

        # Show marker on edited cell
        self.edit_marker.set_data([col], [row])
        self.edit_marker.set_visible(True)
        self.fig.canvas.draw_idle()

    # ── Keyboard shortcuts ──
    def on_key(self, event):
        if event.key == "s":
            self.save_txt()
        elif event.key == "e":
            self.save_image()
        elif event.key == "c":
            self.cycle_colormap()
        elif event.key == "r":
            self.reset_data()

    # ── Refresh plot after edits ──
    def refresh_plot(self):
        self.im.set_data(self.data)
        vmin, vmax = np.nanmin(self.data), np.nanmax(self.data)
        self.im.set_norm(Normalize(vmin=vmin, vmax=vmax))
        self.cbar.update_normal(self.im)
        self.fig.canvas.draw_idle()

    # ── Cycle colormap ──
    def cycle_colormap(self):
        self.cmap_idx = (self.cmap_idx + 1) % len(COLORMAPS)
        name = COLORMAPS[self.cmap_idx]
        self.im.set_cmap(name)
        self.fig.canvas.draw_idle()
        print(f"  Colormap → {name}")

    # ── Save TXT ──
    def save_txt(self):
        out_path = os.path.join(self.dir_name, f"{self.base_name}_edited.txt")
        np.savetxt(out_path, self.data, fmt="%.6f", delimiter="\t")
        print(f"  ✓ Saved TXT → {out_path}")
        self.status_text.set_text(f"Saved: {out_path}")
        self.fig.canvas.draw_idle()

    # ── Save image ──
    def save_image(self):
        out_path = os.path.join(self.dir_name, f"{self.base_name}_plot.png")
        # Temporarily hide crosshairs and markers for clean export
        hv = self.hline.get_visible()
        vv = self.vline.get_visible()
        mv = self.edit_marker.get_visible()
        self.hline.set_visible(False)
        self.vline.set_visible(False)
        self.edit_marker.set_visible(False)
        self.fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
        self.hline.set_visible(hv)
        self.vline.set_visible(vv)
        self.edit_marker.set_visible(mv)
        print(f"  ✓ Saved PNG → {out_path}")
        self.status_text.set_text(f"Saved: {out_path}")
        self.fig.canvas.draw_idle()

    # ── Reset to original ──
    def reset_data(self):
        self.data = copy.deepcopy(self.original_data)
        self.edit_count = 0
        self.edit_marker.set_visible(False)
        self.refresh_plot()
        print("  ✓ Reset to original data")

    # ── Show ──
    def run(self):
        plt.show()


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("   DATA EDITOR")
    print("=" * 55)
    print("  Select a TXT file to begin...\n")

    data, file_path = load_txt_file()

    if data is not None:
        editor = Editor(data, file_path)
        print("\n  Controls:")
        print("    Hover       → see value at cursor")
        print("    Left-click  → edit a point's value")
        print("    S           → save edited TXT file")
        print("    E           → export plot as PNG")
        print("    C           → cycle colormap")
        print("    R           → reset all edits")
        print("    Close window to quit\n")
        editor.run()
    else:
        print("Exiting.")