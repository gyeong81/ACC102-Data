[README.md](https://github.com/user-attachments/files/26919332/README.md)
 📈 China A-Share Sector Performance Dashboard

By: Duoying Gao  
An interactive Streamlit dashboard for exploring and comparing sector-level performance in China's A-share market.

 Problem & Target Users

Analysis Question: How do different industry sectors in China's A-share market perform in terms of returns, volatility, and correlation? Which sectors offer the best risk-adjusted returns, and how do they relate to major market indices?

Target Users: Individual investors, financial analysts, business students, and fund managers who need sector-level insights for portfolio allocation and market understanding.

 Data

- Source: Simulated based on AKShare / East Money data structure and real A-share market characteristics
- Generation Date: April 2026
- Coverage: 10 A-share industry sectors, 6 major market indices, 2023–2026
- Sector Indices: Banking, Securities, Insurance, Healthcare, New Energy, Defense, Real Estate, Technology, Consumer, Semiconductor
- Market Indices: SSE Composite, SZSE Component, ChiNext, SSE 50, CSI 300, CSI 500
- Note: Data is generated using Python (numpy/pandas) with realistic market microstructure (volatility, drift, crisis/rally events, A-share trading calendar) to demonstrate the full analysis pipeline. The methodology and tool design are fully applicable to real AKShare data.

 Method

1. Data Generation: Generate sector and market index data using Python with realistic A-share market characteristics
2. Data Cleaning: Standardize Chinese column names to English, convert dates, handle missing values
3. Data Transformation: Calculate daily returns, 20-day moving averages, rolling volatility, cumulative returns, and risk-return ratios
4. Descriptive Analysis: Sector performance summary, rankings, market benchmark comparison
5. Visualization: Interactive time-series plots, correlation heatmaps, risk-return scatter plots, box plots
6. Interactive Tool: Streamlit dashboard with 6 functional pages — Overview, Sector Trends, Risk-Return, Correlation, Market Indices, Data Explorer

 Key Findings

1. Sector Divergence: Significant performance dispersion across sectors — Technology and Semiconductor show higher returns but also higher volatility.
2. Risk-Return Trade-off: Generally positive relationship between volatility and return, consistent with financial theory.
3. Sector Correlations: Most sectors show positive correlations, especially within related industries (Banking & Securities), with diversification implications.
4. Market Benchmark: Comparing sector performance against CSI 300 and ChiNext helps identify outperforming/underperforming sectors.
5. Volatility Clustering: Real Estate and Securities exhibit the widest return distributions, indicating higher risk.

 How to Run

 Prerequisites

- Python 3.9+
- Required packages listed in `requirements.txt`

 Step 1: Generate Data

```bash
python generate_data.py
```

This generates sector and market index data with realistic A-share market characteristics and saves to `data/`.

 Step 2: Run the App

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

 Project Structure

```
├── README.md
├── app.py                     Streamlit application
├── notebook.ipynb             Jupyter notebook with full analysis
├── generate_data.py           Data generation script (Python)
├── requirements.txt           Python dependencies
├── data/
│   ├── sector_indices.csv     Sector index historical data
│   ├── market_indices.csv     Market index historical data
│   └── stock_snapshot.csv     Stock snapshot (optional)
└── figures/                   Generated chart images
```

 Limitations & Future Improvements

- Limited Time Window: Only 3 years of data; longer history would improve trend analysis.
- Sector-Level Only: Individual stock analysis within sectors could reveal more granular insights.
- No Fundamental Data: Incorporating P/E, ROE, etc. would strengthen the analysis.
- No Predictive Modeling: Future work could include time-series forecasting.
- Future: Add sector rotation signals, relative strength indicators, and macroeconomic overlay.

 Demo Video

https://video.xjtlu.edu.cn/Mediasite/Channel/5827ac887fb940a08d3a8e5b8ab9e97d5f

 Tags

`xjtlu` `acc102` `python` `data-analysis` `streamlit` `a-share` `akshare`
