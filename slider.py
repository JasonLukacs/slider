""" A feature-rich, pure tkinter alternative for tkinter.Scale.

Run demo.py for some examples.

Consider using the interactive builder tool (build.py) to configure
your slider and associated code.

Public class: Slider
"""
import warnings
import tkinter as tk
import tkinter.font as tk_font


class _SliderModel:
    """ Simple container for static parameters. """
    def __init__(
            self, track_style, thumb_style, width, height, color,
            font_color, font, font_size, track_bg, start_value,
            end_value, show_minor_ticks, num_ticks, precision,
            snap_to_ticks
    ):
        # Appearance
        self.track_style = track_style
        self.thumb_style = thumb_style
        self.width = width
        self.height = height
        self.color = color
        self.font_color = font_color
        self.font = font
        self.font_size = font_size
        self.track_bg = track_bg
        self.show_minor_ticks = show_minor_ticks
        self.num_ticks = num_ticks
        self.snap_to_ticks = snap_to_ticks

        # Numerical dimensions
        self.start_value = start_value
        self.end_value = end_value
        self.precision = precision

        # Do some basic input checks
        self._validate_input()

        # Calculate / set internal parameters

        # GENERAL
        # Precision "None" comes in handy when using round(), for
        # string formatting we need "0" as it can't handle "None".
        if self.precision:
            self.txt_precision = self.precision
        else:
            self.precision = None  # just in case self.precision = 0
            self.txt_precision = 0

        # FONT
        if self.font is None:
            self.font = tk_font.Font(font="TkDefaultFont")
        else:
            try:
                self.font = tk_font.Font(font=self.font)
            except BaseException:
                raise ValueError(f"{self.font} is not a valid font.")

        if self.font_size is None:
            self.font_size = self.font.cget("size")
        else:
            self.font.config(size=self.font_size)
        # value for scaling when using large fonts
        self.scale_add = self.font_size - 12

        # COLOR
        if self.color is None:
            self.color = "black"

        # GRAPHICAL DIMENSIONS
        
        # Label bar (top and bottom labels)
        self.label_bar_height = 30 + self.scale_add

        # Track
        if self.height is None:
            self.track_height = 27 + self.scale_add
        else:
            self.track_height = self.height

        # Thumb width and track padding
        if self.thumb_style == "classic":
            # Scale thumb width within limits
            self.track_padding = 4
            self.thumb_width = int(self.width / 10)
            if self.thumb_width < 40:
                self.thumb_width = 40
        else:
            self.track_padding = 0
            self.thumb_width = 30

        # Generic thumb dimensions
        self.thumb_height = self.track_height

        # Tick bar.
        self.tick_bar_height = int(10 + 0.5 * self.scale_add)
        # Offset to center ticks on center of thumb
        self.tick_start_x = int(self.thumb_width * 0.5)

        # Set internal track width (outer width = self.width)
        self.track_width = self.width - self.thumb_width

        # Set available width for ticks
        self.tick_width = int(self.track_width / self.num_ticks)

        # Set final width based on num_ticks * tick_width to account for
        # rounding errors as a result of setting tick_width to integer
        self.width = (
                self.thumb_width
                + self.num_ticks * self.tick_width
        )

        # NUMERICAL DIMENSIONS

        # Set factor to derive change in value from thumb displacement
        value_range = self.end_value - self.start_value
        self.delta_x_to_value = value_range / self.track_width

        # Set numerical width of ticks
        self.value_step = value_range / self.num_ticks

    def _validate_input(self):
        if self.start_value >= self.end_value:
            raise ValueError("Start value must be lower than end value")

        # Color validity
        # todo

        # Gentle warnings for anti-configurations
        # todo.
        """Vars to take into consideration
        print(self.width)
        print(self.start_value, self.end_value)
        print(self.num_ticks or 1)
        print(self.precision or 1)
        """


class _SliderEngine:
    """ Controller class.
    Public methods, (advertised by and through class Slider):
    start(): enable user interaction with the slider
    stop(): disable user interaction, slider can be set though
    set(int or float): set slider value programmatically
    add_subscriber(tk_Var): ad a custom tk variable to be auto-updated

    Inner workings:
    If slider elements are clicked / dragged they will emit the
    horizontal displacement (delta x) to a specific traced var:
    delta_x: To simply move the thumb by amount delta_x
    delta_x_wheel: To make the thumb slide in steps of tick width
    delta_x_snap: To snap the thumb to the nearest tick after moving

    This class traces these vars and calculates the corresponding new
    value (reading) of the slider, taking options like snap to ticks
    into consideration.
    The new value is propagated to slider_value, which is traced by
    top label and thumb in order to update themselves.

    Additionally, method snap_slider provides a way to have the thumb
    be snapped upon button release. This method is bound
    to the <ButtonRelease> event of the thumb and the track when
    applicable.

    """
    def __init__(self, model):
        self.model = model
        self.trace_ids = []
        self.status = "stopped"  # on/off switch of the whole thing
        self.subscriber = None

        # Create tk vars
        self.delta_x = tk.IntVar()
        self.delta_x_wheel = tk.IntVar()
        self.delta_x_snap = tk.IntVar()
        self.slider_value = tk.DoubleVar()

        # This group will be traced when engine is started
        self.traced_vars = (
            self.delta_x,
            self.delta_x_wheel,
            self.delta_x_snap
        )

        # If no precision is set, explicitly set return value to integer
        # to get rid of the ineradicable decimal tk tends to insert
        if self.model.precision:
            self.ret_val = tk.DoubleVar()
        else:
            self.ret_val = tk.IntVar()

        # Trace slider_value to auto-update return value
        self.slider_value.trace_variable("w", self._set_ret_val)

        # Start
        self.start()

    def _slide(self, *_):
        """ Change slider_value proportional to delta_x.
        Use case: simple sliding left or right.
        """
        self.slider_value.set(
            self._clamp(
                    self.slider_value.get()
                    + (self.delta_x.get()
                       * self.model.delta_x_to_value)
            )
        )

    def _slide_wheel(self, *_):
        """ Snap slider_value if not currently snapped, else change
        by a tick width.
        Use case: accelerated sliding with mousewheel or trackpad
        """
        if (
                self.slider_value.get()
                == self._snap(self.slider_value.get())
        ):
            # Slider is snapped, change slider_value in units of
            # numerical tick width
            self.slider_value.set(
                self._clamp(
                    self.slider_value.get()
                    + self.delta_x_wheel.get()
                    * self.model.value_step
                )
            )
        else:
            # Slider is not snapped. Snap to nearest higher tick value
            # if movement is upwards, snap to nearest lower tick value
            # if movement is downwards.
            self.slider_value.set(
                self._clamp(
                    # Bump 0.5 tick_width in the direction of travel,
                    # snap() will finish the job
                    self._snap(
                        self.slider_value.get()
                        + (-1 if self.delta_x_wheel.get() < 0 else 1)
                        * 0.5 * self.model.value_step
                    )
                )
            )

    def _slide_snapped(self, *_):
        """ Change slider_value proportional to delta x and snap it
        to the nearest tick afterwards.
        Use case: automatically snap the slider when clicking the
        track.
        """
        self.slider_value.set(
            self._clamp(
                # Move to clicked position in track,
                # bump 0.5 tick_width in the direction of the
                # displacement and snap() will finish the job
                self._snap(
                    self.slider_value.get()
                    + (self.delta_x_snap.get()
                       * self.model.delta_x_to_value)
                    + (-1 if self.delta_x_snap.get() < 0 else 1)
                    * 0.5 * self.model.value_step
                )
            )
        )

    def _set_ret_val(self, *_):
        """ Set return value rounded to set precision. """
        self.ret_val.set(
            round(self.slider_value.get(), self.model.precision)
        )

    def _clamp(self, value):
        """ Keep value in between start- and end value (including). """
        if self.model.start_value <= value <= self.model.end_value:
            return value
        elif value < self.model.start_value:
            return self.model.start_value
        elif value > self.model.end_value:
            return self.model.end_value

    def _snap(self, value):
        """ Return the numeric value of the tick nearest to value. """
        return (self.model.value_step
                * round(value/self.model.value_step))

    def snap_slider(self, *_):
        """ Set slider_value to the nearest tick.
        Use case: Snap the slider upon button release (after dragging)
        when snap_to_tick option is set. Hence, this is the
        "snap_handler" passed to track and thumb for binding to
        <ButtonRelease>.
        """
        self.slider_value.set(
            self._snap(self.slider_value.get())
        )

    def start(self):
        """ Enable the slider by setting a trace on the variables
        through which slider elements communicate mouse events.
        Status check to prevent redundant traces when called multiple
        times.
        """
        if self.status == "stopped":
            self.trace_ids = []
            self.status = "running"
            funcs = (
                self._slide,
                self._slide_wheel,
                self._slide_snapped
            )
            for var, func in zip(self.traced_vars, funcs):
                self.trace_ids.append(
                    var.trace_variable("w", func)
                )
        else:
            warnings.warn("Attempt to enable already enabled slider.")

    def stop(self):
        """ Disable the slider by removing the trace on the variables
        used to communicate mouse movements. Note the slider *can* be
        set programmatically when disabled.
        Status check to prevent ugly errors when called multiple times.
        """
        if self.status == "running":
            self.status = "stopped"
            for var, trace_id in zip(self.traced_vars, self.trace_ids):
                var.trace_remove("write", trace_id)
        else:
            warnings.warn("Attempt to disable already disabled slider.")

    def set(self, value):
        """ Slider is set programmatically. Do some basic cleaning. """
        try:
            if self.model.precision:
                requested_value = float(value)
            else:
                requested_value = int(value)
        except ValueError:
            txt = f"{value} is not a valid value to set slider."
            raise ValueError(txt)

        if (
                value < self.model.start_value
                or value > self.model.end_value
        ):
            txt_0 = "Invalid attempt to set slider.\n"
            txt_1 = f"{value} not in range ({self.model.start_value}"
            txt_2 = f", {self.model.end_value})"
            raise ValueError("".join([txt_0, txt_1, txt_2]))

        if self.model.snap_to_ticks:
            requested_value = self._snap(requested_value)

        # Input seems okay, set slider
        self.slider_value.set(requested_value)

    def add_subscriber(self, var):
        """ Add your own tk variable to be automatically set to current
        value of the slider.
        """
        if isinstance(var, tk.IntVar) or isinstance(var, tk.DoubleVar):
            self.ret_val.trace_variable(
                "w",
                lambda *args: var.set(self.ret_val.get())
            )
            # Force initialization of external var
            var.set(self.ret_val.get())
        else:
            txt = f"Cannot create subscriber from {repr(var)}"
            raise ValueError(txt)


class _TopLabel:
    """ Create co-sliding label above the slider. """
    def __init__(self, parent, model, engine):
        parent = parent
        self.model = model
        self.engine = engine
        self.slider_value = self.engine.slider_value
        self.delta_x_wheel = self.engine.delta_x_wheel

        # Static helper value, used to truncate floats
        self.trunc_base = 10 ** self.model.txt_precision

        # Build self
        self.bar = tk.Canvas(
            parent,
            width=self.model.width,
            height=self.model.label_bar_height,
            bd=0,
            highlightthickness=0,
        )
        self.bar.pack(ipadx=20)

        self.text = tk.Label(
            self.bar,
            fg=self.model.font_color,
            font=self.model.font,
        )

        self.value_label = self.bar.create_window(
            0,
            0,
            width=self.model.thumb_width + 41,
            anchor=tk.NW,
            window=self.text
        )

        # Catch mouse wheel events for usability
        for element in (self.bar, self.text):
            element.bind(
                "<MouseWheel>",
                lambda event: self.delta_x_wheel.set(event.delta)
            )

        # Trace slider_value for auto-update of self
        self.slider_value.trace_variable("w", self._set)

    def _set(self, *_):
        """ Update label position and label text. """
        label_position = (
            (self.slider_value.get() - self.model.start_value)
            / self.model.delta_x_to_value
        )
        self.bar.coords(self.value_label, label_position, 0)

        # Truncate slider value to prevent the label from showing
        # rounded values which would contradict snap behaviour,
        # e.g. 34.9, showing as 35, snapping to 30).
        # Multiply by 10**precision, make int, divide by 10**precision.
        tmp = (
                int(self.slider_value.get() * self.trunc_base)
                / self.trunc_base
        )
        self.text.config(text=f"{tmp:.{self.model.txt_precision}f}")


class _Track:
    """ Create the slider track and incorporate a thumb. """
    def __init__(self, parent, model, engine):
        parent = parent
        self.model = model
        self.engine = engine
        self.slider_value = self.engine.slider_value
        self.delta_x = self.engine.delta_x
        self.delta_x_wheel = self.engine.delta_x_wheel
        self.delta_x_snap = self.engine.delta_x_snap
        if self.model.snap_to_ticks:
            snap_handler = self.engine.snap_slider
        else:
            snap_handler = None

        self.clicked = False
        self.drag_start_x = 0

        # Create generic track
        track_frame = tk.Frame(
            parent,
            bd=3,
            relief=tk.SUNKEN,
            padx=4,
            pady=self.model.track_padding,
        )
        track_frame.pack()

        self.track = tk.Canvas(
            track_frame,
            width=self.model.width,
            height=self.model.track_height,
            bd=0,
            highlightthickness=0,
        )
        self.track.pack()

        # Reconfigure if style applies
        if self.model.track_style == "line":
            track_frame["relief"] = tk.FLAT
            self.track.create_line(
                0,
                self.model.track_height * 0.5,
                self.model.width,
                self.model.track_height * 0.5,
                fill=self.model.color
            )

        # Create the thumb
        self.thumb = _Thumb(
            parent=self.track,
            model=self.model,
            engine=self.engine
        )

        # Create track background
        if self.model.track_bg and self.model.track_style == "plane":
            self.bg = _TrackBackground(
                self.model,
                self.engine,
                self.track,
                self.thumb
            )

        # Enable clicking and dragging in the track
        self.track.bind("<Button>", self._track_clicked)
        self.track.bind("<Motion>", self._track_moved)
        self.track.bind("<ButtonRelease>", self._track_released)
        # Catch mouse wheel events for usability
        self.track.bind(
            "<MouseWheel>",
            lambda event: self.delta_x_wheel.set(event.delta)
        )

        if snap_handler:
            # If snap_to_ticks options is set, snap to tick on button
            # release
            self.track.bind("<ButtonRelease>", snap_handler, add="+")

    def _track_clicked(self, event):
        # The track is clicked, so the user wants the slider to be
        # moved left or right. Clicking the track will snap the thumb,
        # subsequent movements lead to normal sliding behaviour.
        self.clicked = True
        self.drag_start_x = event.x_root

        delta_x = 0
        if event.x <= self.thumb.thumb_position.get():
            # Move left
            delta_x = event.x - self.thumb.thumb_position.get()
        elif event.x > self.thumb.thumb_position.get():
            # Move right
            delta_x = (event.x
                       - self.model.thumb_width
                       - self.thumb.thumb_position.get()
                       )
        self.delta_x_snap.set(delta_x)

    def _track_moved(self, event):
        """ The mouse is moving in the track. If clicked, drag thumb."""
        if self.clicked:
            self.delta_x.set(event.x_root - self.drag_start_x)
            self.drag_start_x = event.x_root

    def _track_released(self, *_):
        """ Button released, stop dragging. """
        self.clicked = False


class _TrackBackground:
    """ Draw track background
    Respond to changes in thumb_position by drawing the requested
    background from left side of the track up to current thumb position.
    """
    def __init__(self, model, engine, track, thumb):
        self.model = model
        self.track = track
        self.thumb = thumb
        self.slider_value = engine.slider_value

        self.thumb_position = self.thumb.thumb_position
        self.height = self.model.track_height

        # Set self.draw_bg to the appropriate method
        if self.model.track_bg == "green_to_red":
            self.step_size = 510 / self.model.width
            self.draw_bg = self.draw_green_to_red
        elif self.model.track_bg == "white_to_blue":
            self.step_size = 200 / self.model.width
            self.draw_bg = self.draw_white_to_blue
        else:
            self.bg_color = self.model.track_bg
            self.draw_bg = self.draw_solid_bg

        # Trace thumb position to auto-update background
        self.thumb_position.trace_variable("w", self.draw_bg)

    def draw_green_to_red(self, *_):
        # Start green, decrease green and increase red. Some tweaks
        # for smoothness
        self.track.delete("track_bg")
        r = 0
        g = 255
        b = 0
        for x in range(int(self.thumb.thumb_position.get())):
            self._draw_line(x, r, g, b)
            if r <= 255 - self.step_size:
                r += self.step_size
            elif r < 255:  # push to 255 if step_size too large
                r = 255
            if r >= 255:
                g -= self.step_size

    def draw_white_to_blue(self, *_):
        self.track.delete("track_bg")
        # Start white, decrease red and green
        r = 255
        g = 255
        b = 255
        for x in range(int(self.thumb.thumb_position.get())):
            self._draw_line(x, r, g, b)
            if r > 0 + self.step_size:
                r -= self.step_size
                g -= self.step_size

    def draw_solid_bg(self, *_):
        self.track.delete("track_bg")
        self.track.create_rectangle(
            0,
            0,
            int(self.thumb.thumb_position.get()),
            self.height,
            fill=self.bg_color,
            tags="track_bg"
        )

    def _draw_line(self, x, r, g, b):
        color = "".join(
            ("#", f"{int(r):02x}", f"{int(g):02x}", f"{int(b):02x}")
        )
        self.track.create_line(
            x,
            0,
            x,
            self.height,
            fill=color,
            tags="track_bg"
        )


class _Thumb:
    """ Create a thumb """
    def __init__(self, parent, model, engine):
        self.parent = parent
        self.model = model
        self.engine = engine

        self.delta_x = self.engine.delta_x
        self.delta_x_wheel = self.engine.delta_x_wheel

        self.slider_value = self.engine.slider_value

        if self.model.snap_to_ticks:
            snap_handler = self.engine.snap_slider
        else:
            snap_handler = None

        self.thumb_position = tk.DoubleVar()
        self.thumb_clicked = False

        # Create generic thumb
        self.thumb_frame = tk.Frame(
            self.parent,
            width=self.model.thumb_width,
            height=self.model.thumb_height,
            bd=0,
            highlightthickness=0,
        )

        self.thumb = self.parent.create_window(
            0,
            0,
            anchor=tk.NW,
            window=self.thumb_frame
        )

        # Apply style
        if self.model.thumb_style == "classic":
            self._double_button_thumb()
        else:
            self._graphical_thumb()

        # Trace slider_value to auto update thumb position
        self.trace_id = self.slider_value.trace_variable(
            "w",
            self.set_thumb
        )

        # Enable thumb
        for element in self.thumb_elements:
            element.bind("<Button>", self._thumb_clicked)
            element.bind("<Motion>", self._thumb_moved)
            element.bind("<ButtonRelease>", self._thumb_released)
            # Mousewheel events are handled by generic method
            element.bind(
                "<MouseWheel>",
                lambda event: self.delta_x_wheel.set(event.delta)
            )
            if snap_handler:
                # If snap_to_ticks options is set, snap to tick on
                # button release
                element.bind("<ButtonRelease>", snap_handler, add="+")

    def _thumb_clicked(self, event):
        """ The thumb is clicked, future mouse events may be dragging
        the thumb to a new position.
        """
        self.thumb_clicked = True
        self.drag_start_x = event.x_root

    def _thumb_moved(self, event):
        """ If the thumb is clicked and the mouse is being moved,
        drag the thumb
        """
        if self.thumb_clicked:
            displacement = event.x_root - self.drag_start_x
            self.drag_start_x = event.x_root
            self.delta_x.set(displacement)

    def _thumb_released(self, *_):
        """ Button released, stop dragging """
        self.thumb_clicked = False

    def set_thumb(self, *_):
        """ Update position of thumb """
        self.thumb_position.set(
            (self.slider_value.get() - self.model.start_value)
            / self.model.delta_x_to_value
        )
        self.parent.coords(self.thumb, self.thumb_position.get(), 0)

    def _graphical_thumb(self):
        self.thumb_btn_1 = tk.Canvas(
            self.thumb_frame,
            width=self.model.thumb_width,
            height=self.model.thumb_height,
            bd=0,
            highlightthickness=0,
        )
        self.thumb_btn_1.pack(side=tk.LEFT)

        if self.model.thumb_style == "dot":
            self._dot()
        elif self.model.thumb_style == "diamond":
            self._diamond()
        elif self.model.thumb_style == "triangle":
            self._triangle()
        elif self.model.thumb_style == "pointer":
            self._pointer()
        elif self.model.thumb_style == "crosshair":
            self._crosshair()

        # The element above is the widget that will catch mouse
        # events. Create list to bind this widget to handler.
        self.thumb_elements = [
            self.thumb_btn_1
        ]

    def _dot(self):
        """ Create a circle shaped thumb. """
        self.thumb_btn_1.create_oval(
            5,
            int(0.5*self.model.thumb_height - 9),
            24,
            int(0.5*self.model.thumb_height + 9),
            outline="white",
            width=3,
            fill=self.model.color)

    def _diamond(self):
        """ Create a diamond shaped thumb. """
        self.thumb_btn_1.create_polygon(
            self.model.thumb_width * 0.5,
            0,

            self.model.thumb_width-2,
            self.model.thumb_height * 0.5,

            self.model.thumb_width * 0.5,
            self.model.thumb_height,

            2,
            self.model.thumb_height * 0.5,

            outline="white",
            width=3,
            fill=self.model.color
        )

    def _triangle(self):
        """ Create a triangle shaped thumb. """
        self.thumb_btn_1.create_polygon(
            0,
            0,

            self.model.thumb_width-1,
            0,

            self.model.thumb_width * 0.5,
            self.model.thumb_height,

            outline="white",
            width=3,
            fill=self.model.color
        )

    def _pointer(self):
        """ Create a shaped thumb. """
        self.thumb_btn_1.create_polygon(
            5,
            0,

            self.model.thumb_width-6,
            0,

            self.model.thumb_width-6,
            self.model.thumb_height * 0.5,

            self.model.thumb_width * 0.5,
            self.model.thumb_height,

            5,
            self.model.thumb_height * 0.5,

            outline="white",
            width=3,
            fill=self.model.color
        )

    def _crosshair(self):
        """ Create a crosshair shaped thumb. """
        self.thumb_btn_1.create_oval(
            9,
            int(0.5*self.model.thumb_height - 6),
            21,
            int(0.5*self.model.thumb_height + 6),
            outline=self.model.color,
            width=1,
        )
        self.thumb_btn_1.create_line(
            0,
            self.model.thumb_height * 0.5,
            self.model.thumb_width,
            self.model.thumb_height * 0.5,
            fill=self.model.color
        )

        self.thumb_btn_1.create_line(
            self.model.thumb_width * 0.5,
            0,
            self.model.thumb_width * 0.5,
            self.model.thumb_height,
            fill=self.model.color
        )

    def _double_button_thumb(self):
        """ Create classic thumb, consisting of two adjacent
        pseudo-buttons.
        """
        self.thumb_btn_1 = tk.Frame(
            self.thumb_frame,
            width=self.model.thumb_width * 0.5,
            height=self.model.thumb_height,
            bd=3,
            relief=tk.RAISED
        )
        self.thumb_btn_1.pack(side=tk.LEFT)

        self.thumb_btn_2 = tk.Frame(
            self.thumb_frame,
            width=self.model.thumb_width * 0.5,
            height=self.model.thumb_height,
            bd=3,
            relief=tk.RAISED
        )
        self.thumb_btn_2.pack(side=tk.LEFT)

        # The frames above are the widgets that will catch mouse
        # events. Create list to bind these widgets to handler.
        self.thumb_elements = [
            self.thumb_btn_1,
            self.thumb_btn_2
        ]


class _Ticks:
    """ Create a tick bar """
    def __init__(self, model, parent, engine):
        parent = parent
        model = model
        delta_x_wheel = engine.delta_x_wheel

        # Create tick bar
        bar = tk.Canvas(
            parent,
            width=model.width,
            height=model.tick_bar_height,
            bd=0,
            highlightthickness=0,
        )
        bar.pack()

        # Draw ticks
        y = model.tick_bar_height
        for x in range(
                model.tick_start_x,
                model.width - model.tick_start_x + 1,
                model.tick_width
        ):
            bar.create_line(x, 0, x, y, fill=model.color)

        # Draw minor or secondary ticks
        if model.show_minor_ticks:
            for x in range(
                    model.tick_start_x + int(0.5 * model.tick_width),
                    model.width - model.tick_start_x,
                    model.tick_width
            ):
                bar.create_line(x, 0, x, y/2, fill=model.color)

        # Catch mouse wheel events for usability
        bar.bind(
            "<MouseWheel>",
            lambda event: delta_x_wheel.set(event.delta)
        )


class _BottomLabels:
    """ Create (static) bottom labels"""
    def __init__(self, model, parent, engine):
        parent = parent
        model = model
        delta_x_wheel = engine.delta_x_wheel

        bar = tk.Canvas(
            parent,
            width=model.width,
            height=model.label_bar_height,
            bd=0,
            highlightthickness=0,
        )
        bar.pack(ipadx=20)

        # Create label values
        label_value = model.start_value
        for x in range(
                model.tick_start_x + 20,
                model.width + 20,
                model.tick_width
        ):
            bar.create_text(
                x,
                model.scale_add + 10,
                text=f"{label_value:.{model.txt_precision}f}",
                fill=model.font_color,
                font=model.font,
                anchor=tk.CENTER,
            )
            label_value += model.value_step

        # Catch mouse wheel events for usability
        bar.bind(
            "<MouseWheel>",
            lambda event: delta_x_wheel.set(event.delta)
        )


class Slider(tk.Frame):
    """ Create a slider.
    Consider using the interactive builder tool (build.py) to configure
    your slider and associated code.

    Usage: my_slider = Slider(parent, **kwargs)

    Public methods:
    my_slider.set(value: int or float) to set programmatically
    my_slider.get() to get current value
    my_slider.disable() to disable all user interaction
    my_slider.enable() to resuscitate disabled slider

    For automatic updates use my_slider.value as (text)variable or
    bind it to your handler.
    Alternatively, use my_slider.add_subscriber(var) to have your
    own tk_Var updated automatically.
    """
    def __init__(
            self,
            parent,
            relief=tk.FLAT,
            track_style="plane",
            thumb_style="classic",
            width: int = 400,
            height=None,
            color=None,
            font_color="black",
            font=None,
            font_size=None,
            track_bg=None,
            start_value=0.0,
            end_value=100.0,
            initial_value=0.0,
            show_top_label=True,
            show_ticks=True,
            show_minor_ticks=False,
            show_bottom_labels=True,
            num_ticks=10,
            precision=None,
            snap_to_ticks=False,
    ):
        """
        :param parent: Parent widget or window
        :param relief: Style of outer border (== frame relief)
        :param track_style: Literal, "plane" or "line"
        :param thumb_style: Literal, "classic", "dot", "diamond",
        "triangle", "pointer" or "crosshair"
        :param width: Outer width
        :param height: Height of the track
        :param color: Color of certain thumbs and the ticks
        :param font_color: Color of font
        :param font: Tuple containing valid tkinter font options
        :param font_size: Size of the font
        :param track_bg: Any valid color name or hex value, or
        "green_to_red" or "white_to_blue" for a gradient background
        :param start_value: Lower bound of the scale
        :param end_value: Upper bound of the scale
        :param initial_value: Value of slider upon creation
        :param show_top_label: Show the moving label displaying current
        value
        :param show_ticks: Show major ticks
        :param show_minor_ticks: Show minor ticks
        :param show_bottom_labels: Show a bar with major tick values
        :param num_ticks: Number of ticks. Set this sensibly in relation
        to start_value and end_value
        :param precision: Precision of toplabel, bottomlabels and output
        value of the slider
        :param snap_to_ticks: Snap thumb to the nearest tick. Note that
        slider will emit continuous values when user is dragging.
        """
        super().__init__(parent, bd=3, pady=15, relief=relief)

        # Create core objects
        self.model = _SliderModel(
            track_style, thumb_style, width, height, color, font_color,
            font, font_size, track_bg, start_value, end_value,
            show_minor_ticks, num_ticks, precision, snap_to_ticks
        )

        self.engine = _SliderEngine(self.model)

        kwargs = {
            "parent": self,
            "model": self.model,
            "engine": self.engine
        }

        # Create the slider, top to bottom because pack
        if show_top_label:
            self.top_label = _TopLabel(**kwargs)
        self.track = _Track(**kwargs)
        if show_ticks:
            self.tick_bar = _Ticks(**kwargs)
        if show_bottom_labels:
            self.label_bar = _BottomLabels(**kwargs)

        # Set var for publishing engine return value
        self.value = self.engine.ret_val

        # Set initial_value
        self.set(initial_value)

    def _validate_input(self):
        pass

    def set(self, value):
        self.engine.set(value)

    def get(self):
        return self.value.get()

    def enable(self):
        self.engine.start()

    def disable(self):
        self.engine.stop()

    def add_subscriber(self, var):
        self.engine.add_subscriber(var)


if __name__ == "__main__":
    """ Mini showcase """
    root = tk.Tk()
    my_slider = Slider(root)
    label = tk.Label(textvariable=my_slider.value)
    my_slider.pack()
    label.pack()
    root.mainloop()
