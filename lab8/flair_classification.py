from flair.data_fetcher import NLPTaskDataFetcher
from flair.embeddings import WordEmbeddings, FlairEmbeddings, DocumentLSTMEmbeddings
from flair.models import TextClassifier
from flair.trainers import ModelTrainer
from pathlib import Path


def main():
    corpus = NLPTaskDataFetcher.load_classification_corpus(Path('./'), test_file='test.test', dev_file='val.val',
                                                           train_file='train.train')
    word_embeddings = [WordEmbeddings('glove'), FlairEmbeddings('news-forward-fast'),
                       FlairEmbeddings('news-backward-fast')]
    document_embeddings = DocumentLSTMEmbeddings(word_embeddings, hidden_size=512, reproject_words=True,
                                                 reproject_words_dimension=256)
    classifier = TextClassifier(document_embeddings, label_dictionary=corpus.make_label_dictionary(), multi_label=False)
    trainer = ModelTrainer(classifier, corpus)
    trainer.train('./', max_epochs=10)


if __name__ == "__main__":
    main()

