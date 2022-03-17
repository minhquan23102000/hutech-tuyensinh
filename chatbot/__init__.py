import langid
from lib.chatterbot.response_selection import get_random_response
from lib.chatterbot.trainers import ChatterBotCorpusTrainer
from website.config import SQLALCHEMY_DATABASE_URI

from chatbot.sentence_similarity import (VietnameseCosineSimilarity,
                                         Word2VecSimilarity)

from .mychatbot import MyChatBot

DEFAULT_REPONSE = "Xin lỗi, mình chưa được huấn luyện về vấn đề này."
NOT_VIETNAMESE_LANGUAGE_REPONSE = (
    "Xin lỗi, mình chỉ hiểu tiếng việt. Sorry i can only understand vietnamese."
)


Sonny = MyChatBot(
    "Sonny",
    storage_adapter="chatbot.storage_adapter.MySQLStorageAdapter",
    read_only=True,
    statement_comparison_function=Word2VecSimilarity,
    logic_adapters=[
        {
            "import_path": "chatbot.logic_adapter.MyBestMatch",
            "default_response": DEFAULT_REPONSE,
            "response_selection_method": get_random_response,
        }
    ],
    database_uri=SQLALCHEMY_DATABASE_URI,
)


def __retrain__():
    trainer = ChatterBotCorpusTrainer(Sonny)
    trainer.train("chatbot/corpus")


def __train__(filePath):
    trainer = ChatterBotCorpusTrainer(Sonny)
    trainer.train(filePath)


def chatbot_reponse(msg: str, oldtag: str = None, conversation_id=None):
    # Check message lem
    if len(msg) > 255:
        return {"response": "Dài quá!!", "tag": "none"}

    # Get reponse from bot
    if not oldtag:
        oldtag = "none"

    # Request response to bot
    response = Sonny.get_response(statement=msg, tags=oldtag)
    tag = response.get_tags()
    next_questions = response.get_next_questions()
    auto_question = response.auto_question

    if not tag:
        tag = "none"

    # Check if this is an unknown question that chatbot has never learned before
    is_not_known = False
    if response.confidence < 0.35:
        response = DEFAULT_REPONSE
        is_not_known = True
        tag = "none"
    else:
        response = response.text

    if is_not_known:
        # Google search this paper if bot does not know about it
        response = google_search_paper(msg)

    response_data = {
        "response": response,
        "tag": tag,
        "next_questions": next_questions,
        "auto_question": auto_question,
    }

    # Store this question to database
    if conversation_id:
        store_question(
            asking=msg,
            answer=response,
            oldtag=oldtag,
            conversation_id=conversation_id,
            is_not_known=is_not_known,
        )

    return response_data


def store_question(asking: str, answer: str, oldtag, conversation_id, is_not_known):
    from website import db

    from .models import Question, Tag

    msg_lang = langid.classify(asking)[0]
    if msg_lang in ["vi"]:
        question = Question(
            asking=asking,
            answer=answer,
            conversation_id=conversation_id,
            is_not_known=is_not_known,
        )
        tag_db = db.session.query(Tag).filter_by(name=oldtag).first()
        if tag_db:
            question.tag_id = tag_db.id
        db.session.add(question)
        db.session.commit()


def google_search_paper(msg: str):
    # Google search this paper if bot does not know about it
    flag_words = [
        "thủ tục",
        "hành chính",
        "giấy tờ",
        "đơn",
        "giấy phép",
        "đăng ký",
        "văn bản",
        "biên bản",
    ]
    # Google search this paper if bot does not know about it
    from pyvi import ViTokenizer

    words = ViTokenizer.tokenize(msg)
    if any(w.replace("_", " ").lower() in flag_words for w in words.split(" ")):
        from googlesearch import search

        # Make a request to google search
        try:
            url = list(
                search(msg, tld="com", lang="vi", num=1, stop=1, pause=2, country="vi")
            )[0]
            reponse = f"{DEFAULT_REPONSE} Nhưng mình nghĩ bạn có thể tham khảo thêm tại đây: {url}"
        except Exception as e:
            reponse = DEFAULT_REPONSE
    else:
        reponse = get_unknow_reponse()
    return reponse


def get_unknow_reponse():
    import random

    unknow_reponses = [
        DEFAULT_REPONSE,
        "Xin lỗi, bạn có thể nói rõ hơn được không?",
        "Xin lỗi, mình vẫn chưa học qua câu từ này",
    ]
    return random.choice(unknow_reponses)
