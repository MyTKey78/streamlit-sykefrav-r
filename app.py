def beregn_sykefravaerskostnad(
    antall_ansatte,
    arslonn_per_ansatt,
    antall_arbeidsdager=230,
    fravaersprosent=0.064,
    langtidsandel=0.60,
    refusjonsandel=2/3,
    datakilde="NAV",
    fravaerstype="total"
):
    """
    Beregner sykefraværskostnader basert på datakilde og fraværstype.

    fravaerstype: "kort", "lang" eller "total"

    Kildeinformasjon:
    - NAV: Tall fra legemeldt sykefraværsstatistikk, nasjonalt gjennomsnitt ca. 6,4 % sykefravær, hvor ca. 60 % er langtidsfravær.
    - SINTEF: Basert på forskningsrapporter med bransjetilpassede analyser, høyere nivåer av langtidsfravær (opptil 75 %) og total sykefraværsprosent ca. 8 % i offentlige virksomheter.
    - Arbeidsgiverperioden dekkes av arbeidsgiver, og refusjon beregnes for langtidsfravær etter 16 dager, vanligvis 2/3 av varigheten.
    """
    loenn_per_dag = arslonn_per_ansatt / antall_arbeidsdager

    if fravaerstype == "kort":
        justert_fravaersprosent = fravaersprosent * (1 - langtidsandel)
        refusjon = 0  # Ingen refusjon for korttidsfravær
    elif fravaerstype == "lang":
        justert_fravaersprosent = fravaersprosent * langtidsandel
        refusjonsgrunnlag = justert_fravaersprosent * antall_arbeidsdager * antall_ansatte * refusjonsandel
        refusjon = refusjonsgrunnlag * loenn_per_dag
    else:  # total
        justert_fravaersprosent = fravaersprosent
        refusjonsgrunnlag = (fravaersprosent * antall_arbeidsdager * antall_ansatte) * langtidsandel * refusjonsandel
        refusjon = refusjonsgrunnlag * loenn_per_dag

    fravaersdager_per_ansatt = justert_fravaersprosent * antall_arbeidsdager
    total_fravaersdager = fravaersdager_per_ansatt * antall_ansatte

    brutto_kostnad = total_fravaersdager * loenn_per_dag
    netto_kostnad = brutto_kostnad - refusjon

    return {
        "Datakilde": datakilde,
        "Fraværstype": fravaerstype,
        "Antall ansatte": antall_ansatte,
        "Fraværsprosent": round(justert_fravaersprosent * 100, 1),
        "Brutto kostnad": round(brutto_kostnad, 0),
        "Refusjon": round(refusjon, 0),
        "Netto kostnad": round(netto_kostnad, 0)
    }

# Eksempler
nav_total = beregn_sykefravaerskostnad(
    antall_ansatte=100,
    arslonn_per_ansatt=600000,
    fravaersprosent=0.064,
    langtidsandel=0.60,
    datakilde="NAV",
    fravaerstype="total"
)

sintef_total = beregn_sykefravaerskostnad(
    antall_ansatte=100,
    arslonn_per_ansatt=600000,
    fravaersprosent=0.080,
    langtidsandel=0.75,
    datakilde="SINTEF",
    fravaerstype="total"
)

sintef_lang = beregn_sykefravaerskostnad(
    antall_ansatte=100,
    arslonn_per_ansatt=600000,
    fravaersprosent=0.080,
    langtidsandel=0.75,
    datakilde="SINTEF",
    fravaerstype="lang"
)

print("NAV totalberegning:", nav_total)
print("SINTEF totalberegning:", sintef_total)
print("SINTEF langtidsfravær:", sintef_lang)




