from lib.chatterbot.logic import LogicAdapter


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

        self.excluded_words = kwargs.get('excluded_words')

    def process(self,
                input_statement,
                additional_response_selection_parameters=None):
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
            'Using "{}" as a close match to "{}" with a confidence of {}'.
            format(closest_match.in_response_to, input_statement.in_response_to,
                   closest_match.confidence))

        response = closest_match

        return response
