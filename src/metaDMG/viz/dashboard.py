from metaDMG.viz import app, viz_utils


def start_dashboard(
    results_dir=None,
    debug=False,
    host="0.0.0.0",
    port=8050,
):

    if results_dir is None:
        raise Exception(f"Has to be specified.")

    if not debug:
        viz_utils.open_browser_in_background()

    dashboard_app = app.get_app(results_dir)

    dashboard_app.run_server(
        debug=debug,
        host=host,
        port=port,
    )
