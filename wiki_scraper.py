from  WikiClasses.wiki_arg_parser import Control
from WikiClasses.wiki_scraper_class import Scraper
""" This is the main usage """
if __name__ == "__main__":
    URL = "https://bulbapedia.bulbagarden.net/wiki"
    controler = Control(URL)
    controler.iterateArguments()
    obiekt = Scraper(use_local_html_file_instead=True)
    obiekt.summary('Da Vinci')
