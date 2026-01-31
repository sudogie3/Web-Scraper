from WikiClasses.wiki_scraper_class import whatLanguageOffline , extractPhrase , isItWikiPage , getWordsFromText
import pytest
"""Checking if teh extraction works"""
@pytest.mark.parametrize("link, expected", [
    ('/wiki/something', 'something'),
    ('/wiki/Team_Rocket' , 'Team_Rocket'),
    ('/wili/Team_Pocket' , None),
    (None , None)
])
def test_extract_phrase(link ,expected):
    assert extractPhrase(link) == expected
"""Checking if the language identification is correct"""
@pytest.mark.parametrize("phraseHTML, expected", [
    ('Team_Rocket' , 'en'),
    ('Type' , None) # nie mam jego kodu w katalogu
])
def test_what_langauge(phraseHTML , expected):
    assert whatLanguageOffline(phraseHTML) == expected

"""Checking if the link is sub wiki domain"""
@pytest.mark.parametrize("link, expected", [
    ('/wiki/something', True),
    ('/wiki/Team_Rocket' , True),
    ('/wili/Team_Pocket' , False),
    (None , False)
])
def test_is_it_wiki_page(link , expected):
    assert isItWikiPage(link) == expected

"""checking if function correctly lowercases and separates words"""
@pytest.mark.parametrize("text, expected", [
    ('Hello World', ['hello' , 'world']),
    ('DrinkWater', ['drinkwater']),
    (1, []),
    (None, None)
])
def test_parse_text(text , expected):
    assert getWordsFromText(text) == expected