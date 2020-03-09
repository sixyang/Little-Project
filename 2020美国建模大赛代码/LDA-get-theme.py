from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer as TFIV
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import string
from nltk.stem.porter import PorterStemmer


data = pd.read_csv(r'C:\Users\struggle、\Desktop\Problem_C_Data\hair_dryer.tsv',
                   header=0, delimiter="\t", quoting=3)         #读取数据

def load_stopword():
    '''加载停用词，加载符号和数字'''
    with open(r'C:\Users\struggle、\Desktop\sTone!\python\stopwords.txt') as f_stop:
        sw = [line.strip() for line in f_stop]
    for i in string.punctuation:
        sw.append(i)
    sw.extend(list(string.digits))
    return sw
    
import datetime
import time

data = pd.read_csv(r'C:\Users\struggle、\Desktop\Problem_C_Data\pacifier.tsv',
                   header=0, delimiter="\t", quoting=3) 

def sub(s1, s2):
    a = datetime.strptime(s1, '%m/%d/%Y')
    b = datetime.strptime(s2, '%m/%d/%Y')
    substitute = time.mktime(b.timetuple()) - time.mktime(a.timetuple())
    return substitute

def get_time(s):
    t = datetime.strptime(s, '%m/%d/%Y')
    t_tuple = t.timetuple()
    year = t_tuple[0]
    month = t_tuple[1]
    day = t_tuple[2]

    first_day = '3/2/2002'
    minus = sub(first_day, s)/86400
    return [year, month, day, minus]


def main(star_rating=1):
    # start = datetime.strptime(start_time, '%m/%d/%Y')
    # end = datetime.strptime(end_time, '%m/%d/%Y')
    
    review = data.review_body[data.star_rating==1]

    stop_words = load_stopword()
    texts = [[word for word in line.strip().lower().split() if word not in stop_words] for line in review]  #去除符号，数字，停用词

    temp = []
    for i in texts:
        temp.append(' '.join(i))
    print('词语处理完成！')

    '''TF-idf处理数据'''
    n_features = 1000                                               #限定有多少个特征
    tf_vectorizer = TFIV(strip_accents = 'unicode',
                                    max_features=n_features,
                                    stop_words='english',
                                    max_df = 0.5,
                                    min_df = 10)                    #建立TFidf向量化模型

    tf = tf_vectorizer.fit_transform(temp)              #使用模型向量化每一句话

    '''LDA'''
    from sklearn.decomposition import LatentDirichletAllocation     #导入LDA
    n_topics = 5                                                    #一共有多少个主题
    lda = LatentDirichletAllocation(n_components=n_topics, max_iter=50,
                                    learning_method='online',
                                    learning_offset=50.,
                                    random_state=0)                 #建立LDA模型
    lda.fit(tf)                                                     #拟合数据
    def print_top_words(model, feature_names, n_top_words):
        for topic_idx, topic in enumerate(model.components_):
            print("Topic #%d:" % topic_idx)
            print(" ".join([feature_names[i]
                            for i in topic.argsort()[:-n_top_words - 1:-1]]))
        print()                                                     #展示20个主题显示最好的结果
    n_top_words = 20

    tf_feature_names = tf_vectorizer.get_feature_names()            #获得那1000个特征的值
    print_top_words(lda, tf_feature_names, n_top_words)      

if __name__ == "__main__":
    main()                          