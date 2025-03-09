# Brukerinput for sykefravær per måned
st.subheader("Legg inn sykefravær per måned (%)")

sykefravær_per_maaned = {}
maaneder = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Des"]

for mnd in maaneder:
    sykefravær_per_maaned[mnd] = st.slider(f"{mnd}", 0.0, 20.0, sykefravarsprosent, 0.1)

# Konverter input til DataFrame
data_trend = pd.DataFrame({
    "Måned": maaneder,
    "Sykefraværsprosent": [sykefravær_per_maaned[mnd] for mnd in maaneder]
})

# Beregn kostnader for hver måned
data_trend["Kostnad"] = (gjennomsnittslonn * (data_trend["Sykefraværsprosent"] / 100) * (arbeidsgiverperiode / arbeidsdager_per_aar)) * antall_ansatte

# Vis trendgraf
st.subheader("Trend for sykefraværskostnader basert på faktiske data")
fig, ax = plt.subplots(figsize=(8,6))
sns.lineplot(data=data_trend, x="Måned", y="Kostnad", marker="o", ax=ax, color="blue")
ax.set_ylabel("Kostnad (kr)")
ax.set_title("Utvikling av sykefraværskostnader over året basert på faktiske tall")
st.pyplot(fig)
