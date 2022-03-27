from chatbot.models import Conversation, Question, Statement, Tag
from flask import session
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy

from website import db


def get_chat_history(conversation_id, topn=10):

    
    if conversation_id == None or topn <= 0:
        return {}

    questions = (
        db.session.query(Question)
        .filter(Question.conversation_id == conversation_id)
        .order_by(Question.id.desc())
        .limit(topn)
    )
    result = {}
    result = {'chat_history': []}

    for q in questions[::-1]:
        chat = dict()
        chat["question"] = q.asking
        chat["answer"] = q.answer
        result['chat_history'].append(chat)

    
    conversation = db.session.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    q = questions[0]
    if q.statement and q.statement.get_tags() not in ['lời chào', 'cảm xúc', None]:
        result['guide'] = f"Xin chào {conversation.person_name}, bạn có muốn tiếp tục cuộc hội thoại khi nảy về {q.statement.get_tags()} không?"
        result['next_questions'] = q.statement.get_next_questions()
    else:
        result['guide'] = f"Xin chào {conversation.person_name}!"
        result['next_questions'] = []
    
    return result


def new_conversation():
    conversation = Conversation()
    
    db.session.add(conversation)
    db.session.commit()
    db.session.flush()
    return conversation


def get_conversation_id():
    return session.get("conversation_id")


def get_database() -> SQLAlchemy:
    return db
