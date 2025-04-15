import streamlit as st
import pandas as pd
import plotly.express as px

# Chargement des données
df = pd.read_csv("trade_history.csv")  # Renomme ton fichier si besoin
df["time"] = pd.to_datetime(df["time"], dayfirst=True)

# Nettoyage
df["Result"] = df["closedPnl"].apply(lambda x: "Gain" if x > 0 else "Perte" if x < 0 else "Neutre")

# Titre
st.title("📈 Dashboard de Trading Hyperliquid")

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 PnL Total", f"{df['closedPnl'].sum():.2f} $")
col2.metric("📊 Nombre de Trades", len(df))
col3.metric("✅ % Gagnants", f"{(df['closedPnl'] > 0).mean() * 100:.1f}%")
col4.metric("💸 Frais Totaux", f"{df['fee'].sum():.2f} $")

st.markdown("---")

# Filtres
coins = st.multiselect("🔍 Filtrer par coin :", df["coin"].unique(), default=df["coin"].unique())
df_filtered = df[df["coin"].isin(coins)]

# Graphique PnL dans le temps
fig_pnl = px.line(df_filtered, x="time", y="closedPnl", title="Évolution du PnL dans le temps", markers=True)
st.plotly_chart(fig_pnl, use_container_width=True)

# Histogramme des PnL
fig_hist = px.histogram(df_filtered, x="closedPnl", nbins=20, title="Distribution des PnL par trade")
st.plotly_chart(fig_hist, use_container_width=True)

# Pie chart directions
fig_dir = px.pie(df_filtered, names="dir", title="Répartition des directions de trade")
st.plotly_chart(fig_dir, use_container_width=True)

# Pie chart gains vs pertes
fig_result = px.pie(df_filtered, names="Result", title="Trades gagnants vs perdants")
st.plotly_chart(fig_result, use_container_width=True)

# Tableau des trades
st.subheader("📋 Détail des trades")
st.dataframe(df_filtered.sort_values(by="time", ascending=False), use_container_width=True)
