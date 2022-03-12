from lib.chatterbot.conversation import Statement


class IndexedTextSearch:
    """
    :param statement_comparison_function: The dot-notated import path
        to a statement comparison function.
        Defaults to ``LevenshteinDistance``.

    :param search_page_size:
        The maximum number of records to load into memory at a time when searching.
        Defaults to 1000
    """

    name = 'indexed_text_search'

    def __init__(self, chatbot, **kwargs):
        from lib.chatterbot.comparisons import LevenshteinDistance

        self.chatbot = chatbot

        statement_comparison_function = kwargs.get(
            'statement_comparison_function',
            LevenshteinDistance
        )

        self.compare_statements = statement_comparison_function(
            language=self.chatbot.storage.tagger.language
        )

        self.search_page_size = kwargs.get(
            'search_page_size', 1000
        )

    def search(self, input_statement, **additional_parameters):
        """
        Search for close matches to the input. Confidence scores for
        subsequent results will order of increasing value.

        :param input_statement: A statement.
        :type input_statement: chatterbot.conversation.Statement

        :param **additional_parameters: Additional parameters to be passed
            to the ``filter`` method of the storage adapter when searching.

        :rtype: Generator yielding one closest matching statement at a time.
        """
        self.chatbot.logger.info('Beginning search for close text match')

        input_search_in_response_to = input_statement.search_in_response_to

        if not input_statement.search_in_response_to:
            self.chatbot.logger.warn(
                'No value for search_in_response_to was available on the provided input'
            )

            input_search_in_response_to = self.chatbot.storage.tagger.get_bigram_pair_string(
                input_statement.in_response_to
            )

        if self.compare_statements.__class__.__name__ == "Word2VecSimilarity":
            similar_keys = ''
            for word in input_search_in_response_to.split(' '):
                try:
                    similar_words = self.compare_statements.model.most_similar(
                        word, topn=4)
                    similar_keys += ' '.join(
                        [w[0] for w in similar_words]) + ' '
                except Exception as e:
                    self.chatbot.logger.warn(e)
                    continue
        print(self.chatbot.last_search_in_respone)
        search_parameters = {
            'search_in_response_to_contains': similar_keys + input_search_in_response_to,
            'persona_not_startswith': 'bot:',
            'page_size': self.search_page_size,
            'exclude_search': self.chatbot.last_search_in_respone
        }

        if additional_parameters:
            search_parameters.update(additional_parameters)

        statement_list = self.chatbot.storage.filter(**search_parameters)
        first_statement = next(statement_list, None)
        
        if first_statement is None:
            search_parameters = {
                'page_size': self.search_page_size
            }
            statement_list = self.chatbot.storage.filter(**search_parameters)
            first_statement = next(statement_list, input_statement)
        
        closest_match = first_statement
        closest_match.confidence = self.compare_statements(input_statement, first_statement)
        
        self.chatbot.logger.info('Processing search results')
        #Yield first statement
        yield closest_match
        
        # Find the closest matching known statement
        for statement in statement_list:
            confidence = self.compare_statements(input_statement, statement)

            if confidence > closest_match.confidence:
                statement.confidence = confidence
                closest_match = statement

                self.chatbot.logger.info('Similar text found: {} {}'.format(
                    closest_match.in_response_to, confidence
                ))

                yield closest_match
