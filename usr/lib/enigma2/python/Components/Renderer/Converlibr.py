#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from re import sub, S, I, search
from six import text_type
import sys
from unicodedata import normalize

PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    import html
    html_parser = html
    from urllib.parse import quote_plus
else:
    from urllib import quote_plus
    from HTMLParser import HTMLParser
    html_parser = HTMLParser()


def quoteEventName(eventName):
    try:
        text = eventName.decode('utf8').replace(u'\x86', u'').replace(u'\x87', u'').encode('utf8')
    except:
        text = eventName
    return quote_plus(text, safe="+")


REGEX = re.compile(
    r'[\(\[].*?[\)\]]|'                    # Parentesi tonde o quadre
    r':?\s?odc\.\d+|'                      # odc. con o senza numero prima
    r'\d+\s?:?\s?odc\.\d+|'                # numero con odc.
    r'[:!]|'                               # due punti o punto esclamativo
    r'\s-\s.*|'                            # trattino con testo successivo
    r',|'                                  # virgola
    r'/.*|'                                # tutto dopo uno slash
    r'\|\s?\d+\+|'                         # | seguito da numero e +
    r'\d+\+|'                              # numero seguito da +
    r'\s\*\d{4}\Z|'                        # * seguito da un anno a 4 cifre
    r'[\(\[\|].*?[\)\]\|]|'                # Parentesi tonde, quadre o pipe
    r'(?:\"[\.|\,]?\s.*|\"|'               # Testo tra virgolette
    r'\.\s.+)|'                            # Punto seguito da testo
    r'Премьера\.\s|'                       # Specifico per il russo
    r'[хмтдХМТД]/[фс]\s|'                  # Pattern per il russo con /ф o /с
    r'\s[сС](?:езон|ерия|-н|-я)\s.*|'      # Stagione o episodio in russo
    r'\s\d{1,3}\s[чсЧС]\.?\s.*|'           # numero di parte/episodio in russo
    r'\.\s\d{1,3}\s[чсЧС]\.?\s.*|'         # numero di parte/episodio in russo con punto
    r'\s[чсЧС]\.?\s\d{1,3}.*|'             # Parte/Episodio in russo
    r'\d{1,3}-(?:я|й)\s?с-н.*',            # Finale con numero e suffisso russo
    re.DOTALL)


'''
def remove_accents(string):
    if not isinstance(string, text_type):
        string = text_type(string, 'utf-8')
    string = sub(u"[àáâãäå]", 'a', string)
    string = sub(u"[èéêë]", 'e', string)
    string = sub(u"[ìíîï]", 'i', string)
    string = sub(u"[òóôõö]", 'o', string)
    string = sub(u"[ùúûü]", 'u', string)
    string = sub(u"[ýÿ]", 'y', string)
    return string
'''


def remove_accents(string):
    # Normalizza la stringa in forma NFD (separa i caratteri dai loro segni diacritici)
    normalized = normalize('NFD', string)
    # Rimuove tutti i segni diacritici utilizzando una regex
    without_accents = sub(r'[\u0300-\u036f]', '', normalized)
    return without_accents


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, text_type):
        s = text_type(s, encoding)
    if norm:
        s = normalize(norm, s)
    return s


def str_encode(text, encoding="utf8"):
    if not PY3:
        if isinstance(text, text_type):
            return text.encode(encoding)
    return text


def cutName(eventName=""):
    if eventName:
        eventName = eventName.replace('"', '').replace('Х/Ф', '').replace('М/Ф', '').replace('Х/ф', '')  # .replace('.', '').replace(' | ', '')
        eventName = eventName.replace('(18+)', '').replace('18+', '').replace('(16+)', '').replace('16+', '').replace('(12+)', '')
        eventName = eventName.replace('12+', '').replace('(7+)', '').replace('7+', '').replace('(6+)', '').replace('6+', '')
        eventName = eventName.replace('(0+)', '').replace('0+', '').replace('+', '')
        eventName = eventName.replace('المسلسل العربي', '')
        eventName = eventName.replace('مسلسل', '')
        eventName = eventName.replace('برنامج', '')
        eventName = eventName.replace('فيلم وثائقى', '')
        eventName = eventName.replace('حفل', '')
        return eventName
    return ""


def getCleanTitle(eventitle=""):
    # save_name = sub('\\(\d+\)$', '', eventitle)
    # save_name = sub('\\(\d+\/\d+\)$', '', save_name)  # remove episode-number " (xx/xx)" at the end
    # # save_name = sub('\ |\?|\.|\,|\!|\/|\;|\:|\@|\&|\'|\-|\"|\%|\(|\)|\[|\]\#|\+', '', save_name)
    save_name = eventitle.replace(' ^`^s', '').replace(' ^`^y', '')
    return save_name


def sanitize_filename(filename):
    # Replace spaces with underscores and remove invalid characters (like ':')
    sanitized = sub(r'[^\w\s-]', '', filename)  # Remove invalid characters
    # sanitized = sanitized.replace(' ', '_')      # Replace spaces with underscores
    # sanitized = sanitized.replace('-', '_')      # Replace dashes with underscores
    return sanitized.strip()


def convtext(text=''):
    try:
        if text is None:
            print('return None original text:', type(text))
            return  # Esci dalla funzione se text è None
        if text == '':
            print('text is an empty string')
        else:
            # print('original text:', text)
            # Converti tutto in minuscolo
            text = text.lower()
            # print('lowercased text:', text)
            # Rimuovi accenti
            text = remove_accents(text)
            # print('remove_accents text:', text)

            text = text.lstrip()

            # remove episode number from series, like "series"
            regex = re.compile(r'^(.*?)([ ._-]*(ep|episodio|st|stag|odc|parte|pt!series|serie||s[0-9]{1,2}e[0-9]{1,2}|[0-9]{1,2}x[0-9]{1,2})[ ._-]*[.]?[ ._-]*[0-9]+.*)$')
            text = sub(regex, r'\1', text).strip()
            print("titolo_pulito:", text)
            # Force and remove episode number from series, like "series"
            if search(r'[Ss][0-9]+[Ee][0-9]+', text):
                text = sub(r'[Ss][0-9]+[Ee][0-9]+.*[a-zA-Z0-9_]+', '', text, flags=S | I)
            text = sub(r'\(.*\)', '', text).rstrip()  # remove episode number from series, like "series"
            

            # Mappatura sostituzioni con azione specifica
            sostituzioni = [
                ('superman & lois', 'superman e lois', 'set'),
                ('lois & clark', 'superman e lois', 'set'),

                ('1/2', 'mezzo', 'replace'),
                ('tg1', 'tguno', 'replace'),
                ('c.s.i.', 'csi', 'replace'),
                ('c.s.i:', 'csi', 'replace'),
                ('ncis:', 'ncis', 'replace'),
                ('ritorno al futuro:', 'ritorno al futuro', 'replace'),

                ('lingo: parole', 'lingo', 'set'),
                ('heartland', 'heartland', 'set'),
                ('io & marilyn', 'io e marilyn', 'set'),
                ('giochi olimpici parigi', 'olimpiadi di parigi', 'set'),
                ('bruno barbieri', 'brunobarbierix', 'set'),
                ("anni '60", 'anni 60', 'set'),
                ('cortesie per gli ospiti', 'cortesieospiti', 'set'),
                ('tg regione', 'tg3', 'set'),

                ('planet earth', 'planet earth', 'set'),
                ('studio aperto', 'studio aperto', 'set'),
                ('josephine ange gardien', 'josephine ange gardien', 'set'),
                ('josephine angelo', 'josephine ange gardien', 'set'),
                ('elementary', 'elementary', 'set'),
                ('squadra speciale cobra 11', 'squadra speciale cobra 11', 'set'),
                ('criminal minds', 'criminal minds', 'set'),
                ('i delitti del barlume', 'i delitti del barlume', 'set'),
                ('senza traccia', 'senza traccia', 'set'),
                ('hudson e rex', 'hudson e rex', 'set'),
                ('ben-hur', 'ben-hur', 'set'),
                ('alessandro borghese - 4 ristoranti', 'alessandroborgheseristoranti', 'set'),
                ('alessandro borghese: 4 ristoranti', 'alessandroborgheseristoranti', 'set'),
                ('amici di maria', 'amicimaria', 'set'),


                ('csi miami', 'csi miami', 'set'),
                ('csi: miami', 'csi miami', 'set'),
                ('csi: scena del crimine', 'csi scena del crimine', 'set'),
                ('csi: new york', 'csi new york', 'set'),
                ('csi: vegas', 'csi vegas', 'set'),
                ('csi: cyber', 'csi cyber', 'set'),
                ('csi: immortality', 'csi immortality', 'set'),
                ('csi: crime scene talks', 'csi crime scene talks', 'set'),

                ('ncis unità anticrimine', 'ncis unità anticrimine', 'set'),
                ('ncis unita anticrimine', 'ncis unita anticrimine', 'set'),
                ('ncis new orleans', 'ncis new orleans', 'set'),
                ('ncis los angeles', 'ncis los angeles', 'set'),
                ('ncis origins', 'ncis origins', 'set'),
                ('ncis hawai', 'ncis hawai', 'set'),
                ('ncis sydney', 'ncis sydney', 'set'),

                ('ritorno al futuro - parte iii', 'ritornoalfuturoparteiii', 'set'),
                ('ritorno al futuro - parte ii', 'ritornoalfuturoparteii', 'set'),
                ('walker, texas ranger', 'walker texas ranger', 'set'),
                ('e.r.', 'ermediciinprimalinea', 'set'),
                ('alexa: vita da detective', 'alexa vita da detective', 'set'),
                ('delitti in paradiso', 'delitti in paradiso', 'set'),
                ('modern family', 'modern family', 'set'),
                ('shaun: vita da pecora', 'shaun', 'set'),
                ('calimero', 'calimero', 'set'),
                ('i puffi', 'i puffi', 'set'),
                ('stuart little', 'stuart little', 'set'),
                ('gf daily', 'grande fratello', 'set'),
                ('grande fratello', 'grande fratello', 'set'),
                ('castle', 'castle', 'set'),
                ('seal team', 'seal team', 'set'),
                ('fast forward', 'fast forward', 'set'),
                ('un posto al sole', 'un posto al sole', 'set'),
            ]

            # Applicazione delle sostituzioni
            for parola, sostituto, metodo in sostituzioni:
                if parola in text:
                    if metodo == 'set':
                        text = sostituto
                        break
                    elif metodo == 'replace':
                        text = text.replace(parola, sostituto)

            # Applica le funzioni di taglio e pulizia del titolo
            text = cutName(text)
            text = getCleanTitle(text)

            # Regola il titolo se finisce con "the"
            if text.endswith("the"):
                text = "the " + text[:-4]

            # Sostituisci caratteri speciali con stringhe vuote
            text = text.replace("\xe2\x80\x93", "").replace('\xc2\x86', '').replace('\xc2\x87', '').replace('webhdtv', '')
            text = text.replace('1080i', '').replace('dvdr5', '').replace('((', '(').replace('))', ')') .replace('hdtvrip', '')
            text = text.replace('german', '').replace('english', '').replace('ws', '').replace('ituneshd', '').replace('hdtv', '')
            text = text.replace('dvdrip', '').replace('unrated', '').replace('retail', '').replace('web-dl', '').replace('divx', '')
            text = text.replace('bdrip', '').replace('uncut', '').replace('avc', '').replace('ac3d', '').replace('ts', '')
            text = text.replace('ac3md', '').replace('ac3', '').replace('webhdtvrip', '').replace('xvid', '').replace('bluray', '')
            text = text.replace('complete', '').replace('internal', '').replace('dtsd', '').replace('h264', '').replace('dvdscr', '')
            text = text.replace('dubbed', '').replace('line.dubbed', '').replace('dd51', '').replace('dvdr9', '').replace('sync', '')
            text = text.replace('webhdrip', '').replace('webrip', '').replace('repack', '').replace('dts', '').replace('webhd', '')

            text = text.replace('1^tv', '').replace('1^ tv', '').replace(' - prima tv', '').replace(' - primatv', '')
            text = text.replace('primatv', '').replace('en direct:', '').replace('first screening', '').replace('live:', '')
            text = text.replace('1^ visione rai', '').replace('1^ visione', '').replace('premiere:', '').replace('nouveau:', '')
            text = text.replace('prima visione', '').replace('film -', '').replace('en vivo:', '').replace('nueva emisión:', '')
            text = text.replace('new:', '').replace('film:', '').replace('première diffusion', '').replace('estreno:', '')

            print('cutlist:', text)
            # Rimozione pattern specifici
            text = sub(r'^\w{2}:', '', text)  # Rimuove "xx:" all'inizio
            text = sub(r'^\w{2}\|\w{2}\s', '', text)  # Rimuove "xx|xx" all'inizio
            text = sub(r'^.{2}\+? ?- ?', '', text)  # Rimuove "xx -" all'inizio
            text = sub(r'^\|\|.*?\|\|', '', text)  # Rimuove contenuti tra "||"
            text = sub(r'^\|.*?\|', '', text)  # Rimuove contenuti tra "|"
            text = sub(r'\|.*?\|', '', text)  # Rimuove qualsiasi altro contenuto tra "|"
            text = sub(r'\(\(.*?\)\)|\(.*?\)', '', text)  # Rimuove contenuti tra "()"
            text = sub(r'\[\[.*?\]\]|\[.*?\]', '', text)  # Rimuove contenuti tra "[]"
            
            text = sub(r'[^\w\s]+$', '', text)

            text = sub(r' +ح| +ج| +م', '', text)  # Rimuove numeri di episodi/serie in arabo
            # Rimozione di stringhe non valide
            bad_strings = [
                "ae|", "al|", "ar|", "at|", "ba|", "be|", "bg|", "br|", "cg|", "ch|", "cz|", "da|", "de|", "dk|",
                "ee|", "en|", "es|", "eu|", "ex-yu|", "fi|", "fr|", "gr|", "hr|", "hu|", "in|", "ir|", "it|", "lt|",
                "mk|", "mx|", "nl|", "no|", "pl|", "pt|", "ro|", "rs|", "ru|", "se|", "si|", "sk|", "sp|", "tr|",
                "uk|", "us|", "yu|",
                "1080p", "4k", "720p", "hdrip", "hindi", "imdb", "vod", "x264"
            ]

            bad_strings.extend(map(str, range(1900, 2030)))  # Anni da 1900 a 2030
            bad_strings_pattern = re.compile('|'.join(map(re.escape, bad_strings)))
            text = bad_strings_pattern.sub('', text)
            # Rimozione suffissi non validi
            bad_suffix = [
                " al", " ar", " ba", " da", " de", " en", " es", " eu", " ex-yu", " fi", " fr", " gr", " hr", " mk",
                " nl", " no", " pl", " pt", " ro", " rs", " ru", " si", " swe", " sw", " tr", " uk", " yu"
            ]
            bad_suffix_pattern = re.compile(r'(' + '|'.join(map(re.escape, bad_suffix)) + r')$')
            text = bad_suffix_pattern.sub('', text)
            # Rimuovi "." "_" "'" e sostituiscili con spazi
            text = sub(r'[._\']', ' ', text)
            # Rimuove tutto dopo i ":" (incluso ":")
            text = sub(r':.*$', '', text)
            # Pulizia finale
            text = text.partition("(")[0]  # Rimuove contenuti dopo "("
            # text = text.partition(":")[0]
            # text = text + 'FIN'
            # text = sub(r'(odc.\s\d+)+.*?FIN', '', text)
            # text = sub(r'(odc.\d+)+.*?FIN', '', text)
            # text = sub(r'(\d+)+.*?FIN', '', text)
            # text = sub('FIN', '', text)
            # # remove episode number in arabic series
            # text = sub(r' +ح', '', text)
            # # remove season number in arabic series
            # text = sub(r' +ج', '', text)
            # # remove season number in arabic series
            # text = sub(r' +م', '', text)
            text = text.partition(" -")[0]  # Rimuove contenuti dopo "-"
            text = text.strip(' -')
            # Forzature finali
            text = text.replace('XXXXXX', '60')
            text = text.replace('amicimaria', 'amici di maria')
            text = text.replace('alessandroborgheseristoranti', 'alessandro borghese - 4 ristoranti')
            text = text.replace('brunobarbierix', 'bruno barbieri - 4 hotel')
            text = text.replace('il ritorno di colombo', 'colombo')
            text = text.replace('cortesieospiti', 'cortesie per gli ospiti')
            text = text.replace('ermediciinprimalinea', 'er medici in prima linea')
            text = text.replace('ritornoalfuturoparteiii', 'ritorno al futuro parte iii')
            text = text.replace('ritornoalfuturoparteii', 'ritorno al futuro parte ii')
            text = text.replace('tguno', 'tg1')
            # text = quote(text, safe="")
            # text = unquote(text)
            print('text safe:', text)

        return text.capitalize()
    except Exception as e:
        print('convtext error:', e)
        return None
