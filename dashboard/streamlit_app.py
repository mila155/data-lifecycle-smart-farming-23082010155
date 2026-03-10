import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Smart Farming Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

    .stApp { background-color: #0e1117; color: #e0e0e0; }

    div[data-testid="stSidebar"] {
        background-color: #0a0d13 !important;
        border-right: 1px solid #1e2433 !important;
    }
    div[data-testid="stSidebar"] * { color: #c8d0de !important; }

    .metric-card {
        background: linear-gradient(135deg, #1a1f2e, #141820);
        border: 1px solid #2a3040;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 1px 8px rgba(0,0,0,0.3);
    }
    .metric-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 2.2rem;
        font-weight: 600;
        line-height: 1;
    }
    .metric-label {
        font-size: 0.78rem;
        color: #7a8394;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 6px;
    }
    .alert-red {
        background: #2d0e0e;
        border: 1px solid #8b1a1a;
        border-radius: 10px;
        padding: 12px 16px;
        color: #ff6b6b;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        margin: 4px 0;
    }
    .alert-green {
        background: #0d2010;
        border: 1px solid #1a5c2a;
        border-radius: 10px;
        padding: 12px 16px;
        color: #4caf50;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        margin: 4px 0;
    }
    .section-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 3px;
        color: #4a9eff;
        text-transform: uppercase;
        border-bottom: 1px solid #2a3040;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

T = {
    'plot_bg':      'rgba(20,24,32,0.8)',
    'grid':         '#1e2433',
    'font_color':   '#a0aec0',
    'text_muted':   '#7a8394',
    'heatmap_bg':   '#141820',
    'heatmap_text': 'white',
    'tick_color':   '#a0aec0',
    'gauge_bg':     '#1a1f2e',
    'gauge_border': '#2a3040',
}

@st.cache_data
def load_data():
    df1 = pd.read_csv('data/raw/plant_vase1.CSV');    df1['source'] = 'vase1_bunga'
    df2 = pd.read_csv('data/raw/plant_vase1(2).CSV'); df2['source'] = 'vase1_bunga_2'
    df3 = pd.read_csv('data/raw/plant_vase2.CSV');    df3['source'] = 'vase2_tanah'
    df = pd.concat([df1, df2, df3], ignore_index=True)
    df.rename(columns={'irrgation': 'irrigation'}, inplace=True)
    df['datetime'] = pd.to_datetime(df[['year','month','day','hour','minute','second']])
    df = df.sort_values(['source','datetime']).reset_index(drop=True)
    return df

df = load_data()
moisture_cols = ['moisture0','moisture1','moisture2','moisture3','moisture4']
SOURCE_LABELS = {
    'vase1_bunga':   'Pot 1A — Tanah & Bunga',
    'vase1_bunga_2': 'Pot 1B — Tanah & Bunga',
    'vase2_tanah':   'Pot 2 — Tanah Saja'
}
THRESHOLD = 0.30

with st.sidebar:
    st.markdown("## Smart Farming")
    st.markdown("**Soil Moisture IoT Dashboard**")
    st.markdown("---")

    st.markdown("### Filter Data")
    selected_sources = st.multiselect(
        "Sumber Sensor",
        options=list(SOURCE_LABELS.keys()),
        default=list(SOURCE_LABELS.keys()),
        format_func=lambda x: SOURCE_LABELS[x]
    )

    st.markdown("### Threshold Kelembaban")
    threshold = st.slider(
        "Batas kering (alert merah)",
        min_value=0.10, max_value=0.60,
        value=THRESHOLD, step=0.05, format="%.2f"
    )

    st.markdown("### Sensor")
    selected_sensors = st.multiselect(
        "Sensor yang Ditampilkan",
        options=moisture_cols,
        default=moisture_cols
    )

    st.markdown("### Rentang Waktu")
    time_mode = st.radio(
        "Mode tampilan",
        options=["Harian", "Mingguan", "Bulanan", "Custom"],
        index=2
    )

    global_min = df['datetime'].min().date()
    global_max = df['datetime'].max().date()

    if time_mode == "Harian":
        picked = st.date_input("Pilih tanggal", value=global_max,
                               min_value=global_min, max_value=global_max)
        date_start = pd.Timestamp(picked)
        date_end   = date_start + pd.Timedelta(days=1)
    elif time_mode == "Mingguan":
        picked = st.date_input("Pilih tanggal akhir minggu", value=global_max,
                               min_value=global_min, max_value=global_max)
        date_start = pd.Timestamp(picked) - pd.Timedelta(days=6)
        date_end   = pd.Timestamp(picked) + pd.Timedelta(days=1)
    elif time_mode == "Bulanan":
        picked = st.date_input("Pilih bulan", value=global_max,
                               min_value=global_min, max_value=global_max)
        date_start = pd.Timestamp(picked).replace(day=1)
        date_end   = (date_start + pd.offsets.MonthEnd(1)) + pd.Timedelta(days=1)
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            d_start = st.date_input("Dari", value=global_min,
                                    min_value=global_min, max_value=global_max)
        with col_b:
            d_end = st.date_input("Sampai", value=global_max,
                                  min_value=global_min, max_value=global_max)
        date_start = pd.Timestamp(d_start)
        date_end   = pd.Timestamp(d_end) + pd.Timedelta(days=1)

    st.markdown("---")
    st.markdown('<div style="font-size:0.7rem;color:#4a5568;">Jamila Farhana<br>23082010155</div>',
                unsafe_allow_html=True)

if not selected_sources:
    st.warning("Pilih minimal satu sumber sensor.")
    st.stop()

df_filtered = df[
    (df['source'].isin(selected_sources)) &
    (df['datetime'] >= date_start) &
    (df['datetime'] < date_end)
].copy()

if df_filtered.empty:
    st.warning("Tidak ada data dalam rentang waktu yang dipilih.")
    st.stop()

df_filtered['avg_moisture'] = df_filtered[moisture_cols].mean(axis=1)

st.markdown("# Smart Farming — Soil Moisture Dashboard")
period_str = f"{date_start.strftime('%d %b %Y')} — {(date_end - pd.Timedelta(days=1)).strftime('%d %b %Y')}"
st.markdown(f"Monitoring kelembaban tanah dari sensor IoT · **{len(df_filtered):,} pembacaan** · {period_str} · threshold: **{threshold:.2f}**")
st.markdown("---")


st.markdown('<p class="section-title">ringkasan kondisi terkini</p>', unsafe_allow_html=True)
cols = st.columns(len(selected_sources) + 2)

for i, src in enumerate(selected_sources):
    subset     = df_filtered[df_filtered['source'] == src]
    latest_avg = subset[moisture_cols].iloc[-1].mean() if len(subset) > 0 else 0
    color  = "#ff4444" if latest_avg < threshold else "#4caf50" if latest_avg > 0.6 else "#ff9800"
    status = "KERING ⚠️" if latest_avg < threshold else "OPTIMAL ✅" if latest_avg > 0.6 else "SEDANG 💧"
    cols[i].markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color:{color}">{latest_avg:.2f}</div>
        <div class="metric-label">{SOURCE_LABELS[src][:20]}</div>
        <div style="font-size:0.75rem;color:{color};margin-top:8px;font-weight:600">{status}</div>
    </div>""", unsafe_allow_html=True)

n_alert   = (df_filtered['avg_moisture'] < threshold).sum()
pct_alert = n_alert / len(df_filtered) * 100
cols[-2].markdown(f"""
<div class="metric-card">
    <div class="metric-value" style="color:#ff6b6b">{n_alert:,}</div>
    <div class="metric-label">Total Alert Kering</div>
    <div style="font-size:0.75rem;color:#7a8394;margin-top:8px">{pct_alert:.1f}% dari total</div>
</div>""", unsafe_allow_html=True)

irr_count = int(df_filtered['irrigation'].sum())
cols[-1].markdown(f"""
<div class="metric-card">
    <div class="metric-value" style="color:#4a9eff">{irr_count:,}</div>
    <div class="metric-label">Total Irigasi Aktif</div>
    <div style="font-size:0.75rem;color:#7a8394;margin-top:8px">{irr_count/len(df_filtered)*100:.1f}% dari total</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


st.markdown('<p class="section-title">tren waktu & kondisi saat ini</p>', unsafe_allow_html=True)
col_ts, col_gauge = st.columns([3, 1])

with col_ts:
    n_rows  = len(selected_sources)
    palette = ['#4a9eff', '#26c6a0', '#ff6b6b', '#ffd166', '#a29bfe']

    fig = make_subplots(
        rows=n_rows, cols=1,
        shared_xaxes=False,
        subplot_titles=[SOURCE_LABELS[s] for s in selected_sources],
        vertical_spacing=0.12
    )

    for i, src in enumerate(selected_sources):
        subset = df_filtered[df_filtered['source'] == src].sort_values('datetime')

        for j, col in enumerate(selected_sensors):
            fig.add_trace(go.Scatter(
                x=subset['datetime'], y=subset[col],
                name=col,
                line=dict(width=1.2, color=palette[j % len(palette)]),
                opacity=0.85,
                showlegend=(i == 0)
            ), row=i+1, col=1)

        fig.add_hline(
            y=threshold, line_dash="dash",
            line_color="rgba(255,68,68,0.5)", line_width=1,
            row=i+1, col=1
        )

        x_min = subset['datetime'].min()
        x_max = subset['datetime'].max()
        xaxis_key = f"xaxis{'' if i == 0 else i + 1}"
        fig.update_layout(**{xaxis_key: dict(
            range=[x_min, x_max],
            showticklabels=True,
            tickformat="%d %b\n%Y",
            tickangle=0,
            gridcolor=T['grid'],
            zeroline=False,
            tickfont=dict(size=10, color=T['font_color'])
        )})

    fig.update_layout(
        height=280 * n_rows,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor=T['plot_bg'],
        font=dict(color=T['font_color'], family='IBM Plex Mono'),
        legend=dict(
            bgcolor='rgba(0,0,0,0)', font=dict(size=11),
            orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0
        ),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    fig.update_yaxes(
        gridcolor=T['grid'],
        zeroline=False,
        range=[0, 1],
        title_text="Kelembaban",
        title_font=dict(size=11, color=T['font_color']),
        tickformat=".1f"
    )
    st.plotly_chart(fig, use_container_width=True)

with col_gauge:
    st.markdown("**Kelembaban Terkini**")
    for src in selected_sources:
        subset = df_filtered[df_filtered['source'] == src]
        if len(subset) == 0:
            continue
        val   = subset[moisture_cols].iloc[-1].mean()
        color = "#ff4444" if val < threshold else "#4caf50" if val > 0.6 else "#ff9800"

        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(val, 3),
            number={'font': {'color': color, 'family': 'IBM Plex Mono', 'size': 26}},
            gauge={
                'axis': {'range': [0, 1], 'tickcolor': T['tick_color'], 'tickfont': {'size': 9}},
                'bar': {'color': color, 'thickness': 0.25},
                'bgcolor': T['gauge_bg'],
                'bordercolor': T['gauge_border'],
                'steps': [
                    {'range': [0, threshold],   'color': 'rgba(255,68,68,0.15)'},
                    {'range': [threshold, 0.6], 'color': 'rgba(255,152,0,0.1)'},
                    {'range': [0.6, 1],         'color': 'rgba(76,175,80,0.1)'}
                ],
                'threshold': {
                    'line': {'color': '#ff4444', 'width': 2},
                    'thickness': 0.75, 'value': threshold
                }
            }
        ))
        fig_g.update_layout(
            height=175,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=T['font_color']),
            margin=dict(l=15, r=15, t=25, b=5)
        )
        st.markdown(
            f"<div style='font-size:0.72rem;color:{T['text_muted']};text-align:center;margin-top:4px'>"
            f"{SOURCE_LABELS[src][:24]}</div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(fig_g, use_container_width=True)


st.markdown('<p class="section-title">korelasi antar sensor & alert system</p>', unsafe_allow_html=True)
col_heat, col_alert = st.columns([2, 1])

with col_heat:
    st.markdown("**Heatmap Korelasi Sensor Moisture**")
    tabs = st.tabs([SOURCE_LABELS[s][:18] for s in selected_sources])
    for tab, src in zip(tabs, selected_sources):
        with tab:
            subset = df_filtered[df_filtered['source'] == src][moisture_cols]
            corr   = subset.corr()
            fig_h, ax = plt.subplots(figsize=(5, 4))
            fig_h.patch.set_facecolor(T['heatmap_bg'])
            ax.set_facecolor(T['heatmap_bg'])
            sns.heatmap(
                corr, annot=True, fmt='.2f', cmap='YlOrRd', ax=ax,
                square=True, linewidths=0.5,
                annot_kws={'size': 10, 'color': T['heatmap_text']},
                cbar_kws={'shrink': 0.8}
            )
            ax.tick_params(colors=T['tick_color'], labelsize=9)
            plt.setp(ax.get_xticklabels(), rotation=0)
            plt.tight_layout()
            st.pyplot(fig_h)
            plt.close()

with col_alert:
    st.markdown("**Alert System**")
    st.markdown(f"Threshold: `{threshold:.2f}`")

    for src in selected_sources:
        subset    = df_filtered[df_filtered['source'] == src]
        latest    = subset[moisture_cols].iloc[-1].mean() if len(subset) > 0 else 0
        n_alert_s = (subset['avg_moisture'] < threshold).sum()
        pct       = n_alert_s / len(subset) * 100 if len(subset) > 0 else 0

        if latest < threshold:
            st.markdown(f"""<div class="alert-red">
                ⚠️ <b>{SOURCE_LABELS[src][:20]}</b><br>
                Kondisi: KERING ({latest:.3f})<br>
                Alert: {n_alert_s:,}x ({pct:.1f}%)
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="alert-green">
                ✅ <b>{SOURCE_LABELS[src][:20]}</b><br>
                Kondisi: NORMAL ({latest:.3f})<br>
                Alert: {n_alert_s:,}x ({pct:.1f}%)
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Log Alert Terbaru**")
    alert_log = df_filtered[df_filtered['avg_moisture'] < threshold][
        ['datetime', 'source', 'avg_moisture']
    ].sort_values('datetime', ascending=False).head(8).copy()
    alert_log['source']   = alert_log['source'].map(lambda x: SOURCE_LABELS.get(x, x))
    alert_log.columns     = ['Waktu', 'Sumber', 'Moisture']
    alert_log['Moisture'] = alert_log['Moisture'].round(3)
    st.dataframe(alert_log, use_container_width=True, hide_index=True)


st.markdown("---")
with st.expander("Lihat Data Mentah"):
    st.dataframe(
        df_filtered[['datetime', 'source'] + moisture_cols + ['irrigation']].head(200),
        use_container_width=True
    )
    st.caption(f"Menampilkan 200 dari {len(df_filtered):,} baris total.")