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
    print(cursor.execute("SELECT email, id FROM users;"))
    users = cursor.fetchall()
    contrib = []
    for user, id in users:
        count = 0

        print(cursor.execute("SELECT count(*) FROM photos INNER JOIN albums "
                             "ON photos.album = albums.id "
                             "AND albums.owner = %s;", id))
        count = count + cursor.fetchone()[0]

        print(cursor.execute("SELECT count(*) FROM comments WHERE user = %s;", id))
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

    print(cursor.execute("UPDATE users SET " +
                         "firstname = %s, lastname = %s, dateOfBirth = %s, "
                         "homeTown = %s, gender = %s, password = %s " +
                         "WHERE email = %s;", (register['firstname'], register['lastname'],
                                               register['dateOfBirth'], register['homeTown'],
                                               register['gender'], register['password'],
                                               register['email'])))
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
    cursor.execute("SELECT id FROM Users WHERE email = %s;", email)
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


def getTagList():
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']

    print(cursor.execute("SELECT word FROM tags;"))

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


def getPhotosFromAlbum(album):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    cursor.execute("SELECT caption, dir FROM photos WHERE album = %s;", album)
    rows = cursor.fetchall()
    photos = []
    for row in rows:
        userId = row[1].split("/")[1]
        photoId = row[1].split("/")[2].split(".")[0]
        photos.append((row[0], str('images' + row[1]), userId, photoId))
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


def getPhotosFromTag(tag, email):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    cursor.execute("SELECT caption, dir FROM photos WHERE "
                   "id IN " +
                   "(SELECT photoId FROM tags WHERE word LIKE '%%%s%%') "
                   "AND album IN "
                   "(SELECT id FROM albums WHERE owner = %s);" % (tag, getUserIdFromEmail(email)))

    rows = cursor.fetchall()
    photos = []
    for row in rows:
        userId = row[1].split("/")[1]
        photoId = row[1].split("/")[2].split(".")[0]
        photos.append((row[0], str('images' + row[1]), userId, photoId))
    cursor.close()
    conn.close()
    return photos


def getAllPhotosFromTag(tag):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    cursor.execute("SELECT caption, dir FROM photos WHERE id IN " +
                   "(SELECT photoId FROM tags WHERE word LIKE '%%%s%%');" % tag)
    rows = cursor.fetchall()
    photos = []
    for row in rows:
        userId = row[1].split("/")[1]
        photoId = row[1].split("/")[2].split(".")[0]
        photos.append((row[0], str('images' + row[1]), userId, photoId))
    cursor.close()
    conn.close()
    return photos


@app.route('/tag', methods=['GET'])
@flask_login.login_required
def viewTag():
    try:
        tag = request.args.get('tag')
        type = request.args.get('type')
        if tag == '' or tag is None:
            return flask.redirect(flask.url_for('album'))
    except:
        return flask.redirect(flask.url_for('album'))

    if type == 'tagme':
        photos = getPhotosFromTag(tag, flask_login.current_user.id)
        return render_template('tag.html', tag_name=tag, photos=photos, viewall=False,
                               name=flask_login.current_user.id,
                               login=flask_login.current_user.is_authenticated)
    else:
        photos = getAllPhotosFromTag(tag)
        print(photos)
        return render_template('tag.html', tag_name=tag, photos=photos, viewall=True,
                               name=flask_login.current_user.id,
                               login=flask_login.current_user.is_authenticated)


def getComments(photoId):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    print("SELECT text FROM comments WHERE photo_id = %s;" % str(photoId))
    print(cursor.execute("SELECT text FROM comments WHERE photo_id = %s;", photoId))
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
    print(cursor.execute("SELECT caption, dir, id FROM photos WHERE dir LIKE '%%%s%%';" % str(dir)))
    row = cursor.fetchone()

    userId = row[1].split("/")[1]
    photoId = row[1].split("/")[2].split(".")[0]

    comments = getComments(photoId)

    photo = (row[0], str('images' + row[1]), userId, photoId, comments)

    cursor.close()
    conn.close()
    return photo


@app.route('/view/<int:userId>/<int:photoId>', methods=['GET', 'POST'])
def editPhoto(userId, photoId):
    dir = '/' + str(userId) + '/' + str(photoId)
    photo = getPhoto(dir)
    if request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            return render_template('photo.html', photo=photo,
                                   name=flask_login.current_user.id,
                                   login=flask_login.current_user.is_authenticated)
        else:
            return render_template('photo.html', photo=photo,
                                   login=flask_login.current_user.is_authenticated)
    try:
        comment = request.form.get('comment')

    except:
        return flask.redirect(request.path)

    if flask_login.current_user.is_authenticated:
        db = getMysqlConnection()
        conn = db['conn']
        cursor = db['cursor']

        id = getUserIdFromEmail(flask_login.current_user.id)

        print(cursor.execute("INSERT INTO comments " +
                             "(user, photo_id, text) " +
                             "VALUES (%s, %s, %s);", (id, photoId, comment)))

        conn.commit()
        cursor.close()
        conn.close()
        return flask.redirect(request.path)


def findTopTags():
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    print(cursor.execute("SELECT photoId, word, count(*) AS ct FROM tags " +
                         "GROUP BY word ORDER BY ct, word DESC;"))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    tags = []
    for photoId, word, ct in rows:
        tags.append(word)

    tags = tags[:10]

    return tags


def getEmailFromUserId(id):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    cursor.execute("SELECT email FROM Users WHERE id = %s;", id)
    email = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return email

def findFriends(email):
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    id = getUserIdFromEmail(email)
    print(cursor.execute("SELECT friendId AS frid, count(friendId) AS ct FROM friends " +
                         "WHERE userId IN (SELECT friendId FROM friends WHERE userId = %s) " +
                         "GROUP BY friendId HAVING ct > 1 " +
                         "AND frid NOT IN (SELECT friendId FROM friends WHERE userId = %s) " +
                         "ORDER BY ct;", (id, id)))

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
    print(cursor.execute("SELECT caption, dir, id FROM photos WHERE id=%s;", photoId))
    row = cursor.fetchone()

    userId = row[1].split("/")[1]
    photoId = row[1].split("/")[2].split(".")[0]

    comments = getComments(photoId)

    photo = (row[0], str('images' + row[1]), userId, photoId, comments)

    cursor.close()
    conn.close()
    return photo


def getRecommendedPhotos():
    db = getMysqlConnection()
    conn = db['conn']
    cursor = db['cursor']
    print(cursor.execute("SELECT photoid, count(photoId) AS ctr FROM tags " +
                         "JOIN " +
                         "(SELECT word FROM tags GROUP BY word ORDER BY count(word) DESC limit 5) t1 " +
                         "ON " +
                         "tags.word = t1.word " +
                         "GROUP BY photoId ORDER BY ctr DESC;"))

    rows = cursor.fetchall()

    photoIdList = []
    skipnext = False
    for i in range(len(rows)):
        if not skipnext:
            if i < (len(rows) - 1):
                if rows[i][1] == rows[i + 1][1]:
                    print(cursor.execute("SELECT photoId, count(photoId) FROM tags WHERE " +
                                         "photoId = %s or photoId = %s " +
                                         "GROUP BY photoId " +
                                         "ORDER BY count(photoId) ASC;", (rows[i][0], rows[i][0])))
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


app.secret_key = 'super secret string'
app.config['SESSION_TYPE'] = 'filesystem'

if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True, threaded=True)
