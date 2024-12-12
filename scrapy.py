import requests
from bs4 import BeautifulSoup
import time
import json

base_url = 'https://iitb.irins.org/searchc/search'


def scrape_page(url, params):
    response = requests.post(url, data=params, verify=False, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')

    data = []

    experts = soup.find_all('div', class_='list-product-description')

    for expert in experts:
        profile_link_tag = expert.find('a', href=True)
        profile_link = profile_link_tag['href'] if profile_link_tag else 'N/A'
        expert_id = profile_link.split('/')[-1] if profile_link != 'N/A' else 'N/A'

        name_tag = expert.find('h4', class_='title-price')
        name = ' '.join(name_tag.text.split()) if name_tag else 'N/A'

        designation_tag = expert.find('span', class_='title-price')
        designation = ' '.join(designation_tag.text.split()) if designation_tag else 'N/A'

        department_tag = expert.find('b')
        department = ' '.join(department_tag.text.split()) if department_tag else 'N/A'

        expertise_tag = expert.find('i', class_='fa fa-cog')
        expertise = expertise_tag.next_sibling.strip() if expertise_tag and expertise_tag.next_sibling else 'N/A'

        # Convert expertise to an array
        expertise_list = [exp.strip() for exp in expertise.split(',')] if expertise != 'N/A' else []

        data.append({
            'Expert ID': expert_id,
            'Name': name,
            'Designation': designation,
            'Department': department,
            'Expertise': expertise_list,
            'Profile Link': profile_link
        })

    return data


if __name__ == '__main__':
    params = {
        'field': 'all',
        'title': '',
        'designation[]': 'Professor',
        'page': 1,
        'limits': 700  # Set the number of entries per page to 100
    }

    time.sleep(0.5)

    scraped_data = scrape_page(base_url, params)
    with open('scraped_data.json', 'w') as json_file:
        json.dump(scraped_data, json_file, indent=4)

    print("Data has been written to scraped_data.json")