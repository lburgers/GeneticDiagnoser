# Genetic Diagnoser

Relevant files:
```
backend/api.py
frontend/src/App.js
```

## Installation

```
yarn build
pip install -r requirements.txt
```

## Running

```
gunicorn backend.wsgi
```

## Possible edge cases

There are many edge cases to account for in this project.

* Misspellings
    People could easily mispell long conditions which would lead the program astray
* Colloquialisms and Synonyms
    ie. if someone writes 'bloody nose' instead of 'epistaxis', this implementation would fail.
    Similarly the program would fail with abbreviations like UTI.
* Words which spacy is unfamiliar with
    Some medical terms may be unrecognizable and misinterpretted as verbs or adjectives and could be missed in this implementation.
* Describing phenotype rather than stating it as a noun
    ie. 'the patient has trouble falling asleep' instead of 'insomnia'.
* Generic nouns
    Currently the app uses all Nouns and NPs to search for phenotypes.
    This causes issues with nouns like 'abnormality' which match the description of many different phenotypes.
