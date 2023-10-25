from flask import Flask, Response, render_template,redirect,request,jsonify,g
from flask import url_for, flash,session,send_from_directory,send_file
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
import pandas as pd
from io import BytesIO
import cv2
from mtcnn.mtcnn import MTCNN
from imutils.video import VideoStream
import face_recognition
import imutils
import pickle
import time
import psycopg2
import psycopg2.extras
import serial
import os
from imutils import paths
import numpy as np
import uuid
import shutil
from flask import Flask, render_template,request, redirect, url_for
import os
import shutil
import datetime
from openpyxl import load_workbook
from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2 #pip install psycopg2 
import psycopg2.extras
import requests
app = Flask(__name__)
app.secret_key = '0811254Kk@'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


url = 'https://notify-api.line.me/api/notify'
token = 'G4JlVIkXZmgVCa2UhWa6VTGXCUZqSbC0lJn3DuBBPHv'
message = "Hello World"

headers = {
    'Authorization': f'Bearer {token}'
}

sensor_value=""

UPLOAD_FOLDER='static/images/datasets'
UPLOAD='static/images/detection'
# # Define the path to the folder containing your images
IMAGE_FOL4DER = os.path.join(os.getcwd(), 'static/images/detection')
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['UPLOAD']=UPLOAD
messages = []
conn=psycopg2.connect(database="dormitory",user="postgres",password="1234",
                      host="localhost",port="5432")

def get_notifications(user_id):
    conn = psycopg2.connect(
        database="dormitory", user="postgres", password="1234", host="localhost", port="5432"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("SELECT o.* FROM overview o LEFT JOIN read r ON o.ids = r.overview_id WHERE r.user_id IS NULL OR r.user_id != %s",(user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_data_notifications(user_id):
    conn = psycopg2.connect(
        database="dormitory", user="postgres", password="1234", host="localhost", port="5432"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Count the number of rows returned by the SQL query
    cursor.execute("""
        SELECT COUNT(o.*) 
        FROM overview o 
        LEFT JOIN read r ON o.ids = r.overview_id 
        WHERE r.user_id IS NULL OR r.user_id != %s
    """, (user_id,))
    
    count = cursor.fetchone()[0]  # Fetch the count value

    conn.close()
    return count

app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        name=request.form['name']
        lastname=request.form['lastname']
        username=request.form['username']
        password=request.form['password']
        confirm_password=request.form['confirm_password']
        if not (name or lastname or username or password or confirm_password):
            err="Please provided name lastname username password and confirm password"
            return render_template('signup.html',err=err)
        if(password==confirm_password):
            conn = psycopg2.connect(
                database="dormitory", user="postgres", password="1234", host="localhost", port="5432"
            )
            conn.autocommit = True
            cursor=conn.cursor()
            cmd="INSERT INTO users(name,lastname,username,password) VALUES(%s,%s,%s,%s)"
            cursor.execute(cmd,(name,lastname,username,password))
            cursor.close()
            conn.close()
            message="Register are Successfully"
            return render_template('home.html',message=message)
        else:
            error="Password does not matches"
            return render_template('signup.html',error=error)
    else:
        return redirect(url_for('signup'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = psycopg2.connect(
            database="dormitory", user="postgres", password="1234", host="localhost", port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', 
                       (username, password))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            # Storing user data in the session
            session['username'] = user[3]  # Assuming username is at index 3
            session['user_id'] = user[0]  # Assuming user ID is at index 0
            session['name']=user[1]
            session['lastname']=user[2]
            message="Login Successfully"
            return redirect(url_for('home'))
        else:
            error = "Username or Password does not match."
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/home')
def home():
    if 'username' in session:
        username = session['username']
        user_id = session['user_id']
        name=session['name']
        lastname=session['lastname']
        notifications=get_notifications(user_id)
        count=get_data_notifications(user_id)
        return render_template('home.html',notifications=notifications,name=name,lastname=lastname,count=count)
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))



@app.route('/notify/<int:ids>')
def notify(ids):
    def getprofile(ids):
        conn = psycopg2.connect(
            database="dormitory", user="postgres", password="1234", host="localhost", port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM overview WHERE ids = %s", (ids,))
        notification = cursor.fetchone()
        return notification
    def insertId(user_id,id,formatted_datetime):
        conn = psycopg2.connect(
            database="dormitory", user="postgres", password="1234", host="localhost", port="5432"
        )
        conn.autocommit = True
        cursor=conn.cursor()
        cmd="INSERT INTO read(user_id,overview_id,datetimes) VALUES(%s,%s,%s)"
        cursor.execute(cmd,(user_id,ids,formatted_datetime))
        cursor.close()
        conn.close()
    if 'username' in session:
        username = session['username']
        user_id = session['user_id']
        name=session['name']
        lastname=session['lastname']
        count=get_data_notifications(user_id)
        notifications=get_notifications(user_id)
        notification=getprofile(ids)
        # Get the current date and time
        current_datetime = datetime.datetime.now()

# Format the datetime to include microseconds
        formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

        ids=notification[0]
        insertId(user_id,id,formatted_datetime)
        return render_template('notify.html',notification=notification,notifications=notifications, name=session['name'],lastname=session['lastname'],count=count) 
    else:
        return redirect(url_for('login'))
    

@app.route('/member/<int:ids>')
def member(ids):
    if 'username' in session:
        username = session['username']
        user_id = session['user_id']
        name=session['name']
        lastname=session['lastname']
        notifications=get_notifications(user_id)
        count=get_data_notifications(user_id)
        conn = psycopg2.connect(
            database="dormitory", user="postgres", password="1234", host="localhost", port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members WHERE ids = %s", (ids,))
        dataset = cursor.fetchone()
        if dataset:
            dataset=dataset[1]
            folder_path=os.path.join('static','images','datasets',dataset)
            image_files = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png', '.gif','.jpeg','.webb'))]
            return render_template('output.html',dataset=dataset,image_files=image_files,notifications=notifications, name=session['name'],lastname=session['lastname'],count=count)
        else:
            return redirect(url_for('login'))
  
@app.route('/overview', methods=['GET', 'POST'])
def overview():
    search_date = None
    products = []
   
    if 'username' in session:
        username = session['username']
        user_id = session['user_id']
        name=session['name']
        lastname=session['lastname']
        count=get_data_notifications(user_id)
        notifications=get_notifications(user_id)
        #dates=request.form['search_date']
        if request.method == 'POST':
        # Get the date input from the form
            search_date = request.form['search_date']
        # Connect to the PostgreSQL database
            conn=psycopg2.connect(
                    database="dormitory",user="postgres",password="1234",host="localhost",port="5432"
            )
            conn.autocommit = True
            cursor=conn.cursor()
        # Execute a query to search for products by date
            cursor.execute("SELECT * FROM overview WHERE dmy = %s", (search_date,))
            products = cursor.fetchall()

            conn.close()
        return render_template('overview.html', products=products,search_date=search_date,notifications=notifications,name=session['name'],lastname=session['lastname'],count=count)
    else:
        return redirect(url_for('login'))
    
    
@app.route('/edit_subfolder/<int:ids>', methods=['GET', 'POST'])
def edit_subfolder(ids):
    if request.method == 'GET':
        #notifications=get_notifications()
        conn = psycopg2.connect(
            database="dormitory", user="postgres", password="1234", host="localhost", port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members WHERE ids = %s", (ids,))
        dataset = cursor.fetchone()
        if 'username' in session:
            username = session['username']
            user_id = session['user_id']
            name=session['name']
            lastname=session['lastname']
            return render_template('member.html', datasets=[], edit_subfolder=dataset,notifications=notifications,name=session['name'],lastname=session['lastname'],count=count)
    elif request.method == 'POST':
        #notifications=get_notifications()
        name_lastname = request.form['name_lastname']
        old_name=request.form['old_name']
        conn = psycopg2.connect(
            database="dormitory", user="postgres", password="1234", host="localhost", port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("UPDATE members SET name_lastname = %s WHERE ids = %s", (name_lastname, ids))
        conn.commit()

        # Folder renaming code
        folder_path = 'static/images/datasets'
        old_folder_name = os.path.join(folder_path,old_name)  # Create the old folder path
        new_folder_name = os.path.join(folder_path, name_lastname)  # Create the new folder path

        try:
            os.rename(old_folder_name, new_folder_name)  # Rename the folder
            # flash('Computer between processing faces', 'success')
            print('[INFO] Start Processing Faces....')
        
            return redirect(url_for('dataset'),)
        except Exception as e:
            return f"Error renaming folder: {str(e)}"  # Handle any errors here
       
 
@app.route('/delete_subfolder/<int:ids>', methods=['POST'])
def delete_subfolder(ids):
    # Fetch the image filename from the database
    conn=psycopg2.connect(
        database="dormitory",user="postgres",password="1234",host="localhost",port="5432"
    )
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE ids = %s", (ids,))
    dataset = cursor.fetchone()
    cursor.close()

    # Delete the image file from the folder
    if dataset:
        dataset[1]
        # Construct the full path to the image
        folder_path = 'static/images/datasets'  # Path to your subfolders directory
        folder_to_delete = os.path.join(folder_path,dataset[1])

        # Check if the file exists
        if os.path.exists(folder_to_delete) and os.path.isdir(folder_to_delete):
            shutil.rmtree(folder_to_delete)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM members WHERE ids = %s',(dataset[0],))
        conn.commit()
        cursor.close()
        flash('Computer between processing faces', 'success')
        print('[INFO] Start Processing Faces....')
        imgPaths=list(paths.list_images('static/images/datasets'))

        knowEncodings=[]
        knowNames=[]

        for (i,imgPath) in enumerate(imgPaths):
            print('[INFO] Processing Faces {}/{}'.format(i+1,len(imgPaths)))
            name=imgPath.split(os.path.sep)[-2]
            img=cv2.imread(imgPath)
            rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    
            boxes=face_recognition.face_locations(rgb,model='hog')
            encodings=face_recognition.face_encodings(rgb,boxes)

            for encoding in encodings:
                knowEncodings.append(encoding)
                knowNames.append(name)
        print('[INFO] Serializing Encodings....')
        data={'encodings':knowEncodings,'names':knowNames}
        f=open('recognizer/trainer.yml','wb')
        f.write(pickle.dumps(data))
        f.close()
        flash('Finish Processing faces', 'success')
    return redirect(url_for('dataset'))

@app.route('/edit_product/<int:ids>', methods=['GET','POST'])
def edit_product(ids):
    if request.method == 'GET':
        notifications=get_notifications()
        conn=psycopg2.connect(
                    database="dormitory",user="postgres",password="1234",host="localhost",port="5432"
        )
        conn.autocommit = True
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM overview WHERE ids = %s", (ids,))
        product= cursor.fetchone()
        return render_template('overview.html',products=[], edit_product=product,notifications=notifications,count=count)
    elif request.method == 'POST':
        notifications=get_notifications()
        name_lastname = request.form['name_lastname']
        old_name = request.form['old_name']
        imgdetect = request.form['imgdetect']
    
        conn=psycopg2.connect(
            database="dormitory",user="postgres",password="1234",host="localhost",port="5432"
        )
        conn.autocommit = True
        cursor=conn.cursor()
        cursor.execute("UPDATE overview SET name_lastname = %s, imgdetect = %s WHERE ids = %s", (name_lastname, imgdetect, ids))
        conn.commit()
        old_path = os.path.join(app.config['UPLOAD'], old_name)
        new_path = os.path.join(app.config['UPLOAD'], imgdetect)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
       
        flash('Overview updated successfully this id', 'success')  # 'success' is a CSS class for the alert style
        return render_template('overview.html', products=[], edit_product=None,notifications=notifications,count=count)  # Rendering the same page again
        

@app.route('/delete_product/<int:ids>', methods=['POST'])
def delete_product(ids):
    # Fetch the image filename from the database
    conn=psycopg2.connect(
        database="dormitory",user="postgres",password="1234",host="localhost",port="5432"
    )
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM overview WHERE ids = %s", (ids,))
    product = cursor.fetchone()
    cursor.close()
    
    # Delete the image file from the folder
    if product:
        product[2]
        # Construct the full path to the image
        file_path = os.path.join(app.config['UPLOAD'], product[2])

        # Check if the file exists
        if os.path.exists(file_path):
            os.remove(file_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM overview WHERE ids = %s',(product[0],))
        conn.commit()
        cursor.close()
    flash('Overview deleted successfully this id', 'success')
    return redirect(url_for('overview'))

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/video')
def video():
    if 'username' in session:
        username = session['username']
        user_id = session['user_id']
        name=session['name']
        lastname=session['lastname']
        notifications=get_notifications(user_id)
        count=get_data_notifications(user_id)
        return render_template('video.html',notifications=notifications,name=session['name'],lastname=session['lastname'],count=count,sensor_value=sensor_value)
    else:
        return redirect(url_for('login'))
 
def insert(name_lastname,imgdetect,dmy,times):
    conn=psycopg2.connect(
                    database="dormitory",user="postgres",password="1234",host="localhost",
                    port="5432"
    )
    conn.autocommit = True
    cursor=conn.cursor()
    cmd="INSERT INTO overview(name_lastname,imgdetect,dmy,times) VALUES(%s,%s,%s,%s)"
    cursor.execute(cmd,(name_lastname,imgdetect,dmy,times,))
    cursor.close()
    conn.close()   

def generate_frames():
    encodingsP = 'recognizer/trainer.yml'
    print('[INFO] Load Encodings+Face...')
    data = pickle.loads(open(encodingsP, 'rb').read())
    camera = cv2.VideoCapture(0)
    # Set camera width, height, and frame rate
    camera.set(3, 360)  # Width
    camera.set(4, 360)  # Height
    camera.set(5, 15)   # Frame rate
    while True:
        _, frame = camera.read()
    
        if not _:
            print("Error: Could not read from the camera.")
            break

    # Face detection
        boxes = face_recognition.face_locations(frame)
        encodings = face_recognition.face_encodings(frame, boxes)
    
        names = []
        confidences = []  # To store confidence values
    
        for encoding in encodings:
        # Calculate face distances (confidences) for each known encoding
            face_distances = face_recognition.face_distance(data['encodings'], encoding)
        
        # Find the index of the known encoding with the smallest distance (highest confidence)
            # min_distance_idx = face_distances.argmin()
            min_distance_idx = face_distances.argmin()
        
            if face_distances[min_distance_idx] <= 0.45:  # You can adjust this threshold as needed
                name = data['names'][min_distance_idx]
                confidence = (1 - face_distances[min_distance_idx])*100  # Confidence is 1 minus distance
          
            else:
                name = 'Not member'
                confidence = 0
        
            names.append(name)
            
            confidences.append(confidence)
    
    # Process detected faces and save images
        for ((top, right, bottom, left), name, confidence) in zip(boxes, names, confidences):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            text = f"{name} ({confidence:.0f})" if confidence is not None else name
            cv2.putText(frame,text, (left, bottom + 50), cv2.FONT_HERSHEY_COMPLEX, 0.8, 
                        (0, 0, 255), 2)
        current_datetime = datetime.datetime.now()
        date_string = current_datetime.strftime("%d%m%Y")
        time_string =current_datetime.strftime("%H%M%S")
        img_name = "static/images/detection/"+ name +'_'+date_string+'_'+time_string+".jpg"
        cv2.imwrite(img_name, frame)
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
          
        # current_datetime = datetime.datetime.now()
        # date_string = current_datetime.strftime("%d%m%Y")
        # time_string =current_datetime.strftime("%H%M%S")
        # print(name)
        # name_lastname=name
        # print(date_string)
        # print(time_string)
        # time.sleep(30)
       
        
    camera.release()
    



@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/member')
def dataset():
    if 'username' in session:
            username = session['username']
            user_id = session['user_id']
            name=session['name']
            lastname=session['lastname']
            notifications=get_notifications(user_id)
            count=get_data_notifications(user_id)
            conn=psycopg2.connect(
                    database="dormitory",user="postgres",password="1234",host="localhost",port="5432"
            )
            conn.autocommit = True
            cursor=conn.cursor()
    # Execute a query to search for products by date
            cursor.execute("SELECT * FROM members")
            datasets = cursor.fetchall()

            conn.close()
    
            return render_template('member.html', datasets=datasets, notifications=notifications, name=session['name'],lastname=lastname,count=count)
    else:
        return redirect(url_for('login'))
    
@app.route('/upload', methods=['POST'])
def add_dataset():
    folder_name = request.form.get('folder_name')
    if not folder_name:
        return 'No folder name provided'
    # dataset(folder_name)
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    os.makedirs(folder_path, exist_ok=True)
    folder_names=os.listdir(folder_path)
    images = request.files.getlist('images')
    
    for image in images:
        if image.filename != '':
            image.save(os.path.join(folder_path, image.filename))
    conn=psycopg2.connect(
        database="dormitory",user="postgres",password="1234",host="localhost",
        port="5432"
    )
    conn.autocommit = True
    cursor=conn.cursor()
    cmd="INSERT INTO members(name_lastname) VALUES(%s)"
    cursor.execute(cmd,(folder_name,))
    cursor.close()
    conn.close()
    #return 'Folder and images uploaded successfully'
    
    print('[INFO] Start Processing Faces....')
    imgPaths=list(paths.list_images('static/images/datasets'))

    knowEncodings=[]
    knowNames=[]

    for (i,imgPath) in enumerate(imgPaths):
        print('[INFO] Processing Faces {}/{}'.format(i+1,len(imgPaths)))
        name=imgPath.split(os.path.sep)[-2]
        img=cv2.imread(imgPath)
        rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    
        boxes=face_recognition.face_locations(rgb,model='hog')
        encodings=face_recognition.face_encodings(rgb,boxes)
    
        for encoding in encodings:
            knowEncodings.append(encoding)
            knowNames.append(name)
        
    print('[INFO] Serializing Encodings....')
    data={'encodings':knowEncodings,'names':knowNames}
    f=open('recognizer/train.yml','wb')
    f.write(pickle.dumps(data))
    f.close()
    return redirect(url_for('dataset'))

# @app.route('/bell',methods=['POST'])
# def bell():
#     if 'username' in session:
#             username = session['username']
#             user_id = session['user_id']
#             name=session['name']
#             lastname=session['lastname']
#     # Get the current date and time
#             current_datetime = datetime.datetime.now()

# # Format the datetime to include microseconds
#             formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

# # Print the formatted datetime
#             print("Current Date and Time:", formatted_datetime)
#             conn=psycopg2.connect(
#                 database="dormitory",user="postgres",password="1234",host="localhost",
#                 port="5432"
#             )
#             conn.autocommit = True
#             cursor=conn.cursor()
#             cmd="INSERT INTO read(user_id,overview_id,Times) VALUES(%s)"
#             cursor.execute(cmd,(user_id,id,formatted_datetime,))
#             cursor.close()
#             conn.close()


if __name__ == '__main__':
    app.run(debug=True)