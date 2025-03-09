import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

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
total_kostnad_per_virksomhet = total_kostnad_per_ansatt * antall_ansatte

total_aarskostnad = (total_kostnad_per_virksomhet + vikar_kostnad_total + overtid_kostnad_total) * (arbeidsdager_per_aar / arbeidsgiverperiode)

# Vise resultater
st.subheader("Beregnet sykefraværskostnad")
st.write(f"Totale kostnader for arbeidsgiverperioden per ansatt: **{total_kostnad_per_ansatt:,.0f} kr**")
st.write(f"Totale kostnader for hele virksomheten i arbeidsgiverperioden: **{total_kostnad_per_virksomhet:,.0f} kr**")
st.write(f"Årlige totale sykefraværskostnader (inkl. vikar/overtid): **{total_aarskostnad:,.0f} kr**")

# Lag en DataFrame for eksport
df = pd.DataFrame({
    "Kategori": ["Direkte lønnskostnader", "Sosiale avgifter", "Indirekte kostnader", "Vikarutgifter", "Overtidsutgifter"],
    "Kostnad (kr)": [
        direkte_lonnskostnad * antall_ansatte,
        sosiale_avgifter * antall_ansatte,
        indirekte_kostnader * antall_ansatte,
        vikar_kostnad_total,
        overtid_kostnad_total
    ]
})

# 📊 Eksport til Excel
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name="Sykefraværskostnader", index=False)
st.download_button(label="📥 Last ned som Excel", data=excel_buffer.getvalue(), file_name="sykefraværskostnader.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# 📄 Eksport til PDF
def generate_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Sykefraværskostnader i virksomheten", ln=True, align="C")
    
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)  # Linjeskift
    
    # Legg til beregninger i PDF
    pdf.cell(200, 10, f"Totale kostnader per ansatt: {total_kostnad_per_ansatt:,.0f} kr", ln=True)
    pdf.cell(200, 10, f"Totale kostnader for virksomheten: {total_kostnad_per_virksomhet:,.0f} kr", ln=True)
    pdf.cell(200, 10, f"Årlige totale kostnader: {total_aarskostnad:,.0f} kr", ln=True)
    
    pdf.ln(10)  # Linjeskift
    
    # Legg til tabell i PDF
    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 10, "Kategori", border=1)
    pdf.cell(80, 10, "Kostnad (kr)", border=1, ln=True)

    pdf.set_font("Arial", "", 12)
    for index, row in df.iterrows():
        pdf.cell(100, 10, row["Kategori"], border=1)
        pdf.cell(80, 10, f"{row['Kostnad (kr)']:,.0f} kr", border=1, ln=True)

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    return pdf_output.getvalue()

st.download_button(label="📥 Last ned som PDF", data=generate_pdf(), file_name="sykefraværskostnader.pdf", mime="application/pdf")
