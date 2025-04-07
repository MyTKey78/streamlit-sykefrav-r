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
        
        input[type='range']::-webkit-slider-runnable-track {
            background: #084966;
        }
        input[type='range']::-moz-range-track {
            background: #084966;
        }
        input[type='range']::-ms-track {
            background: #084966;
        }
        .as3-footer {
            text-align: center;
            margin-top: 3rem;
            font-size: 0.8rem;
            color: #888;
        }
    </style>
""", unsafe_allow_html=True)

st.image("https://raw.githubusercontent.com/MyTKey78/streamlit-sykefrav-r/main/as3%20logo%20-%20ingen%20bakgrunn.png", width=200)

# 🎯 Tittel
st.title("Sykefraværskostnader i virksomheten")

# 🎯 Brukerinput for interaktive beregninger
st.sidebar.header("Inndata for beregninger")

antall_ansatte = st.sidebar.number_input("Antall ansatte", min_value=1, value=50)
gjennomsnittslonn = st.sidebar.number_input("Gjennomsnittslønn per ansatt (kr)", min_value=100000, value=600000, step=10000)
sykefravarsprosent = st.sidebar.slider("Sykefraværsprosent (%)", 0.0, 20.0, 5.0, 0.1)

datakilde = st.sidebar.selectbox("Velg datakilde", ["NAV", "SINTEF"])
fravaerstype = st.sidebar.selectbox("Velg fraværstype", ["total", "kort", "lang"])

bruker_vikar = st.sidebar.checkbox("Bruker vikar ved fravær?")
vikar_kostnad = st.sidebar.number_input("Vikarkostnad per dag (kr)", min_value=0, value=2500, step=500) if bruker_vikar else 0
overtidsbruk = st.sidebar.checkbox("Bruker overtid ved fravær?")
overtid_kostnad = st.sidebar.number_input("Overtidskostnad per dag (kr)", min_value=0, value=3000, step=500) if overtidsbruk else 0

# 🎯 Kildejustering
if datakilde == "NAV":
    langtidsandel = 0.60
elif datakilde == "SINTEF":
    langtidsandel = 0.75

arbeidsdager_per_aar = 260
arbeidsgiverperiode = 16

# 🎯 Fraværsjustering og refusjon
if fravaerstype == "kort":
    justert_fravaersprosent = sykefravarsprosent * (1 - langtidsandel)
    refusjon = 0
elif fravaerstype == "lang":
    justert_fravaersprosent = sykefravarsprosent * langtidsandel
    refusjonsgrunnlag = justert_fravaersprosent * arbeidsdager_per_aar * antall_ansatte * (2/3)
    refusjon = refusjonsgrunnlag * (gjennomsnittslonn / arbeidsdager_per_aar)
else:
    justert_fravaersprosent = sykefravarsprosent
    refusjonsgrunnlag = sykefravarsprosent * arbeidsdager_per_aar * antall_ansatte * langtidsandel * (2/3)
    refusjon = refusjonsgrunnlag * (gjennomsnittslonn / arbeidsdager_per_aar)

direkte_lonnskostnad = (gjennomsnittslonn * (justert_fravaersprosent / 100) * (arbeidsgiverperiode / arbeidsdager_per_aar))
sosiale_avgifter = direkte_lonnskostnad * 1.14
indirekte_kostnader = direkte_lonnskostnad * 0.5

vikar_kostnad_total = (vikar_kostnad * arbeidsgiverperiode * (justert_fravaersprosent / 100) * antall_ansatte)
overtid_kostnad_total = (overtid_kostnad * arbeidsgiverperiode * (justert_fravaersprosent / 100) * antall_ansatte)

total_kostnad_per_ansatt = sosiale_avgifter + indirekte_kostnader
total_kostnad_per_virksomhet = total_kostnad_per_ansatt * antall_ansatte
total_aarskostnad = (total_kostnad_per_virksomhet + vikar_kostnad_total + overtid_kostnad_total - refusjon) * (arbeidsdager_per_aar / arbeidsgiverperiode)

# 🎯 Resultat
st.subheader("Beregnet sykefraværskostnad")
st.write(f"Datakilde: **{datakilde}**, Fraværstype: **{fravaerstype}**")
st.write(f"Totale kostnader for arbeidsgiverperioden per ansatt: **{total_kostnad_per_ansatt:,.0f} kr**")
st.write(f"Totale kostnader for hele virksomheten i arbeidsgiverperioden: **{total_kostnad_per_virksomhet:,.0f} kr**")
st.write(f"Årlige totale sykefraværskostnader (inkl. vikar/overtid og refusjon): **{total_aarskostnad:,.0f} kr**")

# 🎯 DataFrame og diagram
df = pd.DataFrame({
    "Kategori": ["Direkte lønnskostnader", "Sosiale avgifter", "Indirekte kostnader", "Vikarutgifter", "Overtidsutgifter", "Refusjon fra NAV"],
    "Kostnad (kr)": [
        direkte_lonnskostnad * antall_ansatte,
        sosiale_avgifter * antall_ansatte,
        indirekte_kostnader * antall_ansatte,
        vikar_kostnad_total,
        overtid_kostnad_total,
        -refusjon
    ]
})

st.subheader("Visuell fremstilling av kostnader")
fig, ax = plt.subplots(figsize=(8,6))
ax.bar(df["Kategori"], df["Kostnad (kr)"], color=["#084966", "#286488", "#3A7DA2", "#63CDF6", "#A3DAEB", "#BBBBBB"])
ax.set_ylabel("Kostnad (kr)")
ax.set_title("Fordeling av sykefraværskostnader")
ax.set_xticklabels(df["Kategori"], rotation=45, ha="right")
st.pyplot(fig)

# 🎯 Eksport til Excel
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name="Sykefraværskostnader", index=False)
st.download_button(
    label="📥 Last ned som Excel",
    data=excel_buffer.getvalue(),
    file_name="sykefraværskostnader.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 🎯 Kilder
st.markdown("## 📚 Kildehenvisninger")
st.markdown("""
- **NAVs sykefraværsstatistikk**: [NAV – Sykefravær](https://www.nav.no/no/nav-og-samfunn/statistikk/sykefravar-statistikk)  
- **SINTEF-analyser av sykefravær**: Basert på forskningsrapporter om arbeidsmiljø, helse og langtidsfravær (for eksempel i offentlig sektor).
- **Arbeidsgiverperioden på 16 dager**: [Lovdata – Folketrygdloven § 8-19](https://lovdata.no/dokument/NL/lov/1997-02-28-19/KAPITTEL_8#%C2%A78-19)  
- **Sosiale avgifter (14%)**: Basert på vanlige norske arbeidsgiveravgifter  
- **Indirekte kostnader (50% av lønn)**: HR-beregninger brukt i sykefraværsanalyser  
- **Refusjon fra NAV**: Beregnes for legemeldt fravær utover 16 dager, ofte basert på 2/3 av fraværsperioden
""")

# 🎯 Footer
st.markdown("<div class='as3-footer'>© 2024 AS3 Norge</div>", unsafe_allow_html=True)




