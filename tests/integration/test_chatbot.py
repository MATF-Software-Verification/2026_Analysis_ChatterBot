# Integracioni testovi celog toka: trening, odgovaranje i ucenje.
# Ovde rade svi slojevi zajedno - prava baza, pravi spaCy model i pravi
# treneri - pa se hvataju greske koje nastaju tek u spoju komponenti.
import json

import pytest
from chatterbot import ChatBot
from chatterbot.tagging import PosLemmaTagger
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer, JsonFileTrainer


@pytest.fixture(scope='module')
def tagger():
    # spaCy model se ucitava par sekundi, pa ga pravimo jednom za ceo fajl
    return PosLemmaTagger()


@pytest.fixture
def bot(tagger, tmp_path):
    chatbot = ChatBot(
        'TestBot',
        database_uri='sqlite:///{}'.format(tmp_path / 'bot.sqlite3'),
        initialize=False,      # da ne preuzima podatke sa interneta
        tagger=tagger,
    )

    yield chatbot

    chatbot.storage.drop()
    chatbot.storage.close()


def treniraj(bot, recenice):
    # ListTrainer uci bota da je svaka recenica odgovor na prethodnu
    ListTrainer(bot, show_training_progress=False).train(recenice)


def test_bot_odgovara_nauceno(bot):
    treniraj(bot, ['Hello', 'Hi there!', 'How are you?', 'I am good.'])

    odgovor = bot.get_response('How are you?')

    assert odgovor.text == 'I am good.'
    assert odgovor.confidence > 0.9


def test_slicno_pitanje_daje_isti_odgovor(bot):
    # bot ne trazi doslovno poklapanje nego najslicniju zapamcenu recenicu
    treniraj(bot, ['What is your name?', 'My name is ChatterBot.'])

    odgovor = bot.get_response('What is your name')     # bez upitnika

    assert odgovor.text == 'My name is ChatterBot.'


def test_preprocesor_ucestvuje_u_toku(bot):
    # visak beline se cisti pre pretrage, inace se ulaz ne bi poklopio
    treniraj(bot, ['What is your name?', 'My name is ChatterBot.'])

    odgovor = bot.get_response('  What   is your name?  ')

    assert odgovor.text == 'My name is ChatterBot.'


def test_bot_uci_iz_razgovora(bot):
    # bot u bazu upisuje i korisnikov ulaz i svoj odgovor, pa baza raste
    treniraj(bot, ['Hello', 'Hi there!'])
    pre = bot.storage.count()

    bot.get_response('Hello')

    assert bot.storage.count() > pre


def test_read_only_bot_ne_uci(tagger, tmp_path):
    # read_only je jedini prekidac izmedju "bot uci" i "bot ne uci"
    bot = ChatBot(
        'ReadOnly',
        database_uri='sqlite:///{}'.format(tmp_path / 'ro.sqlite3'),
        initialize=False, tagger=tagger, read_only=True,
    )
    try:
        treniraj(bot, ['Hello', 'Hi there!'])
        pre = bot.storage.count()

        bot.get_response('Hello')

        assert bot.storage.count() == pre
    finally:
        bot.storage.drop()
        bot.storage.close()


def test_netreniran_bot_ne_puca(bot):
    # nad praznom bazom BestMatch vrati sam ulaz sa pouzdanoscu 0
    odgovor = bot.get_response('Nesto sto bot ne zna')

    assert odgovor.confidence == 0


def test_matematicki_adapter_pobedjuje_po_pouzdanosti(tagger, tmp_path):
    # kad ima vise adaptera, bira se onaj sa najvecom pouzdanoscu;
    # MathematicalEvaluation za prepoznat izraz vraca 1
    bot = ChatBot(
        'Racunar',
        database_uri='sqlite:///{}'.format(tmp_path / 'math.sqlite3'),
        initialize=False, tagger=tagger,
        logic_adapters=['chatterbot.logic.MathematicalEvaluation', 'chatterbot.logic.BestMatch'],
    )
    try:
        treniraj(bot, ['Hello', 'Hi there!'])

        odgovor = bot.get_response('What is 4 + 4?')

        assert '8' in odgovor.text
        assert odgovor.confidence == 1
    finally:
        bot.storage.drop()
        bot.storage.close()


def test_trening_iz_korpusa(bot):
    # korpus dolazi iz zasebnog paketa chatterbot_corpus
    ChatterBotCorpusTrainer(bot, show_training_progress=False).train(
        'chatterbot.corpus.english.greetings'
    )

    assert bot.storage.count() > 10


def test_bag_9_bot_ponavlja_korisnikov_ulaz(bot):
    # nalaz #9: obe recenice dobiju isti indeks za pretragu, pa BestMatch u
    # drugoj fazi (best_match.py:85) medju kandidate uvuce i sam trenirani
    # ulaz i onda ga vrati. Za par ['Hello', 'Hi there!'] ovo se ne desava.
    treniraj(bot, ['Good morning', 'Good morning to you too'])

    odgovor = bot.get_response('Good morning')

    assert odgovor.text == 'Good morning'       # ocekivano: 'Good morning to you too'


def test_bag_9_koren_isti_indeks_za_razlicite_recenice(bot):
    # koren baga #9, izolovan: dve razlicite recenice daju isti indeks
    assert bot.tagger.get_text_index_string('Good morning') == 'ADJ:morning'
    assert bot.tagger.get_text_index_string('Good morning to you too') == 'ADJ:morning'


def test_bag_10_izvoz_se_ne_moze_uvesti(bot, tmp_path):
    # nalaz #10: izvoz (trainers.py:75) pise kljuc "conversations" i listu
    # parova, a JsonFileTrainer (:310) cita "conversation" i ocekuje listu
    # recnika, pa uvoz puca
    trener = ListTrainer(bot, show_training_progress=False)
    trener.train(['Hello', 'Hi there!'])
    izlaz = tmp_path / 'izvoz.json'

    trener.export_for_training(str(izlaz))

    assert json.loads(izlaz.read_text(encoding='utf-8')) == {
        'conversations': [['Hello', 'Hi there!']]
    }
    with pytest.raises(KeyError, match='conversation'):
        JsonFileTrainer(bot, show_training_progress=False).train(str(izlaz))
