from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import diskcache
import pandas as pd
from dash import ALL, MATCH, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
from dash.long_callback import DiskcacheLongCallbackManager

from metaDMG.viz import content, figures, viz_utils
from metaDMG.viz.results import VizResults


def get_app(results_dir):

    ## Diskcache
    cache = diskcache.Cache("./.cache")
    long_callback_manager = DiskcacheLongCallbackManager(cache)

    viz_results = VizResults(results_dir)

    #%%

    viz_utils.set_custom_theme()

    #%%

    external_stylesheets = [dbc.themes.BOOTSTRAP]
    # external_stylesheets = [dbc.themes.ZEPHYR]
    # external_scripts = [
    #     "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/"
    #     "MathJax.js?config=TeX-MML-AM_CHTML",
    # ]

    app = dash.Dash(
        __name__,
        external_stylesheets=external_stylesheets,
        # external_scripts=external_scripts, # Not needed with Dash 3.2, wuhuu!
        title="metaDMG",
        update_title="Updating...",
    )

    # to allow custom css
    # app.scripts.config.serve_locally = True

    #%%

    # (1) No sidebars, (2) Only left filter sidebar,
    # (3) Only right plot sidebar, (4) Both sidebars
    start_configuration_id = 3

    configurations = viz_utils.get_configurations(
        sidebar_left_width=30,
        sidebar_right_width=30,
        content_main_margin=1,
    )
    start_configuration = configurations[start_configuration_id]

    d_columns_latex, columns, columns_no_log = viz_utils.get_d_columns_latex(
        viz_results
    )

    #%%

    app.layout = content.get_app_layout(viz_results, start_configuration)

    #%%

    @app.callback(
        output=[
            Output(
                "navbar_collapsed_toggle_styling",
                "is_open",
            ),
            Output(
                "navbar_btn_toggle_styling",
                "outline",
            ),
        ],
        inputs=dict(
            n=Input(
                "navbar_btn_toggle_styling",
                "n_clicks",
            ),
            is_open=State(
                "navbar_collapsed_toggle_styling",
                "is_open",
            ),
        ),
    )
    def toggle_styling(n, is_open):
        # after click
        if n:
            return not is_open, is_open
        # initial setup
        return is_open, True

    #%%

    @app.callback(
        output=[
            Output(
                "sidebar_right_collapsed_toggle_combined",
                "is_open",
            ),
            Output(
                "sidebar_right_btn_toggle_combined",
                "outline",
            ),
        ],
        inputs=dict(
            n=Input(
                "sidebar_right_btn_toggle_combined",
                "n_clicks",
            ),
            is_open=State(
                "sidebar_right_collapsed_toggle_combined",
                "is_open",
            ),
        ),
    )
    def toggle_sidebar_right_combined(n, is_open):
        if n:
            return not is_open, is_open
        return is_open, False

    @app.callback(
        output=[
            Output(
                "sidebar_right_collapsed_toggle_results",
                "is_open",
            ),
            Output(
                "sidebar_right_btn_toggle_results",
                "outline",
            ),
        ],
        inputs=dict(
            n=Input(
                "sidebar_right_btn_toggle_results",
                "n_clicks",
            ),
            is_open=State(
                "sidebar_right_collapsed_toggle_results",
                "is_open",
            ),
        ),
    )
    def toggle_sidebar_right_results(n, is_open):
        if n:
            return not is_open, is_open
        return is_open, True

    @app.callback(
        output=[
            Output(
                "sidebar_right_collapsed_toggle_forward_reverse",
                "is_open",
            ),
            Output(
                "sidebar_right_btn_toggle_forward_reverse",
                "outline",
            ),
        ],
        inputs=dict(
            n=Input(
                "sidebar_right_btn_toggle_forward_reverse",
                "n_clicks",
            ),
            is_open=State(
                "sidebar_right_collapsed_toggle_forward_reverse",
                "is_open",
            ),
        ),
    )
    def toggle_sidebar_right_forward_reverse(n, is_open):
        if n:
            return not is_open, is_open
        return is_open, True

    #%%

    @app.callback(
        output=Output(
            "sidebar_right_graph_combined",
            "figure",
        ),
        inputs=Input(
            "main_graph",
            "clickData",
        ),
    )
    def update_sidebar_right_plot_combined(click_data):
        return figures.update_raw_count_plots(
            viz_results,
            click_data,
            forward_reverse="",
        )

    @app.callback(
        output=Output(
            "sidebar_right_graph_forward",
            "figure",
        ),
        inputs=Input(
            "main_graph",
            "clickData",
        ),
    )
    def update_sidebar_right_plot_forward(click_data):
        return figures.update_raw_count_plots(
            viz_results,
            click_data,
            forward_reverse="Forward",
        )

    @app.callback(
        output=Output(
            "sidebar_right_graph_reverse",
            "figure",
        ),
        inputs=Input(
            "main_graph",
            "clickData",
        ),
    )
    def update_sidebar_right_plot_reverse(click_data):
        return figures.update_raw_count_plots(
            viz_results,
            click_data,
            forward_reverse="Reverse",
        )

    @app.callback(
        output=Output(
            "sidebar_right_datatable_results",
            "children",
        ),
        inputs=Input(
            "main_graph",
            "clickData",
        ),
    )
    def update_sidebar_right_datatable_results(click_data):
        if click_data:
            sample, tax_id = viz_utils.get_sample_tax_id_from_click_data(
                viz_results, click_data
            )

            df_fit = viz_results.filter({"sample": sample, "tax_id": tax_id})
            if len(df_fit) != 1:
                raise AssertionError(f"Should only be length 1")

            ds = df_fit.iloc[0]

            forward_only = []
            if viz_results.forward_only:
                forward_only = ["Forward only!", html.Br(), html.Br()]

            bayesian_list = []
            if viz_results.Bayesian:

                s1 = "Bayesian_D_max_confidence_interval_1_sigma_low"
                s2 = "Bayesian_D_max_confidence_interval_1_sigma_high"
                if s1 in ds and s2 in ds:

                    s_D_max = f", [{ds[s1]:.3f}, {ds[s2]:.3f}]"

                    conf_q_low = ds["Bayesian_q_confidence_interval_1_sigma_low"]
                    conf_q_high = ds["Bayesian_q_confidence_interval_1_sigma_high"]
                    s_q = f", [{conf_q_low:.3f}, {conf_q_high:.3f}]"

                    conf_phi_low = viz_utils.human_format(
                        ds["Bayesian_phi_confidence_interval_1_sigma_low"]
                    )
                    conf_phi_high = viz_utils.human_format(
                        ds["Bayesian_phi_confidence_interval_1_sigma_high"]
                    )
                    s_phi = f", [{conf_phi_low}, {conf_phi_high}]"

                    conf_A_low = ds["Bayesian_A_confidence_interval_1_sigma_low"]
                    conf_A_high = ds["Bayesian_A_confidence_interval_1_sigma_high"]
                    s_A = f", [{conf_A_low:.3f}, {conf_A_high:.3f}]"

                    conf_c_low = ds["Bayesian_c_confidence_interval_1_sigma_low"]
                    conf_c_high = ds["Bayesian_c_confidence_interval_1_sigma_high"]
                    s_c = f", [{conf_c_low:.3f}, {conf_c_high:.3f}]"

                else:
                    s_D_max = ""
                    s_q = ""
                    s_phi = ""
                    s_c = ""

                bayesian_list = [
                    "Fit results:",
                    html.Br(),
                    f"z: {ds['Bayesian_z']:.2f}",
                    html.Br(),
                    f"D-max: {ds['Bayesian_D_max']:.3f} "
                    f"± {ds['Bayesian_D_max_std']:.3f}" + s_D_max,
                    html.Br(),
                    f"q: {ds['Bayesian_q']:.3f} " f"± {ds['Bayesian_q_std']:.3f}" + s_q,
                    html.Br(),
                    f"phi: {viz_utils.human_format(ds['Bayesian_phi'])} "
                    f"± {viz_utils.human_format(ds['Bayesian_phi_std'])}" + s_phi,
                    html.Br(),
                    f"A: {ds['Bayesian_A']:.3f} " f"± {ds['Bayesian_A_std']:.3f}" + s_A,
                    html.Br(),
                    f"c: {ds['Bayesian_c']:.3f} " f"± {ds['Bayesian_c_std']:.3f}" + s_c,
                    html.Br(),
                    f"rho Ac: {ds['Bayesian_rho_Ac']:.3f}",
                    html.Br(),
                    html.Br(),
                ]

            # fmt: off
            lines = [
                html.Br(),
                f"Sample: {ds['sample']}", html.Br(), html.Br(),

                f"Tax Name: {ds['tax_name']}",
                html.Br(),
                f"Tax rank: {ds['tax_rank']}",
                html.Br(),
                f"Tax ID: {ds['tax_id']}",
                html.Br(),
                html.Br(),

                f"N reads: {viz_utils.human_format(ds['N_reads'])}",
                html.Br(),
                f"N alignments: {viz_utils.human_format(ds['N_alignments'])}",
                html.Br(),
                f"Readlength: {ds['mean_L']:.1f} ± {ds['std_L']:.1f}",
                html.Br(),
                f"GC: {ds['mean_GC']:.2f} ± {ds['std_GC']:.2f}",
                html.Br(),
                html.Br(),

                *forward_only,

                *bayesian_list,

                "MAP results:",
                html.Br(),
                f"lambda LR: {ds['lambda_LR']:.2f}",
                html.Br(),
                f"D-max: {ds['D_max']:.3f} "
                f"± {ds['D_max_std']:.3f}",
                html.Br(),
                f"q: {ds['q']:.3f} ± {ds['q_std']:.3f}",
                html.Br(),
                f"phi: {viz_utils.human_format(ds['phi'])} "
                f"± {viz_utils.human_format(ds['phi_std'])}",
                html.Br(),
                f"A: {ds['A']:.3f} ± {ds['A_std']:.3f}",
                html.Br(),
                f"c: {ds['c']:.3f} ± {ds['c_std']:.3f}",
                html.Br(),
                f"asymmetry: {ds['asymmetry']:.3f}",
                html.Br(),
                f"rho Ac: {ds['rho_Ac']:.3f}",
                html.Br(),
                f"Fit valid: {ds['valid']}",
                html.Br(),
                html.Br(),

                f"Tax path: {viz_utils.tax_path_to_string(ds['tax_path'])}",
                html.Br(),
                html.Br(),

                # f"LR_All: {ds['LR_All']:.3f}", html.Br(),
                # f"LR_ForRev: {ds['LR_ForRev']:.3f}", html.Br(),
                # f"LR_ForRev_All: {ds['LR_ForRev_All']:.3f}", html.Br(), html.Br(),
                # f"chi2 all: {ds['chi2_all']:.3f}", html.Br(),
                # f"chi2_ForRev: {ds['chi2_ForRev']:.3f}", html.Br(),
            ]
            # fmt: on

            return [
                html.P(lines),
                # html.Div(
                #     children=html.Img(
                #         src="http://latex2png.com/pngs/2cc065b79dc0045babf538323a9a59c4.png",
                #         style={
                #             "maxWidth": "100%",
                #             "maxHeight": "100%",
                #             "marginLeft": "auto",
                #             "marginRight": "auto",
                #         },
                #     ),
                # ),
            ]

        return html.P(["Please select a point"])

    #%%

    @app.callback(
        output=[
            Output(
                "main_graph",
                "figure",
            ),
            Output(
                "modal",
                "is_open",
            ),
        ],
        inputs=dict(
            sidebar_left_dropdown_samples=Input(
                "sidebar_left_dropdown_samples",
                "value",
            ),
            sidebar_left_taxa_input_specific=Input(
                "sidebar_left_taxa_input_specific",
                "value",
            ),
            sidebar_left_taxa_input_path_contains=Input(
                "sidebar_left_taxa_input_path_contains",
                "value",
            ),
            # tax_id_plot_button=Input("tax_id_plot_button", "n_clicks",),
            sidebar_left_results_dynamic_value=Input(
                {"type": "sidebar_left_results_dynamic", "index": ALL},
                "value",
            ),
            xaxis_column_name=Input(
                "xaxis_column",
                "value",
            ),
            yaxis_column_name=Input(
                "yaxis_column",
                "value",
            ),
            marker_transformation_variable=Input(
                "marker_transformation_variable",
                "value",
            ),
            marker_transformation_function=Input(
                "marker_transformation_function",
                "value",
            ),
            marker_transformation_slider=Input(
                "marker_transformation_slider",
                "value",
            ),
            modal_close_button=Input(
                "modal_close_button",
                "n_clicks",
            ),
            sidebar_left_results_dynamic_ids=State(
                {"type": "sidebar_left_results_dynamic", "index": ALL},
                "id",
            ),
            modal=State(
                "modal",
                "is_open",
            ),
        ),
    )
    def update_main_graph(
        sidebar_left_dropdown_samples,
        sidebar_left_taxa_input_specific,
        sidebar_left_taxa_input_path_contains,
        sidebar_left_results_dynamic_value,
        xaxis_column_name,
        yaxis_column_name,
        marker_transformation_variable,
        marker_transformation_function,
        marker_transformation_slider,
        modal_close_button,
        sidebar_left_results_dynamic_ids,
        modal,
    ):

        # if modal is open and the "close" button is clicked, close down modal
        if modal_close_button and modal:
            return dash.no_update, False

        # if no files selected
        if not sidebar_left_dropdown_samples:
            raise PreventUpdate

        viz_results.set_marker_size(
            marker_transformation_variable,
            marker_transformation_function,
            marker_transformation_slider,
        )

        df_results_filtered = filter_dataframe(
            viz_results,
            sidebar_left_dropdown_samples,
            sidebar_left_results_dynamic_ids,
            sidebar_left_results_dynamic_value,
            sidebar_left_taxa_input_specific,
            sidebar_left_taxa_input_path_contains,
            # sidebar_left_tax_id_subspecies,
        )

        # raise modal warning if no results due to too restrictive filtering
        if len(df_results_filtered) == 0:
            return dash.no_update, True

        fig = figures.make_figure(
            viz_results,
            df=df_results_filtered,
            xaxis_column_name=xaxis_column_name,
            yaxis_column_name=yaxis_column_name,
            d_columns_latex=d_columns_latex,
        )

        return fig, dash.no_update

    #%%

    @app.callback(
        output=Output(
            "sidebar_left_dropdown_samples",
            "value",
        ),
        inputs=Input(
            "sidebar_left_dropdown_samples",
            "value",
        ),
    )
    def update_dropdown_samples_when_Select_all(sidebar_left_dropdown_samples):
        if viz_utils.key_is_in_list_case_insensitive(
            sidebar_left_dropdown_samples,
            "Select all",
        ):
            sidebar_left_dropdown_samples = viz_results.samples
        elif viz_utils.key_is_in_list_case_insensitive(
            sidebar_left_dropdown_samples,
            "Default selection",
        ):
            sidebar_left_dropdown_samples = viz_utils.get_samples_each(
                viz_results.samples
            )

        sidebar_left_dropdown_samples = list(sorted(sidebar_left_dropdown_samples))

        return sidebar_left_dropdown_samples

    #%%

    @app.callback(
        output=Output(
            "sidebar_left_results_container",
            "children",
        ),
        inputs=dict(
            dropdown_names=Input(
                "sidebar_left_results",
                "value",
            ),
            children=State(
                "sidebar_left_results_container",
                "children",
            ),
            current_ids=State(
                {"type": "sidebar_left_results_dynamic", "index": ALL},
                "id",
            ),
        ),
        prevent_initial_call=True,
    )
    def update_sidebar_left_fit_result_sliders(dropdown_names, children, current_ids):

        id_type = "dbc"

        current_names = content.get_current_names(current_ids)

        # add new slider
        if content.slider_is_added(current_names, dropdown_names):
            column = content.get_name_of_added_slider(current_names, dropdown_names)
            new_element = content.make_new_slider(viz_results, column, id_type=id_type)
            children.append(new_element)

        # remove selected slider
        else:
            columns = content.get_name_of_removed_slider(current_names, dropdown_names)
            for column in columns:
                content.remove_name_from_children(column, children, id_type=id_type)

        return children

    @app.callback(
        output=Output(
            {"type": "sidebar_left_results_dynamic_name", "index": MATCH},
            "children",
        ),
        inputs=dict(
            dynamic_slider_values=Input(
                {"type": "sidebar_left_results_dynamic", "index": MATCH},
                "value",
            ),
            sidebar_left_results_dynamic_name=State(
                {"type": "sidebar_left_results_dynamic", "index": MATCH},
                "id",
            ),
        ),
        prevent_initial_call=False,
    )
    def update_sidebar_left_fit_result_slider_names(
        dynamic_slider_values, sidebar_left_results_dynamic_name
    ):
        column = sidebar_left_results_dynamic_name["index"]
        name = content.get_slider_name(column, dynamic_slider_values)
        return name

    #%%

    @app.callback(
        output=[
            Output(
                "sidebar_left_samples_collapsed",
                "is_open",
            ),
            Output(
                "sidebar_left_samples_btn",
                "outline",
            ),
        ],
        inputs=dict(
            n=Input(
                "sidebar_left_samples_btn",
                "n_clicks",
            ),
            is_open=State(
                "sidebar_left_samples_collapsed",
                "is_open",
            ),
        ),
    )
    def toggle_sidebar_left_samples(n, is_open):
        # after click
        if n:
            return not is_open, is_open
        # initial setup
        return True, False

    @app.callback(
        output=[
            Output(
                "sidebar_left_taxanomics_collapsed",
                "is_open",
            ),
            Output(
                "sidebar_left_taxanomics_btn",
                "outline",
            ),
        ],
        inputs=dict(
            n=Input(
                "sidebar_left_taxanomics_btn",
                "n_clicks",
            ),
            is_open=State(
                "sidebar_left_taxanomics_collapsed",
                "is_open",
            ),
        ),
    )
    def toggle_sidebar_left_taxanomics(n, is_open):
        if n:
            return not is_open, is_open
        return False, True

    @app.callback(
        output=[
            Output(
                "sidebar_left_results_collapsed",
                "is_open",
            ),
            Output(
                "sidebar_left_results_btn",
                "outline",
            ),
        ],
        inputs=dict(
            n=Input(
                "sidebar_left_results_btn",
                "n_clicks",
            ),
            is_open=State(
                "sidebar_left_results_collapsed",
                "is_open",
            ),
        ),
    )
    def toggle_sidebar_left_results(n, is_open):
        if n:
            return not is_open, is_open
        return True, False

    #%%

    @app.callback(
        output=[
            Output(
                "content_main",
                "style",
            ),
            Output(
                "sidebar_left",
                "style",
            ),
            Output(
                "sidebar_right",
                "style",
            ),
            Output(
                "sidebar_left_state",
                "data",
            ),
            Output(
                "sidebar_right_state",
                "data",
            ),
            Output(
                "sidebar_left_toggle_btn",
                "outline",
            ),
            Output(
                "sidebar_right_toggle_btn",
                "outline",
            ),
        ],
        inputs=dict(
            _sidebar_left_toggle_btn=Input(
                "sidebar_left_toggle_btn",
                "n_clicks",
            ),
            _sidebar_right_toggle_btn=Input(
                "sidebar_right_toggle_btn",
                "n_clicks",
            ),
            current_state_sidebar_left=State(
                "sidebar_left_state",
                "data",
            ),
            current_state_sidebar_right=State(
                "sidebar_right_state",
                "data",
            ),
            sidebar_left_toggle_btn_outline=State(
                "sidebar_left_toggle_btn",
                "outline",
            ),
            sidebar_right_toggle_btn_outline=State(
                "sidebar_right_toggle_btn",
                "outline",
            ),
        ),
    )
    def toggle_sidebars(
        _sidebar_left_toggle_btn,
        _sidebar_right_toggle_btn,
        current_state_sidebar_left,
        current_state_sidebar_right,
        sidebar_left_toggle_btn_outline,
        sidebar_right_toggle_btn_outline,
    ):

        button_id = viz_utils.get_button_id(dash.callback_context)

        # if the toggle filter button was clicked
        if button_id == "sidebar_left_toggle_btn":
            return (
                *viz_utils.toggle_filter(
                    configurations,
                    current_state_sidebar_left,
                    current_state_sidebar_right,
                ),
                not sidebar_left_toggle_btn_outline,
                sidebar_right_toggle_btn_outline,
            )

        # if the toggle plot button was clicked
        elif button_id == "sidebar_right_toggle_btn":
            return (
                *viz_utils.toggle_plot(
                    configurations,
                    current_state_sidebar_left,
                    current_state_sidebar_right,
                ),
                sidebar_left_toggle_btn_outline,
                not sidebar_right_toggle_btn_outline,
            )

        # base configuration
        else:
            return *start_configuration, True, False

    #%%

    @app.callback(
        output=[
            Output("memory-store-csv", "data"),
            Output("memory-store-pdf", "data"),
        ],
        inputs=dict(
            navbar_btn_export_csv=Input(
                "navbar_btn_export_csv",
                "n_clicks",
            ),
            navbar_btn_export_pdf=Input(
                "navbar_btn_export_pdf",
                "n_clicks",
            ),
            sidebar_left_dropdown_samples=State(
                "sidebar_left_dropdown_samples",
                "value",
            ),
            sidebar_left_taxa_input_specific=State(
                "sidebar_left_taxa_input_specific",
                "value",
            ),
            sidebar_left_results_dynamic_value=State(
                {"type": "sidebar_left_results_dynamic", "index": ALL},
                "value",
            ),
            sidebar_left_results_dynamic_ids=State(
                {"type": "sidebar_left_results_dynamic", "index": ALL},
                "id",
            ),
            sidebar_left_taxa_input_path_contains=State(
                "sidebar_left_taxa_input_path_contains",
                "value",
            ),
            # prevent_initial_call=True,
        ),
    )
    def make_data_for_export(
        navbar_btn_export_csv,
        navbar_btn_export_pdf,
        sidebar_left_dropdown_samples,
        sidebar_left_taxa_input_specific,
        sidebar_left_results_dynamic_value,
        sidebar_left_results_dynamic_ids,
        sidebar_left_taxa_input_path_contains,
    ):

        ctx = dash.callback_context
        if not ctx.triggered:
            button_id = "No clicks yet"
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if navbar_btn_export_csv or navbar_btn_export_pdf:

            df_results_filtered = filter_dataframe(
                viz_results,
                sidebar_left_dropdown_samples,
                sidebar_left_results_dynamic_ids,
                sidebar_left_results_dynamic_value,
                sidebar_left_taxa_input_specific,
                sidebar_left_taxa_input_path_contains,
            )

            df_dict = df_results_filtered.to_dict("records")

            if button_id == "navbar_btn_export_csv":
                return df_dict, dash.no_update

            if button_id == "navbar_btn_export_pdf":
                return dash.no_update, df_dict

        else:
            raise PreventUpdate

    @app.callback(
        output=Output(
            "export_csv",
            "data",
        ),
        inputs=dict(
            data=Input(
                "memory-store-csv",
                "data",
            ),
        ),
    )
    def export_csv(
        data,
    ):

        # if data is None or n_clicks is None:
        if data is None:
            return dash.no_update

        df_results_filtered = pd.DataFrame(data)

        send_dataframe = dcc.send_data_frame(
            df_results_filtered.to_csv,
            "filtered_results.csv",
            index=False,
        )
        return send_dataframe

    @app.long_callback(
        output=Output(
            "export_pdf",
            "data",
        ),
        inputs=dict(
            data=Input(
                "memory-store-pdf",
                "data",
            ),
        ),
        running=[
            (
                Output("modal_pdf", "is_open"),
                True,
                False,
            ),
        ],
        progress=[
            Output(
                "progress_bar",
                "value",
            ),
            Output(
                "progress_bar",
                "max",
            ),
        ],
        cancel=[
            Input(
                "modal_pdf_close_button",
                "n_clicks",
            )
        ],
        manager=long_callback_manager,
        prevent_initial_call=True,
    )
    def export_pdf(
        set_progress,
        data,
    ):

        # if data is None or n_clicks is None:
        if data is None:
            return dash.no_update

        df_results_filtered = pd.DataFrame(data)

        pdf_path = "pdf_export.pdf"
        figures.save_pdf_plots(
            df_results_filtered,
            viz_results,
            pdf_path=pdf_path,
            set_progress=set_progress,
        )
        return dcc.send_file(pdf_path)

    # %%

    return app


#%%


def apply_sidebar_left_tax_id(viz_results, d_filter, sidebar_left_taxa_input_specific):

    d_filter = d_filter.copy()

    if (
        sidebar_left_taxa_input_specific is None
        or len(sidebar_left_taxa_input_specific) == 0
    ):
        return d_filter

    for tax in sidebar_left_taxa_input_specific:
        if tax in viz_results.all_tax_ids:
            d_filter = viz_utils.append_to_list_if_exists(d_filter, "tax_ids", tax)
        elif tax in viz_results.all_tax_names:
            d_filter = viz_utils.append_to_list_if_exists(d_filter, "tax_names", tax)
        elif tax in viz_results.all_tax_ranks:
            d_filter = viz_utils.append_to_list_if_exists(d_filter, "tax_ranks", tax)
        else:
            raise AssertionError(f"Tax {tax} could not be found. ")

    return d_filter


#%%


def filter_dataframe(
    viz_results,
    sidebar_left_dropdown_samples,
    sidebar_left_results_dynamic_ids,
    sidebar_left_results_dynamic_value,
    sidebar_left_taxa_input_specific,
    sidebar_left_taxa_input_path_contains,
):

    d_filter = {"samples": sidebar_left_dropdown_samples}

    columns_no_log = [id["index"] for id in sidebar_left_results_dynamic_ids]
    for sample, values in zip(columns_no_log, sidebar_left_results_dynamic_value):
        d_filter[sample] = values

    d_filter = apply_sidebar_left_tax_id(
        viz_results,
        d_filter,
        sidebar_left_taxa_input_specific,
    )

    df_results_filtered = viz_results.filter(
        d_filter,
        rank=sidebar_left_taxa_input_path_contains,
    )

    return df_results_filtered
