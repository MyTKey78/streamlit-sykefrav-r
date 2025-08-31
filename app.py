import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# ────────────────────────────────────────────────────────────────────────────────
# Grunnoppsett
# ────────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sykefraværskalkulator", layout="centered")

# AS3-stil og enkel branding
st.markdown("""
    <style>
        html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
        .main { background-color: #f9f9f9; }
        h1, h2, h3, .stButton>button { color: #084966; }
        input[type='range']::-webkit-slider-runnable-track { background: #084966; }
        input[type='range']::-moz-range-track { background: #084966; }
        input[type='range']::-ms-track { background: #084966; }
        .as3-footer { text-align: center; margin-top: 3rem; font-size: 0.8rem; color: #888; }
    </style>
""", unsafe_allow_html=True)

st.image(
    "https://raw.githubusercontent.com/MyTKey78/streamlit-sykefrav-r/main/as3%20logo%20-%20ingen%20bakgrunn.png",
    width=200
)

st.title("Sykefraværskostnader i virksomheten")

# ────────────────────────────────────────────────────────────────────────────────
# Inndata (sidebar)
#  - Vi definerer ALT som brukes senere for å unngå NameError.
#  - Vikar/overtid er med igjen som i originalen (per dag).
# ────────────────────────────────────────────────────────────────────────────────
st.sidebar.header("Inndata for beregninger")
antall_ansatte = st.sidebar.number_input("Antall ansatte", min_value=1, value=50, step=1)
gjennomsnittslonn = st.sidebar.number_input(
    "Gjennomsnittslønn per ansatt (kr)", min_value=100_000, value=600_000, step=10_000
)
sykefravarsprosent = st.sidebar.slider("Sykefraværsprosent (%)", 0.0, 20.0, 5.0, 0.1)

# Disse to var årsaken til NameError tidligere – nå er de tilbake som inndata:
vikar_kostnad = st.sidebar.number_input(
    "Vikar-kostnad per dag (kr)", min_value=0, value=0, step=500,
    help="Sett til 0 hvis dere ikke bruker vikar"
)
overtid_kostnad = st.sidebar.number_input(
    "Overtid-kostnad per dag (kr)", min_value=0, value=0, step=500,
    help="Sett til 0 hvis dere ikke bruker overtid"
)

# ────────────────────────────────────────────────────────────────────────────────
# Beregninger
#  - Beholder opprinnelig logikk din (sosiale_avgifter = direkte * 1.14, osv.)
#  - Skalerer fra AGP (16 dager) til årsestimat (260 arb.dager).
# ────────────────────────────────────────────────────────────────────────────────
arbeidsdager_per_aar = 260
arbeidsgiverperiode = 16

# Direkte lønnskost i AGP gitt sykefraværsprosent
direkte_lonnskostnad = (
    gjennomsnittslonn
    * (sykefravarsprosent / 100.0)
    * (arbeidsgiverperiode / arbeidsdager_per_aar)
)

# I originalen var sosiale_avgifter = direkte * 1.14 (inkluderer direkte + 14%)
sosiale_avgifter = direkte_lonnskostnad * 1.14
indirekte_kostnader = direkte_lonnskostnad * 0.5

# Totale kostnader i AGP som følge av vikar/overtid (per dag * AGP-dager * fraværsandel * antall)
vikar_kostnad_total = (
    float(vikar_kostnad) * arbeidsgiverperiode * (sykefravarsprosent / 100.0) * antall_ansatte
)
overtid_kostnad_total = (
    float(overtid_kostnad) * arbeidsgiverperiode * (sykefravarsprosent / 100.0) * antall_ansatte
)

# Totalt i AGP per ansatt og for virksomheten (uten vikar/overtid)
total_kostnad_per_ansatt = sosiale_avgifter + indirekte_kostnader
total_kostnad_per_virksomhet = total_kostnad_per_ansatt * antall_ansatte

# Årsestimat (inkluderer vikar/overtid i årssummen, slik originalen gjorde)
total_aarskostnad = (
    (total_kostnad_per_virksomhet + vikar_kostnad_total + overtid_kostnad_total)
    * (arbeidsdager_per_aar / arbeidsgiverperiode)
)

# ────────────────────────────────────────────────────────────────────────────────
# Resultatvisning
# ────────────────────────────────────────────────────────────────────────────────
st.subheader("Beregnet sykefraværskostnad")
st.write(f"Totale kostnader for arbeidsgiverperioden **per ansatt**: **{total_kostnad_per_ansatt:,.0f} kr**")
st.write(f"Totale kostnader for arbeidsgiverperioden **for hele virksomheten**: **{total_kostnad_per_virksomhet:,.0f} kr**")
st.write(f"**Årlige** totale sykefraværskostnader (inkl. vikar/overtid): **{total_aarskostnad:,.0f} kr**")

# ────────────────────────────────────────────────────────────────────────────────
# Sammensetning (AGP) – tabell + diagram
#   For søylediagrammet viser vi 'Sosiale avgifter' som KUN 14%-delen,
#   slik at «direkte» ikke dobbelttelles i søylene.
# ────────────────────────────────────────────────────────────────────────────────
direkte_sum = float(direkte_lonnskostnad) * antall_ansatte
avgift_only_sum = float(direkte_lonnskostnad) * 0.14 * antall_ansatte  # kun 14% påslag
indirekte_sum = float(indirekte_kostnader) * antall_ansatte

rows = [
    {"Kategori": "Direkte lønnskostnader", "Kostnad (kr)": direkte_sum},
    {"Kategori": "Sosiale avgifter (14%)", "Kostnad (kr)": avgift_only_sum},
    {"Kategori": "Indirekte kostnader (50%)", "Kostnad (kr)": indirekte_sum},
    {"Kategori": "Vikarutgifter (AGP)", "Kostnad (kr)": float(vikar_kostnad_total)},
    {"Kategori": "Overtidsutgifter (AGP)", "Kostnad (kr)": float(overtid_kostnad_total)},
]
df = pd.DataFrame.from_records(rows)

st.subheader("Visuell fremstilling av kostnader i arbeidsgiverperioden (AGP)")
fig, ax = plt.subplots(figsize=(8, 6))
ax.bar(df["Kategori"], df["Kostnad (kr)"], color=["#084966", "#286488", "#3A7DA2", "#63CDF6", "#A3DAEB"])
ax.set_ylabel("Kostnad (kr)")
ax.set_title("Fordeling av sykefraværskostnader (AGP)")
ax.set_xticks(range(len(df)))
ax.set_xticklabels(df["Kategori"], rotation=45, ha="right")
st.pyplot(fig)

# ────────────────────────────────────────────────────────────────────────────────
# Eksport til Excel (AGP-sammensetning)
# ────────────────────────────────────────────────────────────────────────────────
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="Sykefraværskostnader (AGP)", index=False)

st.download_button(
    label="📥 Last ned som Excel",
    data=excel_buffer.getvalue(),
    file_name="sykefraværskostnader_agp.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ────────────────────────────────────────────────────────────────────────────────
# Besparelsesberegning (mål) – robust mot grenser
# ────────────────────────────────────────────────────────────────────────────────
st.subheader("💰 Hvor mye kan virksomheten spare?")
mål_default = max(min(sykefravarsprosent - 1.0, sykefravarsprosent), 0.0)
mål_sykefravær = st.slider(
    "Sett et mål for sykefraværsprosent (%)",
    0.0, float(sykefravarsprosent), float(mål_default), 0.1
)

direkte_lonnskostnad_ny = (
    gjennomsnittslonn
    * (mål_sykefravær / 100.0)
    * (arbeidsgiverperiode / arbeidsdager_per_aar)
)
sosiale_avgifter_ny = direkte_lonnskostnad_ny * 1.14
indirekte_kostnader_ny = direkte_lonnskostnad_ny * 0.5

total_kostnad_per_ansatt_ny = sosiale_avgifter_ny + indirekte_kostnader_ny
total_kostnad_per_virksomhet_ny = total_kostnad_per_ansatt_ny * antall_ansatte

# Merk: vi beholder de samme vikar/overtid-totalsatsene i mål-scenariet (konservativt).
total_aarskostnad_ny = (
    (total_kostnad_per_virksomhet_ny + vikar_kostnad_total + overtid_kostnad_total)
    * (arbeidsdager_per_aar / arbeidsgiverperiode)
)

aarsbesparelse = total_aarskostnad - total_aarskostnad_ny

st.write(f"🔹 Nåværende årlige kostnader: **{total_aarskostnad:,.0f} kr**")
st.write(f"🔹 Ved {mål_sykefravær:.1f}% sykefravær: **{total_aarskostnad_ny:,.0f} kr**")
st.success(f"💰 Potensiell årlig besparelse: **{aarsbesparelse:,.0f} kr**")

# ────────────────────────────────────────────────────────────────────────────────
# Link og footer
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("""
---
🔗 [Vil du få ned sykefraværskostnaden? Trykk her for å finne ut hvordan AS3 kan hjelpe.](https://blog.as3.no/sykefrav%C3%A6r_tjenester)
""")

st.markdown("<div class='as3-footer'>© 2024 AS3 Norge</div>", unsafe_allow_html=True)
