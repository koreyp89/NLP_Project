import math
import re
import pickle
from nltk.corpus import stopwords
import nltk.corpus
import requests.compat
import requests
import os
from bs4 import BeautifulSoup
from nltk import sent_tokenize
import string
from nltk.corpus import stopwords
from nltk import word_tokenize

important_words = ['raskolnikov', 'moscow', 'russia', 'dostoevsky', 'pushkin', 'lent,' 'essays,' 'article', 'tolstoy', 'featuring', 'poet', 'developed', 'papers', 'collections', 'editions']

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
urls = ['https://www.google.com/search?q=Russian+Literature&sca_esv=77f0734d9bd4c6dc&sxsrf=ACQVn08VlNWZBQnh5ZJMzT0hf53qn45RDw%3A1708302584856&ei=-KDSZc_zM52xqtsPjcWW6AM&ved=0ahUKEwjPz_SFk7aEAxWdmGoFHY2iBT0Q4dUDCBA&uact=5&oq=Russian+Literature&gs_lp=Egxnd3Mtd2l6LXNlcnAiElJ1c3NpYW4gTGl0ZXJhdHVyZTINEAAYgAQYigUYQxixAzILEAAYgAQYigUYkQIyCxAAGIAEGIoFGJECMgsQABiABBiKBRiRAjIFEAAYgAQyChAAGIAEGIoFGEMyBRAAGIAEMgUQABiABDIKEAAYgAQYigUYQzIFEAAYgARInxZQAFjeFXAAeAGQAQCYAUSgAbIHqgECMTi4AQPIAQD4AQHCAgQQIxgnwgIKECMYgAQYigUYJ8ICDRAuGIAEGIoFGEMY1ALCAgsQABiABBixAxiDAcICEBAuGEMYgwEYsQMYgAQYigXCAgoQLhiABBiKBRhDwgIQEAAYgAQYFBiHAhixAxiDAcICCxAuGIAEGLEDGIMBwgIIEC4YgAQYsQPCAhYQLhiABBiKBRhDGLEDGIMBGMcBGNEDwgIKEAAYgAQYFBiHAsICExAuGIAEGIoFGEMYsQMYgwEY1ALCAggQABiABBixAw&sclient=gws-wiz-serp#ip=1',
        'https://www.google.com/search?q=Russian+Literature+Golden+age&sca_esv=77f0734d9bd4c6dc&sxsrf=ACQVn08i-hF6UJQhRSFffN21jeNHSGfK6A%3A1708302645786&ei=NaHSZaG_L8GvqtsPybiQgAs&ved=0ahUKEwjhrfuik7aEAxXBl2oFHUkcBLAQ4dUDCBA&uact=5&oq=Russian+Literature+Golden+age&gs_lp=Egxnd3Mtd2l6LXNlcnAiHVJ1c3NpYW4gTGl0ZXJhdHVyZSBHb2xkZW4gYWdlMgUQABiABDILEAAYgAQYigUYhgMyCxAAGIAEGIoFGIYDMgsQABiABBiKBRiGAzILEAAYgAQYigUYhgNIkxhQAFjBF3ACeAGQAQCYAUmgAaIGqgECMTO4AQPIAQD4AQHCAgoQABiABBiKBRhDwgIKEC4YgAQYigUYQ8ICBRAuGIAEwgIKEAAYgAQYFBiHAsICBhAAGBYYHsICBRAhGKAB&sclient=gws-wiz-serp',
        'https://www.google.com/search?q=dostoevsky&sca_esv=77f0734d9bd4c6dc&sxsrf=ACQVn0848yxh9pA61NIYGHyAslc9Kwv_mg%3A1708302681658&ei=WaHSZY3eJ9SHqtsP-eWNgAc&ved=0ahUKEwjN7oi0k7aEAxXUg2oFHflyA3AQ4dUDCBA&uact=5&oq=dostoevsky&gs_lp=Egxnd3Mtd2l6LXNlcnAiCmRvc3RvZXZza3kyBBAjGCcyDhAuGIAEGIoFGJECGLEDMgoQABiABBiKBRhDMgoQABiABBiKBRhDMg4QABiABBiKBRiRAhixAzINEAAYgAQYigUYQxixAzILEC4YgAQYigUYkQIyDhAuGIAEGIoFGJECGNQCMgoQABiABBiKBRhDMg0QLhiABBgUGIcCGNQCSO0MUABYvQtwAHgBkAEAmAFcoAHpBKoBAjEwuAEDyAEA-AEBwgIKECMYgAQYigUYJ8ICDhAuGIAEGIoFGLEDGIMBwgIREC4YgAQYsQMYgwEYxwEY0QPCAggQLhiABBixA8ICBRAAGIAEwgIKEC4YQxiABBiKBcICChAuGIAEGIoFGEPCAg4QLhiABBjHARivARiOBcICFBAuGIMBGK8BGMcBGLEDGIAEGI4FwgITEC4YgAQYigUYQxixAxjHARjRA8ICDRAuGIAEGIoFGEMYsQM&sclient=gws-wiz-serp']


def get_links(urls, headers):
    links = []
    counter = 0

    while urls and counter < 25:
        url = urls.pop(0)
        try:
            req = requests.get(url, headers=headers) # make sure that URL is good
        except Exception: # Skip if bad URL
            continue

        soup = BeautifulSoup(req.content, 'html.parser')

        match = re.search('google', url)
        if not match: #scrape page
            text = [p.text for p in soup.select('p')]

            # Check if anything was scraped
            if len(text) > 0:
                l = ''.join(let for let in url if let.isalnum())
                str = 'raw/raw_text.{}.txt'.format(l[-20:])
                f = open(str, 'w', encoding="utf-8", errors='ignore')
                for t in text:
                    f.write(t)
                counter += 1
                f.close()


        for link in soup.find_all('a'): # Get all of the links on site.

            l = link.get('href')

            # if the link is a file or a shortcut to a part of the page then continue
            if not l or (len(l) > 4 and l[-4] == '.') or l[0] == '#':
                continue

            # Below we have regex pattern matching code to eliminate bad websites
            match = re.search('google', l)
            if match:
                continue
            match = re.search('tel', l)
            if match:
                continue
            match = re.search('twitter', l)
            if match:
                continue
            match = re.search('facebook', l)
            if match:
                continue
            match = re.search('youtube', l)
            if match:
                continue
            match = re.search('apple', l)
            if match:
                continue
            match = re.search('addtoany', l)
            if match:
                continue
            match = re.search('block', l)
            if match:
                continue
            match = re.search('linkedin', l)
            if match:
                continue
            match = re.search('instagram', l)
            if match:
                continue
            match = re.search('javascript', l)
            if match:
                continue
            match = re.search('academic', l)
            if match:
                continue
            match = re.search('ncbi', l)
            if match:
                continue
            match = re.search('jpeg', l)
            if match:
                continue
            match = re.search('mailto', l)
            if match:
                continue

            if l[:4] != 'http': # the link is on site
                if l in urls or len(l) == 1: # do not collect duplicates
                    continue
                address = requests.compat.urljoin(url, l) # get the full address, not just the file location
                urls.append(address)
            else: # We do not have to do anything because the full address is available
                if l in urls:
                    continue
                urls.append(l)



    return links




def get_clean_files():
    directory = 'raw'
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        file = open(f, 'r', encoding="utf-8", errors='ignore')

        text = file.read()
        text = text.strip()
        # Replace missing spaces
        text = text.replace('.', '. ')
        text = text.replace('!', '! ')
        text = text.replace('?', '? ')

        sentences = sent_tokenize(text)

        # getting rid of characters that do not form sentences
        good_chars = string.ascii_letters + string.digits + string.punctuation + ' '
        sentences = [''.join(c for c in x if c in good_chars) for x in sentences]
        print(sentences)

        clean_loc = os.path.join('clean', filename)
        out = open(clean_loc, 'w')
        for sent in sentences:
            out.write(sent + '\n') # write each sentence to a new line

def tf():
    list_of_tf_dicts = []
    stopwors = stopwords.words('english')
    for file in os.listdir('clean'):
        tf_dict = {}
        f = open(os.path.join('clean/', file), 'r')
        text = f.read()
        tokens = word_tokenize(text)
        tokens = [w.lower() for w in tokens if w.isalpha() and w not in stopwors] # remove the stopwords and punctuation

        # get term frequencies
        for t in tokens:
            if t in tf_dict:
                tf_dict[t] += 1
            else:
                tf_dict[t] = 1

        # normalize the term frequencies
        for t in tf_dict.keys():
            tf_dict[t] = tf_dict[t]/len(tokens)

        list_of_tf_dicts.append(tf_dict)

    # make a vocabulary of all the documents
    vocab = set()
    for dictionary in list_of_tf_dicts:
        dict_set = set(dictionary.keys())
        vocab = vocab.union(dict_set)
    vocab = sorted(list(vocab))

    return list_of_tf_dicts, vocab # return the frequency dictionaries

def idf(vocab, tf_dicts):
    idf_dict = {}

    vocab_by_document = [d.keys() for d in tf_dicts]

    for term in vocab:
        temp = ['x' for voc in vocab_by_document if term in voc]
        idf_dict[term] = math.log(1+len(tf_dicts)) / (1+len(temp))

    return idf_dict


def tf_idf(tfs, idf):
    list_of_tfidf_dicts = []
    for tf in tfs:
        tf_idf = {}
        for t in tf.keys():
            tf_idf[t] = tf[t] * idf[t]
        list_of_tfidf_dicts.append(tf_idf)

    dct = dict()
    for dic in list_of_tfidf_dicts:
        for term in dic.keys():
            if term not in dct:
                dct[term] = dic[term]
            else:
                maximum = max(dct[term], dic[term])
                dct[term] = maximum
    list =  sorted(dct, key=dct.get, reverse=True) # sort by the values in reverse
    see = dict()
    for term in list[:200]:
        see[term] = dct[term]
    return list

def build_kb():

    kb = {}
    for word in important_words:
        kb[word] = []
    kb['random'] = []
    pickleplace = open('kb.pickle', 'wb')
    for file in os.listdir('clean'):
        last_used_term = 'random'
        f = open(os.path.join('clean/', file))
        lines = f.readlines()
        stopwors = stopwords.words('english')
        for line in lines:
            inserted = False
            tokens = word_tokenize(line)
            tokens = [w.lower() for w in tokens if
                      w.isalpha() and w not in stopwors]  # remove the stopwords and punctuation
            for word in important_words:
                if word in tokens:
                    kb[word].append(line)
                    last_used_term = word
            if not inserted:
                kb[last_used_term].append(line)
    pickle.dump(kb, pickleplace)





def run():
    #get_links(urls, headers)
    #get_clean_files()
    tf_dictionaries, vocab = tf()
    vocabpickle = open('vocab.pickle','wb')
    pickle.dump(vocab, vocabpickle)
    idf_dict = idf(vocab, tf_dictionaries)
    tf_id = tf_idf(tf_dictionaries, idf_dict)
    print('The top 40 tf_idf terms for all documents are:')
    print(tf_id[:40])
    build_kb()

if __name__ == "__main__":
    run()
