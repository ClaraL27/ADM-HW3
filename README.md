# ADM-HW3

<p align="center">
<img src="https://ilovevg.it/wp-content/uploads/2020/05/anime-e-manga-generi.jpg">
</p>

In this github repository we stored the files written for the third Homework of the ADM course.
### Team Members
* Clara Lecce
* Giulia Luciani
* Luca Mattei
* Zeeshan Asghar

### File and Scripts descriptions
1. __`main.ipynb`__:
   > this is the notebook which contains the executed parts of the points below of the homework:

         1. Data collection
            1.1 Get the list of animes
            1.2 Crawl animes
            1.3 Parse downloaded pages

         2. Search Engine
            2.1 Conjunctive query
               2.1.1 Create your index!
               2.1.2 Execute the query
            2.2 Conjunctive query & Ranking score
               2.2.1 Inverted index
               2.2.2 Execute the query

         3. Define a new score!

         5. Algorithmic question

2. __`functions.py`__:
> Python script in which we have written the useful functions to solve the questions.
      
      # 1 DATA COLLECTION
         # 1.1 Get the list of animes
         def get_link(url_link, file_txt);
         # 1.2 Crawl animes
         def crawl_html(start_index, stop_index=0);
         # 1.3 Parse downloaded pages
            # 1. Anime Name, String
            def get_title(soup);
            # 2. Anime Type, String
            def get_type(soup);
            # 3. Number of episode, Integer
            def get_num_ep(soup);
            # 4. Release and End Dates of anime, datetime format
            def get_dates(soup);
            # 5. Number of members, Integer
            def get_memb(soup);
            # 6. Score, Float
            def get_score(soup);
            # 7. Users, Integer
            def get_users(soup);
            # 8. Rank, Integer
            def get_rank(soup);
            # 9. Popularity, Integer
            def get_pop(soup);
            # 10. Synopsis, String
            def get_descr(soup);
            # 11. Related animes, List of strings
            def get_rel_an(soup);
            # 12. Characters, List of strings
            def get_char(soup);
            # 13. Voices, List of strings
            def get_voices(soup);
            # 14. Staff, List of strings
            def get_staff(soup);

      # 2 SEARCH ENGINE
         # 2.1 Conjunctive query
            def download();
            # function to stem the string given
            def text_mining(string);
            # function to create the vocabulary
            def create_vocab();
            
            # 2.1.1 Create your index!
               # function to create the inverted_index and stores it in a json file
               def invertedIndex();

         # 2.2 Conjunctive query & Ranking score
            # 2.2.1 Inverted index tf*idf
               # function to create the inverted_index_tfidf and stores it in a json file
               def invertedIndex_tfidf(vocabulary, inverted_index);
            # 2.2.2 Execute the query
               # function to take the first k documents
               def top_k_documents(query, k, inverted_index, inverted_index_tfidf, inverted_doc, vocabulary);
               # function to calculate the cosine similarity
               def search_similarity(query, inverted_index, inverted_index_tfidf, inverted_doc, vocabulary);


3. __`anime_links.txt`__:
> contains the links of the animes

4. __`vocabulary.json`__:
> contains the vocabulary of the words contained in all the anime descriptions (but parsed with nltk library).

5. __`inverted_index.json`__:
> contains the inverted index for the Search Engine 2.1

6. __`inverted_index_tfidf.json`__:
> contains the inverted index tfidf for the Search Engine 2.2

7. __`inverted_doc.json`__:
> contains the tfidf for every documents used for the cosine similarity