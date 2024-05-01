import datetime
import os
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
from peewee import MySQLDatabase, SqliteDatabase, Model, CharField, DateTimeField, BooleanField, ForeignKeyField, TextField, IntegrityError

# Database connection
DB = MySQLDatabase('social_media', user='root', password='root', host='db', port=3306)

class BaseModel(Model):
    '''
    Base database model - each extending model inherits Meta class connecting it to the proper database
    '''
    class Meta:
        database = DB

class User(UserMixin, BaseModel):
    '''
    Database model representing a user
    Fields: 
    - username : Username of the user
    - email : Email of the user
    - password : Users password
    - joined : Date and time user joined site
    - admin : Boolean representing admin priveleges in app
    '''
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField()
    joined = DateTimeField(default=datetime.datetime.now())
    admin = BooleanField(default=False)

    class Meta: 
        order_by = ('-username')

    def users_following(self):
        '''
        Get the users that the current user is following
        '''
        return User.select().join(Relationship, on=Relationship.to_user).where(Relationship.from_user == self)

    def followed_by(self):
        '''
        Get the users that are following the current user 
        '''
        return User.select().join(Relationship, on=Relationship.from_user).where(Relationship.to_user == self)

    @classmethod
    def is_following(self, user): 
        '''
        Check if the current user is following a user
        '''
        return Relationship.select().where((Relationship.from_user) & (self & Relationship.to_user == user)).exists()

    @classmethod
    def post(self, content, user_id):
        '''
        Create a new post
        '''
        return Post.create(created_at=datetime.datetime.now(), user=user_id, content=content)

    def get_user_feed(self):
        '''
        Get the current users feed (posts from users that they are following, as well as their own posts)
        '''
        return Post.select().where((Post.user << self.users_following()) | (Post.user == self)).order_by(Post.created_at.desc())

    @classmethod
    def create_user(self, username, email, password, is_admin=False):
        '''
        Add a user to the table
        '''
        try:
            user_id = self.create(username=username, email=email, password=generate_password_hash(password), admin=is_admin)
        except IntegrityError:
            raise ValueError('User already exists!')

        return user_id


class Post(BaseModel): 
    '''
    Database model for a post
    Fields: 
    - created_at : When post was created
    - user : User that made the post (Foreign Key)
    - content : Content of the post 
    '''
    created_at = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(User, backref='created_posts')
    content = TextField()

    class Meta: 
        order_by = ('-created_at')


class Relationship(BaseModel):
    '''
    Database model representing a relationship between two followers 
    Fields:
    - from_user : User relationship originates from
    - to_user : User relationship points to 
    '''
    from_user = ForeignKeyField(User, backref='relationship')
    to_user = ForeignKeyField(User, backref='related_to')

    class Meta: 
        indexes = ((('from_user', 'to_user'), True),)


'''
Helper function to initialize the database, creates all necessary tables if they do not exist
'''
def init_db():
    with DB:
        DB.create_tables([User, Relationship, Post])
