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


Slider, a highly configurable, pure tkinter alternative for tkinter.Scale.

Consider using build.py to configure your slider and associated code.
Run to see a mini-showcase.

Public class: Slider
"""

import warnings
import decimal
from decimal import Decimal
import tkinter as tk
import tkinter.font as tk_font

# tk literals
MOUSE_WHEEL = "<MouseWheel>"
BUTTON = "<Button>"
MOTION = "<Motion>"
BUTTON_RELEASE = "<ButtonRelease>"


class Slider(tk.Frame):
    """ Create a slider.
    Consider using build.py to configure your slider and associated code.

    Usage:
    Slider(parent, options)

    Examples:
    my_slider = Slider(parent)
    my_slider = Slider(parent, orientation="vertical")
    pack, grid or place my_slider

    Methods:
    my_slider.set(value) to set slider
    my_slider.get() to get current value
    my_slider.disable() to disable all user interaction
    my_slider.enable() to resuscitate disabled slider
    Use my_slider.value as (text)variable in a widget, or bind it to
    your handler to automatically retrieve the slider value.
    Alternatively, use my_slider.add_subscriber(var) to have your
    own tk_Var be updated automatically.

    Args:

    parent:
        Tk window or frame

    Keyword Args:

    relief: Literal["raised", "sunken", "flat", "ridge", "solid", "groove"]
        Style of the outer border
    show_top_label: bool
        Show a co-sliding label displaying the current slider value
    show_ticks: bool
        Show a bar displaying tick marks
    show_minor_ticks: bool
        Add secondary tick marks to tick bar
    show_bottom_labels: bool
        Show a bar displaying values on the tick width interval
    snap_to_ticks: bool
        Set thumb and return value to the nearest tick after user input
    orientation: Literal["horizontal", "vertical"]
        Orientation of the slider, either sliding left-right or up-down
    track_length: int
        Width of a horizontal slider / height of a vertical slider
    track_width: int
        Height of a horizontal slider / width of a vertical slider
    track_style: Literal["plane", "line"]
        Style of the track, either a classic plane or a solid line
    track_relief: Literal["raised", "sunken", "flat", "ridge", "solid", "groove"]
        Border style for a "plane" style track
    track_bg: Optional[Union[Literal["green_to_red", "white_to_blue"], str]]
        Background for the track, either a named gradient, a named
        color or a hex value (as a string)
    thumb_style: Literal["classic", "dot", "diamond", "pointer", "crosshair", "cube"]
        Choose a thumb to your liking.
    font: Optional[str]
        Name of an available tkinter font
    font_size: Optional[int]
        Size of the font, anything between circa 8 - 24 will go
    font_bold: bool
        Bold font
    font_italic: bool
        Italic font
    start_value: Union[int, float]
        Most left, or bottom, value of the slider, negative values allowed
    end_value: Union[int, float]
        Most right, or top, value of the slider
    initial_value: Optional[Union[int, float]]
        Value at creation, defaults to start_value
    num_ticks: int
        Number of ticks, used for number of tick marks and number of values
        displayed in the bottom label bar. Set sensibly.
    precision: int
        Number of decimals to show and to return
    prefix: str
        Text to display after the values in top label and
        bottom labels. This text is not included in return values
    suffix: str
        Text to display after the values in top label and
        bottom labels. This text is not included in return values

    Returns:
        Self
    """

    def __init__(self, parent, **kwargs):
        relief = kwargs.get('relief', "flat")
        show_top_label = kwargs.get('show_top_label', True)
        show_ticks = kwargs.get('show_ticks', True)
        show_bottom_labels = kwargs.get('show_bottom_labels', True)

        super().__init__(parent, bd=3, pady=5, padx=5, relief=relief)

        # Create model & controller
        self.model = _SliderModel(**kwargs)
        self.engine = _SliderEngine(self.model)

        # Create graphical elements, top to bottom
        # because elements will pack themselves
        slider_kwargs = {
            "parent": self,
            "model": self.model,
            "engine": self.engine
        }

        if show_top_label:
            self.top_label = _TopLabel(**slider_kwargs)
        self.track = _Track(**slider_kwargs)
        if show_ticks:
            self.ticks = _Ticks(**slider_kwargs)
        if show_bottom_labels:
            self.bottom_labels = _BottomLabels(**slider_kwargs)

        # Publish slider return value as self.value
        self.value = self.engine.ret_val

        # Start & initialize
        self.enable()
        self.set(self.model.initial_value)

    def set(self, value):
        """ Set slider programmatically. """
        self.engine.set(value)

    def get(self):
        """ Get current slider value. """
        return self.value.get()

    def enable(self):
        """ Enable user interaction with slider. """
        self.engine.start()

    def disable(self):
        """ Disable user interaction, slider can still be set
        programmatically. """
        self.engine.stop()

    def add_subscriber(self, var):
        """ Add a custom tk.Var to be updated automatically. """
        self.engine.add_subscriber(var)


class _SliderModel:
    """ Simple container for calculating and serving predominantly
    static parameters.
    Public methods:
    disable(): set colors to "grey" to indicate disabled state
    enable(): set colors to requested value
    """
    def __init__(self, **kwargs):
        orientation = kwargs.get('orientation', 'horizontal')
        track_style = kwargs.get('track_style', 'plane')
        track_relief = kwargs.get('track_relief', 'sunken')
        thumb_style = kwargs.get('thumb_style', 'classic')
        track_length = kwargs.get('track_length', 400)
        track_width = kwargs.get('track_width', 20)
        color = kwargs.get('color', 'black')
        font_color = kwargs.get('font_color', '#000000')
        font = kwargs.get('font', None)
        font_size = kwargs.get('font_size', None)
        font_bold = kwargs.get('font_bold', False)
        font_italic = kwargs.get('font_italic', False)
        track_bg = kwargs.get('track_bg', None)
        start_value = kwargs.get('start_value', 0.0)
        end_value = kwargs.get('end_value', 100.0)
        initial_value = kwargs.get('initial_value', None)
        show_minor_ticks = kwargs.get('show_minor_ticks', False)
        num_ticks = kwargs.get('num_ticks', 10)
        precision = kwargs.get('precision', 0)
        prefix = kwargs.get('prefix', '')
        suffix = kwargs.get('suffix', '')
        snap_to_ticks = kwargs.get('snap_to_ticks', False)

        """ Check validity of range """
        if start_value == end_value:
            raise ValueError("Invalid range, set proper start and end value")

        """ Set general appearance and behaviour """
        self.orientation = orientation
        self.track_style = track_style
        self.track_relief = track_relief
        self.thumb_style = thumb_style
        self.track_bg = track_bg
        self.show_minor_ticks = show_minor_ticks
        self.snap_to_ticks = snap_to_ticks

        """ Set numerical attributes """
        self.precision = precision
        self.start_value = round(start_value, self.precision or None)
        self.end_value = round(end_value, self.precision or None)
        # Differentiate between None and 0 as range may span 0
        if initial_value is None:
            self.initial_value = self.start_value
        else:
            self.initial_value = initial_value
        self.prefix = prefix
        self.suffix = suffix

        # min/max for clamp as range may be descending
        self.min_value = min(self.start_value, self.end_value)
        self.max_value = max(self.start_value, self.end_value)

        # Set maximum number of ticks to prevent duplication of tick
        # values on the label bar
        self.num_ticks = num_ticks
        value_range = self.end_value - self.start_value
        # numerical distance between ticks
        self.tick_width_num = value_range / self.num_ticks

        if abs(self.tick_width_num) < 1 / 10**self.precision:
            self.num_ticks = abs(value_range * 10**self.precision)
            self.tick_width_num = value_range / self.num_ticks
            txt = f"Too many ticks set, adjusted to {self.num_ticks}"
            warnings.warn(txt)

        # Set precision of return value to None to prevent round()
        # from returning a decimal when set precision == 0
        self.ret_val_precision = self.precision or None

        """ Set font and font-size specific attributes """
        font_name = font or "TkDefaultFont"
        self.font_size = font_size
        self.font_color_requested = font_color
        self.font_color = self.font_color_requested

        if self.font_size:
            self.font_size = font_size
        else:
            self.font_size = (
                abs(tk_font.nametofont("TkDefaultFont").cget("size"))
            )

        # Finalize font
        self.font = tk_font.Font(font=(font_name, self.font_size))
        if font_bold:
            self.font.config(weight="bold")
        if font_italic:
            self.font.config(slant="italic")

        # Get dimensions of the longest possible text. Note this might
        # be the lowest value if negative (e.g. slider range -1, 0)
        long_value = self.max_value if (
                len(f"{self.max_value}") > len(f"{self.min_value}")
        ) else self.min_value

        text = f"{self.prefix}{long_value}{self.suffix}"
        max_text_width = self.font.measure(text) + 30  # don't ask
        text_height = self.font.metrics("linespace")

        """ Set color of thumb and ticks """
        self.color_requested = color
        self.color = self.color_requested

        """ Set graphical dimensions """
        # Dimensions are calculated irrespective of orientation.
        # All elements have a short and a long side. Long side wil
        # become height for a "vertical" slider and width for a
        # "horizontal" slider. Dito but the other way around for the
        # short side.

        self.length = track_length
        self.width = track_width

        # Set thumb dimensions
        if self.thumb_style == "classic":
            # Allow for some space for classic button within the track
            self.track_padding = 4
            thumb_long_side = max(int(self.length / 10), 40)
        else:
            self.track_padding = 0
            thumb_long_side = 30

        thumb_short_side = self.width

        # Set preliminary track dimensions
        track_short_side = thumb_short_side
        track_slide_length = self.length - thumb_long_side

        # Set tick bar dimensions
        tick_bar_short_side = max(10, int(0.5 * text_height))
        self.tick_width = int(track_slide_length / self.num_ticks)
        # offset to center ticks on center of thumb
        self.tick_start = int(thumb_long_side * 0.5)

        # Set final dimensions based on num_ticks * tick_width to
        # account for setting tick_width to integer
        self.length = int(
                thumb_long_side
                + self.num_ticks * self.tick_width
        )
        track_long_side = self.length
        track_slide_length = self.length - thumb_long_side

        # Padding, essential to prevent elements from moving relative to
        # each other when user resizes the containing window
        self.bar_pad_y = 0
        self.bar_pad_x = 0
        self.outer_padding = 0

        """ Finalize numerical dimensions """
        # Set factor to convert thumb displacement to change in
        # slider value
        self.displacement_to_value = value_range / track_slide_length

        """ Generics are done, set orientation-specific dimensions """

        if self.orientation == "horizontal":
            self.pack_side = tk.TOP
            self.outer_padding = 25
            if self.track_style == "plane":
                # Compensate for track border (3) + track padding (4)
                self.bar_pad_x = 7
            # Hard coded extension to label_bar_width (and padding)
            # allows for values up to circa 10**4, font size 24
            # for horizontal sliders, where text width is limited
            self.label_bar_width = self.length + 50
            self.label_bar_height = text_height
            self.top_label_bar_height = (
                    self.label_bar_height
                    + tick_bar_short_side
            )
            self.top_label_width = 2 * thumb_long_side
            self.top_label_height = self.label_bar_height
            self.track_width = track_long_side
            self.track_height = track_short_side
            self.thumb_width = thumb_long_side
            self.thumb_height = thumb_short_side
            self.tick_bar_width = self.length
            self.tick_bar_height = tick_bar_short_side
            self.text_start_x = self.thumb_width * 0.5 + 25  # 50/2

        elif self.orientation == "vertical":
            self.pack_side = tk.RIGHT
            if self.track_style == "plane":
                # Compensate track border (3) + padding (4)
                self.bar_pad_y = 7
            self.label_bar_width = max_text_width
            self.label_bar_height = self.length
            self.top_label_bar_height = self.label_bar_height
            self.top_label_width = self.label_bar_width
            self.top_label_height = thumb_long_side
            self.track_width = track_short_side
            self.track_height = track_long_side
            self.thumb_width = thumb_short_side
            self.thumb_height = thumb_long_side
            self.tick_bar_width = tick_bar_short_side
            self.tick_bar_height = self.length
            self.text_start_x = self.tick_bar_width
            self.text_start_y = self.thumb_height * 0.5

    def enable(self):
        """ Adjust color scheme when slider is enabled """
        self.font_color = self.font_color_requested
        self.color = self.color_requested

    def disable(self):
        """ Adjust color scheme when slider is disabled """
        self.font_color = "grey"
        self.color = "grey"


class _SliderEngine:
    """ Controller class.
    Public methods:
    start(): enable user interaction with the slider
    stop(): disable user interaction, slider can be set though
    set(): set slider value programmatically
    add_subscriber(): ad a custom tk variable to be auto-updated
    """
    def __init__(self, model):
        self.model = model
        self.trace_ids = []
        self.subscriber = None

        # Init context and static helper var for decimal calculations
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP
        self.tick_width_dec = Decimal(f"{self.model.tick_width_num}")

        # on/off switch of the whole thing
        self.state = tk.BooleanVar()
        # Current internal value of the slider
        self.slider_value = tk.DoubleVar()
        # Create return value and trace slider_value to auto-update it
        self.ret_val = tk.DoubleVar() if self.model.precision else tk.IntVar()
        self.slider_value.trace_add("write", self._set_ret_val)

        # Slider elements will set one of the following vars to
        # communicate requested displacement, each one is bound to a
        # specific method in self.start()
        self.slide = tk.IntVar()
        self.slide_fast = tk.IntVar()
        self.slide_snapped = tk.IntVar()

        self.traced_vars = (self.slide, self.slide_fast, self.slide_snapped)
        self.funcs = (self._slide, self._slide_fast, self._slide_snapped)

    def start(self):
        """ Enable the slider by setting a trace on the variables
        through which slider elements communicate mouse events.
        Status check to prevent redundant traces when called multiple
        times.
        """
        if not self.state.get():
            self.model.enable()
            self.state.set(True)
            self.trace_ids = [
                var.trace_add("write", func)
                for var, func in zip(self.traced_vars, self.funcs)
            ]
        else:
            warnings.warn("Attempt to enable already enabled slider.")

    def stop(self):
        """ Disable the slider by removing the trace on the variables
        used to communicate mouse movements. Note the slider *can* be
        set programmatically when disabled.
        Status check to prevent ugly errors when called multiple times.
        """
        if self.state.get():
            self.model.disable()
            self.state.set(False)
            for var, trace_id in zip(self.traced_vars, self.trace_ids):
                var.trace_remove("write", trace_id)
        else:
            warnings.warn("Attempt to disable already disabled slider.")

    def _slide(self, *_):
        """ Change slider_value proportional to displacement.
        Use case: simple sliding left or right.
        """
        self.slider_value.set(
            self._clamp(
                    self.slider_value.get()
                    + (self.slide.get()
                       * self.model.displacement_to_value)
            )
        )

    def _slide_fast(self, *_):
        """ Change slider_value in units of tick width per unit of
        displacement.
        Use case: accelerated sliding with mousewheel or trackpad
        """
        if self.slider_value.get() == self._snap(self.slider_value.get()):
            # Slider is snapped, change slider_value in units of
            # numerical tick width
            self.slider_value.set(
                self._clamp(
                    self.slider_value.get()
                    + self.slide_fast.get()
                    * self.model.tick_width_num
                )
            )
        else:
            # Slider is not snapped. Snap to nearest higher tick value
            # if movement is upwards, snap to nearest lower tick value
            # if movement is downwards.
            self.slider_value.set(
                self._clamp(
                    # Bump 0.5 tick width in the direction of travel,
                    # snap() will finish the job
                    self._snap(
                        self.slider_value.get()
                        + (-1 if self.slide_fast.get() < 0 else 1)
                        * 0.5 * self.model.tick_width_num
                    )
                )
            )

    def _slide_snapped(self, *_):
        """ Change slider_value proportional to displacement and snap it
        to the nearest tick afterwards.
        Use case: automatically snap the slider when clicking the
        track.
        """
        self.slider_value.set(
            self._clamp(
                # Move to clicked position in track, bump 0.5 tick_width
                # in the direction of travel and snap() will finish the
                # job
                self._snap(
                    self.slider_value.get()
                    + (self.slide_snapped.get()
                       * self.model.displacement_to_value)
                    + (-1 if self.slide_snapped.get() < 0 else 1)
                    * 0.5 * self.model.tick_width_num
                )
            )
        )

    def snap_slider(self, *_):
        """ Set slider_value to the nearest tick.
        Use case: Snap the slider upon button release (after dragging)
        when snap_to_tick option is set.
        """
        self.slider_value.set(
            self._snap(self.slider_value.get())
        )

    def set(self, value):
        """ Set slider programmatically """
        try:
            if self.model.precision:
                requested_value = float(value)
            else:
                requested_value = int(float(value))
        except ValueError:
            txt = f"Invalid value '{value}', slider not set"
            raise ValueError(txt)

        if requested_value != self._clamp(requested_value):
            txt = f"'{value}' outside valid range, slider not set"
            raise ValueError(txt)

        if self.model.snap_to_ticks:
            self.slider_value.set(self._snap(requested_value))
        else:
            self.slider_value.set(requested_value)

    def _set_ret_val(self, *_):
        """ Set return value rounded to set precision. """
        self.ret_val.set(
            round(self.slider_value.get(), self.model.ret_val_precision)
        )

    def _clamp(self, num):
        """ Keep slider value in between start- and end value. """
        return min(max(self.model.min_value, num), self.model.max_value)

    def _snap(self, value):
        """ Return the numeric value of the tick nearest to value. """
        # Float characteristics and rounding will lead to the slider
        # showing a value that could contradict snap behaviour, e.g.
        # true value 34.9, showing as 35 but snapping to 30.
        # To mitigate, do the math with decimals.
        # Calculate: value/tick width, round half up, now we have an
        # integer number of tick widths, multiply by tick width.
        return (
            int(
                (Decimal(f"{value:.{self.model.precision}f}")
                 / self.tick_width_dec).quantize(Decimal("1"))
                )
            * self.model.tick_width_num
        )

    def add_subscriber(self, var):
        """ Add your own tk variable to be automatically set to current
        value of the slider.
        """
        if isinstance(var, (tk.IntVar, tk.DoubleVar)):
            self.ret_val.trace_add(
                "write",
                lambda *_: var.set(self.ret_val.get())
            )
            # Initialize external var
            var.set(self.ret_val.get())
        else:
            txt = f"{repr(var)} must be IntVar or DoubleVar"
            raise ValueError(txt)


class _TopLabel:
    """ Create co-sliding label showing current value. """
    def __init__(self, parent, model, engine):
        self.model = model
        self.engine = engine

        label_frame = tk.Frame(
            parent,
            padx=model.bar_pad_x,
            pady=model.bar_pad_y,
        )
        label_frame.pack(side=model.pack_side)

        self.bar = tk.Canvas(
            label_frame,
            width=self.model.label_bar_width,
            height=self.model.top_label_bar_height,
            highlightthickness=0,  # don't ask
        )
        self.bar.pack()

        # Catch mouse wheel events in label bar for usability
        self.bar.bind(
            MOUSE_WHEEL,
            lambda event: self.engine.slide_fast.set(event.delta)
        )

        # Set orientation-appropriate update function
        if self.model.orientation == "horizontal":
            self._set = self._set_hor
        elif self.model.orientation == "vertical":
            self._set = self._set_vert

        # Redraw self when slider value has changed or slider is
        # disabled / enabled
        for var in (self.engine.state, self.engine.slider_value):
            var.trace_add("write", self._set)

    def _set_hor(self, *_):
        """ Update top label of horizontal slider. """
        self.bar.delete("top_label_txt")
        self.bar.create_text(
            (
                (self.engine.slider_value.get() - self.model.start_value)
                / self.model.displacement_to_value
                + self.model.text_start_x
            ),
            self.model.top_label_bar_height * 0.5,
            text=(
                f"{self.model.prefix}"
                f"{self.engine.slider_value.get():.{self.model.precision}f}"
                f"{self.model.suffix}"
            ),
            tags="top_label_txt",
            font=self.model.font,
            fill=self.model.font_color,
            anchor=tk.CENTER
        )

    def _set_vert(self, *_):
        """ Update top label of vertical slider. """
        self.bar.delete("top_label_txt")
        self.bar.create_text(
            self.model.text_start_x,
            (
                (self.model.end_value - self.engine.slider_value.get())
                / self.model.displacement_to_value
                + self.model.text_start_y
            ),
            text=(
                f"{self.model.prefix}"
                f"{self.engine.slider_value.get():.{self.model.precision}f}"
                f"{self.model.suffix}"
            ),
            tags="top_label_txt",
            font=self.model.font,
            fill=self.model.font_color,
            anchor=tk.W,
        )


class _Track:
    """ Create the slider track, the thumb and the track background. """
    def __init__(self, parent, model, engine):
        self.model = model
        self.engine = engine
        self.track_clicked = False

        # Create generic track
        track_frame = tk.Frame(
            parent,
            bd=3,
            relief=self.model.track_relief,
            padx=self.model.track_padding,
            pady=self.model.track_padding
        )
        track_frame.pack(
            side=self.model.pack_side,
            padx=self.model.outer_padding
        )

        self.track = tk.Canvas(
            track_frame,
            width=self.model.track_width,
            height=self.model.track_height,
            highlightthickness=0,
        )
        self.track.pack()

        # Catch mouse wheel events in track for usability
        self.track.bind(
            MOUSE_WHEEL,
            lambda event: self.engine.slide_fast.set(event.delta)
        )

        # Reconfigure track if style applies
        if self.model.track_style == "line":
            track_frame["relief"] = tk.FLAT
            track_frame["bd"] = 0
            self._draw_line()

            # Redraw self when slider is disabled/enabled
            self.engine.state.trace_add("write", self._draw_line)

        # Create the thumb
        self.thumb = _Thumb(
            parent=self.track,
            model=self.model,
            engine=self.engine
        )

        # Create track background
        if self.model.track_bg:
            self.bg = _TrackBackground(
                self.model,
                self.engine,
                self.track,
                self.thumb
            )

        # Enable clicking and dragging in the track
        if self.model.orientation == "horizontal":
            self.track.bind(BUTTON, self._click_hor)
            self.track.bind(MOTION, self._move_hor)
        elif self.model.orientation == "vertical":
            self.track.bind(BUTTON, self._click_vert)
            self.track.bind(MOTION, self._move_vert)

        self.track.bind(BUTTON_RELEASE, self._release)

    def _click_hor(self, event):
        # The track of a horizontal slider is clicked, so the user
        # wants the thumb to be moved left or right.
        self.track_clicked = True
        self.drag_start_x = event.x_root

        delta_x = event.x - self.thumb.position.get()
        if event.x > self.thumb.position.get():
            # Clicked to the right of thumb, subtract thumb width
            # to prevent awkwardly big jump of the thumb
            delta_x -= self.model.thumb_width

        # Clicking the track must snap by default, so set slide_snapped
        self.engine.slide_snapped.set(delta_x)

    def _click_vert(self, event):
        # The track of a vertical slider is clicked, so the user
        # wants the thumb to be moved up or down.
        self.track_clicked = True
        self.drag_start_y = event.y_root

        delta_y = self.thumb.position.get() - event.y
        if event.y > self.thumb.position.get():
            # Clicked below thumb, add thumb width
            # to prevent awkwardly big jump of the thumb
            delta_y += self.model.thumb_height

        # Clicking the track snaps by default, so set slide_snapped
        self.engine.slide_snapped.set(delta_y)

    def _move_hor(self, event):
        """ The mouse is moving in the track. If clicked, drag thumb."""
        if self.track_clicked:
            # Simple dragging, so set 'slide'
            self.engine.slide.set(event.x_root - self.drag_start_x)
            self.drag_start_x = event.x_root

    def _move_vert(self, event):
        """ The mouse is moving in the track. If clicked, drag thumb."""
        if self.track_clicked:
            # Simple dragging, so set 'slide'
            self.engine.slide.set(self.drag_start_y - event.y_root)
            self.drag_start_y = event.y_root

    def _release(self, *_):
        """ Button released, stop dragging and snap if appropriate. """
        self.track_clicked = False
        if self.model.snap_to_ticks:
            self.engine.snap_slider()

    def _draw_line(self, *_):
        if self.model.orientation == "horizontal":
            self.track.create_line(
                0,
                self.model.track_height * 0.5,
                self.model.track_width,
                self.model.track_height * 0.5,
                fill=self.model.color
            )
        elif self.model.orientation == "vertical":
            self.track.create_line(
                self.model.track_width * 0.5,
                0,
                self.model.track_width * 0.5,
                self.model.track_height,
                fill=self.model.color,
            )


class _TrackBackground:
    """ Draw track background
    Respond to changes in thumb position by drawing the requested
    background.
    """
    def __init__(self, model, engine, track, thumb):
        self.model = model
        self.track = track
        self.thumb = thumb
        self.engine = engine

        # Set self.draw_bg to the orientation-appropriate method
        # Gradient bg:
        if self.model.track_bg == "green_to_red":
            self.step_size = 510 / self.model.length
            self.draw_bg = (
                self._draw_green_to_red_hor
                if self.model.orientation == "horizontal"
                else self._draw_green_to_red_vert
            )
        elif self.model.track_bg == "white_to_blue":
            self.step_size = 200 / self.model.length
            self.draw_bg = (
                self._draw_white_to_blue_hor
                if self.model.orientation == "horizontal"
                else self._draw_white_to_blue_vert
            )
        # Solid bg:
        else:
            self.bg_color = self.model.track_bg
            self.draw_bg = (
                self._draw_solid_bg_hor
                if self.model.orientation == "horizontal"
                else self._draw_solid_bg_vert
            )
        self.draw_bg()

        # Trace thumb position to auto-update background
        self.thumb.position.trace_add("write", self.draw_bg)

        # Redraw self when slider is disabled/enabled
        self.engine.state.trace_add("write", self._toggle_state)

    def _draw_green_to_red_hor(self, *_):
        """ Draw gradient background, green to red """
        # Start green, decrease green and increase red. Some tweaks
        # for smoothness
        self.track.delete("track_bg")
        r = 0
        g = 255
        b = 0
        for x in range(int(self.thumb.position.get())):
            self.track.create_line(
                x,
                0,
                x,
                self.model.track_height,
                fill=f"#{int(r):02x}{int(g):02x}{int(b):02x}",
                tags="track_bg"
            )
            if r <= 255 - self.step_size:
                r += self.step_size
            elif r < 255:  # push to 255 if step_size too large
                r = 255
            if r >= 255:
                g -= self.step_size

    def _draw_white_to_blue_hor(self, *_):
        """ Draw gradient background, white to blue """
        # Start white, decrease red and green
        self.track.delete("track_bg")
        r = g = b = 255
        for x in range(int(self.thumb.position.get())):
            self.track.create_line(
                x,
                0,
                x,
                self.model.track_height,
                fill=f"#{int(r):02x}{int(g):02x}{int(b):02x}",
                tags="track_bg"
            )
            if r > 0 + self.step_size:
                r -= self.step_size
                g -= self.step_size

    def _draw_green_to_red_vert(self, *_):
        """ Draw gradient background, green to red """
        # Start green, decrease green and increase red. Some tweaks
        # for smoothness
        self.track.delete("track_bg")
        r = b = 0
        g = 255
        for y in range(
                self.model.track_height,
                int(self.thumb.position.get()),
                -1
        ):
            self.track.create_line(
                0,
                y,
                self.model.track_width,
                y,
                fill=f"#{int(r):02x}{int(g):02x}{int(b):02x}",
                tags="track_bg"
            )
            if r <= 255 - self.step_size:
                r += self.step_size
            elif r < 255:  # push to 255 if step_size too large
                r = 255
            if r >= 255:
                g -= self.step_size

    def _draw_white_to_blue_vert(self, *_):
        """ Draw gradient background, white to blue """
        # Start white, decrease red and green
        self.track.delete("track_bg")
        r = g = b = 255
        for y in range(
                self.model.track_height,
                int(self.thumb.position.get() + 0.5 * self.model.thumb_height),
                -1
        ):
            self.track.create_line(
                0,
                y,
                self.model.track_width,
                y,
                fill=f"#{int(r):02x}{int(g):02x}{int(b):02x}",
                tags="track_bg"
            )
            if r > 0 + self.step_size:
                r -= self.step_size
                g -= self.step_size

    def _draw_solid_bg_hor(self, *_):
        """ Draw a solid background for horizontal slider. """
        self.track.delete("track_bg")
        self.track.create_rectangle(
            0,
            0,
            int(self.thumb.position.get()),
            self.model.track_height,
            fill=self.bg_color,
            outline=self.bg_color,
            tags="track_bg"
        )

    def _draw_solid_bg_vert(self, *_):
        """ Draw a solid background for a vertical slider. """
        self.track.delete("track_bg")
        self.track.create_rectangle(
            0,
            int(self.thumb.position.get()) + self.model.thumb_height,
            self.model.track_width,
            self.model.track_height,
            fill=self.bg_color,
            tags="track_bg"
        )

    def _toggle_state(self, *_):
        if self.engine.state.get():
            self.draw_bg()
        else:
            self.track.delete("track_bg")


class _Thumb:
    """ Create a thumb """
    def __init__(self, parent, model, engine):
        self.parent = parent
        self.model = model
        self.engine = engine

        self.position = tk.DoubleVar()
        self._clicked = False

        # Create generic thumb frame
        self.thumb_frame = tk.Frame(
            self.parent,
            width=self.model.thumb_width,
            height=self.model.thumb_height,
        )

        # Put the frame in a canvas window, this is the object to move
        # Note, no pack() of this frame
        self.thumb = self.parent.create_window(
            0,
            0,
            anchor=tk.NW,
            window=self.thumb_frame
        )

        # Apply style
        if self.model.thumb_style == "classic":
            self._classic_thumb()
        else:
            self._graphical_thumb()
            # Redraw self when slider is disabled/enabled
            self.engine.state.trace_add("write", self.draw_thumb)

        # Set orientation appropriate functions
        if self.model.orientation == "horizontal":
            self._set = self._set_hor
            self._move = self._move_hor
        elif self.model.orientation == "vertical":
            self._set = self._set_vert
            self._move = self._move_vert

        # Enable thumb
        for element in self.thumb_elements:
            element.bind(BUTTON, self._click)
            element.bind(MOTION, self._move)
            element.bind(BUTTON_RELEASE, self._release)

            # Catch mouse wheel events in thumb elements for usability
            element.bind(
                MOUSE_WHEEL,
                lambda event: self.engine.slide_fast.set(event.delta)
            )

        # Trace slider_value to auto update thumb position
        self.trace_id = self.engine.slider_value.trace_add(
            "write",
            self._set
        )

    def _click(self, event):
        """ The thumb is clicked, future mouse events may be dragging
        the thumb to a new position.
        """
        self._clicked = True
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root

    def _move_hor(self, event):
        """ If the thumb is clicked and the mouse is being moved,
        drag the thumb.
        """
        if self._clicked:
            self.engine.slide.set(event.x_root - self.drag_start_x)
            self.drag_start_x = event.x_root

    def _move_vert(self, event):
        """ If the thumb is clicked and the mouse is being moved,
        drag the thumb.
        """
        if self._clicked:
            self.engine.slide.set(self.drag_start_y - event.y_root)
            self.drag_start_y = event.y_root

    def _release(self, *_):
        """ Button released, stop dragging and snap if appropriate. """
        self._clicked = False
        if self.model.snap_to_ticks:
            self.engine.snap_slider()

    def _set_hor(self, *_):
        """ Update position of thumb """
        # Set internal value of position
        self.position.set(
            (self.engine.slider_value.get() - self.model.start_value)
            / self.model.displacement_to_value
        )
        # Graphically move thumb
        self.parent.coords(self.thumb, self.position.get(), 0)

    def _set_vert(self, *_):
        """ Update position of thumb """
        # Set internal value of position
        self.position.set(
            (self.model.end_value - self.engine.slider_value.get())
            / self.model.displacement_to_value
        )
        # Graphically move thumb
        self.parent.coords(self.thumb, 0, self.position.get())

    def _classic_thumb(self):
        """ Create classic thumb, consisting of two adjacent
        raised frames to mimic buttons.
        """
        if self.model.orientation == "horizontal":
            width = self.model.thumb_width * 0.5
            height = self.model.thumb_height
            pack_side = tk.LEFT
        else:
            width = self.model.thumb_width,
            height = self.model.thumb_height * 0.5
            pack_side = tk.TOP

        self.thumb_btn_1 = tk.Frame(
            self.thumb_frame,
            width=width,
            height=height,
            bd=3,
            relief=tk.RAISED
        )
        self.thumb_btn_1.pack(side=pack_side)

        self.thumb_btn_2 = tk.Frame(
            self.thumb_frame,
            width=width,
            height=height,
            bd=3,
            relief=tk.RAISED
        )
        self.thumb_btn_2.pack(side=pack_side)

        self.thumb_elements = [
            self.thumb_btn_1,
            self.thumb_btn_2
        ]

    def _graphical_thumb(self):
        self.thumb_canvas = tk.Canvas(
            self.thumb_frame,
            width=self.model.thumb_width,
            height=self.model.thumb_height,
            highlightthickness=0,
        )
        self.thumb_canvas.pack(side=tk.LEFT)
        self.thumb_elements = [self.thumb_canvas]

        self.draw_thumb()

    def draw_thumb(self, *_):
        if self.model.thumb_style == "dot":
            self._dot()
        elif self.model.thumb_style == "diamond":
            self._diamond()
        elif self.model.thumb_style == "pointer":
            self._pointer()
        elif self.model.thumb_style == "crosshair":
            self._crosshair()
        elif self.model.thumb_style == "cube":
            self._cube()
        else:
            txt = f"Invalid thumb style: {self.model.thumb_style}"
            raise ValueError(txt)

    def _dot(self):
        """ Create a circle shaped thumb. """
        self.thumb_canvas.delete("thumb")
        self.thumb_canvas.create_oval(
            (self.model.thumb_width * 0.5) - 10,
            int(0.5*self.model.thumb_height - 9),
            (self.model.thumb_width * 0.5) + 9,
            int(0.5*self.model.thumb_height + 9),
            outline="white",
            width=3,
            fill=self.model.color,
            tags="thumb"
        )

    def _diamond(self):
        """ Create a diamond shaped thumb. """
        self.thumb_canvas.delete("thumb")
        self.thumb_canvas.create_polygon(
            self.model.thumb_width * 0.5,
            0,
            self.model.thumb_width-2,
            self.model.thumb_height * 0.5,
            self.model.thumb_width * 0.5,
            self.model.thumb_height,
            2,
            self.model.thumb_height * 0.5,
            outline="white",
            width=2,
            fill=self.model.color,
            tags="thumb"
        )

    def _pointer(self):
        """ Create a shaped thumb. """
        if self.model.orientation == "horizontal":
            self.thumb_canvas.delete("thumb")
            self.thumb_canvas.create_polygon(
                7,
                0,
                self.model.thumb_width - 8,
                0,
                self.model.thumb_width - 8,
                self.model.thumb_height * 0.5,
                self.model.thumb_width * 0.5,
                self.model.thumb_height,
                7,
                self.model.thumb_height * 0.5,
                outline="white",
                width=1,
                fill=self.model.color,
                tags="thumb"
            )
        elif self.model.orientation == "vertical":
            self.thumb_canvas.delete("thumb")
            self.thumb_canvas.create_polygon(
                0,
                self.model.thumb_height * 0.5,
                8,
                self.model.thumb_height * 0.5 - 7,
                self.model.thumb_width,
                self.model.thumb_height * 0.5 - 7,
                self.model.thumb_width,
                self.model.thumb_height * 0.5 + 7,
                8,
                self.model.thumb_height * 0.5 + 7,
                outline="white",
                width=1,
                fill=self.model.color,
                tags="thumb"
            )

    def _crosshair(self):
        """ Create a crosshair shaped thumb. """
        radius = min(self.model.thumb_width, self.model.thumb_height)
        radius *= 0.3
        self.thumb_canvas.delete("thumb")
        self.thumb_canvas.create_oval(
            self.model.thumb_width * 0.5 - radius,
            self.model.thumb_height * 0.5 - radius,
            self.model.thumb_width * 0.5 + radius,
            self.model.thumb_height * 0.5 + radius,
            outline=self.model.color,
            width=1,
            tags="thumb"
        )
        self.thumb_canvas.create_line(
            self.model.thumb_width * 0.1,
            self.model.thumb_height * 0.5,
            self.model.thumb_width * 0.9,
            self.model.thumb_height * 0.5,
            fill=self.model.color,
            tags="thumb"
        )
        self.thumb_canvas.create_line(
            self.model.thumb_width * 0.5,
            2,
            self.model.thumb_width * 0.5,
            self.model.thumb_height,
            fill=self.model.color,
            tags="thumb"
        )

    def _cube(self):
        """ Create a cube shaped thumb. """
        self.thumb_canvas.delete("thumb")
        self.thumb_canvas.create_rectangle(
            0,
            0.25 * self.model.thumb_height,
            self.model.thumb_width,
            0.75 * self.model.thumb_height,
            outline="white",
            width=2,
            fill=self.model.color,
            tags="thumb"
        )


class _Ticks:
    """ Create a tick bar """
    def __init__(self, model, parent, engine):
        self.model = model

        # Create frame & canvas for tick bar
        ticks_frame = tk.Frame(
            parent,
            width=model.track_width,
            height=model.track_height,
            padx=model.bar_pad_x,
            pady=model.bar_pad_y,
        )
        ticks_frame.pack(
            side=model.pack_side,
            padx=model.outer_padding
        )

        self.bar = tk.Canvas(
            ticks_frame,
            width=model.tick_bar_width,
            height=model.tick_bar_height,
            highlightthickness=0,
        )
        self.bar.pack(side=model.pack_side)

        # Catch mouse wheel events in tick bar for usability
        self.bar.bind(
            MOUSE_WHEEL,
            lambda event: engine.slide_fast.set(event.delta)
        )

        # Set orientation-appropriate function for update of self
        if model.orientation == "horizontal":
            self._draw = self._draw_ticks_hor
        elif model.orientation == "vertical":
            self._draw = self._draw_ticks_vert

        # Redraw self when slider is disabled/enabled
        engine.state.trace_add("write", self._draw)

    def _draw_ticks_hor(self, *_):
        # Draw ticks for horizontal slider
        self.bar.delete("tick")
        y = self.model.tick_bar_height
        for x in range(
                self.model.tick_start,
                self.model.track_width - self.model.tick_start + 1,
                self.model.tick_width
        ):
            self.bar.create_line(x, 0, x,  y,
                                 fill=self.model.font_color,
                                 tags="tick"
                                 )

        # Draw minor ticks
        if self.model.show_minor_ticks:
            for x in range(
                    self.model.tick_start + int(0.5 * self.model.tick_width),
                    self.model.track_width - self.model.tick_start + 1,
                    self.model.tick_width
            ):
                self.bar.create_line(x, 0, x, y * 0.5,
                                     fill=self.model.font_color,
                                     tags="tick"
                                     )

    def _draw_ticks_vert(self, *_):
        # Draw ticks for a vertical slider
        self.bar.delete("tick")
        x = self.model.tick_bar_width
        for y in range(
                self.model.tick_start,
                self.model.track_height - self.model.tick_start + 1,
                self.model.tick_width
        ):
            self.bar.create_line(0, y, self.model.label_bar_width, y,
                                 fill=self.model.font_color,
                                 tags="tick"
                                 )

        # Draw minor ticks
        if self.model.show_minor_ticks:
            for y in range(
                    self.model.tick_start + int(0.5 * self.model.tick_width),
                    self.model.track_height - self.model.tick_start + 1,
                    self.model.tick_width
            ):
                self.bar.create_line(x * 0.5, y, x, y,
                                     fill=self.model.font_color,
                                     tags="tick"
                                     )


class _BottomLabels:
    """ Create static bottom labels. """
    def __init__(self, parent, model, engine):
        self.model = model

        # Create frame & canvas for bottom labels
        label_frame = tk.Frame(
            parent,
            padx=self.model.bar_pad_x,
            pady=self.model.bar_pad_y,
        )
        label_frame.pack(side=self.model.pack_side)

        self.bar = tk.Canvas(
            label_frame,
            width=self.model.label_bar_width,
            height=self.model.label_bar_height,
            highlightthickness=0,
        )
        self.bar.pack(side=self.model.pack_side)

        # Catch mouse wheel events in label bar for usability
        self.bar.bind(
            MOUSE_WHEEL,
            lambda event: engine.slide_fast.set(event.delta)
        )

        # Set appropriate function to draw label values
        if self.model.orientation == "horizontal":
            self.draw_labels = self.draw_labels_hor
        elif self.model.orientation == "vertical":
            self.draw_labels = self.draw_labels_vert

        # Redraw self when slider is disabled/enabled
        engine.state.trace_add("write", self.draw_labels)

    def draw_labels_hor(self, *_):
        # Create label values for horizontal slider
        self.bar.delete("bottom_label")
        label_value = self.model.start_value
        for x in range(
                self.model.tick_start + 25,
                self.model.track_width + 26,
                self.model.tick_width
        ):
            self.bar.create_text(
                x,
                self.model.label_bar_height * 0.5 + 2,
                text=(
                    f"{self.model.prefix}"
                    f"{label_value:.{self.model.precision}f}"
                    f"{self.model.suffix}"
                ),
                fill=self.model.font_color,
                font=self.model.font,
                tags="bottom_label",
                anchor=tk.CENTER,
            )
            label_value += self.model.tick_width_num

    def draw_labels_vert(self, *_):
        # Create label values for "vertical" slider
        self.bar.delete("bottom_label")
        label_value = self.model.end_value
        for y in range(
                self.model.tick_start,
                self.model.track_height - self.model.tick_start + 1,
                self.model.tick_width
        ):
            self.bar.create_text(
                self.model.label_bar_width * 0.5,
                y,
                text=(
                    f"{self.model.prefix}"
                    f"{label_value:.{self.model.precision}f}"
                    f"{self.model.suffix}"
                ),
                fill=self.model.font_color,
                font=self.model.font,
                tags="bottom_label",
                anchor=tk.CENTER,
            )
            label_value -= self.model.tick_width_num


if __name__ == "__main__":
    """ Mini showcase """
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
