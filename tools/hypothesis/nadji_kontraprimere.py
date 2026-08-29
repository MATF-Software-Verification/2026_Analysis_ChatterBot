"""
Pokazna skripta: kako Hypothesis pronalazi bagove u parseru datuma.

Ideja: Hypothesis sam pravi gomilu fraza i proverava jednu stvar -
'datetime_parsing ne sme da pukne (baci gresku)'. Ako pukne, zapisujemo
koja fraza ga je oborila.

Zasto fraze pravimo od unapred izabranih reci: nasumican tekst ('xqz42')
skoro nikad ne lici na datum, pa parser na njemu ne radi nista zanimljivo.
Zato koristimo reci koje parser prepoznaje ('january', 'tomorrow'...).

Pokretanje:  python tools/hypothesis/nadji_kontraprimere.py
"""
from datetime import datetime
from hypothesis import given, settings, strategies as st, HealthCheck
from chatterbot.parsing import datetime_parsing


# Reci koje parser prepoznaje.
RECI = [
    'january', 'february', 'june', 'monday', 'friday',
    'today', 'tomorrow', 'yesterday',
    'next', 'last', 'this', 'end of the',
    'day', 'week', 'month', 'year', 'hours', 'days',
    'ago', 'from now', 'in', 'on', 'the', 'of',
    '1', '13', '29', '30', '31', '31st',
    'morning', 'midnight',
]

# Recept za frazu: uzmi 1-4 reci iz RECI i spoji ih razmakom -> 'next friday'.
fraza = st.lists(st.sampled_from(RECI), min_size=1, max_size=4).map(' '.join)

# Recept za datum: nasumican datum izmedju 2020. i 2030.
bazni_datum = st.datetimes(datetime(2020, 1, 1), datetime(2030, 12, 31))

# Ovde skupljamo greske. Kljuc = opis greske, vrednost = fraza koja ju je izazvala.
# Recnik je van funkcije da bi preziveo svih 5000 poziva.
greske = {}


@given(fraza, bazni_datum)
@settings(max_examples=5000, deadline=None, derandomize=True,
          suppress_health_check=list(HealthCheck))
def proveri(tekst, datum):
    """Hypothesis ovo poziva 5000 puta, svaki put sa novom frazom i datumom."""
    try:
        datetime_parsing(tekst, base_date=datum)
    except Exception as e:
        opis = '{}: {}'.format(type(e).__name__, e)
        # Zapamti samo prvu frazu za svaku vrstu greske (ostale duplikate preskoci).
        if opis not in greske:
            greske[opis] = tekst
        # Gresku NE bacamo dalje - da Hypothesis nastavi i nadje sve vrste,
        # a ne da stane na prvoj.


if __name__ == '__main__':
    print('Trazim fraze koje obaraju datetime_parsing...\n')

    proveri()   # pokrece svih 5000 provera; puni recnik `greske`

    if not greske:
        print('Nijedna fraza nije oborila parser.')
    else:
        print('Pronadjene greske:\n')
        for opis, tekst in sorted(greske.items()):
            print('  fraza {!r} -> {}'.format(tekst, opis))
        print('\nUkupno razlicitih gresaka:', len(greske))