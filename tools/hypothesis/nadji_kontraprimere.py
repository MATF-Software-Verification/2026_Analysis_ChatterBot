# pokazna skripta za nalaz #1 kako Hypothesis nalazi ulaze koji obaraju parser
# alat sam pravi fraze i proverava jedno svojstvo:
# datetime_parsing ne sme da pukne
# fraze se sastavljaju od reci koje parser prepoznaje, jer nasumican tekst
# ('xqz42') ne lici na datum pa se zanimljive grane ne izvrse
# pokretanje:  python tools/hypothesis/nadji_kontraprimere.py
from datetime import datetime
from hypothesis import given, settings, strategies as st, HealthCheck
from chatterbot.parsing import datetime_parsing


# reci koje parser prepoznaje
RECI = [
    'january', 'february', 'june', 'monday', 'friday',
    'today', 'tomorrow', 'yesterday',
    'next', 'last', 'this', 'end of the',
    'day', 'week', 'month', 'year', 'hours', 'days',
    'ago', 'from now', 'in', 'on', 'the', 'of',
    '1', '13', '29', '30', '31', '31st',
    'morning', 'midnight',
]

# fraza je 1-4 reci iz RECI spojene razmakom -> 'next friday'
fraza = st.lists(st.sampled_from(RECI), min_size=1, max_size=4).map(' '.join)

# nasumican datum izmedju 2020. i 2030.
bazni_datum = st.datetimes(datetime(2020, 1, 1), datetime(2030, 12, 31))

# kljuc je opis greske, vrednost je fraza koja ju je izazvala
# recnik je van funkcije da bi preziveo svih 5000 poziva
greske = {}


@given(fraza, bazni_datum)
@settings(max_examples=5000, deadline=None, derandomize=True,
          suppress_health_check=list(HealthCheck))
def proveri(tekst, datum):
    # Hypothesis ovo poziva 5000 puta, svaki put sa novom frazom i datumom
    try:
        datetime_parsing(tekst, base_date=datum)
    except Exception as e:
        opis = '{}: {}'.format(type(e).__name__, e)
        # pamti se samo prva fraza za svaku vrstu greske
        if opis not in greske:
            greske[opis] = tekst
        # greska se ne baca dalje, da alat nadje sve vrste a ne stane na prvoj


if __name__ == '__main__':
    print('Trazim fraze koje obaraju datetime_parsing...\n')

    proveri()   # pokrece svih 5000 provera i puni recnik greske

    if not greske:
        print('Nijedna fraza nije oborila parser.')
    else:
        print('Pronadjene greske:\n')
        for opis, tekst in sorted(greske.items()):
            print('  fraza {!r} -> {}'.format(tekst, opis))
        print('\nUkupno razlicitih gresaka:', len(greske))
