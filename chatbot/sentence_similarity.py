import numpy as np
from lib.chatterbot.comparisons import Comparator
from sklearn.metrics.pairwise import cosine_similarity


class VietnameseCosineSimilarity(Comparator):
    """
    Calculates the similarity of two statements based on the Cosine Similarity
    Step 1: We convert statement to tf-idf vector
    Step 2: Calculate similarity base on consine similarity 
    """

    def compare(self, statement_a, statement_b):
        """
        Return the calculated similarity of two
        statements based on the cosine similarity.
        """
        from sklearn.feature_extraction.text import TfidfVectorizer

        # Caculate tfidf cosine similarity
        tfidf = TfidfVectorizer(token_pattern=r'\S+')
        content = [
            ' '.join(statement_a.search_in_response_to),
            ' '.join(statement_b.search_in_response_to)
        ]
        matrix = tfidf.fit_transform(content)
        confidence = cosine_similarity(matrix[0], matrix[1])[0][0]

        # If any statement has oldtags value, add 5% confidence to it
        if statement_a.get_tags() == statement_b.get_tags() and confidence < 0.95:
            confidence += 0.05

        return np.round(confidence, 4)


class Word2VecSimilarity(Comparator):
    """Using word2vec to calculate similarity

    Args:
        Comparator ([type]): [description]
    """

    def __init__(self, language):
        from gensim.models import KeyedVectors
        super().__init__(language)
        self.model = KeyedVectors.load('chatbot/vietnamese_news_w2v.model')

    def compare(self, statement_a, statement_b):

        # Caculate tfidf cosine similarity
        vec_a = self.to_vector(statement_a.search_in_response_to)
        vec_b = self.to_vector(statement_b.search_in_response_to)

        confidence = cosine_similarity([vec_a], [vec_b])[0][0]

        # If any statement has oldtags value, add 5% confidence to it
        if statement_a.get_tags() == statement_b.get_tags() and confidence < 0.95:
            confidence += 0.05

        return round(confidence, 4)-0.1

    def to_vector(self, sentence):
        words = sentence.split(' ')
        nwords = len(words)
        featureVec = np.zeros(
            (self.model.vectors.shape[1],), dtype="float32")

        for word in words:
            try:
                featureVec = np.add(featureVec, self.model[word])
            except:
                continue

        if nwords > 0:
            featureVec = np.divide(featureVec, nwords)

        return featureVec
