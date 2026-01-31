import csv
import json
import os.path
import time
import wordfreq
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
"""Function that takes the html code and gets the language"""
def whatLanguageOffline(phrase):
    phrase_tmp = phrase.replace(" ", "_")
    path = f"./{phrase_tmp}.html"
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as file:
        htmlText = file.read()
    soup = BeautifulSoup(htmlText, "html.parser")
    return soup.find('html').get('lang')

"""Function that checks if the sufix of the page is Wiki"""
def isItWikiPage(phrase):
    if phrase is None:
        return False
    prefix = "/wiki/"
    if len(phrase) >= len(prefix) and phrase[:len(prefix)] == prefix:
        return True
    return False
"""Function that extract a phrase from link"""
def extractPhrase(phrase):
    prefix = "/wiki/"
    if isItWikiPage(phrase):
        return phrase[len(prefix):]
    return None
"""Function which downloads a site"""
def SiteDownloader(URL):
    response = requests.get(URL)
    if response.status_code != 200:
        print(f"Nie ma takiej strony: {URL} lub nie działa, kod request {response}")
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    return soup
"""Function that gives table of lower case separated words"""
def getWordsFromText(text):
    if text is None:
        return None
    text = str(text)
    words = []
    word = ""
    for i in range(0,len(text)):
        letter = text[i]
        if letter == " ":
            words.append(word)
            word = ""
        elif letter.isalpha() or letter == "-":
            word += letter.lower()
            if i == len(text) - 1:
                words.append(word)
    return words
"""Whole scraper class that has methods which do all the main functionalities"""
class Scraper:
    def __init__(self, link=None, use_local_html_file_instead=False):
        if link is not None and use_local_html_file_instead:
            raise ValueError(
                "Error, you can not give link and set the local_usage argument simultaneously, please choose only one"
            )
        self.link = link
        self.use_local = use_local_html_file_instead
        #used for the analyze_relative_word function
        self.used_count_words = False
        self.language = None
        #used for the auto-count function
        self.alreadyProcessed = {}
        self.first = True

    def summary(self, phrase):
        # checks if the arg is correct
        if phrase is None:
            return False
        phrase_tmp = phrase.replace(" ", "_")
        # checks if we use local file if not then we download
        if self.use_local:
            path = f"./{phrase_tmp}.html"
            #checks if path exist
            if not os.path.exists(path):
                return False
            #if yes then we read it
            with open(path , 'r' , encoding='utf-8') as file:
                htmlText = file.read()
            soup = BeautifulSoup(htmlText , "html.parser")
        else:
            #goes to SiteDownloader func to get the soup-ed html page
            URL_tmp = self.link + "/" + phrase_tmp
            soup = SiteDownloader(URL_tmp)

        if soup is None or '':
            return False
        #get the first div
        div = soup.find("div", class_="mw-parser-output")
        if div is None:
            print(f"No article {phrase} on site {self.link}")
            return False
        para = div.find("p").get_text()
        print(para)
        return para


    def table(self, phrase, number, first_row_header=False):
        # check if the args are correct
        if phrase is None:
            return False
        phrase_tmp = phrase.replace(" ", "_")
        URL_tmp = self.link + "/" + phrase_tmp
        if self.use_local:
            path = f"./{phrase_tmp}.html"
            if not os.path.exists(path):
                return False
            with open(path, 'r', encoding='utf-8') as file:
                htmlText = file.read()
            soup = BeautifulSoup(htmlText, "html.parser")
        else:
            soup = SiteDownloader(URL_tmp)

        tables = soup.find_all("table")
        if number > len(tables):
            print(f"Na stronie {URL_tmp} nie ma tylu tabel")
            return False

        table = tables[number - 1]
        rows = table.find_all("tr")
        tableForPandas = []
        for row in rows:
            dataRow = row.find_all(["td", "th", "thead"])
            dataRowText = [data.get_text().strip() for data in dataRow]
            tableForPandas.append(pd.Series(dataRowText))

        df = pd.DataFrame(tableForPandas)

        if first_row_header:
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
        df = df.set_index(df.columns[0])
        print(df)

        setOfWords = {}
        for i in range(first_row_header, len(tableForPandas)):
            for j in range(1, len(tableForPandas[i])):
                data = tableForPandas[i][j]
                if data in setOfWords:
                    setOfWords[data] += 1
                else:
                    setOfWords[data] = 1

        df2 = pd.DataFrame(setOfWords.items(), columns=['word', 'count'])
        print(df2)

        with open(f"{phrase_tmp}.csv", "w", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerows(tableForPandas)
        return df, df2

    def count_words(self, phrase):
        if phrase is None:
            return False
        phrase_tmp = phrase.replace(" ", "_")

        if self.use_local:
            path = f"./{phrase_tmp}.html"
            if not os.path.exists(path):
                return False

            with open(path, 'r' , encoding='utf-8') as file:
                htmlText = file.read()
            soup = BeautifulSoup(htmlText , "html.parser")
        else:
            URL_tmp = self.link + "/" + phrase_tmp
            soup = SiteDownloader(URL_tmp)

        if soup is None:
            return False
        self.language = soup.find('html').get('lang')
        text = soup.find("div", class_="mw-parser-output").get_text(
            strip=True, separator=" "
        )
        words = getWordsFromText(text)

        # deleting hyperlinks
        i = 0
        while i < len(words):
            word = words[i]
            if word == "" or word[-1] == "-":
                words.pop(i)
            elif len(word) >= 4 and word[:4] == "http":
                words.pop(i)
            elif len(word) >= 3 and word[:3] == "www":
                words.pop(i)
            else:
                i += 1

        setOfWords = {}
        for word in words:
            if word not in setOfWords:
                setOfWords[word] = 1
            else:
                setOfWords[word] += 1
        with open("../word-count.json", "w", encoding="utf-8") as file:
            json.dump(setOfWords, file, ensure_ascii=False)
        self.used_count_words = True
        return True

    def analyze_relative_word_frequency(self, mode, count, chart=None):
        if not self.used_count_words:
            return False
        if (
            mode not in {"article", "language"}
            or count < 0
            or (
                chart is not None
                and len(chart) < 4
                and chart[len(chart) - 4 : len(chart)] != ".png"
            )
        ):
            return False

        with open("../word-count.json", "r", encoding="utf-8") as file:
            siteData = json.load(file)
        setFrequencyLang = {}
        setFrequencyArticle = {}
        sumWords = 0
        mostFrequencyLang = wordfreq.word_frequency(
            wordfreq.top_n_list(n=1, lang=self.language)[0], self.language
        )

        for word in siteData:
            setFrequencyLang[word] = (
                wordfreq.word_frequency(word, lang=self.language) / mostFrequencyLang
            )
            sumWords += siteData[word]
        mostFrequencyArticle = max(siteData.values()) / sumWords

        for word in siteData:
            setFrequencyArticle[word] = (
                siteData[word] / sumWords
            ) / mostFrequencyArticle

        df1 = pd.DataFrame(
            {
                "word": setFrequencyLang.keys(),
                "frequency in wiki language": setFrequencyLang.values(),
            }
        )
        df2 = pd.DataFrame(
            {
                "word": setFrequencyArticle.keys(),
                "frequency in article": setFrequencyArticle.values(),
            }
        )
        pd.set_option(
            "display.float_format", "{:.4f}".format
        )  # wyswietlaj w zmiennoprzecinkowej , nie w naukowej

        df = pd.merge(df2, df1, on="word", how="inner")

        if mode == "article":
            df = df.sort_values("frequency in article", ascending=False)
        if mode == "language":
            df = df.sort_values("frequency in wiki language", ascending=False)

        df = df.head(count)
        print(df)

        if chart is None:
            return False

        df.set_index("word")[
            ["frequency in article", "frequency in wiki language"]
        ].plot(kind="bar", figsize=(10, 5))
        plt.title("Frequency of some words on Wiki")
        plt.ylabel("Frequency")
        plt.xticks(rotation=0)
        plt.savefig(chart)
        return True

    def auto_count_words(self, phrase, depth, wait):
        if phrase is None or depth < 0 or wait < 0:
            return
        # print(f"Jestem w {phrase}")
        # zasypiamy na wait sekund
        time.sleep(wait)
        if self.first:
            self.count_words(phrase)
            self.first = False
        else:
            with open("../word-count.json", "r", encoding="utf-8") as file:
                alreadyProcessdWords = json.load(file)


            if not self.first:
                self.count_words(phrase)

            with open("../word-count.json", "r", encoding="utf-8") as file:
                newWords = json.load(file)

            if self.first:
                self.first = False

            # merguje je
            for k, v in alreadyProcessdWords.items():
                if k in newWords:
                    newWords[k] += v
                else:
                    newWords[k] = v

            with open("../word-count.json", "w", encoding="utf-8") as file:
                json.dump(newWords, file, ensure_ascii=False)
            if depth == 0:
                return

        # szukamy hyperlączy
        soup = SiteDownloader(self.link + "/" + phrase)

        para = soup.find_all("p")
        hyperlinks = []
        for paragraph in para:
            tmp_links = paragraph.find_all("a")
            for link in tmp_links:
                if (
                    ("href" in link.attrs)
                    and (len(link["href"]) >= 6)
                    and (link["href"][:6] == "/wiki/")
                ):
                    hyperlinks.append(link["href"][6:])

        alreadyProcessed = []
        for hyperlink in hyperlinks:
            if hyperlink not in alreadyProcessed:
                alreadyProcessed.append(hyperlink)
                self.auto_count_words(hyperlink, depth - 1, wait)