import yfinance as yf

def fetch_evergreen_history(start: str = "2019-01-01"):
    """Fetch Evergreen Marine Corp. (2603.TW) daily data from Yahoo Finance.

    Returns a pandas DataFrame with columns:
    date, price (close), high, low, volume.
    """
    ticker = "2603.TW"
    data = yf.download(ticker, start=start)
    data = data[["Close", "High", "Low", "Volume"]].reset_index()
    data.rename(
        columns={
            "Date": "date",
            "Close": "price",
            "High": "high",
            "Low": "low",
            "Volume": "volume",
        },
        inplace=True,
    )
    return data


if __name__ == "__main__":
    df = fetch_evergreen_history()
    print(df.head())
    print(f"Fetched {len(df)} rows")
