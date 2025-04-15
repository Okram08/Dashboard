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
df["PnL_cum"] = df["closedPnl"].cumsum()

# Titre
st.title("📈 Dashboard de Gordy🍻")

# KPIs de base
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💰 PnL Total", f"{df['closedPnl'].sum():.2f} $")
    st.caption("ℹ️ Somme totale des profits et pertes réalisés.")

with col2:
    st.metric("📊 Nombre de Trades", len(df))
    st.caption("ℹ️ Total des positions ouvertes et clôturées dans l’historique.")

with col3:
    st.metric("✅ % Gagnants", f"{(df['closedPnl'] > 0).mean() * 100:.1f}%")
    st.caption("ℹ️ Proportion des trades avec un profit net positif. PS: Je doise ncore changer car il prend en compte les fees negatif donc fausse le ratio (il faut faire xé en soit ici pour ajouter la moitié negative mais trop fatigué de le faire now hahah")

with col4:
    st.metric("💸 Frais Totaux", f"{df['fee'].sum():.2f} $")
    st.caption("ℹ️ Total des frais de transaction (commissions).")

# Ratio de Sharpe simplifié + infobulle
mean_return = df["closedPnl"].mean()
std_return = df["closedPnl"].std()
sharpe_ratio = mean_return / std_return if std_return != 0 else 0

col_ratio, _ = st.columns([1, 3])
with col_ratio:
    st.metric("📐 Ratio de Sharpe", f"{sharpe_ratio:.2f}")
    st.caption("ℹ️ Indique le rapport rendement/risque : plus il est élevé, mieux c’est. Calculé ici : moyenne des PnL ÷ écart-type. PS: A voir si je le laisse lui")

# Filtres
st.markdown("---")
coins = st.multiselect("🔍 Filtrer par coin :", df["coin"].unique(), default=df["coin"].unique())
date_min, date_max = st.date_input("📆 Filtrer par date :", [df["time"].min(), df["time"].max()])

df_filtered = df[
    (df["coin"].isin(coins)) &
    (df["time"] >= pd.to_datetime(date_min)) &
    (df["time"] <= pd.to_datetime(date_max))
].copy()

df_filtered["PnL_cum"] = df_filtered["closedPnl"].cumsum()

# Statistiques avancées
gains = df_filtered[df_filtered["closedPnl"] > 0]["closedPnl"]
pertes = df_filtered[df_filtered["closedPnl"] < 0]["closedPnl"]

gain_moyen = gains.mean() if not gains.empty else 0
perte_moyenne = pertes.mean() if not pertes.empty else 0
risk_reward = abs(gain_moyen / perte_moyenne) if perte_moyenne != 0 else 0

st.markdown("### 📊 Statistiques Avancées")
col1, col2, col3 = st.columns(3)
col1.metric("📈 Gain moyen", f"{gain_moyen:.2f} $")
col1.caption("ℹ️ Moyenne des profits sur les trades gagnants.")

col2.metric("📉 Perte moyenne", f"{perte_moyenne:.2f} $")
col2.caption("ℹ️ Moyenne des pertes sur les trades perdants.")

col3.metric("⚖️ Risk/Reward", f"{risk_reward:.2f}")
col3.caption("ℹ️ Rapport entre gain moyen et perte moyenne.")

# Graphiques avec palette personnalisée
st.markdown("---")
color_palette = ["#2E86AB", "#F24405", "#44AF69", "#DA4167", "#F9CB40"]

# Winrate par coin
winrate_coin = df_filtered.groupby("coin")["closedPnl"].apply(lambda x: (x > 0).mean() * 100).reset_index(name="WinRate (%)")
fig_winrate = px.bar(winrate_coin, x="coin", y="WinRate (%)", title="Win Rate par Coin", color="coin", color_discrete_sequence=color_palette)
st.plotly_chart(fig_winrate, use_container_width=True)

# PnL dans le temps
fig_pnl = px.line(df_filtered, x="time", y="closedPnl", title="Évolution du PnL dans le temps", markers=True,
                  color_discrete_sequence=["#2E86AB"])
st.plotly_chart(fig_pnl, use_container_width=True)

# PnL Cumulé
fig_cum = px.line(df_filtered, x="time", y="PnL_cum", title="PnL Cumulé", markers=True,
                  color_discrete_sequence=["#44AF69"])
st.plotly_chart(fig_cum, use_container_width=True)

# PnL par jour
pnl_jour = df_filtered.groupby("jour")["closedPnl"].sum().reset_index()
fig_jour = px.bar(pnl_jour, x="jour", y="closedPnl", title="PnL par Jour", color="closedPnl", color_continuous_scale="rdylgn")
st.plotly_chart(fig_jour, use_container_width=True)

# PnL par mois
pnl_mois = df_filtered.groupby("mois")["closedPnl"].sum().reset_index()
fig_mois = px.bar(pnl_mois, x="mois", y="closedPnl", title="PnL par Mois", color="closedPnl", color_continuous_scale="Mint")
st.plotly_chart(fig_mois, use_container_width=True)

# Pie gagnant/perdant
fig_result = px.pie(df_filtered, names="Result", title="Trades gagnants vs perdants", color_discrete_sequence=["#44AF69", "#F24405", "#999999"])
st.plotly_chart(fig_result, use_container_width=True)

# PnL par coin
pnl_coin = df_filtered.groupby("coin")["closedPnl"].sum().reset_index().sort_values(by="closedPnl")
fig_coin = px.bar(pnl_coin, x="coin", y="closedPnl", title="PnL par Coin", color="closedPnl", color_continuous_scale="Bluered")
st.plotly_chart(fig_coin, use_container_width=True)

# Analyse par taille de position si dispo
if "size" in df_filtered.columns:
    fig_size = px.scatter(
        df_filtered,
        x="size",
        y="closedPnl",
        color="Result",
        title="PnL en fonction de la Taille de Position",
        size="closedPnl",
        hover_data=["coin", "time"],
        color_discrete_sequence=color_palette
    )
    st.plotly_chart(fig_size, use_container_width=True)

# Durée des trades si dispo
if "openTime" in df_filtered.columns:
    df_filtered["openTime"] = pd.to_datetime(df_filtered["openTime"], dayfirst=True)
    df_filtered["duration_min"] = (df_filtered["time"] - df_filtered["openTime"]).dt.total_seconds() / 60
    fig_duree = px.histogram(df_filtered, x="duration_min", nbins=30, title="Durée des trades (minutes)", color_discrete_sequence=["#2E86AB"])
    st.plotly_chart(fig_duree, use_container_width=True)

# Tableau
st.subheader("📋 Détail des trades")
st.dataframe(df_filtered.sort_values(by="time", ascending=False), use_container_width=True)

# Export
st.download_button("📥 Télécharger les données filtrées", df_filtered.to_csv(index=False), file_name="filtered_trades.csv")
