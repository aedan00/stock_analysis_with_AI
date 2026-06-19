import matplotlib.patches as patches


def plot_candlestick(
    ax,
    data,
    ticker,
):

    candle_width = 0.6

    x = range(len(data))

    for i, row in enumerate(data.itertuples()):

        open_price = row.Open
        high = row.High
        low = row.Low
        close = row.Close


        color = (
            "green"
            if close >= open_price
            else "red"
        )


        # wick
        ax.plot(
            [i, i],
            [low, high],
            color=color,
            linewidth=1,
        )


        # body

        bottom = min(
            open_price,
            close
        )

        height = abs(
            close - open_price
        )


        if height == 0:
            height = 0.01


        candle = patches.Rectangle(
            (
                i - candle_width / 2,
                bottom
            ),
            candle_width,
            height,
            facecolor=color,
            edgecolor=color,
        )


        ax.add_patch(candle)



    ax.set_title(
        f"{ticker} Candlestick"
    )

    ax.set_ylabel(
        "Price"
    )

    ax.grid(True)


    step = max(
        1,
        len(data)//10
    )

    ax.set_xticks(
        range(
            0,
            len(data),
            step
        )
    )

    ax.set_xticklabels(
        [
            d.strftime("%Y-%m-%d")
            for d in data.index[::step]
        ],
        rotation=45,
    )