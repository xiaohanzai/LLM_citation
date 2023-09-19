import requests
from bs4 import BeautifulSoup
import numpy as np

def main():
    # search all arxiv papers with "fast radio burst"
    url_template = 'https://arxiv.org/search/?query=fast+radio+burst&searchtype=all&abstracts=hide&order=-announced_date_first&size=200&date-date_type=submitted_date&start={}'

    arxiv_ids = []
    for n in range(0,1500,200): # I know there's going to be less than 1500 papers
        url = url_template.format(n) # next page
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all <a> elements with 'href' attributes containing 'arxiv.org/abs/'
        arxiv_links = soup.find_all('a', href=lambda href: href and 'arxiv.org/abs/' in href)
        for link in arxiv_links:
            arxiv_ids.append(link.text[6:])

    # search all arxiv papers with "FRB"
    url_template = 'https://arxiv.org/search/?query=FRB&searchtype=all&abstracts=hide&order=-announced_date_first&size=200&date-date_type=submitted_date&start={}'

    for n in range(0,1100,200): # I know there's going to be less than 1100 papers
        url = url_template.format(n)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        arxiv_links = soup.find_all('a', href=lambda href: href and 'arxiv.org/abs/' in href)
        for link in arxiv_links:
            if link.text[6:] not in arxiv_ids:
                arxiv_ids.append(link.text[6:])

    # manually add this one in
    arxiv_ids.append('1309.4451')

    # remove some papers
    arxiv_ids = np.array(arxiv_ids)
    ii = np.ones(len(arxiv_ids), dtype=bool)
    for i, arxiv_id in enumerate(arxiv_ids):
        # remove non-astro papers
        # I know this code is stupid, but this way I type it faster...
        if arxiv_id[0] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            ii[i] = False
            continue
        # remove too early papers
        if arxiv_id[:2] < '13' or arxiv_id[0] > '2':
            ii[i] = False
            continue
        # only keep papers before 2023 Sep
        if arxiv_id[:4] > '2308':
            ii[i] = False
            continue
    arxiv_ids = arxiv_ids[ii]

    print('got this number of arxiv ids:', len(arxiv_ids))

    # save to disk
    np.save('../data/FRB_arxivIDs', arxiv_ids)

if __name__ == '__main__':
    main()
