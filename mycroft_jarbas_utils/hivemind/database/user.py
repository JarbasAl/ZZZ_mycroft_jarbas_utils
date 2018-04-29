from sqlalchemy import Column, Text, String, Integer, create_engine, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from mycroft_jarbas_utils.hivemind.database import Base
from mycroft.configuration.config import Configuration
from os.path import dirname, join


class User(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    description = Column(Text)
    api_key = Column(String)
    name = Column(String)
    mail = Column(String)
    last_seen = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)


class UserDatabase(object):
    def __init__(self, path=None, debug=False):
        if path is None:
            path = Configuration.get().get("hivemind", {}).get("sql_user_db",
                                                               "sqlite:///"
                                                               + join(
                                                                   dirname(__file__), "users.db"))
        self.db = create_engine(path)
        self.db.echo = debug

        Session = sessionmaker(bind=self.db)
        self.session = Session()
        Base.metadata.create_all(self.db)

    def update_timestamp(self, api, timestamp):
        user = self.get_user_by_api_key(api)
        if not user:
            return False
        user.last_seen = timestamp
        return self.commit()

    def delete_user(self, api):
        user = self.get_user_by_api_key(api)
        if user:
            self.session.delete(user)
            return self.commit()
        return False

    def change_api(self, user_name, new_key):
        user = self.get_user_by_name(user_name)
        if not user:
            return False
        user.api_key = new_key
        return self.commit()

    def change_name(self, new_name, key):
        user = self.get_user_by_api_key(key)
        if not user:
            return False
        user.name = new_name
        return self.commit()

    def get_user_by_api_key(self, api_key):
        return self.session.query(User).filter_by(api_key=api_key).first()

    def get_user_by_name(self, name):
        return self.session.query(User).filter_by(name=name).first()

    def add_user(self, name=None, mail=None, api="", admin=False):
        user = User(api_key=api, name=name, mail=mail,
                    id=self.total_users() + 1, is_admin=admin)
        self.session.add(user)
        return self.commit()

    def total_users(self):
        return self.session.query(User).count()

    def commit(self):
        try:
            self.session.commit()
            return True
        except IntegrityError:
            self.session.rollback()
        return False
