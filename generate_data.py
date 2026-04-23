import pandas as pd
import numpy as np
import os

np.random.seed(42)

SECTORS = {
    "Banking": {"base_price": 3200, "daily_vol": 0.012, "drift": 0.0002},
    "Securities": {"base_price": 1800, "daily_vol": 0.022, "drift": 0.0003},
    "Insurance": {"base_price": 2100, "daily_vol": 0.015, "drift": 0.0001},
    "Healthcare": {"base_price": 9500, "daily_vol": 0.018, "drift": 0.0004},
    "New Energy": {"base_price": 4200, "daily_vol": 0.025, "drift": 0.0005},
    "Defense": {"base_price": 2800, "daily_vol": 0.020, "drift": 0.0003},
    "Real Estate": {"base_price": 1500, "daily_vol": 0.020, "drift": -0.0003},
    "Technology": {"base_price": 5600, "daily_vol": 0.024, "drift": 0.0006},
    "Consumer": {"base_price": 8200, "daily_vol": 0.014, "drift": 0.0003},
    "Semiconductor": {"base_price": 6800, "daily_vol": 0.028, "drift": 0.0005},
}

MARKET_INDICES = {
    "SSE Composite": {"base_price": 3100, "daily_vol": 0.012, "drift": 0.0001},
    "SZSE Component": {"base_price": 10500, "daily_vol": 0.016, "drift": 0.0002},
    "ChiNext": {"base_price": 2100, "daily_vol": 0.022, "drift": 0.0003},
    "SSE 50": {"base_price": 2700, "daily_vol": 0.011, "drift": 0.0001},
    "CSI 300": {"base_price": 3900, "daily_vol": 0.013, "drift": 0.0002},
    "CSI 500": {"base_price": 5800, "daily_vol": 0.018, "drift": 0.0003},
}

CRISIS_DATES = {
    "2023-08-01": -0.02,
    "2023-10-15": -0.015,
    "2024-01-20": -0.025,
    "2024-06-10": -0.01,
    "2025-03-15": -0.02,
    "2025-09-20": -0.018,
}

RALLY_DATES = {
    "2024-02-05": 0.03,
    "2024-09-24": 0.04,
    "2025-01-15": 0.025,
    "2025-07-10": 0.02,
}

def generate_trading_dates(start="2023-01-03", end="2026-04-15"):
    dates = pd.bdate_range(start=start, end=end)
    dates = dates[~dates.strftime("%m-%d").isin([
        "01-01", "01-02", "01-03", "04-05", "05-01", "05-02", "05-03",
        "10-01", "10-02", "10-03", "10-04", "10-05", "10-06", "10-07",
    ])]
    return dates

def generate_price_series(dates, base_price, daily_vol, drift):
    n = len(dates)
    returns = np.random.normal(drift, daily_vol, n)
    for i, d in enumerate(dates):
        ds = d.strftime("%Y-%m-%d")
        if ds in CRISIS_DATES:
            returns[i] += CRISIS_DATES[ds] + np.random.normal(0, 0.005)
        if ds in RALLY_DATES:
            returns[i] += RALLY_DATES[ds] + np.random.normal(0, 0.005)
    prices = [base_price]
    for r in returns[1:]:
        prices.append(prices[-1] * (1 + r))
    close = np.array(prices)
    open_p = close * (1 + np.random.normal(0, daily_vol * 0.3, n))
    high = np.maximum(close, open_p) * (1 + np.abs(np.random.normal(0, daily_vol * 0.4, n)))
    low = np.minimum(close, open_p) * (1 - np.abs(np.random.normal(0, daily_vol * 0.4, n)))
    volume = np.random.lognormal(mean=18, sigma=0.5, size=n).astype(int)
    amount = (close * volume * np.random.uniform(8, 15, n)).round(2)
    amplitude = ((high - low) / low * 100).round(2)
    pct_change = np.concatenate([[0], np.diff(close) / close[:-1] * 100]).round(2)
    change = np.concatenate([[0], np.diff(close)]).round(2)
    turnover = (np.random.uniform(0.5, 5.0, n)).round(2)
    return pd.DataFrame({
        "日期": dates,
        "开盘": np.round(open_p, 2),
        "收盘": np.round(close, 2),
        "最高": np.round(high, 2),
        "最低": np.round(low, 2),
        "成交量": volume,
        "成交额": amount,
        "振幅": amplitude,
        "涨跌幅": pct_change,
        "涨跌额": change,
        "换手率": turnover,
    })

def main():
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(output_dir, exist_ok=True)

    trading_dates = generate_trading_dates()
    print(f"Trading dates: {len(trading_dates)} days")

    print("Generating sector index data...")
    all_sectors = []
    for sector_name, params in SECTORS.items():
        print(f"  Generating: {sector_name}")
        df = generate_price_series(trading_dates, **params)
        df["sector"] = sector_name
        all_sectors.append(df)
    sector_df = pd.concat(all_sectors, ignore_index=True)
    sector_path = os.path.join(output_dir, "sector_indices.csv")
    sector_df.to_csv(sector_path, index=False)
    print(f"Sector data saved: {sector_path} ({len(sector_df)} records)")

    print("\nGenerating market index data...")
    all_indices = []
    for idx_name, params in MARKET_INDICES.items():
        print(f"  Generating: {idx_name}")
        df = generate_price_series(trading_dates, **params)
        df["index_name"] = idx_name
        df["index_code"] = list(MARKET_INDICES.keys()).index(idx_name)
        all_indices.append(df)
    market_df = pd.concat(all_indices, ignore_index=True)
    market_path = os.path.join(output_dir, "market_indices.csv")
    market_df.to_csv(market_path, index=False)
    print(f"Market data saved: {market_path} ({len(market_df)} records)")

    print("\n" + "=" * 50)
    print("Data generation complete!")
    print(f"Sectors: {sector_df['sector'].nunique()}")
    print(f"Market indices: {market_df['index_name'].nunique()}")
    print(f"Date range: {trading_dates[0].strftime('%Y-%m-%d')} to {trading_dates[-1].strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    main()
