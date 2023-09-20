# Towards building a search engine of references to put in research papers

When I write papers, it's always a headache trying to find out what papers are appropriate to cite in the introduction section, and how many is enough.
I therefore tried building a search engine of papers by embedding titles and abstracts of arxiv papers and doing a similarity search.
The results are not satisfying.  Somehow what a LLM thinks is relevant to my query is not really the same as what researchers think is related to a topic.
Part of the reason, I believe, is that humans are highly biased towards which papers to cite.
For example, when I write a paper on fast radio burst (FRB) I wouldn't cite one that advocates for aliens as the origin of FRBs.
So I thought, why not use gpt to extract the reasons of citing each reference in each arxiv paper and then build a search engine on top of that.

Therefore, I created this prototype search engine for references based on arxiv papers on **fast radio burst**.
The reason for narrowing down to FRB papers is that the first FRB was discovered in 2007, and it wasn't until 2013 that most of the FRB papers started emerging.
So there's only <1500 FRB papers in total until Sep 2023, meaning that there's way less garbage than a lot of other fields in astronomy, and also
a lot less tokens to pass through gpt (and get myself charged).
For extracting the reasons of citation, I only used 249 arxiv papers from July 2022 to Aug 2023 because these most recent papers should be diverse enough
in terms of topic and should contain a lot of the most important citations already (also because I don't have that much money to spend by calling openai's api).
The search engine is then built on top of the 6330 reasons for citing about 2300 papers that appeared in people's introduction sections, among which 700 are
FRB papers.  This means that the citation extraction only covered half of the FRB papers in total, which makes sense because the most recent papers are likely
not cited yet, and there are a lot of papers that people don't want to cite as well.

For comparison, I also included in this app searching by embedding title and abstract.  Sometimes this actually returns better results, so the best practice
is probably to combine citation search and abstract search.  See the examples in `retrieve_examples.ipynb` for details.

Running this app locally requires `streamlit`:

`streamlit run app.py --server.address localhost --browser.gatherUsageStats false`

Here's an example search:

<img width="242" alt="Screenshot 2023-09-19 at 6 34 46 PM" src="https://github.com/xiaohanzai/LLM_citation/assets/30164085/5964011f-3284-4870-ba69-a192e059b763">

If you want to recreate the process of generating all the data used in this project, run in the `code` folder:

`python run_gen_arxivids.py`

`python run_get_abstracts.py`

`python run_get_intros.py`

`python run_extract_citations.py`

`python run_cross_match.py`

`python run_gen_vectordb.py`

You'll need several other packages like `scipdf`, `arxiv`, `langchain`... and most importantly, an openai api key and a small amount of money to send to openai.
