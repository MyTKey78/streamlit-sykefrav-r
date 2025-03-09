import streamlit as st

st.title("Sykefraværskostnader i virksomheten")

st.write("Dette er en enkel Streamlit-app for å beregne kostnader ved sykefravær.")

# Eksempel på input
lønn = st.number_input("Gjennomsnittslønn per ansatt (kr)", min_value=0, value=600000)
sykefravær = st.slider("Sykefraværsprosent (%)", 0.0, 20.0, 5.0)

# Beregning
kostnad = (lønn * (sykefravær / 100)) * (16 / 260)

st.write(f"Totale kostnader for sykefravær i arbeidsgiverperioden: **{kostnad:,.0f} kr**")
