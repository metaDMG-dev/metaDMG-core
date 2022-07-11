import tkinter
from pathlib import Path
from tkinter import W, filedialog

import customtkinter
from customtkinter import ThemeManager


# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("dark")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("blue")

from enum import Enum


output_dir_default = Path("./data/")


FONT = ThemeManager.theme["text"]["font"]


def format_directory(path: Path):
    return path.name + "/"


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


class RANKS(str, Enum):
    "Ranks allowed in the LCA"

    family = "family"
    genus = "genus"
    species = "species"
    none = ""

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def str_list(cls):
        return [c if c != "" else "None" for c in cls.list()]


KW_OPTIONS_MENU = dict(
    fg_color="gray30",
    button_color="gray50",
    button_hover_color="gray60",
)

KW_OPTIONS_MENU_DISABLED = dict(
    fg_color="gray25",
    button_color="gray30",
)

KW_BUTTON = dict(
    border_width=2,
    fg_color=None,
    hover_color="gray30",
    border_color="gray30",
    text_color_disabled="gray40",
)

KW_BUTTON_GRID = dict(
    pady=12,
    padx=10,
    sticky="nsew",
)


KW_LABEL = dict(
    pady=12,
    padx=10,
    sticky="nsew",
)

KW_LABEL_GRID = dict(
    pady=12,
    padx=10,
    sticky="nsew",
)


NAMES_NODES_ACC_LABEL_GRID = dict(
    pady=12,
    padx=10,
    sticky="nse",
)

NAMES_NODES_ACC_BUTTON_GRID = dict(
    pady=12,
    padx=10,
    sticky="w",
)

KW_ENTRY = dict(
    border_color="gray30",
    text_color="gray90",
    placeholder_text_color="gray90",
)
KW_ENTRY_DISABLED = dict(
    border_color="gray30",
    text_color="gray40",
    placeholder_text_color="gray40",
)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("CustomTkinter simple_example.py")

        WIDTH = 800
        HEIGHT = 1000

        self.geometry(f"{WIDTH}x{HEIGHT}")
        # call .on_closing() when app gets closed
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # self.grid_columnconfigure((0, 1), weight=1)

        # configure grid layout (1x2)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)

        self.headline = customtkinter.CTkLabel(
            master=self,
            justify=tkinter.CENTER,
            text="Configuirator",
            text_font=(FONT, "-30"),
        )
        self.headline.grid(row=0, column=0, pady=12, padx=10)

        self.frame_main = customtkinter.CTkFrame(master=self)
        self.frame_main.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=20,
            pady=20,
        )

        self.frame_main.columnconfigure(0, weight=1)
        self.frame_main.rowconfigure(0, weight=1)
        self.frame_main.rowconfigure(1, weight=4)
        self.frame_main.rowconfigure(2, weight=6)

        self.frame_top = customtkinter.CTkFrame(master=self.frame_main)
        self.frame_top.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=20,
            pady=20,
        )

        self.frame_top.columnconfigure((0, 1, 2, 3), weight=1)
        self.frame_top.rowconfigure(0, weight=1)

        self.init_bam()
        self.init_damage_mode()

        self.frame_center = customtkinter.CTkFrame(master=self.frame_main)
        self.frame_center.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=20,
            pady=20,
        )

        self.frame_center.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.frame_center.rowconfigure((0, 1, 2, 3), weight=1)

        self.init_names()
        self.init_nodes()
        self.init_acc2tax()
        self.init_similarity_score()
        self.init_min_mapping_quality()
        self.init_custom_database()
        self.init_lca_rank()

        self.frame_bottom = customtkinter.CTkFrame(master=self.frame_main)
        self.frame_bottom.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=20,
            pady=20,
        )

        self.frame_bottom.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.frame_bottom.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

        self.init_max_position()
        self.init_min_reads()
        self.init_bayesian_forward()

        self.print_config_button = customtkinter.CTkButton(
            master=self,
            text="Generate Config",
            command=self.print_config_callback,
        )
        self.print_config_button.grid(row=2, column=0, pady=12, padx=10)

        inits = [
            self.init_output_dir,
            self.init_sample_prefix,
            self.init_print_config,
        ]

        # for row, init in enumerate(inits):
        #     init(row)

        # ============ BAM FILE (FILE) ============

    def init_bam(self):

        self.bam_file_string = customtkinter.StringVar()

        self.bam_label = customtkinter.CTkLabel(
            master=self.frame_top,
            text="BAM file:",
            justify=tkinter.RIGHT,
            width=10,
        )
        self.bam_label.grid(
            row=0,
            column=0,
            pady=12,
            padx=10,
            sticky="nse",
        )

        self.bam_button = customtkinter.CTkButton(
            master=self.frame_top,
            text="Please select",
            command=self.bam_callback,
            width=10,
            **KW_BUTTON,
        )
        self.bam_button.grid(
            row=0,
            column=1,
            pady=12,
            padx=10,
            sticky="w",
        )

    def bam_callback(self):
        filepath = filedialog.askopenfilename()
        if filepath != "":
            print(filepath)
            self.bam_file_string.set(filepath)
            text = Path(filepath).name
            self.bam_button.configure(text=text)

    # ============ DAMAGE MODE (ENUM) ============

    def init_damage_mode(self):

        self.damage_mode_label = customtkinter.CTkLabel(
            master=self.frame_top,
            text="Damage Mode:",
            justify=tkinter.RIGHT,
            width=50,
        )
        self.damage_mode_label.grid(
            row=0,
            column=2,
            pady=12,
            padx=10,
            sticky="nse",
        )

        self.damage_mode_string = customtkinter.StringVar(
            value=DAMAGE_MODE.LCA,
        )

        self.damage_mode_menu = customtkinter.CTkOptionMenu(
            master=self.frame_top,
            values=DAMAGE_MODE.list(),
            variable=self.damage_mode_string,
            command=self.damage_mode_collback,
            width=100,
            **KW_OPTIONS_MENU,
        )

        self.damage_mode_menu.grid(
            row=0,
            column=3,
            pady=12,
            padx=10,
            sticky="w",
        )

    def damage_mode_collback(self, choice):

        if choice == DAMAGE_MODE.LCA:
            lca_state = "normal"
            text_color = "gray90"
            slider_button_color = ThemeManager.theme["color"]["slider_button"]
            slider_progress_color = ThemeManager.theme["color"]["slider_progress"]
            lca_rank_menu_kw = KW_OPTIONS_MENU
            similarity_score_kw = KW_ENTRY

        else:
            lca_state = "disabled"
            text_color = "gray40"
            slider_button_color = "gray40"
            slider_progress_color = "gray40"
            lca_rank_menu_kw = KW_OPTIONS_MENU_DISABLED
            similarity_score_kw = KW_ENTRY_DISABLED

        texts = [
            self.names_label,
            self.nodes_label,
            self.acc2tax_label,
            self.similarity_score_label,
            self.similarity_score_to,
            self.min_mapping_quality_label,
            self.custom_database_label,
            self.lca_rank_label,
        ]

        for text in texts:
            text.configure(text_color=text_color)

        states = [
            self.names_button,
            self.nodes_button,
            self.acc2tax_button,
            self.similarity_score_min,
            self.similarity_score_max,
            self.min_mapping_quality_slider,
            self.custom_database_switch,
            self.lca_rank_menu,
        ]

        for state in states:
            state.configure(state=lca_state)

        self.min_mapping_quality_slider.configure(
            button_color=slider_button_color,
            progress_color=slider_progress_color,
        )

        self.lca_rank_menu.configure(**lca_rank_menu_kw)
        self.similarity_score_min.configure(**similarity_score_kw)
        self.similarity_score_max.configure(**similarity_score_kw)

    # ============ NAMES FILE (FILE) ============

    def init_names(self):

        self.names_file_string = customtkinter.StringVar()

        self.names_label = customtkinter.CTkLabel(
            master=self.frame_center,
            justify=tkinter.LEFT,
            text="Names:",
            # width=10,
        )
        self.names_label.grid(
            row=0,
            column=0,
            **NAMES_NODES_ACC_LABEL_GRID,
        )

        self.names_button = customtkinter.CTkButton(
            master=self.frame_center,
            text="Please select",
            command=self.names_callback,
            # width=10,
            **KW_BUTTON,
        )
        self.names_button.grid(
            row=0,
            column=1,
            **NAMES_NODES_ACC_BUTTON_GRID,
        )

    def names_callback(self):
        filepath = filedialog.askopenfilename()
        if filepath != "":
            self.names_file_string.set(filepath)
            text = Path(filepath).name
            self.names_button.configure(text=text)

    # ============ NODES FILE (FILE) ============

    def init_nodes(self):

        self.nodes_file_string = customtkinter.StringVar()

        self.nodes_label = customtkinter.CTkLabel(
            master=self.frame_center,
            justify=tkinter.RIGHT,
            text="Nodes:",
            width=10,
        )
        self.nodes_label.grid(
            row=0,
            column=2,
            **NAMES_NODES_ACC_LABEL_GRID,
        )

        self.nodes_button = customtkinter.CTkButton(
            master=self.frame_center,
            text="Please select",
            command=self.nodes_callback,
            width=10,
            **KW_BUTTON,
        )
        self.nodes_button.grid(
            row=0,
            column=3,
            **NAMES_NODES_ACC_BUTTON_GRID,
        )

    def nodes_callback(self):
        filepath = filedialog.askopenfilename()
        if filepath != "":
            self.nodes_file_string.set(filepath)
            text = Path(filepath).name
            self.nodes_button.configure(text=text)

    # ============ ACC2TAX FILE (FILE) ============

    def init_acc2tax(self):

        self.acc2tax_file_string = customtkinter.StringVar()

        self.acc2tax_label = customtkinter.CTkLabel(
            master=self.frame_center,
            justify=tkinter.RIGHT,
            text="Acc2tax:",
            width=10,
        )
        self.acc2tax_label.grid(
            row=0,
            column=4,
            **NAMES_NODES_ACC_LABEL_GRID,
        )

        self.acc2tax_button = customtkinter.CTkButton(
            master=self.frame_center,
            text="Please select",
            command=self.acc2tax_callback,
            width=10,
            **KW_BUTTON,
        )
        self.acc2tax_button.grid(
            row=0,
            column=5,
            **NAMES_NODES_ACC_BUTTON_GRID,
        )

    def acc2tax_callback(self):
        filepath = filedialog.askopenfilename()
        if filepath != "":
            self.acc2tax_file_string.set(filepath)
            text = Path(filepath).name
            self.acc2tax_button.configure(text=text)

    # ============ SIMILARITY SCORE (ENTRY BOXES) ============

    def init_similarity_score(self):

        self.similarity_score_label = customtkinter.CTkLabel(
            master=self.frame_center,
            text="Similarity Score:",
        )
        self.similarity_score_label.grid(
            row=1,
            column=0,
            columnspan=1,
            # sticky="nsw",
        )

        self.similarity_score_min_value = customtkinter.StringVar(
            value="0.95",
        )

        self.similarity_score_min = customtkinter.CTkEntry(
            master=self.frame_center,
            textvariable=self.similarity_score_min_value,
            # placeholder_text="minimum",
            **KW_ENTRY,
        )
        self.similarity_score_min.grid(
            row=1,
            column=2,
            # columnspan=2,
            sticky="e",
        )

        self.similarity_score_to = customtkinter.CTkLabel(
            master=self.frame_center,
            text="to",
        )
        self.similarity_score_to.grid(
            row=1,
            column=3,
            columnspan=1,
            # sticky="nsw",
        )

        self.similarity_score_max_value = customtkinter.StringVar(
            value="1.0",
        )

        self.similarity_score_max = customtkinter.CTkEntry(
            master=self.frame_center,
            textvariable=self.similarity_score_max_value,
            **KW_ENTRY,
        )
        self.similarity_score_max.grid(
            row=1,
            column=4,
            # columnspan=2,
            sticky="w",
        )

    # ============ MAPPING QUALITY (INTEGER) ============

    def init_min_mapping_quality(self):

        MIN_MAPPING_QUALITY_MIN = 0
        MIN_MAPPING_QUALITY_DEFAULT = 0
        MIN_MAPPING_QUALITY_MAX = 50

        self.min_mapping_quality_label = customtkinter.CTkLabel(
            master=self.frame_center,
            # justify=tkinter.LEFT,
        )
        self.min_mapping_quality_slider_callback(MIN_MAPPING_QUALITY_DEFAULT)
        self.min_mapping_quality_label.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="nsw",
        )

        self.min_mapping_quality_slider = customtkinter.CTkSlider(
            master=self.frame_center,
            command=self.min_mapping_quality_slider_callback,
            from_=MIN_MAPPING_QUALITY_MIN,
            to=MIN_MAPPING_QUALITY_MAX,
            number_of_steps=MIN_MAPPING_QUALITY_MAX - MIN_MAPPING_QUALITY_MIN,
        )
        self.min_mapping_quality_slider.set(MIN_MAPPING_QUALITY_DEFAULT)
        self.min_mapping_quality_slider.grid(
            row=2,
            column=2,
            columnspan=4,
        )

    def min_mapping_quality_slider_callback(self, value):
        self.min_mapping_quality_label.configure(
            text=f"Minimum Mapping Quality: {int(value):>2d}"
        )

    # ============ CUSTOM DATABASE (BOOL) ============

    def init_custom_database(self):

        self.custom_database_label = customtkinter.CTkLabel(
            master=self.frame_center,
            # justify=tkinter.LEFT,
            text="Custom Database:",
        )
        self.custom_database_label.grid(
            row=3,
            column=0,
            # columnspan=2,
            # sticky="nsw",
        )

        self.custom_database_bool = customtkinter.BooleanVar()
        self.custom_database_button_title = customtkinter.StringVar(
            value="False",
        )
        self.custom_database_switch = customtkinter.CTkSwitch(
            master=self.frame_center,
            textvariable=self.custom_database_button_title,
            command=self.custom_database_callback,
            onvalue=True,
            offvalue=False,
        )
        self.custom_database_switch.deselect()
        self.custom_database_switch.grid(
            row=3,
            column=1,
            # columnspan=4,
            sticky="w",
        )

    def custom_database_callback(self):
        state = self.custom_database_switch.get()
        self.custom_database_button_title.set(str(state))
        self.custom_database_bool.set(state)

    # ============ LCA RANK (ENUM) ============

    def init_lca_rank(self):

        self.lca_rank_label = customtkinter.CTkLabel(
            master=self.frame_center,
            text="LCA Rank:",
            # justify=tkinter.RIGHT,
        )
        self.lca_rank_label.grid(
            row=3,
            column=3,
            # pady=12,
            # padx=10,
        )

        self.lca_rank_string = customtkinter.StringVar(
            value=RANKS.none,
        )

        self.lca_rank_menu = customtkinter.CTkOptionMenu(
            master=self.frame_center,
            values=RANKS.str_list(),
            # variable=self.lca_rank_string,
            command=self.lca_rank_callback,
            text_color_disabled="gray40",
            **KW_OPTIONS_MENU,
        )
        self.lca_rank_menu.set("None")  # set initial value

        self.lca_rank_menu.grid(
            row=3,
            column=4,
            sticky="w",
            # pady=12,
            # padx=10,
        )

    def lca_rank_callback(self, choice):
        self.lca_rank_string.set(choice if choice != "None" else RANKS.none)

    # ============ OUTPUT DIR (DIRECTORY) ============

    def init_output_dir(self, row):

        self.output_dir_string = customtkinter.StringVar()

        self.output_dir_label = customtkinter.CTkLabel(
            master=self,
            justify=tkinter.RIGHT,
            text="Output Directory",
        )
        self.output_dir_label.grid(row=row, column=0, pady=12, padx=10)

        self.output_dir_button = customtkinter.CTkButton(
            master=self,
            text=format_directory(output_dir_default),
            command=self.output_dir_callback,
            **KW_BUTTON,
        )
        self.output_dir_button.grid(row=row, column=1, pady=12, padx=10)

    def output_dir_callback(self):
        # get a directory path by user
        filepath = filedialog.askdirectory()
        self.output_dir_string.set(filepath)

        text = format_directory(Path(filepath))
        self.output_dir_button.configure(text=text)

    # ============ MAX POSITION (INTEGER) ============

    def init_max_position(self):

        MAX_POSITION_MIN = 1
        MAX_POSITION_DEFAULT = 15
        MAX_POSITION_MAX = 30

        self.max_position_label = customtkinter.CTkLabel(
            master=self.frame_bottom,
            # justify=tkinter.RIGHT,
        )
        self.max_position_slider_callback(MAX_POSITION_DEFAULT)
        self.max_position_label.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="nsw",
        )

        self.max_position_slider = customtkinter.CTkSlider(
            master=self.frame_bottom,
            command=self.max_position_slider_callback,
            from_=MAX_POSITION_MIN,
            to=MAX_POSITION_MAX,
            number_of_steps=MAX_POSITION_MAX - MAX_POSITION_MIN,
        )
        self.max_position_slider.set(MAX_POSITION_DEFAULT)
        self.max_position_slider.grid(
            row=0,
            column=2,
            columnspan=4,
        )

    def max_position_slider_callback(self, value):
        self.max_position_label.configure(text=f"Max Position: {int(value):>2d}")

    # ============ MIN READS (ENTRY BOX) ============

    def init_min_reads(self):

        self.min_reads_label = customtkinter.CTkLabel(
            master=self.frame_bottom,
            text="Minimum number of reads:",
            # justify=tkinter.RIGHT,
        )
        self.min_reads_label.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsw",
        )

        self.min_reads_value = customtkinter.StringVar(
            value="0",
        )

        self.min_reads = customtkinter.CTkEntry(
            master=self.frame_bottom,
            textvariable=self.min_reads_value,
            **KW_ENTRY,
        )
        self.min_reads.grid(
            row=1,
            column=2,
            columnspan=4,
        )

    # ============ BAYESIAN // FORWARD (BOOLS) ============

    def init_bayesian_forward(self):

        self.bayesian_label = customtkinter.CTkLabel(
            master=self.frame_bottom,
            text="Bayesian:",
        )
        self.bayesian_label.grid(
            row=2,
            column=0,
            columnspan=1,
            sticky="e",
        )

        self.bayesian_bool = customtkinter.BooleanVar()
        self.bayesian_button_title = customtkinter.StringVar(
            value="False",
        )
        self.bayesian_switch = customtkinter.CTkSwitch(
            master=self.frame_bottom,
            textvariable=self.bayesian_button_title,
            command=self.bayesian_callback,
            onvalue=True,
            offvalue=False,
        )
        self.bayesian_switch.deselect()
        self.bayesian_switch.grid(
            row=2,
            column=1,
            sticky="w",
        )

        self.forward_label = customtkinter.CTkLabel(
            master=self.frame_bottom,
            text="Forward only:",
        )
        self.forward_label.grid(
            row=2,
            column=3,
            columnspan=1,
            sticky="e",
        )

        self.forward_bool = customtkinter.BooleanVar()
        self.forward_button_title = customtkinter.StringVar(
            value="False",
        )
        self.forward_switch = customtkinter.CTkSwitch(
            master=self.frame_bottom,
            textvariable=self.forward_button_title,
            command=self.forward_callback,
            onvalue=True,
            offvalue=False,
        )
        self.forward_switch.deselect()
        self.forward_switch.grid(
            row=2,
            column=4,
            sticky="w",
        )

    def bayesian_callback(self):
        state = self.bayesian_switch.get()
        self.bayesian_button_title.set(str(state))
        self.bayesian_bool.set(state)

    def forward_callback(self):
        state = self.forward_switch.get()
        self.forward_button_title.set(str(state))
        self.forward_bool.set(state)

    # ============ SAMPLE PREFIX (ENTRY) ============

    def init_sample_prefix(self, row):

        self.sample_prefix_label = customtkinter.CTkLabel(
            master=self,
            text="Sample Prefix",
            justify=tkinter.RIGHT,
        )
        self.sample_prefix_label.grid(row=row, column=0, pady=12, padx=10)

        self.sample_prefix_entry = customtkinter.CTkEntry(
            master=self,
            placeholder_text="",
        )
        self.sample_prefix_entry.grid(row=row, column=1, pady=12, padx=10)

    # ============ PRINT ============

    def init_print_config(self, row):

        self.print_config_button = customtkinter.CTkButton(
            master=self,
            text="Print",
            command=self.print_config_callback,
        )
        self.print_config_button.grid(row=row, column=1, pady=12, padx=10)

    def print_config_callback(self):
        print("")
        print("Config:")
        print(f"BAM file: {self.bam_file_string.get()}")
        print(f"Damage Mode: {self.damage_mode_string.get()}")
        print(f"similarity_score_min: {self.similarity_score_min.get()}")
        print(f"similarity_score_max: {self.similarity_score_max.get()}")
        print(f"Custom Database: {self.custom_database_bool.get()}")
        print(f"LCA Rank: {self.lca_rank_string.get()}")
        print(f"Output directory: {self.output_dir_string.get()}")
        print(f"Max Position: {int(self.max_position_slider.get())}")
        print(f"Sample Prefix: {self.sample_prefix_entry.get()}")

    # ============ OTHER ============

    def on_closing(self, event=0):
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
