import re
from unidecode import unidecode
import numpy as np

def clean_up_string(input_string):
    '''
    Given an input reference string, clean it up before matching the citation patterns.
    Input should look like e.g. 'Sloth et al. (2001)', 'Sloth 2002; Sloth et al. 2001a; Sloth & Flash 2002b'
    There are also cases of numbered references.
    TODO: this function will look difference once I ask gpt to output in json format.
    '''
    # get rid of parentheses and @
    string = re.sub(r'[@\(\)]', '', input_string)
    # get rid of extra content
    if ':' in string:
        string = string[:string.index(':')+1]
    # for numbered references, get rid of ref or ref. or Ref etc.
    string = re.sub(r'[rR]efs?\.?', '', string)
    string = re.sub(r'[rR]eferences?\.?', '', string)
    # those characters
    string = unidecode(string)

    return string

def convert_names_and_years_to_refdicts(names, years):
    '''
    Convert the input names and years strings into reference dict(s).
    Examples of names: 'sloth', 'sloth, flash', 'sloth, ...', 'collaboration, ...'
    Examples of years: '2002', '2020a', '2020a,b'
    Return a list of reference dicts with keys 'authors', 'year', 'pubdate' (=a,b,c,d if appears in years).
    '''
    refs = []
    names = re.sub(r'\s', '', names.lower()).split(',') # input is string, but I'll make it into a list
    if len(years)>=4:
        year = years[:4]
        if len(years)>4:
            for n in years[4:].split(','):
                refs.append({'authors': names, 'year': year, 'pubdate': re.sub(r'\s', '', n)})
        else:
            refs.append({'authors': names, 'year': year, 'pubdate': ''})
    return refs

def match_text_refs(string):
    '''
    Given a cleaned-up string (after calling clean_up_string()), try to match the text references in it with regex.
    Return a list of reference dicts.
    '''
    # text references
    name_pattern = r'[a-zA-Z][a-zA-Z\-/ ]+'
    year_pattern = r'[12]\d{3}[a-d]?(?:,\s*[a-d]+)*'
    problematic_mid = r'[\s,]*' # e.g. sloth et al. (2001,2002) would be extracted in a problematic way

    # there's a small fraction of references separated by , instead of ;
    # so I decided not to split into sub strings by ;
    # just try matching various different patterns
    refs = []
    # first try matching et al
    # I didn't find cases like A, B, et al. but maybe need to keep an eye
    while True:
        m = re.search(f'(?P<names>{name_pattern})et al\.{problematic_mid}(?P<years>{year_pattern})', string)
        if m is None:
            break
        refs += convert_names_and_years_to_refdicts(m.group('names')+',...', m.group('years'))
        string = string[:m.start()] + string[m.end():]
    # in newer versions of MN and ApJ templates there shouldn't be triple-author cases... but just in case
    while True:
        m = re.search(
            f'(?P<name1>{name_pattern}),\s?(?P<name2>{name_pattern}),'\
            f'?\s?\&\s?(?P<name3>{name_pattern}){problematic_mid}(?P<years>{year_pattern})',
            string)
        if m is None:
            break
        refs += convert_names_and_years_to_refdicts(m.group('name1') + ',' + m.group('name2') + ',' + m.group('name3'),
                                      m.group('years'))
        string = string[:m.start()] + string[m.end():]
    # then try double authors
    while True:
        m = re.search(
            f'(?P<name1>{name_pattern})\&\s?(?P<name2>{name_pattern}){problematic_mid}(?P<years>{year_pattern})',
            string)
        if m is None:
            break
        refs += convert_names_and_years_to_refdicts(m.group('name1') + ',' + m.group('name2'), m.group('years'))
        string = string[:m.start()] + string[m.end():]
    # finally try single author
    while True:
        m = re.search(f'(?P<name>{name_pattern}){problematic_mid}(?P<years>{year_pattern})', string)
        if m is None:
            break
        # sometimes collaboration names don't include et al.; need to add it
        name = m.group('name')
        if 'ollaboration' in name: # should be captial C though
            name += ',...'
        refs += convert_names_and_years_to_refdicts(name, m.group('years'))
        string = string[:m.start()] + string[m.end():]

    return refs

def extract_txt_refs(input_string):
    '''
    This is the "main" function to call that extracts ref dicts from an input string, for text references.
    '''

    # temporarily convert to lower-case to compare...
    string = input_string.lower()[:10]
    if 'sec.' in string or 'section' in string or\
        'tab.' in string or 'table' in string or\
        'fig.' in string or 'figure' in string or\
        'catalog' in string or\
        'note:' in string or 'n/a' in string:
        return []

    string = clean_up_string(input_string)

    # try matching text references
    refs = match_text_refs(string)

    # # print all other not-matched cases
    # if len(refs) == 0:
    #     print('not matched', string)

    return refs

def match_num_refs(string):
    '''
    Given a cleaned-up string (after calling clean_up_string()), try to match the number references in it with regex.
    Return a list of reference indices.
    '''
    number_pattern = r'[1-9][0-9]?[0-9]?'

    # deal with extra spaces in - first
    string = re.sub(r'(\d)\s*-\s*(\d)', r'\1-\2', string)
    string = re.sub(r'(\d)\]\s*-\s*\[(\d)', r'\1-\2', string)
    # and then substitute all spaces into comas, so I don't have to deal with spaces anymore
    string = re.sub('\s', ',', string)
    # get rid of square brackets
    string = re.sub(r'[\[\]]', ',', string)
    # there are some cases where refs are separaed by ;
    # also change : into coma
    string = re.sub(r'[;:]', ',', string)

    inds = []
    for substring in string.split(','):
        if substring == '':
            continue
        # match patterns like 1-10
        m = re.fullmatch(f'(?P<n_start>{number_pattern})-(?P<n_end>{number_pattern})', substring)
        if m:
            inds += np.arange(int(m.group('n_start')), int(m.group('n_end'))+1, dtype=int).tolist()
            continue
        # match single number
        m = re.fullmatch(f'(?P<n>{number_pattern})', substring)
        if m:
            inds.append(int(m.group('n')))
            continue
        # there shouldn't be other cases?

    return inds

def extract_lastnames_scipdf(ref_dict):
    '''
    Extract last names of authors from a ref returned by scipdf.
    If a lot of authors, keep <=3.
    '''
    names = ''
    for i,author in enumerate(ref_dict['authors'].split(';')):
        m = re.search(r'[A-Z][a-zA-Z]+([-/][A-Z][a-zA-Z]+)?(\s[A-Z][a-zA-z]+)*', author)
        if m:
            if i > 0:
                names += ','
            names += m.group(0)
        if i > 3:
            break
    return names

def extract_num_refs(string, ref_list):
    '''
    This is the "main" function to call that extracts ref dicts from an input string, for numbered references.
    ref_list is a list of references returned by scipdf.
    This function should be used if text reference extration fails.
    TODO: I'm ignoring numbered references because scipdf doesn't fully extracts all references from a paper.
    '''
    inds = match_num_refs(string)
    refs = []
    for ind in inds:
        names = extract_lastnames_scipdf(ref_list[ind-1])
        refs += convert_names_and_years_to_refdicts(names, ref_list[ind-1]['year'])
    return refs
