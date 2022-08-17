import sqlalchemy as sq
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType



Base = declarative_base()



class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, unique=True, nullable=False)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    sex = sq.Column(sq.Integer)
    bdate = sq.Column(sq.String)
    city = sq.Column(sq.String)
    profile_link = sq.Column(sq.String)
    photo_urls = relationship('Photo')

    def __str__(self):
        self.profile_link = f"https://vk.com/id{self.user_id}"
        ss = f'{self.first_name} {self.last_name} {self.profile_link}'
        return ss

    def my_dict(self):
        my_dict = {'user_id': self.user_id,
                   'first_name': self.first_name,
                   'last_name': self.last_name,
                   'sex': self.sex,
                   'bdate': self.bdate,
                   'city': self.city
                   }
        return my_dict


class Photo(Base):
    __tablename__ = 'photo'

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, ForeignKey('user.user_id'))
    url = sq.Column(sq.String, nullable=False)

    def __str__(self):
        return f"{self.url}"





def create_db(dsn):
    engine = sq.create_engine(dsn)
    session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    return session


def clear_db(dsn):
    engine = sq.create_engine(dsn)
    connection = engine.connect()
    delete_list = ('photo', 'user')
    for entry in delete_list:
        query_string = f"""DELETE FROM {entry};"""
        connection.execute(query_string)






class Vkinder:
    def __init__(self, token=None, group_token=None):
        self.token = token
        self.group_token = group_token
        self.vk_session = vk_api.VkApi(token=self.token).get_api()
        self.group_session = vk_api.VkApi(token=self.group_token)
        self.longpoll = VkLongPoll(vk_api.VkApi(token=self.group_token))

    def get_user_info(self, id_=None):
        vk_user = self.vk_session.users.get(user_ids=id_, fields='sex, bdate, city, relation')
        return vk_user

    def get_photos(self, id_):
        photo = self.vk_session.photos.get(owner_id=id_, album_id='profile', extended=1)
        return photo

    def search(self, params):
        tool = vk_api.tools.VkTools(self.vk_session)
        res = tool.get_all_iter('users.search', 1000, values=params)
        return res

    def send_msg(self, user_id, message, attachment=None):
        self.group_session.method('messages.send',
                                  {'user_id': user_id,
                                   'message': message,
                                   'random_id': randrange(10 ** 7),
                                   'attachment': attachment})

    def read_msg(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                return event




class Message:
    def __init__(self, k, id_):
        self.k = k
        self.id_ = id_

    def write(self, message):
        self.k.send_msg(self.id_, message)

    def read(self):
        text = False
        while not text:
            event = self.k.read_msg()
            if event.user_id == self.id_:
                text = event.text
        return text







