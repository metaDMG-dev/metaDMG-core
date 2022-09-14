#%%
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import betabinom as sp_betabinom

from metaDMG.viz import viz_utils


def sort_dataframe(df):
    samples_ordered = list(
        df.groupby("sample")
        .sum("N_reads")
        .sort_values("N_reads", ascending=False)
        .index
    )

    # Create the dictionary that defines the order for sorting
    sorterIndex = dict(zip(samples_ordered, range(len(samples_ordered))))

    # Generate a rank column that will be used to sort
    # the dataframe numerically
    df["sample_rank"] = df["sample"].map(sorterIndex)

    df = df.sort_values(
        ["sample_rank", "tax_id"],
        ascending=[True, True],
        inplace=False,
    ).drop(columns="sample_rank")

    return df


def clip_df(df, column):
    if column in df.columns:
        df["_" + column] = df[column]  # save original data _column
        df[column] = np.clip(df[column], a_min=0, a_max=None)


def pd_wide_to_long_forward_reverse(group_wide, sep, direction):
    stub_names = ["k", "N", "f"]
    group_long = pd.wide_to_long(
        group_wide,
        stubnames=stub_names,
        i="tax_id",
        j="|x|",
        sep=sep,
    )[stub_names]
    group_long["direction"] = direction
    return group_long.reset_index()


def wide_to_long_df(group_wide):

    group_long_forward = pd_wide_to_long_forward_reverse(
        group_wide,
        sep="+",
        direction="Forward",
    )

    try:
        group_long_reverse = pd_wide_to_long_forward_reverse(
            group_wide,
            sep="-",
            direction="Reverse",
        )

        group_long = pd.concat([group_long_forward, group_long_reverse])
        # group_long.loc[:, ["k", "N"]] = group_long.loc[:, ["k", "N"]].astype(int)

    # happens when forward only
    except ValueError:
        group_long = group_long_forward

    group_long["sample"] = group_wide["sample"].iloc[0]

    return group_long


# def remove_LCA_columns(columns):
#     remove_cols = ["tax_name", "tax_rank", "N_alignments"]
#     return [col for col in columns if col not in remove_cols]


def correct_for_non_LCA(df):
    if "N_alignments" in df.columns:
        df.loc[:, "N_alignments"] = df["N_alignments"].fillna(np.nan)
    else:
        df.loc[:, "N_alignments"] = np.nan

    if "tax_name" in df.columns:
        df.loc[:, "tax_name"] = df["tax_name"].fillna("NO TAX NAME")
    else:
        df.loc[:, "tax_name"] = "NO TAX NAME"

    if "tax_rank" in df.columns:
        df.loc[:, "tax_rank"] = df["tax_rank"].fillna("NO TAX RANK")
    else:
        df.loc[:, "tax_rank"] = "NO TAX RANK"

    if "tax_path" in df.columns:
        df.loc[:, "tax_path"] = df["tax_path"].fillna("NO TAX PATH")
    else:
        df.loc[:, "tax_path"] = "NO TAX PATH"

    return df


#%%


def compute_variance_scaling(df, phi_string):
    phi = df[phi_string]
    if "N_x=1_reverse" in df.columns:
        N_x = [df["N_x=1_forward"], df["N_x=1_reverse"]]
    else:
        N_x = [df["N_x=1_forward"]]
    N = np.mean(N_x)
    return (phi + N) / (phi + 1)


#%%


class VizResults:
    def __init__(self, results_dir):
        self.results_dir = Path(results_dir)
        self._load_df_results()
        self._set_cmap()
        self._set_hover_info()

    def _load_parquet_file(self, results_dir):
        df = pd.read_parquet(results_dir)
        return correct_for_non_LCA(df)

    def _load_df_results(self):
        df = self._load_parquet_file(self.results_dir)
        df = sort_dataframe(df)

        # force tax_id to be categorical strings.
        # XXX remove in final version
        df.loc[:, "tax_id"] = df["tax_id"].astype("str").astype("category")

        for column in ["lambda_LR", "forward_lambda_LR", "reverse_lambda_LR"]:
            clip_df(df, column)

        Bayesian = any(["Bayesian" in column for column in df.columns]) and (
            not any(df["Bayesian_z"].isna())
        )
        self.Bayesian = Bayesian

        df["D_max_significance"] = df["D_max"] / df["D_max_std"]
        df["rho_Ac_abs"] = np.abs(df["rho_Ac"])
        df["variance_scaling"] = compute_variance_scaling(df, phi_string="phi")

        if Bayesian:
            df["Bayesian_D_max_significance"] = (
                df["Bayesian_D_max"] / df["Bayesian_D_max_std"]
            )
            df["Bayesian_rho_Ac_abs"] = np.abs(df["Bayesian_rho_Ac"])
            df["Bayesian_variance_scaling"] = compute_variance_scaling(
                df, phi_string="Bayesian_phi"
            )

            s1 = "Bayesian_D_max_confidence_interval_1_sigma_low"
            s2 = "Bayesian_D_max_confidence_interval_1_sigma_high"
            if s1 in df.columns and s2 in df.columns:
                df["Bayesian_D_max_CI_low"] = df[s1]
                df["Bayesian_D_max_CI_high"] = df[s2]

        df["D_max_CI_low"] = df["D_max"] - df["D_max_std"]
        df["D_max_CI_high"] = df["D_max"] + df["D_max_std"]

        log_columns = [
            "N_reads",
            "N_alignments",
            "lambda_LR",
            "phi",
            "k_sum_total",
            "N_sum_total",
        ]

        for column in log_columns:
            log_column = "log_" + column
            df.loc[:, log_column] = np.log10(1 + df[column])

        if np.isnan(df["asymmetry"]).all() and not "forward_A" in df.columns:
            self.forward_only = True
        else:
            self.forward_only = False

        self.df = df

        self.all_tax_ids = set(self.df["tax_id"].unique())
        self.all_tax_names = set(self.df["tax_name"].unique())  # if with_LCA else set()
        self.all_tax_ranks = set(self.df["tax_rank"].unique())  # if with_LCA else set()
        self.samples = list(self.df["sample"].unique())
        self.columns = list(self.df.columns)
        self.set_marker_size(variable="N_reads", function="sqrt", slider=30)

    def set_marker_size(self, variable="N_reads", function="sqrt", slider=30):

        d_functions = {
            "constant": np.ones_like,
            "linear": lambda x: x,
            "sqrt": np.sqrt,
            "log10": np.log10,
        }

        self.df.loc[:, "size"] = d_functions[function](self.df[variable])

        self.max_of_size = np.max(self.df["size"])
        self.marker_size = slider

    def filter(self, filters, *, rank=None):

        query = ""
        for column, filter in filters.items():

            if filter is None:
                continue

            elif column == "samples":
                query += f"(sample in {filter}) & "

            elif column == "sample":
                query += f"(sample == '{filter}') & "

            elif column == "tax_id":
                query += f"(tax_id == '{filter}') & "

            elif column == "tax_ids":
                query += f"(tax_id in {filter}) & "

            elif column == "tax_rank":
                query += f"(tax_rank == {filter}) & "

            elif column == "tax_ranks":
                query += f"(tax_rank in {filter}) & "

            elif column == "tax_name":
                query += f"(tax_name == {filter}) & "

            elif column == "tax_names":
                query += f"(tax_name in {filter}) & "

            elif column == "tax_path":
                rank = filter

            else:
                low, high = filter
                if viz_utils.is_log_transform_column(column):
                    low = viz_utils.log_transform_slider(low)
                    high = viz_utils.log_transform_slider(high)
                query += f"({low} <= {column} <= {high}) & "

        query = query[:-2]
        # print(query)

        df_out = self.df.query(query)

        if rank is not None:
            mask = df_out["tax_path"].str.lower().str.contains(rank.lower())
            df_out = df_out.loc[mask]

        return df_out

    def filter_tax_path(self, rank):
        mask = self.df["tax_path"].str.contains(rank)
        return self.df.loc[mask]

    def _set_cmap(self):
        # https://plotly.com/python/discrete-color/#color-sequences-in-plotly-express
        # blue, orange, green, red, purple, brown, pink, grey, camouflage, turquoise
        # cmap = px.colors.qualitative.D3
        # cmap taken from http://www.cookbook-r.com/Graphs/Colors_%28ggplot2%29/
        cmap = [
            "#0072B2",
            "#D55E00",
            "#009E73",
            "#CC79A7",
            "#E69F00",
            "#56B4E9",
            "#F0E442",
        ]
        N_cmap = len(cmap)

        groupby = self.df.groupby("sample", sort=False)

        symbol_counter = 0
        d_cmap = {}
        d_symbols = {}
        markers = ["o", "s", "^", "v", "<", ">", "d"]
        d_markers = {}
        for i, (name, _) in enumerate(groupby):

            if (i % N_cmap) == 0 and i != 0:
                symbol_counter += 1

            d_cmap[name] = cmap[i % N_cmap]
            d_symbols[name] = symbol_counter % 44  # max Plotly symbol number
            d_markers[name] = markers[symbol_counter % len(markers)]

        self.cmap = cmap
        self.d_cmap = d_cmap
        self.d_symbols = d_symbols
        self.d_markers = d_markers

        self.d_cmap_fit = {"Forward": cmap[0], "Reverse": cmap[3], "Fit": cmap[2]}

    def _set_hover_info(self):

        placeholder = "_XXX_"

        self.custom_data_columns = [
            "sample",
            "tax_name",
            "tax_rank",
            "tax_id",
            # Bayesian Fits
            # Frequentist fits
            "lambda_LR",
            "D_max",
            "D_max_std",
            "q",
            "q_std",
            "phi",
            "phi_std",
            "asymmetry",
            "rho_Ac",
            # Counts
            "N_reads",
            "N_alignments",
            "N_sum_total",
            "k_sum_total",
        ]

        custom_data_columns_Bayesian = [
            "Bayesian_z",
            "Bayesian_D_max",
            "Bayesian_D_max_std",
            "Bayesian_q",
            "Bayesian_q_std",
            "Bayesian_phi",
            "Bayesian_phi_std",
            "Bayesian_rho_Ac",
        ]

        self.hovertemplate = (
            "<b>%{customdata[_XXX_]}</b><br><br>"
            "<b>Tax</b>: <br>"
            "    Name: %{customdata[_XXX_]} <br>"
            "    Rank: %{customdata[_XXX_]} <br>"
            "    ID:   %{customdata[_XXX_]} <br><br>"
            "<b>MAP results</b>: <br>"
            "    LR:       %{customdata[_XXX_]:9.2f} <br>"
            "    D max:    %{customdata[_XXX_]:9.2f} ± %{customdata[_XXX_]:.2f} <br>"
            "    q:        %{customdata[_XXX_]:9.2f} ± %{customdata[_XXX_]:.2f} <br>"
            "    phi:      %{customdata[_XXX_]:.3s} ± %{customdata[_XXX_]:.3s} <br>"
            "    asymmetry:%{customdata[_XXX_]:9.3f} <br>"
            "    rho_Ac:   %{customdata[_XXX_]:9.3f} <br><br>"
            "<b>Counts</b>: <br>"
            "    N reads:     %{customdata[_XXX_]:.3s} <br>"
            "    N alignments:%{customdata[_XXX_]:.3s} <br>"
            "    N sum total: %{customdata[_XXX_]:.3s} <br>"
            "    k sum total: %{customdata[_XXX_]:.3s} <br>"
            "<extra></extra>"
        )

        hovertemplate_Bayesian = (
            "<b>Fit results</b>: <br>"
            "    z:        %{customdata[_XXX_]:9.2f} <br>"
            "    D max:    %{customdata[_XXX_]:9.2f} ± %{customdata[_XXX_]:.2f} <br>"
            "    q:        %{customdata[_XXX_]:9.2f} ± %{customdata[_XXX_]:.2f} <br>"
            "    phi:      %{customdata[_XXX_]:.3s} ± %{customdata[_XXX_]:.3s} <br>"
            "    rho_Ac:   %{customdata[_XXX_]:9.3f} <br><br>"
        )

        if self.forward_only:
            index = self.hovertemplate.find("<b>MAP results</b>: <br>")
            self.hovertemplate = (
                self.hovertemplate[:index]
                + "<b>Forward only! </b><br><br>"
                + self.hovertemplate[index:]
            )

        # if Bayesian fits, include these results
        if self.Bayesian:
            index = self.custom_data_columns.index("lambda_LR")
            self.custom_data_columns[index:index] = custom_data_columns_Bayesian

            index = self.hovertemplate.find("<b>MAP results</b>: <br>")
            self.hovertemplate = (
                self.hovertemplate[:index]
                + hovertemplate_Bayesian
                + self.hovertemplate[index:]
            )

        # fill in the templates with data
        data_counter = 0
        i = 0
        while True:
            if self.hovertemplate[i : i + len(placeholder)] == placeholder:
                # break
                s_new = self.hovertemplate[:i]
                s_new += str(data_counter)
                s_new += self.hovertemplate[i + len(placeholder) :]
                self.hovertemplate = s_new
                data_counter += 1
            i += 1
            if i >= len(self.hovertemplate):
                break

        # if not self.with_LCA:
        #     self.custom_data_columns = remove_LCA_columns(self.custom_data_columns)
        # self.customdata = self.df[self.custom_data_columns]
        self.hovertemplate_fit = (
            "Fit: <br>D(x) = %{y:.3f} ± %{error_y.array:.3f}<br>" "<extra></extra>"
        )

    def parse_click_data(self, click_data, column):
        try:
            index = self.custom_data_columns.index(column)
            value = click_data["points"][0]["customdata"][index]
            return value

        except Exception as e:
            raise e

    def get_single_count_group(self, sample, tax_id, forward_reverse=""):
        query = f"sample == '{sample}' & tax_id == '{tax_id}'"
        group_wide = self.df.query(query)
        group = wide_to_long_df(group_wide)

        if forward_reverse.lower() == "forward":
            return group.query(f"direction=='Forward'")
        elif forward_reverse.lower() == "reverse":
            return group.query(f"direction=='Reverse'")
        else:
            return group

    def get_single_fit_prediction(self, sample, tax_id, forward_reverse=""):
        query = f"sample == '{sample}' & tax_id == '{tax_id}'"
        ds = self.df.query(query)
        if len(ds) != 1:
            raise AssertionError(f"Something wrong here, got: {ds}")

        if self.forward_only:
            if forward_reverse.lower() == "reverse":
                return "FORWARD ONLY"
            else:
                forward_reverse = ""

        group = self.get_single_count_group(sample, tax_id, forward_reverse)

        if forward_reverse.lower() == "forward":
            prefix = "forward_"
        elif forward_reverse.lower() == "reverse":
            prefix = "reverse_"
        else:
            if self.Bayesian:
                prefix = "Bayesian_"
            else:
                prefix = ""

        A = getattr(ds, f"{prefix}A").values
        q = getattr(ds, f"{prefix}q").values
        c = getattr(ds, f"{prefix}c").values
        phi = getattr(ds, f"{prefix}phi").values

        max_position = viz_utils.get_max_position_from_group(group)

        abs_x = group["|x|"].values[:max_position]
        N = group["N"].values[:max_position]

        Dx = A * (1 - q) ** (abs_x - 1) + c

        alpha = Dx * phi
        beta = (1 - Dx) * phi

        dist = sp_betabinom(n=N, a=alpha, b=beta)

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            std = dist.std() / N

        std[np.isnan(std)] = 0

        text = self._ds_to_fit_text(ds)

        d_out = {"mu": Dx, "std": std, "Dx": Dx, "|x|": abs_x, "text": text}

        return d_out

    def get_D_max(self, sample, tax_id):
        query = f"sample == '{sample}' & tax_id == '{tax_id}'"
        ds = self.df.query(query)

        if len(ds) != 1:
            s = (
                f"Something wrong here, ds should be of length 1, got {len(ds)}"
                + f"{ds}"
            )
            raise AssertionError(s)

        if self.Bayesian:
            prefix = "Bayesian_"
        else:
            prefix = ""

        D_max = ds[f"{prefix}D_max"].iloc[0]

        s1 = "Bayesian_D_max_confidence_interval_1_sigma_low"
        s2 = "Bayesian_D_max_confidence_interval_1_sigma_high"
        if s1 in ds and s2 in ds:
            D_max_low = ds[s1].iloc[0]
            D_max_high = ds[s2].iloc[0]
        else:
            std = ds[f"{prefix}D_max_std"].iloc[0]
            D_max_low = D_max - std
            D_max_high = D_max + std

        return D_max, D_max_low, D_max_high

    def _ds_to_fit_text(self, ds):

        d_columns_latex = viz_utils.get_d_columns_latex(self)[0]

        sanitize = (
            lambda s: d_columns_latex[s]
            .strip(r"$")
            .replace(r"\text{(MAP)}", r"")
            .replace(r"\text", r"\mathrm")
        )

        text = r"$\mathrm{Bayesian}" if self.Bayesian else r"$\mathrm{MAP}"
        text += r"\,\, \mathrm{fit}$" + "\n\n"

        D_max_col = "Bayesian_D_max" if self.Bayesian else "D_max"
        D_max_str = sanitize(D_max_col)
        D_max = ds[D_max_col].iloc[0]
        D_max_std = ds[D_max_col + "_std"].iloc[0]
        text += (
            "$" + D_max_str + f" = {D_max:.3f} " + r"\pm" + f" {D_max_std:.3f}" + r"$"
        )
        text += "\n"

        fitqual_col = "Bayesian_z" if self.Bayesian else "lambda_LR"
        fitqual_str = sanitize(fitqual_col)
        fitqual = ds[fitqual_col].iloc[0]
        text += "$" + fitqual_str + f" = {fitqual:.2f} " + r"$"
        text += "\n"

        phi_col = "Bayesian_phi" if self.Bayesian else "phi"
        phi_str = sanitize(phi_col)
        phi = viz_utils.human_format(ds[phi_col].iloc[0])
        phi_std = viz_utils.human_format(ds[phi_col + "_std"].iloc[0])
        text += "$" + phi_str + f" = {phi} " + r"\pm" + f" {phi_std}" + r"$"
        text += "\n"

        q_col = "Bayesian_q" if self.Bayesian else "q"
        q_str = sanitize(q_col)
        q = ds[q_col].iloc[0]
        q_std = ds[q_col + "_std"].iloc[0]
        text += "$" + q_str + f" = {q:.2f} " + r"\pm" + f" {q_std:.2f}" + r"$"
        # text += "\n"

        return text
