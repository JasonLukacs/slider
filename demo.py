import tkinter as tk
import slider
from config import *

root = tk.Tk()

def create_font_tuple(value):
    # Receive comma separated string "Family, size, option option"
    # Return tuple ("Family", "size", "option option")
    temp = value.rstrip(",").split(",")
    for index, item in enumerate(temp):
        temp[index] = item.strip()
    return tuple(temp)

for prebuilt in prebuilt_defs:
    kwargs = {}
    for key in prebuilt_defs[prebuilt]:
        value = prebuilt_defs[prebuilt][key]
        if key == "font":
            value = create_font_tuple(value)
        kwargs[key] = value
    slider.Slider(root, **kwargs).pack(anchor=tk.W)

# Mainloop
root.mainloop()