import flask
from flask import Flask, redirect, request, abort, render_template, session
from flaskext.mysql import MySQL
import flask_login
from werkzeug import secure_filename
import os, base64

app = Flask(__name__)
app.secret_key = 'super secret string'

UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__file__)) + "/static/images"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
# app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_DB'] = 'db_assignment'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

def getMysqlConnection():
    connection = mysql.connect()
    cursor = connection.cursor()
    return {"cursor": cursor, "conn": connection}

def getUserList():
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    cursor.execute("SELECT email FROM users;")
    cursor.close()
    conn.close()
    return cursor.fetchall()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''


def getAllPhotos():
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    cursor.execute("SELECT caption, dir FROM photos WHERE album;")
    rows = cursor.fetchall()
    photos = []
    for row in rows:
        photos.append((row[0], str('images/' + row[1])))
    cursor.close()
    conn.close()
    return photos


# default page
@app.route("/", methods=['GET'])
def index():
    photos = getAllPhotos()
    if flask_login.current_user.is_anonymous:
        return render_template('index.html', photos=photos,
                               login=flask_login.current_user.is_authenticated)
    else:
        return render_template('index.html', photos=photos, name=flask_login.current_user.id,
                               login=flask_login.current_user.is_authenticated)


def checkEmail(email):
    # use this to check if a email has already been registered
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    if cursor.execute("SELECT email FROM users WHERE email=%s;", email):
        cursor.close()
        conn.close()
        return True
    else:
        cursor.close()
        conn.close()
        return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html',
                               title='Sign In')

    email = request.form['email']
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    test = checkEmail(email)
    if test:
        print(cursor.execute("SELECT password FROM users WHERE email=%s;", email))
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        pwd = str(data[0][0])
        if request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user)
            session['username'] = email
            return flask.redirect(flask.url_for('index'))  # protected is a function defined in this file
        else:
            return render_template('login.html', title='Sign In', message='Password Incorrect!')
    else:
        print("couldn't find all tokens")
        return render_template('login.html', title='Sign In', message='Email Incorrect!')



@app.route('/profile')
@flask_login.login_required
def profile():
    if request.method == 'GET':
        user = {}
        db = getMysqlConnection()
        conn = db['conn']
        cursor = db['cursor']
        if cursor.execute("SELECT firstname, lastname, email, dateOfBirth, "
                          "homeTown, gender, password FROM users WHERE email=%s;", flask_login.current_user.id):
            for row in cursor.fetchall():
                user['firstname'] = row[0]
                user['lastname'] = row[1]
                user['email'] = row[2]
                user['dateOfBirth'] = row[3]
                user['homeTown'] = row[4]
                user['gender'] = row[5]
                user['password'] = row[6]

        cursor.close()
        conn.close()
        return render_template('profile.html', user=user, name=flask_login.current_user.id,
                               login=flask_login.current_user.is_authenticated)

    import datetime
    register = {}
    try:
        register['email'] = request.form.get('email')
        register['password'] = request.form.get('password')
        register['firstname'] = request.form.get('firstname')
        register['lastname'] = request.form.get('lastname')
        register['dateOfBirth'] = request.form.get('dateOfBirth')
        register['homeTown'] = request.form.get('homeTown')
        register['gender'] = request.form.get('gender')

        if register['dateOfBirth'] != "" and register['dateOfBirth'] is not None:
            dob = datetime.datetime.strptime(register['dateOfBirth'], '%Y-%m-%d')
            if dob >= datetime.datetime.today():
                return render_template('register.html', datebig=True)

        for key, value in register.items():
            if value == '':
                register[key] = 'NULL'

    except ValueError:
        return render_template('register.html', date=True,
                               login=flask_login.current_user.is_authenticated)
    except:
        print("couldn't find all tokens")
        return render_template('register.html', email=True,
                               login=flask_login.current_user.is_authenticated)

    test = isEmailUnique(register['email'])
    print(test)
    if test:
        db = getMysqlConnection()
        conn = db['conn']
        cursor = db['cursor']
        print(cursor.execute("UPDATE users SET " +
                             "firstname = %s, lastname = %s, email = %s, "
                             "dateOfBirth = %s, homeTown = %s, gender = %s, password = %s " +
                             "WHERE email = %s;", (register['firstname'], register['lastname'],
                                                   register['dateOfBirth'], register['homeTown'],
                                                   register['gender'], register['password'],
                                                   register['email'])))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('index.html', name=flask_login.current_user.id, message='Account Created!',
                               login=flask_login.current_user.is_authenticated)
    else:
        return render_template('register.html', email=True,
                               login=flask_login.current_user.is_authenticated)


@app.route('/logout')
def logout():
    photos = getAllPhotos()
    if flask_login.current_user.is_anonymous:
        return render_template('index.html', photos=photos, messages=['Already logged out'],
                               login=flask_login.current_user.is_authenticated)
    else:
        flask_login.logout_user()
        return render_template('index.html', photos=photos, messages=['Logged out'],
                               login=flask_login.current_user.is_authenticated)

@login_manager.unauthorized_handler
def unauthorized_handler():
    return abort(401)


# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress='True',
                           login=flask_login.current_user.is_authenticated)


def isEmailUnique(email):
    # use this to check if a email has already been registered
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    if cursor.execute("SELECT email FROM users WHERE email = %s;", email):
        return False
    else:
        return True

    cursor.close()
    conn.close()


@app.route("/register", methods=['POST'])
def register_user():
    import datetime
    register = {}
    try:
        register['email'] = request.form.get('email')
        register['password'] = request.form.get('password')
        register['firstname'] = request.form.get('firstname')
        register['lastname'] = request.form.get('lastname')
        register['dateOfBirth'] = request.form.get('dateOfBirth')
        register['homeTown'] = request.form.get('homeTown')
        register['gender'] = request.form.get('gender')

        if register['dateOfBirth'] != "" and register['dateOfBirth'] is not None:
            dob = datetime.datetime.strptime(register['dateOfBirth'], '%Y-%m-%d')
            if dob >= datetime.datetime.today():
                return render_template('register.html', datebig=True,
                                       login=flask_login.current_user.is_authenticated)

        for key, value in register.items():
            if value == '':
                register[key] = 'NULL'

    except ValueError:
        return render_template('register.html', date=True,
                               login=flask_login.current_user.is_authenticated)
    except:
        print("couldn't find all tokens")
        return render_template('register.html', email=True,
                               login=flask_login.current_user.is_authenticated)

    test = isEmailUnique(register['email'])

    print(test)

    if test:
        db = getMysqlConnection()
        conn = db['conn']
        cursor = db['cursor']
        print(cursor.execute("INSERT INTO users " +
                             "(firstname, lastname, email, dateOfBirth, homeTown, gender, password) " +
                             "VALUES (%s, %s, %s, %s, %s, %s, %s);", (register['firstname'], register['lastname'],
                                                                       register['email'], register['dateOfBirth'],
                                                                       register['homeTown'], register['gender'],
                                                                       register['password'])))
        conn.commit()
        cursor.close()
        conn.close()
        # log user in
        user = User()
        user.id = register['email']
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('index'))
    else:
        return render_template('register.html', email=True)


def getUsersPhotos(email):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = %s;", email)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def getUserIdFromEmail(email):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    cursor.execute("SELECT id  FROM Users WHERE email = %s;", email)
    id = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return id


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def getAlbumList(email):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    print(cursor.execute("SELECT id, name FROM albums WHERE owner = %s;", getUserIdFromEmail(email)))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    album = []
    for row in rows:
        album.append((row[0], row[1]))
    return album


def savePhotoData(album, caption, dir):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    sql = "INSERT INTO photos (album, caption, dir) VALUES (\"%s\", \"%s\", \"%s\");" % (album, caption, dir)
    print(cursor.execute(sql))
    conn.commit()
    print(cursor.execute("SELECT id FROM photos ORDER BY dateofcreation LIMIT 1;"))
    id = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return id


def savePhotoTags(photoId, tags):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    for tag in tags:
        print(cursor.execute("INSERT INTO tags (photoId, word) VALUES (%s, %s);", (photoId, tag)))

    conn.commit()
    cursor.close()
    conn.close()


@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload():
    album = getAlbumList(flask_login.current_user.id)
    if request.method == 'GET':
        return render_template('upload.html', album_list=album, name=flask_login.current_user.id,
                               login=flask_login.current_user.is_authenticated)

    try:
        album = request.form.get('album')
        file = request.files['photo']
        caption = request.form.get('caption')
        tags = list(set(request.form.get('tags').split(" ")))
        if album == '':
            render_template('upload.html', album_list=album, album='True', name=flask_login.current_user.id,
                            login=flask_login.current_user.is_authenticated)
    except:
        print("couldn't find all tokens")
        return render_template('register.html')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        directory = app.config['UPLOAD_FOLDER']
        name = "/" + str(getUserIdFromEmail(flask_login.current_user.id))
        if not os.path.exists(directory + name):
            os.makedirs(directory + name)

        listOfFiles = [f for f in os.listdir(directory + name)]
        i = 1
        for f in listOfFiles:
            currentfile = f.split(".")[-2]
            if i > int(currentfile) + 1:
                pass
            i = int(currentfile) + 1

        file.save(os.path.join(directory + name, filename))
        source = directory + name + "/" + filename
        extension = str(filename.split(".")[1])

        newname = directory + name + "/" + str(i) + "." + extension
        os.rename(source, newname)

        dir = name + "/" + str(i) + "." + extension

        print(album)
        print(caption)
        print(dir)

        photoId = savePhotoData(album, caption, dir)

        savePhotoTags(photoId, tags)

        return flask.redirect(flask.url_for('index'))

    else:
        render_template('upload.html', album_list=album, reupload='True', name=flask_login.current_user.id,
                        login=flask_login.current_user.is_authenticated)


@app.route('/album', methods=['GET', 'POST'])
@flask_login.login_required
def album():
    album = getAlbumList(flask_login.current_user.id)
    return render_template('album.html', album_list=album, name=flask_login.current_user.id,
                           login=flask_login.current_user.is_authenticated)


@app.route('/make', methods=['POST'])
@flask_login.login_required
def makeAlbum():
    try:
        name = request.form.get('album')
        owner = getUserIdFromEmail(flask_login.current_user.id)

    except:
        return flask.redirect(flask.url_for('album'))

    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    print(cursor.execute("INSERT INTO albums " +
                         "(name, owner) " +
                         "VALUES (%s, %s);", (name, owner)))
    conn.commit()
    cursor.close()
    conn.close()
    return flask.redirect(flask.url_for('album'))


def getAlbumName(id):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    cursor.execute("SELECT name FROM albums WHERE id = %s;", id)
    name = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return name


def getPhotos(album):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    cursor.execute("SELECT caption, dir FROM photos WHERE album = %s;", album)
    rows = cursor.fetchall()
    photos = []
    for row in rows:
        photos.append((row[0], str('images/' + row[1])))
    cursor.close()
    conn.close()
    return photos

@app.route('/view', methods=['GET', 'POST'])
@flask_login.login_required
def makeEdit():
    if request.method == 'GET':
        try:
            id = request.args.get('album')
            owner = getUserIdFromEmail(flask_login.current_user.id)
        except:
            return flask.redirect(flask.url_for('album'))

        album = getAlbumName(id)
        photos = getPhotos(id)
        return render_template('view.html', album_name=album, album_id=id, photos=photos,
                               name=flask_login.current_user.id,
                               login=flask_login.current_user.is_authenticated)

    try:
        id = request.form.get('id')
        name = request.form.get('new')
        owner = getUserIdFromEmail(flask_login.current_user.id)

    except:
        return flask.redirect(flask.url_for('album'))

    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    print(cursor.execute("UPDATE albums SET " +
                         "name = %s, owner = %s " +
                         "WHERE id = %s;", (name, owner, id)))
    conn.commit()
    cursor.close()
    conn.close()
    return flask.redirect(flask.url_for('album'))


# @app.route('/edit/<int:id>', methods=['GET', 'POST'])
# @flask_login.login_required
# def editAlbum(id):
#     db = getMysqlConnection()
#     conn = db['conn']
#     cursor = db['cursor']
#     print(cursor.execute("SELECT name FROM albums WHERE id = %s);", id))
#     album = cursor.fetchone()[0]
#     cursor.close()
#     conn.close()
#     return render_template('view.html', id=id, album=album, name=flask_login.current_user.id)


app.secret_key = 'super secret string'
app.config['SESSION_TYPE'] = 'filesystem'


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True, threaded=True)
