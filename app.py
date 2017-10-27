# coding=utf-8
import flask
from flask import Flask, request, abort, render_template, session
from flaskext.mysql import MySQL
import flask_login
from werkzeug import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'super secret string'

UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__file__)) + "/static/images"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
# app.config['MYSQL_DATABASE_DB'] = 'db_assignment'
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
    if not email or email not in str(users):
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
        userId = row[1].split("/")[1]
        photoId = row[1].split("/")[2].split(".")[0]
        photos.append((row[0], str('images' + row[1]), userId, photoId))
    cursor.close()
    conn.close()
    return photos


# default page
@app.route("/", methods=['GET'])
def index():
    photos = getAllPhotos()
    if not flask_login.current_user.is_authenticated:
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


def findTopUsers():
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT email, id FROM users;")

    users = cursor.fetchall()
    contrib = []
    for user, id in users:
        count = 0

        cursor.execute("SELECT count(*) FROM photos INNER JOIN albums "
                       "ON photos.album=albums.id "
                       "AND albums.owner=%s;", id)

        count = count + cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM comments WHERE user=%s;", id)

        count = count + cursor.fetchone()[0]

        contrib.append((user, count))

    contrib = sorted(contrib, key=lambda x: x[1], reverse=True)[:10]

    users = []
    for user, id in contrib:
        users.append(user)

    cursor.close()
    conn.close()

    return users


@app.route('/top', methods=['GET'])
def top10Users():
    users = findTopUsers()
    if flask_login.current_user.is_authenticated:
        return render_template('top.html', users=users, name=flask_login.current_user.id,
                               login=flask_login.current_user.is_authenticated)

    else:
        return render_template('top.html', users=users,
                               login=flask_login.current_user.is_authenticated)


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
        cursor.execute("SELECT password FROM users WHERE email=%s;", email)

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
            return render_template('login.html', title='Sign In', messages=['Password Incorrect!'])
    else:
        print("couldn't find all tokens")
        return render_template('login.html', title='Sign In', messages=['Email Incorrect!'])


@app.route('/profile', methods=['GET', 'POST'])
@flask_login.login_required
def profile():
    if request.method == 'GET':
        user = {}
        db = getMysqlConnection()
        conn = db['conn']
        cursor = db['cursor']
        if cursor.execute("SELECT firstname, lastname, email, dateOfBirth, "
                          "homeTown, gender, password FROM users WHERE email=%s;", flask_login.current_user.id):
            row = cursor.fetchone()
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
                return render_template('profile.html', datebig=True)

        for key, value in register.items():
            if value == '':
                register[key] = 'NULL'

    except ValueError:
        return render_template('profile.html', date=True,
                               login=flask_login.current_user.is_authenticated)

    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("UPDATE users SET firstname=%s, " +
                   "lastname=%s, dateOfBirth=%s, "
                   "homeTown=%s, gender=%s, password=%s " +
                   "WHERE email=%s;", (register['firstname'], register['lastname'],
                                       register['dateOfBirth'], register['homeTown'],
                                       register['gender'], register['password'],
                                       register['email']))

    conn.commit()
    cursor.close()
    conn.close()
    return flask.redirect(flask.url_for('index'))


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
    if cursor.execute("SELECT email FROM users WHERE email=%s;", email):
        cursor.close()
        conn.close()
        return False
    else:
        cursor.close()
        conn.close()
        return True


@app.route("/register", methods=['POST'])
def register_user():
    import datetime
    register = {}
    try:
        register['email'] = str(request.form.get('email')).lower()
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

    if test:
        db = getMysqlConnection()
        conn = db['conn']
        cursor = db['cursor']
        cursor.execute("INSERT INTO users " +
                       "(firstname, lastname, email, dateOfBirth, homeTown, gender, password) " +
                       "VALUES (%s, %s, %s, %s, %s, %s, %s);", (register['firstname'], register['lastname'],
                                                                register['email'], register['dateOfBirth'],
                                                                register['homeTown'], register['gender'],
                                                                register['password']))
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


def getUserIdFromEmail(email):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT id FROM Users WHERE email=%s;", email)

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

    cursor.execute("SELECT id, name FROM albums WHERE owner=%s;", getUserIdFromEmail(email))

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

    cursor.execute("INSERT INTO photos " +
                   "(album, caption, dir) " +
                   "VALUES (\"%s\", \"%s\", \"%s\");" % (album, caption, dir))

    conn.commit()

    cursor.execute("SELECT id FROM photos WHERE dir LIKE '%%%s%%' ORDER BY dateofcreation LIMIT 1;" % dir)

    id = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return id


def savePhotoTags(photoId, tags):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    for tag in tags:
        if cursor.execute("SELECT id FROM tags WHERE word LIKE '%%%s%%';" % tag):
            cursor.execute("SELECT id FROM tags WHERE word LIKE '%%%s%%';" % tag)

            id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO phototags (photoId, tagId) VALUES (%s, %s);", (photoId, id))

        else:
            cursor.execute("INSERT INTO tags (word) VALUES (%s);", tag)

            conn.commit()

            cursor.execute("SELECT id FROM tags WHERE word LIKE '%%%s%%';" % tag)

            id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO phototags (photoId, tagId) VALUES (%s, %s);", (photoId, id))

    conn.commit()
    cursor.close()
    conn.close()


@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload():
    albumList = getAlbumList(flask_login.current_user.id)
    if request.method == 'GET':
        return render_template('upload.html', album_list=albumList, name=flask_login.current_user.id,
                               login=flask_login.current_user.is_authenticated)

    try:
        album = request.form.get('album')
        file = request.files['photo']
        caption = request.form.get('caption')
        tags = list(set(request.form.get('tags').split(" ")))
        if album == '' or album is None:
            return render_template('upload.html', album_list=albumList, album='True',
                                   name=flask_login.current_user.id,
                                   login=flask_login.current_user.is_authenticated)
    except:
        print("couldn't find all tokens")
        return render_template('upload.html', album_list=albumList, album='True',
                               name=flask_login.current_user.id,
                               login=flask_login.current_user.is_authenticated)

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

        photoId = savePhotoData(album, caption, dir)
        savePhotoTags(photoId, tags)

        return flask.redirect(flask.url_for('index'))

    else:
        render_template('upload.html', album_list=album, reupload='True', name=flask_login.current_user.id,
                        login=flask_login.current_user.is_authenticated)


def getTagList():
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT word FROM tags;")

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    tags = []
    for row in rows:
        tags.append(row[0])
    return tags


@app.route('/album', methods=['GET'])
@flask_login.login_required
def album():
    albums = getAlbumList(flask_login.current_user.id)
    tags = getTagList()
    return render_template('album.html', album_list=albums, tag_list=tags,
                           name=flask_login.current_user.id,
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

    cursor.execute("INSERT INTO albums " +
                   "(name, owner) " +
                   "VALUES (%s, %s);", (name, owner))

    conn.commit()
    cursor.close()
    conn.close()
    return flask.redirect(flask.url_for('album'))


def getAlbumName(id):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT name FROM albums WHERE id=%s;", id)

    name = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return name


def getPhotosFromAlbum(album):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT caption, dir, id FROM photos WHERE album=%s;", album)

    rows = cursor.fetchall()
    photos = []
    for row in rows:
        caption = row[0]
        dir = str('images' + row[1])
        photoId = row[2]
        userId = row[1].split("/")[1]
        photoNo = row[1].split("/")[2].split(".")[0]

        comments = getComments(photoId)

        cursor.execute("SELECT tagId FROM phototags WHERE photoId=%s;", photoId)

        rows = cursor.fetchall()

        tags = []
        for tagId in rows:
            tags.append(getTag(tagId))

        photo = (caption, dir, userId, photoNo, comments, photoId, tags)
        photos.append(photo)

    cursor.close()
    conn.close()
    return photos


@app.route('/view', methods=['GET', 'POST'])
@flask_login.login_required
def makeEdit():
    if request.method == 'GET':
        try:
            id = request.args.get('album')
            if id == '' or id is None:
                return flask.redirect(flask.url_for('album'))
        except:
            return flask.redirect(flask.url_for('album'))

        album = getAlbumName(id)
        photos = getPhotosFromAlbum(id)
        return render_template('view.html', album_name=album, album_id=id, photos=photos,
                               name=flask_login.current_user.id,
                               login=flask_login.current_user.is_authenticated)

    try:
        id = request.form.get('id')
        name = request.form.get('name')

    except:
        return flask.redirect(flask.url_for('album'))

    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("UPDATE albums SET name=%s WHERE id=%s;", (name, id))

    conn.commit()
    cursor.close()
    conn.close()
    return flask.redirect(flask.url_for('album'))


@app.route('/deletealbum', methods=['GET', 'POST'])
@flask_login.login_required
def deleteAlbum():
    if request.method == 'GET':
        return flask.redirect(flask.url_for('view'))

    try:
        id = request.form.get('id')

    except:
        return flask.redirect(flask.url_for('album'))

    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("DELETE FROM albums WHERE id=%s;", id)

    conn.commit()
    cursor.close()
    conn.close()
    return flask.redirect(flask.url_for('album'))


def getPhotosFromTag(tag, email):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    sql = "SELECT caption, dir FROM photos WHERE id IN " \
          "(SELECT photoId FROM phototags WHERE tagId IN " \
          "(SELECT id FROM tags WHERE word LIKE '%%%s%%')) " \
          "AND album IN " \
          "(SELECT id FROM albums WHERE owner=%s);" % (tag, getUserIdFromEmail(email))

    cursor.execute(sql)

    rows = cursor.fetchall()
    photos = []
    for row in rows:
        userId = row[1].split("/")[1]
        photoNo = row[1].split("/")[2].split(".")[0]
        photos.append((row[0], str('images' + row[1]), userId, photoNo))
    cursor.close()
    conn.close()
    return photos


def getAllPhotosFromTag(tag):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT caption, dir FROM photos WHERE id IN " +
                   "(SELECT photoId FROM phototags WHERE tagId IN "
                   "(SELECT id FROM tags WHERE word LIKE '%%%s%%'));" % tag)

    rows = cursor.fetchall()
    photos = []
    for row in rows:
        userId = row[1].split("/")[1]
        photoNo = row[1].split("/")[2].split(".")[0]
        photos.append((row[0], str('images' + row[1]), userId, photoNo))
    cursor.close()
    conn.close()
    return photos


@app.route('/tag', methods=['GET'])
def viewTag():
    try:
        tag = request.args.get('tag')
        type = request.args.get('type')
        if tag == '' or tag is None:
            return flask.redirect(flask.url_for('album'))
    except:
        return flask.redirect(flask.url_for('album'))

    if type == 'tagme':
        if flask_login.current_user.is_authenticated:
            photos = getPhotosFromTag(tag, flask_login.current_user.id)
            return render_template('tag.html', tag_name=tag, photos=photos, viewall=False,
                                   name=flask_login.current_user.id,
                                   login=flask_login.current_user.is_authenticated)
        else:
            url = '/tag?type=tagall&tag=' + str(tag)
            return flask.redirect(url)

    else:
        photos = getAllPhotosFromTag(tag)
        if flask_login.current_user.is_authenticated:
            return render_template('tag.html', tag_name=tag, photos=photos, viewall=True,
                                   name=flask_login.current_user.id,
                                   login=flask_login.current_user.is_authenticated)
        else:
            return render_template('tag.html', tag_name=tag, photos=photos, viewall=True,
                                   login=flask_login.current_user.is_authenticated)


def getComments(photoId):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT text FROM comments WHERE photoId=%s;", photoId)

    rows = cursor.fetchall()
    comments = []
    for row in rows:
        comments.append(row[0])
    cursor.close()
    conn.close()
    return comments


def getPhoto(dir):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT caption, dir, id FROM photos WHERE dir LIKE '%%%s%%';" % str(dir))

    row = cursor.fetchone()

    caption = row[0]
    dir = str('images' + row[1])
    photoId = row[2]
    userId = row[1].split("/")[1]
    photoNo = row[1].split("/")[2].split(".")[0]

    comments = getComments(photoId)

    cursor.execute("SELECT tagId FROM phototags WHERE photoId=%s;", photoId)

    rows = cursor.fetchall()

    tags = []
    for tagId in rows:
        tags.append(getTag(tagId))

    photo = (caption, dir, userId, photoNo, comments, photoId, tags)

    cursor.close()
    conn.close()
    return photo


def getLikeNumber(photoId):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT count(*) FROM likes WHERE photo=%s;", photoId)

    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count


def checkLike(photoId, userId):
    # use this to check if a email has already been registered
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    if cursor.execute("SELECT * FROM likes WHERE photo=%s AND user=%s;", (photoId, userId)):
        cursor.close()
        conn.close()
        return True
    else:
        cursor.close()
        conn.close()
        return False


@app.route('/view/<int:userId>/<int:photoId>', methods=['GET', 'POST'])
def editPhoto(userId, photoId):
    dir = '/' + str(userId) + '/' + str(photoId)
    photo = getPhoto(dir)
    noOfLikes = getLikeNumber(photo[5])
    if request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            likes = checkLike(photo[5], getUserIdFromEmail(flask_login.current_user.id))
            return render_template('photo.html', photo=photo, likes=likes, noOfLikes=noOfLikes,
                                   name=flask_login.current_user.id,
                                   login=flask_login.current_user.is_authenticated)
        else:
            return render_template('photo.html', photo=photo, noOfLikes=noOfLikes,
                                   login=flask_login.current_user.is_authenticated)
    try:
        comment = request.form.get('comment')
        photoId = request.form.get('photoId')

    except:
        return flask.redirect(request.path)

    if flask_login.current_user.is_authenticated:
        db = getMysqlConnection()
        conn = db['conn']
        cursor = db['cursor']

        id = getUserIdFromEmail(flask_login.current_user.id)

        cursor.execute("INSERT INTO comments " +
                       "(user, photoId, text) " +
                       "VALUES (%s, %s, %s);", (id, photoId, comment))

        conn.commit()
        cursor.close()
        conn.close()
        return flask.redirect(request.path)


def getTag(tagId):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT word FROM tags WHERE id=%s;", tagId)

    word = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    return word


def findTopTags():
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT photoId, tagId, count(*) AS ct FROM phototags " +
                   "GROUP BY tagId ORDER BY ct DESC;")

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    tags = []
    for photoId, tagId, ct in rows:
        tags.append(getTag(tagId))

    tags = tags[:10]

    return tags


def getEmailFromUserId(id):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT email FROM users WHERE id=%s;", id)

    email = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return email


def findFriends(email):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    id = getUserIdFromEmail(email)

    cursor.execute("SELECT friendId AS frid, count(friendId) AS ct FROM friends " +
                   "WHERE userId IN (SELECT friendId FROM friends WHERE userId=%s) " +
                   "GROUP BY friendId HAVING ct > 1 " +
                   "AND frid NOT IN (SELECT friendId FROM friends WHERE userId=%s) " +
                   "ORDER BY ct;", (id, id))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    friends = []
    for friendId, ct in rows:
        friends.append(getEmailFromUserId(friendId))

    return friends


def getPhotoFromId(photoId):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT caption, dir, id FROM photos WHERE id=%s;", photoId)

    row = cursor.fetchone()

    caption = row[0]
    dir = str('images' + row[1])
    userId = row[1].split("/")[1]
    photoNo = row[1].split("/")[2].split(".")[0]

    comments = getComments(photoId)

    cursor.execute("SELECT tagId FROM phototags WHERE photoId=%s;", photoId)

    rows = cursor.fetchall()

    tags = []

    for tagId in rows:
        tags.append(getTag(tagId))

    photo = (caption, dir, userId, photoNo, comments, photoId, tags)

    cursor.close()
    conn.close()
    return photo


def getRecommendedPhotos():
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT photoid, count(photoId) AS ctr FROM phototags " +
                   "JOIN " +
                   "(SELECT tagId FROM phototags GROUP BY tagId ORDER BY count(tagId) DESC limit 5) t1 " +
                   "ON " +
                   "phototags.tagId = t1.tagId " +
                   "GROUP BY photoId ORDER BY ctr DESC;")

    rows = cursor.fetchall()

    photoIdList = []
    skipnext = False
    for i in range(len(rows)):
        if not skipnext:
            if i < (len(rows) - 1):
                if rows[i][1] == rows[i + 1][1]:
                    cursor.execute("SELECT photoId, count(photoId) FROM phototags WHERE " +
                                   "photoId=%s or photoId=%s " +
                                   "GROUP BY photoId " +
                                   "ORDER BY count(photoId) ASC;", (rows[i][0], rows[i][0]))

                    conflict = cursor.fetchone()
                    photoIdList.append(conflict[0])

                    skipnext = True
                else:
                    photoIdList.append(rows[i][0])
            else:
                photoIdList.append(rows[i][0])

        else:
            skipnext = False

    cursor.close()
    conn.close()

    photos = []
    for id in photoIdList:
        photos.append(getPhotoFromId(id))

    return photos


@app.route('/explore', methods=['GET'])
def explore():
    tags = findTopTags()
    users = findFriends(flask_login.current_user.id)
    photos = getRecommendedPhotos()
    return render_template('explore.html', tags=tags, users=users, photos=photos,
                           name=flask_login.current_user.id,
                           login=flask_login.current_user.is_authenticated)


def getFriendResult(userEmail, friendEmail):
    uesrId = getUserIdFromEmail(userEmail)
    friendId = getUserIdFromEmail(friendEmail)
    resultIds = []
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    if cursor.execute("SELECT friendId FROM friends WHERE " +
                              "userId=%s AND friendId=%s;", (uesrId, friendId)):
        return True

    elif cursor.execute("SELECT friendId FROM friends WHERE " +
                                "friendId=%s AND userId=%s;", (uesrId, friendId)):
        return True

    else:
        return False


@app.route('/user', methods=['GET', 'POST'])
def friend():
    if request.method == 'GET':
        friendId = request.args.get('id')
        user = {}
        db = getMysqlConnection()
        conn = db['conn']
        cursor = db['cursor']
        if cursor.execute("SELECT firstname, lastname, email, dateOfBirth, "
                          "homeTown, gender, password FROM users WHERE email=%s;", friendId):
            row = cursor.fetchone()
            user['firstname'] = row[0]
            user['lastname'] = row[1]
            user['email'] = row[2]
            user['dateOfBirth'] = row[3]
            user['homeTown'] = row[4]
            user['gender'] = row[5]
            user['password'] = row[6]

        cursor.close()
        conn.close()
        if flask_login.current_user.is_authenticated:
            friendCheck = getFriendResult(flask_login.current_user.id, user['email'])
            return render_template('user.html', user=user, friendCheck=friendCheck,
                                   name=flask_login.current_user.id,
                                   login=flask_login.current_user.is_authenticated)
        else:
            return render_template('user.html', user=user,
                                   login=flask_login.current_user.is_authenticated)

    user = {}
    try:
        user['email'] = request.form.get('email')
        user['password'] = request.form.get('password')
        user['firstname'] = request.form.get('firstname')
        user['lastname'] = request.form.get('lastname')
        user['dateOfBirth'] = request.form.get('dateOfBirth')
        user['homeTown'] = request.form.get('homeTown')
        user['gender'] = request.form.get('gender')

    except ValueError:
        return render_template('user.html', user=user, name=flask_login.current_user.id,
                               login=flask_login.current_user.is_authenticated)

    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("INSERT INTO friends " +
                   "(userId, friendId) " +
                   "VALUES (%s, %s);", (getUserIdFromEmail(user['email']),
                                        getUserIdFromEmail(flask_login.current_user.id)))

    cursor.execute("INSERT INTO friends " +
                   "(userId, friendId) " +
                   "VALUES (%s, %s);", (getUserIdFromEmail(flask_login.current_user.id),
                                        getUserIdFromEmail(user['email'])))

    conn.commit()
    cursor.close()
    conn.close()
    return flask.redirect(flask.url_for('index'))


@app.route('/like', methods=['GET', 'POST'])
@flask_login.login_required
def like():
    if request.method == 'GET':
        return flask.redirect(flask.url_for('index'))

    try:
        photoId = request.form.get('photoId')

    except ValueError:
        return flask.redirect(flask.url_for('index'))

    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("INSERT INTO likes " +
                   "(photo, user) " +
                   "VALUES (%s, %s);", (photoId,
                                        getUserIdFromEmail(flask_login.current_user.id)))

    conn.commit()
    cursor.close()
    conn.close()
    return flask.redirect(flask.url_for('index'))


def searchComment(comment):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT photoId FROM comments WHERE text LIKE '%%%s%%';" % comment)

    rows = cursor.fetchall()

    results = []
    for row in rows:
        results.append(getPhotoFromId(row[0]))

    print(results)

    cursor.close()
    conn.close()
    return results


def searchEmail(email):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT email FROM users WHERE email LIKE '%%%s%%';" % email)

    rows = cursor.fetchall()

    results = []
    for row in rows:
        results.append(row[0])

    cursor.close()
    conn.close()
    return results


def searchTag(tags):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    results = []

    for tag in tags:
        cursor.execute("SELECT word FROM tags WHERE word LIKE '%%%s%%';" % tag)

        rows = cursor.fetchall()
        for row in rows:
            results.append(row[0])

    cursor.close()
    conn.close()
    return results


@app.route('/search', methods=['GET'])
def search():
    searchType = request.args.get('type')
    query = request.args.get('search')

    if searchType == 'comment':
        result = searchComment(query)
        if flask_login.current_user.is_authenticated:
            return render_template('search.html', photos=result, name=flask_login.current_user.id,
                                   tagSearch=False, userSearch=False, commentSearch=True,
                                   login=flask_login.current_user.is_authenticated)
        else:
            return render_template('search.html', photos=result,
                                   tagSearch=False, userSearch=False, commentSearch=True,
                                   login=flask_login.current_user.is_authenticated)

    elif searchType == 'email':
        result = searchEmail(query)
        if flask_login.current_user.is_authenticated:
            return render_template('search.html', users=result, name=flask_login.current_user.id,
                                   tagSearch=False, userSearch=True, commentSearch=False,
                                   login=flask_login.current_user.is_authenticated)
        else:
            return render_template('search.html', users=result,
                                   tagSearch=False, userSearch=True, commentSearch=False,
                                   login=flask_login.current_user.is_authenticated)
    else:
        result = searchTag(list(set(query.split(" "))))
        if flask_login.current_user.is_authenticated:
            return render_template('search.html', tags=result, name=flask_login.current_user.id,
                                   tagSearch=True, userSearch=False, commentSearch=False,
                                   login=flask_login.current_user.is_authenticated)
        else:
            return render_template('search.html', tags=result,
                                   tagSearch=True, userSearch=False, commentSearch=False,
                                   login=flask_login.current_user.is_authenticated)


def getFriendList(email):
    id = getUserIdFromEmail(email)
    resultIds = []
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    cursor.execute("SELECT DISTINCT friendId FROM friends WHERE " +
                   "userId=%s AND NOT friendId=%s;", (id, id))

    rows = cursor.fetchall()
    for row in rows:
        resultIds.append(row[0])

    cursor.execute("SELECT DISTINCT userId FROM friends WHERE " +
                   "friendId=%s AND NOT userId=%s;", (id, id))

    rows = cursor.fetchall()
    for row in rows:
        resultIds.append(row[0])
        resultIds = sorted(set(resultIds))

    results = []

    for result in resultIds:
        results.append(getEmailFromUserId(result))

    cursor.close()
    conn.close()
    return results


@app.route('/friendlist', methods=['GET'])
@flask_login.login_required
def friendlist():
    result = getFriendList(flask_login.current_user.id)

    return render_template('friends.html', users=result, name=flask_login.current_user.id,
                           login=flask_login.current_user.is_authenticated)


app.secret_key = 'super secret string'
app.config['SESSION_TYPE'] = 'filesystem'

if __name__ == "__main__":
    app.jinja_env.cache = {}
    app.run(port=5000, debug=True, threaded=True)
