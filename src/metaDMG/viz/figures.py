# import matplotlib
# matplotlib.use("Agg")

#%%

import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from matplotlib import ticker
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import EngFormatter
from tqdm import tqdm

from metaDMG.viz import viz_utils


#%%

plt.rcParams["text.usetex"] = True

#%%

#%%


def create_empty_figure(s=None, width=None, height=None):

    if s is None:
        s = "Please select a point"

    fig = go.Figure()

    fig.add_annotation(
        xref="x domain",
        yref="y domain",
        x=0.5,
        y=0.5,
        text=s,
        font_size=20,
        showarrow=False,
    )

    fig.update_layout(
        xaxis_visible=False,
        yaxis_visible=False,
        width=width,
        height=height,
    )

    if width is not None:
        fig.update_layout(width=width)

    if height is not None:
        fig.update_layout(height=height)

    return fig


#%%


def set_opacity_for_trace(
    trace, method="sqrt", scale=3.0, opacity_min=0.001, opacity_max=0.9
):
    N = len(trace.x)
    if "lin" in method:
        opacity = 1 / N
    elif method == "sqrt":
        opacity = 1 / np.sqrt(N)
    elif method == "log":
        opacity = 1 / np.log(N)

    opacity *= scale
    opacity = max(opacity_min, min(opacity, opacity_max))

    # print(trace.name, opacity)
    trace.update(marker_opacity=opacity)


#%%


def make_figure(
    viz_results,
    df=None,
    xaxis_column_name="lambda_LR",
    yaxis_column_name="D_max",
    d_columns_latex=None,
):

    if df is None:
        df = viz_results.df

    if d_columns_latex is None:
        d_columns_latex = viz_utils.get_d_columns_latex(viz_results)[0]

    fig = px.scatter(
        # df,
        viz_utils.replace_nans(df),
        x=xaxis_column_name,
        y=yaxis_column_name,
        size="size",
        color="sample",
        hover_name="sample",
        color_discrete_map=viz_results.d_cmap,
        custom_data=viz_results.custom_data_columns,
        render_mode="webgl",
        symbol="sample",
        symbol_map=viz_results.d_symbols,
    )

    # 2. * max(array of size values) / (desired maximum marker size ** 2)

    fig.update_traces(
        hovertemplate=viz_results.hovertemplate,
        marker_line_width=0,
        marker_sizemode="area",
        marker_sizeref=2.0 * viz_results.max_of_size / (viz_results.marker_size**2),
    )

    fig.update_layout(
        xaxis_title=xaxis_column_name,
        yaxis_title=yaxis_column_name,
        showlegend=False,
    )

    N_unique = df["sample"].nunique()
    if N_unique <= 10:
        fig.update_layout(
            showlegend=True,
            legend=dict(
                title="Samples: ",
                title_font_size=16,
                font_size=12,
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

    fig.for_each_trace(
        lambda trace: set_opacity_for_trace(
            trace,
            method="sqrt",
            scale=20 / df["sample"].nunique(),
            opacity_min=0.3,
            opacity_max=0.95,
        )
    )

    fig.update_xaxes(title=d_columns_latex[xaxis_column_name])
    fig.update_yaxes(title=d_columns_latex[yaxis_column_name])

    return fig


#%%


def plot_group(viz_results, group, D_max_info=None, fit=None, forward_reverse=""):

    custom_data_columns = [
        "direction",
        "f",
        "k",
        "N",
    ]

    hovertemplate = (
        "<b>%{customdata[0]}</b><br>"
        "f: %{customdata[1]:8.3f} <br>"
        "k: %{customdata[2]:8d} <br>"
        "N: %{customdata[3]:8d} <br>"
        "<extra></extra>"
    )

    fig = px.scatter(
        group,
        x="|x|",
        y="f",
        color="direction",
        color_discrete_map=viz_results.d_cmap_fit,
        hover_name="direction",
        custom_data=custom_data_columns,
    )

    max_position = viz_utils.get_max_position_from_group(group)

    fig.update_xaxes(
        title_text=r"$|x|$",
        title_standoff=0,
        range=[0.3, max_position + 0.5],
    )
    fig.update_yaxes(
        title=r"",
        rangemode="nonnegative",  # tozero, nonnegative
    )

    fig.update_traces(hovertemplate=hovertemplate, marker={"size": 10})

    layout = dict(
        title_text=r"",
        autosize=False,
        margin=dict(l=10, r=10, t=10, b=10),
        # hovermode="x",
        hovermode="x unified",
        hoverlabel_font_size=14,
    )

    if forward_reverse == "":
        fig.update_layout(
            **layout,
            legend=dict(
                title_text="",
                font_size=18,
                y=1.15,
                yanchor="top",
                x=0.95,
                xanchor="right",
                bordercolor="grey",
                borderwidth=1,
                itemclick="toggle",
                itemdoubleclick="toggleothers",
            ),
        )

        fig.add_annotation(
            # text=r"$\frac{k}{N}$",
            text=r"$k \,/ \,N$",
            x=0.01,
            xref="paper",
            xanchor="center",
            y=1.05,
            yref="paper",
            yanchor="bottom",
            showarrow=False,
            font_size=30,
        )

        # add D-max as single errorbar
        if D_max_info is not None:

            D_max, D_max_low, D_max_high = D_max_info

            # fit with errorbars
            fig.add_trace(
                go.Scatter(
                    x=[0.5],
                    y=[D_max],
                    error_y=dict(
                        type="data",
                        symmetric=False,
                        array=[D_max_high - D_max],
                        arrayminus=[D_max - D_max_low],
                        visible=True,
                        color="black",
                    ),
                    mode="markers",
                    name="D-max",
                    marker_color="black",
                    # hovertemplate=viz_results.hovertemplate_D_max,
                    hoverinfo="skip",
                )
            )

    else:

        fig.update_layout(**layout, showlegend=False)

    if fit is None:
        return fig

    if isinstance(fit, str):
        fig.add_annotation(
            text=fit,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            textangle=-10,
            font=dict(color="red", size=60),
        )
        return fig

    green_color = viz_results.d_cmap_fit["Fit"]
    green_color_transparent = viz_utils.hex_to_rgb(green_color, opacity=0.1)

    # fit with errorbars
    fig.add_trace(
        go.Scatter(
            x=fit["|x|"],
            y=fit["mu"],
            error_y=dict(
                type="data",
                array=fit["std"],
                visible=True,
                color=green_color,
            ),
            mode="markers",
            name="Fit",
            marker_color=green_color,
            hovertemplate=viz_results.hovertemplate_fit,
        )
    )

    # fit filled area start
    fig.add_trace(
        go.Scatter(
            x=fit["|x|"],
            y=fit["mu"] + fit["std"],
            mode="lines",
            line_width=0,
            showlegend=False,
            fill=None,
            hoverinfo="skip",
        )
    )

    # fit filled stop
    fig.add_trace(
        go.Scatter(
            x=fit["|x|"],
            y=fit["mu"] - fit["std"],
            mode="lines",
            line_width=0,
            fill="tonexty",
            fillcolor=green_color_transparent,
            showlegend=False,
            hoverinfo="skip",
        )
    )

    return fig


#%%


def update_raw_count_plots(viz_results, click_data, forward_reverse):
    if click_data is not None:

        sample, tax_id = viz_utils.get_sample_tax_id_from_click_data(
            viz_results,
            click_data,
        )

        group = viz_results.get_single_count_group(
            sample,
            tax_id,
            forward_reverse,
        )
        fit = viz_results.get_single_fit_prediction(
            sample,
            tax_id,
            forward_reverse,
        )

        D_max_info = viz_results.get_D_max(sample, tax_id)

        fig = plot_group(
            viz_results,
            group,
            D_max_info,
            fit,
            forward_reverse,
        )
        return fig
    else:
        raise PreventUpdate


#%%


def compute_markersize(
    x,
    size_min,
    size_max,
    markersize_min=1,
    markersize_max=100,
):
    return (x - size_min) / (size_max - size_min) * (
        markersize_max - markersize_min
    ) + markersize_min


def plt_scatterplot(df, viz_results):

    x = "Bayesian_z" if viz_results.Bayesian else "lambda_LR"
    y = "Bayesian_D_max" if viz_results.Bayesian else "D_max"

    size_max = df["size"].max()
    size_min = df["size"].min()

    styles = viz_utils.get_mpl_styles()
    with plt.style.context(styles):

        fig, ax = plt.subplots(figsize=(4, 4))

        for sample, group in df.groupby("sample", sort=False):
            # break

            markersize = compute_markersize(
                group["size"],
                size_min,
                size_max,
            )
            ax.scatter(
                group[x],
                group[y],
                c=viz_results.d_cmap[sample],
                s=markersize,
                marker=viz_results.d_markers[sample],
                label=r"$\verb|" + sample + r"|$" if viz_utils.has_latex() else sample,
            )

        ax.set_xlabel(
            r"$z$" if viz_results.Bayesian else r"$\lambda_\mathrm{LR}$",
            fontsize=12,
        )
        ax.set_ylabel(
            r"$D_\mathrm{max}$",
            fontsize=12,
            labelpad=5,
        )
        ax.tick_params(axis="both", labelsize=10)

        legend = ax.legend(
            title=r"Samples:",
            title_fontsize=12,
            fontsize=8,
            loc="lower center",
            bbox_to_anchor=(0.5, 1.0),
            ncol=1,
        )
        for legend_handle in legend.legendHandles:
            legend_handle._sizes = [30]

    return fig, ax


#%%


def get_dataseries(df, viz_results):
    d = {}
    for sample, group in df.groupby("sample", sort=False):
        group["N_reads_rel"] = group["N_reads"] / group["N_reads"].sum()
        viz_utils.add_tax_str(group, include_rank=False)
        ds = (
            group[["tax_str", "N_reads_rel", "N_reads"]]
            .reset_index(drop=True)
            .sort_values("N_reads_rel", ascending=False)
        )
        ds["color"] = viz_results.d_cmap[sample]
        d[sample] = ds
    return d


def plt_bar_chart(ds, sample, max_rows=20):

    ds_plot = ds.iloc[:max_rows].iloc[::-1]
    color = ds["color"].iloc[0]

    styles = viz_utils.get_mpl_styles()
    with plt.style.context(styles):

        fig, ax = plt.subplots(figsize=(3, 4))

        ds_plot.plot.barh(
            x="tax_str",
            y="N_reads",
            legend=False,
            ax=ax,
            color=color,
            width=0.6,
        )

        title = (
            r"\large{Sample: \verb|"
            + sample
            + r"|}"
            + "\n"
            + r"\small{"
            + f"{viz_utils.human_format(len(ds))} Tax IDs selected"
            + r"}"
        )

        if not viz_utils.has_latex():
            title = f"Sample: {sample}. \n{viz_utils.human_format(len(ds))} Tax IDs selected."

        ax.set(ylabel="")
        ax.set_title(title, pad=10)
        ax.set_xlabel("Number of reads", fontsize=12, labelpad=5)
        ax.tick_params(axis="x", labelsize=8)
        ax.tick_params(axis="y", labelsize=6)

        ax.xaxis.set_major_formatter(EngFormatter(usetex=True))
        fig.tight_layout()

    return fig, ax


def plt_bar_charts(df, viz_results):
    d_ds = get_dataseries(df, viz_results)
    figs = []
    for sample, ds in d_ds.items():
        fig, ax = plt_bar_chart(ds, sample)
        figs.append(fig)
    return figs


#%%


class MultipleOffsetLocator(ticker.MultipleLocator):
    def __init__(self, base=1.0, offset=0.0):
        self._edge = ticker._Edge_integer(base, 0)
        self._offset = offset

    def tick_values(self, vmin, vmax):
        if vmax < vmin:
            vmin, vmax = vmax, vmin
        step = self._edge.step
        vmin = self._edge.ge(vmin) * step
        n = (vmax - vmin + 0.001 * step) // step
        locs = self._offset + vmin - step + np.arange(n + 3) * step
        return self.raise_if_exceeds(locs)


def plt_errorplot(viz_results, group, fit=None):

    mask_forward = group["direction"].str.lower() == "forward"
    mask_reverse = group["direction"].str.lower() == "reverse"

    sample = group["sample"].iloc[0]
    color = viz_results.d_cmap[sample]
    marker = viz_results.d_markers[sample]

    styles = viz_utils.get_mpl_styles()
    with plt.style.context(styles):
        fig, ax = plt.subplots(figsize=(4, 4))

        ax.plot(
            group.loc[mask_forward, ["|x|"]].values,
            group.loc[mask_forward, ["f"]].values,
            linestyle="None",
            color=color,
            marker=marker,
            markersize=4.5,
            markeredgewidth=0,
            label="Forward",
        )

        if not viz_results.forward_only:
            ax.plot(
                group.loc[mask_reverse, ["|x|"]].values,
                group.loc[mask_reverse, ["f"]].values,
                linestyle="None",
                color=color,
                marker=marker,
                markersize=5,
                markeredgewidth=0,
                label="Reverse",
                alpha=0.4,
            )

        if isinstance(fit, str):
            pass

        elif fit is not None:
            ax.plot(fit["|x|"], fit["Dx"], "-", color="dimgrey", label="Fit")
            ax.fill_between(
                fit["|x|"],
                fit["Dx"] + fit["std"],
                fit["Dx"] - fit["std"],
                color="grey",
                alpha=0.2,
                edgecolor="none",
                label=r"$1 \sigma$ C.I.",
            )

        ax.set(ylim=(0, None), xlim=(0.5, group["|x|"].max() + 0.5))
        ax.set_xlabel(r"$|x|$", fontsize=12)

        ax.set_ylabel(
            r"$\displaystyle\frac{k}{N}$" if viz_utils.has_latex() else "k / N",
            fontsize=12,
            labelpad=15,
            rotation=0,
        )
        ax.tick_params(axis="both", labelsize=10)

        title = (
            r"\Large{Tax ID: "
            + str(group["tax_id"].iloc[0])
            + r"}"
            + "\n\n"
            + r"\small{Sample: \verb|"
            + sample
            + r"|}"
        )

        if not viz_utils.has_latex():
            title = f"Tax ID: {group['tax_id'].iloc[0]}. \nSample: {sample}"

        ax.set_title(title, pad=30)

        ax.xaxis.set_major_locator(MultipleOffsetLocator(base=2, offset=1))

        legend = ax.legend(
            # title=r"Direction:",
            # title_fontsize=14,
            fontsize=10,
            loc="lower center",
            bbox_to_anchor=(0.48, 0.99),
            ncol=4,
            handletextpad=0.4,
            columnspacing=1.2,
        )
        for legend_handle in legend.legendHandles:
            legend_handle._sizes = [40]

        # set custom spacing between Forward/Reverse and dots
        for vpacker in legend._legend_handle_box._children[:2]:
            for hpacker in vpacker._children:
                hpacker.sep = -3

        if isinstance(fit, str):
            pass

        elif fit is not None:
            ax.text(
                0.95,
                0.95,
                fit["text"],
                verticalalignment="top",
                horizontalalignment="right",
                transform=ax.transAxes,
                fontsize=12,
            )

    return fig


def count_errorplots(viz_results, df):
    counter = 0
    for sample, sample_group in df.groupby("sample", sort=False):
        for tax_id in sample_group["tax_id"]:
            counter += 1
    return counter


def plt_errorplots(viz_results, df):
    for sample, sample_group in df.groupby("sample", sort=False):
        for tax_id in sample_group["tax_id"]:
            # x=x
            group = viz_results.get_single_count_group(sample=sample, tax_id=tax_id)
            fit = viz_results.get_single_fit_prediction(sample, tax_id)
            fig = plt_errorplot(viz_results=viz_results, group=group, fit=fit)
            yield fig


def count_all_plots(df, viz_results):
    total = 1 + df["sample"].nunique() + count_errorplots(viz_results, df)
    return total


#%%


def generate_plt_plots(df, viz_results):

    fig_scatter = plt_scatterplot(df, viz_results)[0]
    yield fig_scatter

    fig_bar_charts = plt_bar_charts(df, viz_results)
    for fig_bar_chart in fig_bar_charts:
        yield fig_bar_chart

    for fig_error_plot in plt_errorplots(viz_results, df):
        yield fig_error_plot


def save_pdf_plots(
    df,
    viz_results,
    pdf_path="pdf_export.pdf",
    set_progress=None,
    do_tqdm=False,
):

    figs = generate_plt_plots(df=df, viz_results=viz_results)
    total = count_all_plots(df=df, viz_results=viz_results)

    if do_tqdm:
        figs = tqdm(figs, desc=f"Making plots", total=total)

    def progress(i, total):
        if set_progress is None:
            return None
        return set_progress((max(i + 1, int(0.05 * total)), total))

    with PdfPages(pdf_path) as pdf:
        for i, fig in enumerate(figs):
            progress(i, total)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close("all")
        d = pdf.infodict()
        d["Title"] = "metaDMG plots"
        d["Author"] = "Christian Michelsen"


# %%
