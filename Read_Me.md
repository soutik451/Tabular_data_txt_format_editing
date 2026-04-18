================================================================================
                              2D MATRIX IN TXT FILE EDITOR
================================================================================

An interactive, lightweight Python tool for visualizing and editing 2D MATRIX 
(or any tabular) data matrices. 

This application opens a file-picker to load your text-based data files, 
renders them as an interactive 2D colorplot, and allows you to instantly edit 
individual data points on the fly. It is perfect for cleaning up artifacts, 
tweaking specific amplitude values, or quickly inspecting large matrices.


--------------------------------------------------------------------------------
FEATURES
--------------------------------------------------------------------------------
* Interactive Visualization: Renders your 2D data matrix as a colorplot with 
  an automatic colorbar.

* Live Inspection: Hover over any point on the plot to view its exact [Row, Col] 
  coordinates and amplitude value in the status bar.

* Point-and-Click Editing: Left-click any cell to pop up an edit dialog. Type a 
  new value to instantly update both the plot and the underlying dataset.

* Dynamic Colormaps: Press 'C' to cycle through popular colormaps (jet, viridis, 
  plasma, inferno, turbo).

* Easy Export: Press 'E' to capture and save the current plot as a clean, 
  high-resolution PNG image.

* Save Changes: Press 'S' to export your edited data to a new tab-separated 
  .txt file without overwriting your original.

* Undo/Reset: Made a mistake? Press 'R' to instantly revert all edits back to 
  the original loaded data.


--------------------------------------------------------------------------------
REQUIREMENTS
--------------------------------------------------------------------------------
The script uses standard scientific Python libraries. If you are using an 
Anaconda distribution, you likely have these already. Otherwise, install them 
via your command prompt or terminal:

    pip install numpy matplotlib

(Note: 'tkinter' is used for the GUI dialogs. It is included in the standard 
Python library by default).


--------------------------------------------------------------------------------
USAGE
--------------------------------------------------------------------------------
Run the script from your terminal or VS Code environment:

    python Editor.py

1. A file dialog will prompt you to select your data file.
2. The interactive plot will open.
3. Use the following keyboard and mouse controls:

    Hover Mouse  : Displays the row, column, and value at the cursor.
    Left-Click   : Opens a dialog to input a new numeric value for that cell.
    Press 'S'    : Saves the updated array to [original_filename]_edited.txt.
    Press 'E'    : Saves the current visual plot as a PNG image.
    Press 'C'    : Changes the color scheme of the plot.
    Press 'R'    : Reverts all edits back to the original state.


--------------------------------------------------------------------------------
SUPPORTED DATA FORMATS
--------------------------------------------------------------------------------
The program is built to flexibly handle various text-based data files (.txt, 
.csv, .dat, .asc, .tsv). 

For the code to work correctly, your file must contain PURELY NUMERIC DATA and 
match one of the following structures:

1. 2D Matrix (Standard)
The ideal format is a 2D grid of numbers separated by spaces, tabs, or commas. 
Every row should have the same number of columns.

    Example (data.txt):
    0.523  0.112  0.943  0.221
    0.884  0.551  0.339  0.104
    0.992  0.773  0.441  0.505

2. 1D Array (Perfect Square)
If your file is a single, long column or row of data, the program will attempt 
to reshape it into a 2D matrix. HOWEVER, this only works if the total number of 
values forms a perfect square (e.g., 100 values becomes a 10x10 matrix, 400 
values becomes 20x20).

    Example:
    0.523
    0.112
    0.943
    ... (must equal x-squared total rows)

Parsing Details:
* Delimiters: The script automatically attempts to parse your file using commas, 
  tabs, and spaces. 
* Headers/Text: The file should NOT contain string headers or text columns. If 
  it contains irregular formatting, the script falls back to 'np.genfromtxt', 
  which attempts to salvage the data by replacing unreadable characters with NaN 
  (Not a Number), but it is highly recommended to provide clean numeric arrays.