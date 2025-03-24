import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# 🎯 Design-tilpasning (AS3 profil)
st.set_page_config(page_title="Sykefraværskalkulator", layout="centered")

st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-family: 'Work Sans', sans-serif;
        }
        .main {
            background-color: #f9f9f9;
        }
        .as3-header {
            background-color: #084966;
            color: white;
            padding: 2rem;
            text-align: center;
            border-radius: 0 0 12px 12px;
            margin-bottom: 2rem;
        }
        .as3-container {
            max-width: 800px;
            margin: auto;
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            border: 1px solid #084966;
        }
        .as3-button > button {
            background-color: #286488;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            font-size: 1rem;
        }
        .as3-button > button:hover {
            background-color: #3A7DA2;
        }
        .result-box {
            background-color: #f0f8ff;
            padding: 1.5rem;
            border-left: 5px solid #084966;
            border-radius: 8px;
            margin-top: 2rem;
            border: 1px solid #084966;
        }
        .stSlider > div[data-baseweb="slider"] > div {
            background-color: #084966 !important;
        }
        .stNumberInput input {
            border: 1px solid #084966 !important;
        }
        .stSelectbox div[data-baseweb="select"] > div {
            border: 1px solid #084966 !important;
        }
    input[type='range']::-webkit-slider-runnable-track {
            background: #084966;
        }
        input[type='range']::-moz-range-track {
            background: #084966;
        }
        input[type='range']::-ms-track {
            background: #084966;
        }
    </style>
""", unsafe_allow_html=True)



# 🎯 Legg til AS3-logo
st.image("as3 logo - ingen bakgrunn.png", width=200)

st.markdown("""
    <div class="as3-header">
        <h1>Sykefraværskostnader i virksomheten</h1>
        
    </div>
""", unsafe_allow_html=True)

st.markdown("<div class='as3-container'>", unsafe_allow_html=True)

# 🎯 Beregninger
arbeidsdager_per_aar = 260
arbeidsgiverperiode = 16
direkte_lonnskostnad = (gjennomsnittslonn * (sykefravarsprosent / 100) * (arbeidsgiverperiode / arbeidsdager_per_aar))
sosiale_avgifter = direkte_lonnskostnad * 1.14
indirekte_kostnader = direkte_lonnskostnad * 0.5

# Totale kostnader
vikar_kostnad_total = (vikar_kostnad * arbeidsgiverperiode * (sykefravarsprosent / 100) * antall_ansatte)
overtid_kostnad_total = (overtid_kostnad * arbeidsgiverperiode * (sykefravarsprosent / 100) * antall_ansatte)

total_kostnad_per_ansatt = sosiale_avgifter + indirekte_kostnader
total_kostnad_per_virksomhet = total_kostnad_per_ansatt * antall_ansatte
total_aarskostnad = (total_kostnad_per_virksomhet + vikar_kostnad_total + overtid_kostnad_total) * (arbeidsdager_per_aar / arbeidsgiverperiode)

# 🎯 Vise resultater
st.subheader("Beregnet sykefraværskostnad")
st.write(f"Totale kostnader for arbeidsgiverperioden per ansatt: **{total_kostnad_per_ansatt:,.0f} kr**")
st.write(f"Totale kostnader for hele virksomheten i arbeidsgiverperioden: **{total_kostnad_per_virksomhet:,.0f} kr**")
st.write(f"Årlige totale sykefraværskostnader (inkl. vikar/overtid): **{total_aarskostnad:,.0f} kr**")

st.write(f"Årlige totale sykefraværskostnader (inkl. vikar/overtid): **{total_aarskostnad:,.0f} kr**")




