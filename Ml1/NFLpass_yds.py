import requests
from bs4 import BeautifulSoup
import re
import csv
import yaml
import os
headers = ['Player','Pass Yds','Cmp%','TD','INT','Rate','Year']
CSV_FILE = 'NFL_Passing_STAT.csv'
class NFLSTAT_extractor:
    def __init__(self, url):
        self.url = url
        self.content = ""
        self.qb = []
        self.pass_list = []
    def load_page(self):
        page = requests.get(self.url)
        if page.status_code == 200:
            self.content = page.content
    def get_content(self):
        return self.content
    def process_content(self):
        children = self.get_all_dropdowns(self.url)[1:5]
        for s in children:
            year = s[56:60]
            #print(year)
            self.url = s
            all_pages = self.get_all_pages(self.url)
            for page in all_pages:
                soup = BeautifulSoup(requests.get(page).content, 'html.parser')
                table_one = soup.find_all('table')[0]
                rows = table_one.find_all('tr')
                for row in rows[1:]:
                    cols = row.find_all('td')
                    name = cols[0].text.strip()
                    yds = cols[1].text.strip()
                    cmp_percentage = cols[5].text.strip()
                    td = cols[6].text.strip()
                    interceptions = cols[7].text.strip()
                    rating = cols[8].text.strip()
                    self.pass_list.append([name,yds,cmp_percentage,td,interceptions,rating,year])
        print(len(self.pass_list))
    def generate_csv(self):
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(self.pass_list)
    def get_all_dropdowns(self,url):
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        dropdown = soup.find('select', {'class': 'd3-o-dropdown'})
        lis = []
        options = dropdown.find_all('option')
        for i in options:
            val = i.get('value')
            lis.append(f"https://www.nfl.com{val}")
        return lis
    def get_all_pages(self,url):
        pages_list = []
        pages_list.append(url)
        link = url
        while link is not None:
            res = requests.get(link)
            soup = BeautifulSoup(res.text, 'html.parser')
            buttons = soup.find_all('a')
            if len(buttons) > 0:
                button_var = "Next Page"
                for i in buttons:
                    button = i.get('title')
                    if button == button_var:
                        href = f"https://www.nfl.com{i.get('href')}"
                        pages_list.append(href)
                        link = href
                    else:
                        link = None
        return pages_list
if __name__ == "__main__":
    extractor = NFLSTAT_extractor('https://www.nfl.com/stats/player-stats/')
    extractor.load_page()
    extractor.process_content()
    extractor.generate_csv()
    extractor.get_all_pages('https://www.nfl.com/stats/player-stats/category/passing/2023/reg/all/passingyards/desc')
# Constants
