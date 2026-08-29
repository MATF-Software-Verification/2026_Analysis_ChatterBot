# Testovi za utils.py. Tu je mehanizam kojim ChatterBot ucitava komponente po
# imenu, zbog cega se bot i konfigurise stringovima:
# ChatBot('Bot', logic_adapters=['chatterbot.logic.BestMatch']).
import pytest
from chatterbot import ChatBot
from chatterbot.adapters import Adapter
from chatterbot.logic import LogicAdapter
from chatterbot.storage import StorageAdapter
from chatterbot.utils import import_module, initialize_class, validate_adapter_class


def test_import_module_vraca_klasu():
    # dobija se sama klasa, ne njena instanca
    Klasa = import_module('chatterbot.logic.BestMatch')

    assert Klasa.__name__ == 'BestMatch'


def test_import_module_puca_za_nepostojecu_klasu():
    with pytest.raises(AttributeError):
        import_module('chatterbot.logic.NepostojecaKlasa')


def test_validacija_puca_za_pogresan_tip():
    # tipicna korisnicka greska: storage adapter tamo gde ide logic adapter
    with pytest.raises(Adapter.InvalidAdapterTypeException):
        validate_adapter_class('chatterbot.storage.SQLStorageAdapter', LogicAdapter)


def test_bag_8a_import_path_se_prosledjuje_konstruktoru():
    # nalaz #8a: utils.py:26 koristi data.get umesto data.pop, pa import_path
    # ostane u recniku i zavrsi kao parametar konstruktora
    with pytest.raises(TypeError, match='import_path'):
        initialize_class({'import_path': 'chatterbot.tagging.LowercaseTagger'})


def test_bag_8b_menja_korisnikov_recnik():
    # nalaz #8b: data.update(kwargs) u utils.py:27 menja recnik koji je dao
    # korisnik, pa u njemu zavrsi i lista koja sadrzi taj isti recnik
    konfiguracija = {'import_path': 'chatterbot.logic.BestMatch'}

    ChatBot('Test', database_uri=None, initialize=False, logic_adapters=[konfiguracija])

    assert 'database_uri' in konfiguracija      # ovoga nije bilo pre poziva
    assert konfiguracija['logic_adapters'][0] is konfiguracija


# jos nekoliko jednostavnih provera

def test_import_module_vraca_storage_klasu():
    Klasa = import_module('chatterbot.storage.SQLStorageAdapter')

    assert Klasa.__name__ == 'SQLStorageAdapter'


def test_import_module_vraca_funkciju():
    # ne mora da bude klasa, moze i funkcija kao sto je preprocesor
    funkcija = import_module('chatterbot.preprocessors.clean_whitespace')

    assert funkcija.__name__ == 'clean_whitespace'


def test_import_module_puca_za_nepostojeci_modul():
    with pytest.raises(ModuleNotFoundError):
        import_module('chatterbot.nepostojeci.Klasa')


def test_validacija_prolazi_za_logic_adapter():
    # ne baca izuzetak jer BestMatch jeste logic adapter
    validate_adapter_class('chatterbot.logic.BestMatch', LogicAdapter)


def test_validacija_prolazi_za_storage_adapter():
    validate_adapter_class('chatterbot.storage.SQLStorageAdapter', StorageAdapter)


def test_validacija_puca_za_recnik_bez_import_path():
    with pytest.raises(Adapter.InvalidAdapterTypeException):
        validate_adapter_class({'nema': 'import_path'}, StorageAdapter)


def test_initialize_class_pravi_instancu_iz_stringa():
    tagger = initialize_class('chatterbot.tagging.LowercaseTagger')

    assert tagger.__class__.__name__ == 'LowercaseTagger'


def test_bot_se_moze_napraviti_sa_adapterom_kao_stringom():
    # najcesci nacin konfiguracije iz dokumentacije
    bot = ChatBot(
        'Test',
        database_uri=None,
        initialize=False,
        logic_adapters=['chatterbot.logic.BestMatch'],
    )

    assert len(bot.logic_adapters) == 1
    assert bot.logic_adapters[0].__class__.__name__ == 'BestMatch'


def test_bot_moze_da_ima_vise_adaptera():
    bot = ChatBot(
        'Test',
        database_uri=None,
        initialize=False,
        logic_adapters=[
            'chatterbot.logic.MathematicalEvaluation',
            'chatterbot.logic.BestMatch',
        ],
    )

    assert len(bot.logic_adapters) == 2
