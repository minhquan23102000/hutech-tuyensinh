from datetime import datetime

from dateutil import parser as date_parser
from pytz import UTC


class StatementMixin(object):
    """
    This class has shared methods used to
    normalize different statement models.
    """

    statement_field_names = [
        'id',
        'text',
        'search_text',
        'conversation',
        'persona',
        'tags',
        'in_response_to',
        'search_in_response_to',
        'created_at',
        'next_question_1',
        'next_question_2',
        'next_question_3',
      
    ]

    extra_statement_field_names = []

    def get_statement_field_names(self):
        """
        Return the list of field names for the statement.
        """
        return self.statement_field_names + self.extra_statement_field_names

    def get_tags(self):
        """
        Return the tags for this statement.
        """
        return self.tags

    def add_tags(self, tags):
        """
        Update statement tag
        """
        self.tags = tags

    def add_next_question(self, next_questions):
        n = len(next_questions)
        if n >= 1:
            self.next_question_1 = next_questions[0]

        if n >= 2:
            self.next_question_2 = next_questions[1]

        if n >= 3:
            self.next_question_3 = next_questions[2]

    def get_next_questions(self):
        next_questions = []

        if self.next_question_1:
            next_questions.append(self.next_question_1)

        if self.next_question_2:
            next_questions.append(self.next_question_2)

        if self.next_question_3:
            next_questions.append(self.next_question_3)

        return next_questions

    def serialize(self):
        """
        :returns: A dictionary representation of the statement object.
        :rtype: dict
        """
        data = {}

        for field_name in self.get_statement_field_names():
            format_method = getattr(self, 'get_{}'.format(
                field_name
            ), None)

            if format_method:
                data[field_name] = format_method()
            else:
                data[field_name] = getattr(self, field_name)

        return data


class Statement(StatementMixin):
    """
    A statement represents a single spoken entity, sentence or
    phrase that someone can say.
    """

    __slots__ = (
        'id',
        'text',
        'search_text',
        'conversation',
        'persona',
        'tags',
        'in_response_to',
        'search_in_response_to',
        'created_at',
        'confidence',
        'storage',
        'next_question_1',
        'next_question_2',
        'next_question_3',
     
    )

    def __init__(self, text=None, in_response_to=None, **kwargs):

        self.id = kwargs.get('id')
        self.text = text
        self.search_text = kwargs.get('search_text', '')
        self.conversation = kwargs.get('conversation', '')
        self.persona = kwargs.get('persona', '')
        self.tags = kwargs.pop('tags', None)
        self.in_response_to = in_response_to
        self.search_in_response_to = kwargs.get('search_in_response_to', '')
        self.created_at = kwargs.get('created_at', datetime.now())
        self.next_question_1 = kwargs.get('next_question_1', '')
        self.next_question_2 = kwargs.get('next_question_2', '')
        self.next_question_3 = kwargs.get('next_question_3', '')
        self.auto_question = kwargs.get('auto_question','')

        if not isinstance(self.created_at, datetime):
            self.created_at = date_parser.parse(self.created_at)

        # Set timezone to UTC if no timezone was provided
        if not self.created_at.tzinfo:
            self.created_at = self.created_at.replace(tzinfo=UTC)

        # This is the confidence with which the chat bot believes
        # this is an accurate response. This value is set when the
        # statement is returned by the chat bot.
        self.confidence = 0

        self.storage = None

    def __str__(self):
        return self.text

    def __repr__(self):
        return '<Statement text:%s>' % (self.text)

    def save(self):
        """
        Save the statement in the database.
        """
        self.storage.update(self)
