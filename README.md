# Analiza projekta ChatterBot

Seminarski rad iz predmeta Verifikacija softvera, Matematički fakultet,
Univerzitet u Beogradu.

## Autor

Bogdan Tomić, broj indeksa 1040/2025, [github.com/BogBogdan](https://github.com/BogBogdan)

## Analizirani projekat

[ChatterBot](https://github.com/gunthercox/ChatterBot), grana `master`, komit
[`feafc81`](https://github.com/gunthercox/ChatterBot/commit/feafc81a00be8b8bb65622e4ddc89ebf7b3e1329)
(verzija 1.2.13, licenca BSD-3-Clause, oko 10.400 linija Python koda).

To je biblioteka za pravljenje chat botova. Ne koristi jezički model. Bot pamti
rečenice u bazi, a kad dobije pitanje traži najsličniju zapamćenu rečenicu i
vraća ono što je zapisano kao odgovor na nju.

Projekat je uključen kao git submodul u folderu `ChatterBot/` i **njegov kod nije
menjan**. Sve što je pisano u okviru rada, dakle testovi, skripte i izveštaj,
stoji izvan tog foldera.

## Zavisnosti

| Šta | Verzija | Čemu služi |
|---|---|---|
| Python | 3.12.10 | sve se izvršava pod njim |
| git | bilo koja | preuzimanje submodula |
| bash | Git Bash na Windowsu | pokretanje `*.sh` skripti |
| spaCy model `en_core_web_sm` | 3.8.0 | obrada teksta u ChatterBot-u |

Biblioteke se instaliraju iz `requirements.txt`, sa zakucanim verzijama da bi
brojke iz izveštaja važile i kod drugog korisnika:

| Biblioteka | Verzija |
|---|---|
| pytest | 9.0.3 |
| pytest-cov | 7.1.0 |
| coverage | 7.14.0 |
| hypothesis | 6.145.1 |
| flake8 | 7.3.0 |
| mypy | 1.19.0 |
| bandit | 1.9.2 |

Sam ChatterBot se ne instalira sa PyPI-ja nego iz submodula, u razvojnom režimu,
da bi se analizirao tačno onaj kod koji je u repozitorijumu.

## Instalacija

```bash
git clone --recurse-submodules https://github.com/MATF-Software-Verification/2026_Analysis_ChatterBot.git
cd 2026_Analysis_ChatterBot

python -m venv .venv
.venv/Scripts/activate        # Windows
source .venv/bin/activate     # Linux, macOS

bash scripts/priprema.sh
```

`scripts/priprema.sh` preuzima submodul, instalira ChatterBot iz njega,
instalira alate iz `requirements.txt` i skida spaCy model. Za ovaj korak je
potreban internet; sve posle njega radi bez mreže.

Ako je folder `ChatterBot/` prazan, repozitorijum je kloniran bez submodula, pa
treba pokrenuti `git submodule update --init --recursive`.

Na Windowsu treba koristiti **Git Bash**, a ne WSL. Ako je `bash` na `PATH`-u
WSL-ov, skripte se pokrenu ali ne vide `python` iz `.venv`. Rešava se sa:

```powershell
$env:PATH = "C:\Program Files\Git\bin;$env:PATH"
```

Putanje se bash-u uvek pišu sa `/`, jer `\` tumači kao znak za nadovezivanje.

## Primeri upotrebe

Analizirana biblioteka se koristi ovako: bot se istrenira listom rečenica u
kojoj je svaka odgovor na prethodnu, pa se onda pita.

```python
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

bot = ChatBot('Primer', database_uri='sqlite:///primer.sqlite3')

ListTrainer(bot).train([
    'Hello',
    'Hi there!',
    'How are you?',
    'I am good.',
])

print(bot.get_response('How are you?'))     # I am good.
```

Iz iste biblioteke se može pozvati i parser datuma, koji je u analizi ispao
najproblematičniji deo:

```python
from chatterbot.parsing import datetime_parsing

datetime_parsing('we met on 3 May 2021')
# [('3 May 2021', datetime.datetime(2021, 5, 3, 0, 0), (10, 20))]

datetime_parsing('end of the week')
# TypeError: unsupported operand type(s) for +: 'int' and 'datetime.timedelta'
```

## Ulazni primeri

Za upotrebu i za testiranje koriste se sledeći ulazi.

**Parovi za trening.** Lista rečenica u kojoj je svaka odgovor na prethodnu, na
primer `['Hello', 'Hi there!']` ili `['What is your name?', 'My name is
ChatterBot.']`. Par `['Good morning', 'Good morning to you too']` je onaj na
kome se vidi nalaz 9.

**Ugrađeni korpus.** `ChatterBotCorpusTrainer` prima imena poput
`chatterbot.corpus.english.greetings`, koja dolaze uz biblioteku.

**Fraze koje obaraju parser datuma.** Svedene na najkraći oblik, ovih pet ulaza
obaraju `datetime_parsing`, i svaki ima svoj test u `tests/property/`:

```
'last month'        u januaru       -> ValueError: month must be in 1..12
'last month'        31. u mesecu    -> ValueError: day is out of range for month
'end of the week'                   -> TypeError: 'int' + 'timedelta'
'end of the monday'                 -> TypeError: 'NoneType' + 'timedelta'
'29 hours'                          -> ValueError: hour must be in 0..23
```

Duže fraze koje je Hypothesis zaista izgenerisao stoje u
`tools/hypothesis/results/kontraprimeri.txt`.

**Tekst od samih stop-reči.** Ulaz `'the'` obara `JaccardSimilarity` deljenjem
nulom.

**Zlonamerna tar arhiva.** Pravi je skripta
`tools/bandit/poc_path_traversal.py`, sa članom `../ubuntu_dialogs_evil/pwned.txt`,
koji izlazi iz dozvoljenog direktorijuma i prolazi kroz zaštitu projekta.

## Alati korišćeni za analizu

| Alat | Šta radi | Pokretanje | Rezultat |
|---|---|---|---|
| flake8 | stil i sitne greške | `bash tools/flake8/run.sh` | 3 prijave |
| mypy | provera tipova bez pokretanja koda | `bash tools/mypy/run.sh` | 46 grešaka |
| bandit | poznati nesigurni obrasci | `bash tools/bandit/run.sh` | 6 nalaza, 1 visokog prioriteta |
| pytest, jedinični testovi | pojedinačne funkcije | `bash tools/unit-tests/run.sh` | 112 testova, svi prolaze |
| pytest, integracioni testovi | prava baza i spaCy model | `bash tools/integration-tests/run.sh` | 18 testova, svi prolaze |
| Hypothesis | sam pravi ulaze i traži kontraprimer | `bash tools/hypothesis/run.sh` | 10 testova, 4 kontraprimera |

Svi odjednom, istim redosledom kao u izveštaju:

```bash
bash scripts/pokreni_sve.sh
```

Izlaz svakog alata se čuva u `tools/<alat>/results/`. Uz jedinične testove se
meri i pokrivenost koda, a taj izveštaj se otvara u pregledaču iz fajla
`tools/unit-tests/results/htmlcov/index.html`.

## Testovi

Testovi su deo repozitorijuma, u folderu `tests/`, i podeljeni su u tri sloja:

| Folder | Šta proverava | Broj |
|---|---|---|
| `tests/unit/` | pojedinačne funkcije, bez baze i mreže, sa lažnim objektima | 112 |
| `tests/integration/` | prava SQLite baza, pravi spaCy model i treneri | 18 |
| `tests/property/` | svojstva koja moraju važiti za svaki ulaz (Hypothesis) | 10 |

Pokreću se skriptama iz tabele iznad, ili direktno preko pytest-a:

```bash
python -m pytest tests/unit -v
python -m pytest tests/integration -v
python -m pytest tests/property -v
python -m pytest                        # sve odjednom, 140 testova
```

Svaki test koji dokazuje neki nalaz ima broj nalaza u imenu, pa se može ciljati
pojedinačno:

```bash
python -m pytest -k bag_6 -v                    # nalaz 6
python -m pytest -k bag_9 -v                    # nalaz 9
python -m pytest -k "bag_1 and not bag_10" -v   # nalaz 1, svih pet uzroka
```

Nalaz 3 nije test nego zasebna skripta, jer dokazuje da se bezbednosna zaštita
može zaobići:

```bash
python tools/bandit/poc_path_traversal.py
```

Skripte koje su korišćene za pokretanje su u repozitorijumu:
`scripts/priprema.sh` za instalaciju, `scripts/pokreni_sve.sh` za sve alate, i
po jedna `run.sh` u svakom folderu unutar `tools/`.

## Nalazi

Pronađeno je deset problema. Ukratko:

1. Parser datuma (`parsing.py`) puca umesto da vrati prazan rezultat, iz pet
   nezavisnih razloga, na primer za `end of the week` ili `last month` u januaru.
2. `JaccardSimilarity` deli nulom kada su oba teksta samo stop-reči.
3. Zaštita od path traversal napada u `trainers.py` može da se zaobiđe, što je
   potvrđeno skriptom `tools/bandit/poc_path_traversal.py`.
4. `LevenshteinDistance` nije simetričan.
5. `SpacySimilarity` je neupotrebljiv sa modelom koji projekat podrazumeva.
6. `created_at` u `conversation.py` je lokalno vreme označeno kao UTC.
7. `get_most_frequent_response` vraća `None` iako u potpisu piše `Statement`.
8. `initialize_class` menja rečnik koji je korisnik prosledio.
9. Bot ume da vrati korisnikov sopstveni ulaz umesto naučenog odgovora.
10. Izvezena baza ne može da se uveze nazad nijednim trenerom.

Za svaki nalaz postoji test koji ga dokazuje i koji pada dok je greška u kodu.
Detaljno objašnjenje, sa uzrocima i predlozima ispravki, nalazi se u
[`ProjectAnalysisReport.pdf`](ProjectAnalysisReport.pdf).

## Struktura repozitorijuma

```
ChatterBot/                 analizirani projekat (git submodul, komit feafc81)
tests/
  unit/                     jedinicni testovi
  integration/              integracioni testovi
  property/                 property-based testovi
tools/                      po jedan folder za svaki alat: run.sh i results/
  flake8/  mypy/  bandit/  unit-tests/  integration-tests/  hypothesis/
scripts/
  priprema.sh               instalira zavisnosti
  pokreni_sve.sh            pokrece svih sest alata
ProjectAnalysisReport.pdf   izvestaj
README.md
```

## Zaključci

Projekat je uredan po pitanju stila, ali ima slabe rubne slučajeve. Najviše
grešaka je u `parsing.py` i `trainers.py`. Ta dva modula nisu bez testova,
`parsing.py` ih u samom projektu ima 53, ali nijedan od njih ne očekuje
izuzetak. Statička i dinamička analiza su se dopunile: dve greške je mypy
prijavio bez pokretanja koda, a Hypothesis ih je nezavisno izazvao stvarnim
ulazom.
