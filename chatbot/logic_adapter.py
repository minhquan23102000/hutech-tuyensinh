from lib.chatterbot.conversation import Statement
from lib.chatterbot.logic import LogicAdapter
from nltk import NaiveBayesClassifier
from pyvi import ViPosTagger, ViTokenizer


class MyBestMatch(LogicAdapter):
    """
    A logic adapter that returns a response based on known responses to
    the closest matches to the input statement.

    :param excluded_words:
        The excluded_words parameter allows a list of words to be set that will
        prevent the logic adapter from returning statements that have text
        containing any of those words. This can be useful for preventing your
        chat bot from saying swears when it is being demonstrated in front of
        an audience.
        Defaults to None
    :type excluded_words: list
    """

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)

        self.excluded_words = kwargs.get("excluded_words")

    def process(self, input_statement, additional_response_selection_parameters=None):
        search_results = self.search_algorithm.search(input_statement)

        # Use the input statement as the closest match if no other results are found
        closest_match = next(search_results, input_statement)

        max_confidence = 0
        # Search for the closest match to the input statement
        for result in search_results:

            # Stop searching if a match that is close enough is found
            if result.confidence >= self.maximum_similarity_threshold:
                closest_match = result
                break
            if result.confidence > max_confidence:
                closest_match = result
                max_confidence = result.confidence

        self.chatbot.logger.info(
            'Using "{}" as a close match to "{}" with a confidence of {}'.format(
                closest_match.in_response_to,
                input_statement.in_response_to,
                closest_match.confidence,
            )
        )

        response = closest_match

        return response


class NameRememberAdapter(LogicAdapter):
    """
    An class that remember user name, when they talk to chatbot.
    There are three conditions that turn on this adapter
        1. If there are Pronoun in message input
        2. If there are a word "ten" in message input
        3. If all pos tag of the sentence input is 'Np'
    """

    P_WORDS = ["anh", "chị", "em", "tớ", "tôi", "mình", "tao", "mô"]

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)

        self.nlp = lambda x: ViPosTagger.postagging(ViTokenizer.tokenize(x))

        self.positive = kwargs.get(
            "positive",
            [
                "tôi tên là",
                "mình tên là",
                "họ tên của tớ là",
                "tao là ai",
                "tôi là ai",
                "anh tên là",
            ],
        )

        self.negative = kwargs.get(
            "negative",
            [
                "tớ là một người bạn tuyệt vời",
                "bạn tên là gì"
                "bạn có tên không",
                "bạn là ai",
                "anh ta là một người tốt",
                "mình là giảng viên kỹ thuật",
                "bạn thích món ăn nào nhất?",
                "cho tôi hỏi về giấy khai sinh?",
                "tôi đăng ký kết hôn như thế nào?",
                "mình muốn hỏi về thủ tục thường trú",
            ],
        )

        labeled_data = [(name, 0) for name in self.negative] + [
            (name, 1) for name in self.positive
        ]

        train_set = [
            (self.name_question_features(text), n) for (text, n) in labeled_data
        ]

        self.classifier = NaiveBayesClassifier.train(train_set)

    def name_question_features(self, text):
        """
        Provide an analysis of significant features in the string.
        """
        features = {}

        # A list of all words from the known sentences
        all_words = self.nlp(" ".join(self.positive + self.negative))[0]

        # A list of the first word in each of the known sentence
        # all_first_words = []
        # for sentence in self.positive + self.negative:
        #     all_first_words.append(sentence.split(" ", 1)[0])

        # for word in text.split():
        #     features["first_word({})".format(word)] = word in all_first_words
        words_text = self.nlp(text.lower())
        
        for word, tag in zip(words_text[0], words_text[1]):
            features["contains({})".format(word)] = word in all_words
            features["count({})".format(word)] = words_text[0].count(word)
 

        return features

    def can_process(self, statement):
        """
        A preliminary check that is called to determine if a
        logic adapter can process a given statement.

        :rtype: bool
        """

        statement_lower_bag_words = set(statement.in_response_to.split())

        if "tên" in statement_lower_bag_words:
            return True

        if statement_lower_bag_words & set(self.P_WORDS):
            return True

        if all(tag == "Np" for tag in self.nlp(statement.in_response_to)[1]):
            return True

        return False

    def process(self, input_statement, additional_response_selection_parameters=None):
        from website import dao

        from chatbot.models import Conversation

        input_text = input_statement.in_response_to
        person_name = self.name_extract(input_text)
        conversation_id = dao.get_conversation_id()
        db = dao.get_database()

        conversation = (
            db.session.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )
        name_feature = self.name_question_features(input_text)

        confidence = self.classifier.prob_classify(name_feature).prob(1)
        
        if person_name:
            # Store person name to database
            conversation.person_name = person_name
            response = f"Xin chào {person_name}, bạn có một cái tến rất đẹp!"
            statement = Statement(response)
        elif not conversation:
            statement = Statement("Bạn chưa nói cho mình tên của bạn.")
        else:
            # Get person name from database
            person_name = conversation.person_name
            if person_name:
                statement = Statement(
                    f"Bạn tên là {person_name}."
                )
            else:
                statement = Statement(
                    "Bạn chưa nói cho mình tên của bạn."
                )

        statement.confidence = confidence
        self.chatbot.logger.info(f"NameRememberLogic preprocess {input_text} with confidence = {confidence} and response {statement.text}")
        return statement

    def name_extract(self, sent: str) -> str:
        """Extract person name from a string sentence

        Args:
            sent (str): a string sentence to extract

        Returns:
            str: person name, if == '' than there a no person name in sentence.
        """

        pos_tag = self.nlp(sent)

        if all([tag == "Np" for tag in pos_tag[1]]):
            return " ".join(pos_tag[0])

        turn = False
        get = False
        name = ""
        for word, tag in zip(pos_tag[0], pos_tag[1]):
            if turn:
                if tag == "Np" and word.lower() != "tớ":
                    name += word + " "
                    get = True
                elif get:
                    break

            elif word.lower() in ["là", "tên"]:
                turn = True

        return name.replace('_', ' ').strip()
