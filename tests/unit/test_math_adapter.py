# Testovi za MathematicalEvaluation, najjednostavniji logic adapter.
# Prepozna matematicki izraz u recenici, izracuna ga i vrati rezultat.
import pytest
from chatterbot import ChatBot
from chatterbot.conversation import Statement
from chatterbot.logic import MathematicalEvaluation


@pytest.fixture
def adapter():
    # adapteru treba bot, pa ga pravimo sa bazom u memoriji
    bot = ChatBot('TestBot', database_uri=None, initialize=False)
    return MathematicalEvaluation(bot)


def test_prepoznaje_matematicki_izraz(adapter):
    assert adapter.can_process(Statement(text='What is 10 plus 10?')) is True


def test_ne_prepoznaje_obican_tekst(adapter):
    assert adapter.can_process(Statement(text='Kako si danas?')) is False


def test_racuna_izraz(adapter):
    statement = Statement(text='What is 10 plus 10?')
    adapter.can_process(statement)      # ovde se rezultat kesira

    odgovor = adapter.process(statement)

    assert odgovor.text == '10 plus 10 = 20'
    assert odgovor.confidence == 1


def test_moze_da_se_koristi_kao_alat(adapter):
    # adapter moze i direktno da se pozove, npr. iz LLM adaptera
    assert adapter.execute_as_tool(expression='five times five') == 'five times five = 25'


def test_alat_bez_izraza_vraca_gresku(adapter):
    assert adapter.execute_as_tool() == 'Error: No expression provided'


# jos nekoliko jednostavnih provera

@pytest.mark.parametrize('pitanje, ocekivano', [
    ('What is 2 + 2?', '2 + 2 = 4'),
    ('What is 5 minus 3?', '5 minus 3 = 2'),
    ('What is 7 times 3?', '7 times 3 = 21'),
    ('What is 100 divided by 4?', '100 divided by 4 = 25'),
])
def test_racuna_razlicite_izraze(adapter, pitanje, ocekivano):
    statement = Statement(text=pitanje)
    adapter.can_process(statement)

    assert adapter.process(statement).text == ocekivano


@pytest.mark.parametrize('tekst', [
    'Zdravo',
    'Kako se zoves?',
    '',
])
def test_ne_prepoznaje_tekst_bez_izraza(adapter, tekst):
    assert adapter.can_process(Statement(text=tekst)) is False


def test_pouzdanost_je_uvek_jedan(adapter):
    # kad prepozna izraz, adapter je siguran u svoj odgovor
    statement = Statement(text='What is 3 + 3?')
    adapter.can_process(statement)

    assert adapter.process(statement).confidence == 1


def test_alat_racuna_sabiranje(adapter):
    assert adapter.execute_as_tool(expression='two plus two') == 'two plus two = 4'


def test_alat_vraca_gresku_za_besmislen_izraz(adapter):
    rezultat = adapter.execute_as_tool(expression='zdravo kako si')

    assert 'Error' in rezultat


def test_odgovor_je_statement_objekat(adapter):
    statement = Statement(text='What is 1 + 1?')
    adapter.can_process(statement)

    assert isinstance(adapter.process(statement), Statement)
