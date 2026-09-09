
import pandas as pd
import matplotlib.pyplot as plt


from HelperFunctions.demographics_settings import AGE_COL, EXPERIENCE_ORDER, EXPERIENCE_COLS, GENDER_COL
from Study import participants







def plot_age_distribution(df):
    order = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]

    counts = df[AGE_COL].value_counts().reindex(order).dropna()
    percentages = counts / counts.sum() * 100

    fig, ax = plt.subplots(figsize=(6, 3))

    bars = ax.barh(
        counts.index,
        counts,
        color="#4C78A8",
        edgecolor="white",
    )

    ax.set_xlabel("Number of Participants")
    ax.set_ylabel("Age group")

    for bar, n, pct in zip(bars, counts, percentages):
        ax.text(
            n + 0.1,
            bar.get_y() + bar.get_height() / 2,
            f"{int(n)} ({pct:.0f}%)",
            va="center",
        )

    ax.set_xlim(0, counts.max() * 1.25)

    fig.tight_layout()
    fig.savefig("age_distribution.pdf", bbox_inches="tight")

    return ax



def plot_gender_distribution(df):
    fig, ax = plt.subplots(figsize=(5, 4))

    counts = df[GENDER_COL].value_counts()
    percentages = counts / counts.sum() * 100

    bars = ax.bar(
        percentages.index,
        percentages.values,
        color="#59A14F",
        edgecolor="white",
        linewidth=0.8,
    )

    ax.set_ylabel("Participants [%]")
    ax.set_xlabel("Gender")
    ax.set_title("Gender distribution")

    ax.set_ylim(0, max(percentages) * 1.15)

    for bar, value in zip(bars, percentages):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.0f}%",
            ha="center",
            va="bottom",
        )

    fig.savefig("gender_distribution.pdf")
    return ax



def plot_experience_distribution(df):
    experience_cols = {
        "Spreadsheets": (
            "How much experience do you have using spreadsheets?"
        ),
        "Tablets / touchscreens": (
            "How much experience do you have using tablets or similar large touchscreens?"
        ),
        "Digital pen / stylus": (
            "How much experience do you have using a digital pen or stylus?"
        ),
    }

    experience_order = [
        "very little",
        "a little",
        "some",
        "a lot",
    ]

    data = []

    for label, column in experience_cols.items():
        counts = df[column].value_counts().reindex(
            experience_order,
            fill_value=0,
        )

        percentages = counts / counts.sum() * 100
        data.append([label, *percentages])

    data = pd.DataFrame(
        data,
        columns=["Experience", *experience_order],
    ).set_index("Experience")

    fig, ax = plt.subplots(figsize=(7, 3.8))

    colors = [
        "#D9E2F3",
        "#9FBAD0",
        "#5B8DB8",
        "#1F4E79",
    ]

    data.plot(
        kind="barh",
        stacked=True,
        ax=ax,
        color=colors,
        edgecolor="white",
        linewidth=0.8,
        width=0.65,
    )

    ax.set_xlim(0, 100)
    ax.set_xlabel("Participants [%]")
    ax.set_ylabel("")
    ax.invert_yaxis()

    # Keep y-axis line, remove unnecessary top/right lines
    ax.spines["left"].set_visible(True)
    ax.spines["bottom"].set_visible(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Legend with border
    ax.legend(
        title="Experience",
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        ncol=4,
        frameon=True,
        edgecolor="black",
        fancybox=False,
        fontsize=8,
        handlelength=1.2,
        handleheight=0.8,
        columnspacing=1.0,
        handletextpad=0.4,
        borderpad=0.4,
    )

    # Add percentage to EVERY non-zero segment
    for y, row in enumerate(data.itertuples(index=False)):
        left = 0

        for value, color in zip(row, colors):
            if value > 0:
                ax.text(
                    left + value / 2,
                    y,
                    f"{value:.0f}%",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="black" if color in colors[:2] else "white",
                )

            left += value

    fig.tight_layout()
    fig.savefig(
        "experience_distribution.pdf",
        bbox_inches="tight",
    )

    return ax


if __name__ == "__main__":
    # DATA ACCESS:
    data = []
    for p in participants:
        line = p.get_demographic_data()
        line["participant"] = p.id
        data.append(line)
    df = pd.DataFrame(data)


    # RUNNING:
    plot_age_distribution(df=df)

    plot_gender_distribution(df=df)

    plot_experience_distribution(df=df)




