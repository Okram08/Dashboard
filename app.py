import streamlit as st
import pandas as pd
import plotly.express as px

# Chargement des données
df = pd.read_csv("trade_history.csv")
df["time"] = pd.to_datetime(df["time"], dayfirst=True)

# Nettoyage des colonnes
df["Result"] = df["closedPnl"].apply(lambda x: "Gain" if x > 0 else "Perte" if x < 0 else "Neutre")

# Filtrer les trades où la colonne 'close' est "close long" ou "close short" et la direction est "long" ou "short"
df_filtered = df[df["dir"].isin(["close long", "close short"])]

# Titre principal
st.title("📈 Dashboard de Trading Hyperliquid")

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 PnL Total", f"{df_filtered['closedPnl'].sum():.2f} $")
col2.metric("📊 Nombre de Trades", len(df_filtered))
col3.metric("✅ % Gagnants", f"{(df_filtered['closedPnl'] > 0).mean() * 100:.1f}%")
col4.metric("💸 Frais Totaux", f"{df_filtered['fee'].sum():.2f} $")

st.markdown("---")

# Filtres
coins = st.multiselect("🔍 Filtrer par coin :", df["coin"].unique(), default=df["coin"].unique())
df_filtered = df_filtered[df_filtered["coin"].isin(coins)]

# PnL cumulé dans le temps (daily)
df_filtered["date"] = df_filtered["time"].dt.date
daily_pnl = df_filtered.groupby("date")["closedPnl"].sum().cumsum().reset_index()
fig_pnl = px.line(daily_pnl, x="date", y="closedPnl", title="📆 Évolution du PnL cumulé par jour", markers=True)
fig_pnl.update_traces(line=dict(color="green"))
st.plotly_chart(fig_pnl, use_container_width=True)

# Histogramme des PnL plus lisible
fig_hist = px.histogram(
    df_filtered,
    x="closedPnl",
    nbins=40,
    title="📊 Distribution des PnL par trade",
    color_discrete_sequence=["#636EFA"]
)
fig_hist.update_layout(bargap=0.2)
st.plotly_chart(fig_hist, use_container_width=True)

# Nettoyage de la colonne 'dir'
df_filtered["dir_clean"] = df_filtered["dir"].str.lower().str.strip()

# Filtrer uniquement long / short
filtered_directions = df_filtered[df_filtered["dir_clean"].isin(["long", "short"])]

# Pie chart
fig_dir = px.pie(filtered_directions, names="dir_clean", title="🧭 Répartition des directions (Long vs Short)")
st.plotly_chart(fig_dir, use_container_width=True)

# Pie chart gains vs pertes
fig_result = px.pie(df_filtered, names="Result", title="🎯 Trades gagnants vs perdants")
st.plotly_chart(fig_result, use_container_width=True)

# Tableau final
st.subheader("📋 Détail des trades")
st.dataframe(df_filtered.sort_values(by="time", ascending=False), use_container_width=True)
