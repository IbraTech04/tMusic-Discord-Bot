import requests

cookies = {
    '__Host-device_id': 'AQA0brwPIaZ6XIBUTOMDJHzjALh1B2OxraZAsZiUmwqyreLFP7frBI5A7I1z_aI4U--KigFWfbOssoTAY94MO040ZRFxC88FQY0',
    'sp_t': '923f5a846f86db930c6c577f49ad53f4',
    'OptanonAlertBoxClosed': '2022-04-29T19:19:53.645Z',
    'sp_m': 'ca-en',
    'spot': '%7B%22t%22%3A1656651155%2C%22m%22%3A%22ca-en%22%2C%22p%22%3Anull%7D',
    'sp_last_utm': '%7B%22utm_campaign%22%3A%22upgrade%22%2C%22utm_medium%22%3A%22desktop%22%2C%22utm_source%22%3A%22app%22%7D',
    'sp_landing': 'https%3A%2F%2Fwww.spotify.com%2Fca-en%2F',
    'sp_usid': '2e48e96b-431d-4819-82ea-a7e81ec1998f',
    '__HOST-sp_fid': '69572ecc-1189-45a4-ad74-d0893811ee59',
    'sp_tr': 'true',
    '__Secure-TPASESSION': 'AQAzZuPe2PHD2be8n0dDfu+ApMfHz7B1YDeO2vfT1vLcTuUlWxdcam/2pLwb93JTvpmQruLiFaAKEFi1O5Fxogyml+TjAtR+PRk=',
    'remember': 'Chehab.ibrahim%40outlook.com',
    'sp_sso_csrf_token': '013acda71974bb0a56dec1b7da5ce9786b086418c531363637363631383438383732',
    'OptanonConsent': 'geolocation=CA%3BON&datestamp=Sat+Nov+05+2022+11%3A25%3A57+GMT-0400+(Eastern+Daylight+Time)&version=6.26.0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=s00%3A1%2Cf00%3A1%2Cm00%3A1%2Ct00%3A1%2Ci00%3A1%2Cf02%3A1%2Cm02%3A1%2Ct02%3A1&AwaitingReconsent=false',
    '__Host-sp_csrf_sid': '58a4029310e3b543769a0ed2c376e7ec36b9bef44cce330c50728b5205d3f67b',
}

headers = {
    'authority': 'accounts.spotify.com',
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    # Requests sorts cookies= alphabetically
    # 'cookie': '__Host-device_id=AQA0brwPIaZ6XIBUTOMDJHzjALh1B2OxraZAsZiUmwqyreLFP7frBI5A7I1z_aI4U--KigFWfbOssoTAY94MO040ZRFxC88FQY0; sp_t=923f5a846f86db930c6c577f49ad53f4; OptanonAlertBoxClosed=2022-04-29T19:19:53.645Z; sp_m=ca-en; spot=%7B%22t%22%3A1656651155%2C%22m%22%3A%22ca-en%22%2C%22p%22%3Anull%7D; sp_last_utm=%7B%22utm_campaign%22%3A%22upgrade%22%2C%22utm_medium%22%3A%22desktop%22%2C%22utm_source%22%3A%22app%22%7D; sp_landing=https%3A%2F%2Fwww.spotify.com%2Fca-en%2F; sp_usid=2e48e96b-431d-4819-82ea-a7e81ec1998f; __HOST-sp_fid=69572ecc-1189-45a4-ad74-d0893811ee59; sp_tr=true; __Secure-TPASESSION=AQAzZuPe2PHD2be8n0dDfu+ApMfHz7B1YDeO2vfT1vLcTuUlWxdcam/2pLwb93JTvpmQruLiFaAKEFi1O5Fxogyml+TjAtR+PRk=; remember=Chehab.ibrahim%40outlook.com; sp_sso_csrf_token=013acda71974bb0a56dec1b7da5ce9786b086418c531363637363631383438383732; OptanonConsent=geolocation=CA%3BON&datestamp=Sat+Nov+05+2022+11%3A25%3A57+GMT-0400+(Eastern+Daylight+Time)&version=6.26.0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=s00%3A1%2Cf00%3A1%2Cm00%3A1%2Ct00%3A1%2Ci00%3A1%2Cf02%3A1%2Cm02%3A1%2Ct02%3A1&AwaitingReconsent=false; __Host-sp_csrf_sid=58a4029310e3b543769a0ed2c376e7ec36b9bef44cce330c50728b5205d3f67b',
    'origin': 'https://accounts.spotify.com',
    'prefer': 'safe',
    'referer': 'https://accounts.spotify.com/en/login',
    'sec-ch-ua': '"Microsoft Edge";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.26',
    'x-csrf-token': '013acda71974bb0a56dec1b7da5ce9786b086418c531363637363631383438383732',
}

data = {
    'username': 'Chehab.ibrahim@outlook.com',
    'password': 'IBRahim@Spotify',
    'remember': 'true',
    'recaptchaToken': '03AIIukzgQeMpNFozfwl8O8cT4V2Y5i6FC80KBdm5XYIKC6na75xbO5I08JbCqbjqvYGBav8StHR5oMhuaTQCdIyX7Y_FuPRsbsYcutFgDcE2kUgIV1IEh1LumBDafw-gR-2ukdFpLWGo2Dqp8Z44ICMREl67lTJ1DcNEPO4Tb7E2CFpOLHxiy2hQMzJNzqIS3JUNyFiYfks5vDOnFjxE-97M6qjAJT_KhS0YStVRDu6V90vF5OtDUTU5NwOPO2enNPAKczCpSHALiq7Iyb6t9qzlPgEeOzXiXXUj0_z-G97lNjnjbIo7S4eiHzfIhP_2C5PUMDfI0QmSYk1JpoqZGKCn2QsnhoDKI7nbv6j5KVv-NBClsiyDoySLz-nIfh56m28tgej405OK24Hmlrb-X5Ao9BP_6PpoKeUN0Xl8_eZBrAJdL3qHaNPHixtuI4u1lvt3Fa3WF1a1S5as_EI8xblz9oBy_Z4eDE0xQ37lk_QBVeybiufY_di6FCCh4yaUyIR544mc_TZaynbmj2OlehRAQKC05Ws3JPisNEx1Bpgtf_9drLZgAczViQKRggYcKULrVMZCiBQDhtCudQKU55uSz-R0FzvXMsTlYyF5uuGwnS6FJ14MLtaYLDZzxAO_G0ttwqKT9Pe-XJvEagl3ujoblwlkeVFbTi1gGNCzRh7MGUCXXdUq4Sx7RZmumJ0wma7qDjIxtjeH9KDMoI0OInZ4uHzUIaxIIzCxWweqvIfKWVmVIxGYXqzwfByMMspqCkTrxbee1nXnLMyzX13NnX9g8p75UXV6TfXawq5XlC8gF0bxNjOzPtIuZpRjsZ4dlh-h7I8lO5ix2r-oVnuPtJ8mF46ePYNNcU04EIamw6D0MvO7PKOUzNoZ9EUDWdp_8-nKaoY_KHCiBYIeiJIQxT9j-so3jPlODJE-bOTvX3mqrKsZkNZbsb_qAVj3zmmGB5bWOvyYcK1WhY58Ww1uv5YUtrpxejhsAj5P-uY0u-Q7TffryPLUwuFPkLzskAxI98W2Hvbx0hmke6Ru3xGkxqhZtUe9S89Plp-cSJDwxXYQJkQK2W9tJtsez7byGdu9vzdf5R-YFRTTpIhvD4d6shIYRjOo3a1xL_qiX-5PjWquopoDHm45fId9nYbrYLYkrJmT4MVoPRJ4BFBKmMcl8UTgPgIrOM18J_Bw85-mEkXwbii6O08xJQb_Mk818grqdZnXbYFbl6LAGJtlbyueU8iM8yUr1yRrQc1nWLsLTE7d0SenanXsPu88yO8jm-J-wH_8dj2nUnxh7uSF0Q4hn4dqo67k1VW9Udp1wwXO0wDjpo8B3mtrqDU9tKbFLDBb5x8mA95TqnAyPfPNzz6MEGG7qqKoSzcMO0vCcDhJUJVqUu-GAcXu-MgI',
    'continue': 'https://accounts.spotify.com/en/status',
}

response = requests.post('https://accounts.spotify.com/login/password', cookies=cookies, headers=headers, data=data)

print(response.cookies)

def method(arg1, arg2):
    print(arg1, arg2)

def method(arg1, arg2, arg3):
    print(arg1, arg2, arg3)
    
print(method(1, 2, 3))
print(method(1, 2))