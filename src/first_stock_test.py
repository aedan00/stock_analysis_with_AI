import yfinance as yf

# Choose a stock
ticker = "AAPL"

# Create a stock object
stock = yf.Ticker(ticker)

# Download 1 year of historical data
data = stock.history(period="1y")

# Display the first 5 rows
print(data.head())

# Display the latest closing price
latest_price = data["Close"].iloc[-1]

print("\nLatest closing price:")
print(latest_price)