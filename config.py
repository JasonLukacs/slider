""" Copyright (c) 2023 J.A. Lukács
SPDX-License-Identifier: 0BSD
Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
-------------------------------------------------------------------------------
"""

# FORMFIELDS
# Values for comboboxes
borders = [
    "flat",
    "solid",
    "raised",
    "sunken",
    "ridge",
    "groove"
]
thumb_styles = [
    "classic",
    "dot",
    "diamond",
    "pointer",
    "crosshair",
    "cube",
]
track_styles = ["plane", "line"]
track_backgrounds = [
    "None",
    "green_to_red",
    "white_to_blue",
    "grey",
    "red",
    "blue",
    "green",
    "yellow",
    "orange",
    "pink"
]
precisions = ["0 (int)", "1", "2"]
colors = [
    "<auto>",
    "grey",
    "red",
    "green",
    "blue",
    "#06038D",
    "#FE5BAC",
]
fonts = [
    "<auto>",
    "Arial",
    "Courier",
    "Comic Sans MS",
    "Helvetica",
    "Times New Roman",
]
prefixes = [
    "$",
    "€",
    "£",
    "￥",
    "±",
    "None"
]
suffixes = [
    "%",
    "‰",
    "x",
    "None"
]

# Formfield tooltip texts
tip_text_0 = """Pick a gradient or named color, or: 
                Any valid tkinter color, named or hex code."""
tip_text_1 = """Color of ticks and thumb. 
                Any valid tkinter color, named or hex code."""
tip_text_2 = "Any valid tkinter color, named or hex code."
tip_text_3 = "Any valid tkinter font"

# Formfields
basic_fields = [
    # orientation
    {
        "kwarg_name": "orientation",
        "kwarg_type": "str",
        "kwarg_label_text": "Horizontal or vertical",
        "default_val": "horizontal",
        "widget_type": "combo",
        "widget_readonly": True,
        "values": ["horizontal", "vertical"],
    },
    # relief
    {
        "kwarg_name": "relief",
        "kwarg_type": "str",
        "kwarg_label_text": "Borderstyle",
        "default_val": "flat",
        "widget_type": "combo",
        "widget_readonly": True,
        "values": borders,
    },
    # show_top_label
    {
        "kwarg_name": "show_top_label",
        "kwarg_type": "bool",
        "kwarg_label_text": "Show current value",
        "default_val": 1,
        "widget_type": None,
        "widget_readonly": False,
        "values": None,
    },
    # show_ticks
    {
        "kwarg_name": "show_ticks",
        "kwarg_type": "bool",
        "kwarg_label_text": "Show ticks",
        "default_val": 1,
        "widget_type": None,
        "widget_readonly": False,
        "values": None,
    },
    # show_minor_ticks
    {
        "kwarg_name": "show_minor_ticks",
        "kwarg_type": "bool",
        "kwarg_label_text": "Show minor ticks",
        "default_val": 0,
        "widget_type": None,
        "widget_readonly": False,
        "values": None,
    },
    # show_bottom_labels
    {
        "kwarg_name": "show_bottom_labels",
        "kwarg_type": "bool",
        "kwarg_label_text": "Show bottom labels",
        "default_val": 1,
        "widget_type": None,
        "widget_readonly": False,
        "values": None,
    },
    # snap_to_ticks
    {
        "kwarg_name": "snap_to_ticks",
        "kwarg_type": "bool",
        "kwarg_label_text": "Snap to ticks",
        "default_val": 0,
        "widget_type": None,
        "widget_readonly": False,
        "values": None,
    },

]
track_thumb_fields = [
    # width
    {
        "kwarg_name": "track_length",
        "kwarg_type": "int",
        "kwarg_label_text": "Track length",
        "default_val": "<auto>",
        "widget_type": "entry",
        "widget_readonly": False,
        "values": None,
    },
    # height
    {
        "kwarg_name": "track_width",
        "kwarg_type": "int",
        "kwarg_label_text": "Track width",
        "default_val": "<auto>",
        "widget_type": "entry",
        "widget_readonly": False,
        "values": None,
    },
    # track_style
    {
        "kwarg_name": "track_style",
        "kwarg_type": "str",
        "kwarg_label_text": "Track style",
        "default_val": "plane",
        "widget_type": "combo",
        "widget_readonly": True,
        "values": track_styles,
    },
    # track_relief
    {
        "kwarg_name": "track_relief",
        "kwarg_type": "str",
        "kwarg_label_text": "Track relief style",
        "default_val": "sunken",
        "widget_type": "combo",
        "widget_readonly": True,
        "values": borders,
    },
    # thumb_style
    {
        "kwarg_name": "thumb_style",
        "kwarg_type": "str",
        "kwarg_label_text": "Thumb style",
        "default_val": "classic",
        "widget_type": "combo",
        "widget_readonly": True,
        "values": thumb_styles,
    }
]
colors_fonts_fields = [
    # track_bg
    {
        "kwarg_name": "track_bg",
        "kwarg_type": "str",
        "kwarg_label_text": "Track background",
        "tool_tip_txt": tip_text_0,
        "default_val": "None",
        "widget_type": "combo",
        "widget_readonly": False,
        "values": track_backgrounds,
    },
    # color
    {
        "kwarg_name": "color",
        "kwarg_type": "str",
        "kwarg_label_text": "Color",
        "tool_tip_txt": tip_text_1,
        "default_val": "<auto>",
        "widget_type": "combo",
        "widget_readonly": False,
        "values": colors,
    },
    # font_color
    {
        "kwarg_name": "font_color",
        "kwarg_type": "str",
        "kwarg_label_text": "Font color",
        "tool_tip_txt": tip_text_2,
        "default_val": "<auto>",
        "widget_type": "combo",
        "widget_readonly": False,
        "values": colors,
    },
    # font
    {
        "kwarg_name": "font",
        "kwarg_type": "str",
        "kwarg_label_text": "Font",
        "tool_tip_txt": tip_text_3,
        "default_val": "<auto>",
        "widget_type": "combo",
        "widget_readonly": False,
        "values": fonts,
    },
    # font_size
    {
        "kwarg_name": "font_size",
        "kwarg_type": "int",
        "kwarg_label_text": "Font size",
        "default_val": "<auto>",
        "widget_type": "entry",
        "widget_readonly": False,
        "values": None,
    },
    # font bold
    {
        "kwarg_name": "font_bold",
        "kwarg_type": "bool",
        "kwarg_label_text": "Bold",
        "default_val": 0,
        "widget_type": None,
        "widget_readonly": False,
        "values": None,
    },
    # font italic
    {
        "kwarg_name": "font_italic",
        "kwarg_type": "bool",
        "kwarg_label_text": "Italic",
        "default_val": 0,
        "widget_type": None,
        "widget_readonly": False,
        "values": None,
    },
]
advanced_fields = [
    # start_value
    {
        "kwarg_name": "start_value",
        "kwarg_type": "float",
        "kwarg_label_text": "Start value",
        "default_val": "0",
        "widget_type": "entry",
        "widget_readonly": False,
        "values": None,
    },
    # end_value
    {
        "kwarg_name": "end_value",
        "kwarg_type": "float",
        "kwarg_label_text": "End value",
        "default_val": "100",
        "widget_type": "entry",
        "widget_readonly": False,
        "values": None,
    },
    # initial_value
    {
        "kwarg_name": "initial_value",
        "kwarg_type": "float",
        "kwarg_label_text": "Inital value",
        "default_val": "None",
        "widget_type": "entry",
        "widget_readonly": False,
        "values": None,
    },
    # num_ticks
    {
        "kwarg_name": "num_ticks",
        "kwarg_type": "int",
        "kwarg_label_text": "Number of ticks",
        "default_val": "10",
        "widget_type": "entry",
        "widget_readonly": False,
        "values": None,
    },
    # precision
    {
        "kwarg_name": "precision",
        "kwarg_type": "int",
        "kwarg_label_text": "Precision",
        "default_val": "0 (int)",
        "widget_type": "combo",
        "widget_readonly": False,
        "values": precisions,
    },
    # prefix
    {
        "kwarg_name": "prefix",
        "kwarg_type": "str",
        "kwarg_label_text": "Prefix",
        "default_val": "None",
        "widget_type": "combo",
        "widget_readonly": False,
        "values": prefixes,
    },
    # suffix
    {
        "kwarg_name": "suffix",
        "kwarg_type": "str",
        "kwarg_label_text": "Suffix",
        "default_val": "None",
        "widget_type": "combo",
        "widget_readonly": False,
        "values": suffixes,
    }
]

# PREBUILT SLIDERS
prebuilts = {
    "Default": {
    },
    "Precise": {
        'show_minor_ticks': True,
        'track_width': 15,
        'track_relief': "ridge",
        'track_bg': '#696969',
        'start_value': 0.0,
        'end_value': 1.0,
        'num_ticks': 5,
        'precision': 2,
    },
    "Balance": {
        'orientation': 'vertical',
        'show_top_label': False,
        'show_ticks': False,
        'snap_to_ticks': True,
        'track_length': 300,
        'track_style': 'line',
        'thumb_style': 'dot',
        'color': '#06038D',
        'font_color': '#06038D',
        'start_value': -5.0,
        'end_value': 5.0,
        'initial_value': 0,
    },
    "Gradient": {
        'show_top_label': False,
        'show_ticks': False,
        'track_length': 250,
        'track_bg': 'green_to_red',
        'end_value': 100,
        'initial_value': 87,
        'num_ticks': 4,
        'suffix': '%',
    },
    "Switch": {
        'show_top_label': False,
        'show_ticks': False,
        'snap_to_ticks': True,
        'track_length': 75,
        'track_width': 30,
        'track_bg': '#C21807',
        'font': 'Courier',
        'font_size': 16,
        'end_value': 1.0,
        'initial_value': 1.0,
        'num_ticks': 1,
    },
}

# HELP TEXT
help_text = """# Minimal implementation:

import tkinter as tk
from slider import Slider


root = tk.Tk()

my_slider = Slider(
    root,
    # options
)
my_slider.pack()

tk.Button(
    text="Disable",
    command=lambda: my_slider.disable()
).pack(side=tk.RIGHT)

tk.Button(
    text="Enable",
    command=lambda: my_slider.enable()
).pack(side=tk.RIGHT)

get_var = tk.IntVar()
tk.Label(
    width=5,
    textvariable=get_var,
    fg="blue",
    anchor=tk.W
).pack(side=tk.RIGHT)

tk.Button(
    text="Get >",
    command=lambda: get_var.set(my_slider.get())
).pack(side=tk.RIGHT)

tk.Button(
    text="< Set",
    command=lambda: my_slider.set(entry.get())
).pack(side=tk.RIGHT)

entry = tk.Entry(width=5, fg="blue")
entry.pack(side=tk.RIGHT)
tk.Label(text="Enter a value:").pack(side=tk.RIGHT)

tk.Label(
    textvariable=my_slider.value,
    width=6,
    fg="blue",
    anchor=tk.W,
).pack(side=tk.RIGHT)
tk.Label(text="Current value:").pack(side=tk.RIGHT)

root.mainloop()

"""