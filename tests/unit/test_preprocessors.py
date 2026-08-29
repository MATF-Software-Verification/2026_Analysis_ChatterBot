# testovi za preprocesore
import pytest
from chatterbot.conversation import Statement
from chatterbot.preprocessors import clean_whitespace, convert_to_ascii, unescape_html


@pytest.mark.parametrize('ulaz, ocekivano', [
    ('a  b', 'a b'),          # dva razmaka -> jedan
    ('  a b  ', 'a b'),       # beline sa krajeva se brisu
    ('a\tb', 'a b'),          # tab -> razmak
    ('a\nb', 'a b'),          # novi red -> razmak
    ('   ', ''),              # sami razmaci -> prazan tekst
])
def test_clean_whitespace(ulaz, ocekivano):
    """provera za sve slucajeve parametara"""
    assert clean_whitespace(Statement(text=ulaz)).text == ocekivano


def test_clean_whitespace_menja_isti_objekat():
    """proverava da li se menja bas onaj objekat koji je prosledjen"""
    statement = Statement(text='a  b')

    rezultat = clean_whitespace(statement)

    assert rezultat is statement
    assert statement.text == 'a b'


@pytest.mark.parametrize('ulaz, ocekivano', [
    ('&lt;b&gt;', '<b>'),     # primer iz dokumentacije funkcije
    ('&amp;', '&'),
    ('bez entiteta', 'bez entiteta'),
])
def test_unescape_html(ulaz, ocekivano):
    assert unescape_html(Statement(text=ulaz)).text == ocekivano


def test_unescape_html_menja_isto_objekat():
    statement = Statement(text='&amp;')

    rezultat = unescape_html(statement)

    assert rezultat is statement
    assert statement.text == '&'


@pytest.mark.parametrize('ulaz, ocekivano', [
    ('på fédéral', 'pa federal'),   # primer iz dokumentacije
    ('Čačak', 'Cacak'),
])
def test_convert_to_ascii(ulaz, ocekivano):
    assert convert_to_ascii(Statement(text=ulaz)).text == ocekivano


def test_convert_to_ascii_brise_cirilicu():
    assert convert_to_ascii(Statement(text='Здраво')).text == ''


def test_convert_to_ascii_menja_isti_objekat():
    statmanet = Statement(text='Čačak')

    rezultat = convert_to_ascii(statmanet)

    assert rezultat is statmanet
    assert statmanet.text == 'Cacak'


def test_clean_whitespace_cist_tekst_ostaje_isti():
    assert clean_whitespace(Statement(text='ovo je vec cisto')).text == 'ovo je vec cisto'


def test_clean_whitespace_jedna_rec():
    assert clean_whitespace(Statement(text='zdravo')).text == 'zdravo'


def test_clean_whitespace_prazan_tekst():
    assert clean_whitespace(Statement(text='')).text == ''


def test_clean_whitespace_vise_praznih_redova():
    assert clean_whitespace(Statement(text='a\n\n\nb')).text == 'a b'


def test_clean_whitespace_tab_i_razmak_zajedno():
    assert clean_whitespace(Statement(text='a \t b')).text == 'a b'


def test_clean_whitespace_windows_prelom_reda():
    assert clean_whitespace(Statement(text='a\r\nb')).text == 'a b'


def test_unescape_html_veca_zagrada():
    assert unescape_html(Statement(text='&gt;')).text == '>'


def test_unescape_html_navodnici():
    assert unescape_html(Statement(text='&quot;zdravo&quot;')).text == '"zdravo"'


def test_unescape_html_apostrof():
    assert unescape_html(Statement(text='&#39;')).text == "'"


def test_unescape_html_broj_entiteta():
    assert unescape_html(Statement(text='&#65;')).text == 'A'


def test_unescape_html_prazan_tekst():
    assert unescape_html(Statement(text='')).text == ''


def test_convert_to_ascii_obican_tekst_ostaje_isti():
    assert convert_to_ascii(Statement(text='hello world')).text == 'hello world'


def test_convert_to_ascii_brojevi_ostaju():
    assert convert_to_ascii(Statement(text='123')).text == '123'


def test_convert_to_ascii_prazan_tekst():
    assert convert_to_ascii(Statement(text='')).text == ''


def test_convert_to_ascii_emoji_se_brise():
    assert convert_to_ascii(Statement(text='zdravo 😀')).text == 'zdravo '


def test_convert_to_ascii_nemacko_slovo():
    assert convert_to_ascii(Statement(text='über')).text == 'uber'


def test_sva_tri_preprocesora_zajedno():
    # ovako se ulancavaju u botu
    statement = Statement(text='  &lt;b&gt;   Čačak  ')

    statement = clean_whitespace(statement)
    statement = unescape_html(statement)
    statement = convert_to_ascii(statement)

    assert statement.text == '<b> Cacak'
