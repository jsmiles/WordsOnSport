import requests
import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


big_list = []

def find_between(s, first, last):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


def parser(page):
    headers = {'User-Agen': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0'}
    url = f'https://www.extratime.com/news/10/page/{page}/?q=preview'
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    articles = soup.find_all('div', {'class':'archive-single'})
    for item in articles:
        title = item.find('a', {'class': 'read-more-link'}).text
        links = 'https://www.extratime.com/' + item.find('a', {'class': 'read-more-link'})['href']
        r_href = requests.get(links)
        article = BeautifulSoup(r_href.text, 'html.parser')

        local_list = []

        text = article.find('div', {'class': 'left-content'}).text.strip()
        reporter = article.find('div', {'class': 'content-category'}).text.strip()
        referee = find_between(text, 'Referee: ', '\n').strip()
        comp = find_between(text, 'League Preview:', 'Credit:')
        home_team = find_between(comp, ' ', ' -v-').strip()
        away_team = find_between(comp, '-v- ', '\n').strip()
        date = find_between(text, reporter, 'Credit:').strip()
        tags = find_between(text, "TAGS", reporter).strip().replace('\n', '')
        ht = home_team.upper()
        at = away_team.upper()
        ht_words = find_between(text, ht, at).strip().replace('\n', '')
        at_words = find_between(text, at, 'Referee:').strip().replace('\n', '')
        prediction = re.sub(f'{home_team} ','', find_between(text,'PREDICTION', 'Injured').strip().replace('\n', ''))


        local_list.append(reporter)
        local_list.append(referee)
        local_list.append(date)
        local_list.append(tags)
        local_list.append(home_team)
        local_list.append(away_team)
        local_list.append(ht_words)
        local_list.append(at_words)
        local_list.append(prediction)
        big_list.append(local_list)

    return big_list


for x in range(1,71):
    res = parser(x)
    print(len(res))

df = pd.DataFrame(big_list, columns=['reporter', 'referee', 'date', 'tags', 'home_team', 'away_team', 'ht_words', 'at_words', 'prediction'])
df.to_csv('loi_articles.csv', index=False)



##########################
## Pull the match results
##########################

url = ['https://www.extratime.com/competition/100/2033/#2021-league-of-ireland-premier-division',
       'https://www.extratime.com/competition/100/2034/#2020-league-of-ireland-premier-division',
       'https://www.extratime.com/competition/100/2031/#2019-league-of-ireland-premier-division',
       'https://www.extratime.com/competition/100/2028/#2018-league-of-ireland-premier-division',
       'https://www.extratime.com/competition/100/2026/#2017-league-of-ireland-premier-division',
       'https://www.extratime.com/competition/100/2024/#2016-league-of-ireland-premier-division',
       'https://www.extratime.com/competition/101/2033/#2021-league-of-ireland-first-division',
       'https://www.extratime.com/competition/101/2034/#2020-league-of-ireland-first-division',
       'https://www.extratime.com/competition/101/2031/#2019-league-of-ireland-first-division',
       'https://www.extratime.com/competition/101/2028/#2018-league-of-ireland-first-division',
       'https://www.extratime.com/competition/101/2026/#2017-league-of-ireland-first-division',
       'https://www.extratime.com/competition/101/2024/#2016-league-of-ireland-first-division']

big_list = []

for year in url:
    response = requests.get(year)
    # print(f'https://www.extratime.com/competition/100/2033/#{url}-league-of-ireland-{division}-division')
    soup = BeautifulSoup(response.text, 'html.parser')
    for x in soup.find_all("div", {"id": "Matches"}):
        for p in x.find_all("div", {"class": "fixturebar"}):
            local_list = []
            for q in p.find_all("div", {"class": "comp"}):
                local_list.append(q.get_text())
            for j in p.find_all("a", {"class": "max teamName"}): # home team
                local_list.append(j.get_text())
            for k in p.find_all("div", {"class": "fixturescore"}): # home team
                local_list.append(k.get_text())
            local_list.append(year)
            big_list.append(local_list)

print(len(big_list))


# # Create pandas dataframe
df = pd.DataFrame(big_list, columns=['CompDate', 'HomeTeam', 'AwayTeam', 'Score', 'YearDivision'])
df.to_csv('loi_results.csv', index=False)
