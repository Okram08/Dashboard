import streamlit as st
import pandas as pd
import plotly.express as px

# Chargement des données
df = pd.read_csv("trade_history.csv")
df["time"] = pd.to_datetime(df["time"], dayfirst=True)

# Filtrage des trades fermés uniquement pour l'analyse de performance
df_closed = df[df["position"].str.contains("Close", case=False)].copy()

# Ajout colonne Result
df_closed["Result"] = df_closed["closedPnl"].apply(lambda x: "Gain" if x > 0 else "Perte" if x < 0 else "Neutre")

# ---- TITRE
st.title("📊 Dashboard de Trading")

# --- METRIQUES PRINCIPALES
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 PnL Total", f"{df_closed['closedPnl'].sum():.2f} $")
col2.metric("📊 Nombre de Trades", len(df_closed))
col3.metric("✅ % Gagnants", f"{(df_closed['closedPnl'] > 0).mean() * 100:.1f}%")
col4.metric("💸 Frais Totaux", f"{df['fee'].sum():.2f} $")  # On garde tous les frais (open+close)

# --- METRIQUES AVANCEES
gain_moyen = df_closed[df_closed["closedPnl"] > 0]["closedPnl"].mean()
perte_moyenne = df_closed[df_closed["closedPnl"] < 0]["closedPnl"].mean()
risk_reward = abs(gain_moyen / perte_moyenne) if perte_moyenne != 0 else 0

mean_return = df_closed["closedPnl"].mean()
std_return = df_closed["closedPnl"].std()
sharpe_ratio = mean_return / std_return if std_return != 0 else 0

st.markdown("### 📈 Indicateurs de Performance")
col5, col6, col7 = st.columns(3)
col5.metric("📈 Gain moyen", f"{gain_moyen:.2f} $")
col6.metric("📉 Perte moyenne", f"{perte_moyenne:.2f} $")
col7.metric("⚖️ Risk/Reward", f"{risk_reward:.2f}")

# Ratio de Sharpe avec info-bulle
with st.container():
    st.markdown("""
    <div style="display: flex; align-items: center;">
        <div style="font-size: 16px; margin-right: 10px;"><b>📐 Ratio de Sharpe :</b> {0:.2f}</div>
        <div title="Le ratio de Sharpe mesure la performance ajustée au risque. Plus il est élevé, mieux c'est.">🛈</div>
    </div>
    """.format(sharpe_ratio), unsafe_allow_html=True)

st.markdown("---")

# --- FILTRE PAR COIN
coins = st.multiselect("🔍 Filtrer par coin :", df_closed["coin"].unique(), default=df_closed["coin"].unique())
df_filtered = df_closed[df_closed["coin"].isin(coins)]

# --- GRAPHIQUE PNL DANS LE TEMPS
fig_pnl = px.line(df_filtered, x="time", y="closedPnl", title="📅 PnL au fil du temps", markers=True,
                  color_discrete_sequence=["#00CC96"])
fig_pnl.update_layout(plot_bgcolor="#f9f9f9", paper_bgcolor="#f9f9f9")
st.plotly_chart(fig_pnl, use_container_width=True)

# --- PIE CHART RESULTATS
fig_result = px.pie(df_filtered, names="Result", title="✅ Répartition des trades gagnants vs perdants",
                    color_discrete_map={"Gain": "#2ecc71", "Perte": "#e74c3c", "Neutre": "#95a5a6"})
st.plotly_chart(fig_result, use_container_width=True)

# --- TABLEAU DETAILLE
st.markdown("### 📋 Détail des trades fermés")
st.dataframe(df_filtered.sort_values(by="time", ascending=False), use_container_width=True)
