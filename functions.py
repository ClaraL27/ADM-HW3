from bs4 import BeautifulSoup
from tqdm import tqdm
import requests
import os
import re
from datetime import datetime
import nltk
from nltk.stem import PorterStemmer
import csv
import json
import pandas as pd
import numpy as np
import heapq

# 1 DATA COLLECTION
# 1.1 Get the list of animes
# we are using the get response request to "download" the page,
# and then we use the library BeautifulSoup to get the urls needed.
def get_link(url_link, file_txt):
    anime = []
    for page in tqdm(range(0, 400)):
        url = url_link + str(page * 50)
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', class_='hoverinfo_trigger fl-l ml12 mr8'):
            if type(link.get('id')) == str:
                anime.append(link.get('href'))

    with open(file_txt, 'w', encoding = 'utf-8') as f:
        for link_l in anime:
            f.write(link_l + str('\n'))


# 1.2 Crawl animes
def crawl_html(start_index, stop_index=0):
    with open('anime_links.txt', 'r', encoding='utf-8') as f:
        urls = f.read().splitlines()[start_index:]
        if stop_index != 0:
            urls = urls[:stop_index-start_index]
        else:
            stop_index = 19130
        for i, url in zip(tqdm(range(start_index, stop_index)), urls):
            # headers contains every kind of user agent that could open the url page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.35 Safari/537.36 QIHU 360SE'
            }

            anime_page = requests.get(url, headers=headers)

            # in case something bad happen
            if anime_page.status_code != 200:
                raise Exception(f"Something really bad happened. Current index is {i}")

            pages = i//50 + 1
            path = f"pages/page_{pages}"

            with open(f'{path}/article_{i+1}.html', 'w', encoding='utf-8') as f:
                f.write(anime_page.text)


# 1.3 Parse downloaded pages
# to get the information, we checked the html pages to see
# where the information was stored, and after that, we
# use BeautifulSoup to get it!
# sometimes we use a try, except because the information is
# not present and it could return an exception error
# 1. Anime Name, String
def get_title(soup):
    title = soup.find('meta', {'property': 'og:title'})
    return str(title.get('content'))


# 2. Anime Type, String
def get_type(soup):
    an_type = soup.find_all('div', class_='spaceit_pad')
    for tag in an_type:
        type_info = tag.text.split()
        if type_info[0] == "Type:":
            return str(type_info[1])


# 3. Number of episode, Integer
def get_num_ep(soup):
    epis = soup.find_all('div', class_='spaceit_pad')
    for tag in epis:
        ep_info = tag.text.split()
        if ep_info[0] == "Episodes:":
            try:
                return int(ep_info[1])
            except ValueError:
                return ''


# 4. Release and End Dates of anime, datetime format
def get_dates(soup):
    date = soup.find_all('div', class_='spaceit_pad')
    for tag in date:
        date_info = tag.text.split()
        if date_info[0] == "Aired:":
            only_date = date_info[1:]
            # this condition is for the anime that do not have any Release or End Dates
            if "Not available" in " ".join(only_date) or "Not Available" in " ".join(only_date):
                return ['', '']
            data = []
            for string in only_date:
                # we use a regex function to get only the needed dates
                # Months: 3 letters or 0, Day: 2 numbers or 0, Year: 4 numbers
                # sometimes the end date is not in there
                prova = re.findall(r'[a-zA-Z]{0,3}[0-9]{0,2}[0-9]{0,4}', string)
                data.append(prova[0])
            data = list(filter(None, data))
            first_date_list = data
            second_date_list = []
            first_date = ''
            second_date = ''
            # if there is the end date, also there is a 'to' string
            # to divide the release from the end date
            if 'to' in data:
                ind = data.index('to')
                first_date_list = data[:ind]
                second_date_list = data[ind+1:]

            first_count = len(first_date_list)
            second_count = len(second_date_list)
            if first_count == 3:
                first_date = " ".join(first_date_list)
                first_date = datetime.strptime(first_date, '%b %d %Y').date()
            if first_count == 2:
                first_date = " ".join(first_date_list)
                first_date = datetime.strptime(first_date, '%b %Y').date()
            if first_count == 1:
                first_date = datetime.strptime(first_date_list[0], '%Y').date()
            if second_count == 3:
                second_date = " ".join(second_date_list)
                second_date = datetime.strptime(second_date, '%b %d %Y').date()
            if second_count == 2:
                second_date = " ".join(second_date_list)
                second_date = datetime.strptime(second_date, '%b %Y').date()
            if second_count == 1:
                second_date = datetime.strptime(second_date_list[0], '%Y').date()

            return [first_date, second_date]


# 5. Number of members, Integer
def get_memb(soup):
    members = soup.find('span', class_="numbers members")
    try:
        return int(''.join(re.findall(r'\d+', members.text)))
    except ValueError:
        return ''


# 6. Score, Float
def get_score(soup):
    score = soup.find('div', class_="fl-l score")
    try:
        return float(score.find('div').text)
    except ValueError:
        return ''


# 7. Users, Integer
def get_users(soup):
    users = soup.find('div', class_="fl-l score")
    try:
        return int(''.join(re.findall(r'\d+', users.get('data-user'))))
    except ValueError:
        return ''


# 8. Rank, Integer
def get_rank(soup):
    rank = soup.find('span', class_='numbers ranked')
    try:
        return int(re.findall(r'\d+', rank.text)[0])
    except IndexError:
        return ''


# 9. Popularity, Integer
def get_pop(soup):
    pop = soup.find('span', class_='numbers popularity')
    try:
        return int(re.findall(r'\d+', pop.text)[0])
    except IndexError:
        return ''


# 10. Synopsis, String
def get_descr(soup):
    descr = soup.find('p', itemprop="description")
    try:
        if "No synopsis" not in descr.text:
            if descr.find('span'):
                span = descr.find('span')
                return descr.text.replace(span.text, '')
            else:
                return descr.text
        else:
            return ''
    except:
        return ''


# 11. Related animes, List of strings
def get_rel_an(soup):
    relat = soup.find('table', class_="anime_detail_related_anime")
    try:
        list_rel = []
        for anim in relat.find_all('a'):
            if anim.text not in list_rel:
                list_rel.append(anim.text)
        if len(list_rel) > 0:
            return list_rel
        else:
            return ''
    except AttributeError:
        return ''


# 12. Characters, List of strings
def get_char(soup):
    all_chars = soup.find_all('h3', class_="h3_characters_voice_actors")
    if len(all_chars) == 0:
        return ''
    chars = []
    for char in all_chars:
        chars.append(char.text)
    return list(dict.fromkeys(chars))


# 13. Voices, List of strings
def get_voices(soup):
    all_voices = soup.find_all('td', class_="va-t ar pl4 pr4")
    if len(all_voices) == 0:
        return ''
    voices = []
    for voice in all_voices:
        voices.append(voice.find('a').text)
    return list(dict.fromkeys(voices))


# 14. Staff, List of strings
def get_staff(soup):
    find_staff = soup.find_all('div', class_='detail-characters-list clearfix')
    if len(find_staff) == 1:
        find_staff = find_staff[0]
    elif len(find_staff) == 2:
        find_staff = find_staff[1]
    else:
        return ''
    staffs = []
    for elem in find_staff.find_all('a'):
        staff = ' '.join(elem.text.split())
        if staff != '':
            staffs.append(staff)

    staffs_type = []
    for staff_type in find_staff.find_all('small'):
        staffs_type.append(staff_type.text)

    final_staff = []
    for i, j in zip(staffs, staffs_type):
        final_staff.append([i, j])

    return final_staff


# 2 SEARCH ENGINE
# 2.1 Conjunctive query
def download():
    nltk.download('punkt')
    nltk.download('stopwords')


# function to stem the string given
# input: string of the text
# output: list of every word stemmed in the query
def text_mining(string):
    # gather all the stopwords
    stop_words = set(nltk.corpus.stopwords.words('english'))
    # tokenization
    tokens = nltk.word_tokenize(string.lower())
    # remove punctuations and numbers and then word stemming
    res_tok = [PorterStemmer().stem(word) for word in tokens if word.isalpha() and word not in stop_words]
    return res_tok


# function to create the vocabulary
# key -> term (string)
# value -> term_id (integer)
def create_vocab():
    vocabulary = dict()
    for i in tqdm(range(1, 384)):
        path = f'pages_tsv/page_{i}/'
        for file in os.listdir(path):
            tsv_file = open(path+file, 'r', encoding='utf-8')
            anime = csv.DictReader(tsv_file, delimiter='\t')
            descr = anime.__next__()['animeDescription']

            for word in text_mining(descr):
                if word not in vocabulary.keys():
                    vocabulary[word] = len(vocabulary)

    file_voc = open("vocabulary.json", "w", encoding='utf-8')
    json.dump(vocabulary, file_voc, ensure_ascii=False)
    file_voc.close()

# 2.1.1 Create your index!
# function to create the inverted_index and stores it in a json file
# key -> term_id (unique integer)
# value -> list of documents which contain the term
def invertedIndex():

    inverted_index = dict()

    voc_json = open('vocabulary.json', 'r', encoding='utf-8')
    vocabulary = json.load(voc_json)

    # creating an empty inverted_index dictionary
    for word in vocabulary:
        inverted_index[vocabulary[word]] = []

    for i in tqdm(range(1, 384)):
        path = f'pages_tsv/page_{i}/'

        for file in os.listdir(path):
            tsv_file = open(path+file, 'r', encoding='utf-8')
            document_id = 'document_' + (''.join(re.findall(r'\d+', file)))
            anime = csv.DictReader(tsv_file, delimiter='\t')
            descr = anime.__next__()['animeDescription']

            for word in text_mining(descr):
                if document_id not in inverted_index[vocabulary[word]]:
                    inverted_index[vocabulary[word]].append(document_id)

    file_inv_ind = open("inverted_index.json", "w", encoding='utf-8')
    json.dump(inverted_index, file_inv_ind, ensure_ascii=False)
    file_inv_ind.close()


# 2.2 Conjunctive query & Ranking score
# 2.2.1 Inverted index tf*idf
# function to create the inverted_index_tfidf and stores it in a json file
# key -> term_id (unique integer)
# value -> list of tuples of (document_id, tfidf_{term, document_id})
def invertedIndex_tfidf(vocabulary, inverted_index):

    inverted_index_tfidf = dict()
    inverted_doc = dict()

    n_doc = 0
    for i in range(1, 384):
        path = f'pages_tsv/page_{i}/'
        n_doc += len(os.listdir(path))

    # creating an empty inverted_index_tfidf dictionary
    for word in vocabulary:
        inverted_index_tfidf[vocabulary[word]] = []

    for i in tqdm(range(1, 384)):
        path = f'pages_tsv/page_{i}/'

        for file in os.listdir(path):
            tsv_file = open(path+file, 'r', encoding='utf-8')
            document_id = 'document_' + (''.join(re.findall(r'\d+', file)))
            anime = csv.DictReader(tsv_file, delimiter='\t')
            descr = anime.__next__()['animeDescription']
            descr = text_mining(descr)

            # count how many word has the document
            n_descr = len(descr)
            inverted_doc[document_id] = 0
            # to store the words already used
            word_counted = []
            for word in descr:
                tf = descr.count(word) / n_descr
                idf = np.log10(n_doc/len(inverted_index[str(vocabulary[word])]))
                tfidf = tf * idf
                inverted_doc[document_id] += np.square(tfidf)
                if word not in word_counted:
                    inverted_index_tfidf[vocabulary[word]].append((document_id, tfidf))
                    word_counted.append(word)

    file_inv_term = open("inverted_index_tfidf.json", "w", encoding='utf-8')
    json.dump(inverted_index_tfidf, file_inv_term, ensure_ascii=False)
    file_inv_term.close()

    file_inv_doc = open("inverted_doc.json", "w", encoding='utf-8')
    json.dump(inverted_doc, file_inv_doc, ensure_ascii=False)
    file_inv_doc.close()


# 2.2.2 Execute the query
# output:
# final_doc contains only the first k documents: key -> document_id
#                                                value -> cos_sim
# result: key -> document_id
#         value -> cos_sim
def top_k_documents(query, k, inverted_index, inverted_index_tfidf, inverted_doc, vocabulary):
    # we are taking the first k similar documents to the query using heapq
    result, heap = search_similarity(query, inverted_index, inverted_index_tfidf, inverted_doc, vocabulary)
    heap_k = heapq.nlargest(k, heap)
    final_doc = dict()
    for i in range(len(heap_k)):
        pos = list(result.values()).index(heap_k[i])
        final_doc[list(result)[pos]] = result[list(result)[pos]]
    return final_doc, result


# this function calculates the cosine similarity between a document and a query
# more explanation abaut it on the main notebook
def search_similarity(query, inverted_index, inverted_index_tfidf, inverted_doc, vocabulary):

    # saving the inverted_index of the query
    # creating index query dictionary
    query_dict_2 = dict()
    for word in query:
        if word in vocabulary.keys():
            query_dict_2[vocabulary[word]] = inverted_index[str(vocabulary[word])]

    query_index_2 = list(query_dict_2.keys())

    # searching for the documents requested from the query
    doc_list_2 = set(query_dict_2[query_index_2[0]])

    for query_word in query_index_2[1:]:
        doc_list_2.intersection_update(query_dict_2[query_word])

    # create the heap list in order to take the first k documents
    heap = list()
    heapq.heapify(heap)
    result, numerator = dict(), dict()

    #creating the numerator dictionary
    for word in query:
        if word in vocabulary.keys():
            for elem in inverted_index_tfidf[str(vocabulary[word])]:
                if elem[0] in doc_list_2:
                    if elem[0] not in numerator:
                        numerator[elem[0]] = elem[1]
                    else:
                        numerator[elem[0]] += elem[1]

    for document in doc_list_2:
        cos_sim = numerator[document]/(np.sqrt(inverted_doc[document]) * np.sqrt(len(query)))
        result[document] = cos_sim
        heapq.heappush(heap, cos_sim)

    return result, heap