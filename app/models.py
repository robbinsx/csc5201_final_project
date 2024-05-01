import datetime
import os
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
from peewee import MySQLDatabase, SqliteDatabase, Model, CharField, DateTimeField, BooleanField, ForeignKeyField, TextField, IntegrityError

# DB_HOST = os.getenv('MYSQL_HOST')

# DB = SqliteDatabase('social_media.db')
DB = MySQLDatabase('social_media', user='root', password='root', host='db', port=3306)

class BaseModel(Model):
    class Meta:
        database = DB

class User(UserMixin, BaseModel):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField()
    joined = DateTimeField(default=datetime.datetime.now())
    admin = BooleanField(default=False)

    class Meta: 
        order_by = ('-username')

    def users_following(self):
        return User.select().join(Relationship, on=Relationship.to_user).where(Relationship.from_user == self)

    def followed_by(self):
        return User.select().join(Relationship, on=Relationship.from_user).where(Relationship.to_user == self)

    @classmethod
    def is_following(self, user): 
        return Relationship.select().where((Relationship.from_user) & (self & Relationship.to_user == user)).exists()

    @classmethod
    def post(self, content, user_id):
        return Post.create(created_at=datetime.datetime.now(), user=user_id, content=content)

    def get_user_feed(self):
        return Post.select().where((Post.user << self.users_following()) | (Post.user == self)).order_by(Post.created_at.desc())

    @classmethod
    def create_user(self, username, email, password, is_admin=False):
        try:
            user_id = self.create(username=username, email=email, password=generate_password_hash(password), admin=is_admin)
        except IntegrityError:
            raise ValueError('User already exists!')

        return user_id


class Post(BaseModel): 
    created_at = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(User, backref='created_posts')
    content = TextField()

    class Meta: 
        order_by = ('-created_at')


class Relationship(BaseModel):
    from_user = ForeignKeyField(User, backref='relationship')
    to_user = ForeignKeyField(User, backref='related_to')

    class Meta: 
        indexes = ((('from_user', 'to_user'), True),)


def init_db():
    with DB:
        DB.create_tables([User, Relationship, Post])
