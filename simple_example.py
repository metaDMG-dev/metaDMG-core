import tkinter
from pathlib import Path
from tkinter import filedialog

import customtkinter


# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("System")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("blue")

from enum import Enum


class DAMAGE_MODE(str, Enum):
    "Damage mode allowed in the LCA"

    LCA = "lca"
    LOCAL = "local"
    GLOBAL = "global"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def upper_list(cls):
        return [c.upper() for c in cls.list()]


class App(customtkinter.CTk):

    WIDTH = 400
    HEIGHT = 580

    MAX_POSITION_MIN = 1
    MAX_POSITION_DEFAULT = 10
    MAX_POSITION_MAX = 30

    CUSTOM_DATABASE_TRUE = "Custom Database: ON"
    CUSTOM_DATABASE_FALSE = "Custom Database: OFF"

    def __init__(self):
        super().__init__()

        self.title("CustomTkinter simple_example.py")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.grid_columnconfigure((0, 1), weight=1)
        # call .on_closing() when app gets closed
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.bam_init()
        self.max_position_init()
        self.custom_database_init()
        self.damage_mode_init()

        self.print_config_button = customtkinter.CTkButton(
            master=self,
            text="Print",
            command=self.print_config,
        )
        self.print_config_button.grid(row=10, column=1, pady=12, padx=10)

    def print_config(self):
        print("")
        print("Config:")
        print(f"BAM file: {self.bam_file_string.get()}")
        print(f"Max Position: {int(self.max_position_slider.get())}")
        print(f"Custom Database: {self.custom_database_bool.get()}")
        print(f"Damage Mode: {self.damage_mode_string.get()}")

    # ============ BAM FILE (FILE) ============

    def bam_init(self):

        self.bam_file_string = customtkinter.StringVar()

        self.bam_label = customtkinter.CTkLabel(
            master=self,
            justify=tkinter.LEFT,
            text="Please select a BAM file",
        )
        self.bam_label.grid(row=0, column=0, pady=12, padx=10)

        self.bam_button = customtkinter.CTkButton(
            master=self,
            text="Input BAM file",
            command=self.bam_callback,
        )
        self.bam_button.grid(row=0, column=1, pady=12, padx=10)

    def bam_callback(self):
        # get a directory path by user
        filepath = filedialog.askopenfilename()
        text = f"BAM file: {Path(filepath).name}"
        self.bam_label.configure(text=text)
        self.bam_file_string.set(filepath)

    # ============ MAX POSITION (INTEGER) ============

    def max_position_init(self):

        self.max_position_label = customtkinter.CTkLabel(
            master=self,
            justify=tkinter.LEFT,
        )
        self.max_position_slider_callback(App.MAX_POSITION_DEFAULT)
        self.max_position_label.grid(row=1, column=0, pady=12, padx=10)

        self.max_position_slider = customtkinter.CTkSlider(
            master=self,
            command=self.max_position_slider_callback,
            from_=App.MAX_POSITION_MIN,
            to=App.MAX_POSITION_MAX,
            number_of_steps=App.MAX_POSITION_MAX - App.MAX_POSITION_MIN,
        )
        self.max_position_slider.set(App.MAX_POSITION_DEFAULT)
        self.max_position_slider.grid(row=1, column=1, pady=12, padx=10)

    def max_position_slider_callback(self, value):
        self.max_position_label.configure(text=f"Max Position: {int(value)}")

    # ============ CUSTOM DATABASE (BOOL) ============

    def custom_database_init(self):

        self.custom_database_label = customtkinter.CTkLabel(
            master=self,
            justify=tkinter.LEFT,
            text="Custom Database",
        )
        self.custom_database_label.grid(row=2, column=0, pady=12, padx=10)

        self.custom_database_bool = customtkinter.BooleanVar()

        self.custom_database_button_title = customtkinter.StringVar(
            value="False",
        )
        self.custom_database_switch = customtkinter.CTkSwitch(
            master=self,
            textvariable=self.custom_database_button_title,
            command=self.switch_event,
            onvalue=True,
            offvalue=False,
        )
        self.custom_database_switch.deselect()
        self.custom_database_switch.grid(row=2, column=1, pady=12, padx=10)

    def switch_event(self):
        state = self.custom_database_switch.get()
        self.custom_database_button_title.set(str(state))
        self.custom_database_bool.set(state)

    # ============ DAMAGE MODE (ENUM) ============

    def damage_mode_init(self):

        self.damage_mode_label = customtkinter.CTkLabel(
            master=self,
            text="Damage Mode",
            justify=tkinter.LEFT,
        )
        self.damage_mode_label.grid(row=3, column=0, pady=12, padx=10)

        self.damage_mode_string = customtkinter.StringVar(
            value=DAMAGE_MODE.LCA,
        )

        self.damage_mode_switch = customtkinter.CTkOptionMenu(
            master=self,
            values=DAMAGE_MODE.list(),
            variable=self.damage_mode_string,
        )

        self.damage_mode_switch.grid(row=3, column=1, pady=12, padx=10)

    # ============ OTHER ============

    def on_closing(self, event=0):
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()


# if False:

#     MAX_POSITION_MIN = 1
#     MAX_POSITION_DEFAULT = 10
#     MAX_POSITION_MAX = 30

#     app = customtkinter.CTk()
#     app.geometry("400x580")
#     app.title("CustomTkinter simple_example.py")

#     frame_1 = customtkinter.CTkFrame(master=app)
#     frame_1.pack(pady=20, padx=60, fill="both", expand=True)

#     def slider_callback(label, text):
#         label.configure(text=text)

#     def max_position_slider_callback(value):
#         slider_callback(max_position_label, f"Max Position: {int(value)}")

#     max_position_label = customtkinter.CTkLabel(
#         master=frame_1,
#         justify=tkinter.LEFT,
#     )
#     max_position_label.pack(pady=12, padx=10)
#     max_position_slider_callback(MAX_POSITION_DEFAULT)

#     max_position_slider = customtkinter.CTkSlider(
#         master=frame_1,
#         command=max_position_slider_callback,
#         from_=MAX_POSITION_MIN,
#         to=MAX_POSITION_MAX,
#         number_of_steps=MAX_POSITION_MAX - MAX_POSITION_MIN,
#     )
#     max_position_slider.pack(pady=12, padx=10)
#     max_position_slider.set(MAX_POSITION_DEFAULT)

#     app.mainloop()

#


# def button_callback():
#     print("Button click", combobox_1.get())

# def label_callback(value):
#     max_position_label.set(value)


# entry_1 = customtkinter.CTkEntry(
#     master=frame_1,
#     placeholder_text="CTkEntry",
#     command=label_callback,
# )
# entry_1.pack(pady=12, padx=10)


# progressbar_1 = customtkinter.CTkProgressBar(master=frame_1)
# progressbar_1.pack(pady=12, padx=10)

# button_1 = customtkinter.CTkButton(master=frame_1, command=button_callback)
# button_1.pack(pady=12, padx=10)


# def get_directory():
#     # get a directory path by user
#     directory = filedialog.askdirectory(title="Dialog box XXX")
#     print(f"Directory is: {directory}")


# button_2 = customtkinter.CTkButton(
#     master=frame_1,
#     text="Output Folder",
#     command=get_directory,
# )
# button_2.pack(pady=12, padx=10)


# def get_file():
#     # get a directory path by user
#     filepath = filedialog.askopenfilename(title="Dialog box YYY")
#     print(f"File is: {filepath}")


# button_3 = customtkinter.CTkButton(
#     master=frame_1,
#     text="Output File",
#     command=get_file,
# )
# button_3.pack(pady=12, padx=10)


# optionmenu_1 = customtkinter.CTkOptionMenu(
#     frame_1, values=["Option A", "Option B", "Option ABC long long long..."]
# )
# optionmenu_1.pack(pady=12, padx=10)
# optionmenu_1.set("CTkOptionMenu")

# combobox_1 = customtkinter.CTkComboBox(
#     frame_1, values=["Option 1", "Option 2", "Option 42 long long long..."]
# )
# combobox_1.pack(pady=12, padx=10)
# combobox_1.set("CTkComboBox")

# checkbox_1 = customtkinter.CTkCheckBox(master=frame_1)
# checkbox_1.pack(pady=12, padx=10)

# radiobutton_var = tkinter.IntVar(value=1)

# radiobutton_1 = customtkinter.CTkRadioButton(
#     master=frame_1, variable=radiobutton_var, value=1
# )
# radiobutton_1.pack(pady=12, padx=10)

# radiobutton_2 = customtkinter.CTkRadioButton(
#     master=frame_1, variable=radiobutton_var, value=2
# )
# radiobutton_2.pack(pady=12, padx=10)

# switch_1 = customtkinter.CTkSwitch(master=frame_1)
# switch_1.pack(pady=12, padx=10)
