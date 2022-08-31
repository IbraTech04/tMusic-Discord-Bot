import pylrc
from lyricsgenius import Genius

"""
file = open('Post Malone - Sunflower (Spider-Man_ Into the Spider-Verse).lrc', 'r')
string = ''.join(file.readlines())
file.close

subs = pylrc.parse(string)
times = []
for sub in subs:
    times.append(sub.time)
#find the lyric closest to a given time

print(min(times, key=lambda x:abs(x-100)))

"""
GENUIS_CLIENT_ID = 'Chx7q6AqZyjgCRkmV52NK4zkqO4KiKQF5qaLI4C_UhIs-Zf7HK9_q3yEpVjcwTEz'
GENIUS_SECRET = 'blXkhbM_tgAVin1Cq_nFUljGk2EFvBlG-rWvAutqGHc1w4QwdyZZV9evlrQTaWpPU69L7BUrCKzyOC3xYceEqQ'
GENIUS_TOKEN = 'sorYarHPpZGFsmSPDipAnaPxjicRCAGaX01rmHgGwDME1Fjv-EujD56xlL44T0ap'
genius = Genius(GENIUS_TOKEN)

sp = genius.search('Post Malone - Sunflower')
id = (sp['hits'][0]['result']['api_path'].split('/')[-1])
print(genius.lyrics(id))