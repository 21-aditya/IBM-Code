from flask import Flask, render_template, request, redirect, url_for, session
#from flask_mysqldb import MySQL
import base64
from PIL import Image
import io

app = Flask(__name__)
app.secret_key = 'hello'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Vasu$0308'
app.config['MYSQL_DB'] = 'ibm'


#mysql = MySQL(app) #SETTING MYSQL CONNECTION

@app.route('/')
def index():  

    #---------INSERTING AN IMAGE-----------
    '''
    cursor = mysql.connection.cursor()
    file = open('static/apple_colour.jpg','rb').read()
    file = base64.b64encode(file) # We must encode the file to get base64 string
    cursor.execute('INSERT INTO IMAGETABLE (IMAGE) VALUES (%s)', (file,))
    mysql.connection.commit()
    '''
    #----------SELECTING AN IMAGE----------
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
    return render_template('image.html')

    #image.show()

if __name__ ==  "__main__":
    app.run(debug=True)