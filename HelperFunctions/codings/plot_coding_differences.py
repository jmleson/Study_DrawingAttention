import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from HelperFunctions.codings.compare_codings import get_both_codings


def plot_coding_differences(metric="ttu", filename="coding_difference.html", title=""):
    """
    Plots the difference (Coder 2 - Coder 1) per participant across all tasks.

    Parameters:
        metric (str): "ttu" or "dou"
        filename (str): Output HTML filename
        title (str): Custom title (e.g., "TTU: Difference between Coders")
    """
    # Step 1: Load data
    id, ttu, dou, ttu_secondCoder, dou_secondCoder = get_both_codings()

    # Create DataFrame
    if metric == "ttu":
        df = pd.DataFrame({
            'participant': [i.split('_')[0] for i in id],
            'task': [int(i.split('_')[1]) for i in id],
            'coder1': ttu,
            'coder2': ttu_secondCoder
        })
        y_label = "Difference (TTU: Coder 2 - Coder 1)"
        default_title = "TTU: Difference between Coders (Coder 2 - Coder 1)"
    elif metric == "dou":
        df = pd.DataFrame({
            'participant': [i.split('_')[0] for i in id],
            'task': [int(i.split('_')[1]) for i in id],
            'coder1': dou,
            'coder2': dou_secondCoder
        })
        y_label = "Difference (DOU: Coder 2 - Coder 1)"
        default_title = "DOU: Difference between Coders (Coder 2 - Coder 1)"
    else:
        raise ValueError("metric must be 'ttu' or 'dou'")

    # Use safe color palette (Dark24 = 24 colors)
    colors = px.colors.qualitative.Dark24

    # Create figure
    fig = go.Figure()

    # Add one line per participant
    for part in sorted(df['participant'].unique()):
        data = df[df['participant'] == part].sort_values('task')
        diff = data['coder2'] - data['coder1']

        # Extract last digit of participant ID as integer index
        last_char = part[-1]
        if last_char.isdigit():
            color_index = int(last_char) % len(colors)
        else:
            color_index = 0  # fallback

        fig.add_trace(go.Scatter(
            x=data['task'],
            y=diff,
            mode='lines+markers',
            name=f"{part}",
            line=dict(color=colors[color_index], width=2),
            marker=dict(size=6),
            hovertext=[f"Participant: {part}, Task: {t}, Diff: {d:.2f}"
                       for t, d in zip(data['task'], diff)],
            hoverinfo='text'
        ))

    # Update layout: full width, all tasks on x-axis, legend, title
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 19)),  # Tasks 1 to 18
            ticktext=[str(i) for i in range(1, 19)],
            title_text="Task",
            showgrid=True,
            gridcolor='lightgray',
            zeroline=False
        ),
        yaxis=dict(
            title_text=y_label,
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='gray',
            zerolinewidth=1
        ),
        hovermode='x unified',
        title_text=title or default_title,
        legend_title="Participant",
        showlegend=True,
        margin=dict(l=20, r=20, t=40, b=40),
        width=None,  # Let Plotly auto-scale to full width
        height=600,
        template="plotly_white"
    )

    # Save as HTML with full width
    fig.write_html(filename, include_plotlyjs='cdn', full_html=True, auto_open=False)
    print(f"✅ Plot saved as '{filename}' (full width, all tasks, legend included)")


# ----------------------------
# Final Call: Run the function
# ----------------------------
if __name__ == "__main__":
    # Plot TTU
    plot_coding_differences(
        metric="ttu",
        filename="ttu_coding_difference.html",
        title="TTU: Difference between Coders (Coder 2 - Coder 1)"
    )

    # Plot DOU
    plot_coding_differences(
        metric="dou",
        filename="dou_coding_difference.html",
        title="DOU: Difference between Coders (Coder 2 - Coder 1)"
    )