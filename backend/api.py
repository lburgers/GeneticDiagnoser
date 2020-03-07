import spacy
import xml.etree.cElementTree as ET
from django.http import JsonResponse

# TODO: load XML and nlp stuff on server init
# TODO: XML loader
# TODO: XML searcher
# TODO: probability matcher
# should be higher if more words/larger phrase match, should be higher if rare phenotype, and all multiplied by the phenotypes prior
# TODO: API

# TODO: fix front end loader (maybe add whitenoise package)

nlp = spacy.load('en_core_web_sm')

def parse(request):
    query = request.GET.get('q', '')

    doc = nlp(query)

    # should these be stemmed (ie. lemmas) or should they be the full text
    noun_phrases = [chunk.lemma_ for chunk in doc.noun_chunks]
    nouns = [token.lemma_ for token in doc if token.pos_ == 'NOUN']

    # is this the best way to dedup
    all_queries = list( set( noun_phrases + nouns ))

    return JsonResponse({'results': all_queries})

