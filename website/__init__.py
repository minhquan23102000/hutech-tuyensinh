import numpy as np
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

TAG_REMOVE = ['F', 'Np', 'C', 'M', 'L', 'X']
with open('chatbot/vietnamese_stopwords.txt', 'r', encoding="utf8") as f:
    STOPWORDS = np.array(f.read().split('\n'))


def create_app():
    app = Flask(__name__)

    app.config.from_pyfile('config.py')

    # Connect db to app
    db.init_app(app)

    from .views import views
    app.register_blueprint(views, url_prefix='/')

    # check = ""
    # while (check != 'Y' and check != 'N'):
    #     check = input("Tạo lại cơ sở dữ liệu? Y:N\n")
    #     if (check == 'Y'):
    #         init_database(app)

    # retrain_chatbot(app)

    return app


def init_database(app):
    # Import model
    import chatbot
    import chatbot.models
    from chatbot.models import (Base, Conversation, Paper, PaperLinkTag,
                                Question, Role, Statement, Tag, User)

    chatbot.Sonny.storage.recreate_database()


def retrain_chatbot(app):
    # Retrain chatbot
    import chatbot

    check = ""
    while (check != 'Y' and check != 'N'):
        check = input("Train lại chatbot? Y:N\n")
        if (check == "Y"):
            chatbot.Sonny.storage.drop()
            chatbot.__retrain__()
