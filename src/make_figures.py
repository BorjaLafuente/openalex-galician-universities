"""
Step 5 of the pipeline - Figures: turn the indicator tables in results/ into
the charts used in the README.

Reads the CSV files written by run_queries.py and saves one PNG per indicator
in figures/.

Run from the project root:  python src/make_figures.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

RESULTS_DIR = Path("results")
FIG_DIR = Path("figures")

# --- Style -------------------------------------------------------------------
# Corporate colours of each university (R names: deeppink3, dodgerblue3,
# darkgreen). Checked for colour-blind safety: dodgerblue3 is used instead of
# dodgerblue4, which is hard to tell apart from deeppink3 with red-green
# colour blindness. Each university keeps the same colour in every chart.
UNI_COLORS = {"UDC": "#CD1076", "USC": "#1874CD", "UVIGO": "#006400"}
UNIVERSITIES = list(UNI_COLORS)

# Pairs of universities are different entities, so they get their own colours,
# clearly different from the university colours
PAIR_COLORS = {"UDC–USC": "#4a3aa7", "UDC–UVIGO": "#eb6834", "USC–UVIGO": "#1baf7a"}

# Open access routes, from "most open" to closed; closed is a neutral grey
OA_ROUTES = {
    "gold": "#2a78d6",
    "diamond": "#eb6834",
    "hybrid": "#1baf7a",
    "bronze": "#eda100",
    "green": "#e87ba4",
    "closed": "#c9c8c3",
}

SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.size": 10,
    "text.color": TEXT_PRIMARY,
    "axes.labelcolor": TEXT_SECONDARY,
    "xtick.color": TEXT_SECONDARY,
    "ytick.color": TEXT_SECONDARY,
    "axes.edgecolor": GRID,
    "legend.frameon": False,
})


# --- Helpers -----------------------------------------------------------------

def style_axes(ax):
    """Recessive axes: no top/right frame, light horizontal grid behind the data."""
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def add_titles(fig, title, subtitle):
    """Left-aligned title and a one-line subtitle explaining what is shown."""
    fig.text(0.01, 0.98, title, fontsize=13, fontweight="bold", va="top")
    fig.text(0.01, 0.92, subtitle, fontsize=9.5, color=TEXT_SECONDARY, va="top")


def label_line_ends(ax, ends, min_gap=11):
    """Direct labels just right of the last point of each line (in text colour).

    ends: list of (x, y, text), one per line. When two lines end at similar
    values, their labels would overlap, so labels are pushed apart vertically
    until they are at least min_gap points away from each other (similar to
    ggrepel in R). Each label stays as close as possible to its own line.
    """
    # Convert each end point from data units to points on the page, because
    # the minimum gap is a text size (points), not a data value.
    to_points = 72 / ax.figure.dpi
    positions = []
    for x, y, text in ends:
        _, y_pixels = ax.transData.transform((x, y))
        positions.append([y_pixels * to_points, x, y, text])

    # Go from the lowest label upwards: if a label is too close to the one
    # below it, move it up just enough.
    positions.sort()
    for i in range(1, len(positions)):
        lowest_allowed = positions[i - 1][0] + min_gap
        if positions[i][0] < lowest_allowed:
            positions[i][0] = lowest_allowed

    # Re-centre the group, so labels are spread around the lines rather than
    # all pushed upwards.
    original = [ax.transData.transform((x, y))[1] * to_points for _, x, y, _ in positions]
    shift = (sum(original) - sum(p[0] for p in positions)) / len(positions)

    for (label_y, x, y, text), line_y in zip(positions, original):
        offset = label_y + shift - line_y  # vertical offset in points
        ax.annotate(text, xy=(x, y), xytext=(6, offset), textcoords="offset points",
                    va="center", fontsize=9, color=TEXT_PRIMARY)


def save(fig, name):
    path = FIG_DIR / name
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {path}")


def line_chart(df, x, y, series_col, colors, title, subtitle, ylabel,
               filename, provisional_last_year=False, note=None):
    """One line per series, with legend and direct labels at the line ends."""
    fig, ax = plt.subplots(figsize=(8, 4.8))
    fig.subplots_adjust(top=0.76)

    ends = []  # last point of each line, labelled once the axes are final
    for name, color in colors.items():
        d = df[df[series_col] == name].sort_values(x)
        if d.empty:
            continue
        if provisional_last_year and len(d) > 1:
            # Solid line up to the second-to-last year, dashed to the last one
            ax.plot(d[x].iloc[:-1], d[y].iloc[:-1], color=color, linewidth=2,
                    marker="o", markersize=4, label=name)
            ax.plot(d[x].iloc[-2:], d[y].iloc[-2:], color=color, linewidth=2,
                    linestyle="--", marker="o", markersize=4)
        else:
            ax.plot(d[x], d[y], color=color, linewidth=2, marker="o",
                    markersize=4, label=name)
        ends.append((d[x].iloc[-1], d[y].iloc[-1], name))

    style_axes(ax)
    ax.set_ylabel(ylabel)
    ax.set_xticks(sorted(df[x].unique()))
    ax.set_ylim(bottom=0)
    ax.margins(x=0.08)
    # Labels go after the axis limits are set, because their spacing is
    # computed from the final position of each line end on the page.
    label_line_ends(ax, ends)
    # Legend above the plot area, so it never covers the data
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.02), ncols=len(colors),
              borderaxespad=0, handlelength=1.8)
    add_titles(fig, title, subtitle)
    if note:
        fig.text(0.01, -0.02, note, fontsize=8.5, color=TEXT_SECONDARY, va="top")
    save(fig, filename)


# --- Figures -----------------------------------------------------------------

def fig_output():
    df = pd.read_csv(RESULTS_DIR / "01_output_by_year.csv")
    line_chart(
        df, "year", "articles_reviews", "university", UNI_COLORS,
        title="Research output",
        subtitle="Articles and reviews per year (full counting)",
        ylabel="Publications",
        filename="01_output.png",
    )


def fig_open_access_routes():
    df = pd.read_csv(RESULTS_DIR / "03_open_access_by_route.csv")
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.8), sharey=True)
    fig.subplots_adjust(top=0.72, wspace=0.12)

    for ax, uni in zip(axes, UNIVERSITIES):
        d = df[df["university"] == uni].sort_values("year")
        ax.stackplot(
            d["year"],
            [d[f"pct_{route}"] for route in OA_ROUTES],
            colors=list(OA_ROUTES.values()),
            labels=[route.capitalize() for route in OA_ROUTES],
            edgecolor=SURFACE, linewidth=1,  # thin gap between the layers
        )
        style_axes(ax)
        ax.set_title(uni, loc="left", fontsize=11, fontweight="bold")
        ax.set_xlim(d["year"].min(), d["year"].max())
        ax.set_ylim(0, 100)
        ax.set_xticks([2016, 2020, 2024])  # inner ticks, so labels of adjacent panels never touch

    axes[0].set_ylabel("% of articles and reviews")
    # Legend in the same order as the layers, top layer first
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles[::-1], labels[::-1], loc="upper left", ncols=6,
               bbox_to_anchor=(0.005, 0.87), fontsize=9, handlelength=1.4)
    add_titles(fig, "Open access by route",
               "Share of articles and reviews by open access route (OpenAlex classification)")
    save(fig, "02_open_access_routes.png")


def fig_international():
    df = pd.read_csv(RESULTS_DIR / "04_international_collaboration.csv")
    line_chart(
        df, "year", "pct_int_art_rev", "university", UNI_COLORS,
        title="International collaboration",
        subtitle="% of articles and reviews with authors from more than one country",
        ylabel="% of articles and reviews",
        filename="03_international_collaboration.png",
    )


def fig_impact():
    df = pd.read_csv(RESULTS_DIR / "05_citation_impact.csv")
    line_chart(
        df, "year", "pct_top10", "university", UNI_COLORS,
        title="Citation impact",
        subtitle="% of articles and reviews in the 10% most cited of their field and year",
        ylabel="% in top 10%",
        filename="04_citation_impact.png",
        provisional_last_year=True,
        note=("OpenAlex indicators: valid for comparing the three universities, not as absolute "
              "levels (about twice CWTS Leiden Ranking values).\nDashed: last year, short "
              "citation window."),
    )


def fig_galician_collaboration():
    df = pd.read_csv(RESULTS_DIR / "06_galician_collaboration.csv")
    df["pair"] = df["uni_a"] + "–" + df["uni_b"]
    line_chart(
        df, "year", "n_shared", "pair", PAIR_COLORS,
        title="Collaboration between Galician universities",
        subtitle="Articles and reviews co-authored by each pair of universities",
        ylabel="Shared publications",
        filename="05_galician_collaboration.png",
    )


def main():
    FIG_DIR.mkdir(exist_ok=True)
    fig_output()
    fig_open_access_routes()
    fig_international()
    fig_impact()
    fig_galician_collaboration()


if __name__ == "__main__":
    main()
