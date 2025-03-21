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
        }
    </style>
""", unsafe_allow_html=True)

# 🎯 Legg til AS3-logo
st.image("as3 logo - ingen bakgrunn.png", width=200)

st.markdown("""
    <div class="as3-header">
        <h1>Sykefraværskostnader i virksomheten</h1>
        <p>Utviklet i tråd med AS3s designprofil</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<div class='as3-container'>", unsafe_allow_html=True)

# 🎯 Beregning av besparelse ved redusert sykefravær
st.subheader("💰 Hvor mye kan virksomheten spare?")
mål_sykefravær = st.slider("Sett et mål for sykefraværsprosent (%)", 0.0, sykefravarsprosent, max(0.0, sykefravarsprosent - 2.0), 0.1)

direkte_lonnskostnad_ny = (gjennomsnittslonn * (mål_sykefravær / 100) * (arbeidsgiverperiode / arbeidsdager_per_aar))
sosiale_avgifter_ny = direkte_lonnskostnad_ny * 1.14
indirekte_kostnader_ny = direkte_lonnskostnad_ny * 0.5

total_kostnad_per_ansatt_ny = sosiale_avgifter_ny + indirekte_kostnader_ny
total_kostnad_per_virksomhet_ny = total_kostnad_per_ansatt_ny * antall_ansatte

besparelse = total_kostnad_per_virksomhet - total_kostnad_per_virksomhet_ny

total_aarskostnad_ny = (total_kostnad_per_virksomhet_ny * (arbeidsdager_per_aar / arbeidsgiverperiode))
total_aarskostnad_nå = (total_kostnad_per_virksomhet * (arbeidsdager_per_aar / arbeidsgiverperiode))
aarsbesparelse = total_aarskostnad_nå - total_aarskostnad_ny

st.write(f"🔹 **Nåværende kostnad i arbeidsgiverperioden**: {total_kostnad_per_virksomhet:,.0f} kr")
st.write(f"🔹 **Ny kostnad ved {mål_sykefravær:.1f}% sykefravær**: {total_kostnad_per_virksomhet_ny:,.0f} kr")
st.write(f"✅ **Potensiell besparelse i arbeidsgiverperioden**: **{besparelse:,.0f} kr**")

# 🎯 Eksport til Excel
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name="Sykefraværskostnader", index=False)
st.download_button(label="📥 Last ned som Excel", data=excel_buffer.getvalue(), file_name="sykefraværskostnader.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# 🎯 Footer
st.markdown("""
    <div style='text-align: center; margin-top: 2rem;'>
        <small>© 2024 AS3 Norge. Alle rettigheter forbeholdt.</small>
    </div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

