import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# 🎯 Tittel
st.title("Sykefraværskostnader i virksomheten")

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

# 🎯 Vise resultater
st.subheader("Beregnet sykefraværskostnad")
st.write(f"Totale kostnader for arbeidsgiverperioden per ansatt: **{total_kostnad_per_ansatt:,.0f} kr**")
st.write(f"Totale kostnader for hele virksomheten i arbeidsgiverperioden: **{total_kostnad_per_virksomhet:,.0f} kr**")
st.write(f"Årlige totale sykefraværskostnader (inkl. vikar/overtid): **{total_aarskostnad:,.0f} kr**")

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

ax.bar(kategorier, verdier, color=["red", "blue", "purple", "yellow", "green"])
ax.set_ylabel("Kostnad (kr)")
ax.set_title("Fordeling av sykefraværskostnader")
ax.set_xticklabels(kategorier, rotation=45, ha="right")
st.pyplot(fig)

# 🎯 Eksport til Excel
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name="Sykefraværskostnader", index=False)
st.download_button(label="📥 Last ned som Excel", data=excel_buffer.getvalue(), file_name="sykefraværskostnader.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown('[🔗 Vil du ha hjelp til å få ned kostnadene? Ta kontakt med AS3 Norge her](https://www.as3.no/for-virksomheter/#sykefravr)')

# 📌 Kildehenvisninger
st.markdown("## 📚 Kildehenvisninger")
st.markdown("""
- **NAVs sykefraværsstatistikk**: [NAV – Sykefravær](https://www.nav.no/no/nav-og-samfunn/statistikk/sykefravar-statistikk)  
- **Arbeidsgiverperioden på 16 dager**: [Lovdata – Folketrygdloven § 8-19](https://lovdata.no/dokument/NL/lov/1997-02-28-19/KAPITTEL_8#%C2%A78-19)  
- **Sosiale avgifter (14%)**: Basert på vanlige norske arbeidsgiveravgifter  
- **Indirekte kostnader (50% av lønn)**: HR-beregninger brukt i sykefraværsanalyser  
""")

def redusere_sykefravaer(analysevalg):
    råd = ""

    if "Arbeidsmiljø" in analysevalg:
        råd += "- **Forbedre arbeidsmiljøet:** Sørg for et trygt og inkluderende arbeidsmiljø. Vurder tiltak som bedre ergonomi, fleksibilitet i arbeidstider og trivselstiltak.\n\n"
    
    if "Lederoppfølging" in analysevalg:
        råd += "- **Styrke lederoppfølging:** God lederkommunikasjon og tett oppfølging av ansatte kan redusere sykefravær. Gi ledere opplæring i sykefraværsoppfølging.\n\n"
    
    if "Helsefremmende tiltak" in analysevalg:
        råd += "- **Helsefremmende tiltak:** Tilby treningstilbud, helsekontroller og psykologisk støtte for å fremme helse og velvære blant ansatte.\n\n"

    if "Forebygging av langtidssykefravær" in analysevalg:
        råd += "- **Forebygge langtidssykefravær:** Tidlig intervensjon er nøkkelen. Kartlegg risikofaktorer og legg til rette for tilpasninger før fraværet blir langvarig.\n\n"

    if "Tilrettelegging" in analysevalg:
        råd += "- **Bedre tilrettelegging:** Tilpass arbeidsoppgaver for ansatte med helseutfordringer. Bruk delvis sykemelding og gradvis tilbakeføring for å unngå langtidsfravær.\n\n"

    if råd == "":
        råd = "Velg minst én faktor for å få anbefalinger om hvordan redusere sykefraværet."

    return råd

# 🎯 Brukerinput for sykefraværsanalyse
st.subheader("🔍 Hvordan redusere sykefraværet?")
analysevalg = st.multiselect(
    "Velg hvilke faktorer du vil analysere:",
    ["Arbeidsmiljø", "Lederoppfølging", "Helsefremmende tiltak", "Forebygging av langtidssykefravær", "Tilrettelegging"]
)

if st.button("📉 Få råd for å redusere sykefravær"):
    råd = redusere_sykefr
# 🎯 Beregning av besparelse ved redusert sykefravær
st.subheader("💰 Hvor mye kan virksomheten spare?")
mål_sykefravær = st.slider("Sett et mål for sykefraværsprosent (%)", 0.0, sykefravarsprosent, max(0.0, sykefravarsprosent - 2.0), 0.1)

# Beregn ny kostnad basert på mål
direkte_lonnskostnad_ny = (gjennomsnittslonn * (mål_sykefravær / 100) * (arbeidsgiverperiode / arbeidsdager_per_aar))
sosiale_avgifter_ny = direkte_lonnskostnad_ny * 1.14
indirekte_kostnader_ny = direkte_lonnskostnad_ny * 0.5

total_kostnad_per_ansatt_ny = sosiale_avgifter_ny + indirekte_kostnader_ny
total_kostnad_per_virksomhet_ny = total_kostnad_per_ansatt_ny * antall_ansatte

# Beregn besparelse for arbeidsgiverperioden
besparelse = total_kostnad_per_virksomhet - total_kostnad_per_virksomhet_ny

# Beregn årlig besparelse
total_aarskostnad_ny = (total_kostnad_per_virksomhet_ny * (arbeidsdager_per_aar / arbeidsgiverperiode))
total_aarskostnad_nå = (total_kostnad_per_virksomhet * (arbeidsdager_per_aar / arbeidsgiverperiode))
aarsbesparelse = total_aarskostnad_nå - total_aarskostnad_ny

# 🎯 Vise resultat
st.write(f"🔹 **Nåværende kostnad i arbeidsgiverperioden**: {total_kostnad_per_virksomhet:,.0f} kr")
st.write(f"🔹 **Ny kostnad ved {mål_sykefravær:.1f}% sykefravær**: {total_kostnad_per_virksomhet_ny:,.0f} kr")
st.write(f"✅ **Potensiell besparelse i arbeidsgiverperioden**: **{besparelse:,.0f} kr**")

st.write("---")

st.write(f"📆 **Nåværende årlige sykefraværskostnader**: {total_aarskostnad_nå:,.0f} kr")
st.write(f"📆 **Nye årlige kostnader ved {mål_sykefravær:.1f}% sykefravær**: {total_aarskostnad_ny:,.0f} kr")
st.write(f"💰 **Årlig total besparelse**: **{aarsbesparelse:,.0f} kr** 🎉")
