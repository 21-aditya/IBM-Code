import os,re
import MySQLdb.cursors
from flask import Flask, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from ibm_watson_machine_learning import APIClient
import tarfile
from keras.models import load_model
from keras.preprocessing import image
import numpy as np

WMLCredentials = {
    "url": "https://eu-de.ml.cloud.ibm.com",
    "apikey": "otPqZJ572G9Kvgqd5eTuHSeZ-ktrTokqdXvWd8kaFXLv"
}
client = APIClient(WMLCredentials)
client.set.default_space("12f0d23b-8918-45db-a632-01c21bee5035")
model_id = "7a55f72e-8a35-4f60-891e-ae833db7f9d6"

try:
    client.repository.download(model_id, 'dn.tgz')
    model = tarfile.open('dn.tgz')
    model.extractall('/Users/adityaramachandran/Library/CloudStorage/OneDrive-Personal/Documents/Sem-7/IBM-Project/IBM-Code')
    model.close()
except:
    print("File exists!!")

app = Flask(__name__)
app.secret_key = 'abc123'
UPLOAD_FOLDER = os.path.join('static', 'uploads')

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Jan2021!'
app.config['MYSQL_DB'] = 'ibmproj'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    msg = '' # Output message
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/uploaded', methods=['GET','POST'])
def uploaded():
    if 'loggedin' in session:
        if request.method=='POST':
            imagereceived = request.files['imageUpload']
            img_filename = secure_filename(imagereceived.filename)
            imagereceived.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
            print(imagereceived)
            return redirect(url_for('showimage', filename=img_filename))
        return render_template('home.html', uploaded_image=os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
    return redirect(url_for('login'))

@app.route('/showimage')
def showimage():
    if 'loggedin' in session:
        img_filename = request.args['filename']
        model = load_model('model_wo_aug.h5')
        classes = ['Corpse Flower','Great Indian Bustard Bird','Lady Slipper Orchid Flower',
                   'Pangolin Mammal','Senenca White Deer Mammal','Spoon Billed Sandpiper Bird']

        img = image.load_img(os.path.join(app.config['UPLOAD_FOLDER'], img_filename), target_size=(64, 64))
        img = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        pred = np.argmax(model.predict(img), axis=1)
        print(pred)
        print('Prediction: ', classes[pred[0]])
        return render_template('showimage.html', uploaded_image=os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM accounts WHERE username = %s OR email = %s', (username,email))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute(
                'INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s',
                       (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/history')
def history():
    # ---------INSERTING AN IMAGE-----------
    '''
    cursor = mysql.connection.cursor()
    file = open('static/apple_colour.jpg','rb').read()
    file = base64.b64encode(file) # We must encode the file to get base64 string
    cursor.execute('INSERT INTO IMAGETABLE (IMAGE) VALUES (%s)', (file,))
    mysql.connection.commit()
    '''
    # ----------SELECTING AN IMAGE----------
    '''
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT IMAGE FROM IMAGETABLE WHERE ID = 1 ')
    data = cursor.fetchall()
    # The returned data will be a list of lists
    image = data[0][0]
    # Decode the string
    binary_data = base64.b64decode(image)
    image = Image.open(io.BytesIO(binary_data))
    '''
    return render_template('carousel.html')
