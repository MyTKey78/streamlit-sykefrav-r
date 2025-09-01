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

antall_ansatte = st.sidebar.number_input(
    "Antall ansatte", min_value=1, value=50, step=1
)

gjennomsnittslonn = st.sidebar.number_input(
    "Gjennomsnittslønn per ansatt (kr)",
    min_value=100_000, value=600_000, step=10_000
)

sykefravarsprosent = st.sidebar.slider(
    "Sykefraværsprosent (%)",
    0.0, 20.0, 5.0, 0.1
)

vikar_kostnad = st.sidebar.number_input(
    "Vikar-kostnad per dag (kr)",
    min_value=0, value=0, step=500,
    help="Sett til 0 hvis dere ikke bruker vikar"
)

overtid_kostnad = st.sidebar.number_input(
    "Overtid-kostnad per dag (kr)",
    min_value=0, value=0, step=500,
    help="Sett til 0 hvis dere ikke bruker overtid"
)

# Antall sykefraværstilfeller pr ansatt per år (gjennomsnitt)
tilfeller_per_ansatt = st.sidebar.number_input(
    "Tilfeller pr ansatt pr år",
    min_value=0.0, value=1.0, step=0.1
)

# Hvor mange ARBEIDSDAGER av de første 16 kalenderdagene som faktisk gir lønnskost (typisk ~12)
agp_arbeidsdager = st.sidebar.number_input(
    "AGP-arbeidsdager (av 16 kal.dager)",
    min_value=1, value=12, step=1,
    help="Helger gir normalt ikke lønn – 16 kalenderdager ≈ ca. 12 arbeidsdager"
)

# ────────────────────────────────────────────────────────────────────────────────
# Beregninger (KORRIGERT LOGIKK)
#  - Dagskost = årslønn * (1 + AGA) / 260
#  - AGP-kostnad pr TILFELLE = dagskost * agp_arbeidsdager (ingen NAV-refusjon i AGP)
#  - Per ansatt pr år = pr tilfelle * tilfeller_per_ansatt
#  - For virksomheten = per ansatt * antall ansatte
#  - Vikar/overtid knyttes til AGP-dager, skalert på antall tilfeller og ansatte
# ────────────────────────────────────────────────────────────────────────────────
arbeidsdager_per_aar = 260
arbeidsgiverperiode = 16
aga_sats = 0.141  # 14,1% (endre hvis dere bruker annen sone)

# Dagskost inkl. AGA
dagskost = gjennomsnittslonn * (1.0 + aga_sats) / arbeidsdager_per_aar

# Kostnad i arbeidsgiverperioden PR TILFELLE (ingen refusjon)
agp_kostnad_pr_tilfelle = dagskost * agp_arbeidsdager

# Estimat PR ANSATT PR ÅR (gitt antall tilfeller pr ansatt)
agp_kostnad_pr_ansatt_pr_aar = agp_kostnad_pr_tilfelle * float(tilfeller_per_ansatt)

# For hele virksomheten
agp_kostnad_virksomhet_pr_aar = agp_kostnad_pr_ansatt_pr_aar * int(antall_ansatte)

# Vikar/overtid i AGP (per dag * AGP-dager * antall tilfeller * antall ansatte)
vikar_kostnad_total = float(vikar_kostnad) * int(agp_arbeidsdager) * float(tilfeller_per_ansatt) * int(antall_ansatte)
overtid_kostnad_total = float(overtid_kostnad) * int(agp_arbeidsdager) * float(tilfeller_per_ansatt) * int(antall_ansatte)

# Inkluder evt. «indirekte» kostnader som multiplikator (valgfritt).
# Her bevarer vi din 50%-antakelse, men anvender den på AGP-grunnkost (uten vikar/overtid).
indirekte_andel = 0.50
indirekte_kostnader_virksomhet = agp_kostnad_virksomhet_pr_aar * indirekte_andel

# Totalt (AGP-relatert) pr år for virksomheten
total_agp_virksomhet_pr_aar = agp_kostnad_virksomhet_pr_aar + indirekte_kostnader_virksomhet + vikar_kostnad_total + overtid_kostnad_total

# Merk: sykefraværsprosent brukes ikke lenger direkte i AGP-kostnaden – AGP avhenger av antall tilfeller.
# Hvis du ønsker en egen «fullt årsfravær»-kostnad basert på prosent, kan vi legge til det som separat visning senere.

# ────────────────────────────────────────────────────────────────────────────────
# Resultatvisning
# ────────────────────────────────────────────────────────────────────────────────
st.write(f"Kostnad i AGP **per tilfelle** (uten refusjon): **{agp_kostnad_pr_tilfelle:,.0f} kr**")
st.write(f"Kostnad i AGP **per ansatt per år** (gitt {tilfeller_per_ansatt:.1f} tilfeller): **{agp_kostnad_pr_ansatt_pr_aar:,.0f} kr**")
st.write(f"AGP-kostnad **for hele virksomheten per år** (inkl. indirekte {int(indirekte_andel*100)}%, vikar og overtid): **{total_agp_virksomhet_pr_aar:,.0f} kr**")

# ────────────────────────────────────────────────────────────────────────────────
# Sammensetning (AGP) – tabell + diagram
#   For søylediagrammet viser vi 'Sosiale avgifter' som KUN 14%-delen,
#   slik at «direkte» ikke dobbelttelles i søylene.
# ────────────────────────────────────────────────────────────────────────────────
direkte_dagskost = gjennomsnittslonn / arbeidsdager_per_aar
aga_dagskost = direkte_dagskost * aga_sats

# Sum for virksomheten, pr år (skalert med tilfeller og agp_arbeidsdager)
faktor = int(antall_ansatte) * float(tilfeller_per_ansatt) * int(agp_arbeidsdager)

direkte_sum = direkte_dagskost * faktor
aga_sum = aga_dagskost * faktor
indirekte_sum = (direkte_sum + aga_sum) * indirekte_andel

rows = [
    {"Kategori": "Direkte lønn (AGP)", "Kostnad (kr)": direkte_sum},
    {"Kategori": "Arbeidsgiveravgift (AGP)", "Kostnad (kr)": aga_sum},
    {"Kategori": "Indirekte kostnader (50%)", "Kostnad (kr)": indirekte_sum},
    {"Kategori": "Vikarutgifter (AGP)", "Kostnad (kr)": float(vikar_kostnad_total)},
    {"Kategori": "Overtidsutgifter (AGP)", "Kostnad (kr)": float(overtid_kostnad_total)},
]
df = pd.DataFrame.from_records(rows)

st.subheader("Visuell fremstilling av AGP-kostnader (per år, virksomheten)")
fig, ax = plt.subplots(figsize=(8, 6))
ax.bar(df["Kategori"], df["Kostnad (kr)"])
ax.set_ylabel("Kostnad (kr)")
ax.set_title("Fordeling av sykefraværskostnader i arbeidsgiverperioden (AGP)")
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
