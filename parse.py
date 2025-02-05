from bs4 import BeautifulSoup
import urllib.request
import re
from collections import defaultdict
import json
from enum import Enum
import copy

def remove_text_between_parens(text): # lazy: https://stackoverflow.com/questions/37528373/how-to-remove-all-text-between-the-outer-parentheses-in-a-string
    n = 1  # run at least once
    while n:
        text, n = re.subn(r'\([^()]*\)', '', text)  # remove non-nested/flat balanced parts
    return text

abbrevs = {
    "A": "Assamese",
    "al": "Alashai dialect of Pashai",
    "amg": "Ardhamāgadhī Prakrit",
    "Ap": "Apabhraṁśa",
    "Ar": "Arabic",
    "Ār": "Aryan, i.e. Indo-iranian",
    "ar": "Areti dialect of Pashai",
    "Aram": "Aramaic",
    "Arm": "Armenian",
    "arm": "Armenian dialect of Gypsy",
    "as": "Asiatic dialects of Gypsy",
    "Aś": "Aśokan, i.e. the language of the Inscriptions of Aśoka",
    "Ash": "Ashkun (Aṣkū̃ — Kaf.)",
    "Austro-as": "Austro-asiatic",
    "Av": "Avestan (Iranian)",
    "Aw": "Awadhī",
    "awāṇ": "Awāṇkārī dialect of Lahndā",
    "B": "Bengali (Baṅglā)",
    "Bal": "Balūčī (Iranian)",
    "bāṅg": "Bāṅgarū dialect of Western Hindī",
    "Bashg": "Bashgalī (Kaf.)",
    "bh": "Bairāṭ Bhābrū Minor Rock Edict of Aśoka",
    "bhad": "Bhadrawāhī dialect of West Pahāṛī",
    "bhal": "Bhalesī dialect of West Pahāṛī",
    "bhaṭ": "Bhaṭěālī sub-dialect of Ḍogrī dialect of Panjābī",
    "bhiḍ": "Bhiḍlàī sub-dialect of Bhadrawāhī dialect of West Pahāṛī",
    "Bhoj": "Bhojpurī",
    "BHSk": "Buddhist Hybrid Sanskrit",
    "Bi": "Bihārī",
    "bir": "Birir dialect of Kalasha",
    "boh": "Bohemian dialect of European Gypsy",
    "Brah": "Brāhūī (Dravidian)",
    "Brj": "Brajbhāṣā",
    "bro": "Brokpā dialect of Shina",
    "Bshk": "Bashkarīk (Dard.)",
    "bul": "Bulgarian dialect of European Gypsy",
    "Bur": "Burushaski",
    "cam": "Cameāḷī dialect of West Pahāṛī",
    "Chil": "Chilīs (Dard.)",
    "chil": "Chilasi dialect of Shina or of Pashai",
    "cur": "Curāhī dialect of West Pahāṛī",
    "Ḍ": "Ḍumāki",
    "dar": "Darrai-i Nūr dialect of Pashai",
    "Dard": "Dardic",
    "dh": "Dhauli Rock Inscription of Aśoka",
    "Dhp": "Gāndhārī or Northwest Prakrit (as recorded in the Dharmapada ed. J. Brough, Oxford 1962)",
    "Dm": "Dameli (Damε̃ḍīˊ — Kaf.-Dard.)",
    "ḍoḍ": "Ḍoḍī (Sirājī of Ḍoḍā), a dialect of Kashmiri in Jammu",
    "ḍog": "Ḍogrī dialect of Panjābī",
    "dr": "Drās dialect of Shina",
    "Drav": "Dravidian",
    "Eng": "English",
    "eng": "English dialect of European Gypsy",
    "eur": "European (Gypsy)",
    "Fr": "French",
    "G": "Gujarātī",
    "Ga": "Gadba (Dravidian)",
    "Garh": "Gaṛhwālī",
    "Gau": "Gauro (Dard.)",
    "gav": "Gavīmaṭh Inscription of Aśoka",
    "Gaw": "Gawar-Bati (Dard.)",
    "germ": "German dialect of European Gypsy",
    "ghis": "Ghisāḍī dialect of wandering blacksmiths in Gujarat",
    "gil": "Gilgitī dialect of Shina",
    "gir": "Girnār Rock Inscription of Aśoka",
    "Gk": "Greek",
    "Gmb": "Gambīrī (Kaf.)",
    "gng": "Gaṅgoī dialect of Kumaunī",
    "Goth": "Gothic",
    "gr": "Greek dialect of European Gypsy",
    "gul": "Gulbahārī dialect of Pashai",
    "gur": "Gurēsī dialect of Shina",
    "Gy": "Gypsy or Romani",
    "H": "Hindī",
    "hal": "Halabī dialect of Marāṭhī",
    "haz": "Hazara Hindkī dialect of Lahndā",
    "h.rudh": "High Rudhārī sub-dialect of Khaśālī dialect of West Pahāṛī",
    "hung": "Hungarian dialect of European Gypsy",
    "IA": "Indo-aryan",
    "IE": "Indo-european",
    "Ind": "Indo-aryan of India proper excluding Kafiri and Dardic",
    "Indo-ir": "Indo-iranian or Aryan",
    "Ir": "Iranian",
    "ish": "Ishpi dialect of Pashai",
    "Ishk": "Ishkāshmī (Iranian)",
    "isk": "Iskeni dialect of Pashai",
    "it": "Italian dialect of European Gypsy",
    "jau": "Jaugaḍa Rock Inscription of Aśoka",
    "jaun": "Jaunsārī dialect of West Pahāṛī",
    "jij": "Jijelut dialect of Shina",
    "jmag": "Jaina Māgadhī Prakrit",
    "jmh": "Jaina Mahārāṣṭrī Prakrit",
    "jt": "Jāṭū sub-dialect of Bāṅgarū dialect of Western Hindī",
    "jub": "North Jubbal dialect of West Pahāṛī",
    "K": "Kashmiri (Kāśmīrī)",
    "kach": "Kāchṛī dialect of Lahndā",
    "Kaf": "Kafiri",
    "Kal": "Kalasha (Kaláṣa — Dard.)",
    "kāl": "Kālsī Rock Inscription of Aśoka",
    "Kamd": "See Kmd.",
    "Kan": "Kanarese (Kannaḍa — Dravidian)",
    "Kand": "Kandia (Dard.)",
    "kar": "Karači (Transcaucasian) dialect of Asiatic Gypsy",
    "kash": "or kiś. Kashṭawāṛī dialect of Kashmiri",
    "Kaṭ": "Kaṭārqalā (Dard.)",
    "kāṭh": "Kāṭhiyāvāḍi dialect of Gujarātī",
    "kb": "Kauśāmbī Pillar Edict of Aśoka",
    "kc": "Kocī dialect of West Pahāṛī",
    "kcch": "Kacchī dialect of Sindhī",
    "kch": "Kachur-i Sala dialect of Pashai",
    "kgr": "or kng. Kāṅgrā sub-dialect of Ḍogrī dialect of Panjābī",
    "KharI": "MIA. forms occurring in Corpus Inscriptionum Indicarum Vol. II Pt. 1",
    "khas": "Khasa dialect of Kumaunī",
    "khaś": "Khaśālī dialect of West Pahāṛī",
    "khet": "Khetrānī dialect of Lahndā",
    "Kho": "Khowār (Dard.)",
    "Khot": "Khotanese (Iranian)",
    "kiś": "See kash.",
    "kiũth": "Kiũthalī dialect of West Pahāṛī",
    "Kmd": "or Kamd. Kāmdeshi (Kaf.), Kāmdesh dialect of Kati",
    "kṇḍ": "Kaṇḍak dialect of Pashai",
    "kng": "See kgr.",
    "Ko": "Koṅkaṇī",
    "Koh": "Kohistānī (Dard.)",
    "koh": "Kohistānī dialect of Shina",
    "Kol": "Kōlāmī (Dravidian)",
    "kōl": "Kōlā dialect of Shina",
    "kq": "Kauśāmbī (Queen's Edict) Inscription of Aśoka",
    "Kt": "Kati or Katei (Kaf.)",
    "kṭg": "Kotgarhi dialect of West Pahāṛī",
    "Ku": "Kumaunī",
    "Kur": "Kuruḵẖ (Dravidian)",
    "kuṛ": "Kuṛaṅgali dialect of Pashai",
    "Kurd": "Kurdish (Iranian)",
    "kurd": "Kurdari dialect of Pashai",
    "ky": "Kanyawālī dialect of Maiyã̄",
    "L": "Lahndā",
    "la": "Lāṛī dialect of Sindhī",
    "lagh": "Laghmani dialect of Pashai",
    "lakh": "Lakhīmpurī dialect of Awadhī",
    "Lat": "Latin",
    "lauṛ": "Lauṛowānī dialect of Pashai",
    "Lith": "Lithuanian",
    "l.rudh": "Low Rudhārī sub-dialect of Khaśālī dialect of West Pahāṛī",
    "ludh": "Ludhiānī dialect of Panjābī",
    "M": "Marāṭhī",
    "mag": "Magahī dialect of Bihārī",
    "Mai": "Maiyã̄ (Dard.)",
    "Mal": "Malayāḷam (Dravidian)",
    "Māl": "or Malw. Mālwāī",
    "mald": "See Md.",
    "Malw": "See Māl.",
    "man": "Mānsehrā Rock Inscription of Aśoka",
    "marm": "Marmatī sub-dialect of Khaśālī dialect of West Pahāṛī",
    "Marw": "Mārwāṛī",
    "Md": "or mald. Maldivian dialect of Sinhalese",
    "mg": "Māgadhī Prakrit",
    "mh": "Mahārāsṭrī Prakrit",
    "MIA": "Middle Indo-aryan",
    "mi": "Delhi Mīrat Pillar Edict of Aśoka",
    "mid.rudh": "Middle Rudhārī sub-dialect of Khaśālī dialect of West Pahāṛī",
    "Mj": "Munǰī (Iranian)",
    "Mth": "Maithilī",
    "mth": "Mathiā (Lauṛiyā-Nandangaṛh) Inscription of Aśoka",
    "Mu": "Muṇḍā",
    "mult": "Multānī dialect of Lahndā",
    "N": "Nepāli",
    "New": "Newārī",
    "ng": "Nāgārjunī Cave Inscription of Aśoka",
    "NIA": "New (modern) Indo-aryan",
    "NiDoc": "Language of `Kharoṣṭhī Inscriptions discovered by Sir Aurel Stein in Chinese Turkestan' edited by A. M. Boyer, E. J. Rapson, and E. Senart",
    "nig": "Niglīvā Inscription of Aśoka",
    "nij": "Nijelami (Neẓəlāˊm) dialect of Pashai",
    "Niṅg": "Niṅgalāmī (Dard.)",
    "nir": "Nirlāmī dialect of Pashai",
    "Nk": "Naiki (Dravidian)",
    "norw": "Norwegian dialect of European Gypsy",
    "OHG": "Old High German",
    "OPruss": "Old Prussian",
    "Or": "Oṛiyā",
    "Orm": "Ōrmuṛīˊ (Iranian)",
    "OSlav": "Old Slavonic",
    "Oss": "Ossetic (Iranian)",
    "P": "Panjābī (Pañjābī)",
    "Pa": "Pali",
    "pach": "See pch.",
    "pāḍ": "Pāḍarī sub-dialect of Bhadrawāhī dialect of West Pahāṛī",
    "Pah": "Pahāṛī",
    "Pahl": "Pahlavi (Iranian)",
    "paiś": "Paiśācī Prakrit",
    "pal": "Palestinian dialect of Asiatic Gypsy of the Nawar",
    "pales": "Palesī dialect of Shina",
    "paṅ": "Paṅgwāḷī dialect of West Pahāṛī",
    "Par": "Parachi (Parāčī — Iranian)",
    "Parth": "Parthian (Iranian)",
    "Paš": "Pashai (Pašaī — Dard.)",
    "paṭ": "Paṭṭanī dialect of Gujarātī",
    "pch": "or pach. Pachaghani dialect of Pashai",
    "Pers": "Persian (Iranian)",
    "pers": "Persian dialect of Asiatic Gypsy",
    "Phal": "Phalūṛa (Dard.)",
    "Pk": "Prakrit",
    "pog": "Pǒgulī dialect of Kashmiri",
    "pol": "Polish dialect of European Gypsy",
    "poṭh": "Poṭhwārī dialect of Lahndā",
    "pow": "Pōwādhī dialect of Panjābī",
    "Pr": "Prasun (Kaf.)",
    "Prj": "Parji (Dravidian)",
    "Psht": "Pashto (Iranian)",
    "pun": "Punchī dialect of Lahndā",
    "punl": "Puniali dialect of Shina",
    "rām": "Rāmbanī dialect of Kashmiri in Jammu",
    "rdh": "Radhia (Lauṛiyā Ararāj) Pillar Edict of Aśoka",
    "Rj": "Rājasthānī",
    "roḍ": "Roḍiyā dialect of Sinhalese",
    "roh": "Rohruī dialect of West Pahāṛī",
    "rp": "Rāmpurvā Rock Edict of Aśoka",
    "ru": "Rūpnāth Inscription of Aśoka",
    "rudh": "Rudhārī sub-dialect of Khaśālī dialect of West Pahāṛī",
    "rum": "Rumanian dialect of European Gypsy",
    "rumb": "Rumbūr dialect of Kalasha",
    "rus": "Russian dialect of European Gypsy",
    "Russ": "Russian",
    "S": "Sindhī",
    "ś": "Śaurasenī Prakrit",
    "sah": "Sahasrām Inscription of Aśoka",
    "Sang": "Sanglechi (Saṅlēčī — Iranian)",
    "Sant": "Santālī (Muṇḍā)",
    "Sar": "Sarīkolī (Iranian)",
    "SEeur": "South-east European dialects of Gypsy",
    "śeu": "Śeuṭī sub-dialect of Khaśālī dialect of West Pahāṛī",
    "Sh": "Shina (Ṣiṇā — Dard.)",
    "shah": "Shāhbāzgaṛhī Rock Inscription of Aśoka",
    "sham": "Shamakaṭ dialect of Pashai",
    "she": "Shewa dialect of Pashai",
    "Shgh": "Shughnī (Iranian)",
    "Shum": "Shumashti (Šumāštī — Dard.)",
    "shut": "Shutuli dialect of Pashai",
    "Si": "Sinhalese",
    "Sik": "Sikalgārī (Mixed Gypsy Language: LSI xi 167)",
    "sir": "Sirājī dialect of West Pahāṛī",
    "sirm": "Sirmaurī dialect of West Pahāṛī",
    "Sk": "Sanskrit",
    "sn": "Sārnāth Inscription of Aśoka",
    "snj": "Sanjan dialect of Pashai",
    "sod": "Sǒdōcī dialect of West Pahāṛī",
    "Sogd": "Sogdian (Iranian)",
    "sop": "Bombay-Sopārā Inscription of Aśoka",
    "sp": "Spanish dialect of European Gypsy",
    "srk": "Sirāikī dialect of Sindhī",
    "suk": "Suketī dialect of West Pahāṛī",
    "Sv": "Savi (Dard.)",
    "Tam": "Tamil (Dravidian)",
    "Tel": "Telugu (Dravidian)",
    "Tib": "Tibetan",
    "Tir": "Tirāhī (Dard.)",
    "Toch": "Tocharian",
    "top": "Delhi-Tōprā Pillar Edict of Aśoka",
    "Tor": "Tōrwālī (Dard.)",
    "Tu": "Tuḷu (Dravidian)",
    "Turk": "Turkish",
    "urt": "Urtsun dialect of Kalasha",
    "uzb": "Uzbini dialect of Pashai",
    "vrāc": "Vrācaḍa Apabhraṁśa",
    "waz": "Waziri dialect of Pashto",
    "weg": "Wegali dialect of Pashai",
    "wel": "Welsh dialect of European Gypsy",
    "Werch": "Werchikwār or Wershikwār (Yasin dialect of Burushaski)",
    "Wg": "Waigalī or Wai-alā (Kaf.)",
    "Wkh": "Wakhi (Iranian)",
    "Woṭ": "Woṭapūrī (language of Woṭapūr and Kaṭārqalā — Dard.)",
    "WPah": "West Pahāṛī",
    "Yazgh": "Yazghulami (Iranian)",
    "Yghn": "Yaghnobi (Iranian)",
    "Yid": "Yidgha (Iranian)",
    "OA": "Old Assamese",
    "OP": "Old Punjabi",
    "OH": "Old Hindi",
    "OMarw": "Old Marwari",
    "OB": "Old Bengali",
    "OG": "Old Gujarati",
    "OSi": "Old Sinhala",
    "OM": "Old Marathi",
    "OK": "Old Kashmiri",
    "OMth": "Old Maithili",
    "OOr": "Old Oriya",
    "OAw": "Old Awadhi"
}

reflexes = defaultdict(list)

regex = r'(?<=[\W\.])(' + f'{"|".join(list(abbrevs.keys()))}' + r')\.'


# this is such a big brain regex

total_pages = 836
with open("dasa_list.txt", "a") as fout:
    for page in range(1, total_pages + 1):
        print(page)
        link = "https://dsal.uchicago.edu/cgi-bin/app/soas_query.py?page=" + str(page)
        with urllib.request.urlopen(link) as resp:
            soup = BeautifulSoup(resp, 'html.parser')
            soup = str(soup).split('<number>')
            for entry in soup:
                entry = BeautifulSoup('<number>' + entry)
                if entry.find('b'):
                    lemma = entry.find('b').text
                    number = entry.find('number').text
                    data = str(entry).replace('\n', '').split('<br/>')

                    reflexes[number].append({'lang': 'Indo-Aryan', 'words': [lemma], 'ref': data[0]})
                    if (len(data) == 1): continue

                    langs = []
                    data[1] = ', '.join(data[1:])
                    data[1] = remove_text_between_parens(data[1])
                    matches = list(re.finditer(regex, data[1]))
                    for i in range(len(matches)):
                        lang = matches[i].group(1)
                        lang_entry = {'lang': lang, 'words': []}
                        word = None
                        if i == len(matches) - 1:
                            word = data[1][matches[i].start():]
                        else:
                            word = data[1][matches[i].start():matches[i + 1].start()]
                        
                        word = word.replace('ˊ', '́')
                        word = word.replace(' -- ', '–')
                        word = word.replace('--', '–')
                        
                        forms = list(re.finditer(r'(<i>(.*?)</i>|ʻ(.*?)ʼ)', word))
                        if lang == 'kcch':
                            if langs:
                                if langs[-1] == 'S':
                                    langs.pop()

                        langs.append(lang)
                        if len(forms) == 0:
                            continue

                        cur = None
                        defs = []
                        for i in forms:
                            if i.group(0).startswith('<i>'):
                                if cur:
                                    for each in cur.split(','):
                                        definition = '; '.join(defs) if defs != [] else ''
                                        lang_entry['words'].append([each.strip(), definition])
                                defs = []
                                cur = i.group(2)
                            else:
                                defs.append(i.group(3).strip())
                        if cur:
                            for each in cur.split(','):
                                definition = '; '.join(defs) if defs != [] else ''
                                lang_entry['words'].append([each.strip(), definition])

                        for l in langs:
                            lang_entry['lang'] = l
                            reflexes[number].append(copy.deepcopy(lang_entry))
                        langs = []

with open(f'data/all.json', 'w') as fout:
    json.dump(reflexes, fout, indent=2)