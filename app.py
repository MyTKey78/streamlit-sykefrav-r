import streamlit as st
}
return round(totale_kost), tapte_timer, detaljer


kost_nå, timer_nå, detaljer_nå = beregn_kostnader(sykefr_var)
kost_mål, timer_mål, detaljer_mål = beregn_kostnader(sykefr_mal)
innsparing = max(kost_nå - kost_mål, 0)


m1, m2, m3, m4 = st.columns(4)
with m1:
st.metric("Årlige kostnader i dag", f"{kost_nå:,.0f} kr")
with m2:
st.metric("Årlige kostnader ved mål", f"{kost_mål:,.0f} kr")
with m3:
st.metric("Potensiell innsparing/år", f"{innsparing:,.0f} kr")
with m4:
st.metric("Tapte timer (nå)", f"{timer_nå:,.0f}")


st.divider()


c1, c2 = st.columns(2)
with c1:
st.subheader("Kostnadsfordeling – nå")
df_nå = pd.DataFrame({"Kategori": list(detaller_nå := detaljer_nå.keys()), "Beløp": list(detaller_nå.values())})
st.bar_chart(df_nå.set_index("Kategori"))
with c2:
st.subheader("Kostnadsfordeling – mål")
df_mal = pd.DataFrame({"Kategori": list(detaller_mål := detaljer_mål.keys()), "Beløp": list(detaller_mål.values())})
st.bar_chart(df_mal.set_index("Kategori"))


st.divider()


st.subheader("Sensitivitetsanalyse")
colA, colB = st.columns(2)
with colA:
step = st.slider("Trinn (pp) for sensitivitet", 0.1, 5.0, 1.0, 0.1)
with colB:
ant_steg = st.slider("Antall steg hver vei", 1, 10, 3)


s_range = [max(sykefr_var - i*step, 0) for i in range(ant_steg, 0, -1)] + [sykefr_var] + [min(sykefr_var + i*step, 30.0) for i in range(1, ant_steg+1)]
res = []
for s in s_range:
k, t, _ = beregn_kostnader(s)
res.append({"Sykefravær %": s, "Kostnad (kr/år)": k})


sens_df = pd.DataFrame(res)
st.line_chart(sens_df.set_index("Sykefravær %"))


with st.expander("Antagelser og metode"):
st.markdown(
"""
**Forenklet modell:**
* Kostnad/time ≈ (årslønn × (1 + feriepenger) + AGA) / arbeidstimer.
* Tap i produksjon = tapte timer × kostnad/time × valgt produktivitetstap.
* Vikarkost = tapte timer × vikardekning × kostnad/time × (1 + påslag).
* Oppfølging/adm = antall tilfeller × kost pr. tilfelle (skalert med nivå på fravær).
* Refusjon (forenklet) reduserer kost på langtidsandelen, med 6G-tak (valgfritt).


Juster parametre for å speile deres virkelighet. Tallene er veiledende.
"""
)


st.caption("© AS3 Norge – Sykefraværskalkulatoren. Denne versjonen er laget for enkel redigering og utvidelse i Streamlit.")
