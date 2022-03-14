import enum

from flask_login import UserMixin
from lib.chatterbot import constants
from lib.chatterbot.conversation import StatementMixin
from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer,
                        String, Table, UniqueConstraint)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func


class ModelBase(object):
    """
    An augmented base class for SqlAlchemy models.
    """
    @declared_attr
    def __tablename__(cls):
        """
        Return the lowercase class name as the name of the table.
        """
        return cls.__name__.lower()


Base = declarative_base(cls=ModelBase)


class Paper(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_name = Column(String(250), unique=True)
    img_src = Column(String(255))


class PaperLinkTag(Base):
    __tablename__ = 'paperlink'
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)
    paper_id = Column(Integer, ForeignKey('paper.id'), primary_key=True)
    description = Column(String(255))
    paper = relationship('Paper')


class Tag(Base):
    """
    A tag that describes a statement.
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(constants.TAG_NAME_MAX_LENGTH), unique=True)
    description = Column(String(255))
    papers = relationship('PaperLinkTag')
    tokhai_src = Column(String(255))

    def __repr__(self):
        return '<Tag %r>' % (self.name)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Statement(Base, StatementMixin):
    """
    A Statement represents a sentence or phrase.
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    confidence = 0

    text = Column(String(constants.STATEMENT_TEXT_MAX_LENGTH), nullable=True)

    search_text = Column(String(constants.STATEMENT_TEXT_MAX_LENGTH),
                         nullable=True,
                         server_default='')

    conversation = Column(String(constants.CONVERSATION_LABEL_MAX_LENGTH),
                          nullable=False,
                          server_default='')

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tag_id = Column(Integer(), ForeignKey('tag.id'), nullable=True)

    tags = relationship('Tag', backref='statements')

    in_response_to = Column(String(constants.STATEMENT_TEXT_MAX_LENGTH),
                            nullable=True)

    search_in_response_to = Column(String(constants.STATEMENT_TEXT_MAX_LENGTH),
                                   nullable=False,
                                   server_default='')

    persona = Column(String(constants.PERSONA_MAX_LENGTH),
                     nullable=False,
                     server_default='')

    next_question_1 = Column(String(constants.STATEMENT_TEXT_MAX_LENGTH),
                             nullable=True)

    next_question_2 = Column(String(constants.STATEMENT_TEXT_MAX_LENGTH),
                             nullable=True)

    next_question_3 = Column(String(constants.STATEMENT_TEXT_MAX_LENGTH),
                             nullable=True)
    auto_question = Column(String(constants.STATEMENT_TEXT_MAX_LENGTH),
                           nullable=True)

    def get_tags(self):
        """
        Return  tags for this statement.
        """
        if self.tags:
            return self.tags.name
        else:
            return ''

    def add_tags(self, tags):
        """
        Update tag for this statement.
        """
        print("Calling add tag function")
        self.tags = Tag(name=tags)

    def get_next_questions(self):
        next_questions = []

        if self.next_question_1 != '':
            next_questions.append(self.next_question_1)

        if self.next_question_2 != '':
            next_questions.append(self.next_question_2)

        if self.next_question_3 != '':
            next_questions.append(self.next_question_3)

        return next_questions

    def __str__(self):
        return f'{self.text}: {self.in_response_to}'

    def __unicode__(self):
        return f'{self.text}: {self.in_response_to}'


class Role(enum.Enum):
    ADMIN = enum.auto()
    PEOPLE = enum.auto()


class User(Base, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(150), unique=True)
    password = Column(String(150))
    first_name = Column(String(150))
    last_name = Column(String(150))
    role = Column(Enum(Role), nullable=False)
    create_at = Column(DateTime(timezone=True), default=func.now())


class Sentiment(enum.Enum):
    HAILONG = enum.auto()
    KHONGHAILONG = enum.auto()


class Conversation(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer(), ForeignKey('user.id'), nullable=True)
    create_at = Column(DateTime(timezone=True), default=func.now())
    sentiment = Column(Enum(Sentiment), nullable=True)
    question = relationship("Question", backref=backref("question"))


class Question(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer(),
                             ForeignKey('conversation.id'),
                             nullable=False)
    tag_id = Column(Integer(), ForeignKey('tag.id'), nullable=True)
    asking = Column(String(255), nullable=False)
    answer = Column(String(255), nullable=False)
    create_at = Column(DateTime(timezone=True), default=func.now())
    is_not_known = Column(Boolean(), default=False)
    tag = relationship('Tag', backref=backref('questions', lazy='dynamic'))

    next_question_1 = Column(String(constants.STATEMENT_TEXT_MAX_LENGTH),
                             nullable=True)

    next_question_2 = Column(String(constants.STATEMENT_TEXT_MAX_LENGTH),
                             nullable=True)

    next_question_3 = Column(String(constants.STATEMENT_TEXT_MAX_LENGTH),
                             nullable=True)

    def get_next_questions(self):
        next_questions = []

        if self.next_question_1:
            next_questions.append(self.next_question_1)

        if self.next_question_2:
            next_questions.append(self.next_question_2)

        if self.next_question_3:
            next_questions.append(self.next_question_3)

        return next_questions
