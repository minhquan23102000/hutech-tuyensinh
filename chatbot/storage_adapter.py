from lib.chatterbot.storage.sql_storage import SQLStorageAdapter

from .tag import VietnameseTager


class MySQLStorageAdapter(SQLStorageAdapter):
    """
    The SQLStorageAdapter allows ChatterBot to store conversation
    data in any database supported by the SQL Alchemy ORM.
    All parameters are optional, by default a sqlite database is used.
    It will check if tables are present, if they are not, it will attempt
    to create the required tables.
    :keyword database_uri: eg: sqlite:///database_test.sqlite3',
        The database_uri can be specified to choose database driver.
    :type database_uri: str
    """

    def __init__(self, **kwargs):
        import logging
        self.logger = kwargs.get('logger', logging.getLogger(__name__))
        self.tagger = VietnameseTager()

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        self.database_uri = kwargs.get('database_uri', False)

        # None results in a sqlite in-memory database as the default
        if self.database_uri is None:
            self.database_uri = 'sqlite://'

        # Create a file database if the database is not a connection string
        if not self.database_uri:
            self.database_uri = 'sqlite:///db.sqlite3'

        self.engine = create_engine(self.database_uri, convert_unicode=True)

        if self.database_uri.startswith('sqlite://'):
            from sqlalchemy import event
            from sqlalchemy.engine import Engine

            @event.listens_for(Engine, 'connect')
            def set_sqlite_pragma(dbapi_connection, connection_record):
                dbapi_connection.execute('PRAGMA journal_mode=WAL')
                dbapi_connection.execute('PRAGMA synchronous=NORMAL')

        if not self.engine.dialect.has_table(self.engine, 'Statement'):
            self.create_database()

        self.Session = sessionmaker(bind=self.engine, expire_on_commit=True)

    def get_statement_model(self):
        """
        Return the statement model.
        """
        from chatbot.models import Statement
        return Statement

    def get_tag_model(self):
        """
        Return the conversation model.
        """
        from chatbot.models import Tag
        return Tag

    def create_database(self):
        """
        Populate the database with the tables.
        """
        from chatbot.models import Base
        Base.metadata.create_all(self.engine)

    def recreate_database(self):
        from chatbot.models import Base
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

    def drop(self):
        """
        Drop the database.
        """
        from chatbot.models import Conversation, Paper, PaperLinkTag, Question
        Statement = self.get_model('statement')
        Tag = self.get_model('tag')

        session = self.Session()

        session.query(Statement).delete()

        session.query(Question).delete()
        session.query(Conversation).delete()
        session.query(PaperLinkTag).delete()
        session.query(Tag).delete()

        session.commit()
        session.close()
