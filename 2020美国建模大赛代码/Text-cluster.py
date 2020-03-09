from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import re
from bs4 import BeautifulSoup
import random
import pandas as pd
import string


star = 1
clusters = 7
data = pd.read_csv(r'C:\Users\struggle、\pacifier.csv')

def load_stopword():
    '''加载停用词，加载符号和数字'''
    with open(r'C:\Users\struggle、\Desktop\sTone!\python\stopwords.txt') as f_stop:
        sw = [line.strip() for line in f_stop]
    for i in string.punctuation:
        sw.append(i)
    sw.extend(list(string.digits))
    return sw

def review_to_wordlist(review):
    '''把评论转成词序列'''
    review_text = BeautifulSoup(review, "html.parser").get_text()
    review_text = re.sub("[^a-zA-Z]", " ", review_text)
    words = review_text.lower().split()
    return words

def main(): 
    review = data.review_body[data.star_rating==star]
    stop_words = load_stopword()
    train_data = []
    review.index = range(len(review))
    for i in range(0, len(review)):
        train_data.append(" ".join(review_to_wordlist(review[i])))
    texts = [[word for word in line.strip().lower().split() if word not in stop_words] for line in train_data]  #去除符号，数字，停用词

    temp = []
    for i in texts:
        temp.append(' '.join(i))
    print('词语处理完成！')

    vectorizer = CountVectorizer()
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(vectorizer.fit_transform(temp))

    word = vectorizer.get_feature_names()
    print("word feature length: {}".format(len(word)))

    tfidf_weight = tfidf.toarray()

    kmeans = KMeans(n_clusters=clusters)
    kmeans.fit(tfidf_weight)

    print(kmeans.cluster_centers_)
    print('聚类完成！')

    d = data[data.star_rating==star].copy()
    d['category'] = kmeans.labels_


    ret = pd.DataFrame()
    for i in range(7):
        #随机挑选n条评论来看情况
        temp = d[d['category'] == i].review_body
        l = 10
        temp.index = range(len(temp))
        flag = True

        # while flag:
        s = [random.randint(0, len(temp)) for i in range(l)]
        # if len(set(s)) == len(s):
        #     flag = False
        a = temp[s].copy()
        a.index = range(len(a))
        ret[i] = a
    ret.to_csv('review{}.csv'.format(star))

if __name__ == "__main__":
    main()