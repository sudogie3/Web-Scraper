import argparse
import csv
import re

import wordfreq
import requests
import pandas as pd
from bs4 import BeautifulSoup


# Musze wybrać jakiego typu ma być to wiki (kanye west , marvel , ekipa friza)

class Scraper():

    def __init__(self , link_URL ,use_local_html_file_instead=False):
        self.link = link_URL
        self.use_lokal = use_local_html_file_instead

    def changingSpaceTo_(self , phrase):
        phrase_tmp = ''
        for charackter in phrase:
            if charackter == ' ':
                phrase_tmp = phrase_tmp + '_'
            else:
                phrase_tmp = phrase_tmp + charackter
        return phrase_tmp

    def SiteDownloader(self, URL):
        response = requests.get(URL)
        if response.status_code != 200:
            print(f"Nie ma takiej strony: {URL} lub nie działa")
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    def summary(self , phrase):
        phrase_tmp = self.changingSpaceTo_(phrase)
        URL_tmp = self.link + '/' + phrase_tmp
        soup = self.SiteDownloader(URL_tmp)
        # zrobić to w div class
        para  = soup.find('p').get_text()
        print(para)


    def table(self , phrase , number , first_row_header = False):
        phrase_tmp = self.changingSpaceTo_(phrase)
        URL_tmp = self.link + '/' + phrase_tmp
        soup = self.SiteDownloader(URL_tmp)
        file_name = f'{phrase_tmp}.csv'
        tables = soup.find_all('table')
        if number > len(tables):
            print(f"Na stronie {URL_tmp} nie ma tylu tabel")
            return None

        table = tables[number - 1]
        rows = table.find_all('tr') # wiersze
        data = []
        print(rows)
        tableForPandas = []
        for row in rows:
            dataAndHeadersInRow = row.find_all(['td' , 'th']) # dane i nagłówki
            dataAndHeadersInRowText = [data.get_text().strip() for data in dataAndHeadersInRow] # bierzemy jedynie tekst
                                                                                     # z każdej komorki
            print(dataAndHeadersInRow)
            tableForPandas.append(pd.Series(dataAndHeadersInRowText))
            data.append(dataAndHeadersInRowText)
        #print(tableForPandas)

    def count_words(self , phrase):
        phrase_tmp = self.changingSpaceTo_(phrase)
        soup = self.SiteDownloader(self.link + '/' + phrase_tmp)

        if soup is None:
            return
        text = soup.find("div" , class_ = "mw-content-ltr mw-parser-output").get_text(strip=True , separator=' ')

        print(text)
        words = []
        word = ""
        skips ={"(" , ")" , "[" , "]" , "{" , "}" , "\"" , "\'" , ";" , ":" , "*" , "!" , "?" , "`", "." , "," , "'s"}
        for letter in text:
            if letter == " ":
                words.append(word)
                word = ""
            elif letter in skips:
                pass
            else:
                word += letter.lower()
        for word in text:
            pass
        setOfWords = {}
        for word in words:
            if word not in setOfWords:
                setOfWords[word] = 1
            else:
                setOfWords[word] += 1
        df = pd.DataFrame(list(setOfWords.items()) , columns=['słowa' , 'licznik'])
        print(df.head(n=100))








    def analyze_relative_word_freq(self):
        pass


    def auto_count_words(self):
        pass


        # with open(file_name , 'w' , encoding='utf-8') as csvfile:
        #     writer = csv.writer(csvfile)
        #     for row in rows:
        #         writer.writerow(row)







        



def creating_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--summary' , type = str , help ='searching phrase')
    # parser.add_argument('--table' , type = str , help = 'searching for a table in ...')
    # parser.add_argument('--number' , type = int , help = 'searching for n-th table')
    # parser.add_argument('--first-row-is-header' , type = bool , action=False , help = 'if this argument '
    #                                                                                   'is given then we claim that first '
    #                                                                                   'row is a header')
    # parser.add_argument('--count-words' , type = str ,help = 'counting in given phrase words' )
    # parser.add_argument('--analyze-relative-word-frequency' , type = bool , help = 'shows the difference'
    #                                                                                ' between frequencies in the words '
    #                                                                                'in article' )
    # parser.add_argument('--mode' , type = str , help = 'sorts the relative-word-frequencies table by '
    #                                                    'the given arg')
    # parser.add_argument('--chart' , type = str , action=False , help= 'creates a chart of the '
    #                                                                   'relative-word-frequency analiz')
    # parser.add_argument('--auto-count-words' , type = str , help='counting in given phrase '
    #                                                              'words and going into hyperlinks')

    return parser


if __name__ == '__main__':
    URL = 'https://bulbapedia.bulbagarden.net/wiki'
    obiekt = Scraper(URL)
    #obiekt.table('Type' , 2)
    obiekt.count_words('Type')
