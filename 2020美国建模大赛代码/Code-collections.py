# import numpy as np
# from gensim import corpora, models, similarities
# from pprint import pprint
# import time
# import pandas as pd
 
 
'''LDA分词'''
# def load_stopword():      
#     with open('./stopwords.txt') as f_stop:
#         sw = [line.strip() for line in f_stop]
#     return sw
 
# def load_words(path):
#     data = pd.read_csv(path, delimiter='\t')
#     return data.review_body
 
# if __name__ == '__main__':
 
    # print('1.初始化停止词列表 ------')
    # # 开始的时间
    # t_start = time.time()
    # # 加载停用词表
    # stop_words = load_stopword()

    # print('2.开始读入语料数据 ------ ')
    # # 读入语料库
    # f = load_words(r'C:\Users\struggle、\Desktop\Problem_C_Data\hair_dryer.tsv')
    # # 语料库分词并去停用词
    # texts = [[word for word in line.strip().lower().split() if word not in stop_words] for line in f]

    # print('读入语料数据完成，用时%.3f秒' % (time.time() - t_start))
    # M = len(texts)
    # print('文本数目：%d个' % M)

    # print('3.正在建立词典 ------')
    # # 建立字典
    # dictionary = corpora.Dictionary(texts)
    # V = len(dictionary)

    # print ('4.正在计算文本向量 ------')
    # # 转换文本数据为索引，并计数
    # corpus = [dictionary.doc2bow(text) for text in texts]

    # print ('5.正在计算文档TF-IDF ------')
    # t_start = time.time()
    # # 计算tf-idf值
    # corpus_tfidf = models.TfidfModel(corpus)[corpus]
    # print ('建立文档TF-IDF完成，用时%.3f秒' % (time.time() - t_start))

    # print ('6.LDA模型拟合推断 ------')
    # # 训练模型
    # num_topics = 30
    # t_start = time.time()
    # lda = models.LdaModel(corpus_tfidf, num_topics=num_topics, id2word=dictionary,
    #                         alpha=0.01, eta=0.01, minimum_probability=0.001,
    #                         update_every = 1, chunksize = 100, passes = 1)
    # print('LDA模型完成，训练时间为\t%.3f秒' % (time.time() - t_start))


'''别人的文本相似度'''
# from gensim import corpora, models, similarities
# import jieba
# text1 = '无痛人流并非无痛'
# text2 = '北方人流浪到南方'
# texts = [text1, text2]
# keyword = '无痛人流'
# texts = [jieba.lcut(text) for text in texts]
# dictionary = corpora.Dictionary(texts)
# num_features = len(dictionary.token2id)
# corpus = [dictionary.doc2bow(text) for text in texts]
# tfidf = models.TfidfModel(corpus)
# new_vec = dictionary.doc2bow(jieba.lcut(keyword))
# # 相似度计算
# index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features)
# print('\nTF-IDF模型的稀疏向量集：')
# for i in tfidf[corpus]:
#     print(i)
# print('\nTF-IDF模型的keyword稀疏向量：')
# print(tfidf[new_vec])
# print('\n相似度计算：')
# sim = index[tfidf[new_vec]]
# for i in range(len(sim)):
#     print('第', i+1, '句话的相似度为：', sim[i])


'''时间处理··'''
# import pandas as pd
# import datetime
# import time

# data = pd.read_csv(r'C:\Users\struggle、\Desktop\Problem_C_Data\pacifier.tsv',
#                    header=0, delimiter="\t", quoting=3) 

# def sub(s1, s2):
#     a = datetime.strptime(s1, '%m/%d/%Y')
#     b = datetime.strptime(s2, '%m/%d/%Y')
#     substitute = time.mktime(b.timetuple()) - time.mktime(a.timetuple())
#     return substitute

# def get_time(s):
#     t = datetime.strptime(s, '%m/%d/%Y')
#     t_tuple = t.timetuple()
#     year = t_tuple[0]
#     month = t_tuple[1]
#     day = t_tuple[2]

#     first_day = '4/27/2003'
#     minus = sub(first_day, s)/86400
#     return [year, month, day, minus]

# date = []
# for i in data.review_date:
#     date.append(get_time(i))
# year = [i[0] for i in date]
# month = [i[1] for i in date]
# day = [i[2] for i in date]
# sub = [i[3] for i in date]

# data['year'] = year
# data['month'] = month
# data['day'] = day
# data['sub'] = sub

# data.to_csv('pacifier.csv')

'''年，月，日画图'''
date = data.groupby(['review_date']).size()
plt.bar(date.index, date)
plt.show()
    
month = data.groupby(['month']).size()
plt.bar(month.index, month)
plt.show()

year = data.groupby(['year']).size()
plt.bar(year.index, year)
plt.show()

year_month = data.groupby(['year', 'month']).size()
i = []
for k in year_month.index:
    i.append(str(k[0])+'-'+str(k[1]))
plt.xticks(rotation=90,fontsize=5)
plt.bar(i, year_month, color='gold')
plt.show()


'''商品id，parent，title聚合与评星聚合的图像'''
def review_Value(product):
    f2=0
    f1=0
    k1=0.3
    sr = {1:-1,2:-0.7,3:-0.2,4:0.5,5:1}
    if(product.vine=='Y' and product.verified_purchase=='Y'): f2=3
    elif (product.vine=='Y' or product.verified_purchase=='Y'): f2=1
    res = sr.get(product.star_rating)*(((2*product.helpful_votes)-product.total_votes)*k1+1)
    return res

def get_star(product, helpful_vote_rate=0.1, v_rate=3, verified_purchase_rate=1.5):
    '''获得加权星级'''
    ret = 1
    if product.helpful_votes:
        ret *= product.helpful_votes*helpful_vote_rate
    if product.vine == 'Y':
        ret *= v_rate
    if product.verified_purchase == 'Y':
        ret *= verified_purchase_rate
    ret *= product.star_rating
    return ret

data['star'] = data.apply(get_star, axis=1)         #获得加权的星级

# =====================
parent_sale = data.groupby(['product_parent']).size()
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
l = le.fit_transform(parent_sale.index)

plt.plot(l, parent_sale)
plt.show()                                          #这边可以获得一个parent的总体销量图表，也就为下面为什么是300做铺垫
print(parent_sale[parent_sale>300])

# =====================
title_sale = data.groupby(['product_title']).size()
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
l = le.fit_transform(title_sale.index)

plt.plot(l, title_sale)
plt.show()   
print(title_sale[title_sale>250])

# ===================== 
id_sale = data.groupby(['product_id']).size()
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
l = le.fit_transform(id_sale.index)

plt.plot(l, id_sale)
plt.show()   
print(id_sale[id_sale>250])

# =====================
star = data['star'].groupby(data['product_id']).sum() # 获得每个product的加权星级之和
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
l = le.fit_transform(star.index)

plt.plot(l, star)
plt.show()                                          #这边可以获得一个parent的总体销量图表，也就为下面为什么是300做铺垫
print(star[star>1500])

# =====================
top6 = parent_sale.sort_values()[-6:]                   #声誉图，即该商家占比总数
a = data['star'].groupby(data['product_parent']).sum()
b = a[a>5]
da = data[data['product_parent'].isin(b.index)]
for i in range(len(top6)):
    t = data[data.product_parent == top6.index[i]]
    ll = t['star'].groupby([t['sub']]).sum().cumsum()
    
    total = (da['star'].groupby([da['sub']]).sum().cumsum())[ll.index]
    ret = ll/total
    plt.plot(ret.index, ret, label='{}'.format(top6.iloc[i]))
plt.legend()
plt.show()

# =====================
top6 = parent_sale.sort_values()[-6:]                   #销量占比图
for i in range(len(top6)):
    t = data[data.product_parent == top6.index[i]]
    sales = t.groupby([t['sub']]).size().cumsum()
    
    total_sale = (data.groupby([data['sub']]).size().cumsum())[sales.index]
    ret = sales/total_sale
    plt.plot(ret.index, ret, label='sales volume per day')
plt.legend()
plt.show()


# 将每个商家的销量和声誉放在一个图，然后画6个商家
fig = plt.figure()
fig.set(alpha=0.2)
plt.subplot2grid((2, 3),(0, 0))

a = data['star'].groupby(data['product_parent']).sum()
b = a[a>5]
da = data[data['product_parent'].isin(b.index)]
top6 = parent_sale.sort_values()[-6:]
for k in range(len(top6)):
    i = k
    if i > 2:
        i -= 3
        j = 1
    else:j = 0
    plt.subplot2grid((2, 3), (j, i))
    t = data[data.product_parent == top6.index[k]]
    sales = t.groupby([t['sub']]).size().cumsum()
    
    total_sale = (data.groupby([data['sub']]).size().cumsum())[sales.index]
    ret = sales/total_sale
    plt.plot(ret.index, ret)

    ll = t['star'].groupby([t['sub']]).sum().cumsum()
    
    total = (da['star'].groupby([da['sub']]).sum().cumsum())[ll.index]
    ret = ll/total
    plt.plot(ret.index, ret, label='{}'.format(top6.iloc[i]))
plt.show()



# =============================
'''相似度分类'''
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import re
from bs4 import BeautifulSoup
import random


star = 1
clusters = 7

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
    # 去掉HTML标签，拿到内容
    review_text = BeautifulSoup(review, "html.parser").get_text()
    # 用正则表达式取出符合规范的部分
    review_text = re.sub("[^a-zA-Z]", " ", review_text)
    # 小写化所有的词，并转成词list
    words = review_text.lower().split()
    # 返回words
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
    for index, label in enumerate(kmeans.labels_, 1):
        print('index: {}, label: {}'.format(index, label))
    print('inertia: {}'.format(kmeans.inertia_))


    d = data[data.star_rating==category].copy()
    d['category'] = kmeans.labels_


    ret = pd.DataFrame()
    for i in range(7):
        #随机挑选n条评论来看情况
        temp = d[d['category'] == i].review_body
        l = len(temp) // 20
        temp.index = range(len(temp))
        s = [random.randint(0, len(temp)) for i in range(l)]
        temp[s]
        ret[i] = temp[s]
    ret.to_csv('review{}.csv'.format(star))
    


