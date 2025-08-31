import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Sykefraværskalkulator", layout="centered")

# AS3-stil og logo
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
        }
        .main {
            background-color: #f9f9f9;
        }
        h1, h2, h3, .stButton>button {
            color: #084966;
        }
        input[type='range']::-webkit-slider-runnable-track { background: #084966; }
        input[type='range']::-moz-range-track { background: #084966; }
        input[type='range']::-ms-track { background: #084966; }
        .as3-footer {
            text-align: center;
            margin-top: 3rem;
            font-size: 0.8rem;
            color: #888;
        }
    </style>
""", unsafe_allow_html=True)

st.image(
    "https://raw.githubusercontent.com/MyTKey78/streamlit-sykefrav-r/main/as3%20logo%20-%20ingen%20bakgrunn.png",
    width=200
)

# 🎯 Tittel
st.title("Sykefraværskostnader i virksomheten")

# 🎯 Brukerinput for interaktive beregninger
st.sidebar.header("Inndata for beregninger")
antall_ansatte = st.sidebar.number_input("Antall ansatte", min_value=1, value=50)
gjennomsnittslonn = st.sidebar.number_input(
    "Gjennomsnittslønn per ansatt (kr)", min_value=100_000, value=600_000, step=10_000
)
sykefravarsprosent = st.sidebar.slider("Sykefraværsprosent (%)", 0.0, 20.0, 5.0, 0.1)

vikar_kostnad = st.sidebar.number_input(
    "Vikar-kostnad per dag (kr)",
    min_value=0,
    value=0,
    step=500,
    help="Sett til 0 hvis dere ikke bruker vikar"
)

overtid_kostnad = st.sidebar.number_input(
    "Overtid-kostnad per dag (kr)",
    min_value=0,
    value=0,
    step=500,
    help="Sett til 0 hvis dere ikke bruker overtid"
)

# 🎯 Beregninger
arbeidsdager_per_aar = 260
arbeidsgiverperiode = 16

direkte_lonnskostnad = (
    gjennomsnittslonn * (sykefravarsprosent / 100.0) * (arbeidsgiverperiode / arbeidsdager_per_aar)
)
sosiale_avgifter = direkte_lonnskostnad * 1.14
indirekte_kostnader = direkte_lonnskostnad * 0.5

vikar_kostnad_total = (
    float(vikar_kostnad) * arbeidsgiverperiode * (sykefravarsprosent / 100.0) * antall_ansatte
)
overtid_kostnad_total = (
    float(overtid_kostnad) * arbeidsgiverperiode * (sykefravarsprosent / 100.0) * antall_ansatte
)

total_kostnad_per_ansatt = sosiale_avgifter + indirekte_kostnader
total_kostnad_per_virksomhet = total_kostnad_per_ansatt * antall_ansatte
total_aarskostnad = (
    (total_kostnad_per_virksomhet + vikar_kostnad_total + overtid_kostnad_total)
    * (arbeidsdager_per_aar / arbeidsgiverperiode)
)

# 🎯 Resultat
st.subheader("Beregnet sykefraværskostnad")
st.write(f"Totale kostnader for arbeidsgiverperioden per ansatt: **{total_kostnad_per_ansatt:,.0f} kr**")
st.write(f"Totale kostnader for hele virksomheten i arbeidsgiverperioden: **{total_kostnad_per_virksomhet:,.0f} kr**")
st.write(f"År
