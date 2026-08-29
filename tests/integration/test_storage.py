
import pytest
from chatterbot.storage import SQLStorageAdapter


@pytest.fixture
def skladiste(tmp_path):
    # nova prazna baza za svaki test
    # zastita za search_text nam ovde ne treba
    adapter = SQLStorageAdapter(
        database_uri='sqlite:///{}'.format(tmp_path / 'test.sqlite3'),
        raise_on_missing_search_text=False,
    )

    yield adapter

    adapter.drop()
    adapter.close()


def test_prazna_baza(skladiste):
    assert skladiste.count() == 0


def test_upis_i_citanje(skladiste):
    skladiste.create(text='zdravo', in_response_to='hej')

    rezultat = list(skladiste.filter(text='zdravo'))

    assert len(rezultat) == 1
    assert rezultat[0].in_response_to == 'hej'
    assert rezultat[0].id is not None      # baza je dodelila primarni kljuc


def test_filtriranje_po_in_response_to(skladiste):
    # ovako bot trazi odgovore
    skladiste.create(text='zdravo', in_response_to='hej')
    skladiste.create(text='cao', in_response_to='hej')
    skladiste.create(text='nesto', in_response_to='drugo pitanje')

    rezultat = list(skladiste.filter(in_response_to='hej'))

    assert {r.text for r in rezultat} == {'zdravo', 'cao'}


def test_tagovi_se_cuvaju_u_svojoj_tabeli(skladiste):
    # tagovi idu u zasebnu tabelu
    skladiste.create(text='zdravo', tags=['pozdrav'])
    skladiste.create(text='zbogom', tags=['rastanak'])

    pozdravi = list(skladiste.filter(tags=['pozdrav']))

    assert [r.text for r in pozdravi] == ['zdravo']


def test_brisanje(skladiste):
    skladiste.create(text='zdravo')
    skladiste.create(text='cao')

    skladiste.remove('zdravo')

    assert skladiste.count() == 1


def test_prazna_baza_daje_jasnu_gresku(skladiste):
    # prazna baza ima svoju gresku
    with pytest.raises(SQLStorageAdapter.EmptyDatabaseException):
        skladiste.get_random()


def test_podaci_prezivljavaju_zatvaranje_veze(tmp_path):
    # upis jednim adapterom pa citanje drugim
    putanja = 'sqlite:///{}'.format(tmp_path / 'trajna.sqlite3')

    prvi = SQLStorageAdapter(database_uri=putanja, raise_on_missing_search_text=False)
    prvi.create(text='zapamti me')
    prvi.close()

    drugi = SQLStorageAdapter(database_uri=putanja, raise_on_missing_search_text=False)
    try:
        assert len(list(drugi.filter(text='zapamti me'))) == 1
    finally:
        drugi.drop()
        drugi.close()
