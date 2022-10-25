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

    df = (
        df.sort_values(
            ["sample_rank", "N_reads"],
            ascending=[True, False],
        )
        .drop(columns="sample_rank")
        .reset_index(drop=True)
    )

    return df


def pd_wide_to_long_forward_only(group_wide, sep, direction):
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

    group_long_forward = pd_wide_to_long_forward_only(
        group_wide,
        sep="+",
        direction="Forward",
    )

    try:
        group_long_reverse = pd_wide_to_long_forward_only(
            group_wide,
            sep="-",
            direction="Reverse",
        )

        group_long = pd.concat([group_long_forward, group_long_reverse])

    # happens when forward only
    except ValueError:
        group_long = group_long_forward

    group_long["sample"] = group_wide["sample"].iloc[0]

    return group_long


def correct_for_non_LCA(df):
    if "N_alignments" in df.columns:
        df["N_alignments"] = df["N_alignments"].fillna(np.nan)
    else:
        df["N_alignments"] = np.nan

    if "tax_name" in df.columns:
        df["tax_name"] = df["tax_name"].fillna("NO TAX NAME")
    else:
        df["tax_name"] = "NO TAX NAME"

    if "tax_rank" in df.columns:
        df["tax_rank"] = df["tax_rank"].fillna("NO TAX RANK")
    else:
        df["tax_rank"] = "NO TAX RANK"

    if "tax_path" in df.columns:
        df["tax_path"] = df["tax_path"].fillna("NO TAX PATH")
    else:
        df["tax_path"] = "NO TAX PATH"

    return df


#%%


def add_MAP_measures(df):
    df["MAP_rho_Ac_abs"] = np.abs(df["MAP_rho_Ac"])
    df["MAP_damage_CI_low"] = df["MAP_damage"] - df["MAP_damage_std"]
    df["MAP_damage_CI_high"] = df["MAP_damage"] + df["MAP_damage_std"]


def add_bayesian_measures(df):
    df["rho_Ac_abs"] = np.abs(df["rho_Ac"])
    df["damage_CI_low"] = df["damage_CI_1_sigma_low"]
    df["damage_CI_high"] = df["damage_CI_1_sigma_high"]


#%%


class VizResults:
    def __init__(self, results_dir):
        self.results_dir = Path(results_dir)
        self._load_df_results()
        self._set_cmap()
        self._set_hover_info()

    def _load_parquet_file(self, results_dir):
        # df = pd.read_parquet(results_dir)
        dfs = []
        for path in results_dir.glob("*.parquet"):
            dfs.append(pd.read_parquet(path))
        df = pd.concat(dfs, ignore_index=True)
        return correct_for_non_LCA(df)

    def _load_df_results(self):
        df = self._load_parquet_file(self.results_dir)
        df = sort_dataframe(df)

        # force tax_id to be categorical strings.
        # XXX remove in final version
        df["tax_id"] = df["tax_id"].astype("str").astype("category")

        add_MAP_measures(df)

        if "damage" in df.columns and (not any(df["damage"].isna())):
            self.Bayesian = True
            add_bayesian_measures(df)
        else:
            self.Bayesian = False

        log_columns = [
            "N_reads",
            "N_alignments",
            "MAP_phi",
            "k_sum_total",
            "N_sum_total",
        ]
        if self.Bayesian:
            log_columns.append("phi")

        for column in log_columns:
            log_column = "log_" + column
            df.loc[:, log_column] = np.log10(1 + df[column])

        if np.isnan(df["k-1"]).any():
            self.contains_forward_only = True
            if "k-1" in df.columns:
                df["forward_only"] = df["k-1"].isna()
                df["forward_only_str"] = np.where(
                    df["forward_only"], "Forward only!", ""
                )
            else:
                df["forward_only"] = True
                df["forward_only_str"] = "Forward only!"

        else:
            self.contains_forward_only = False
            df["forward_only"] = False
            df["forward_only_str"] = ""

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
        # cmap = [
        #     "#0072B2",
        #     "#D55E00",
        #     "#009E73",
        #     "#CC79A7",
        #     "#E69F00",
        #     "#56B4E9",
        #     "#F0E442",
        # ]
        cmap = [
            "#3BA0E7",
            "#E7554C",
            "#00B050",
            "#b36fb5",
            "#c0c0c0",
            "#FFC000",
            "#9f99c8",
        ]

        N_cmap = len(cmap)

        groupby = self.df.groupby("sample", sort=False)

        symbol_counter = 0
        d_cmap = {}
        d_symbols = {}
        markers = ["o", "s", "^", "v", "<", ">", "damage"]
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

        self.d_cmap_fit = {
            "Forward": cmap[0],
            "Reverse": cmap[1],
            "Fit": cmap[2],
        }

    def _set_hover_info(self):

        placeholder = "_XXX_"

        self.custom_data_columns = [
            "sample",
            "tax_name",
            "tax_rank",
            "tax_id",
            # Bayesian Fits
            # Frequentist fits
            "MAP_damage",
            "MAP_damage_std",
            "MAP_significance",
            "MAP_q",
            "MAP_q_std",
            "MAP_phi",
            "MAP_phi_std",
            "MAP_rho_Ac",
            # Counts
            "N_reads",
            "N_alignments",
            "N_sum_total",
            "k_sum_total",
        ]

        custom_data_columns_Bayesian = [
            "damage",
            "damage_std",
            "significance",
            "q",
            "q_std",
            "phi",
            "phi_std",
            "rho_Ac",
        ]

        self.hovertemplate = (
            "<b>%{customdata[_XXX_]}</b><br><br>"
            "<b>Tax</b>: <br>"
            "    Name: %{customdata[_XXX_]} <br>"
            "    Rank: %{customdata[_XXX_]} <br>"
            "    ID:   %{customdata[_XXX_]} <br><br>"
            "<b>MAP results</b>: <br>"
            "    D:             %{customdata[_XXX_]:6.2%} ± %{customdata[_XXX_]:.2%} <br>"
            "    significance: %{customdata[_XXX_]:6.2f} <br>"
            "    q:            %{customdata[_XXX_]:6.2f}  ± %{customdata[_XXX_]:.2f} <br>"
            "    phi:            %{customdata[_XXX_]:.3s} ± %{customdata[_XXX_]:.3s} <br>"
            "    corr. Ac:      %{customdata[_XXX_]:6.3f} <br><br>"
            "<b>Counts</b>: <br>"
            "    N reads:      %{customdata[_XXX_]:6.3s} <br>"
            "    N alignments: %{customdata[_XXX_]:6.3s} <br>"
            "    N sum total:  %{customdata[_XXX_]:6.3s} <br>"
            "    k sum total:  %{customdata[_XXX_]:6.3s} <br>"
            "<extra></extra>"
        )

        hovertemplate_Bayesian = (
            "<b>Fit results</b>: <br>"
            "    D:             %{customdata[_XXX_]:6.2%} ± %{customdata[_XXX_]:.2%} <br>"
            "    significance: %{customdata[_XXX_]:6.2f} <br>"
            "    q:            %{customdata[_XXX_]:6.2f}  ± %{customdata[_XXX_]:.2f} <br>"
            "    phi:            %{customdata[_XXX_]:.3s} ± %{customdata[_XXX_]:.3s} <br>"
            "    corr. Ac:      %{customdata[_XXX_]:6.3f} <br><br>"
        )

        if self.contains_forward_only:
            index = self.custom_data_columns.index("MAP_damage")
            self.custom_data_columns[index:index] = ["forward_only_str"]

            index = self.hovertemplate.find("<b>MAP results</b>: <br>")
            self.hovertemplate = (
                self.hovertemplate[:index]
                + "<b>%{customdata[_XXX_]}</b><br><br>"
                + self.hovertemplate[index:]
            )

        # if Bayesian fits, include these results
        if self.Bayesian:
            index = self.custom_data_columns.index("MAP_damage")
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

    def get_single_count_group(self, sample, tax_id, forward_only=False):
        query = f"sample == '{sample}' & tax_id == '{tax_id}'"
        group_wide = self.df.query(query)
        group = wide_to_long_df(group_wide).dropna(axis="rows")

        if forward_only:
            return group.query(f"direction=='Forward'")
        else:
            return group

    def get_single_fit_prediction(self, sample, tax_id, forward_only=False):
        query = f"sample == '{sample}' & tax_id == '{tax_id}'"
        ds = self.df.query(query)
        if len(ds) != 1:
            raise AssertionError(f"Something wrong here, got: {ds}")

        group = self.get_single_count_group(sample, tax_id, forward_only)

        if len(group) == 0:
            raise AssertionError(
                f"Something wrong here, got: {group=}, {tax_id=}, {forward_only=}"
            )

        if self.Bayesian:
            prefix = ""
        else:
            prefix = "MAP_"

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

    def get_D(self, sample, tax_id):
        query = f"sample == '{sample}' & tax_id == '{tax_id}'"
        ds = self.df.query(query)

        if len(ds) != 1:
            s = (
                f"Something wrong here, ds should be of length 1, got {len(ds)}"
                + f"{ds}"
            )
            raise AssertionError(s)

        if self.Bayesian:
            prefix = ""
        else:
            prefix = "MAP_"

        D = ds[f"{prefix}damage"].iloc[0]

        s1 = f"{prefix}damage_CI_low"
        s2 = f"{prefix}damage_CI_high"
        D_low = ds[s1].iloc[0]
        D_high = ds[s2].iloc[0]

        return D, D_low, D_high

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

        D_col = "damage" if self.Bayesian else "MAP_damage"
        D_str = sanitize(D_col)
        D = ds[D_col].iloc[0]
        D_std = ds[D_col + "_std"].iloc[0]
        text += "$" + D_str + f" = {D:.3f} " + r"\pm" + f" {D_std:.3f}" + r"$"
        text += "\n"

        fitqual_col = "significance" if self.Bayesian else "MAP_significance"
        fitqual_str = sanitize(fitqual_col)
        fitqual = ds[fitqual_col].iloc[0]
        text += "$" + fitqual_str + f" = {fitqual:.2f} " + r"$"
        text += "\n"

        phi_col = "phi" if self.Bayesian else "MAP_phi"
        phi_str = sanitize(phi_col)
        phi = viz_utils.human_format(ds[phi_col].iloc[0])
        phi_std = viz_utils.human_format(ds[phi_col + "_std"].iloc[0])
        text += "$" + phi_str + f" = {phi} " + r"\pm" + f" {phi_std}" + r"$"
        text += "\n"

        q_col = "q" if self.Bayesian else "MAP_q"
        q_str = sanitize(q_col)
        q = ds[q_col].iloc[0]
        q_std = ds[q_col + "_std"].iloc[0]
        text += "$" + q_str + f" = {q:.2f} " + r"\pm" + f" {q_std:.2f}" + r"$"
        # text += "\n"

        return text
