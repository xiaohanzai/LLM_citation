import requests
from urllib.parse import urlencode
from unidecode import unidecode
from utils import get_year_from_arxivid

def extract_lastname_ads(author):
    '''
    Extract the last name of an author from an ads author string.
    Ads authors look like 'CHIME/FRB Collaboration', 'Andersen, B. C.'.
    Remove spaces and convert to lower case.
    '''
    return unidecode(author.split(',')[0].lower().replace(' ', ''))

def extract_ads_refs(response):
    '''
    Returns a list of ref dicts from the response of an ads API call.
    '''
    refs = []
    for result in response.json()['response']['docs']:
        # extract arxiv id and arxiv year
        arxiv_id = ''
        arxiv_year = ''
        for identifier in result['identifier']:
            if 'arXiv:' in identifier[:7]:
                arxiv_id = identifier[len('arxiv:'):]
                arxiv_year = get_year_from_arxivid(arxiv_id)
                break
        if arxiv_id == '':
            arxiv_id = result['identifier'][0] # use the first identifier

        # get author names
        names = []
        authors = result['author']
        # check if big collaboration first
        # damn it... ligo virgo and another one can all appear in the same paper???
        # I have no idea how papers like that are gonna be cited so... those will be ignored for now
        if len(authors) <= 3:
            for author in authors:
                names.append(extract_lastname_ads(author))
        else:
            if 'Collaboration' in authors[0]:
                names.append(extract_lastname_ads(authors[0]))
                for i in range(1, len(authors)):
                    # find the first name that doesn't include the collaboration name
                    if 'Collaboration' not in authors[i]:
                        names.append(extract_lastname_ads(authors[i]))
                        break
                names.append('...')
            elif 'Collaboration' in authors[-1]:
                names.append(extract_lastname_ads(authors[-1]))
                names.append(extract_lastname_ads(authors[0]))
                names.append('...')
            elif len(authors) > 25:
                # in (rare?) cases collaboration name doesn't appear
                # although some nature papers have a crazy amount of authors too
                names.append('collaboration')
                names.append(extract_lastname_ads(authors[0]))
                names.append('...')
            else:
                # not a big collaboration, append two names
                names.append(extract_lastname_ads(authors[0]))
                names.append(extract_lastname_ads(authors[1]))
                names.append('...')

        # get pub date
        year = result['pubdate'][:4]
        pubdate = result['pubdate']

        # collect all info
        refs.append({
            'authors': names,
            'year': year,
            'arxiv_year': arxiv_year,
            'pubdate': pubdate,
            'arxiv_id': arxiv_id
        })

    return refs

def call_ads_api(arxiv_id, token, max_refs=500):
    '''
    Make an API call to fetch all references assuming max 500 references.
    '''
    query = f'references(identifier:arxiv:{arxiv_id})'
    encoded_query = urlencode({'q': query, 'fl': 'author,pubdate,identifier', 'start': 0, 'rows': max_refs})
    response = requests.get("https://api.adsabs.harvard.edu/v1/search/query?{}".format(encoded_query), \
                       headers={'Authorization': 'Bearer ' + token})
    return response

def get_ads_refs(arxiv_id, token, max_refs=500):
    '''
    This is the "main" function to call to extract all references of a paper being identified by its arxiv id.
    Make an API call to fetch all references and convert response to ref dicts.
    '''
    response = call_ads_api(arxiv_id, token, max_refs)
    return extract_ads_refs(response)
