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




if __name__ == '__main__':
    # Plot TTU
    get_coding_alignment(metric="ttu")

    # get_coding_alignment(metric="video_length_in_s")#TODO

    # # Plot DOU
    # get_coding_alignment(metric="dou")