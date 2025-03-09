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
direkte_lonnskostnad = (gjennomsnittslonn * (sykefravarsprosent / 100) * (arbeidsgiverperiode / arbeidsdager_per_aar))
sosiale_avgifter = direkte_lonnskostnad * 1.14
indirekte_kostnader = direkte_lonnskostnad * 0.5

# Totale kostnader
vikar_kostnad_total = (vikar_kostnad * arbeidsgiverperiode * (sykefravarsprosent / 100) * antall_ansatte)
overtid_kostnad_total = (overtid_kostnad * arbeidsgiverperiode * (sykefravarsprosent / 100) * antall_ansatte)

total_kostnad_per_ansatt = sosiale_avgifter + indirekte_kostnader
total_kostnad_per_avdeling = total_kostnad_per_ansatt * antall_ansatte

total_aarskostnad = (total_kostnad_per_avdeling + vikar_kostnad_total + overtid_kostnad_total) * (arbeidsdager_per_aar / arbeidsgiverperiode)

# Vise resultater
st.subheader("Beregnet sykefraværskostnad")
st.write(f"Totale kostnader for arbeidsgiverperioden per ansatt: **{total_kostnad_per_ansatt:,.0f} kr**")
st.write(f"Totale kostnader for hele virksomheten i arbeidsgiverperioden: **{total_kostnad_per_avdeling:,.0f} kr**")
st.write(f"Årlige totale sykefraværskostnader (inkl. vikar/overtid): **{total_aarskostnad:,.0f} kr**")

# Diagram: Totale kostnader
st.subheader("Visuell fremstilling av kostnader")
fig, ax = plt.subplots(figsize=(8,6))
kategorier = ["Direkte lønnskostnader", "Sosiale avgifter", "Indirekte kostnader", "Vikarutgifter", "Overtidsutgifter"]
verdier = [
    direkte_lonnskostnad * antall_ansatte,
    sosiale_avgifter * antall_ansatte,
    indirekte_kostnader * antall_ansatte,
    vikar_kostnad_total,
    overtid_kostnad_total
]
ax.bar(kategorier, verdier, color=["blue", "green", "red", "purple", "orange"])
ax.set_ylabel("Kostnad (kr)")
ax.set_title("Fordeling av sykefraværskostnader")
ax.set_xticklabels(kategorier, rotation=45, ha="right")
st.pyplot(fig)

# Trendanalyse: Utvikling av kostnader over tid
st.subheader("Trend for sykefraværskostnader")
data_trend = pd.DataFrame({
    "Måned": ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Des"],
    "Kostnad": [
        total_kostnad_per_avdeling * (0.9 + i*0.02) for i in range(12)
    ]
})
fig, ax = plt.subplots(figsize=(8,6))
sns.lineplot(data=data_trend, x="Måned", y="Kostnad", marker="o", ax=ax)
ax.set_ylabel("Kostnad (kr)")
ax.set_title("Utvikling av sykefraværskostnader over året")
st.pyplot(fig)
