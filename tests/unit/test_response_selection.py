# Testovi za funkcije koje biraju jedan odgovor kada ima vise kandidata.
# get_most_frequent_response jedina od njih dira bazu, pa joj umesto prave
# baze dajemo lazni objekat koji ima samo metodu filter().
from chatterbot.conversation import Statement
from chatterbot.response_selection import (
    get_first_response,
    get_random_response,
    get_most_frequent_response,
)


class LazniStorage:
    # umesto SQL upita, filtriramo obicnu listu u memoriji

    def __init__(self, recenice):
        self.recenice = recenice

    def filter(self, **kwargs):
        trazeno = kwargs.get('in_response_to')
        return [r for r in self.recenice if r.in_response_to == trazeno]


def test_prvi_odgovor():
    kandidati = [Statement(text='prvi'), Statement(text='drugi')]

    assert get_first_response(Statement(text='pitanje'), kandidati).text == 'prvi'


def test_nasumican_odgovor_je_iz_liste():
    # ne mozemo da predvidimo koji ce biti izabran, ali mora biti iz liste
    kandidati = [Statement(text='a'), Statement(text='b'), Statement(text='c')]

    for _ in range(20):
        assert get_random_response(Statement(text='pitanje'), kandidati) in kandidati


def test_bira_najcesci_odgovor():
    # 'cao' je tri puta zapisan kao odgovor na 'hej', a 'zdravo' samo jednom
    baza = LazniStorage([
        Statement(text='zdravo', in_response_to='hej'),
        Statement(text='cao', in_response_to='hej'),
        Statement(text='cao', in_response_to='hej'),
        Statement(text='cao', in_response_to='hej'),
    ])
    kandidati = [Statement(text='zdravo'), Statement(text='cao')]

    izbor = get_most_frequent_response(Statement(text='hej'), kandidati, storage=baza)

    assert izbor.text == 'cao'


def test_bag_7_vraca_none_umesto_statement():
    # nalaz #7: u potpisu (response_selection.py:50) pise da vraca Statement,
    # ali za praznu listu vrati None. Isto je prijavio i mypy.
    izbor = get_most_frequent_response(Statement(text='pitanje'), [], storage=LazniStorage([]))

    assert izbor is None


# jos nekoliko jednostavnih provera

def test_prvi_odgovor_sa_jednim_kandidatom():
    kandidati = [Statement(text='jedini')]

    assert get_first_response(Statement(text='pitanje'), kandidati).text == 'jedini'


def test_prvi_odgovor_vraca_bas_taj_objekat():
    # nema kopiranja, vraca se isti objekat koji je bio u listi
    prvi = Statement(text='prvi')
    kandidati = [prvi, Statement(text='drugi')]

    assert get_first_response(Statement(text='pitanje'), kandidati) is prvi


def test_prvi_odgovor_sa_tri_kandidata():
    kandidati = [Statement(text='a'), Statement(text='b'), Statement(text='c')]

    assert get_first_response(Statement(text='pitanje'), kandidati).text == 'a'


def test_nasumican_odgovor_sa_jednim_kandidatom():
    # kad je kandidat samo jedan, nasumican izbor je uvek isti
    kandidati = [Statement(text='jedini')]

    assert get_random_response(Statement(text='pitanje'), kandidati).text == 'jedini'


def test_najcesci_odgovor_sa_jednim_kandidatom():
    baza = LazniStorage([])
    kandidati = [Statement(text='jedini')]

    izbor = get_most_frequent_response(Statement(text='pitanje'), kandidati, storage=baza)

    assert izbor.text == 'jedini'


def test_najcesci_odgovor_kada_nijedan_nije_u_bazi():
    # svi imaju nula pojavljivanja, pa zbog uslova >= pobedi poslednji
    baza = LazniStorage([])
    kandidati = [Statement(text='a'), Statement(text='b')]

    izbor = get_most_frequent_response(Statement(text='pitanje'), kandidati, storage=baza)

    assert izbor.text == 'b'


def test_najcesci_odgovor_gleda_samo_svoje_pitanje():
    # recenice koje su odgovor na neko drugo pitanje ne treba da se broje
    baza = LazniStorage([
        Statement(text='cao', in_response_to='drugo pitanje'),
        Statement(text='cao', in_response_to='drugo pitanje'),
        Statement(text='zdravo', in_response_to='hej'),
    ])
    kandidati = [Statement(text='cao'), Statement(text='zdravo')]

    izbor = get_most_frequent_response(Statement(text='hej'), kandidati, storage=baza)

    assert izbor.text == 'zdravo'


def test_lazni_storage_filtrira_po_pitanju():
    # provera da lazni objekat zaista radi ono sto od njega ocekujemo
    baza = LazniStorage([
        Statement(text='a', in_response_to='hej'),
        Statement(text='b', in_response_to='nesto drugo'),
    ])

    rezultat = baza.filter(in_response_to='hej')

    assert len(rezultat) == 1
    assert rezultat[0].text == 'a'
