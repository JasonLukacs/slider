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


GUI for generating or testing code to create a slider object.

"""

import importlib
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext
from tkinter import messagebox
import slider
import config


class Formfield:
    """ Class to bundle a label, an input widget, a tk variable and a
    tooltip in one object. It enables the efficient creation of a large
    form, and the efficient gathering from this form of a set of
    keyword arguments to create a slider.
    """
    def __init__(
            self,
            parent,
            kwarg_name,
            kwarg_type,
            kwarg_label_text,
            default_val,
            tool_tip_txt=None,
            widget_type=None,
            widget_readonly=False,
            values=None,
    ):
        self.parent = parent
        self.kwarg_name = kwarg_name
        self.kwarg_type = kwarg_type
        self.kwarg_label_text = kwarg_label_text
        self.default_val = default_val
        self.tool_tip_txt = tool_tip_txt
        self.widget_type = widget_type
        self.widget_readonly = widget_readonly
        self.values = values

        # Create label
        self.label = tk.Label(self.parent, text=self.kwarg_label_text)

        # Create widget and tk variable
        # If kwarg_type is a boolean: override widget_type and create a
        # checkbutton. Else obey widget_type.
        if self.kwarg_type == "bool":
            self.tk_var = tk.BooleanVar(value=self.default_val)
            self.widget = tk.Checkbutton(
                self.parent,
                variable=self.tk_var
            )
        elif self.kwarg_type in ("int", "float", "str"):
            # Create a tk.StringVar so we can display anything in the
            # widget, type is preserved in kwargs_type and self.get()
            # will return correct type
            self.tk_var = tk.StringVar(value=self.default_val)

            # Gather options in a dict to use in creation of widget
            kwargs = {"textvariable": self.tk_var}

            # Create entry or combo widget
            if self.widget_type == "entry":
                self.widget = tk.Entry(self.parent, **kwargs)
            elif self.widget_type == "combo":
                if self.values:
                    kwargs["values"] = self.values
                if self.widget_readonly:
                    kwargs["state"] = "readonly"
                self.widget = ttk.Combobox(self.parent, **kwargs)
            else:
                raise TypeError(
                    "Formfield received an unknown widget_type.")
        else:
            raise TypeError("Formfield received an unknown kwarg_type.")

        # Create tooltip
        if self.tool_tip_txt:
            self.tool_tip = Tooltip(
                self.parent,
                self.kwarg_label_text,
                self.tool_tip_txt
            )
        else:
            self.tool_tip = None

    def get(self):
        """ Return the type-checked value of the formfield input
        widget
        """
        # Exception will be raised when widget contains invalid value,
        # these must be handled by caller
        retval = self.tk_var.get()
        # Convert to specified type only if value is not default,
        # effectively allowing default values like "<auto>" for numeric
        # fields.
        if retval != self.default_val:
            if self.kwarg_type == "int":
                retval = int(retval)
            elif self.kwarg_type == "float":
                retval = float(retval)
        return retval


class Prebuilt:
    """ Class to bundle a label, a button and a dict containing
    definitions of a prebuilt slider. Enables easy creation of the
    tab where a prebuilt can be selected.
    """
    def __init__(self,
                 parent,
                 tk_var,
                 identifier,
                 ):
        self.identifier = identifier
        self.args = config.prebuilts[identifier]

        self.btn = tk.Button(
            parent,
            width=20,
            text=identifier,
            command=lambda: tk_var.set(self.identifier)
        )


class Tooltip(tk.Button):
    """ Simple tooltip button"""
    def __init__(
            self,
            parent,
            message_title,
            message,
    ):
        self.message = message
        self.message_title = message_title
        self.parent = parent
        super().__init__(
            self.parent,
            text="?",
            fg="#00008b",
            takefocus=0,
            command=self.show_msg
        )

    def show_msg(self):
        tk.messagebox.showinfo(
            self.message_title,
            self.message
        )


class Creator():
    """ Main application """
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.parent.title("Create slider")
        self.parent.geometry("+50+50")
        self.form_fields = []
        self.field_index = {}
        self.args = {}

        # Gentle quit
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create a generic validator, corrector for entry and combo box
        self.validator = self.parent.register(self.validate)
        self.corrector = self.parent.register(self.correct)

        # Build main window
        self.init_gui()

        # Initialize self
        self.init_prebuilt_selector()
        self.init_config_options()

        # Enable auto-update of preview when user input changes
        self.enable_observatory()

        # Draw initial slider
        self.create_preview()

    # init
    def init_gui(self):
        """ Build the main window """

        # Left hand part of main window
        # Create five-tab notebook
        s = ttk.Style()
        s.configure('TNotebook', tabposition=tk.NW)
        form_pane = ttk.Notebook(self.parent)
        form_pane.grid(row=0, column=0, sticky=tk.NSEW)

        # Tab 1: Prebuilts selection
        self.form_tab_1 = tk.Frame(form_pane)
        form_pane.add(self.form_tab_1, text='Prebuilt')

        # Tab 2-5: Configuration options for slider
        self.form_tab_2 = tk.Frame(form_pane)
        self.form_tab_3 = tk.Frame(form_pane)
        self.form_tab_4 = tk.Frame(form_pane)
        self.form_tab_5 = tk.Frame(form_pane)
        form_pane.add(self.form_tab_2, text='Basic')
        form_pane.add(self.form_tab_3, text='Track & thumb')
        form_pane.add(self.form_tab_4, text='Colors & fonts')
        form_pane.add(self.form_tab_5, text='Advanced')

        # Right hand part of main window
        # Create three-tab notebook for slider, code preview and help
        self.preview_pane = ttk.Notebook(self.parent)
        self.preview_pane.grid(row=0, column=1, sticky=tk.NSEW)

        self.preview_tab_1 = tk.Frame(self.preview_pane)
        self.preview_tab_1.rowconfigure(0, weight=1)
        self.preview_tab_1.columnconfigure(0, weight=1)
        self.preview_tab_2 = tk.Frame(self.preview_pane)
        self.preview_tab_3 = tk.Frame(self.preview_pane)

        self.preview_pane.add(self.preview_tab_1, text='Preview')
        self.preview_pane.add(self.preview_tab_2, text='Code')
        self.preview_pane.add(self.preview_tab_3, text='Help')

        # Configure preview tab 1
        # Create a frame for the slider
        self.slider_pane = tk.Frame(
            self.preview_tab_1,
        )
        self.slider_pane.rowconfigure(0, weight=1)
        self.slider_pane.columnconfigure(0, weight=1)
        self.slider_pane.grid(row=0, column=0, padx=15, sticky=tk.NSEW)

        # Create label showing current slider value
        self.slider_value = tk.IntVar()
        label_frame = tk.Frame(self.preview_tab_1)
        label_frame.grid(row=1, column=0, sticky=tk.W)
        value_label_text = tk.Label(label_frame,
                                    text="Slider return value:"
                                    )
        value_label_text.grid(row=0, column=0, sticky=tk.W)
        value_label = tk.Label(label_frame,
                               textvariable=self.slider_value,
                               fg="blue",
                               font=("Courier", "14")
                               )
        value_label.grid(row=0, column=1, sticky=tk.W)

        # Configure preview tab 2
        # Create a preview pane for the code
        self.code_pane = tk.scrolledtext.ScrolledText(
            self.preview_tab_2,
            takefocus=0,
            width=70,
            height=20,
            padx=10,
            pady=10,
            highlightthickness=0,
            font=("Courier", "16")
        )
        self.code_pane.grid()

        # Configure preview tab 3 (Help)
        # Create a pane
        self.help_pane = tk.scrolledtext.ScrolledText(
            self.preview_tab_3,
            takefocus=0,
            width=70,
            height=20,
            padx=10,
            pady=10,
            highlightthickness=0,
            font=("Courier", "16")
        )
        self.help_pane.insert(1.0, config.help_text)
        self.help_pane.grid()

        # Create tags to change code font color
        self.code_pane.tag_configure("red", foreground="red")
        self.code_pane.tag_configure("green", foreground="green")

        # Change font color when user bepotles code
        for event in ("<Control-v>", "<KeyPress>"):
            self.code_pane.bind(event, self.code_changed)

        # Create buttons to copy/paste/run the code in the code pane
        code_button_pane = tk.Frame(self.preview_tab_2)
        code_button_pane.columnconfigure(1, weight=1)
        code_button_pane.grid(
            column=0,
            row=1,
            padx=5,
            pady=15,
            sticky=tk.EW
        )

        tk.Button(
            code_button_pane,
            text="Copy code to clipboard",
            command=self.copy_to_clipboard
        ).grid(row=0, column=0, sticky=tk.W)

        tk.Button(
            code_button_pane,
            text="Paste code from clipboard",
            command=self.paste_from_clipboard
        ).grid(row=0, column=1, sticky=tk.E)

        tk.Button(
            code_button_pane,
            text="Run code",
            command=self.run_code
        ).grid(row=0, column=2, sticky=tk.E)

        # Tabs configured, finalize main window
        # Create main window buttons
        tk.Button(
            self.parent,
            text="Reset form",
            command=self.reset,
        ).grid(column=0, row=1, padx=30, pady=5, sticky=tk.W)

        main_button_pane = tk.Frame(self.parent)
        main_button_pane.rowconfigure(0, weight=1)
        main_button_pane.columnconfigure(3, weight=1)
        main_button_pane.grid(column=1, row=1, padx=30, pady=5, sticky=tk.NSEW)

        """
        # Dev / debugging only: reimport slider
        tk.Button(
            main_button_pane,
            text="Reimport slider",
            command=lambda: importlib.reload(slider)
        ).grid(row=0, column=0, padx=0, pady=10, sticky=tk.W)
        """

        tk.Button(
            main_button_pane,
            text="Enable slider",
            command=lambda: self.my_slider.enable()
        ).grid(row=0, column=1, padx=0, pady=10, sticky=tk.W)

        tk.Button(
            main_button_pane,
            text="Disable slider",
            command=lambda: self.my_slider.disable()
        ).grid(row=0, column=2, padx=0, pady=10, sticky=tk.W)

        tk.Button(
            main_button_pane,
            text="Quit",
            command=self.on_closing
        ).grid(row=0, column=3, padx=0, pady=10, sticky=tk.E)

    # init
    def init_prebuilt_selector(self):
        """ Fill tab 1 with a list of selectable prebuilt sliders """

        self.prebuilts = []
        self.current_prebuilt = tk.StringVar(value="Default")

        # Create the prebuilt options
        self.prebuilts.extend(
            Prebuilt(
                self.form_tab_1,
                tk_var=self.current_prebuilt,
                identifier=style_name,
            )
            for style_name in config.prebuilts
        )

        # Create a dict to lookup index of prebuilt by identifier
        self.prebuilt_index = {
            prebuilt.identifier: index
            for index, prebuilt
            in enumerate(self.prebuilts)
        }

        # Grid the prebuilt options
        for row, prebuilt in enumerate(self.prebuilts):
            prebuilt.btn.grid(
                row=row,
                column=0,
                padx=10,
                pady=5,
                sticky=tk.NW
            )

        # Automatically create a prebuilt slider upon selection
        self.prebuilts_trace_id = self.current_prebuilt.trace_variable(
            "w",
            self.set_prebuilt
        )

    # init
    def init_config_options(self):
        """ For every keyword argument accepted by class slider, create
        a form field in the appropriate tab.
        """
        for args in config.basic_fields:
            self.form_fields.append(
                Formfield(self.form_tab_2, **args)
            )

        for args in config.track_thumb_fields:
            self.form_fields.append(
                Formfield(self.form_tab_3, **args)
            )

        for args in config.colors_fonts_fields:
            self.form_fields.append(
                Formfield(self.form_tab_4, **args)
            )

        for args in config.advanced_fields:
            self.form_fields.append(
                Formfield(self.form_tab_5, **args)
            )

        # Create a dict to lookup index of formfield by kwarg_name
        self.field_index = {
            field.kwarg_name: index
            for index, field
            in enumerate(self.form_fields)
        }

        # Bind entry and combo boxes to validation and correction
        # method.
        for field in self.form_fields:
            if field.widget_type in ("entry", "combo"):
                field.widget["validate"] = "focusout"
                field.widget["validatecommand"] = (self.validator, "%P")
                field.widget["invalidcommand"] = (
                    self.corrector,
                    # Can't pass widget, send index (will become str)
                    self.field_index[field.kwarg_name]
                )

        # Grid the formfields
        for row, field in enumerate(self.form_fields):
            field.label.grid(
                row=row,
                column=0,
                padx=10,
                pady=5,
                sticky=tk.NW
            )
            field.widget.grid(
                row=row,
                column=1,
                padx=10,
                pady=5,
                sticky=tk.NW
            )
            if field.tool_tip:
                field.tool_tip.grid(
                    row=row,
                    column=2,
                    padx=10,
                    sticky=tk.NW
                )

    # Main method for handling changes in form input
    def create_preview(self, *_):
        """ Create a slider and code based on current form values. """
        # Get arguments from form and try to create a slider
        self.kwargs = {}
        self.clear_preview_pane()
        self.code_pane.delete(1.0, tk.END)

        for field in self.form_fields:
            try:
                value = field.get()
            except ValueError:
                msg = f"Invalid input in {field.kwarg_label_text}"
                self.show_error(msg)
                raise

            # Omit defaults as slider sets defaults itself
            if value != field.default_val:
                self.kwargs[field.kwarg_name] = value

        try:
            self.my_slider = slider.Slider(
                self.slider_pane,
                **self.kwargs,
            )
        except Exception as exception:
            msg = "Error in args, try again\n" + str(exception)
            self.show_error(msg)
            raise

        # Create a slider
        self.my_slider.grid(row=0, column=0)
        self.my_slider.add_subscriber(self.slider_value)

        # Create code
        """
        # Debug / dev only:
        # Create dict-style code
        # Useful when generating prebuilts for config.py
        code_string = "\n"
        for key in self.kwargs:
            arg = self.kwargs.get(key)
            val = f"'{arg}'" if type(arg) is str else arg
            code_string += f"'{key}': {val},"
            code_string += "\n"
        self.code_pane.insert(1.0, code_string)
        """

        code_string = "slider.Slider(\n    root,"
        for key in self.kwargs:
            arg = self.kwargs.get(key)
            val = f"'{arg}'" if type(arg) is str else arg
            code_string += f"\n    {key}={val},"
        code_string += "\n)"
        self.code_pane.insert(1.0, code_string)

        # Reset window size to fit contents neatly
        self.parent.geometry("")

    # Build a prebuilt slider when selected
    def set_prebuilt(self, *_):
        """ Create a slider from preset arguments stored in the
        'prebuilt' object
        """
        self.reset(redraw=False)
        self.disable_observatory()
        index = self.prebuilt_index[self.current_prebuilt.get()]
        for key in self.prebuilts[index].args:
            value = self.prebuilts[index].args[key]
            field_index = self.field_index[key]
            self.form_fields[field_index].tk_var.set(value)
        self.preview_pane.select(self.preview_tab_1)
        self.create_preview()
        self.enable_observatory()

    # Create a slider from code input
    def run_code(self):
        """ Create a slider based on the code in the code pane. Any
        valid "key=value" line in the input will be used, other input
        will be ignored.
        """
        self.clear_preview_pane()
        self.reset(redraw=False)  # preserve code until all is well
        self.disable_observatory()
        kwargs = {}
        kwargs_okay = True
        invalid_kwargs = []

        code = (self.code_pane.get("1.0", tk.END)).split("\n")
        for line in code:
            if line.find("=") != -1:
                # Consider portion before "=" to be kwarg_name, and the
                # portion after to be kwarg_value
                kwarg_name, kwarg_value = line.split("=")

                # Do some cleaning
                kwarg_name = kwarg_name.strip()
                kwarg_value = kwarg_value.strip()
                kwarg_value = kwarg_value.rstrip(",")

                for character in ("'", '"', "(", ")"):
                    kwarg_value = kwarg_value.replace(character, "")

                # Test if keyword is valid
                try:
                    index = self.field_index[kwarg_name]
                    kwargs[index] = kwarg_value
                except KeyError:
                    kwargs_okay = False
                    invalid_kwargs.append(kwarg_name)

        if kwargs_okay:
            for index in kwargs:
                self.form_fields[index].tk_var.set(kwargs[index])
            # Note create_preview will override contents of code pane
            # with newly generated code
            self.preview_pane.select(self.preview_tab_1)
            self.create_preview()
        else:
            msg = f"\nInvalid arguments found:\n"
            self.code_pane.insert(tk.END, msg, "red")
            for arg in invalid_kwargs:
                self.code_pane.insert(tk.END, f"\n{arg}", "red")
            self.code_pane.see(tk.END)
        self.enable_observatory()

    # Enable auto-update of preview when form input changes
    def enable_observatory(self):
        """ Auto-redraw preview when input values change.
        Entry and combo will be bound to specific events in order
        to let validation do its work and to prevent all too jumpy
        behaviour. For other widgets we simply trace the tk_var of
        the widget.
        """
        for field in self.form_fields:
            if field.widget_type in ("entry", "combo"):
                for event in ("<FocusOut>",
                              "<Return>",
                              "<<ComboboxSelected>>"
                              ):
                    field.widget.bind(event, self.create_preview)
            else:
                field.trace_id = field.tk_var.trace_variable(
                    "w",
                    self.create_preview
                )

    # Disable auto-update of preview
    def disable_observatory(self):
        """ Disable auto-redraw to prevent an avalanche of redraws when
        (re)setting the form
        """
        for field in self.form_fields:
            if field.widget_type:
                field.widget.unbind("<FocusOut>")
                field.widget.unbind("<Return>")
                field.widget.unbind("<<ComboboxSelected>>")
            # This clause is to prevent exceptions when no trace present
            elif len(field.tk_var.trace_info()) > 0:
                field.tk_var.trace_remove("write", field.trace_id)

    # Helper functions
    def reset(self, redraw=True):
        """  Reset all input widgets to default value"""
        txt = "All input will be lost, do you want to reset the form?"
        ack = True
        if redraw:
            ack = messagebox.askokcancel("Reset", txt)
        if ack:
            self.disable_observatory()
            for field in self.form_fields:
                field.tk_var.set(field.default_val)
            if redraw:
                self.create_preview()
            self.enable_observatory()

    def clear_preview_pane(self):
        """ Delete the slider in the preview pane"""
        for widget in self.slider_pane.winfo_children():
            widget.destroy()
        # tk occasionally has some lag, preemptively set value to 0
        self.slider_value.set(0)

    def validate(self, value):
        """ Callback for validate, prevent empty widgets """
        return value != ""

    def correct(self, formfield_index):
        """ Callback for invalidcommand: set widget to default value """
        index = int(formfield_index)  # everything arrives as a string
        self.form_fields[index].widget.insert(
            0,
            self.form_fields[index].default_val
        )

    def copy_to_clipboard(self):
        """ Copy code from code pane to clipboard"""
        self.parent.clipboard_clear()
        self.parent.clipboard_append(self.code_pane.get("1.0", tk.END))

    def paste_from_clipboard(self):
        """ Paste code from clipboard to code pane """
        self.clear_preview_pane()
        self.code_pane.focus_set()  # avoid triggering focusout
        self.code_pane.delete(1.0, tk.END)
        self.code_pane.insert(1.0, self.parent.clipboard_get(), "green")

    def show_error(self, msg):
        """ Show error message in the preview pane """
        # Remove existing label
        self.clear_preview_pane()
        tk.Label(
            self.slider_pane,
            fg="red",
            font=("Courier", 16),
            text=msg
        ).grid(sticky=tk.NSEW)

    def code_changed(self, *_):
        """ Change font color in code pane when user bepotles code. """
        self.code_pane.tag_add("green", "1.0", tk.END)

    def on_closing(self):
        """  Let user reconsider their decision to part ways. """
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.parent.destroy()


# Mainloop
if __name__ == "__main__":
    root = tk.Tk()
    creator = Creator(root)
    root.mainloop()
