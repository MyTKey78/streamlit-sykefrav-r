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
# Konstanter (REN SINTEF)
# ────────────────────────────────────────────────────────────────────────────────
ARBEIDSDAGER_PER_AAR = 260
SINTEF_KOSTNAD_PER_DAG = 4200  # kr per årsverk per sykefraværsdag

# ────────────────────────────────────────────────────────────────────────────────
# Inndata (sidebar)
# ────────────────────────────────────────────────────────────────────────────────
st.sidebar.header("Inndata for beregninger")

antall_ansatte = st.sidebar.number_input(
    "Antall ansatte (årsverk)", min_value=1, value=50, step=1
)

sykefravarsprosent = st.sidebar.slider(
    "Dagens sykefraværsprosent (%)",
    0.0, 30.0, 7.0, 0.1
)

# Valgfrie tillegg utenfor SINTEF (settes til 0 om dere ikke vil bruke dem)
st.sidebar.markdown("— *Valgfrie tillegg (utenfor SINTEF)* —")
vikar_kostnad_per_dag = st.sidebar.number_input(
    "Vikar-kostnad per dag (kr)", min_value=0, value=0, step=500,
    help="Tillegg utenfor SINTEF. Sett 0 hvis ikke relevant."
)
overtid_kostnad_per_dag = st.sidebar.number_input(
    "Overtid-kostnad per dag (kr)", min_value=0, value=0, step=500,
    help="Tillegg utenfor SINTEF. Sett 0 hvis ikke relevant."
)

# ────────────────────────────────────────────────────────────────────────────────
# Beregninger – dagens nivå (REN SINTEF + valgfrie tillegg)
# ────────────────────────────────────────────────────────────────────────────────
# Sykedager per årsverk
sykedager_per_arsverk = (sykefravarsprosent / 100.0) * ARBEIDSDAGER_PER_AAR

# Kostnad per årsverk (SINTEF)
sintef_kost_per_arsverk = sykedager_per_arsverk * SINTEF_KOSTNAD_PER_DAG

# Tillegg per årsverk (utenfor SINTEF)
tillegg_per_arsverk = sykedager_per_arsverk * (vikar_kostnad_per_dag + overtid_kostnad_per_dag)

# Totalt per årsverk og for virksomheten
total_per_arsverk = sintef_kost_per_arsverk + tillegg_per_arsverk
total_aarskostnad = total_per_arsverk * antall_ansatte  # <-- DEFINERT TIDLIG

# ────────────────────────────────────────────────────────────────────────────────
# Resultatvisning – dagens nivå
# ────────────────────────────────────────────────────────────────────────────────
st.subheader("Dagens kostnader")
col1, col2, col3 = st.columns(3)
col1.metric("Sykedager pr. årsverk", f"{sykedager_per_arsverk:,.1f} dager")
col2.metric("SINTEF-kost pr. årsverk", f"{sintef_kost_per_arsverk:,.0f} kr")
col3.metric("Tillegg pr. årsverk", f"{tillegg_per_arsverk:,.0f} kr")

st.write("---")
st.metric("Total årlig kostnad (dagens)", f"{total_aarskostnad:,.0f} kr")

# ────────────────────────────────────────────────────────────────────────────────
# Sammensetning – tabell + diagram
# ────────────────────────────────────────────────────────────────────────────────
rows = [
    {"Kategori": "Basiskostnad", "Kostnad (kr)": sintef_kost_per_arsverk * antall_ansatte},
    {"Kategori": "Vikar (tillegg)", "Kostnad (kr)": (sykedager_per_arsverk * vikar_kostnad_per_dag) * antall_ansatte},
    {"Kategori": "Overtid (tillegg)", "Kostnad (kr)": (sykedager_per_arsverk * overtid_kostnad_per_dag) * antall_ansatte},
]
df = pd.DataFrame.from_records(rows)

st.subheader("Fordeling av årlige kostnader")
fig, ax = plt.subplots(figsize=(8, 6))
ax.bar(df["Kategori"], df["Kostnad (kr)"])
ax.set_ylabel("Kostnad (kr)")
ax.set_title("Sammensetning: SINTEF-basiskostnad + eventuelle tillegg")
ax.set_xticks(range(len(df)))
ax.set_xticklabels(df["Kategori"], rotation=20, ha="right")
st.pyplot(fig)

# ────────────────────────────────────────────────────────────────────────────────
# Eksport til Excel (sammensetning)
# ────────────────────────────────────────────────────────────────────────────────
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="Sykefraværskostnader (SINTEF)", index=False)

st.download_button(
    label="📥 Last ned som Excel",
    data=excel_buffer.getvalue(),
    file_name="sykefraværskostnader_sintef.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ────────────────────────────────────────────────────────────────────────────────
# Mål/Scenario – beregn besparelse (REN SINTEF + samme tilleggssatser)
# ────────────────────────────────────────────────────────────────────────────────
st.subheader("💰 Hvor mye kan virksomheten spare?")
mål_default = max(sykefravarsprosent - 1.0, 0.0)
mål_sykefravær = st.slider(
    "Sett et mål for sykefraværsprosent (%)",
    0.0, float(sykefravarsprosent), float(mål_default), 0.1
)

sykedager_per_arsverk_ny = (mål_sykefravær / 100.0) * ARBEIDSDAGER_PER_AAR
sintef_kost_per_arsverk_ny = sykedager_per_arsverk_ny * SINTEF_KOSTNAD_PER_DAG
tillegg_per_arsverk_ny = sykedager_per_arsverk_ny * (vikar_kostnad_per_dag + overtid_kostnad_per_dag)

total_per_arsverk_ny = sintef_kost_per_arsverk_ny + tillegg_per_arsverk_ny
total_aarskostnad_ny = total_per_arsverk_ny * antall_ansatte  # <-- DEFINERT FØR BRUK

aarsbesparelse = total_aarskostnad - total_aarskostnad_ny

st.write(f"🔹 Ved {mål_sykefravær:.1f}% sykefravær: **{total_aarskostnad_ny:,.0f} kr/år**")
st.success(f"💰 Potensiell årlig besparelse: **{aarsbesparelse:,.0f} kr**")

# ────────────────────────────────────────────────────────────────────────────────
# Link og footer
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("""
---
🔗 [Vil du få ned sykefraværskostnaden? Slik kan AS3 hjelpe.](https://blog.as3.no/sykefrav%C3%A6r_tjenester)
""")

st.markdown("<div class='as3-footer'>© 2025 AS3 Norge</div>", unsafe_allow_html=True)

