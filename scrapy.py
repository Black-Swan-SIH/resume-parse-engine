from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup

driver = webdriver.Chrome()
base_url = "https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors=iitd.ac.in+"

driver.get(base_url)

time.sleep(3)

profile_list = []

def parse_profiles():
    soup = BeautifulSoup(driver.page_source, "html.parser")
    profiles = soup.find_all("div", class_="gs_ai_t")

    for profile in profiles:
        name = profile.find("h3", class_="gs_ai_name").text.strip() if profile.find("h3", class_="gs_ai_name") else "No name"
        link = profile.find("a", href=True)['href'] if profile.find("a", href=True) else "No link"
        institution = profile.find("div", class_="gs_ai_aff").text.strip() if profile.find("div", class_="gs_ai_aff") else "No institution"
        interests = ", ".join([interest.text.strip() for interest in profile.find_all("a", class_="gs_ai_one_int")]) if profile.find_all("a", class_="gs_ai_one_int") else "No interests"

        profile_data = {
            "Name": name,
            "Link": f"https://scholar.google.com{link}" if link != "No link" else "No link",
            "Institution": institution,
            "Interests": interests
        }
        profile_list.append(profile_data)

parse_profiles()

for page in range(1, 10):
    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        next_button = soup.find("button", class_="gs_btnPR gs_in_ib gs_btn_half gs_btn_lsu")
        if not next_button:
            print("No more pages available.")
            break

        next_url = next_button.get("onclick")
        if not next_url:
            print("No next URL found.")
            break

        after_author = next_url.split("after_author=")[1].split("&")[0]
        next_page_url = f"{base_url}&after_author={after_author}&astart={page * 10}"

        driver.get(next_page_url)
        time.sleep(3)

        parse_profiles()
    except Exception as e:
        print(f"Error occurred: {e}")
        break

driver.quit()

for profile in profile_list:
    print(profile)