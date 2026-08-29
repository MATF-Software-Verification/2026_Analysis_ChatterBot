# Testovi za komparatore. Oni racunaju koliko su dva teksta slicna, od 0 do 1.
import warnings

import pytest
from chatterbot.comparisons import LevenshteinDistance, SpacySimilarity, JaccardSimilarity
from chatterbot.languages import ENG


# Komparatori se prave jednom za ceo fajl (scope='module') jer konstruktor
# ucitava spaCy model, a to traje par sekundi.
@pytest.fixture(scope='module')
def levenshtein():
    return LevenshteinDistance(ENG)


@pytest.fixture(scope='module')
def jaccard():
    return JaccardSimilarity(ENG)


@pytest.fixture(scope='module')
def spacy_slicnost():
    return SpacySimilarity(ENG)


def test_levenshtein_primer_iz_dokumentacije(levenshtein):
    # u komentaru klase (comparisons.py:42) pise da je ova slicnost 65%
    rezultat = levenshtein.compare_text(
        'where is the post office?',
        'looking for the post office'
    )

    assert rezultat == 0.65


def test_levenshtein_ne_gleda_velika_i_mala_slova(levenshtein):
    assert levenshtein.compare_text('Hello', 'hello') == 1.0


@pytest.mark.parametrize('a, b', [('hello', None), (None, 'hello')])
def test_levenshtein_vraca_nulu_za_none(levenshtein, a, b):
    # None ovde nije greska, znaci da teksta nema
    assert levenshtein.compare_text(a, b) == 0


def test_jaccard_delimicno_poklapanje(jaccard):
    # 'hello world' daje leme {hello, world}, a 'hello there' samo {hello}
    # jer je 'there' stop-rec. Presek / unija = 1/2.
    assert jaccard.compare_text('hello world', 'hello there') == 0.5


def test_bag_2_jaccard_deli_nulom(jaccard):
    # nalaz #2: kad su oba teksta samo stop-reci, skupovi lema ostanu prazni
    # pa comparisons.py:183 deli nulom
    with pytest.raises(ZeroDivisionError):
        jaccard.compare_text('the', 'the')


def test_bag_5_spacy_bez_vektora(spacy_slicnost):
    # nalaz #5: model iz constants.py:36 nema vektore reci, pa i nepovezane
    # recenice dobiju slicnost oko 0.87 i spaCy javi upozorenje W007
    with warnings.catch_warnings(record=True) as uhvacena:
        warnings.simplefilter('always')
        rezultat = spacy_slicnost.compare_text(
            'the cat sat on the mat',
            'a dog ran in the park'
        )

    poruke = ' '.join(str(u.message) for u in uhvacena)

    assert 'no word vectors loaded' in poruke
    assert rezultat > 0.8


def test_bag_4_levenshtein_nije_simetrican(levenshtein):
    # nalaz #4: zamena argumenata menja rezultat, jer difflib.SequenceMatcher
    # gleda indekse drugog niza. Kontraprimer je nasao Hypothesis.
    assert levenshtein.compare_text('ab', 'bacb') == 0.67
    assert levenshtein.compare_text('bacb', 'ab') == 0.33


# jos nekoliko jednostavnih provera

def test_levenshtein_isti_tekst(levenshtein):
    assert levenshtein.compare_text('hello', 'hello') == 1.0


def test_levenshtein_potpuno_razlicit_tekst(levenshtein):
    assert levenshtein.compare_text('abc', 'xyz') == 0.0


def test_levenshtein_prazan_i_prazan(levenshtein):
    # dva prazna teksta su ista, pa je slicnost 1
    assert levenshtein.compare_text('', '') == 1.0


def test_levenshtein_tekst_i_prazan(levenshtein):
    assert levenshtein.compare_text('hello', '') == 0.0


def test_levenshtein_slicne_reci(levenshtein):
    # 'cat' i 'cats' se razlikuju samo u jednom slovu
    assert levenshtein.compare_text('cat', 'cats') == 0.86


def test_levenshtein_rezultat_je_izmedju_nule_i_jedan(levenshtein):
    rezultat = levenshtein.compare_text('dobar dan', 'dobro vece')

    assert 0.0 <= rezultat <= 1.0


def test_levenshtein_svi_veliki_slova(levenshtein):
    assert levenshtein.compare_text('HELLO', 'hello') == 1.0


def test_jaccard_isti_tekst(jaccard):
    assert jaccard.compare_text('hello world', 'hello world') == 1.0


def test_jaccard_bez_poklapanja(jaccard):
    assert jaccard.compare_text('cat', 'dog') == 0.0


def test_jaccard_ne_gleda_velika_i_mala_slova(jaccard):
    assert jaccard.compare_text('Hello World', 'hello world') == 1.0


def test_jaccard_redosled_reci_nije_bitan(jaccard):
    # poredi skupove lema, pa redosled reci ne utice na rezultat
    assert jaccard.compare_text('cat dog', 'dog cat') == 1.0


def test_jaccard_vraca_nulu_za_none(jaccard):
    assert jaccard.compare_text(None, 'hello') == 0


def test_spacy_vraca_nulu_za_none(spacy_slicnost):
    assert spacy_slicnost.compare_text('hello', None) == 0
