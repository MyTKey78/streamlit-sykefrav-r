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
        
    </div>
""", unsafe_allow_html=True)

st.markdown("<div class='as3-container'>", unsafe_allow_html=True)

# 🎯 Brukerinput for interaktive beregninger
st.sidebar.header("Inndata for beregninger")

antall_ansatte = st.sidebar.number_input("Antall ansatte", min_value=1, value=50)
gjennomsnittslonn = st.sidebar.number_input("Gjennomsnittslønn per ansatt (kr)", min_value=100000, value=600000, step=10000)
sykefravarsprosent = st.sidebar.slider("Sykefraværsprosent (%)", 0.0, 20.0, 5.0, 0.1)

bruker_vikar = st.sidebar.checkbox("Bruker vikar ved fravær?")
vikar_kostnad = st.sidebar.number_input("Vikarkostnad per dag (kr)", min_value=0, value=2500, step=500) if bruker_vikar else 0
overtidsbruk = st.sidebar.checkbox("Bruker overtid ved fravær?")
overtid_kostnad = st.sidebar.number_input("Overtidskostnad per dag (kr)", min_value=0, value=3000, step=500) if overtidsbruk else 0

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

# 🎯 DataFrame for eksport og visualisering
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

# 🎯 Diagram: Oversikt over kostnader
st.subheader("Visuell fremstilling av kostnader")
fig, ax = plt.subplots(figsize=(8,6))
kategorier = df["Kategori"]
verdier = df["Kostnad (kr)"]
ax.bar(kategorier, verdier, color=["#084966", "#286488", "#3A7DA2", "#8DD8F8", "#63CDF6"])
ax.set_ylabel("Kostnad (kr)")
ax.set_title("Fordeling av sykefraværskostnader")
ax.set_xticklabels(kategorier, rotation=45, ha="right")
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

# 🎯 Tiltaksanalyse
st.subheader("🔍 Hvordan redusere sykefraværet?")

def redusere_sykefravaer(analysevalg):
    råd = ""
    if "Arbeidsmiljø" in analysevalg:
        råd += "- **Forbedre arbeidsmiljøet**: Sørg for et trygt og inkluderende arbeidsmiljø...\n\n"
    if "Lederoppfølging" in analysevalg:
        råd += "- **Styrk lederoppfølging**: Gi ledere opplæring i sykefraværsoppfølging...\n\n"
    if "Helsefremmende tiltak" in analysevalg:
        råd += "- **Helsefremmende tiltak**: Tilby trening, helsekontroller og støtte...\n\n"
    if "Forebygging av langtidssykefravær" in analysevalg:
        råd += "- **Tidlig intervensjon**: Kartlegg risiko og tilpass arbeid...\n\n"
    if "Tilrettelegging" in analysevalg:
        råd += "- **Tilpass arbeidsoppgaver** for ansatte med helseutfordringer...\n\n"
    if råd == "":
        råd = "Velg minst én faktor for å få anbefalinger."
    return råd

analysevalg = st.multiselect(
    "Velg hvilke faktorer du vil analysere:",
    ["Arbeidsmiljø", "Lederoppfølging", "Helsefremmende tiltak", "Forebygging av langtidssykefravær", "Tilrettelegging"]
)

if st.button("📉 Få råd for å redusere sykefravær"):
    st.markdown(redusere_sykefravaer(analysevalg))

# 🎯 Besparelsesberegning
st.subheader("💰 Potensiell besparelse ved lavere sykefravær")
mål_sykefravær = st.slider("Sett et mål for sykefraværsprosent (%)", 0.0, sykefravarsprosent, sykefravarsprosent - 1.0, 0.1)

direkte_lonnskostnad_ny = (gjennomsnittslonn * (mål_sykefravær / 100) * (arbeidsgiverperiode / arbeidsdager_per_aar))
sosiale_avgifter_ny = direkte_lonnskostnad_ny * 1.14
indirekte_kostnader_ny = direkte_lonnskostnad_ny * 0.5

total_kostnad_per_ansatt_ny = sosiale_avgifter_ny + indirekte_kostnader_ny
total_kostnad_per_virksomhet_ny = total_kostnad_per_ansatt_ny * antall_ansatte
total_aarskostnad_ny = (total_kostnad_per_virksomhet_ny + vikar_kostnad_total + overtid_kostnad_total) * (arbeidsdager_per_aar / arbeidsgiverperiode)
aarsbesparelse = total_aarskostnad - total_aarskostnad_ny

st.write(f"🔹 Nåværende årlige kostnader: **{total_aarskostnad:,.0f} kr**")
st.write(f"🔹 Ved {mål_sykefravær:.1f}% sykefravær: **{total_aarskostnad_ny:,.0f} kr**")
st.success(f"💰 Potensiell årlig besparelse: **{aarsbesparelse:,.0f} kr**")

# 🎯 Footer
st.markdown("""
    <div style='text-align: center; margin-top: 2rem;'>
        <small>© 2024 AS3 Norge. Alle rettigheter forbeholdt.</small>
    </div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)





