# Analiza projekta ChatterBot

Seminarski rad iz predmeta Verifikacija softvera, Matematički fakultet.

Autor: Bogdan Tomić, 1040/2025

## Analizirani projekat

[ChatterBot](https://github.com/gunthercox/ChatterBot), grana `master`, komit
[`feafc81`](https://github.com/gunthercox/ChatterBot/commit/feafc81a00be8b8bb65622e4ddc89ebf7b3e1329)
(verzija 1.2.13). To je Python biblioteka za pravljenje chat botova koja pamti
rečenice u bazi i na novo pitanje vraća odgovor zapisan uz najsličniju
zapamćenu rečenicu.

Projekat je uključen kao git submodul u folderu `ChatterBot/` i njegov kod nije
menjan.

## Pokretanje

```bash
git clone --recurse-submodules <url>
cd 2026_Analysis_ChatterBot

python -m venv .venv
.venv/Scripts/activate        # Windows
source .venv/bin/activate     # Linux, macOS

bash scripts/priprema.sh
bash scripts/pokreni_sve.sh
```

Sve skripte se pokreću iz korena repozitorijuma, sa aktiviranim `.venv`.

## Alati

| Alat | Pokretanje | Rezultat |
|---|---|---|
| flake8 | `bash tools/flake8/run.sh` | 3 prijave |
| mypy | `bash tools/mypy/run.sh` | 46 grešaka |
| bandit | `bash tools/bandit/run.sh` | 6 nalaza, 1 visokog prioriteta |
| pytest, jedinični testovi | `bash tools/unit-tests/run.sh` | 112 testova, svi prolaze |
| pytest, integracioni testovi | `bash tools/integration-tests/run.sh` | 18 testova, svi prolaze |
| Hypothesis, property-based testovi | `bash tools/hypothesis/run.sh` | 10 testova, 4 kontraprimera za parser |

Izlaz svakog alata se čuva u `tools/<alat>/results/`. Uz testove se meri i
pokrivenost koda, a izveštaj se otvara u pregledaču iz fajla
`tools/unit-tests/results/htmlcov/index.html`.

## Nalazi

Pronašao sam deset problema. Ukratko:

1. Parser datuma (`parsing.py`) puca umesto da vrati prazan rezultat, iz pet
   nezavisnih razloga, na primer za `"end of the week"` ili `"last month"` u
   januaru.
2. `JaccardSimilarity` deli nulom kada su oba teksta samo stop-reči.
3. Zaštita od path traversal napada u `trainers.py` može da se zaobiđe, što
   sam potvrdio skriptom `tools/bandit/poc_path_traversal.py`.
4. `LevenshteinDistance` nije simetričan.
5. `SpacySimilarity` je neupotrebljiv sa modelom koji projekat podrazumeva.
6. `created_at` u `conversation.py` je lokalno vreme označeno kao UTC.
7. `get_most_frequent_response` vraća `None` iako u potpisu piše `Statement`.
8. `initialize_class` menja rečnik koji je korisnik prosledio.
9. Bot ume da vrati korisnikov sopstveni ulaz umesto naučenog odgovora.
10. Izvezena baza ne može da se uveze nazad nijednim trenerom.

Detaljno objašnjenje svakog nalaza, sa uzrocima i predlozima ispravki, nalazi
se u [`ProjectAnalysisReport.pdf`](ProjectAnalysisReport.pdf).

## Zaključci

Projekat je uredan po pitanju stila, ali ima slabe rubne slučajeve. Najviše
grešaka je u `parsing.py` i `trainers.py`. Ta dva modula nisu bez testova,
`parsing.py` ih u samom projektu ima 53, ali nijedan od njih ne očekuje
izuzetak. Statička i dinamička analiza su se dopunile: dve greške je mypy
prijavio bez pokretanja koda, a Hypothesis ih je nezavisno izazvao stvarnim
ulazom.
