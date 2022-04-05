import itertools

import dash_bootstrap_components as dbc
import numpy as np
from dash import dcc, html

from metaDMG.viz import figures, viz_utils


#%%


def get_navbar():

    navbar = dbc.NavbarSimple(
        [
            dbc.Button(
                "Filters",
                outline=True,
                color="light",
                className="mr-1",
                id="sidebar_left_toggle_btn",
            ),
            dbc.Button(
                "Styling",
                outline=True,
                color="light",
                className="mr-1",
                id="navbar_btn_toggle_styling",
            ),
            dbc.Button(
                "Raw data",
                outline=False,
                color="light",
                className="mr-1",
                id="sidebar_right_toggle_btn",
            ),
            dbc.Button(
                "",
                color="link",
                outline=False,
                disabled=True,
                id="invisible_button",
            ),
            html.Div(dcc.Store(id="memory-store-csv")),
            html.Div(dcc.Store(id="memory-store-pdf")),
            dbc.Button(
                "Export CSV",
                outline=True,
                color="light",
                className="mr-1",
                id="navbar_btn_export_csv",
            ),
            dcc.Download(id="export_csv"),
            dbc.Button(
                "Export PDF",
                outline=True,
                color="light",
                className="mr-1",
                id="navbar_btn_export_pdf",
            ),
            dcc.Download(id="export_pdf"),
        ],
        brand="metaDMG",
        brand_href="https://github.com/metaDMG/metaDMG",
        color="dark",
        dark=True,
        fluid=True,
    )

    return navbar


#%%


def get_content_main(viz_results, start_configuration):

    _, columns, columns_no_log = viz_utils.get_d_columns_latex(viz_results)

    dropdown_x_axis = dcc.Dropdown(
        id="xaxis_column",
        options=[{"label": i, "value": i} for i in columns],
        value="Bayesian_z" if viz_results.Bayesian else "lambda_LR",
    )

    dropdown_y_axis = dcc.Dropdown(
        id="yaxis_column",
        options=[{"label": i, "value": i} for i in columns],
        value="Bayesian_D_max" if viz_results.Bayesian else "D_max",
    )

    XY_axis_dropdowns = [
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(html.Center("X-axis: ")),
                        dbc.Col(dropdown_x_axis, width=12),
                    ]
                ),
            ],
            width=6,
        ),
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(html.Center("Y-axis: ")),
                        dbc.Col(dropdown_y_axis, width=12),
                    ]
                ),
            ],
            width=6,
        ),
    ]

    marker_transformation_function = dcc.Dropdown(
        id="marker_transformation_function",
        options=[
            {"label": "Constant", "value": "constant"},
            {"label": "Linear", "value": "linear"},
            {"label": "Sqrt", "value": "sqrt"},
            {"label": "Log", "value": "log10"},
        ],
        value="sqrt",
        searchable=False,
        clearable=False,
    )

    marker_transformation_variable = dcc.Dropdown(
        id="marker_transformation_variable",
        options=[{"label": col, "value": col} for col in columns_no_log],
        value="N_reads",
        searchable=True,
        clearable=False,
    )

    marker_transformation_slider = dcc.Slider(
        id="marker_transformation_slider",
        min=1,
        max=60,
        step=1,
        value=30,
        marks={mark: str(mark) for mark in [1, 10, 20, 30, 40, 50, 60]},
    )

    marker_transformations = [
        dbc.Col(
            dbc.Row(
                [
                    dbc.Col(html.Center("Variable:")),
                    dbc.Col(marker_transformation_variable, width=12),
                ],
            ),
            width=4,
        ),
        dbc.Col(
            dbc.Row(
                [
                    dbc.Col(html.Center("Function:")),
                    dbc.Col(marker_transformation_function, width=12),
                ],
            ),
            width=2,
        ),
        dbc.Col(
            dbc.Row(
                [
                    dbc.Col(html.Center("Scale:")),
                    dbc.Col(marker_transformation_slider, width=12),
                ],
            ),
            width=6,
        ),
    ]

    content_main = html.Div(
        html.Div(
            [
                dcc.Graph(id="main_graph", **viz_utils.get_graph_kwargs()),
                dbc.Collapse(
                    [
                        dbc.Row(dbc.Col(html.Hr())),
                        dbc.Row(
                            dbc.Col(html.Center("Axis variables", className="lead"))
                        ),
                        dbc.Row(
                            XY_axis_dropdowns,
                            # no_gutters=True,
                            className="g-0",
                        ),
                        dbc.Row(dbc.Col(html.Hr())),
                        dbc.Row(dbc.Col(html.Center("Marker size", className="lead"))),
                        dbc.Row(
                            marker_transformations,
                            # no_gutters=True,
                            className="g-0",
                        ),
                    ],
                    id="navbar_collapsed_toggle_styling",
                    is_open=False,
                ),
            ]
        ),
        id="content_main",
        style=start_configuration.style_content_main,
    )

    return content_main


#%%


#%%


def get_sidebar_left(viz_results, start_configuration):

    d_columns_latex, columns, columns_no_log = viz_utils.get_d_columns_latex(
        viz_results
    )

    filter_dropdown_file = dbc.Form(
        viz_utils.get_dropdown_file_selection(
            viz_results=viz_results,
            id="sidebar_left_dropdown_samples",
            samples_to_show="each",  # one for each first letter in sample
        ),
    )

    filters_collapse_files = html.Div(
        [
            html.Div(
                dbc.Button(
                    "Samples",
                    id="sidebar_left_samples_btn",
                    color="secondary",
                    outline=True,
                    size="lg",
                ),
                className="d-grid gap-2",
            ),
            dbc.Collapse(
                filter_dropdown_file,
                id="sidebar_left_samples_collapsed",
                is_open=False,
            ),
        ]
    )

    filter_tax_id = dbc.Row(
        [
            dbc.Col(html.Br(), width=12),
            dbc.Col(html.H6("Specific taxas:"), width=12),
            dbc.Col(
                dbc.Form(
                    dcc.Dropdown(
                        id="sidebar_left_taxa_input_specific",
                        options=[
                            {"label": tax, "value": tax}
                            for tax in itertools.chain.from_iterable(
                                [
                                    viz_results.all_tax_ranks,
                                    viz_results.all_tax_names,
                                    viz_results.all_tax_ids,
                                ]
                            )
                        ],
                        clearable=True,
                        multi=True,
                        placeholder="Select taxas...",
                    ),
                ),
                width=12,
            ),
            dbc.Col(html.Br(), width=12),
            dbc.Col(html.H6("Taxonomic path contains:"), width=12),
            dbc.Col(
                dbc.Form(
                    dbc.Input(
                        id="sidebar_left_taxa_input_path_contains",
                        placeholder="Input goes here...",
                        type="text",
                        autoComplete="off",
                        debounce=True,  # activates after enter
                    ),
                ),
                width=12,
            ),
            dbc.Col(
                dbc.Form(
                    html.Div(
                        dbc.Button(
                            "Update",
                            id="tax_id_plot_button",
                            color="light",
                        ),
                        className="d-grid gap-2",
                    ),
                ),
            ),
        ],
        justify="between",
        className="form-row"
        # form=True,
    )

    filters_collapse_tax_id = html.Div(
        [
            html.Div(
                dbc.Button(
                    "Taxa",
                    id="sidebar_left_taxanomics_btn",
                    color="secondary",
                    outline=True,
                    size="lg",
                ),
                className="d-grid gap-2",
            ),
            dbc.Collapse(
                filter_tax_id,
                id="sidebar_left_taxanomics_collapsed",
                is_open=False,
            ),
        ]
    )

    #%%

    # default sliders (with default values)

    slider_N_reads = make_new_slider(
        viz_results,
        column="N_reads",
        id_type="dbc",
        min_value=np.log10(100),
    )
    slider_k_sum_total = make_new_slider(
        viz_results,
        column="k_sum_total",
        id_type="dbc",
        min_value=np.log10(10),
    )

    slider_phi_column = "Bayesian_phi" if viz_results.Bayesian else "phi"
    slider_phi = make_new_slider(
        viz_results,
        column=slider_phi_column,
        id_type="dbc",
        min_value=np.log10(100),
    )

    filters_collapse_ranges = html.Div(
        [
            html.Div(
                dbc.Button(
                    "Fits",
                    id="sidebar_left_results_btn",
                    color="secondary",
                    outline=True,
                    size="lg",
                ),
                className="d-grid gap-2",
            ),
            dbc.Collapse(
                [
                    html.Br(),
                    dbc.Col(
                        html.H6("Fit results:"),
                        width=12,
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="sidebar_left_results",
                            options=[
                                {"label": sample, "value": sample}
                                for sample in columns_no_log
                            ],
                            value=[
                                "N_reads",
                                "k_sum_total",
                                slider_phi_column,
                            ],
                            multi=True,
                            placeholder="Select a variable ...",
                            optionHeight=30,
                        ),
                        width=12,
                    ),
                    dbc.Col(
                        id="sidebar_left_results_container",
                        # children=[],
                        children=[
                            slider_N_reads,
                            slider_k_sum_total,
                            slider_phi,
                        ],
                        width=12,
                    ),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                ],
                id="sidebar_left_results_collapsed",
                is_open=False,
            ),
        ]
    )

    sidebar_left = html.Div(
        [
            html.H2("Filters", className="display-4"),
            dbc.Form(
                [
                    filters_collapse_files,
                    html.Hr(),
                    filters_collapse_tax_id,
                    html.Hr(),
                    filters_collapse_ranges,
                ]
            ),
        ],
        id="sidebar_left",
        style=start_configuration.style_sidebar_left,
    )

    return sidebar_left


#%%


def get_sidebar_right(start_configuration):

    sidebar_right_results = html.Div(
        [
            html.Div(
                dbc.Button(
                    "Fit results",
                    id="sidebar_right_btn_toggle_results",
                    color="secondary",
                    outline=True,
                    size="lg",
                ),
                className="d-grid gap-2",
            ),
            dbc.Collapse(
                html.Div(
                    "sidebar_right_datatable_results",
                    id="sidebar_right_datatable_results",
                ),
                id="sidebar_right_collapsed_toggle_results",
                is_open=False,
            ),
        ]
    )

    sidebar_right_collapsed_toggle_combined_graph = dbc.Form(
        dcc.Graph(
            figure=figures.create_empty_figure(),
            id="sidebar_right_graph_combined",
            **viz_utils.get_graph_kwargs_no_buttons(),
        ),
    )

    sidebar_right_collapsed_toggle_combined = html.Div(
        [
            html.Div(
                dbc.Button(
                    "Combined",
                    id="sidebar_right_btn_toggle_combined",
                    color="secondary",
                    outline=False,
                    size="lg",
                ),
                className="d-grid gap-2",
            ),
            dbc.Collapse(
                sidebar_right_collapsed_toggle_combined_graph,
                id="sidebar_right_collapsed_toggle_combined",
                is_open=True,
            ),
        ]
    )

    sidebar_right_collapsed_toggle_forward_reverse_graph = dbc.Form(
        [
            dcc.Graph(
                figure=figures.create_empty_figure(),
                id="sidebar_right_graph_forward",
                style={"height": "20vh"},
                **viz_utils.get_graph_kwargs_no_buttons(),
            ),
            dcc.Graph(
                figure=figures.create_empty_figure(),
                id="sidebar_right_graph_reverse",
                style={"height": "20vh"},
                **viz_utils.get_graph_kwargs_no_buttons(),
            ),
        ]
    )

    sidebar_right_collapsed_toggle_forward_reverse = html.Div(
        [
            html.Div(
                dbc.Button(
                    "Forward / Reverse",
                    id="sidebar_right_btn_toggle_forward_reverse",
                    color="secondary",
                    outline=True,
                    size="lg",
                ),
                className="d-grid gap-2",
            ),
            dbc.Collapse(
                sidebar_right_collapsed_toggle_forward_reverse_graph,
                id="sidebar_right_collapsed_toggle_forward_reverse",
                is_open=False,
            ),
            html.Br(),
            html.Br(),
            html.Br(),
        ]
    )

    sidebar_right = html.Div(
        [
            html.H2("Raw data", className="display-4"),
            # html.Hr(),
            sidebar_right_collapsed_toggle_combined,
            html.Hr(),
            sidebar_right_results,
            html.Hr(),
            sidebar_right_collapsed_toggle_forward_reverse,
        ],
        id="sidebar_right",
        style=start_configuration.style_sidebar_right,
    )

    return sidebar_right


#%%


def get_app_layout(viz_results, start_configuration):

    navbar = get_navbar()
    content_main = get_content_main(viz_results, start_configuration)
    sidebar_left = get_sidebar_left(viz_results, start_configuration)
    sidebar_right = get_sidebar_right(start_configuration)

    modal_filtering = dbc.Modal(
        [
            dbc.ModalHeader("Filtering Error"),
            dbc.ModalBody(
                "Too restrictive filtering, no points left to plot. "
                "Please choose a less restrictive filtering."
            ),
            dbc.ModalFooter(
                dbc.Button("Close", id="modal_close_button", className="ml-auto")
            ),
        ],
        centered=True,
        id="modal",
    )

    modal_pdf = dbc.Modal(
        [
            dbc.ModalHeader("Generating plots, please wait."),
            dbc.ModalBody(
                dbc.Progress(
                    id="progress_bar",
                    value=5,
                    max=100,
                    color="info",
                    striped=True,
                    animated=True,
                )
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Cancel",
                    id="modal_pdf_close_button",
                    className="ml-auto",
                ),
            ),
        ],
        centered=True,
        id="modal_pdf",
    )

    return html.Div(
        [
            dcc.Store(id="sidebar_right_state"),
            dcc.Store(id="sidebar_left_state"),
            navbar,
            sidebar_left,
            content_main,
            sidebar_right,
            modal_filtering,
            modal_pdf,
        ],
    )


#%%


def get_id_dict(child):
    return child["props"]["id"]


def find_index_in_children(children, id_type, search_index):
    for i, child in enumerate(children):
        d_id = get_id_dict(child)
        if d_id["type"] == id_type and d_id["index"] == search_index:
            return i


def get_current_names(current_ids):
    return [x["index"] for x in current_ids if x]


def slider_is_added(current_names, dropdown_names):
    "Returns True if a new slider is added, False otherwise"
    return set(current_names).issubset(dropdown_names)


def get_name_of_added_slider(current_names, dropdown_names):
    return list(set(dropdown_names).difference(current_names))[0]


def get_name_of_removed_slider(current_names, dropdown_names):
    return list(set(current_names).difference(dropdown_names))


def remove_name_from_children(column, children, id_type):
    "Given a column, remove the corresponding child element from children"
    index = find_index_in_children(children, id_type=id_type, search_index=column)
    children.pop(index)


def get_slider_name(column, low_high):
    if isinstance(low_high, dict):
        low = low_high["min"]
        high = low_high["max"]
    elif isinstance(low_high, (tuple, list)):
        low = low_high[0]
        high = low_high[1]

    if viz_utils.is_log_transform_column(column):
        low = viz_utils.log_transform_slider(low)
        high = viz_utils.log_transform_slider(high)

    low = viz_utils.human_format(low)
    high = viz_utils.human_format(high)

    return f"{column}: [{low}, {high}]"


def make_new_slider(
    viz_results, column, id_type, N_steps=100, value=None, min_value=None
):

    d_range_slider = viz_utils.get_range_slider_keywords(
        viz_results,
        column=column,
        N_steps=N_steps,
    )

    if value is not None:
        d_range_slider["value"] = value

    if min_value is not None:
        d_range_slider["value"][0] = min_value

    return dbc.Container(
        [
            dbc.Row(html.Br()),
            dbc.Row(
                html.P(
                    get_slider_name(column, d_range_slider),
                    id={
                        "type": "sidebar_left_results_dynamic_name",
                        "index": column,
                    },
                ),
                justify="center",
            ),
            dbc.Row(
                dbc.Col(
                    dcc.RangeSlider(
                        id={
                            "type": "sidebar_left_results_dynamic",
                            "index": column,
                        },
                        **d_range_slider,
                    ),
                    width=12,
                ),
            ),
        ],
        id={"type": id_type, "index": column},
    )
