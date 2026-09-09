import plotly.express as px
from matplotlib import pyplot as plt
import pandas as pd

from HelperFunctions.codings.compare_codings import get_both_codings


def get_coding_alignment(metric="ttu"):
    """
    Creates a scatter plot comparing coding results between Coder 1 and Coder 2.
    Each participant is shown in a different color.

    Parameters:
        metric (str): "ttu" for Time to Understand, "dou" for Degree of Understanding
    """
    id, ttu, dou, ttu_secondCoder, dou_secondCoder = get_both_codings()

    # Create DataFrame
    df = pd.DataFrame({
        'participant': [i.split('_')[0] for i in id],
        'task': [int(i.split('_')[1]) for i in id],
        'ttu_coder1': ttu,
        'ttu_coder2': ttu_secondCoder,
        'dou_coder1': dou,
        'dou_coder2': dou_secondCoder
    })

    # Get unique participants and assign colors
    participants = sorted(df['participant'].unique())
    colors = px.colors.qualitative.Dark24

    # Select data based on metric
    if metric.lower() not in ["ttu", "dou"]:
        raise ValueError("metric must be 'ttu' or 'dou'")

    x_data = df[f'{metric.lower()}_coder1']
    y_data = df[f'{metric.lower()}_coder2']
    xlabel = f"{metric.upper()} (Coder 1)"
    ylabel = f"{metric.upper()} (Coder 2)"
    if metric.lower() == "ttu":
        xlabel += " [s]"
        ylabel += " [s]"

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 8))

    # Plot each participant with unique color
    for i, part in enumerate(participants):
        data = df[df['participant'] == part]
        # filter out data:
        # data = data[data[x_data.name] <= 2000]

        ax.scatter(
            data[x_data.name], data[y_data.name],
            color=colors[i], label=part, alpha=0.5, s=60
        )

    # Perfect agreement line
    min_val = min(x_data.min(), y_data.min())
    max_val = max(x_data.max(), y_data.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=1, label='Perfect Agreement')

    # Labels and grid
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)

    if metric == "ttu":
        ax.set_xlim(0,350)
        ax.set_ylim(0,350)

    plt.tight_layout(rect=[0, 0, 0.95, 1])  # Make room for legend
    plt.savefig(f"{metric.lower()}_coding_alignment.png")
    plt.show()
    return fig




import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

def get_coding_alignment_plotly(metric: str = "ttu") -> go.Figure:
    """
    Creates an interactive Plotly scatter plot that compares coding results
    between Coder 1 and Coder 2.  Each participant is shown in a distinct colour
    and the hover tooltip displays the participant‑id, task‑id and the two
    metric values.

    Parameters
    ----------
    metric : {"ttu", "dou"}
        * ``"ttu"`` – Time‑to‑Understand (seconds)
        * ``"dou"`` – Degree‑of‑Understanding (rating)

    Returns
    -------
    plotly.graph_objects.Figure
        The interactive figure.  It is also saved as ``{metric}_coding_alignment.html``.
    """
    # ------------------------------------------------------------------ #
    # 1️⃣  Load the raw data (same helper you already have)
    # ------------------------------------------------------------------ #
    # NOTE: ``get_both_codings`` must be defined elsewhere in your code base.
    # It should return five parallel lists:
    #   id, ttu, dou, ttu_secondCoder, dou_secondCoder
    id_list, ttu, dou, ttu_secondCoder, dou_secondCoder = get_both_codings()

    # ------------------------------------------------------------------ #
    # 2️⃣  Build a tidy DataFrame
    # ------------------------------------------------------------------ #
    df = pd.DataFrame({
        "participant": [i.split("_")[0] for i in id_list],
        "task":        [int(i.split("_")[1]) for i in id_list],
        "ttu_coder1":  ttu,
        "ttu_coder2":  ttu_secondCoder,
        "dou_coder1":  dou,
        "dou_coder2":  dou_secondCoder,
    })

    # ------------------------------------------------------------------ #
    # 3️⃣  Validate the metric argument
    # ------------------------------------------------------------------ #
    metric = metric.lower()
    if metric not in {"ttu", "dou"}:
        raise ValueError("metric must be either 'ttu' or 'dou'")

    x_col = f"{metric}_coder1"
    y_col = f"{metric}_coder2"

    # ------------------------------------------------------------------ #
    # 4️⃣  Plotly scatter – colour by participant
    # ------------------------------------------------------------------ #
    palette = px.colors.qualitative.Dark24

    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color="participant",
        color_discrete_sequence=palette,
        hover_data=["participant", "task", x_col, y_col],
        labels={
            x_col: f"{metric.upper()} (Coder 1){' [s]' if metric == 'ttu' else ''}",
            y_col: f"{metric.upper()} (Coder 2){' [s]' if metric == 'ttu' else ''}",
        },
        title=f"Coding alignment – {metric.upper()}",
        width=800,
        height=800,
    )

    # ------------------------------------------------------------------ #
    # 5️⃣  Add the perfect‑agreement line (y = x)
    # ------------------------------------------------------------------ #
    # Determine the limits that encompass all points (plus a little margin)
    min_val = min(df[x_col].min(), df[y_col].min())
    max_val = max(df[x_col].max(), df[y_col].max())

    # If you are dealing with TTU you may want to clamp the axis to 0‑350 as
    # you did in the Matplotlib version.
    if metric == "ttu":
        min_val, max_val = 0, 350

    fig.add_shape(
        type="line",
        x0=min_val,
        y0=min_val,
        x1=max_val,
        y1=max_val,
        line=dict(color="red", dash="dash", width=1),
        name="Perfect Agreement",
    )

    # ------------------------------------------------------------------ #
    # 6️⃣  Axis configuration
    # ------------------------------------------------------------------ #
    fig.update_xaxes(range=[min_val, max_val], title_font=dict(size=14))
    fig.update_yaxes(range=[min_val, max_val], title_font=dict(size=14))
    fig.update_layout(
        legend=dict(
            title_text="Participant",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            font=dict(size=10),
        ),
        margin=dict(l=60, r=200, t=80, b=60),  # give space for the legend
        hovermode="closest",
        template="simple_white",
    )

    # ------------------------------------------------------------------ #
    # 7️⃣  Save the interactive figure (HTML) – optional PNG export
    # ------------------------------------------------------------------ #
    out_html = Path(f"{metric}_coding_alignment.html")
    fig.write_html(str(out_html), include_plotlyjs="cdn")
    # If you also want a static PNG you can use kaleido (pip install -U kaleido)
    # fig.write_image(f"{metric}_coding_alignment.png", scale=2)

    # ------------------------------------------------------------------ #
    # 8️⃣  Return the figure for further manipulation / inline display
    # ------------------------------------------------------------------ #
    fig.write_html(f"{metric}_coding_alignment.html", include_plotlyjs="cdn")
    return fig



if __name__ == '__main__':
    # Plot TTU
    # get_coding_alignment(metric="ttu")

    get_coding_alignment_plotly(metric="ttu")


    # Plot DOU
    # get_coding_alignment(metric="dou")
    get_coding_alignment_plotly(metric="dou")