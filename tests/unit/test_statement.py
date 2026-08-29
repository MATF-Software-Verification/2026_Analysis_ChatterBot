# testovi za Statement
from datetime import datetime, timezone

from chatterbot.conversation import Statement


def test_tekst_se_pretvara_u_string():
    # conversation.py:80 radi str(text)
    assert Statement(text=42).text == '42'


def test_podrazumevane_vrednosti():
    statement = Statement(text='zdravo')

    assert statement.in_response_to is None
    assert statement.search_text == ''
    assert statement.tags == []
    assert statement.confidence == 0


def test_tagovi():
    statement = Statement(text='zdravo')

    statement.add_tags('pozdrav', 'test')

    assert statement.get_tags() == ['pozdrav', 'test']


def test_serialize_vraca_sva_polja():
    # serialize pravi recnik za upis u bazu
    podaci = Statement(text='zdravo', in_response_to='pitanje').serialize()

    assert podaci['text'] == 'zdravo'
    assert podaci['in_response_to'] == 'pitanje'


def test_bag_6_created_at_je_lokalno_vreme_oznaceno_kao_utc():
    # nalaz #6 lokalno vreme dobije oznaku UTC bez konverzije
    # conversation.py:92 i :99
    lokalno_sada = datetime.now()

    statement = Statement(text='zdravo')

    assert statement.created_at.tzinfo == timezone.utc
    razlika = abs((statement.created_at.replace(tzinfo=None) - lokalno_sada).total_seconds())
    assert razlika < 5


def test_str_vraca_tekst():
    assert str(Statement(text='zdravo')) == 'zdravo'


def test_repr_prikazuje_tekst():
    assert repr(Statement(text='zdravo')) == '<Statement text:zdravo>'


def test_prazan_tekst_je_dozvoljen():
    assert Statement(text='').text == ''


def test_in_response_to_se_moze_zadati():
    statement = Statement(text='odgovor', in_response_to='pitanje')

    assert statement.in_response_to == 'pitanje'


def test_persona_se_moze_zadati():
    assert Statement(text='zdravo', persona='korisnik').persona == 'korisnik'


def test_conversation_se_moze_zadati():
    assert Statement(text='zdravo', conversation='sesija-1').conversation == 'sesija-1'


def test_confidence_se_moze_zadati():
    assert Statement(text='zdravo', confidence=0.5).confidence == 0.5


def test_tagovi_se_dodaju_u_vise_poziva():
    statement = Statement(text='zdravo')

    statement.add_tags('a')
    statement.add_tags('b', 'c')

    assert statement.get_tags() == ['a', 'b', 'c']


def test_dve_recenice_ne_dele_tagove():
    prva = Statement(text='a')
    druga = Statement(text='b')

    prva.add_tags('samo-prvoj')

    assert druga.get_tags() == []


def test_serialize_ima_devet_polja():
    podaci = Statement(text='zdravo').serialize()

    assert len(podaci) == 9


def test_serialize_sadrzi_ocekivane_kljuceve():
    podaci = Statement(text='zdravo').serialize()

    assert 'text' in podaci
    assert 'search_text' in podaci
    assert 'created_at' in podaci


def test_created_at_iz_stringa():
    statement = Statement(text='zdravo', created_at='2020-05-17T12:30:00')

    assert statement.created_at.year == 2020
    assert statement.created_at.month == 5
    assert statement.created_at.day == 17


def test_search_text_se_moze_zadati():
    statement = Statement(text='zdravo', search_text='INTJ:zdravo')

    assert statement.search_text == 'INTJ:zdravo'
