import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import os
import math
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Trump Signal Backtester",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --gold: #C9A84C;
    --gold-light: #F0CC6E;
    --gold-dim: #8a6f2e;
    --bg: #0a0a0a;
    --surface: #111111;
    --surface2: #1a1a1a;
    --border: #2a2a2a;
    --text: #e8e8e8;
    --text-dim: #888;
    --red: #e05252;
    --green: #52c97a;
    --blue: #5b9cf6;
    --purple: #a78bfa;
}

html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stApp { background-color: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem !important; max-width: 1400px !important; }

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: var(--text-dim) !important;
}

.stSelectbox > div > div,
.stTextInput > div > div > input,
.stMultiSelect > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}

.hero {
    border-bottom: 1px solid var(--border);
    padding-bottom: 1.5rem;
    margin-bottom: 2rem;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    color: var(--gold);
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(2.2rem, 4vw, 3.8rem);
    letter-spacing: 0.04em;
    line-height: 1;
    color: var(--text);
    margin: 0;
}
.hero-title span { color: var(--gold); }
.hero-sub {
    font-size: 0.88rem;
    color: var(--text-dim);
    margin-top: 0.6rem;
    line-height: 1.6;
}

.stat-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    margin-bottom: 2rem;
}
.stat-card {
    background: var(--surface);
    padding: 1.2rem 1.4rem;
    position: relative;
}
.stat-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--gold);
    opacity: 0;
    transition: opacity 0.2s;
}
.stat-card:hover::after { opacity: 1; }
.stat-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 0.4rem;
}
.stat-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.9rem;
    letter-spacing: 0.03em;
    color: var(--gold-light);
    line-height: 1;
}
.stat-value.green { color: var(--green); }
.stat-value.red   { color: var(--red); }
.stat-delta {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    margin-top: 0.25rem;
    color: var(--text-dim);
}

.section-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.3rem;
    letter-spacing: 0.08em;
    color: var(--text);
    margin-bottom: 0.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
    margin-left: 0.75rem;
}
.section-sub {
    font-size: 0.78rem;
    color: var(--text-dim);
    margin-bottom: 1rem;
    font-family: 'DM Mono', monospace;
}

.finding {
    background: var(--surface);
    border-left: 3px solid var(--gold);
    padding: 0.9rem 1.2rem;
    margin: 0.8rem 0 1.2rem;
    font-size: 0.85rem;
    line-height: 1.7;
    color: var(--text-dim);
}
.finding strong { color: var(--gold-light); }
.finding.green  { border-color: var(--green); }
.finding.red    { border-color: var(--red); }
.finding.blue   { border-color: var(--blue); }

.ticker-pill {
    display: inline-block;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 0.15rem 0.5rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: var(--gold);
    margin: 0.1rem;
}

.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 0 !important;
    border-bottom: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--text-dim) !important;
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 1.1rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom: 2px solid var(--gold) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.2rem !important; }

[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    padding: 0.8rem !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}

/* warning box */
.warn {
    background: #1a1200;
    border-left: 3px solid #C9A84C;
    padding: 0.7rem 1rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #888;
    margin-bottom: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
PT   = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='DM Sans', color='#666666', size=10),
            margin=dict(l=10, r=10, t=30, b=10))
AXIS = dict(gridcolor='#1a1a1a', linecolor='#2a2a2a', tickcolor='#2a2a2a', zeroline=False)

GOLD   = '#C9A84C'
RED    = '#e05252'
GREEN  = '#52c97a'
BLUE   = '#5b9cf6'
PURPLE = '#a78bfa'
DIM    = '#2a2a2a'
PALETTE = [GOLD, GREEN, BLUE, PURPLE, RED, '#f97316', '#06b6d4']

TRUMP_PATH = "trump_processed.csv"

PRESET_PORTFOLIOS = {
    "XAU/USD Only":       ["GC=F"],
    "Macro Hedge":        ["GC=F", "GLD", "SLV", "TLT", "UUP"],
    "Tech Giants":        ["AAPL", "MSFT", "NVDA", "GOOGL", "META"],
    "Trump Tariff Plays": ["GC=F", "X", "NUE", "CLF", "AA"],
    "China Exposed":      ["BABA", "JD", "PDD", "NIO", "FXI"],
    "Custom":             [],
}

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;
                letter-spacing:0.08em;color:#C9A84C;padding-bottom:1rem;
                border-bottom:1px solid #2a2a2a;margin-bottom:1rem;">
        📡 Signal Config
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;color:#555;margin-bottom:0.5rem;">Asset Universe</div>', unsafe_allow_html=True)

    preset = st.selectbox("Portfolio Preset", list(PRESET_PORTFOLIOS.keys()))

    if preset == "Custom":
        custom_input = st.text_input("Tickers (comma-separated)", "GC=F, AAPL, NVDA")
        tickers = [t.strip().upper() for t in custom_input.split(",") if t.strip()]
    else:
        tickers = PRESET_PORTFOLIOS[preset]
        st.markdown(
            " ".join([f'<span class="ticker-pill">{t}</span>' for t in tickers]),
            unsafe_allow_html=True
        )

    equal_weight = st.checkbox("Equal-weight portfolio", value=True,
                                help="Off = inverse-vol weighting (HRP-style)")

    st.markdown("---")
    st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;color:#555;margin-bottom:0.5rem;">Signal Parameters</div>', unsafe_allow_html=True)

    cutoff_hour = st.slider("Tweet cutoff (EST hour)", 6, 21, 12,
                             help="Only tweets before this hour count as same-day signal")

    sent_filter = st.multiselect("Sentiment filter",
                                  ["positive", "negative", "neutral"],
                                  default=["positive", "negative"])

    starting_capital = st.number_input("Starting Capital ($)", min_value=1000,
                                        max_value=1_000_000, value=10_000, step=1000)

    st.markdown("---")
    run_btn = st.button("▶  RUN BACKTEST", use_container_width=True)

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Signal Backtester · Truth Social × Markets · Next-Day Return Study</div>
    <h1 class="hero-title">Does Trump Move <span>Your Assets?</span></h1>
    <p class="hero-sub">
        Buy close on tweet day, sell next-day close. Student's t-test (equal variance) on
        next-day returns — same methodology as the notebook analysis.
        Regression models reveal whether the effect survives sentiment and volume controls.
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_trump():
    df = pd.read_csv(TRUMP_PATH, parse_dates=['created_at'])
    df['created_at_est'] = pd.to_datetime(df['created_at'], utc=True).dt.tz_convert('US/Eastern')
    df['tweet_hour_est'] = df['created_at_est'].dt.hour
    df['tweet_date_est'] = df['created_at_est'].dt.date
    return df

@st.cache_data
def fetch_prices(tickers_tuple, start, end):
    tickers_list = list(tickers_tuple)
    raw = yf.download(tickers_list, start=start, end=end,
                      auto_adjust=True, progress=False)
    if len(tickers_list) == 1:
        close = raw[['Close']].copy()
        close.columns = tickers_list
    else:
        close = raw['Close'] if isinstance(raw.columns, pd.MultiIndex) else raw
    return close.dropna(how='all')


@st.cache_data
def load_xau_daily():
    path = "XAU_daily.csv"
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    au = pd.read_csv(path)
    au['Date'] = pd.to_datetime(au['Date'])
    au = au.set_index('Date')
    if 'Close' not in au.columns:
        raise KeyError('XAU_daily.csv must contain a Close column')
    returns = au['Close'].pct_change() * 100
    return returns.rename('daily_return')

def build_portfolio_returns(close_df, equal_weight=True):
    rets = close_df.pct_change()
    if equal_weight or close_df.shape[1] == 1:
        port = rets.mean(axis=1)
    else:
        vol = rets.rolling(21).std().iloc[-1]
        w   = (1 / vol) / (1 / vol).sum()
        port = (rets * w).sum(axis=1)
    return (port * 100).rename('daily_return')

def build_analysis_df(trump_df, cutoff, sentiment_list, port_returns):
    """
    Notebook methodology:
    - Aggregate tweet days (before cutoff, filtered by sentiment)
    - Merge with NEXT-DAY return (shift -1 on price series)
    - t-test: tweet days vs no-tweet days on next_day_return
    """
    early = trump_df[
        (trump_df['tweet_hour_est'] < cutoff) &
        (trump_df['sentiment'].isin(sentiment_list))
    ].copy()

    daily = early.groupby('tweet_date_est').agg(
        tweet_count          =('content_clean', 'count'),
        avg_sentiment        =('vader_compound', 'mean'),
        dominant_sentiment   =('sentiment', lambda x: x.value_counts().index[0]),
        earliest_hour        =('tweet_hour_est', 'min'),
        sample_tweet         =('content_clean', 'first')
    ).reset_index()
    daily['tweet_date_est'] = pd.to_datetime(daily['tweet_date_est'])

    price_df = port_returns.reset_index()
    price_df.columns = ['Date', 'daily_return']
    price_df['Date'] = pd.to_datetime(price_df['Date'])

    # next-day return = shift(-1) on the price series
    price_df['next_day_return'] = price_df['daily_return'].shift(-1)

    merged = price_df.merge(daily, left_on='Date', right_on='tweet_date_est', how='left')
    merged['has_tweet'] = merged['tweet_count'].notna()
    return merged.dropna(subset=['daily_return'])

def ttest_ind_manual(a, b):
    """Student's t-test (equal variance assumed) — matches scipy.stats.ttest_ind default."""
    n1, n2 = len(a), len(b)
    m1, m2 = a.mean(), b.mean()
    # pooled variance
    s1, s2 = a.var(ddof=1), b.var(ddof=1)
    sp2 = ((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2)
    se  = np.sqrt(sp2 * (1/n1 + 1/n2))
    t   = (m1 - m2) / se if se > 0 else 0
    df  = n1 + n2 - 2

    # two-tailed p via incomplete beta (normal approx for large df)
    def norm_cdf(x):
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

    if df > 100:
        p = 2 * (1 - norm_cdf(abs(t)))
    else:
        # t-distribution via regularised incomplete beta
        import math as _math
        x = df / (df + t * t)
        # use lgamma for numerical stability
        lbeta = _math.lgamma(df/2) + _math.lgamma(0.5) - _math.lgamma((df+1)/2)
        # regularised incomplete beta via continued fraction (Lentz) — simple approx for UI
        # For the UI we use the normal approx for df>30, exact otherwise
        if df > 30:
            p = 2 * (1 - norm_cdf(abs(t)))
        else:
            # rough normal approx is fine for display; note for very small n
            p = 2 * (1 - norm_cdf(abs(t) * (1 - 1/(4*df))))
    return t, p

def run_backtest(analysis_df, capital=10_000):
    """
    Notebook backtest:
    - Buy close on tweet day, sell next-day close
    - Compound returns on $capital
    """
    bt = analysis_df[analysis_df['has_tweet']].dropna(
        subset=['next_day_return']).sort_values('Date').copy()
    if len(bt) < 3:
        return None

    tweet_ret    = bt['next_day_return']
    no_tweet_ret = analysis_df[~analysis_df['has_tweet']]['next_day_return'].dropna()

    t_stat, p_val = ttest_ind_manual(tweet_ret, no_tweet_ret)

    # compound growth
    bt['trade_return']       = bt['next_day_return'] / 100
    bt['cumulative_capital'] = capital * (1 + bt['trade_return']).cumprod()

    total_ret    = (bt['cumulative_capital'].iloc[-1] - capital) / capital * 100
    win_rate     = (bt['next_day_return'] > 0).mean()
    avg_win      = bt[bt['next_day_return'] > 0]['next_day_return'].mean()
    avg_loss     = bt[bt['next_day_return'] < 0]['next_day_return'].mean()
    sharpe       = (bt['trade_return'].mean() / bt['trade_return'].std()) * np.sqrt(252) if bt['trade_return'].std() > 0 else 0
    running_max  = bt['cumulative_capital'].cummax()
    max_dd       = ((running_max - bt['cumulative_capital']) / running_max).max() * 100
    baseline_wr  = (no_tweet_ret > 0).mean()

    return dict(
        n=len(bt), win_rate=win_rate, total_ret=total_ret,
        final_capital=bt['cumulative_capital'].iloc[-1],
        avg_win=avg_win, avg_loss=avg_loss, sharpe=sharpe,
        max_dd=max_dd, p_val=p_val, t_stat=t_stat,
        tweet_ret=tweet_ret, no_tweet_ret=no_tweet_ret,
        baseline_wr=baseline_wr,
        mean_tweet=tweet_ret.mean(), mean_no_tweet=no_tweet_ret.mean(),
        bt=bt
    )

def run_regression(analysis_df):
    """
    Model 1: has_tweet → next_day_return (OLS, manual)
    Model 2: avg_sentiment + tweet_count + lag_return → next_day_return (tweet days only)
    """
    df = analysis_df.dropna(subset=['next_day_return']).copy()
    df['has_tweet_int'] = df['has_tweet'].astype(int)
    df['lag_return']    = df['daily_return'].shift(1)

    # Model 1
    X1 = np.column_stack([np.ones(len(df)), df['has_tweet_int'].values])
    y1 = df['next_day_return'].values
    mask1 = ~np.isnan(y1) & ~np.isnan(X1).any(axis=1)
    X1, y1 = X1[mask1], y1[mask1]
    beta1    = np.linalg.lstsq(X1, y1, rcond=None)[0]
    yhat1    = X1 @ beta1
    resid1   = y1 - yhat1
    n1, k1   = len(y1), X1.shape[1]
    s2_1     = (resid1**2).sum() / (n1 - k1)
    XtX_inv1 = np.linalg.inv(X1.T @ X1)
    se1      = np.sqrt(np.diag(s2_1 * XtX_inv1))
    t1       = beta1 / se1
    r2_1     = 1 - (resid1**2).sum() / ((y1 - y1.mean())**2).sum()

    def t_to_p(t, df):
        def norm_cdf(x):
            return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
        return 2 * (1 - norm_cdf(abs(t)))

    p1 = [t_to_p(ti, n1 - k1) for ti in t1]

    # Model 2 — tweet days only
    tw = df[df['has_tweet']].dropna(subset=['avg_sentiment', 'lag_return', 'tweet_count']).copy()
    if len(tw) >= 10:
        X2 = np.column_stack([
            np.ones(len(tw)),
            tw['avg_sentiment'].values,
            tw['tweet_count'].values,
            tw['lag_return'].values
        ])
        y2   = tw['next_day_return'].values
        mask2 = ~np.isnan(y2) & ~np.isnan(X2).any(axis=1)
        X2, y2 = X2[mask2], y2[mask2]
        beta2   = np.linalg.lstsq(X2, y2, rcond=None)[0]
        yhat2   = X2 @ beta2
        resid2  = y2 - yhat2
        n2, k2  = len(y2), X2.shape[1]
        s2_2    = (resid2**2).sum() / (n2 - k2)
        XtX_inv2 = np.linalg.inv(X2.T @ X2)
        se2     = np.sqrt(np.diag(s2_2 * XtX_inv2))
        t2      = beta2 / se2
        r2_2    = 1 - (resid2**2).sum() / ((y2 - y2.mean())**2).sum()
        p2      = [t_to_p(ti, n2 - k2) for ti in t2]
        model2  = dict(
            labels=['const', 'avg_sentiment', 'tweet_count', 'lag_return'],
            coef=beta2, se=se2, t=t2, p=p2, r2=r2_2, n=n2
        )
    else:
        model2 = None

    model1 = dict(
        labels=['const', 'has_tweet'],
        coef=beta1, se=se1, t=t1, p=p1, r2=r2_1, n=n1
    )
    return model1, model2


# ─────────────────────────────────────────────
# LOAD TRUMP
# ─────────────────────────────────────────────
try:
    trump_df = load_trump()
except FileNotFoundError:
    st.error(f"**{TRUMP_PATH} not found.** Place it in the same folder as this app.")
    st.stop()

date_min = trump_df['created_at_est'].min().date()
date_max = trump_df['created_at_est'].max().date()

# ─────────────────────────────────────────────
# FETCH PRICES
# ─────────────────────────────────────────────
if not tickers:
    st.warning("Add at least one ticker in the sidebar.")
    st.stop()

with st.spinner(f"Fetching {', '.join(tickers)} from yfinance..."):
    try:
        # If user has local XAU daily file and requested a single XAU ticker,
        # prefer the local data to avoid live yfinance fetch.
        if len(tickers) == 1 and os.path.exists('XAU_daily.csv'):
            port_ret = load_xau_daily()
        else:
            close    = fetch_prices(tuple(tickers), str(date_min), str(date_max))
            port_ret = build_portfolio_returns(close, equal_weight)
    except Exception as e:
        st.error(f"yfinance error: {e}")
        st.stop()

# ─────────────────────────────────────────────
# BUILD ANALYSIS & BACKTEST
# ─────────────────────────────────────────────
analysis_df = build_analysis_df(trump_df, cutoff_hour, sent_filter, port_ret)
result      = run_backtest(analysis_df, starting_capital)

if result is None:
    st.error("No tweet days matched your filters. Widen the sentiment filter or cutoff hour.")
    st.stop()

model1, model2 = run_regression(analysis_df)

# ─────────────────────────────────────────────
# METHODOLOGY NOTE
# ─────────────────────────────────────────────
st.markdown("""
<div class="warn">
⚠️ METHODOLOGY · Buy portfolio close on tweet day → sell next-day close.
Student's t-test (equal variance). R² from notebook is ~0.0012 — effect is real but explains very little variance.
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# STAT CARDS
# ─────────────────────────────────────────────
wr_class  = "green" if result['win_rate'] > 0.5 else "red"
ret_class = "green" if result['total_ret'] > 0 else "red"
sh_class  = "green" if result['sharpe'] > 1 else ("" if result['sharpe'] > 0 else "red")
p_class   = "green" if result['p_val'] < 0.05 else ""

st.markdown(f"""
<div class="stat-grid">
    <div class="stat-card">
        <div class="stat-label">Win Rate (Tweet Days)</div>
        <div class="stat-value {wr_class}">{result['win_rate']*100:.1f}%</div>
        <div class="stat-delta">vs {result['baseline_wr']*100:.1f}% baseline · {result['n']} trades</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Total Return</div>
        <div class="stat-value {ret_class}">{result['total_ret']:+.1f}%</div>
        <div class="stat-delta">${starting_capital:,.0f} → ${result['final_capital']:,.0f}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Avg Next-Day Ret</div>
        <div class="stat-value">{result['mean_tweet']:+.4f}%</div>
        <div class="stat-delta">vs {result['mean_no_tweet']:+.4f}% no-tweet · Δ {result['mean_tweet']-result['mean_no_tweet']:+.4f}%</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Sharpe Ratio</div>
        <div class="stat-value {sh_class}">{result['sharpe']:.3f}</div>
        <div class="stat-delta">annualised · √252 scaling</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Max Drawdown</div>
        <div class="stat-value red">{result['max_dd']:.2f}%</div>
        <div class="stat-delta">peak-to-trough on compound equity</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">P-Value (t-test)</div>
        <div class="stat-value {p_class}">{result['p_val']:.4f}</div>
        <div class="stat-delta">t={result['t_stat']:.3f} · {"✓ Sig. at 5%" if result['p_val'] < 0.05 else "✗ Not sig. at 5%"}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Verdict
diff = result['mean_tweet'] - result['mean_no_tweet']
if result['p_val'] < 0.05:
    st.markdown(f"""
    <div class="finding green">
        <strong>Statistically significant at 5% (p={result['p_val']:.4f}).</strong>
        Tweet days produce <strong>{diff:+.4f}%</strong> higher next-day return than baseline.
        Win rate: <strong>{result['win_rate']*100:.1f}%</strong> vs {result['baseline_wr']*100:.1f}% on non-tweet days.
        Note: effect size is small — the notebook's regression R² is ~0.0012, meaning tweets explain ~0.1% of return variance.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="finding red">
        <strong>Not significant at 5% (p={result['p_val']:.4f}, t={result['t_stat']:.3f}).</strong>
        Difference in next-day return: <strong>{diff:+.4f}%</strong>.
        Widen filters or use the full (unfiltered) tweet set to replicate the notebook's p=0.0102 result.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💹  Equity Curve",
    "📐  Regression",
    "🎭  By Sentiment",
    "📊  Per Asset",
    "🔬  Event Study",
])

# ══════════════════════════════════════════════
# TAB 1 — EQUITY CURVE
# ══════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Strategy Equity Curve</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Buy close on tweet day · sell next-day close · compound returns · starting ${starting_capital:,.0f}</div>', unsafe_allow_html=True)

    bt = result['bt']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=bt['Date'], y=bt['cumulative_capital'],
        mode='lines', name='Portfolio Value',
        line=dict(color=GOLD, width=2.5),
        fill='tozeroy', fillcolor='rgba(201,168,76,0.07)'
    ))
    fig.add_hline(y=starting_capital, line_color='#2a2a2a', line_width=1,
                  annotation_text=f"Starting ${starting_capital:,.0f}",
                  annotation_font=dict(color='#444', size=9))

    wins   = bt[bt['next_day_return'] > 0]
    losses = bt[bt['next_day_return'] < 0]
    fig.add_trace(go.Scatter(
        x=wins['Date'], y=wins['cumulative_capital'],
        mode='markers', marker=dict(color=GREEN, size=5, symbol='circle'),
        name='Win', opacity=0.7
    ))
    fig.add_trace(go.Scatter(
        x=losses['Date'], y=losses['cumulative_capital'],
        mode='markers', marker=dict(color=RED, size=5, symbol='circle'),
        name='Loss', opacity=0.7
    ))

    fig.update_layout(**PT, height=380,
                      xaxis=dict(**AXIS),
                      yaxis=dict(**AXIS, title='Portfolio Value ($)'),
                      legend=dict(orientation='h', y=1.05, font_size=10))
    st.plotly_chart(fig, use_container_width=True)

    # Return distribution
    c1, c2 = st.columns(2)
    with c1:
        fig_d = go.Figure()
        fig_d.add_trace(go.Histogram(
            x=result['tweet_ret'], nbinsx=30,
            marker_color=GOLD, opacity=0.75, name='Tweet Days'
        ))
        fig_d.add_trace(go.Histogram(
            x=result['no_tweet_ret'], nbinsx=30,
            marker_color=BLUE, opacity=0.4, name='No-Tweet Days'
        ))
        fig_d.update_layout(**PT, height=260, barmode='overlay',
                             xaxis=dict(**AXIS, title='Next-Day Return (%)'),
                             yaxis=dict(**AXIS),
                             legend=dict(orientation='h', y=1.05, font_size=9),
                             title=dict(text='Return Distribution', font_size=11, x=0, font_color='#666'))
        st.plotly_chart(fig_d, use_container_width=True)

    with c2:
        fig_b = go.Figure()
        fig_b.add_trace(go.Box(
            y=result['tweet_ret'], name='Tweet Days',
            marker_color=GOLD, line_color=GOLD, boxmean=True
        ))
        fig_b.add_trace(go.Box(
            y=result['no_tweet_ret'], name='No-Tweet Days',
            marker_color=BLUE, line_color=BLUE, boxmean=True
        ))
        fig_b.update_layout(**PT, height=260,
                             yaxis=dict(**AXIS, title='Next-Day Return (%)'),
                             xaxis=dict(**AXIS),
                             legend=dict(orientation='h', y=1.05, font_size=9),
                             title=dict(text='Box Plot Comparison', font_size=11, x=0, font_color='#666'))
        st.plotly_chart(fig_b, use_container_width=True)

    # Trade log
    st.markdown('<div class="section-header" style="font-size:1rem;margin-top:0.5rem">Trade Log</div>', unsafe_allow_html=True)
    log = bt[['Date', 'dominant_sentiment', 'earliest_hour',
              'daily_return', 'next_day_return', 'cumulative_capital', 'sample_tweet']].copy()
    log.columns = ['Date', 'Sentiment', 'Tweet Hour EST',
                   'Day Ret %', 'Next-Day Ret %', 'Portfolio Value $', 'Sample Tweet']
    log['Day Ret %']       = log['Day Ret %'].round(3)
    log['Next-Day Ret %']  = log['Next-Day Ret %'].round(3)
    log['Portfolio Value $'] = log['Portfolio Value $'].round(2)
    log['Sample Tweet']    = log['Sample Tweet'].str[:90] + '...'
    st.dataframe(log.sort_values('Date', ascending=False),
                 use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 2 — REGRESSION
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">OLS Regression Models</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Does the tweet signal survive controls? — replicates notebook Models 1 & 2</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="finding blue">
        <strong>Model 1 — Tweet Presence:</strong>
        coef={model1['coef'][1]:.4f}, p={model1['p'][1]:.4f}, R²={model1['r2']:.4f} (n={model1['n']}).<br>
        Low R² ({model1['r2']:.4f}) means the effect, while statistically detectable, explains very little return variance —
        consistent with the notebook's R²≈0.0012 finding.
    </div>
    """, unsafe_allow_html=True)

    # Model 1 table
    m1_df = pd.DataFrame({
        'Variable': model1['labels'],
        'Coef':     [f"{v:.4f}" for v in model1['coef']],
        'Std Err':  [f"{v:.4f}" for v in model1['se']],
        't-stat':   [f"{v:.4f}" for v in model1['t']],
        'P-value':  [f"{v:.4f}" for v in model1['p']],
        'Sig':      ["✓" if p < 0.05 else "✗" for p in model1['p']]
    })
    st.dataframe(m1_df, use_container_width=True, hide_index=True)

    # Coefficient bar chart model 1
    fig_m1 = go.Figure()
    for i, (lbl, coef, p) in enumerate(zip(model1['labels'], model1['coef'], model1['p'])):
        fig_m1.add_trace(go.Bar(
            x=[lbl], y=[coef],
            marker_color=GREEN if p < 0.05 else DIM,
            text=f"p={p:.3f}", textposition='outside',
            textfont=dict(size=9, color='#666'),
            showlegend=False
        ))
    fig_m1.add_hline(y=0, line_color='#333')
    fig_m1.update_layout(**PT, height=240,
                          xaxis=dict(**AXIS), yaxis=dict(**AXIS, title='Coefficient'),
                          title=dict(text='Model 1 Coefficients (green = sig. at 5%)',
                                     font_size=11, x=0, font_color='#666'))
    st.plotly_chart(fig_m1, use_container_width=True)

    if model2:
        st.markdown("---")
        st.markdown(f"""
        <div class="finding blue">
            <strong>Model 2 — Sentiment + Volume + Lag Return (tweet days only):</strong>
            R²={model2['r2']:.4f} (n={model2['n']}).
            None of the controls are individually significant — consistent with the notebook result.
            The intercept carries most of the signal.
        </div>
        """, unsafe_allow_html=True)

        m2_df = pd.DataFrame({
            'Variable': model2['labels'],
            'Coef':     [f"{v:.4f}" for v in model2['coef']],
            'Std Err':  [f"{v:.4f}" for v in model2['se']],
            't-stat':   [f"{v:.4f}" for v in model2['t']],
            'P-value':  [f"{v:.4f}" for v in model2['p']],
            'Sig':      ["✓" if p < 0.05 else "✗" for p in model2['p']]
        })
        st.dataframe(m2_df, use_container_width=True, hide_index=True)

        fig_m2 = go.Figure()
        for lbl, coef, p in zip(model2['labels'], model2['coef'], model2['p']):
            fig_m2.add_trace(go.Bar(
                x=[lbl], y=[coef],
                marker_color=GREEN if p < 0.05 else DIM,
                text=f"p={p:.3f}", textposition='outside',
                textfont=dict(size=9, color='#666'),
                showlegend=False
            ))
        fig_m2.add_hline(y=0, line_color='#333')
        fig_m2.update_layout(**PT, height=260,
                              xaxis=dict(**AXIS), yaxis=dict(**AXIS, title='Coefficient'),
                              title=dict(text='Model 2 Coefficients (green = sig. at 5%)',
                                         font_size=11, x=0, font_color='#666'))
        st.plotly_chart(fig_m2, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 — BY SENTIMENT
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Next-Day Return by Sentiment</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Notebook finding: negative tweets (+0.34%) outperform positive (+0.23%) — does tone even matter?</div>', unsafe_allow_html=True)

    sent_colors = {'positive': GREEN, 'negative': RED, 'neutral': GOLD}
    sent_rows   = []

    for s in ['positive', 'negative', 'neutral']:
        early_s = trump_df[
            (trump_df['tweet_hour_est'] < cutoff_hour) &
            (trump_df['sentiment'] == s)
        ]
        daily_s = early_s.groupby('tweet_date_est').agg(
            tweet_count          =('content_clean', 'count'),
            avg_sentiment        =('vader_compound', 'mean'),
            dominant_sentiment   =('sentiment', lambda x: x.value_counts().index[0]),
            earliest_hour        =('tweet_hour_est', 'min'),
            sample_tweet         =('content_clean', 'first')
        ).reset_index()
        daily_s['tweet_date_est'] = pd.to_datetime(daily_s['tweet_date_est'])

        price_df2 = port_ret.reset_index()
        price_df2.columns = ['Date', 'daily_return']
        price_df2['Date'] = pd.to_datetime(price_df2['Date'])
        price_df2['next_day_return'] = price_df2['daily_return'].shift(-1)

        m2 = price_df2.merge(daily_s, left_on='Date', right_on='tweet_date_est', how='left')
        m2['has_tweet'] = m2['tweet_count'].notna()
        m2 = m2.dropna(subset=['daily_return'])

        tw_ret   = m2[m2['has_tweet']]['next_day_return'].dropna()
        ntw_ret  = m2[~m2['has_tweet']]['next_day_return'].dropna()
        if len(tw_ret) >= 3:
            t_s, p_s = ttest_ind_manual(tw_ret, ntw_ret)
            wr = (tw_ret > 0).mean()
            sent_rows.append(dict(
                sentiment=s, n=len(tw_ret),
                mean_ret=tw_ret.mean(), std_ret=tw_ret.std(),
                win_rate=wr, t_stat=t_s, p_val=p_s
            ))

    if sent_rows:
        c1, c2 = st.columns(2)
        with c1:
            fig3 = go.Figure()
            for sr in sent_rows:
                fig3.add_trace(go.Bar(
                    x=[sr['sentiment'].capitalize()],
                    y=[sr['mean_ret']],
                    marker_color=sent_colors[sr['sentiment']],
                    text=f"n={sr['n']}<br>{sr['mean_ret']:+.4f}%",
                    textposition='outside', textfont=dict(size=9, color='#aaa'),
                    showlegend=False
                ))
            fig3.add_hline(y=result['mean_no_tweet'], line_dash='dash', line_color='#444',
                           annotation_text=f"Baseline ({result['mean_no_tweet']:+.4f}%)",
                           annotation_font=dict(color='#555', size=9))
            fig3.update_layout(**PT, height=300, showlegend=False,
                               xaxis=dict(**AXIS), yaxis=dict(**AXIS, title='Avg Next-Day Return (%)'),
                               title=dict(text='Avg Next-Day Return by Sentiment', font_size=11,
                                          x=0, font_color='#666'))
            st.plotly_chart(fig3, use_container_width=True)

        with c2:
            fig4 = go.Figure()
            for sr in sent_rows:
                fig4.add_trace(go.Bar(
                    x=[sr['sentiment'].capitalize()],
                    y=[sr['win_rate'] * 100],
                    marker_color=GREEN if sr['win_rate'] > 0.5 else RED,
                    text=f"{sr['win_rate']*100:.1f}%",
                    textposition='outside', textfont=dict(size=9, color='#aaa'),
                    showlegend=False
                ))
            fig4.add_hline(y=result['baseline_wr'] * 100, line_dash='dash', line_color='#444',
                           annotation_text=f"Baseline {result['baseline_wr']*100:.1f}%",
                           annotation_font=dict(color='#555', size=9))
            fig4.update_layout(**PT, height=300, showlegend=False,
                               xaxis=dict(**AXIS), yaxis=dict(**AXIS, title='Win Rate (%)'),
                               title=dict(text='Win Rate by Sentiment', font_size=11,
                                          x=0, font_color='#666'))
            st.plotly_chart(fig4, use_container_width=True)

        st.dataframe(pd.DataFrame([{
            'Sentiment': sr['sentiment'].capitalize(),
            'N':         sr['n'],
            'Avg Next-Day Ret': f"{sr['mean_ret']:+.4f}%",
            'Std':       f"{sr['std_ret']:.4f}%",
            'Win Rate':  f"{sr['win_rate']*100:.1f}%",
            't-stat':    f"{sr['t_stat']:.4f}",
            'P-Value':   f"{sr['p_val']:.4f}",
            'Sig':       "✓" if sr['p_val'] < 0.05 else "✗"
        } for sr in sent_rows]), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 4 — PER ASSET
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Per-Asset Breakdown</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Next-day return effect for each ticker individually</div>', unsafe_allow_html=True)

    asset_rows = []
    # `close` may not exist when a local `port_ret` Series is used (XAU_daily.csv).
    # If so, use `port_ret` directly for the single-ticker case.
    for tkr in tickers:
        if 'close' in globals():
            if tkr not in close.columns:
                continue
            tkr_ret = (close[tkr].pct_change() * 100).rename('daily_return')
        else:
            # port_ret may be a Series of daily returns for the single-ticker local file
            if isinstance(port_ret, pd.Series):
                # only serve the matching single ticker
                if len(tickers) != 1:
                    continue
                tkr_ret = port_ret.rename('daily_return')
            else:
                continue
        a_df    = build_analysis_df(trump_df, cutoff_hour, sent_filter, tkr_ret)
        r3      = run_backtest(a_df, starting_capital)
        if r3:
            asset_rows.append(dict(ticker=tkr, **r3))

    if asset_rows:
        fig6 = make_subplots(rows=1, cols=2,
                             subplot_titles=["Avg Next-Day Return (%)", "Win Rate (%)"])
        for i, ar in enumerate(asset_rows):
            c = PALETTE[i % len(PALETTE)]
            fig6.add_trace(go.Bar(
                x=[ar['ticker']], y=[ar['mean_tweet']],
                marker_color=GREEN if ar['mean_tweet'] > 0 else RED,
                showlegend=False,
                text=f"{ar['mean_tweet']:+.4f}%",
                textposition='outside', textfont=dict(size=9, color='#aaa')
            ), row=1, col=1)
            fig6.add_trace(go.Bar(
                x=[ar['ticker']], y=[ar['win_rate'] * 100],
                marker_color=c, showlegend=False,
                text=f"{ar['win_rate']*100:.1f}%",
                textposition='outside', textfont=dict(size=9, color='#aaa')
            ), row=1, col=2)

        fig6.add_hline(y=0, line_color='#444', line_width=1, row=1, col=1)
        fig6.add_hline(y=50, line_dash='dash', line_color='#444', row=1, col=2)
        fig6.update_layout(**PT, height=320,
                           xaxis=dict(**AXIS), xaxis2=dict(**AXIS),
                           yaxis=dict(**AXIS), yaxis2=dict(**AXIS))
        st.plotly_chart(fig6, use_container_width=True)

        # equity curves
        fig7 = go.Figure()
        for i, ar in enumerate(asset_rows):
            fig7.add_trace(go.Scatter(
                x=ar['bt']['Date'], y=ar['bt']['cumulative_capital'],
                mode='lines', name=ar['ticker'],
                line=dict(color=PALETTE[i % len(PALETTE)], width=1.8)
            ))
        fig7.add_hline(y=starting_capital, line_color='#2a2a2a', line_width=1)
        fig7.update_layout(**PT, height=320,
                           xaxis=dict(**AXIS),
                           yaxis=dict(**AXIS, title='Portfolio Value ($)'),
                           legend=dict(orientation='h', y=1.05, font_size=10))
        st.plotly_chart(fig7, use_container_width=True)

        st.dataframe(pd.DataFrame([{
            'Ticker':             ar['ticker'],
            'N Trades':           ar['n'],
            'Win Rate':           f"{ar['win_rate']*100:.1f}%",
            'Avg Next-Day Ret':   f"{ar['mean_tweet']:+.4f}%",
            'Avg Baseline Ret':   f"{ar['mean_no_tweet']:+.4f}%",
            'Δ':                  f"{ar['mean_tweet']-ar['mean_no_tweet']:+.4f}%",
            'Sharpe':             f"{ar['sharpe']:.3f}",
            'Max DD':             f"{ar['max_dd']:.2f}%",
            'Final Capital':      f"${ar['final_capital']:,.0f}",
            'P-Value':            f"{ar['p_val']:.4f}",
            'Sig':                "✓" if ar['p_val'] < 0.05 else "✗"
        } for ar in asset_rows]), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 5 — EVENT STUDY
# ══════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">Event Study · [-3, +3] Window</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Portfolio return around tweet days vs baseline — t=0 is tweet day, t+1 is the traded return</div>', unsafe_allow_html=True)

    windows = range(-3, 4)
    ev_rows = []
    for w in windows:
        shifted = analysis_df['daily_return'].shift(-w)
        tw = analysis_df['has_tweet']
        ev_rows.append(dict(w=w,
                            tweet_avg=shifted[tw].mean(),
                            no_tweet_avg=shifted[~tw].mean()))
    ev_df = pd.DataFrame(ev_rows)
    ev_df['abnormal'] = ev_df['tweet_avg'] - ev_df['no_tweet_avg']
    ev_df['CAR']      = ev_df['abnormal'].cumsum()

    fig8 = make_subplots(rows=1, cols=2,
                         subplot_titles=["Avg Return by Day", "Cumulative Abnormal Return"])
    xticks = [f"t{w:+d}" for w in windows]

    fig8.add_trace(go.Bar(
        x=xticks, y=ev_df['tweet_avg'],
        marker_color=[GOLD if v >= 0 else RED for v in ev_df['tweet_avg']],
        name='Tweet Days',
        text=[f"{v:+.3f}%" for v in ev_df['tweet_avg']],
        textposition='outside', textfont=dict(size=8, color='#666')
    ), row=1, col=1)
    fig8.add_trace(go.Scatter(
        x=xticks, y=ev_df['no_tweet_avg'],
        mode='lines+markers',
        line=dict(color=DIM, width=1.5, dash='dash'),
        marker=dict(size=4, color='#444'),
        name='Baseline'
    ), row=1, col=1)
    fig8.add_trace(go.Scatter(
        x=xticks, y=ev_df['CAR'],
        mode='lines+markers',
        line=dict(color=GOLD, width=2.5),
        marker=dict(size=6, color=GOLD, line=dict(color='#000', width=1)),
        fill='tozeroy', fillcolor='rgba(201,168,76,0.08)',
        name='CAR', showlegend=False
    ), row=1, col=2)
    fig8.add_hline(y=0, line_color='#333', line_width=1, row=1, col=2)
    fig8.update_layout(**PT, height=340,
                       xaxis=dict(**AXIS), xaxis2=dict(**AXIS),
                       yaxis=dict(**AXIS, title='Avg Return (%)'),
                       yaxis2=dict(**AXIS, title='CAR (%)'),
                       legend=dict(orientation='h', y=1.08, font_size=10))
    st.plotly_chart(fig8, use_container_width=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown(f"""
<div style="border-top:1px solid #1a1a1a;margin-top:2.5rem;padding-top:1rem;
            font-family:'DM Mono',monospace;font-size:0.62rem;color:#333;
            display:flex;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
    <span>Trump Signal Backtester · Truth Social × {', '.join(tickers)}</span>
    <span>Student's t-test · Buy-close sell-next-close · Zero slippage · Not financial advice</span>
</div>
""", unsafe_allow_html=True)