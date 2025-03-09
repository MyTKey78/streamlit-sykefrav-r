import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Tittel
st.title("Sykefraværskostnader i virksomheten")

# Brukerinput for interaktive beregninger
st.sidebar.header("Inndata for beregninger")

antall_ansatte = st.sidebar.number_input("Antall ansatte", min_value=1, value=50)
gjennomsnittslonn = st.sidebar.number_input("Gjennomsnittslønn per ansatt (kr)", min_value=100000, value=600000, step=10000)
sykefravarsprosent = st.sidebar.slider("Sykefraværsprosent (%)", 0.0, 20.0, 5.0, 0.1)

bruker_vikar = st.sidebar.checkbox("Bruker vikar ved fravær?")
vikar_kostnad = st.sidebar.number_input("Vikarkostnad per dag (kr)", min_value=0, value=2500, step=500) if bruker_vikar else 0
overtidsbruk = st.sidebar.checkbox("Bruker overtid ved fravær?")
overtid_kostnad = st.sidebar.number_input("Overtidskostnad per dag (kr)", min_value=0, value=3000, step=500) if overtidsbruk else 0

# Beregninger
arbeidsdager_per_aar = 260
arbeidsgiverperiode = 16

# --- Sykefraværstrend med brukerinput ---
st.subheader("Legg inn sykefravær per måned (%)")

maaneder = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Des"]
sykefravær_per_maaned = {}

for mnd in maaneder:
    sykefravær_per_maaned[mnd] = st.slider(f"{mnd}", 0.0, 20.0, sykefravarsprosent, 0.1)

# Konverter input til DataFrame
data_trend = pd.DataFrame({
    "Måned": maaneder,
    "Sykefraværsprosent": [sykefravær_per_maaned[mnd] for mnd in maaneder]
})

# Beregn kostnader for hver måned basert på sykefravær
data_trend["Kostnad"] = (gjennomsnittslonn * (data_trend["Sykefraværsprosent"] / 100) * (arbeidsgiverperiode / arbeidsdager_per_aar)) * antall_ansatte

# Vis trendgraf
st.subheader("Trend for sykefraværskostnader basert på faktiske data")
fig, ax = plt.subplots(figsize=(8,6))
sns.lineplot(data=data_trend, x="Måned", y="Kostnad", marker="o", ax=ax, color="blue")
ax.set_ylabel("Kostnad (kr)")
ax.set_title("Utvikling av sykefraværskostnader over året basert på faktiske tall")
st.pyplot(fig)
