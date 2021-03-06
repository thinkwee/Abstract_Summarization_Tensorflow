import gensim
import os
from sklearn import svm
import numpy as np
from sklearn import preprocessing
from sklearn.metrics import classification_report
from sklearn.externals import joblib


def file_preprocessing(file_name):
    file_output = open('./data/' + file_name + '.txt', 'w')
    with open('./data/sample.' + file_name + '.txt', 'r') as f:
        for line in f:
            if not line.__contains__('review') and line != "\n" and len(line) > 10:
                file_output.write(line)
    f.close()
    file_output.close()
    print(file_name + " preprocessing complete")


class SVM(object):
    def __init__(self, trainset, testset):
        self.trainset = trainset
        self.testset = testset
        self.file_train = open(self.trainset, 'r+')
        self.file_test = open(self.testset, 'r+')
        self.train_data = np.loadtxt(self.file_train)
        self.train_x = self.train_data[:, 1:]
        self.train_y = self.train_data[:, 0]
        self.test_data = np.loadtxt(self.file_test)
        self.test_x = self.test_data[:, :]
        self.clf = svm.SVC(probability=True)

    def Normalization(self):
        self.train_x = preprocessing.minmax_scale(self.train_x, feature_range=(-1, 1))
        self.test_x = preprocessing.minmax_scale(self.test_x, feature_range=(-1, 1))

    def Fitclf(self):
        self.clf.fit(self.train_x, self.train_y)

    def Predict(self):
        self.result = self.clf.predict(self.test_x)
        self.result_prob = self.clf.predict_proba(self.test_x)
        return self.result, self.result_prob

    def SaveModel(self):
        joblib.dump(self.clf, './SVM/train_model')

    def LoadModel(self):
        self.clf = joblib.load('./SVM/train_model')


def train_SVM():
    train_data = "./data/doc_vector_np.txt"
    test_data = "./data/doc_vector_np_test.txt"

    classifier = SVM(train_data, test_data)
    classifier.Normalization()
    classifier.Fitclf()
    classifier.SaveModel()
    # classifier.LoadModel()
    print("SVM training complete")
    result, result_prob = classifier.Predict()

    standard = []
    for i in range(200):
        standard.append(1)
        standard.append(-1)
    target_name = ['negative', 'positive']
    print(standard)
    print(result)
    print(classification_report(standard, result, target_names=target_name))

    for i in range(400):
        if result[i] != standard[i]:
            print(i, result_prob[i], standard[i])


def label_corpora():
    train_data = "./data/doc_vector_np.txt"
    test_data = "./data/article_middle_vec.txt"
    classifier_article = SVM(train_data, test_data)
    classifier_article.Normalization()
    classifier_article.LoadModel()
    result_article, result_prob_article = classifier_article.Predict()
    print("svm article predict complete")
    test_data = "./data/headline_middle_vec.txt"
    classifier_headline = SVM(train_data, test_data)
    classifier_headline.Normalization()
    classifier_headline.LoadModel()
    result_headline, result_prob_headline = classifier_headline.Predict()
    print("svm headline predict complete")
    output_file_p = open("./data/middle_corpora_sentiment_p.txt", "w")
    output_file_n = open("./data/middle_corpora_sentiment_n.txt", "w")
    count_p = 0
    count_n = 0
    for i in range(1000000):
        if result_prob_article[i][0] > 0.8 and result_prob_headline[i][0] > 0.8:
            output_file_n.writelines(
                str(i) + " " + str(result_headline[i]) + " " + str(result_prob_headline[i]) + " " + str(
                    result_prob_article[i]) + "\n")
            count_n += 1
        elif result_prob_article[i] < 0.2 and result_prob_headline[i] < 0.2:
            output_file_p.writelines(
                str(i) + " " + str(result_headline[i]) + " " + str(result_prob_headline[i]) + " " + str(
                    result_prob_article[i]) + "\n")
            count_p += 1

    print("%d positive sentence addded" % count_p)
    print("%d negative sentence addded" % count_n)


def train_Doc2Vec_Middle_corpora(file_name):
    input_file = open("./data/" + file_name + "_middle.txt", "r")
    output_file = open("./data/" + file_name + "_middle_vec.txt", "w")
    sentence = gensim.models.doc2vec.TaggedLineDocument(input_file)
    model = gensim.models.Doc2Vec(sentence, vector_size=100, window=5)
    print("Doc2Vec model for " + file_name + " built")
    for i in range(500000):
        for j in range(100):
            output_file.write(str(model.docvecs[i][j]) + ' ')
        output_file.write("\n")
    print("model saved to file")


def train_Doc2Vec():
    input_file_p = open("./data/positive.txt", "r")
    input_file_n = open("./data/negative.txt", "r")
    output_together = open("./data/together.txt", "a")
    p = []
    n = []
    for line in input_file_p:
        p.append(line)
    for line in input_file_n:
        n.append(line)
    for i in range(10200):
        output_together.write(p[i])
        output_together.write(n[i])
    output_together.close()
    input_file_n.close()
    input_file_p.close()
    print("p/n corpora added")

    input_file = open("./data/together.txt", "r")
    sentence = gensim.models.doc2vec.TaggedLineDocument(input_file)
    model = gensim.models.Doc2Vec(sentence, vector_size=100, window=5)
    print("Doc2Vec training completed")
    checkpoint = "./doc2vec/vec_model"
    model.save(checkpoint)
    input_file.close()

    output_file = open("./data/article_middle_vec.txt", "w")
    for i in range(1000000):
        for j in range(100):
            output_file.write(str(model.docvecs[i][j]) + ' ')
        output_file.write('\n')
    output_file.close()
    print("article_middle_vec output completed")

    output_file = open("./data/headline_middle_vec.txt", "w")
    for i in range(1000000, 2000000):
        for j in range(100):
            output_file.write(str(model.docvecs[i][j]) + ' ')
        output_file.write('\n')
    output_file.close()
    print("headline_middle_vec output completed")

    output_file = open("./data/doc_vector_np.txt", "w")
    for i in range(2000000, 2020000):
        if i % 2 == 0:
            output_file.write('1 ')
        else:
            output_file.write('-1 ')
        for j in range(100):
            output_file.write(str(model.docvecs[i][j]) + ' ')
        output_file.write('\n')
    print('sentiment vector output completed')
    output_file.close()

    test_file = open("./data/doc_vector_np_test.txt", "w")
    for i in range(2020000, 2020400):
        for j in range(100):
            test_file.write(str(model.docvecs[i][j]) + ' ')
        test_file.write('\n')
    test_file.close()
    print('sentiment vector test output completed')


# file_preprocessing("positive")
# file_preprocessing("negative")

# train_Doc2Vec()

train_SVM()

# train_Doc2Vec_Middle_corpora("headline")
# train_Doc2Vec_Middle_corpora("article")

# label_corpora()
