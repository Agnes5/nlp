import random
from os import listdir

from sklearn.feature_extraction import stop_words
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


def main():
    training_z = './ustawy/training/z/'
    training_bz = './ustawy/training/bz/'
    testing_z = './ustawy/testing/z/'
    testing_bz = './ustawy/testing/bz/'
    val_z = './ustawy/validation/z/'
    val_bz = './ustawy/validation/bz/'

    train_x = []
    train_y = []
    test_x = []
    test_y = []
    val_x = []
    val_y = []

    for filename in listdir(training_z):
        f = open(training_z + filename, 'r')

        # full
        # text = f.read()

        text = f.readlines()
        k = round(len(text) * 0.1)
        print(str(len(text)) + ' ' + str(k))
        if len(text) < k:
            text = f.read()
        else:
            text_tmp = random.sample(text, k=k)
            text = ''
            for line in text_tmp:
               text += line

        train_x.append(text)
        train_y.append(1)

    for filename in listdir(training_bz):
        f = open(training_bz + filename, 'r')

        # full
        # text = f.read()

        text = f.readlines()
        k = round(len(text) * 0.1)
        if len(text) < k:
            text = f.read()
        else:
            text_tmp = random.sample(text, k=k)
            text = ''
            for line in text_tmp:
               text += line

        train_x.append(text)
        train_y.append(0)

    trains = list(zip(train_x, train_y))
    random.shuffle(trains)

    for filename in listdir(testing_z):
        f = open(testing_z + filename, 'r')

        # full
        # text = f.read()

        text = f.readlines()
        k = round(len(text) * 0.1)
        if len(text) < k:
            text = f.read()
        else:
            text_tmp = random.sample(text, k=k)
            text = ''
            for line in text_tmp:
               text += line

        test_x.append(text)
        test_y.append(1)

    for filename in listdir(testing_bz):
        f = open(testing_bz + filename, 'r')

        # full
        # text = f.read()

        text = f.readlines()
        k = round(len(text) * 0.1)
        if len(text) < k:
            text = f.read()
        else:
            text_tmp = random.sample(text, k=k)
            text = ''
            for line in text_tmp:
               text += line

        test_x.append(text)
        test_y.append(0)

    tests = list(zip(test_x, test_y))
    random.shuffle(tests)

    for filename in listdir(val_z):
        f = open(val_z + filename, 'r')

        # full
        # text = f.read()

        text = f.readlines()
        k = int(len(text) * 0.1)
        if len(text) < k:
            text = f.read()
        else:
            text_tmp = random.sample(text, k=k)
            text = ''
            for line in text_tmp:
               text += line

        val_x.append(text)
        val_y.append(1)

    for filename in listdir(val_bz):
        f = open(val_bz + filename, 'r')

        # full
        # text = f.read()

        text = f.readlines()
        k = int(len(text) * 0.1)
        if len(text) < k:
            text = f.read()
        else:
            text_tmp = random.sample(text, k=k)
            text = ''
            for line in text_tmp:
               text += line

        val_x.append(text)
        val_y.append(0)


    f_train = open('./fastText-0.2.0/train.train', 'w')
    f_test = open('./fastText-0.2.0/test.test', 'w')
    f_val = open('./val.val', 'w')
    f_test2 = open('test_value', 'w')

    for elem, tag in trains:
        text = elem.replace('\n', ' ')
        f_train.write('__label__' + str(tag) + ' ' + text + '\n')

    for elem, tag in tests:
        text = elem.replace('\n', ' ')
        f_test.write('__label__' + str(tag) + ' ' + text + '\n')
        f_test2.write('__label__' + str(tag) + '\n')

    for elem, tag in zip(val_x, val_y):
        text = elem.replace('\n', ' ')
        f_val.write('__label__' + str(tag) + ' ' + text + '\n')



    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', OneVsRestClassifier(LinearSVC()))
    ])
    parameters = {
        'tfidf__max_df': (0.25, 0.5, 0.75),
        'tfidf__ngram_range': [(1, 1), (1, 2), (1, 3)],
        "clf__estimator__C": [0.01, 0.1, 1],
        "clf__estimator__class_weight": ['balanced', None],
    }

    grid_search_tune = GridSearchCV(
        pipeline, parameters, cv=2, n_jobs=2, verbose=3)
    grid_search_tune.fit(train_x, train_y)

    best_clf = grid_search_tune.best_estimator_
    predictions = best_clf.predict(test_x)

    print(classification_report(test_y, predictions))


if __name__ == "__main__":
    main()