import flask # Not importing specific things or I get lost
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash, generate_password_hash
import models
import mysql.connector
import flask_monitoringdashboard as dashboard

app = flask.Flask(__name__)

dashboard.config.init_from(file='dashboard_config.cfg')

login_manager = LoginManager()
login_manager.init_app(app)

app.secret_key = '1GPptoBEczEy1FMUnBCL7g'

@app.before_request
def bef_request():
    flask.g.db = models.DB
    flask.g.db.connect()


@app.after_request
def after_request(response):
    flask.g.db.close()
    return response


@login_manager.user_loader
def load_logged_in(userid):
    try: 
        return models.User.get(models.User.id == userid)
    except models.User.DoesNotExist:
        return None


@login_manager.unauthorized_handler
def unauthorized():
    return flask.redirect(flask.url_for('index'))


@app.route('/')
def index():
    return flask.render_template('index.html')


'''
Defines route to register a new user to the site 
'''
@app.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'POST':
        email = flask.request.form['email']
        username = flask.request.form['username']
        password = flask.request.form['password']
        confirm_password = flask.request.form['confirm_password']

        if models.User.select().where((models.User.email == email) | (models.User.username == username)).exists():
            flask.flash('Username or email already exists!', 'error')
            return flask.render_template('register.html')

        if password != confirm_password:
            flask.flash('Passwords must match!', 'error')
            return flask.render_template('register.html')

        try: 
            models.User.create_user(username, email, password)
        except ValueError:
            flask.flash('Username already exists!', 'error')
            return flask.render_template('register.html')

        flask.flash('Registered successfully! You can now login.', 'info')
        return flask.redirect(flask.url_for('login'))

    return flask.render_template('register.html')


'''
Defines route to login page
'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        # get username from form
        username = flask.request.form['username']
        # try to get username from db
        try: 
            user = models.User.get(models.User.username == username)
        except models.User.DoesNotExist:
            # user doesn't exist redirect 
            flask.flash('Username Does Not Exist', 'error')
            return flask.render_template('login.html')

        if user and check_password_hash(user.password, flask.request.form['password']): 
            login_user(user)
            flask.flash('Login Success', 'info')
            return flask.redirect(flask.url_for('feed'))
        else: 
            flask.flash('Incorrect Password', 'error')
            return flask.render_template('login.html')

    # otherwise return login template
    return flask.render_template('login.html')


'''
Defines logout route, used through logout buttons in app
'''
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return flask.redirect(flask.url_for('login'))


'''
Used to direct user to create a post page, and adding post to database
'''
@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post(): 
    if flask.request.method == 'POST':
        content = flask.request.form['content']
        if content:
            post_id = models.User.post(content, current_user.id)
            print(post_id)
            flask.flash('Posted!', 'info')
            return flask.redirect(flask.url_for('feed'))

    return flask.render_template('new_post.html')


'''
Defines the route displaying the users profile
'''
@app.route('/my_profile')
@login_required
def my_profile():
    user = models.User.get(current_user.id)
    user_posts = models.Post.select().where(models.Post.user == current_user.id)
    for post in user_posts:
        print(post.content)
    # NEED A NEW TEMPLATE 
    return flask.render_template('my_profile.html', posts=user_posts, user=user)


'''
Defines a route to display another users profile, from which they can follow said user
'''
@app.route('/profile/<username>')
@login_required
def public_profile(username):
    try:
        target_user = models.User.get(models.User.username == username)
        target_user_posts = models.Post.select().where(models.Post.user == target_user)
        if target_user == current_user:
            return flask.render_template('my_profile.html', posts=target_user_posts, user=target_user)

        return flask.render_template('public_profile.html', posts=target_user_posts, user=target_user)
    except models.User.DoesNotExist:
        flask.flash('User not found.', 'error')
        return flask.redirect(flask.url_for('feed'))


'''
Displays the users feed, including all posts made by the users they are following and their own
'''
@app.route('/feed')
@login_required
def feed():
    user = models.User.get(current_user.id)
    if len(user.users_following()) == 0:
        flask.flash("You're not following anyone, follow users to customize your feed.", 'info')
        posts = models.Post.select().order_by(models.Post.created_at.desc())
    else:
        posts = user.get_user_feed()
    return flask.render_template('feed.html', posts=posts)


'''
Displays all users posts on the app
'''
@app.route('/explore')
@login_required
def explore():
    posts = models.Post.select().order_by(models.Post.created_at.desc())
    return flask.render_template('explore.html', posts=posts)


'''
Defines the route to follow a user, used through follow buttons on accounts in app
'''
@app.route('/follow/<username>')
@login_required
def follow_user(username):
    user = models.User.get_or_none(models.User.username == username)
    if user:
        if not user in current_user.users_following():
            models.Relationship.create(from_user=current_user, to_user=user)
            flask.flash(f'You followed {username}!', 'info')

    return flask.redirect(flask.url_for('public_profile', username=username))


'''
Defines the route to unfollow a user, used through unfollow button on accounts already following
'''
@app.route('/unfollow/<username>')
@login_required
def unfollow_user(username):
    user = models.User.get_or_none(models.User.username == username)
    if user:
        relationship = models.Relationship.get_or_none((models.Relationship.from_user == current_user) & (models.Relationship.to_user == user))
        if relationship:
            relationship.delete_instance()
            flask.flash(f'You unfollowed {username}', 'info')

    return flask.redirect(flask.url_for('public_profile', username=username))

dashboard.bind(app)

if __name__ == '__main__':
    # Init database
    models.init_db()
    # Insert test user 
    try: 
        models.User.create_user(username='xrobbins', email='robbinsx@msoe.edu', password='password', is_admin=True)
    except ValueError:
        print('Test user already exists!')
    # Run app
    app.run(host='0.0.0.0')