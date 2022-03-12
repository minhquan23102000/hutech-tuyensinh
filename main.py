import logging
import os

from website import create_app

logging.basicConfig(level=logging.INFO)
logging.getLogger("gensim").setLevel(logging.WARNING)
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
