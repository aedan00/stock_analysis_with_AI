import pandas as pd


def plot_price_chart(
    ax,
    data: pd.DataFrame,
    ticker: str,
):

    ax.plot(
        data.index,
        data["Close"],
        color="black",
        linewidth=2,
        label="Close",
    )


    if "MA50" in data.columns:

        ax.plot(
            data.index,
            data["MA50"],
            color="blue",
            label="MA50",
        )


    if "MA200" in data.columns:

        ax.plot(
            data.index,
            data["MA200"],
            color="orange",
            label="MA200",
        )


    # Bollinger Bands

    if (
        "BB_UPPER" in data.columns
        and "BB_LOWER" in data.columns
    ):

        ax.fill_between(
            data.index,
            data["BB_LOWER"],
            data["BB_UPPER"],
            color="gray",
            alpha=0.2,
            label="Bollinger",
        )


    # Support / Resistance

    for column, color, label in [
        (
            "SUPPORT",
            "green",
            "Support",
        ),
        (
            "RESISTANCE",
            "red",
            "Resistance",
        ),
    ]:

        if column in data.columns:

            ax.axhline(
                data[column].iloc[-1],
                color=color,
                linestyle="--",
                label=label,
            )


    # Fibonacci

    fib_levels = [
        "FIB_23_6",
        "FIB_38_2",
        "FIB_50",
        "FIB_61_8",
        "FIB_78_6",
    ]


    for level in fib_levels:

        if level in data.columns:

            ax.axhline(
                data[level].iloc[-1],
                color="purple",
                linestyle=":",
                alpha=.4,
            )


    ax.set_title(
        f"{ticker} Price Analysis"
    )

    ax.set_ylabel(
        "Price ($)"
    )

    ax.grid(True)
    ax.legend(
        fontsize=8
    )



def plot_momentum(
    ax,
    data,
    ticker,
):

    if "RSI" in data.columns:

        ax.plot(
            data.index,
            data["RSI"],
            color="purple",
            label="RSI",
        )


    if "STOCH_K" in data.columns:

        ax.plot(
            data.index,
            data["STOCH_K"],
            color="green",
            label="Stoch %K",
        )


    if "STOCH_D" in data.columns:

        ax.plot(
            data.index,
            data["STOCH_D"],
            color="orange",
            label="Stoch %D",
        )


    ax.axhline(
        70,
        color="red",
        linestyle="--",
    )

    ax.axhline(
        30,
        color="green",
        linestyle="--",
    )


    ax.set_ylim(
        0,
        100,
    )

    ax.set_title(
        "Momentum"
    )

    ax.grid(True)
    ax.legend()



def plot_macd(
    ax,
    data,
    ticker,
):

    ax.plot(
        data.index,
        data["MACD"],
        label="MACD",
        color="blue",
    )


    ax.plot(
        data.index,
        data["MACD_SIGNAL"],
        label="Signal",
        color="red",
    )


    if "MACD_HISTOGRAM" in data.columns:

        colors = [
            "green" if value >= 0 else "red"
            for value in data["MACD_HISTOGRAM"]
        ]

        ax.bar(
            data.index,
            data["MACD_HISTOGRAM"],
            color=colors,
            alpha=.5,
        )


    ax.axhline(
        0,
        color="black",
    )


    ax.set_title(
        "MACD"
    )

    ax.grid(True)
    ax.legend()



def plot_volume(
    ax,
    data,
    ticker,
):

    ax.bar(
        data.index,
        data["Volume"],
        alpha=.4,
        label="Volume",
    )


    if "AVG_VOLUME20" in data.columns:

        ax.plot(
            data.index,
            data["AVG_VOLUME20"],
            color="orange",
            label="20 Day Average",
        )


    if "OBV" in data.columns:

        ax2 = ax.twinx()

        ax2.plot(
            data.index,
            data["OBV"],
            color="purple",
            label="OBV",
        )


    ax.set_title(
        "Volume Analysis"
    )

    ax.grid(True)



def plot_trend_strength(
    ax,
    data,
    ticker,
):

    ax.plot(
        data.index,
        data["ADX"],
        color="black",
        label="ADX",
    )


    if "PLUS_DI" in data.columns:

        ax.plot(
            data.index,
            data["PLUS_DI"],
            color="green",
            label="+DI",
        )


    if "MINUS_DI" in data.columns:

        ax.plot(
            data.index,
            data["MINUS_DI"],
            color="red",
            label="-DI",
        )


    ax.axhline(
        25,
        color="gray",
        linestyle="--",
        label="Strong Trend",
    )


    ax.set_title(
        "ADX Trend Strength"
    )

    ax.grid(True)
    ax.legend()