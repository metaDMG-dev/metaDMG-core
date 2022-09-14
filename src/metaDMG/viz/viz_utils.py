#%%
import webbrowser
from collections import namedtuple
from distutils.spawn import find_executable
from importlib import resources
from pathlib import Path
from threading import Timer

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from dash import dcc
from dash.exceptions import PreventUpdate
from PIL import ImageColor


#%%


def has_latex():
    if find_executable("latex"):
        return True
    else:
        return False


def mpl_style_path(name):
    with resources.path("metaDMG.viz.mpl_styles", f"{name}.mplstyle") as p:
        mpl_style = p
    return mpl_style


def get_mpl_styles():

    style = [
        mpl_style_path("science"),
        mpl_style_path("scatter"),
        mpl_style_path("ieee"),
    ]

    if not has_latex():
        style.append(mpl_style_path("no-latex"))

    return style


#%%


def set_custom_theme():

    pio.templates["custom_template"] = go.layout.Template(
        layout=go.Layout(
            font_size=16,
            title_font_size=30,
            legend=dict(
                title_font_size=20,
                font_size=16,
                itemsizing="constant",
                itemclick=False,
                itemdoubleclick=False,
            ),
            hoverlabel_font_family="Monaco, Lucida Console, Courier, monospace",
            dragmode="zoom",
        )
    )

    # pio.templates.default = "plotly_white"
    pio.templates.default = "simple_white+custom_template"


#%%


def human_format(num, digits=3, mode="eng"):
    num = float(f"{num:.{digits}g}")
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0

    if mode == "eng" or mode == "SI":
        translate = ["", "k", "M", "G", "T"]
    elif mode == "scientific" or mode == "latex":
        translate = ["", r"\cdot 10^3", r"\cdot 10^6", r"\cdot 10^9", r"\cdot 10^12"]
    else:
        raise AssertionError(f"'mode' has to be 'eng' or 'scientific', not {mode}.")

    return "{}{}".format(
        "{:f}".format(num).rstrip("0").rstrip("."), translate[magnitude]
    )


#%%


def replace_nans(df):
    # return df
    return df.replace(np.nan, "NAN")


#%%


def tax_path_to_string(tax_path):
    if "NO TAX" in tax_path:
        return tax_path

    string = ""
    for line in tax_path.split("\t"):
        name = line.split(":")[1]
        string += f"{name} : "
    return string[:-3]


#%%


def is_log_transform_column(column):
    log_transform_columns = ["N_reads", "N_alignments", "k_sum_", "N_sum_", "phi"]
    return any([log_col in column for log_col in log_transform_columns])


def log_transform_slider(x):
    return np.where(x < 0, 0, 10 ** np.clip(x, 0, a_max=None))


#%%


def open_browser(port: int = 8050):
    webbrowser.open(f"http://0.0.0.0:{port}")


def open_browser_in_background(port: int = 8050):
    Timer(3, open_browser, [port]).start()
    # Timer(3, open_browser, [port]).start()


#%%


def add_tax_str(df, include_rank=True):
    if include_rank:
        df["tax_str"] = (
            df["tax_name"] + " : " + df["tax_rank"] + " : " + df["tax_id"].astype(str)
        )
    else:
        df["tax_str"] = df["tax_name"] + ": " + df["tax_id"].astype(str)


#%%


def hex_to_rgb(hex_string, opacity=1):
    rgb = ImageColor.getcolor(hex_string, "RGB")
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {opacity})"


def get_samples_each(all_samples):
    first_letters = {s[0] for s in all_samples}
    values = []
    for first_letter in first_letters:
        for sample in all_samples:
            if sample[0] == first_letter:
                values.append(sample)
                break
    return values


def get_dropdown_file_selection(viz_results, id, samples_to_show="all"):

    special_samples = ["Select all", "Default selection"]
    N_special_samples = len(special_samples)
    all_samples = special_samples + viz_results.samples

    if samples_to_show is None:
        values = all_samples

    elif isinstance(samples_to_show, int):
        values = all_samples[: samples_to_show + N_special_samples]

    elif isinstance(samples_to_show, str):

        if samples_to_show == "all":
            values = all_samples

        elif samples_to_show == "each":
            values = get_samples_each(viz_results.samples)

    values = list(sorted(values))

    dropdown_file_selection = dcc.Dropdown(
        id=id,
        options=[{"label": sample, "value": sample} for sample in all_samples],
        value=values,
        multi=True,
        placeholder="Select files to plot",
    )

    return dropdown_file_selection


#%%


def _insert_mark_values(mark_values):
    # https://github.com/plotly/dash-core-components/issues/159
    # work-around bug reported in https://github.com/plotly/dash-core-components/issues/159
    # if mark keys happen to fall on integers, cast them to int

    mark_labels = {}
    for mark_val in mark_values:
        # close enough to an int for my use case
        if abs(mark_val - round(mark_val)) < 1e-3:
            mark_val = int(mark_val)
        mark_labels[mark_val] = human_format(mark_val)
    return mark_labels


def get_range_slider_keywords(viz_results, column="N_reads", N_steps=100):

    no_min = "Min"
    no_max = "Max"

    df = viz_results.df

    if is_log_transform_column(column):

        x = df[column]

        range_log = np.log10(x[x > 0])
        range_min = np.floor(range_log.min())
        range_max = np.ceil(range_log.max())
        marks_steps = np.arange(range_min, range_max + 1)

        # if x contains 0-values
        if (x <= 0).sum() != 0:
            range_min = -1
            marks_steps = np.insert(marks_steps, 0, -1)

        if len(marks_steps) > 6:
            marks_steps = (
                [marks_steps[0]] + [x for x in marks_steps[1:-1:2]] + [marks_steps[-1]]
            )

        f = lambda x: human_format(log_transform_slider(x))
        marks = {int(i): f"{f(i)}" for i in marks_steps}

        marks[marks_steps[0]] = {"label": no_min, "style": {"color": "#a3ada9"}}
        marks[marks_steps[-1]] = {"label": no_max, "style": {"color": "#a3ada9"}}

    elif column in ["D_max", "q", "A", "c"] or column in [
        "Bayesian_D_max",
        "Bayesian_q",
        "Bayesian_A",
        "Bayesian_c",
        "Bayesian_D_max_CI_low",
        "Bayesian_D_max_CI_high",
    ]:
        range_min = 0.0
        range_max = 1.0
        marks = {
            0.25: "0.25",
            0.5: "0.5",
            0.75: "0.75",
        }
        marks[0] = {"label": no_min, "style": {"color": "#a3ada9"}}
        marks[1] = {"label": no_max, "style": {"color": "#a3ada9"}}

    else:

        array = df[column]
        array = array[np.isfinite(array) & array.notnull()]

        range_min = np.min(array)
        range_max = np.max(array)

        if range_max - range_min > 1:
            range_min = np.floor(range_min)
            range_max = np.ceil(range_max)
            mark_values = np.linspace(range_min, range_max, 5, dtype=int)
            marks = _insert_mark_values(mark_values[1:-1])

        else:
            decimals = abs(int(np.floor(np.log10(range_max - range_min))))
            range_min = np.around(range_min, decimals=decimals)
            range_max = np.around(range_max, decimals=decimals)

            mark_values = np.linspace(range_min, range_max, 5)
            marks = {float(val): str(val) for val in mark_values[1:-1]}

        marks[int(mark_values[0])] = {"label": no_min, "style": {"color": "#a3ada9"}}
        marks[int(mark_values[-1])] = {
            "label": no_max,
            "style": {"color": "#a3ada9"},
        }

    step = (range_max - range_min) / N_steps

    return dict(
        min=range_min,
        max=range_max,
        step=step,
        marks=marks,
        value=[range_min, range_max],
        allowCross=False,
        updatemode="mouseup",
        included=True,
        # tooltip=dict(
        #     always_visible=False,
        #     placement="bottom",
        # ),
    )


#%%


def get_sample_tax_id_from_click_data(viz_results, click_data):
    try:
        sample = viz_results.parse_click_data(click_data, column="sample")
        tax_id = viz_results.parse_click_data(click_data, column="tax_id")
    except KeyError:
        raise PreventUpdate
    return sample, tax_id


#%%


def append_to_list_if_exists(d, key, value):
    if key in d:
        d[key].append(value)
    else:
        d[key] = [value]
    return d


#%%
def get_max_position_from_group(group):
    max_position = group.dropna()["|x|"].max()
    return max_position


#%%


def key_is_in_list_case_insensitive(lst, key):
    return any([key.lower() in s.lower() for s in lst])


#%%


def get_configurations(
    sidebar_left_width=30,  # in %
    sidebar_right_width=20,  # in %
    content_main_margin=1,  # in %
):

    style_sidebar_base = {
        "position": "fixed",
        "top": 62.5,
        "bottom": 0,
        "height": "100%",
        "z-index": 1,
        "overflow-x": "hidden",
        "transition": "all 0.5s",
        "padding": "0.5rem 1rem",
        # "background-color": "#f8f9fa",
    }

    # the style arguments for the sidebar_right. We use position:fixed and a fixed width
    style_sidebar_left_shown = {
        **style_sidebar_base,
        "left": "0%",
        "width": f"{sidebar_left_width}%",
    }

    style_sidebar_left_hidden = {
        **style_sidebar_base,
        "left": f"-{sidebar_left_width}%",
        "width": f"{sidebar_left_width}%",
    }

    # the style arguments for the sidebar_right. We use position:fixed and a fixed width
    style_sidebar_right_shown = {
        **style_sidebar_base,
        "left": f"{100-sidebar_right_width}%",
        "width": f"{sidebar_right_width}%",
    }

    style_sidebar_right_hidden = {
        **style_sidebar_base,
        "left": "100%",
        "width": f"{sidebar_right_width}%",
    }

    style_main_base = {
        "transition": "margin .5s",
        "padding": "2rem 1rem",
        # "background-color": "#f8f9fa",
    }

    style_main_both_sidebars = {
        **style_main_base,
        "margin-left": f"{sidebar_left_width+content_main_margin}%",
        "margin-right": f"{sidebar_right_width+content_main_margin}%",
    }

    style_main_no_sidebars = {
        **style_main_base,
        "margin-left": f"{content_main_margin}%",
        "margin-right": f"{content_main_margin}%",
    }

    style_main_filter_sidebar = {
        **style_main_base,
        "margin-left": f"{sidebar_left_width+content_main_margin}%",
        "margin-right": f"{content_main_margin}%",
    }

    style_main_plot_sidebar = {
        **style_main_base,
        "margin-left": f"{content_main_margin}%",
        "margin-right": f"{sidebar_right_width+content_main_margin}%",
    }

    configuration = namedtuple(
        "configuration",
        [
            "style_content_main",
            "style_sidebar_left",
            "style_sidebar_right",
            "state_sidebar_left",
            "state_sidebar_right",
        ],
    )

    d_sidebar_left = {
        "shown": {
            "style_sidebar_left": style_sidebar_left_shown,
            "state_sidebar_left": "SHOWN",
        },
        "hidden": {
            "style_sidebar_left": style_sidebar_left_hidden,
            "state_sidebar_left": "HIDDEN",
        },
    }

    d_sidebar_right = {
        "shown": {
            "style_sidebar_right": style_sidebar_right_shown,
            "state_sidebar_right": "SHOWN",
        },
        "hidden": {
            "style_sidebar_right": style_sidebar_right_hidden,
            "state_sidebar_right": "HIDDEN",
        },
    }

    configurations = {
        1: configuration(
            style_content_main=style_main_no_sidebars,
            **d_sidebar_left["hidden"],
            **d_sidebar_right["hidden"],
        ),
        2: configuration(
            style_content_main=style_main_filter_sidebar,
            **d_sidebar_left["shown"],
            **d_sidebar_right["hidden"],
        ),
        3: configuration(
            style_content_main=style_main_plot_sidebar,
            **d_sidebar_left["hidden"],
            **d_sidebar_right["shown"],
        ),
        4: configuration(
            style_content_main=style_main_both_sidebars,
            **d_sidebar_left["shown"],
            **d_sidebar_right["shown"],
        ),
    }

    return configurations


#%%


def toggle_plot(
    configurations,
    current_state_sidebar_left,
    current_state_sidebar_right,
):

    # going from (4) -> (2)
    if current_state_sidebar_left == "SHOWN" and current_state_sidebar_right == "SHOWN":
        return configurations[2]

    # going from (2) -> (4)
    elif (
        current_state_sidebar_left == "SHOWN"
        and current_state_sidebar_right == "HIDDEN"
    ):
        return configurations[4]

    # going from (3) -> (1)
    elif (
        current_state_sidebar_left == "HIDDEN"
        and current_state_sidebar_right == "SHOWN"
    ):
        return configurations[1]

    # going from (1) -> (3)
    elif (
        current_state_sidebar_left == "HIDDEN"
        and current_state_sidebar_right == "HIDDEN"
    ):
        return configurations[3]


#%%


def toggle_filter(
    configurations,
    current_state_sidebar_left,
    current_state_sidebar_right,
):

    # going from (4) -> (3)
    if current_state_sidebar_left == "SHOWN" and current_state_sidebar_right == "SHOWN":
        return configurations[3]

    # going from (2) -> (1)
    elif (
        current_state_sidebar_left == "SHOWN"
        and current_state_sidebar_right == "HIDDEN"
    ):
        return configurations[1]

    # going from (3) -> (4)
    elif (
        current_state_sidebar_left == "HIDDEN"
        and current_state_sidebar_right == "SHOWN"
    ):
        return configurations[4]

    # going from (1) -> (2)
    elif (
        current_state_sidebar_left == "HIDDEN"
        and current_state_sidebar_right == "HIDDEN"
    ):
        return configurations[2]


def get_button_id(ctx):
    "Get button clicked"
    if not ctx.triggered:
        button_id = None
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return button_id


def get_graph_kwargs():
    graph_kwargs = dict(
        config={
            "displaylogo": False,
            "doubleClick": "reset",
            "showTips": True,
            "modeBarButtonsToRemove": [
                "select2d",
                "lasso2d",
                "autoScale2d",
                "hoverClosestCartesian",
                "hoverCompareCartesian",
                "toggleSpikelines",
            ],
        },
        # # https://css-tricks.com/fun-viewport-units/
        style={"width": "100%", "height": "65vh"},
        mathjax=True,
    )
    return graph_kwargs


def get_graph_kwargs_no_buttons():
    graph_kwargs_no_buttons = dict(
        config={
            "displaylogo": False,
            "doubleClick": "reset",
            "showTips": True,
            "modeBarButtonsToRemove": [
                "zoom2d",
                "pan2d",
                "select2d",
                "lasso2d",
                "zoomIn2d",
                "zoomOut2d",
                "autoScale2d",
                "resetScale2d",
                "hoverClosestCartesian",
                "hoverCompareCartesian",
                "toggleSpikelines",
                "toImage",
            ],
        },
        mathjax=True,
    )
    return graph_kwargs_no_buttons


def get_d_columns_latex(viz_results):
    d_columns_latex = {
        "Bayesian_z": r"$z$",
        "Bayesian_D_max": r"$D_\text{max}$",
        #
        "lambda_LR": r"$\lambda_\text{LR} \text{(MAP)}$",
        "D_max": r"$D_\text{max} \text{(MAP)}$",
        #
        "asymmetry": r"$\text{asymmetry} \text{(MAP)}$",
        "Bayesian_D_max_significance": r"$D_\text{max} \,\, \text{sig.}$",
        "D_max_significance": r"$D_\text{max} \,\, \text{sig.} \,\, \text{(MAP)}$",
        "Bayesian_D_max_CI_low": r"$D_\text{max} \,\, \text{CI. low}$",
        "Bayesian_D_max_CI_high": r"$D_\text{max} \,\, \text{CI. high}$",
        "D_max_CI_low": r"$D_\text{max} \,\, \text{CI. low} \,\, \text{(MAP)}$",
        "D_max_CI_high": r"$D_\text{max} \,\, \text{CI. high} \,\, \text{(MAP)}$",
        #
        "Bayesian_q": r"$q$",
        "q": r"$q \text{(MAP)}$",
        "Bayesian_phi": r"$\phi$",
        "phi": r"$\phi \text{(MAP)}$",
        "Bayesian_A": r"$A$",
        "A": r"$A \text{(MAP)}$",
        "Bayesian_c": r"$c$",
        "c": r"$c \text{(MAP)}$",
        "Bayesian_rho_Ac": r"$\rho_{A, c}$",
        "rho_Ac": r"$\rho_{A, c} \text{(MAP)}$",
        "Bayesian_rho_Ac_abs": r"$|\rho_{A, c}|$",
        "rho_Ac_abs": r"$|\rho_{A, c}| \text{(MAP)}$",
        #
        "N_reads": r"$N_\text{reads}$",
        "N_alignments": r"$N_\text{alignments}$",
        "k_sum_total": r"$\sum_i k_i$",
        "N_sum_total": r"$\sum_i N_i$",
        "N_min": r"$\text{min} N_i$",
        #
        "mean_L": r"$\text{mean readlength}$",
        "std_L": r"$\text{std readlength}$",
        "mean_GC": r"$\text{mean GC}$",
        "std_GC": r"$\text{std GC}$",
        #
        # "LR_P": r"$\text{P}_\lambda \text{(MAP)}$ ",
        # "LR_z": r"$z_\lambda \text{(MAP)}$",
        #
        "Bayesian_D_max_std": r"$\sigma_{D_\text{max}}$",
        "D_max_std": r"$\sigma_{D_\text{max}} \text{(MAP)}$",
        "q_std": r"$\sigma_q \text{(MAP)}$",
        "phi_std": r"$\sigma_\phi \text{(MAP)}$",
        "A_std": r"$\sigma_A \text{(MAP)}$",
        "c_std": r"$\sigma_c \text{(MAP)}$",
        #
        # "Bayesian_variance_scaling": r"$\text{variance} \,\, \text{scaling}$",
        # "variance_scaling": r"$\text{variance} \,\, \text{scaling} \,\, \text{(MAP)}$",
        #
        # "log_lambda_LR": r"$\log_{10}(1+\lambda_\text{LR})$",
        # "log_phi": r"$\log_{10}(1+\phi)$",
        # "log_N_reads": r"$\log_{10}(1+N_\text{reads})$",
        # "log_N_alignments": r"$\log_{10}(1+N_\text{alignments})$",
        # "log_k_sum_total": r"$\log_{10}(1+\sum_i k_i)$",
        # "log_N_sum_total": r"$\log_{10}(1+\sum_i N_i)$",
        #
        "forward_lambda_LR": r"$ \lambda_\text{LR} \,\, \text{(forward)}$",
        "forward_D_max": r"$ D_\text{max} \,\, \text{(forward)}$",
        "forward_q": r"$ q \,\, \text{(forward)}$",
        "forward_phi": r"$ \phi \,\, \text{(forward)}$",
        "forward_A": r"$ A \,\, \text{(forward)}$",
        "forward_c": r"$ c \,\, \text{(forward)}$",
        "forward_rho_Ac": r"$ \rho_{A, c} \,\, \text{(forward)}$",
        "forward_LR_P": r"$ \text{P}_\lambda \,\, \text{(forward)}$",
        "forward_LR_z": r"$ z_\lambda \,\, \text{(forward)}$",
        #
        "forward_D_max_std": r"$ \sigma_{D_\text{max}} \,\, \text{(forward)}$",
        "forward_q_std": r"$ \sigma_q \,\, \text{(forward)}$",
        "forward_phi_std": r"$ \sigma_\phi \,\, \text{(forward)}$",
        "forward_A_std": r"$ \sigma_A \,\, \text{(forward)}$",
        "forward_c_std": r"$ \sigma_c \,\, \text{(forward)}$",
        #
        "k_sum_forward": r"$\sum_i k_i \,\, \text{(forward)}$",
        "N_x=1_forward": r"$N_{x=1} \,\, \text{(forward)}$",
        "N_sum_forward": r"$\sum_i N_i \,\, \text{(forward)}$",
        #
        "reverse_lambda_LR": r"$ \lambda_\text{LR} \,\, \text{(reverse)}$",
        "reverse_D_max": r"$ D_\text{max} \,\, \text{(reverse)}$",
        "reverse_q": r"$ q \,\, \text{(reverse)}$",
        "reverse_phi": r"$ \phi \,\, \text{(reverse)}$",
        "reverse_A": r"$ A \,\, \text{(reverse)}$",
        "reverse_c": r"$ c \,\, \text{(reverse)}$",
        "reverse_rho_Ac": r"$ \rho_{A, c} \,\, \text{(reverse)}$",
        "reverse_LR_P": r"$ \text{P}_\lambda \,\, \text{(reverse)}$",
        "reverse_LR_z": r"$ z_\lambda \,\, \text{(reverse)}$",
        #
        "reverse_D_max_std": r"$ \sigma_{D_\text{max}} \,\, \text{(reverse)}$",
        "reverse_q_std": r"$ \sigma_q \,\, \text{(reverse)}$",
        "reverse_phi_std": r"$ \sigma_\phi \,\, \text{(reverse)}$",
        "reverse_A_std": r"$ \sigma_A \,\, \text{(reverse)}$",
        "reverse_c_std": r"$ \sigma_c \,\, \text{(reverse)}$",
        #
        "k_sum_reverse": r"$\sum_i k_i \,\, \text{(reverse)}$",
        "N_x=1_reverse": r"$N_{x=1} \,\, \text{(reverse)}$",
        "N_sum_reverse": r"$\sum_i N_i \,\, \text{(reverse)}$",
        #
        #
        # "LR_All": r"$\text{LR All}$",
        # "LR_ForRev": r"$\text{LR ForRev}$",
        # "LR_ForRev_All": r"$\text{LR ForRev All}$",
        # #
        # "chi2_all": r"$\chi^2 \text{all}$",
        # "chi2_ForRev": r"$\chi^2 \text{ForRev}$",
    }

    keys_to_remove = [
        key for key in d_columns_latex.keys() if not key in viz_results.df.columns
    ]
    [d_columns_latex.pop(key) for key in keys_to_remove]

    columns = list(d_columns_latex.keys())
    columns_no_log = [col for col in columns if not col.startswith("log_")]

    return d_columns_latex, columns, columns_no_log
