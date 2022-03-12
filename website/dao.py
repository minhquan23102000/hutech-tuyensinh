from chatbot.models import Conversation, Question, Statement, Tag

from website import db


def get_chat_history(conversation_id, topn=10):
    if conversation_id == None or topn <= 0:
        return []

    questions = (
        db.session.query(Question)
        .filter(Question.conversation_id == conversation_id)
        .order_by(Question.id.desc())
        .limit(topn)
    )
    result = []

    for q in questions[::-1]:
        chat = dict()
        chat["question"] = q.asking
        chat["answer"] = q.answer
        result.append(chat)

    return result


def new_conversation():
    conversation = Conversation()
    db.session.add(conversation)
    db.session.commit()
    db.session.flush()
    return conversation
