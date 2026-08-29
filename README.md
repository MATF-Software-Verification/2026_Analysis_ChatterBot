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
| pytest, jedinični testovi + coverage.py | `bash tools/unit-tests/run.sh` | 112 prolazi, pokrivenost 30% |
| pytest, integracioni testovi | `bash tools/integration-tests/run.sh` | 18 prolazi, pokrivenost 47% |
| Hypothesis, property-based testovi | `bash tools/hypothesis/run.sh` | 10 prolazi, 5 uzroka pada parsera |
| flake8 | `bash tools/flake8/run.sh` | 3 prijave, 87 sa strožom granicom |
| mypy | `bash tools/mypy/run.sh` | 46 grešaka |
| bandit | `bash tools/bandit/run.sh` | 6 nalaza, 1 visokog prioriteta |

Izlaz svakog alata se čuva u `tools/<alat>/results/`. Ukupna pokrivenost svih
140 testova je 53% (`pytest tests --cov=ChatterBot/chatterbot`).

Alati koje nismo radili na vežbama su Hypothesis, mypy i bandit. Alat za
proveru stila je samo jedan, a coverage.py se ne broji kao zaseban alat.

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
se u [`ProjectAnalysisReport.pdf`](ProjectAnalysisReport.pdf). LaTeX izvor tog
dokumenta je u folderu `latex/`, a ponovo se prevodi sa `bash latex/prevedi.sh`.

## Zaključci

Projekat je uredan po pitanju stila, ali ima slabe rubne slučajeve. Najviše
grešaka sam našao u modulima koji nisu imali testove, `parsing.py` i
`trainers.py`. Statička i dinamička analiza su se dopunile: dve greške je mypy
prijavio bez pokretanja koda, a Hypothesis ih je nezavisno izazvao stvarnim
ulazom. Bezbednosni nalaz pokazuje da se prijava alata ne sme odbaciti samo
zato što zaštita postoji, jer je baš ta zaštita bila probojna.
