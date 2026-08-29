
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
    # f(f(x)) mora da bude isto kao f(x)
    jednom = clean_whitespace(Statement(text=tekst)).text
    dvaput = clean_whitespace(Statement(text=jednom)).text

    assert jednom == dvaput


@given(st.text())
def test_konverzija_daje_samo_ascii(tekst):
    # encode puca ako izlaz nije ascii
    convert_to_ascii(Statement(text=tekst)).text.encode('ascii')


@given(st.text(max_size=30), st.text(max_size=30))
@settings(max_examples=200)
def test_slicnost_je_izmedju_0_i_1(a, b):
    assert 0.0 <= levenshtein.compare_text(a, b) <= 1.0


@given(st.text(max_size=30))
@settings(max_examples=200)
def test_tekst_je_maksimalno_slican_sam_sebi(a):
    assert levenshtein.compare_text(a, a) == 1.0


# nalaz #1 parser sme da vrati praznu listu ali ne sme da pukne
# ulaze je nasao Hypothesis

def test_bag_1a_last_month_puca_u_januaru():
    # parsing.py:609 u januaru dobije mesec 0
    with pytest.raises(ValueError, match='month must be in 1..12'):
        datetime_parsing('last month', base_date=datetime(2026, 1, 15))


def test_bag_1b_last_month_puca_31_u_mesecu():
    # ne skracuje dan na duzinu ciljnog meseca
    with pytest.raises(ValueError, match='day is out of range'):
        datetime_parsing('last month', base_date=datetime(2026, 3, 31))


def test_bag_1c_end_of_the_week_uvek_puca():
    # parsing.py:636 sabira int i timedelta
    with pytest.raises(TypeError):
        datetime_parsing('end of the week', base_date=datetime(2026, 6, 15))


def test_bag_1d_29_sati_puca():
    # N hours se tumaci kao doba dana
    with pytest.raises(ValueError, match='hour must be in 0..23'):
        datetime_parsing('29 hours', base_date=datetime(2026, 6, 15))


def test_bag_1e_end_of_the_ponedeljak_puca():
    # parsing.py:564 vrati None pa se na to dodaje timedelta
    with pytest.raises(TypeError):
        datetime_parsing('end of the monday', base_date=datetime(2026, 6, 15))
