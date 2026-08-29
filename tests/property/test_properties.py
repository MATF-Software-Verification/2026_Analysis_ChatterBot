# Property-based testovi (Hypothesis). Umesto pojedinacnog primera zadajemo
# svojstvo koje mora da vazi za svaki ulaz, a alat sam pravi ulaze i trazi
# onaj koji ga obori. st.text() u @given znaci "bilo kakav tekst".
from datetime import datetime

import pytest
from hypothesis import given, strategies as st, settings
from chatterbot.comparisons import LevenshteinDistance
from chatterbot.conversation import Statement
from chatterbot.languages import ENG
from chatterbot.parsing import datetime_parsing
from chatterbot.preprocessors import clean_whitespace, convert_to_ascii

levenshtein = LevenshteinDistance(ENG)


@given(st.text())
def test_ciscenje_ne_ostavlja_dvostruke_razmake(tekst):
    assert '  ' not in clean_whitespace(Statement(text=tekst)).text


@given(st.text())
def test_ciscenje_je_idempotentno(tekst):
    # f(f(x)) == f(x); bitno jer se preprocesori primenjuju u petlji
    jednom = clean_whitespace(Statement(text=tekst)).text
    dvaput = clean_whitespace(Statement(text=jednom)).text

    assert jednom == dvaput


@given(st.text())
def test_konverzija_daje_samo_ascii(tekst):
    # ako izlaz nije ASCII, encode ce baciti izuzetak i test pada
    convert_to_ascii(Statement(text=tekst)).text.encode('ascii')


@given(st.text(max_size=30), st.text(max_size=30))
@settings(max_examples=200)
def test_slicnost_je_izmedju_0_i_1(a, b):
    assert 0.0 <= levenshtein.compare_text(a, b) <= 1.0


@given(st.text(max_size=30))
@settings(max_examples=200)
def test_tekst_je_maksimalno_slican_sam_sebi(a):
    assert levenshtein.compare_text(a, a) == 1.0


# Nalaz #1: datetime_parsing sme da vrati praznu listu, ali ne sme da pukne.
# Ulaze je nasao Hypothesis (tools/hypothesis/nadji_kontraprimere.py), ovde
# su zapisani najmanji primeri.

def test_bag_1a_last_month_puca_u_januaru():
    # parsing.py:609 racuna datetime(godina, mesec - 1, dan), pa u januaru
    # dobije mesec 0. Grana za "next month" prelaz preko godine radi ispravno.
    with pytest.raises(ValueError, match='month must be in 1..12'):
        datetime_parsing('last month', base_date=datetime(2026, 1, 15))


def test_bag_1b_last_month_puca_31_u_mesecu():
    # ista linija ne skracuje dan na duzinu ciljnog meseca: 31. mart -> 31. februar
    with pytest.raises(ValueError, match='day is out of range'):
        datetime_parsing('last month', base_date=datetime(2026, 3, 31))


def test_bag_1c_end_of_the_week_uvek_puca():
    # parsing.py:636 uzima base_date.weekday() (int) pa to sabira sa timedelta;
    # istu gresku je prijavio i mypy, a "end of the month" radi normalno
    with pytest.raises(TypeError):
        datetime_parsing('end of the week', base_date=datetime(2026, 6, 15))


def test_bag_1d_29_sati_puca():
    # parsing.py:496-501 tumaci "N hours" kao doba dana umesto kao trajanje,
    # pa pravi datetime sa satom 29
    with pytest.raises(ValueError, match='hour must be in 0..23'):
        datetime_parsing('29 hours', base_date=datetime(2026, 6, 15))


def test_bag_1e_end_of_the_ponedeljak_puca():
    # date_from_relative_day (parsing.py:564) nema granu za "end of the" pa
    # vrati None, a pozivalac na to dodaje timedelta. Mypy je to prijavio kao
    # "Missing return statement".
    with pytest.raises(TypeError):
        datetime_parsing('end of the monday', base_date=datetime(2026, 6, 15))
