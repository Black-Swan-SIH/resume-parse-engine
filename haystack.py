"""
Fuck it we ball
"""
from urllib import parse, request
from bs4 import BeautifulSoup
from time import sleep
import re
import pprint
def Scrape_profile(label, university_names, country):
    paper_repos_dict = {
        'name': [],
        'email': [],
        'affiliations': [],
        'Citation': [],
        'interests': [],
        'uni': [],
        'country': []
    }
    for uni in university_names:
        params = {
            "view_op": "search_authors",
            "mauthors": f'label:{label} "{uni}"',
            "hl": "en",
            "astart": 0,
            "engine": "google_scholar_profiles",
        }

        while True:
            try:
                url = r"https://scholar.google.com/citations?"
                data = parse.urlencode(params)
                req = request.Request(url + data, headers={'cookie': '<my cookie>'})
                resp = request.urlopen(req).read()
                soupy = BeautifulSoup(resp, "html5lib")
                proftags = soupy.find_all('div', class_='gs__profile gs__profile_main')
                for mytag in proftags:
                    paper_repos_dict['name'].append(mytag.find("h3", {"class": "gs_ai_name"}).text)
                    paper_repos_dict['email'].append(mytag.find("div", {"class": "gs_ai_eml"}).text)
                    paper_repos_dict['affiliations'].append(mytag.find("div", {"class": "gs_ai_aff"}).text)
                    paper_repos_dict['Citation'].append(mytag.find("div", {"class": "gs_ai_cby"}).text[8:])
                    paper_repos_dict['interests'].append([item.text for item in mytag.findAll("a", {"class": "gs_ai_one_int"})])
                    paper_repos_dict['uni'].append(uni)
                    paper_repos_dict['country'].append(country)

                sleep(0.5)

                next_button = soupy.select_one("gsc_pgn button.gs_btnPR")
                if next_button and next_button.get('onclick'):
                    match = re.search(r"after_author\\x3d(.*)\\x26", next_button.get('onclick'))
                    if match:
                        params["after_author"] = match.group(1)
                        params["astart"] += 10
                    else:
                        break
                else:
                    break

            except Exception as e:
                print(f"Error occurred: {e}")
                break

        return paper_repos_dict

label = "Finite Time Thermodynamics"
university_name = ["Indian Institute of Technology, Delhi"]
country = 'India'

result = Scrape_profile(label, university_name, country)
pprint.pprint(result)
