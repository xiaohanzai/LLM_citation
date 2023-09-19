import pandas as pd
import streamlit as st
import sys
sys.path.append('code/')
from retriever_functions import *

@st.cache_resource
def load_data():
    citation_data = pd.read_csv('data/FRB_citations_23.csv') 
    abstract_data = pd.read_csv('data/FRB_abstracts.csv')
    return citation_data, abstract_data

@st.cache_resource
def load_retrievers(key):
    retriever_abstract = gen_retriever('VectorStoreIndex', 'abstract', openai_api_key=key, path_to_db_folder='./data/')
    retriever_citation = gen_retriever('VectorStoreIndex', 'citation', openai_api_key=key, path_to_db_folder='./data/')
    return retriever_citation, retriever_abstract

def get_results_above_threshold(results_citation, results_abstract, score_threshold_percentile):
    if query and retriever_citation is not None and citation_data is not None:
        results_abstract = rearrange_query_results(results_abstract, score_threshold=0.8)
        scores = get_all_scores(results_citation, show_hist=False)
        score_threshold = np.percentile(scores, score_threshold_percentile)
        results_citation = rearrange_query_results(results_citation, score_threshold=score_threshold, sort=True)
        return results_citation, results_abstract

@st.cache_data
def query_retreivers(query, score_threshold_percentile):
    if query and retriever_abstract is not None and abstract_data is not None:
        results_citation = retriever_citation.retrieve(query)
        results_abstract = retriever_abstract.retrieve(query)
        results_citation, results_abstract = get_results_above_threshold(results_citation, results_abstract, score_threshold_percentile)
        return results_citation, results_abstract

st.title("LLM Citation Tool")
st.write(
    "Have you ever felt it quite a headache to find out which papers to cite when writing\
    a paper? This tool is designed to help you with that.")
st.write("This app is a prototype built from arXiv papers on **fast radio bursts (FRBs)**, which means\
    it can only do FRB literature search for now.\
    For each FRB paper from July 2022 to Aug 2023, we extracted the citations in the introduction\
    section of the paper and the reasons for citing these papers using OpenAI's API.\
    The motivation of this project is that we find that humans are highly biased towards which papers\
    they want to cite, and that finding references from embedding abstracts often gives interestingly\
    unuseful results (e.g. those papers are indeed very related to a topic but just not what people\
    normally would like to cite).\
    Therefore, why not search for the reasons why other people cite papers and follow them?")
st.write("On the left column of this page, you will see query results from performing a similarity search\
    on the reasons for citation. On the right column, you will see query results from embedding the\
    title and abstracts of the papers. You can adjust the similarity score threshold and the number\
    of results to display using the sliders below.")
st.write("This app uses OpenAI Embedding so **please input your own API key** below.\
    It's not going to cost you more than a few cents, but I'm poor so I don't want to share my own key.")

st.write("This is just a prototype and the citation query is very likely to return unsatisfying results.\
    For example, some papers (e.g. Lorimer et al.) that are identified by gpt3.5 as\
    'cited to provide background knowleges of FRBs'\
    seem to be matched to whatever query you make.  Try raising the similarity score threshold and see if\
    anything changes.\
    Including abbreviations in the query, e.g. fast radio burst (frb), circumgalactic medium (cgm),\
    may also help getting better query results.\
    There are, however, failure cases like searching for FRB scintillation.  Perhaps OpenAI Embedding doesn't\
    process scintillation as an astrophysical term?")

st.write("There may be cases where the abstract search gives better results, so don't rely too much on the reasons for citation\
    for now.")

api_key = st.text_input("Enter your OpenAI API key:")
query = st.text_input("Enter your query:")
st.write("Similarity score threshold for the citation search is determined by the percentile of the all scores.\
        Default is set to 99.7, which roughly returns the top 20 most similar reasons of citation to the query.\
        We then group these reasons with the same arXiv id and count the number of times each one appears.\
        The final results are sorted by the number of times each arXiv id appears.\
        This does not affect the abstract search because that one simply returns the top results above a\
        similarity score threshold of 0.8.")
score_threshold = st.slider("Similarity score threshold (percentage):", min_value=99.0, max_value=99.8, value=99.7)
search_clicked = st.button("Search")

results_citation = results_abstract = None
if search_clicked and query and api_key:
    citation_data, abstract_data = load_data() 
    retriever_citation, retriever_abstract = load_retrievers(api_key)

    results_citation, results_abstract = query_retreivers(query, score_threshold)

col_l, col_r = st.columns(2)
n_results = 5

with col_l:
    st.header("**Results**: from embedding reasons for citation")
    if results_citation is not None:
        for i in range(min(n_results, len(results_citation))):
            row = results_citation.iloc[i]
            doc_id = row['doc_id']
            reasons = row['reasons']
            if len(reasons) > 500:
                reasons = reasons[:500] + '...'
            arxiv_id = citation_data.iloc[doc_id]['arxiv_id']
            txt_ref = citation_data.iloc[doc_id]['txt_ref']
            st.subheader(f"{i+1}: {txt_ref} (arXiv id: {arxiv_id})")
            st.write("***Reasons that people cited it:***")
            for reason in reasons.split(';'):
                st.write(reason)
            st.divider()
    # else:
    #     st.write('nothing mached your search')

with col_r:
    st.header("**Results**: from embedding title and abstracts")
    if results_abstract is not None:
        for i in range(min(n_results, len(results_abstract))):
            row = results_abstract.iloc[i]
            doc_id = row['doc_id']
            arxiv_id = abstract_data.iloc[doc_id]['arxiv_id']
            authors = abstract_data.iloc[doc_id]['authors']
            title = abstract_data.iloc[doc_id]['title']
            abstract = abstract_data.iloc[doc_id]['abstract']
            if len(abstract) > 800:
                abstract = abstract[:800] + '...'
            st.subheader(f"{i+1}: {authors} (arXiv id: {arxiv_id})")
            st.write(f"***Title:*** {title}")
            st.write(f"***Abstract:*** {abstract}")
            st.divider()
    # else:
    #     st.write('nothing mached your search')
