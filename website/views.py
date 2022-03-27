
from chatbot import chatbot_reponse
from flask import Blueprint, jsonify, render_template, request, session

from website import dao

views = Blueprint("views", __name__)


@views.route('/')
def index(): 
    return render_template('home.html')
    
@views.route("/get")
def get_bot_response():
    userText = request.args.get("msg")
    oldtag = request.args.get("oldtag")

    # Check if there are conversation in session, if not create a new conversation

    if session.get("conversation_id") == None:
        conversation = dao.new_conversation()
        session["conversation_id"] = conversation.id

    response = chatbot_reponse(str(userText), oldtag, session["conversation_id"])
    return jsonify(response)

@views.route("/get-chat-history")
def get_chat_history():
    topn = request.args.get("topn")
    conversation_id = session.get("conversation_id")

    if topn == None:
        chat_history = dao.get_chat_history(conversation_id)
    else:  #
        chat_history = dao.get_chat_history(conversation_id, int(topn))

    return jsonify(chat_history)

