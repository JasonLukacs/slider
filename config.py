# Definitions of formfields and prebuilt sliders

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
    "triangle",
    "pointer",
    "crosshair",
]
track_styles = ["plane", "line"]

gradients = [
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
    "blue",
    "green",
    "yellow",
    "orange",
    "pink"
]

# Formfield tooltip texts
tip_text_1 = "Any valid tkinter color, named or hex code."
tip_text_2 = (
    "tkinter style font definition:\n"
    "Font family, [size, option option]\n"
    "Helvetica, 14, bold italic\n"
    "Times, 18"
)
# Formfields
basic_fields = [
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
    # width
    {
        "kwarg_name": "width",
        "kwarg_type": "int",
        "kwarg_label_text": "Width",
        "default_val": "<auto>",
        "widget_type": "entry",
        "widget_readonly": False,
        "values": None,
    },
    # height
    {
        "kwarg_name": "height",
        "kwarg_type": "int",
        "kwarg_label_text": "Height",
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
    # track_bg
    {
        "kwarg_name": "track_bg",
        "kwarg_type": "str",
        "kwarg_label_text": "Track background",
        "default_val": "None",
        "widget_type": "combo",
        "widget_readonly": False,
        "values": gradients,
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
colors_fonts_fields = [
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
    # font
    {
        "kwarg_name": "font",
        "kwarg_type": "str",
        "kwarg_label_text": "Font",
        "tool_tip_txt": tip_text_2,
        "default_val": "<auto>",
        "widget_type": "entry",
        "widget_readonly": False,
        "values": None,
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
    # font_color
    {
        "kwarg_name": "font_color",
        "kwarg_type": "str",
        "kwarg_label_text": "Font color",
        "tool_tip_txt": tip_text_1,
        "default_val": "<auto>",
        "widget_type": "combo",
        "widget_readonly": False,
        "values": colors,
    },

]
numerical_fields = [
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
        "default_val": "0",
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
    }
]

# PREBUILT SLIDERS
prebuilt_defs = {
    "Classic": {
    },
    "Blue lagoon": {
        'track_style': 'line',
        'thumb_style': 'dot',
        'color': '#06038D',
        'font_color': '#06038D',
        'show_top_label': False,
        'show_ticks': False,
        'show_bottom_labels': False,
    },
    "Balance": {
        'track_style': 'line',
        'thumb_style': 'dot',
        'color': '#06038D',
        'font_color': 'grey',
        'show_top_label': False,
        'show_ticks': False,
        'start_value': -5.0,
        'end_value': 5.0,
        'initial_value': 0,
        'snap_to_ticks': True,
    },
    "Precise": {
        'relief': 'groove',
        'width': 500,
        'height': 10,
        'font': "Courier",
        'track_bg': "#696969",
        'start_value': 0.0,
        'end_value': 1.0,
        'initial_value': 0.15,
        'num_ticks': 10,
        'show_minor_ticks': True,
        'precision': 2,
    },
    "Big laugh": {
        'track_style': 'line',
        'thumb_style': 'pointer',
        'width': 600,
        'color': '#964B00',
        'font_color': '#663300',
        'font': 'Comic Sans MS, 20, bold italic',
        'end_value': 1000.0,
        'num_ticks': 4,
    },
    "Gradient alarm": {
        'track_bg': 'green_to_red',
        'show_top_label': False,
        'show_ticks': False,
        'initial_value': 80,
    },
    "Gradient ocean": {
        'track_bg': 'white_to_blue',
        'show_top_label': False,
        'show_ticks': False,
        'initial_value': 80,
    },
    "Sniper": {
        "width": 200,
        'track_style': 'line',
        "thumb_style": 'crosshair',
        'show_top_label': False,
        'show_ticks': False,
        'snap_to_ticks': True,
        'color': 'grey',
        'font_color': 'grey',
        'end_value': 5.0,
        'initial_value': 4.0,
        'num_ticks': 5,
    },
    "Switch": {
        'relief': 'raised',
        'width': 100,
        'height': 60,
        "track_bg": "#696969",
        'font': "Courier",
        'font_color': 'grey',
        'font_size': 24,
        'show_top_label': False,
        'show_ticks': False,
        'start_value': 0.0,
        'end_value': 1.0,
        'initial_value': 1,
        'num_ticks': 1,
        'snap_to_ticks': True,
    }
}
