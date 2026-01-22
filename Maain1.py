import pandas as pd
import numpy as np
import os
import requests
from bs4 import BeautifulSoup
from time import sleep
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

csv_file = 'companies.csv'
base_url = 'https://www.ambitionbox.com/companies-in-pune?page='

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 11.0; Win64; x64)'
}

all_data = []

for page in range(1, 11):
    url = f'{base_url}{page}'
    print(f'Scraping page {page}...')
    
    try:
        req = requests.get(url, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(req.text, 'html.parser')

        cards = soup.select('div.companyCardWrapper')
        if not cards:
            print('No more cards found, stopping')
            break

        for card in cards:
            # Company name
            name_tag = card.select_one('a.companyCardWrapper__companyName')
            name = name_tag.get_text(strip=True) if name_tag else ''

            info_links = card.select('div.companyCardWrapper__tertiaryInformation a')

            data = {
                'Company Name': name,
                'Reviews': '',
                'Salaries': '',
                'Interviews': '',
                'Jobs': '',
                'Benefits': '',
                'Photos': ''
            }

            for link in info_links:
                count_tag = link.select_one('.companyCardWrapper__ActionCount')
                title_tag = link.select_one('.companyCardWrapper__ActionTitle')

                count = count_tag.get_text(strip=True) if count_tag else ''
                title = title_tag.get_text(strip=True) if title_tag else ''

                if title in data:
                    data[title] = count

            all_data.append(data)

        sleep(1)

    except Exception as e:
        print('Error:', e)

df = pd.DataFrame(all_data)

# Remove duplicates BEFORE saving
df.drop_duplicates(inplace=True)

# Convert text counts to numbers
def convert_to_num(value):
    if pd.isna(value) or value == '':
        return 0
    value = str(value).strip().lower()
    if 'k' in value:
        return int(float(value.replace('k', '')) * 1000)
    if 'l' in value:
        return int(float(value.replace('l', '')) * 100000)
        return int(float(value))

cols = ['Reviews', 'Salaries', 'Interviews', 'Jobs', 'Benefits', 'Photos']
for col in cols:
    df[col] = df[col].apply(convert_to_num)

# Engagement Ratio
df['reviews_per_job'] = np.where(
    df['Jobs'] > 0,              # condition
    df['Reviews'] / df['Jobs'],  # if true
    0                             # if false
)

# Save once (clean data)
df.to_csv(csv_file, index=False)
print(f'Saved: {csv_file}')
print('Total companies:', len(df))