def display_fundamental_report(
    metrics
):

    valuation = metrics.valuation

    print(
        "\n============= Fundamental Analysis ==============\n"
    )


    print(
        f"Market Cap: "
        f"${valuation.market_cap:,.0f}"
    )


    print(
        f"P/E Ratio: "
        f"{valuation.pe_ratio:.2f}"
    )

    print(
        f"P/E Signal: "
        f"{valuation.pe_signal}"
    )


    print(
        f"PEG Ratio: "
        f"{valuation.peg_ratio:.2f}"
    )

    print(
        f"PEG Signal: "
        f"{valuation.peg_signal}"
    )


    print(
        f"Price / Book: "
        f"{valuation.price_to_book:.2f}"
    )

    print(
        f"P/B Signal: "
        f"{valuation.pb_signal}"
    )


    print(
        "\n================================================="
    )