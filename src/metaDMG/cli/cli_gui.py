from pathlib import Path
from threading import Thread
from time import sleep
from tkinter import filedialog

import customtkinter
from rich import print

from metaDMG.cli import cli_utils


#%%

# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("dark")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("blue")

FONT = customtkinter.ThemeManager.theme["text"]["font"]


#%%


def format_directory(path: Path):
    return path.name + "/"


def path_to_text(filepath: str, cut: int = 10) -> str:
    text = Path(filepath).name
    if len(text) > cut:
        text = text[:cut] + " ..."
    return text


#%%

KW_OPTIONS_MENU = dict(
    fg_color="gray30",
    button_color="gray50",
    button_hover_color="gray60",
)

KW_OPTIONS_MENU_DISABLED = dict(
    fg_color="gray25",
    button_color="gray30",
)


KW_BUTTON_BASE = dict(
    hover=True,
    border_width=2,
    text_color_disabled="gray40",
)

KW_BUTTON_GOOD_COLORS = dict(
    fg_color=None,
    hover_color="gray30",
    border_color="gray30",
)

KW_BUTTON_BAD_COLORS = dict(
    hover_color="#78413d",
    border_color="#78413d",
    fg_color="#603431",
)


KW_ENTRY_GOOD_COLORS = dict(
    border_color="gray30",
    text_color="gray90",
    placeholder_text_color="gray90",
    fg_color="#2A2D2E",
)
KW_ENTRY_DISABLED = dict(
    border_color="gray30",
    text_color="gray40",
    placeholder_text_color="gray40",
    fg_color="#2A2D2E",
)

KW_ENTRY_BAD_COLORS = dict(
    border_color="#78413d",
    text_color="gray90",
    placeholder_text_color="gray90",
    fg_color="#603431",
)


KW_SWITCH = dict(button_color="gray80")
KW_SWITCH_DISABLED = dict(button_color="gray40")


KW_SLIDER = dict(
    button_color="#1F6AA5",
    progress_color="#AAB0B5",
)
KW_SLIDER_DISABLED = dict(
    button_color="gray40",
    progress_color="gray40",
)


TOP_LABEL_WIDTH = 50
TOP_LABEL_PAD_X = 20
TOP_LABEL_GRID_KW = dict(
    pady=12,
    padx=TOP_LABEL_PAD_X,
    sticky="nsw",
)

CENTER_LABEL_WIDTH = 50
CENTER_LABEL_PAD_X = 20
CENTER_LABEL_GRID_KW = dict(
    pady=12,
    padx=CENTER_LABEL_PAD_X,
    sticky="nsw",
)

RIGHT_LABEL_WIDTH = 50
RIGHT_LABEL_PAD_X = 20
RIGHT_LABEL_GRID_KW = dict(
    pady=12,
    padx=RIGHT_LABEL_PAD_X,
    sticky="nsw",
)


#%%


class Gui(customtkinter.CTk):
    def __init__(self, verbose: bool = True):
        super().__init__()

        self.verbose = verbose

        self.title("MetaDMG Configuirator")

        WIDTH = 785
        HEIGHT = 655
        X, Y = self.get_center_coordinates(WIDTH, HEIGHT)
        self.geometry(f"{WIDTH}x{HEIGHT}+{X}+{Y}")
        self.resizable(False, False)

        # call .on_closing() when app gets closed
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # ============ create frames ============
        self.setup_header()

        # ============ frame_top ============
        self.setup_top_frame()

        # ============ frame_center ============
        self.setup_center_frame()

        # ============ frame_right ============
        self.setup_right_frame()

        # ============ background threads ============
        self.start_similarity_scores_background_thread()
        self.start_minimum_reads_background_thread()

    # ============ HEADER ============

    def setup_header(self):

        self.headline = customtkinter.CTkLabel(
            master=self,
            justify="center",
            text="Confi-gui-rator",
            text_font=(FONT, "-30"),
        )
        self.headline.grid(
            row=0,
            column=0,
            columnspan=2,
        )

    # ============ TOP FRAME ============

    def setup_top_frame(self):

        self.frame_top = customtkinter.CTkFrame(
            master=self,
        )
        self.frame_top.grid(
            row=1,
            column=0,
            sticky="nswe",
            padx=20,
            pady=20,
        )

        # # empty row with minsize as spacing
        # self.frame_top.grid_rowconfigure(0, minsize=50)
        # # empty row with minsize as spacing
        self.frame_top.grid_columnconfigure(1, minsize=80)
        self.TOP_LABEL_KW = dict(master=self.frame_top, width=TOP_LABEL_WIDTH)

        self.setup_bam_file()
        self.setup_damage_mode()

    # ============ BAM FILE ============

    def setup_bam_file(self):

        self.bam_label = customtkinter.CTkLabel(
            text="BAM file:",
            **self.TOP_LABEL_KW,
        )
        self.bam_label.grid(
            row=0,
            column=0,
            **TOP_LABEL_GRID_KW,
        )

        self.bam_file_path = None

        self.bam_button = customtkinter.CTkButton(
            master=self.frame_top,
            text="Select file",
            command=self.bam_callback,
            **KW_BUTTON_BASE,
            **KW_BUTTON_BAD_COLORS,
        )
        self.bam_button.grid(
            row=0,
            column=2,
            pady=12,
            sticky="e",
        )
        self.bam_is_okay = False

    # ============ DAMAGE MODE ============

    def setup_damage_mode(self):

        self.damage_mode_label = customtkinter.CTkLabel(
            text="Damage Mode:",
            **self.TOP_LABEL_KW,
        )
        self.damage_mode_label.grid(
            row=1,
            column=0,
            **TOP_LABEL_GRID_KW,
        )

        self.damage_mode_value = cli_utils.DAMAGE_MODE.LCA

        self.damage_mode_menu = customtkinter.CTkOptionMenu(
            master=self.frame_top,
            values=cli_utils.DAMAGE_MODE.list(),
            command=self.damage_mode_collback,
            **KW_OPTIONS_MENU,
        )

        self.damage_mode_menu.grid(
            row=1,
            column=2,
            pady=12,
            sticky="e",
        )

        self.is_lca = True

    # ============ CENTER FRAME ============

    def setup_center_frame(self):

        self.frame_center = customtkinter.CTkFrame(
            master=self,
        )
        self.frame_center.grid(
            row=2,
            column=0,
            sticky="nswe",
            padx=20,
            # pady=20,
        )

        # configure grid layout (3 x 2) (row x column)
        self.frame_center.grid_rowconfigure(0, minsize=10)
        self.CENTER_LABEL_KW = dict(master=self.frame_center, width=CENTER_LABEL_WIDTH)

        self.setup_names()
        self.setup_nodes()
        self.setup_acc2tax()
        self.setup_similarity_score()
        self.setup_min_mapping_quality()
        self.setup_custom_database()
        self.setup_lca_rank()

    # ============ NAMES ============

    def setup_names(self):

        # self.names_file_string = customtkinter.StringVar()
        self.names_file_path = None

        self.names_label = customtkinter.CTkLabel(
            text="Names:",
            **self.CENTER_LABEL_KW,
        )
        self.names_label.grid(
            row=1,
            column=0,
            **CENTER_LABEL_GRID_KW,
        )

        self.names_button = customtkinter.CTkButton(
            master=self.frame_center,
            text="Select file",
            command=self.names_callback,
            **KW_BUTTON_BASE,
            **KW_BUTTON_BAD_COLORS,
        )
        self.names_button.grid(
            row=1,
            column=1,
            pady=12,
            padx=10,
        )
        self.names_is_okay = False
        self.names_button_colors = KW_BUTTON_BAD_COLORS

    # ============ NODES ============

    def setup_nodes(self):

        self.nodes_file_path = None

        self.nodes_label = customtkinter.CTkLabel(
            text="Nodes:",
            **self.CENTER_LABEL_KW,
        )
        self.nodes_label.grid(
            row=2,
            column=0,
            **CENTER_LABEL_GRID_KW,
        )

        self.nodes_button = customtkinter.CTkButton(
            master=self.frame_center,
            text="Select file",
            command=self.nodes_callback,
            **KW_BUTTON_BASE,
            **KW_BUTTON_BAD_COLORS,
        )
        self.nodes_button.grid(
            row=2,
            column=1,
            pady=12,
            padx=10,
        )

        self.nodes_is_okay = False
        self.nodes_button_colors = KW_BUTTON_BAD_COLORS

    # ============ ACC2TAX ============

    def setup_acc2tax(self):

        self.acc2tax_file_path = None

        self.acc2tax_label = customtkinter.CTkLabel(
            text="Acc2tax:",
            **self.CENTER_LABEL_KW,
        )
        self.acc2tax_label.grid(
            row=3,
            column=0,
            **CENTER_LABEL_GRID_KW,
        )

        self.acc2tax_button = customtkinter.CTkButton(
            master=self.frame_center,
            text="Select file",
            command=self.acc2tax_callback,
            **KW_BUTTON_BASE,
            **KW_BUTTON_BAD_COLORS,
        )

        self.acc2tax_button.grid(
            row=3,
            column=1,
            pady=12,
            padx=10,
        )

        self.acc2tax_is_okay = False
        self.acc2tax_button_colors = KW_BUTTON_BAD_COLORS

    # ============ SIMILARITY SCORE ============

    def setup_similarity_score(self):

        self.similarity_score_label = customtkinter.CTkLabel(
            text="Similarity Score:",
            **self.CENTER_LABEL_KW,
        )
        self.similarity_score_label.grid(
            row=4,
            column=0,
            **CENTER_LABEL_GRID_KW,
        )

        self.frame_similarity = customtkinter.CTkFrame(
            master=self.frame_center,
            fg_color="#2A2D2E",
        )
        self.frame_similarity.grid(
            row=4,
            column=1,
            columnspan=3,
            rowspan=1,
            # pady=20,
            padx=30,
            sticky="w",
        )

        self.similarity_score_min_value = customtkinter.StringVar(
            value="0.95",
        )

        self.similarity_score_min = customtkinter.CTkEntry(
            master=self.frame_similarity,
            textvariable=self.similarity_score_min_value,
            width=40,
            **KW_ENTRY_GOOD_COLORS,
        )
        self.similarity_score_min.grid(
            row=0,
            column=0,
            # sticky="nse",
        )

        self.similarity_score_to = customtkinter.CTkLabel(
            master=self.frame_similarity,
            text="to",
            width=20,
        )
        self.similarity_score_to.grid(
            row=0,
            column=1,
            # sticky="ns",
        )

        self.similarity_score_max_value = customtkinter.StringVar(
            value="1.0",
        )

        self.similarity_score_max = customtkinter.CTkEntry(
            master=self.frame_similarity,
            textvariable=self.similarity_score_max_value,
            width=40,
            **KW_ENTRY_GOOD_COLORS,
        )
        self.similarity_score_max.grid(
            row=0,
            column=2,
            # sticky="nsw",
        )

    # ============ MIN MAPPING QUALITY ============

    def setup_min_mapping_quality(self):

        MIN_MAPPING_QUALITY_MIN = 0
        MIN_MAPPING_QUALITY_DEFAULT = 0
        MIN_MAPPING_QUALITY_MAX = 50

        self.min_mapping_quality_label = customtkinter.CTkLabel(
            text="Minimum Mapping Quality:",
            **self.CENTER_LABEL_KW,
        )
        self.min_mapping_quality_label.grid(
            row=5,
            column=0,
            **CENTER_LABEL_GRID_KW,
        )

        self.frame_min_mapping_quality = customtkinter.CTkFrame(
            master=self.frame_center,
            fg_color="#2A2D2E",
        )
        self.frame_min_mapping_quality.grid(
            row=5,
            column=1,
            sticky="e",
        )

        self.min_mapping_quality_slider = customtkinter.CTkSlider(
            master=self.frame_min_mapping_quality,
            command=self.min_mapping_quality_slider_callback,
            from_=MIN_MAPPING_QUALITY_MIN,
            to=MIN_MAPPING_QUALITY_MAX,
            number_of_steps=MIN_MAPPING_QUALITY_MAX - MIN_MAPPING_QUALITY_MIN,
            width=100,
            **KW_SLIDER,
        )
        self.min_mapping_quality_slider.set(MIN_MAPPING_QUALITY_DEFAULT)
        self.min_mapping_quality_slider.grid(
            row=0,
            column=0,
            sticky="e",
        )

        self.min_mapping_quality_value = customtkinter.CTkLabel(
            master=self.frame_min_mapping_quality,
            width=20,
        )
        self.min_mapping_quality_slider_callback(MIN_MAPPING_QUALITY_DEFAULT)
        self.min_mapping_quality_value.grid(
            row=0,
            column=1,
            pady=12,
            padx=0,
        )

    # ============ CUSTOM DATABASE ============

    def setup_custom_database(self):

        self.custom_database_label = customtkinter.CTkLabel(
            text="Custom Database:",
            **self.CENTER_LABEL_KW,
        )
        self.custom_database_label.grid(
            row=6,
            column=0,
            **CENTER_LABEL_GRID_KW,
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
            **KW_SWITCH,
        )
        self.custom_database_switch.deselect()
        self.custom_database_switch.grid(
            row=6,
            column=1,
        )

    # ============ LCA RANK ============

    def setup_lca_rank(self):

        self.lca_rank_label = customtkinter.CTkLabel(
            text="LCA Rank:",
            **self.CENTER_LABEL_KW,
        )
        self.lca_rank_label.grid(
            row=7,
            column=0,
            **CENTER_LABEL_GRID_KW,
        )

        self.lca_rank_string = customtkinter.StringVar(
            value=cli_utils.RANKS.none,
        )

        self.lca_rank_menu = customtkinter.CTkOptionMenu(
            master=self.frame_center,
            values=cli_utils.RANKS.str_list(),
            command=self.lca_rank_callback,
            text_color_disabled="gray40",
            **KW_OPTIONS_MENU,
        )
        self.lca_rank_menu.set("none")  # set initial value

        self.lca_rank_menu.grid(
            row=7,
            column=1,
        )

    # ============ RIGHT FRAME ============

    def setup_right_frame(self):

        self.frame_right = customtkinter.CTkFrame(
            master=self,
        )
        self.frame_right.grid(
            row=1,
            column=1,
            # sticky="e",
            # sticky="nswe",
            rowspan=3,
            # padx=20,
            pady=20,
        )

        # configure grid layout (3 x 2) (row x column)

        self.frame_right.grid_rowconfigure(0, minsize=10)
        self.RIGHT_LABEL_KW = dict(
            master=self.frame_right,
            width=RIGHT_LABEL_WIDTH,
        )
        self.setup_max_position()
        self.setup_min_reads()
        self.setup_bayesian()
        self.setup_forward()
        self.setup_parallel_samples()
        self.setup_cores_per_sample()
        self.setup_prefix()
        self.setup_suffix()
        self.setup_long_name()
        self.setup_config_name()
        self.setup_output_dir()
        self.setup_save_config()

    # ============ MAX POSITION ============

    def setup_max_position(self):

        MAX_POSITION_MIN = 1
        MAX_POSITION_DEFAULT = 15
        MAX_POSITION_MAX = 30

        self.max_position_label = customtkinter.CTkLabel(
            text="Maximum Position:",
            **self.RIGHT_LABEL_KW,
        )
        self.max_position_label.grid(
            row=1,
            column=0,
            **RIGHT_LABEL_GRID_KW,
        )

        self.frame_max_position = customtkinter.CTkFrame(
            master=self.frame_right,
            fg_color="#2A2D2E",
        )
        self.frame_max_position.grid(
            row=1,
            column=1,
            sticky="e",
        )

        self.max_position_slider = customtkinter.CTkSlider(
            master=self.frame_max_position,
            command=self.max_position_slider_callback,
            from_=MAX_POSITION_MIN,
            to=MAX_POSITION_MAX,
            number_of_steps=MAX_POSITION_MAX - MAX_POSITION_MIN,
            width=100,
            **KW_SLIDER,
        )
        self.max_position_slider.set(MAX_POSITION_DEFAULT)
        self.max_position_slider.grid(
            row=0,
            column=0,
            sticky="e",
        )

        self.max_position_value = customtkinter.CTkLabel(
            master=self.frame_max_position,
            width=20,
        )
        self.max_position_value.grid(
            row=0,
            column=1,
            pady=12,
            padx=0,
        )

        self.max_position_slider_callback(MAX_POSITION_DEFAULT)

    # ============ MINIMUM READS ============

    def setup_min_reads(self):

        self.min_reads_label = customtkinter.CTkLabel(
            text="Minimum number of reads:",
            **self.RIGHT_LABEL_KW,
        )
        self.min_reads_label.grid(
            row=2,
            column=0,
            **RIGHT_LABEL_GRID_KW,
        )

        self.min_reads_value = customtkinter.StringVar(
            value="0",
        )

        self.min_reads_entry = customtkinter.CTkEntry(
            master=self.frame_right,
            textvariable=self.min_reads_value,
            **KW_ENTRY_GOOD_COLORS,
        )
        self.min_reads_entry.grid(
            row=2,
            column=1,
        )

    # ============ BAYESIAN ============

    def setup_bayesian(self):

        self.bayesian_label = customtkinter.CTkLabel(
            text="Bayesian:",
            **self.RIGHT_LABEL_KW,
        )
        self.bayesian_label.grid(
            row=3,
            column=0,
            **RIGHT_LABEL_GRID_KW,
        )

        self.bayesian_bool = customtkinter.BooleanVar()
        self.bayesian_button_title = customtkinter.StringVar(
            value="False",
        )
        self.bayesian_switch = customtkinter.CTkSwitch(
            master=self.frame_right,
            textvariable=self.bayesian_button_title,
            command=self.bayesian_callback,
            onvalue=True,
            offvalue=False,
            **KW_SWITCH,
        )
        self.bayesian_switch.deselect()
        self.bayesian_switch.grid(
            row=3,
            column=1,
        )

    # ============ FORWARD ============

    def setup_forward(self):

        self.forward_label = customtkinter.CTkLabel(
            text="Forward only:",
            **self.RIGHT_LABEL_KW,
        )
        self.forward_label.grid(
            row=4,
            column=0,
            **RIGHT_LABEL_GRID_KW,
        )

        self.forward_bool = customtkinter.BooleanVar()
        self.forward_button_title = customtkinter.StringVar(
            value="False",
        )
        self.forward_switch = customtkinter.CTkSwitch(
            master=self.frame_right,
            textvariable=self.forward_button_title,
            command=self.forward_callback,
            onvalue=True,
            offvalue=False,
            **KW_SWITCH,
        )
        self.forward_switch.deselect()
        self.forward_switch.grid(
            row=4,
            column=1,
        )

    # ============ PARALLEL SAMPLES ============

    def setup_parallel_samples(self):

        self.parallel_label = customtkinter.CTkLabel(
            text="Samples in parallel:",
            **self.RIGHT_LABEL_KW,
        )
        self.parallel_label.grid(
            row=5,
            column=0,
            **RIGHT_LABEL_GRID_KW,
        )

        self.frame_parallel_samples = customtkinter.CTkFrame(
            master=self.frame_right,
            fg_color="#2A2D2E",
        )
        self.frame_parallel_samples.grid(
            row=5,
            column=1,
            sticky="e",
        )

        PARALLEL_SAMPLES_MIN = 1
        PARALLEL_SAMPLES_DEFAULT = 1
        PARALLEL_SAMPLES_MAX = 20

        self.parallel_samples_slider = customtkinter.CTkSlider(
            master=self.frame_parallel_samples,
            command=self.parallel_samples_slider_callback,
            from_=PARALLEL_SAMPLES_MIN,
            to=PARALLEL_SAMPLES_MAX,
            number_of_steps=PARALLEL_SAMPLES_MAX - PARALLEL_SAMPLES_MIN,
            width=100,
            **KW_SLIDER,
        )
        self.parallel_samples_slider.set(PARALLEL_SAMPLES_DEFAULT)
        self.parallel_samples_slider.grid(
            row=0,
            column=0,
            sticky="e",
        )

        self.parallel_samples_value = customtkinter.CTkLabel(
            master=self.frame_parallel_samples,
            width=20,
        )
        self.parallel_samples_value.grid(
            row=0,
            column=1,
            pady=12,
            padx=0,
        )

        self.parallel_samples_slider_callback(PARALLEL_SAMPLES_DEFAULT)

    # ============ CORES PR. SAMPLE ============

    def setup_cores_per_sample(self):

        self.cores_per_sample_label = customtkinter.CTkLabel(
            text="Cores pr. sample:",
            **self.RIGHT_LABEL_KW,
        )
        self.cores_per_sample_label.grid(
            row=6,
            column=0,
            **RIGHT_LABEL_GRID_KW,
        )

        self.frame_cores_per_sample = customtkinter.CTkFrame(
            master=self.frame_right,
            fg_color="#2A2D2E",
        )
        self.frame_cores_per_sample.grid(
            row=6,
            column=1,
            sticky="e",
        )

        PARALLEL_CORES_PER_SAMPLE_MIN = 1
        PARALLEL_CORES_PER_SAMPLE_DEFAULT = 1
        PARALLEL_CORES_PER_SAMPLE_MAX = 20

        self.cores_per_sample_slider = customtkinter.CTkSlider(
            master=self.frame_cores_per_sample,
            command=self.cores_per_sample_slider_callback,
            from_=PARALLEL_CORES_PER_SAMPLE_MIN,
            to=PARALLEL_CORES_PER_SAMPLE_MAX,
            number_of_steps=PARALLEL_CORES_PER_SAMPLE_MAX
            - PARALLEL_CORES_PER_SAMPLE_MIN,
            width=100,
            **KW_SLIDER,
        )
        self.cores_per_sample_slider.set(PARALLEL_CORES_PER_SAMPLE_DEFAULT)
        self.cores_per_sample_slider.grid(
            row=0,
            column=0,
            sticky="e",
        )

        self.cores_per_sample_value = customtkinter.CTkLabel(
            master=self.frame_cores_per_sample,
            width=20,
        )
        self.cores_per_sample_value.grid(
            row=0,
            column=1,
            pady=12,
            padx=0,
        )

        self.cores_per_sample_slider_callback(PARALLEL_CORES_PER_SAMPLE_DEFAULT)

    # ============ PREFIX ============

    def setup_prefix(self):

        self.prefix_label = customtkinter.CTkLabel(
            text="Prefix:",
            **self.RIGHT_LABEL_KW,
        )
        self.prefix_label.grid(
            row=7,
            column=0,
            **RIGHT_LABEL_GRID_KW,
        )

        self.prefix_entry = customtkinter.CTkEntry(
            master=self.frame_right,
            placeholder_text="",
            **KW_ENTRY_GOOD_COLORS,
        )
        self.prefix_entry.grid(
            row=7,
            column=1,
        )

    # ============ SUFFIX ============

    def setup_suffix(self):

        self.suffix_label = customtkinter.CTkLabel(
            text="Suffix:",
            **self.RIGHT_LABEL_KW,
        )
        self.suffix_label.grid(
            row=8,
            column=0,
            **RIGHT_LABEL_GRID_KW,
        )

        self.suffix_entry = customtkinter.CTkEntry(
            master=self.frame_right,
            placeholder_text="",
            **KW_ENTRY_GOOD_COLORS,
        )
        self.suffix_entry.grid(
            row=8,
            column=1,
        )

    # ============ LONG NAME ============

    def setup_long_name(self):

        self.long_name_label = customtkinter.CTkLabel(
            text="Long name:",
            **self.RIGHT_LABEL_KW,
        )
        self.long_name_label.grid(
            row=9,
            column=0,
            **RIGHT_LABEL_GRID_KW,
        )

        self.long_name_bool = customtkinter.BooleanVar()
        self.long_name_button_title = customtkinter.StringVar(
            value="False",
        )
        self.long_name_switch = customtkinter.CTkSwitch(
            master=self.frame_right,
            textvariable=self.long_name_button_title,
            command=self.long_name_callback,
            onvalue=True,
            offvalue=False,
            **KW_SWITCH,
        )
        self.long_name_switch.deselect()
        self.long_name_switch.grid(
            row=9,
            column=1,
        )

    # ============ CONFIG NAME ============

    def setup_config_name(self):

        self.config_name_label = customtkinter.CTkLabel(
            text="Config Name:",
            **self.RIGHT_LABEL_KW,
        )
        self.config_name_label.grid(
            row=10,
            column=0,
            **RIGHT_LABEL_GRID_KW,
        )

        self.config_button = customtkinter.CTkButton(
            master=self.frame_right,
            text="Select file",
            command=self.config_callback,
            **KW_BUTTON_BASE,
            **KW_BUTTON_BAD_COLORS,
        )
        self.config_button.grid(
            row=10,
            column=1,
            pady=12,
            padx=10,
        )

        self.config_is_okay = False
        self.config_file_path = None

    # ============ OUTPUT DIRECTORY ============

    def setup_output_dir(self):

        self.output_dir_label = customtkinter.CTkLabel(
            text="Output Directory",
            **self.RIGHT_LABEL_KW,
        )
        self.output_dir_label.grid(
            row=12,
            column=0,
            **RIGHT_LABEL_GRID_KW,
        )

        self.output_dir_button = customtkinter.CTkButton(
            master=self.frame_right,
            text=format_directory(cli_utils.output_dir_default),
            command=self.output_dir_callback,
            **KW_BUTTON_BASE,
            **KW_BUTTON_GOOD_COLORS,
        )
        self.output_dir_button.grid(
            row=12,
            column=1,
        )

        self.output_dir_path = cli_utils.output_dir_default

    # ============ SAVE CONFIG ============

    def setup_save_config(self):

        self.frame_save_config = customtkinter.CTkFrame(
            master=self,
            fg_color="#212325",
        )
        self.frame_save_config.grid(
            row=3,
            column=0,
        )

        self.save_config_button = customtkinter.CTkButton(
            master=self.frame_save_config,
            text="Save Config",
            command=self.save_config_callback,
        )
        self.save_config_button.grid(
            row=0,
            column=0,
            pady=12,
            padx=10,
        )

        # ============ BAM FILE (FILE) ============

    # def init_bam(self):

    def bam_callback(self):
        filepaths = filedialog.askopenfilenames()
        # filepath = filedialog.askopenfilename()

        if filepaths == "":
            return

        elif len(filepaths) == 1:
            filepath = filepaths[0]
            text = path_to_text(filepath)
            self.bam_button.configure(text=text)
            self.bam_file_path = [Path(filepath)]

        else:
            # self.bam_file_string.set(str(filepaths))
            self.bam_button.configure(text="File paths set")
            self.bam_file_path = [Path(path) for path in filepaths]

        self.bam_is_okay = True
        self.bam_button.configure(**KW_BUTTON_GOOD_COLORS)

    # ============ DAMAGE MODE (ENUM) ============

    def damage_mode_collback(self, choice):

        if choice == cli_utils.DAMAGE_MODE.LCA:
            self.damage_mode_value = cli_utils.DAMAGE_MODE.LCA
        elif choice == cli_utils.DAMAGE_MODE.LOCAL:
            self.damage_mode_value = cli_utils.DAMAGE_MODE.LOCAL
        elif choice == cli_utils.DAMAGE_MODE.GLOBAL:
            self.damage_mode_value = cli_utils.DAMAGE_MODE.GLOBAL

        if choice == cli_utils.DAMAGE_MODE.LCA:
            lca_state = "normal"
            text_color = "gray90"
            slider = KW_SLIDER
            lca_rank_menu_kw = KW_OPTIONS_MENU
            switch = KW_SWITCH
            self.is_lca = True

        else:
            lca_state = "disabled"
            text_color = "gray40"
            slider = KW_SLIDER_DISABLED
            lca_rank_menu_kw = KW_OPTIONS_MENU_DISABLED
            switch = KW_SWITCH_DISABLED
            self.is_lca = False

        texts = [
            self.names_label,
            self.nodes_label,
            self.acc2tax_label,
            self.min_mapping_quality_label,
            self.min_mapping_quality_value,
            self.custom_database_label,
            self.lca_rank_label,
        ]

        for text in texts:
            text.configure(text_color=text_color)

        states = [
            self.names_button,
            self.nodes_button,
            self.acc2tax_button,
            self.min_mapping_quality_slider,
            self.custom_database_switch,
            self.lca_rank_menu,
        ]

        for state in states:
            state.configure(state=lca_state)

        self.min_mapping_quality_slider.configure(**slider)
        self.lca_rank_menu.configure(**lca_rank_menu_kw)
        self.custom_database_switch.configure(**switch)

        if choice == cli_utils.DAMAGE_MODE.LCA:
            self.names_button.configure(**self.names_button_colors)
            self.nodes_button.configure(**self.nodes_button_colors)
            self.acc2tax_button.configure(**self.acc2tax_button_colors)
        else:
            self.names_button.configure(**KW_BUTTON_GOOD_COLORS)
            self.nodes_button.configure(**KW_BUTTON_GOOD_COLORS)
            self.acc2tax_button.configure(**KW_BUTTON_GOOD_COLORS)

        self.check_similarity_scores()

    # ============ NAMES FILE (FILE) ============

    def names_callback(self):
        filepath = filedialog.askopenfilename()
        if filepath != "":
            self.names_file_path = Path(filepath)
            text = path_to_text(filepath)
            self.names_button.configure(text=text)
            self.names_button.configure(**KW_BUTTON_GOOD_COLORS)
            self.names_is_okay = True
            self.names_button_colors = KW_BUTTON_GOOD_COLORS

    # ============ NODES FILE (FILE) ============

    def nodes_callback(self):
        filepath = filedialog.askopenfilename()
        if filepath != "":
            self.nodes_file_path = Path(filepath)
            text = path_to_text(filepath)
            self.nodes_button.configure(text=text)
            self.nodes_button.configure(**KW_BUTTON_GOOD_COLORS)
            self.nodes_is_okay = True
            self.nodes_button_colors = KW_BUTTON_GOOD_COLORS

    # ============ ACC2TAX FILE (FILE) ============

    def acc2tax_callback(self):
        filepath = filedialog.askopenfilename()
        if filepath != "":
            self.acc2tax_file_path = Path(filepath)
            text = path_to_text(filepath)
            self.acc2tax_button.configure(text=text)
            self.acc2tax_button.configure(**KW_BUTTON_GOOD_COLORS)
            self.acc2tax_is_okay = True
            self.acc2tax_button_colors = KW_BUTTON_GOOD_COLORS

    #############

    def config_callback(self):
        filepath = filedialog.asksaveasfilename()
        if filepath != "":

            if not ("yaml" in filepath or "yml" in filepath):
                filepath += ".yaml"

            self.config_file_path = Path(filepath)
            text = path_to_text(filepath)
            self.config_button.configure(text=text)
            self.config_button.configure(**KW_BUTTON_GOOD_COLORS)
            self.config_is_okay = True
            self.config_button_colors = KW_BUTTON_GOOD_COLORS

    # ============ MAPPING QUALITY (INTEGER) ============

    def min_mapping_quality_slider_callback(self, value):
        self.min_mapping_quality_value.configure(text=f"= {int(value):>2d}")

    # ============ CUSTOM DATABASE (BOOL) ============

    def custom_database_callback(self):
        state = self.custom_database_switch.get()
        self.custom_database_button_title.set(str(state))
        self.custom_database_bool.set(state)

    # ============ LCA RANK (ENUM) ============

    def lca_rank_callback(self, choice):
        self.lca_rank_string.set(choice if choice != "none" else cli_utils.RANKS.none)

    # ============ MAX POSITION (INTEGER) ============

    def max_position_slider_callback(self, value):
        self.max_position_value.configure(text=f"= {int(value):>2d}")

    # ============ BAYESIAN (BOOL) ============

    def bayesian_callback(self):
        state = self.bayesian_switch.get()
        self.bayesian_button_title.set(str(state))
        self.bayesian_bool.set(state)

    # ============ FORWARD (BOOL) ============

    def forward_callback(self):
        state = self.forward_switch.get()
        self.forward_button_title.set(str(state))
        self.forward_bool.set(state)

    # ============ PARALLEL CORES (SLIDER) ============

    def parallel_samples_slider_callback(self, value):
        self.parallel_samples_value.configure(text=f"= {int(value):>2d}")

    # ============ CORES PER SAMPLE (SLIDER) ============

    def cores_per_sample_slider_callback(self, value):
        self.cores_per_sample_value.configure(text=f"= {int(value):>2d}")

    # ============ LONG NAME (ENTRY) ============

    def long_name_callback(self):
        state = self.long_name_switch.get()
        self.long_name_button_title.set(str(state))
        self.long_name_bool.set(state)

    # ============ CHECK SIMILARITY SCORE ============

    def check_similarity_scores(self):

        if self.is_lca:
            text_color = "gray90"
            self.similarity_score_label.configure(text_color=text_color)
            self.similarity_score_to.configure(text_color=text_color)
            self.similarity_score_min.configure(state="normal")
            self.similarity_score_max.configure(state="normal")

            try:
                min_score = float(self.similarity_score_min.get())
                max_score = float(self.similarity_score_max.get())
                is_float = True
            except ValueError:
                is_float = False

            if is_float and (0 <= min_score <= max_score <= 1):
                self.similarity_score_min.configure(**KW_ENTRY_GOOD_COLORS)
                self.similarity_score_max.configure(**KW_ENTRY_GOOD_COLORS)
                self.similarity_is_ok = True

            else:
                self.similarity_score_min.configure(**KW_ENTRY_BAD_COLORS)
                self.similarity_score_max.configure(**KW_ENTRY_BAD_COLORS)
                self.similarity_is_ok = False
        else:
            text_color = "gray40"
            self.similarity_score_label.configure(text_color=text_color)
            self.similarity_score_to.configure(text_color=text_color)
            self.similarity_score_min.configure(state="disabled", **KW_ENTRY_DISABLED)
            self.similarity_score_max.configure(state="disabled", **KW_ENTRY_DISABLED)

    def check_similarity_scores_background(self, interval_sec):
        # run forever
        while True:
            # block for the interval
            sleep(interval_sec)
            # perform the task
            self.check_similarity_scores()

    def start_similarity_scores_background_thread(self):
        # create and start the daemon thread
        daemon = Thread(
            target=self.check_similarity_scores_background,
            args=(0.05,),
            daemon=True,
            name="Similarity-score-checking",
        )
        daemon.start()

    # ============ CHECK MIN READS  ============

    def check_minimum_reads(self):

        try:
            min_reads = int(self.min_reads_value.get())
            is_int = True
        except ValueError:
            is_int = False

        if is_int and (0 <= min_reads):
            self.min_reads_is_ok = True
            self.min_reads_entry.configure(**KW_ENTRY_GOOD_COLORS)
        else:
            self.min_reads_entry.configure(**KW_ENTRY_BAD_COLORS)
            self.min_reads_is_ok = False

    def check_minimum_reads_background(self, interval_sec):
        # run forever
        while True:
            # block for the interval
            sleep(interval_sec)
            # perform the task
            self.check_minimum_reads()

    def start_minimum_reads_background_thread(self):
        # create and start the daemon thread
        daemon = Thread(
            target=self.check_minimum_reads_background,
            args=(0.05,),
            daemon=True,
            name="minimum-reads-checking",
        )
        daemon.start()

    # ============ OUTPUT DIR (DIRECTORY) ============

    def output_dir_callback(self):
        # get a directory path by user
        filepath = filedialog.askdirectory()
        self.output_dir_path = Path(filepath)

        text = format_directory(Path(filepath))
        self.output_dir_button.configure(text=text)

    def create_popup_window(self, text):

        window_popup = customtkinter.CTkToplevel(self)
        window_popup.title("metaDMG - Error")

        width = 365
        height = 110
        x, y = self.get_center_coordinates(width, height)

        window_popup.geometry(f"{width}x{height}+{x}+{y}")

        label = customtkinter.CTkLabel(
            window_popup,
            text=f"Error occurred in config creation. \nPlease {text}.",
        )

        label.grid(
            row=0,
            column=0,
            padx=80,
            pady=12,
        )

        def close_popup_callback():
            window_popup.destroy()

        button = customtkinter.CTkButton(
            master=window_popup,
            text="Close",
            command=close_popup_callback,
        )
        button.grid(
            row=1,
            column=0,
            padx=80,
            pady=12,
        )

    # ============ PRINT ============

    def config_is_good(self):

        self.check_similarity_scores()
        self.check_minimum_reads()

        if not self.bam_is_okay:
            self.create_popup_window("fix BAM file")
            return False

        if self.is_lca and (not self.names_is_okay):
            self.create_popup_window("fix names file")
            return False

        if self.is_lca and (not self.nodes_is_okay):
            self.create_popup_window("fix nodes file")
            return False

        if self.is_lca and (not self.acc2tax_is_okay):
            self.create_popup_window("fix acc2tax file")
            return False

        if self.is_lca and (not self.similarity_is_ok):
            self.create_popup_window("fix similarity score")
            return False

        if not self.min_reads_is_ok:
            self.create_popup_window("fix minimum number of reads")
            return False

        if not self.config_is_okay:
            self.create_popup_window("fix config file name")
            return False

        return True

    def get_config(self):

        if not self.config_is_good():
            return None

        from metaDMG import __version__

        config = cli_utils.get_config_dict(
            samples=self.bam_file_path,
            damage_mode=self.damage_mode_value,
            #
            names=self.names_file_path,
            nodes=self.nodes_file_path,
            acc2tax=self.acc2tax_file_path,
            min_similarity_score=float(self.similarity_score_min.get()),
            max_similarity_score=float(self.similarity_score_max.get()),
            min_edit_dist=None,
            max_edit_dist=None,
            min_mapping_quality=int(self.min_mapping_quality_slider.get()),
            custom_database=self.custom_database_bool.get(),
            lca_rank=self.lca_rank_string.get(),
            #
            metaDMG_cpp="./metaDMG-cpp",
            max_position=int(self.max_position_slider.get()),
            min_reads=int(self.min_reads_value.get()),
            weight_type=1,
            forward_only=self.forward_bool.get(),
            bayesian=self.bayesian_bool.get(),
            output_dir=self.output_dir_path,
            parallel_samples=int(self.parallel_samples_slider.get()),
            cores_per_sample=int(self.cores_per_sample_slider.get()),
            config_file=self.config_file_path,
            sample_prefix=self.prefix_entry.get(),
            sample_suffix=self.suffix_entry.get(),
            long_name=self.long_name_bool.get(),
            __version__=__version__,
        )

        return config

    def save_config_file(self, config, overwrite_config=False):
        if self.verbose:
            print("")
            print("Config file to save:")
            print(config)
        cli_utils.save_config_file(
            config=config,
            config_file=self.config_file_path,
            overwrite_config=overwrite_config,
            verbose=self.verbose,
        )

    def make_overwrite_window(self, config):

        window_overwrite = customtkinter.CTkToplevel(self)
        window_overwrite.title("metaDMG - Computing")

        width = 365
        height = 110
        x, y = self.get_center_coordinates(width, height)

        window_overwrite.geometry(f"{width}x{height}+{x}+{y}")

        label = customtkinter.CTkLabel(
            window_overwrite,
            text="Config file already exists. Do you want to overwrite it?",
        )

        label.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=20,
            pady=12,
        )

        def no_overwrite_callback():
            window_overwrite.destroy()

        def overwrite_callback():
            self.save_config_file(config=config, overwrite_config=True)
            window_overwrite.destroy()

        button_yes = customtkinter.CTkButton(
            master=window_overwrite,
            text="Yes",
            command=overwrite_callback,
        )
        button_yes.grid(
            row=1,
            column=0,
            padx=20,
            pady=12,
        )

        button_no = customtkinter.CTkButton(
            master=window_overwrite,
            text="No",
            command=no_overwrite_callback,
        )
        button_no.grid(
            row=1,
            column=1,
            padx=20,
            pady=12,
        )

    def save_config_callback(self):

        config = self.get_config()
        if config is None:
            return

        if self.config_file_path.exists():
            self.make_overwrite_window(config)
        else:
            self.save_config_file(config)

    # ============ OTHER ============

    def on_closing(self, event=0):
        self.destroy()

    def get_center_coordinates(self, width, height):
        # get screen width and height
        ws = self.winfo_screenwidth()  # width of the screen
        hs = self.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (width / 2)
        y = (hs / 2) - (height / 2)

        return int(x), int(y)


if __name__ == "__main__":
    gui = Gui(verbose=True)
    gui.mainloop()
