import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
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
    grid-template-columns: repeat(5, 1fr);
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

    market_prob = st.slider("Polymarket implied prob (%)", 45, 70, 55,
                             help="What % the market prices the asset going UP") / 100

    stake = st.number_input("Stake per bet ($)", min_value=10,
                             max_value=10000, value=100, step=10)

    st.markdown("---")
    run_btn = st.button("▶  RUN BACKTEST", use_container_width=True)

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Signal Backtester · Truth Social × Markets · Polymarket Edge Finder</div>
    <h1 class="hero-title">Does Trump Move <span>Your Assets?</span></h1>
    <p class="hero-sub">
        Test whether Trump's Truth Social posts on tariffs, trade, and macro predict
        same-day direction across gold, stocks, and custom portfolios.
        Find your Polymarket edge before placing a bet.
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

def build_portfolio_returns(close_df, equal_weight=True):
    rets = close_df.pct_change()
    if equal_weight or close_df.shape[1] == 1:
        port = rets.mean(axis=1)
    else:
        vol = rets.rolling(21).std().iloc[-1]
        w   = (1 / vol) / (1 / vol).sum()
        port = (rets * w).sum(axis=1)
    return (port * 100).rename('port_return')

def build_signal_df(trump_df, cutoff, sentiment_list, port_returns):
    early = trump_df[
        (trump_df['tweet_hour_est'] < cutoff) &
        (trump_df['sentiment'].isin(sentiment_list))
    ].copy()

    daily = early.groupby('tweet_date_est').agg(
        tweet_count    =('content_clean', 'count'),
        avg_sentiment  =('vader_compound', 'mean'),
        dominant_sentiment=('sentiment', lambda x: x.value_counts().index[0]),
        earliest_hour  =('tweet_hour_est', 'min'),
        sample_tweet   =('content_clean', 'first')
    ).reset_index()
    daily['tweet_date_est'] = pd.to_datetime(daily['tweet_date_est'])

    price_df = port_returns.reset_index()
    price_df.columns = ['Date', 'port_return']
    price_df['Date'] = pd.to_datetime(price_df['Date'])

    merged = price_df.merge(daily, left_on='Date', right_on='tweet_date_est', how='left')
    merged['has_tweet'] = merged['tweet_count'].notna()
    merged['direction'] = (merged['port_return'] > 0).astype(float)
    return merged.dropna(subset=['port_return'])

def run_backtest(signal_df, mkt_prob, stake_amt):
    bt = signal_df[signal_df['has_tweet']].dropna(
        subset=['direction']).sort_values('Date').copy()
    if len(bt) < 3:
        return None

    payout_win   = stake_amt * (1 / mkt_prob - 1)
    bt['pnl']    = bt['direction'].apply(lambda x: payout_win if x == 1 else -stake_amt)
    bt['bankroll'] = bt['pnl'].cumsum()

    n        = len(bt)
    win_rate = bt['direction'].mean()
    total    = bt['pnl'].sum()
    roi      = total / (stake_amt * n) * 100
    ev       = stake_amt * (win_rate * (1/mkt_prob - 1) - (1 - win_rate))
    b        = 1/mkt_prob - 1
    kelly    = (b * win_rate - (1 - win_rate)) / b

    tweet_ret    = signal_df[signal_df['has_tweet']]['port_return'].dropna()
    no_tweet_ret = signal_df[~signal_df['has_tweet']]['port_return'].dropna()
    
    if len(no_tweet_ret) > 1 and len(tweet_ret) > 1:
        mean1, mean2 = tweet_ret.mean(), no_tweet_ret.mean()
        var1, var2 = tweet_ret.var(ddof=1), no_tweet_ret.var(ddof=1)
        n1, n2 = len(tweet_ret), len(no_tweet_ret)
        
        # Welch's t-test statistic
        se = np.sqrt(var1/n1 + var2/n2)
        t_stat = (mean1 - mean2) / se if se > 0 else 0
        
        # Normal approximation for p-value (two-tailed)
        def norm_cdf(x):
            return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
            
        p_val = 2 * (1 - norm_cdf(abs(t_stat)))
    else:
        p_val = 1.0

    baseline_wr = (no_tweet_ret > 0).mean()

    return dict(n=n, win_rate=win_rate, total_pnl=total, roi=roi, ev=ev,
                kelly=kelly, p_val=p_val, positive_ev=ev > 0,
                bt=bt, tweet_ret=tweet_ret, no_tweet_ret=no_tweet_ret,
                baseline_wr=baseline_wr)

# ─────────────────────────────────────────────
# LOAD TRUMP (always from disk)
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
        close    = fetch_prices(tuple(tickers), str(date_min), str(date_max))
        port_ret = build_portfolio_returns(close, equal_weight)
    except Exception as e:
        st.error(f"yfinance error: {e}")
        st.stop()

# ─────────────────────────────────────────────
# BUILD SIGNAL & BACKTEST
# ─────────────────────────────────────────────
signal_df = build_signal_df(trump_df, cutoff_hour, sent_filter, port_ret)
result    = run_backtest(signal_df, market_prob, stake)

if result is None:
    st.error("No tweet days matched your filters. Widen the sentiment filter or cutoff hour.")
    st.stop()

# ─────────────────────────────────────────────
# STAT CARDS
# ─────────────────────────────────────────────
wr_class  = "green" if result['win_rate'] > market_prob else "red"
pnl_class = "green" if result['total_pnl'] > 0 else "red"
ev_class  = "green" if result['ev'] > 0 else "red"
k_class   = "green" if result['kelly'] > 0 else "red"
p_class   = "green" if result['p_val'] < 0.05 else ""

st.markdown(f"""
<div class="stat-grid">
    <div class="stat-card">
        <div class="stat-label">Win Rate (Tweet Days)</div>
        <div class="stat-value {wr_class}">{result['win_rate']*100:.1f}%</div>
        <div class="stat-delta">vs {result['baseline_wr']*100:.1f}% baseline · {result['n']} bets</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Total PnL (${stake}/bet)</div>
        <div class="stat-value {pnl_class}">${result['total_pnl']:+,.0f}</div>
        <div class="stat-delta">ROI {result['roi']:+.1f}%</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">EV per Bet</div>
        <div class="stat-value {ev_class}">${result['ev']:+.2f}</div>
        <div class="stat-delta">at {market_prob:.0%} implied odds</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Kelly Fraction</div>
        <div class="stat-value {k_class}">{result['kelly']*100:.1f}%</div>
        <div class="stat-delta">½ Kelly = {result['kelly']*50:.1f}% of bankroll</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">P-Value (t-test)</div>
        <div class="stat-value {p_class}">{result['p_val']:.4f}</div>
        <div class="stat-delta">{"✓ Sig. at 5%" if result['p_val'] < 0.05 else "✗ Not sig. at 5%"}</div>
    </div>
</div>
""", unsafe_allow_html=True)

ev_color   = "green" if result['ev'] > 0 else "red"
ev_verdict = (
    f"<strong>+EV at {market_prob:.0%} implied odds.</strong> "
    f"Every ${stake} bet returns ${result['ev']:+.2f} in expectation. "
    f"Half-Kelly sizing = {result['kelly']*50:.1f}% of bankroll per bet."
    if result['ev'] > 0 else
    f"<strong>-EV at {market_prob:.0%} implied odds.</strong> "
    f"Market is too efficient at this probability. "
    f"Try tightening the sentiment filter or lowering the cutoff hour."
)
st.markdown(f'<div class="finding {ev_color}">{ev_verdict}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💹  Equity Curve",
    "🎯  Odds Sweep",
    "🎭  By Sentiment",
    "📊  Per Asset",
    "🔬  Event Study",
])

# ══════════════════════════════════════════════
# TAB 1 — EQUITY CURVE
# ══════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Strategy Equity Curve</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Bet UP on portfolio every Trump tweet day · ${stake}/bet · {market_prob:.0%} implied odds · before {cutoff_hour}:00 EST</div>', unsafe_allow_html=True)

    bt = result['bt']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=bt['Date'], y=bt['bankroll'],
        mode='lines', name='Cumulative PnL',
        line=dict(color=GOLD, width=2.5),
        fill='tozeroy', fillcolor='rgba(201,168,76,0.07)'
    ))
    fig.add_hline(y=0, line_color='#2a2a2a', line_width=1)

    # Win/loss tick marks
    wins   = bt[bt['pnl'] > 0]
    losses = bt[bt['pnl'] < 0]
    fig.add_trace(go.Scatter(
        x=wins['Date'], y=wins['bankroll'],
        mode='markers', marker=dict(color=GREEN, size=5, symbol='circle'),
        name='Win', opacity=0.7
    ))
    fig.add_trace(go.Scatter(
        x=losses['Date'], y=losses['bankroll'],
        mode='markers', marker=dict(color=RED, size=5, symbol='circle'),
        name='Loss', opacity=0.7
    ))

    fig.update_layout(**PT, height=380,
                      xaxis=dict(**AXIS),
                      yaxis=dict(**AXIS, title='Cumulative PnL ($)'),
                      legend=dict(orientation='h', y=1.05, font_size=10))
    st.plotly_chart(fig, use_container_width=True)

    # Trade log
    st.markdown('<div class="section-header" style="font-size:1rem;margin-top:0.5rem">Trade Log</div>', unsafe_allow_html=True)
    log = bt[['Date','dominant_sentiment','earliest_hour',
              'port_return','pnl','bankroll','sample_tweet']].copy()
    log.columns = ['Date','Sentiment','Tweet Hour EST',
                   'Asset Ret %','PnL $','Cumul PnL $','Sample Tweet']
    log['Asset Ret %'] = log['Asset Ret %'].round(3)
    log['PnL $']       = log['PnL $'].round(2)
    log['Cumul PnL $'] = log['Cumul PnL $'].round(2)
    log['Sample Tweet'] = log['Sample Tweet'].str[:90] + '...'
    st.dataframe(log.sort_values('Date', ascending=False),
                 use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 2 — ODDS SWEEP
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">EV Across Polymarket Odds</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">At what implied probability does your edge disappear?</div>', unsafe_allow_html=True)

    sweep_rows = []
    for p in np.arange(0.45, 0.76, 0.01):
        r = run_backtest(signal_df, p, stake)
        if r:
            sweep_rows.append(dict(implied_prob=p, ev=r['ev'],
                                   kelly=r['kelly']*100,
                                   total_pnl=r['total_pnl'],
                                   positive_ev=r['ev'] > 0))
    sweep_df = pd.DataFrame(sweep_rows)

    breakeven = (sweep_df[sweep_df['ev'] >= 0]['implied_prob'].max()
                 if len(sweep_df[sweep_df['ev'] >= 0]) else None)

    fig2 = make_subplots(rows=1, cols=2,
                         subplot_titles=["EV per Bet ($)", "Kelly Fraction (%)"])
    fig2.add_trace(go.Bar(
        x=(sweep_df['implied_prob']*100).round(0), y=sweep_df['ev'],
        marker_color=[GREEN if v else RED for v in sweep_df['positive_ev']],
        showlegend=False
    ), row=1, col=1)
    fig2.add_hline(y=0, line_color='#444', line_width=1, row=1, col=1)
    fig2.add_trace(go.Scatter(
        x=(sweep_df['implied_prob']*100).round(0), y=sweep_df['kelly'],
        line=dict(color=GOLD, width=2), mode='lines', showlegend=False
    ), row=1, col=2)
    fig2.add_hline(y=0, line_color='#444', line_width=1, row=1, col=2)
    fig2.update_layout(**PT, height=340,
                       xaxis=dict(**AXIS, title='Implied Prob (%)'),
                       xaxis2=dict(**AXIS, title='Implied Prob (%)'),
                       yaxis=dict(**AXIS), yaxis2=dict(**AXIS))
    st.plotly_chart(fig2, use_container_width=True)

    if breakeven:
        status = "✓ you have edge" if market_prob <= breakeven else "✗ no edge at current setting"
        st.markdown(f"""
        <div class="finding green">
            <strong>Breakeven: {breakeven:.0%} implied odds.</strong>
            Your edge is positive as long as Polymarket prices below <strong>{breakeven:.0%}</strong>.
            Current setting: {market_prob:.0%} → {status}.
        </div>
        """, unsafe_allow_html=True)

    st.dataframe(sweep_df.assign(**{
        'Implied Prob': (sweep_df['implied_prob']*100).map('{:.0f}%'.format),
        'EV/Bet ($)':   sweep_df['ev'].map('${:+.2f}'.format),
        'Kelly (%)':    sweep_df['kelly'].map('{:.1f}%'.format),
        'Total PnL':    sweep_df['total_pnl'].map('${:+,.0f}'.format),
        '+EV?':         sweep_df['positive_ev'].map({True:'✓ YES', False:'✗ NO'})
    })[['Implied Prob','EV/Bet ($)','Kelly (%)','Total PnL','+EV?']],
    use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 3 — BY SENTIMENT
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Win Rate & EV by Tweet Sentiment</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Does tone matter, or just the topic?</div>', unsafe_allow_html=True)

    sent_colors = {'positive': GREEN, 'negative': RED, 'neutral': GOLD}
    sent_rows   = []

    for s in ['positive', 'negative', 'neutral']:
        early_s = trump_df[
            (trump_df['tweet_hour_est'] < cutoff_hour) &
            (trump_df['sentiment'] == s)
        ]
        daily_s = early_s.groupby('tweet_date_est').agg(
            tweet_count       =('content_clean', 'count'),
            avg_sentiment     =('vader_compound', 'mean'),
            dominant_sentiment=('sentiment', lambda x: x.value_counts().index[0]),
            earliest_hour     =('tweet_hour_est', 'min'),
            sample_tweet      =('content_clean', 'first')
        ).reset_index()
        daily_s['tweet_date_est'] = pd.to_datetime(daily_s['tweet_date_est'])

        price_df2 = port_ret.reset_index()
        price_df2.columns = ['Date', 'port_return']
        price_df2['Date'] = pd.to_datetime(price_df2['Date'])
        m2 = price_df2.merge(daily_s, left_on='Date',
                              right_on='tweet_date_est', how='left')
        m2['has_tweet'] = m2['tweet_count'].notna()
        m2['direction'] = (m2['port_return'] > 0).astype(float)
        m2 = m2.dropna(subset=['port_return'])

        r2 = run_backtest(m2, market_prob, stake)
        if r2 and r2['n'] >= 3:
            sent_rows.append(dict(sentiment=s, **r2))

    if sent_rows:
        c1, c2 = st.columns(2)
        with c1:
            fig3 = go.Figure()
            for sr in sent_rows:
                fig3.add_trace(go.Bar(
                    x=[sr['sentiment'].capitalize()],
                    y=[sr['win_rate']*100],
                    marker_color=sent_colors[sr['sentiment']],
                    text=f"n={sr['n']}<br>{sr['win_rate']*100:.1f}%",
                    textposition='outside', textfont=dict(size=9, color='#aaa'),
                    showlegend=False
                ))
            fig3.add_hline(y=market_prob*100, line_dash='dash', line_color='#444',
                           annotation_text=f"Market odds ({market_prob:.0%})",
                           annotation_font=dict(color='#555', size=9))
            fig3.update_layout(**PT, height=300, showlegend=False,
                               xaxis=dict(**AXIS), yaxis=dict(**AXIS, title='Win Rate (%)'),
                               title=dict(text='Win Rate by Sentiment', font_size=11,
                                          x=0, font_color='#666'))
            st.plotly_chart(fig3, use_container_width=True)

        with c2:
            fig4 = go.Figure()
            for sr in sent_rows:
                fig4.add_trace(go.Bar(
                    x=[sr['sentiment'].capitalize()],
                    y=[sr['ev']],
                    marker_color=GREEN if sr['ev'] > 0 else RED,
                    text=f"${sr['ev']:+.2f}",
                    textposition='outside', textfont=dict(size=9, color='#aaa'),
                    showlegend=False
                ))
            fig4.add_hline(y=0, line_color='#333', line_width=1)
            fig4.update_layout(**PT, height=300, showlegend=False,
                               xaxis=dict(**AXIS), yaxis=dict(**AXIS, title='EV/Bet ($)'),
                               title=dict(text='EV per Bet by Sentiment', font_size=11,
                                          x=0, font_color='#666'))
            st.plotly_chart(fig4, use_container_width=True)

        # Equity curves
        fig5 = go.Figure()
        for sr in sent_rows:
            fig5.add_trace(go.Scatter(
                x=sr['bt']['Date'], y=sr['bt']['bankroll'],
                mode='lines', name=sr['sentiment'].capitalize(),
                line=dict(color=sent_colors[sr['sentiment']], width=2)
            ))
        fig5.add_hline(y=0, line_color='#2a2a2a', line_width=1)
        fig5.update_layout(**PT, height=280,
                           xaxis=dict(**AXIS),
                           yaxis=dict(**AXIS, title='Cumulative PnL ($)'),
                           legend=dict(orientation='h', y=1.05, font_size=10))
        st.plotly_chart(fig5, use_container_width=True)

        st.dataframe(pd.DataFrame([{
            'Sentiment': sr['sentiment'].capitalize(),
            'N Bets':    sr['n'],
            'Win Rate':  f"{sr['win_rate']*100:.1f}%",
            'EV/Bet':    f"${sr['ev']:+.2f}",
            'Kelly %':   f"{sr['kelly']*100:.1f}%",
            'Total PnL': f"${sr['total_pnl']:+,.0f}",
            '+EV?':      "✓ YES" if sr['positive_ev'] else "✗ NO"
        } for sr in sent_rows]), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 4 — PER ASSET
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Per-Asset Breakdown</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">How does each ticker respond individually to Trump posts?</div>', unsafe_allow_html=True)

    asset_rows = []
    for tkr in tickers:
        if tkr not in close.columns:
            continue
        tkr_ret = (close[tkr].pct_change() * 100).rename('port_return')
        sig2 = build_signal_df(trump_df, cutoff_hour, sent_filter, tkr_ret)
        r3   = run_backtest(sig2, market_prob, stake)
        if r3:
            asset_rows.append(dict(ticker=tkr, **r3))

    if asset_rows:
        fig6 = make_subplots(rows=1, cols=2,
                             subplot_titles=["Win Rate (%)", "EV per Bet ($)"])
        for i, ar in enumerate(asset_rows):
            c = PALETTE[i % len(PALETTE)]
            fig6.add_trace(go.Bar(
                x=[ar['ticker']], y=[ar['win_rate']*100],
                marker_color=c, showlegend=False,
                text=f"{ar['win_rate']*100:.1f}%",
                textposition='outside', textfont=dict(size=9, color='#aaa')
            ), row=1, col=1)
            fig6.add_trace(go.Bar(
                x=[ar['ticker']], y=[ar['ev']],
                marker_color=GREEN if ar['ev'] > 0 else RED,
                showlegend=False,
                text=f"${ar['ev']:+.2f}",
                textposition='outside', textfont=dict(size=9, color='#aaa')
            ), row=1, col=2)

        fig6.add_hline(y=market_prob*100, line_dash='dash',
                       line_color='#444', row=1, col=1)
        fig6.add_hline(y=0, line_color='#444', line_width=1, row=1, col=2)
        fig6.update_layout(**PT, height=320,
                           xaxis=dict(**AXIS), xaxis2=dict(**AXIS),
                           yaxis=dict(**AXIS), yaxis2=dict(**AXIS))
        st.plotly_chart(fig6, use_container_width=True)

        fig7 = go.Figure()
        for i, ar in enumerate(asset_rows):
            fig7.add_trace(go.Scatter(
                x=ar['bt']['Date'], y=ar['bt']['bankroll'],
                mode='lines', name=ar['ticker'],
                line=dict(color=PALETTE[i % len(PALETTE)], width=1.8)
            ))
        fig7.add_hline(y=0, line_color='#2a2a2a', line_width=1)
        fig7.update_layout(**PT, height=320,
                           xaxis=dict(**AXIS),
                           yaxis=dict(**AXIS, title='Cumulative PnL ($)'),
                           legend=dict(orientation='h', y=1.05, font_size=10))
        st.plotly_chart(fig7, use_container_width=True)

        st.dataframe(pd.DataFrame([{
            'Ticker':            ar['ticker'],
            'N Bets':            ar['n'],
            'Win Rate':          f"{ar['win_rate']*100:.1f}%",
            'EV/Bet':            f"${ar['ev']:+.2f}",
            'Kelly %':           f"{ar['kelly']*100:.1f}%",
            'Total PnL':         f"${ar['total_pnl']:+,.0f}",
            'Avg Ret (tweet)':   f"{ar['tweet_ret'].mean():+.3f}%",
            'Avg Ret (no tweet)':f"{ar['no_tweet_ret'].mean():+.3f}%",
            'P-Value':           f"{ar['p_val']:.4f}",
            '+EV?':              "✓ YES" if ar['positive_ev'] else "✗ NO"
        } for ar in asset_rows]), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 5 — EVENT STUDY
# ══════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">Event Study · [-3, +3] Window</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Portfolio return around tweet days vs baseline — when does the signal arrive?</div>', unsafe_allow_html=True)

    windows = range(-3, 4)
    ev_rows = []
    for w in windows:
        shifted = signal_df['port_return'].shift(-w)
        tw = signal_df['has_tweet']
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
    <span>VADER Sentiment · Zero slippage assumption · Not financial advice</span>
</div>
""", unsafe_allow_html=True)