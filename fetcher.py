import re
import subprocess

import bleach
import requests
import grequests
from bs4 import BeautifulSoup


FALLOUT2_BASE_LINK = 'http://ru.fallout.wikia.com'
FALLOUT2_DIALOGUES_LINK = FALLOUT2_BASE_LINK + '/wiki/Диалоговые_файлы_Fallout_2'

fallout2_page = requests.get(FALLOUT2_DIALOGUES_LINK)
parser = BeautifulSoup(fallout2_page.text, 'lxml')
phrases_links = [
    FALLOUT2_BASE_LINK + link['href']
    for link in parser.select('td a')
    if link['href'].lower().endswith('msg')
]
rs = (grequests.get(l) for l in phrases_links)
results = grequests.map(rs)
for result in results:
    with open('./data/fallout2_dirty.txt', 'a+') as fallout2:
        parser = BeautifulSoup(result.text, 'lxml')
        dialogue_entries = parser.select_one('div.va-transcript-text p')
        if dialogue_entries:
            cleaned = bleach.clean(
                dialogue_entries.text, tags=[], attributes={}, styles=[], strip=True
            )
            for line in cleaned.split('\n'):
                try:
                    phrase = re.search(r'\{.*\}\{.*\}\{(?P<phrase>.*)\}', line).group('phrase')
                except AttributeError:
                    pass
                print(phrase, file=fallout2)

subprocess.call("awk '!seen[$0]++' ./data/fallout2_dirty.txt > ./data/fallout2.txt", shell=True)