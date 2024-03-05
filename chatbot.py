from nltk import word_tokenize, sent_tokenize
import pickle
import nltk.corpus
from math import sqrt
import random

important_words = ['raskolnikov', 'moscow', 'russia', 'dostoevsky', 'pushkin', 'lent,' 'essays,' 'article', 'tolstoy', 'featuring', 'poet', 'developed', 'papers', 'collections', 'editions']
stopwords = nltk.corpus.stopwords.words('english')

kb_place = open('kb.pickle', 'rb')
kb = pickle.load(kb_place)
vocab = pickle.load(open('vocab.pickle', 'rb'))


class user:

    def __init__(self):
        self.likes = []
        self.dislikes = []
        self.other_things = []

user_base = pickle.load(open('users.pickle', 'rb'))



def vectorize(lines):
    vectors = []
    for line in lines:
        newline = word_tokenize(line)
        newline = [t.lower() for t in newline if t.isalpha() and t not in stopwords]
        vec = [newline.count(t) for t in vocab]
        vectors.append(vec)
    return vectors

def dotProduct(vec1, vec2):
    rolling_sum = 0
    for i, num in enumerate(vec1):
        rolling_sum += (num*vec2[i])
    return rolling_sum

def normalize(vector):
    rolling_sum = 0
    for num in vector:
        rolling_sum += num**2
    return sqrt(rolling_sum)

def cos_sim(vec1, vec2):
    dot_prod = dotProduct(vec1, vec2)
    denom = normalize(vec1)*normalize(vec2)
    if denom == 0: return 0
    return dot_prod/denom

def run():
    print('Chatbot: Hello user, I am a chatbot specifically trained on the golden age (19th Century) of Russian literature.\nI know best topics related to articles, essays, papers and collections written by Russian authors such as Dostoevsky, Pushkin and Tolstoy,\nas well as the themes and characters developed in them.')
    name = input("\nChatbot: May I have your full name?\n\nUser: ")

    # add user if not in the database
    if name not in user_base.keys():
        user_new = user()
        likes = input('Hello {}, as this is our first time chatting, I would like to ask you questions to get to know you better. \nPlease enter a list of your likes, such as hobbies or food, separated only by spaces:\n\nUser: '.format(name))
        user_new.likes = word_tokenize(likes)
        dislikes = input('\nChatbot: Please give me a list of your dislikes, this time also separated by spaces.\n\nUser: ')
        user_new.dislikes = word_tokenize(dislikes)
        other_things = input('\nChatbot: Great, is there anything else you would like me to know about you?\n\nUser: ')
        user_new.other_things = sent_tokenize(other_things)
        user_base[name] = user_new
        pickle.dump(user_base, open('users.pickle', 'wb'))

    user1 = user_base[name]
    print('Chatbot: Hello {}, is there anything in particular you would like to begin chatting about? Perhaps {} and how it relates to the Golden Age of Russian literature.\nWe will do our best to stay away from topics such as {}. If at any time you would like to exit, simply type exit.\n'.format(name, user1.likes[random.randint(0, len(user1.likes)-1)], user1.dislikes[random.randint(0, len(user1.dislikes)-1)]))




    stay = True
    while stay:
        query = input('{}: '.format(name))
        if query == 'exit':
            stay = False
            continue
        query_tokens = word_tokenize(query)
        query_tokens = [t.lower() for t in query_tokens if t.isalpha() and t not in stopwords]
        possible_returns = []
        for word in important_words:
            if word in query_tokens:
                possible_returns += kb[word]
        possible_returns += kb['random']

        best_response = None
        best_score = 0
        query_vector = [query_tokens.count(t) for t in vocab]
        response_vectors = vectorize(possible_returns)
        for i, vector in enumerate(response_vectors):
            score = cos_sim(query_vector, vector)
            if score > best_score:
                best_score = score
                best_response = possible_returns[i]
        print('Chatbot: {}'.format(best_response))


run()