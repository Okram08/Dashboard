import streamlit as st
import pandas as pd
import plotly.express as px

# Chargement des données
df = pd.read_csv("trade_history.csv")
df["time"] = pd.to_datetime(df["time"], dayfirst=True)

# Nettoyage & enrichissement
df["Result"] = df["closedPnl"].apply(lambda x: "Gain" if x > 0 else "Perte" if x < 0 else "Neutre")
df["jour"] = df["time"].dt.date
df["mois"] = df["time"].dt.to_period("M").astype(str)
df["heure"] = df["time"].dt.hour
df["PnL_cum"] = df["closedPnl"].cumsum()

# Titre
st.title("📈 Dashboard de Trading - Analyse Avancée")

# KPIs de base
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 PnL Total", f"{df['closedPnl'].sum():.2f} $")
col2.metric("📊 Nombre de Trades", len(df))
col3.metric("✅ % Gagnants", f"{(df['closedPnl'] > 0).mean() * 100:.1f}%")
col4.metric("💸 Frais Totaux", f"{df['fee'].sum():.2f} $")

# Ratio de Sharpe simplifié
mean_return = df["closedPnl"].mean()
std_return = df["closedPnl"].std()
sharpe_ratio = mean_return / std_return if std_return != 0 else 0
st.metric("📐 Ratio de Sharpe (simplifié)", f"{sharpe_ratio:.2f}")

# Filtres
st.markdown("---")
coins = st.multiselect("🔍 Filtrer par coin :", df["coin"].unique(), default=df["coin"].unique())
date_min, date_max = st.date_input("📆 Filtrer par date :", [df["time"].min(), df["time"].max()])

df_filtered = df[
    (df["coin"].isin(coins)) &
    (df["time"] >= pd.to_datetime(date_min)) &
    (df["time"] <= pd.to_datetime(date_max))
].copy()

# Enrichissement filtré
df_filtered["PnL_cum"] = df_filtered["closedPnl"].cumsum()

# Ratios supplémentaires
gains = df_filtered[df_filtered["closedPnl"] > 0]["closedPnl"]
pertes = df_filtered[df_filtered["closedPnl"] < 0]["closedPnl"]

gain_moyen = gains.mean() if not gains.empty else 0
perte_moyenne = pertes.mean() if not pertes.empty else 0
risk_reward = abs(gain_moyen / perte_moyenne) if perte_moyenne != 0 else 0

st.markdown("### 📊 Statistiques Avancées")
col1, col2, col3 = st.columns(3)
col1.metric("📈 Gain moyen", f"{gain_moyen:.2f} $")
col2.metric("📉 Perte moyenne", f"{perte_moyenne:.2f} $")
col3.metric("⚖️ Risk/Reward", f"{risk_reward:.2f}")

# Winrate par coin
winrate_coin = df_filtered.groupby("coin")["closedPnl"].apply(lambda x: (x > 0).mean() * 100).reset_index(name="WinRate (%)")
fig_winrate = px.bar(winrate_coin, x="coin", y="WinRate (%)", title="Win Rate par Coin")
st.plotly_chart(fig_winrate, use_container_width=True)

# Graphiques principaux
st.markdown("---")
fig_pnl = px.line(df_filtered, x="time", y="closedPnl", title="Évolution du PnL dans le temps", markers=True)
st.plotly_chart(fig_pnl, use_container_width=True)

fig_cum = px.line(df_filtered, x="time", y="PnL_cum", title="PnL Cumulé", markers=True)
st.plotly_chart(fig_cum, use_container_width=True)

fig_hist = px.histogram(df_filtered, x="closedPnl", nbins=20, title="Distribution des PnL par trade")
st.plotly_chart(fig_hist, use_container_width=True)

pnl_jour = df_filtered.groupby("jour")["closedPnl"].sum().reset_index()
fig_jour = px.bar(pnl_jour, x="jour", y="closedPnl", title="PnL par Jour")
st.plotly_chart(fig_jour, use_container_width=True)

pnl_mois = df_filtered.groupby("mois")["closedPnl"].sum().reset_index()
fig_mois = px.bar(pnl_mois, x="mois", y="closedPnl", title="PnL par Mois")
st.plotly_chart(fig_mois, use_container_width=True)

fig_result = px.pie(df_filtered, names="Result", title="Trades gagnants vs perdants")
st.plotly_chart(fig_result, use_container_width=True)

pnl_coin = df_filtered.groupby("coin")["closedPnl"].sum().reset_index().sort_values(by="closedPnl")
fig_coin = px.bar(pnl_coin, x="coin", y="closedPnl", title="PnL par Coin", color="closedPnl")
st.plotly_chart(fig_coin, use_container_width=True)

# Performance par heure
fig_hour = px.box(df_filtered, x="heure", y="closedPnl", points="all", title="Performance par Heure de la Journée")
st.plotly_chart(fig_hour, use_container_width=True)

# Analyse par taille de position si dispo
if "size" in df_filtered.columns:
    fig_size = px.scatter(
        df_filtered,
        x="size",
        y="closedPnl",
        color="Result",
        title="PnL en fonction de la Taille de Position",
        size="closedPnl",
        hover_data=["coin", "time"]
    )
    st.plotly_chart(fig_size, use_container_width=True)

# Durée des trades
if "openTime" in df_filtered.columns:
    df_filtered["openTime"] = pd.to_datetime(df_filtered["openTime"], dayfirst=True)
    df_filtered["duration_min"] = (df_filtered["time"] - df_filtered["openTime"]).dt.total_seconds() / 60
    fig_duree = px.histogram(df_filtered, x="duration_min", nbins=30, title="Durée des trades (minutes)")
    st.plotly_chart(fig_duree, use_container_width=True)

# Tableau des trades
st.subheader("📋 Détail des trades")
st.dataframe(df_filtered.sort_values(by="time", ascending=False), use_container_width=True)

# Export CSV
st.download_button("📥 Télécharger les données filtrées", df_filtered.to_csv(index=False), file_name="filtered_trades.csv")
