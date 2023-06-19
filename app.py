from flask import Flask, render_template, request,redirect,url_for,json,session,flash
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import cv2
from keras.models import load_model
import webbrowser
from datetime import datetime


with open('config.json','r') as c:
	params=json.load(c) ["params"]

app = Flask(__name__)

app.secret_key="super-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/groove"
# initialize the app with the extension
db= SQLAlchemy(app)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

info = {}

haarcascade = "haarcascade_frontalface_default.xml"
label_map = ['Anger', 'Neutral', 'Fear', 'Happy', 'Sad', 'Surprise']
print("+"*50, "loadin gmmodel")
model = load_model(r'C:\Users\veathavalli\Downloads\model (2).h5')
cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@app.route('/')
def content():
	return render_template('content.html')

# accounts class table of login and register
class Accounts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20))
    username = db.Column(db.String(80))
    password = db.Column(db.String(120))
    date = db.Column(db.String(12))

#login routes
@app.route("/login",methods=["GET", "POST"])
def login():
	
    if request.method == "POST":
        email = request.form["email"]
        passw = request.form["passw"]
        login =  Accounts.query.filter_by(email=email,password=passw).first()
        if login is not None:
            return render_template("afterlogin.html",login=login,date=datetime.now())
    return render_template("newlogin.html")
   

#register routes
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['email']
        passw = request.form['passw']

        register =  Accounts(username = uname, email = mail, password = passw,date=datetime.now())
        db.session.add(register)
        db.session.commit()
        
        return render_template("newlogin.html")
    flash("You are Successfully Registered")
    return render_template("newregister.html")

#logout routes
@app.route('/logout')
def logout():
	session.clear
	flash("You're Logged out!")
	return redirect(url_for("content"))

#dashbord routes
@app.route('/dashboard',methods=["GET","POST"])
def dashboard():

	if request.method=="POST":
		username=request.form.get('uname')
		userpass=request.form.get('passw')
		if (username == params['admin_user'] and  userpass == params['admin_pass']):
			contacts = Contacts.query.all()
			accounts = Accounts.query.all()
			details = Details.query.all()
			return render_template("dashboard.html",params=params,contacts=contacts,accounts=accounts,details=details)
		
	return render_template("admin.html",params=params)

#contact class table 
class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    phone_num = db.Column(db.String(80))
    msg = db.Column(db.String(120))
    date = db.Column(db.String(12))
    email = db.Column(db.String(20))

#contact routes
@app.route('/contact',methods=['GET','POST'])
def contact():
	if(request.method=='POST'):
		name=request.form.get('name')
		email=request.form.get('email')
		phone=request.form.get('phone')
		message=request.form.get('message')

		entry = Contacts(name=name,phone_num=phone,msg=message,date=datetime.now(),email=email)
		db.session.add(entry)
		db.session.commit()

	return render_template('contact.html')

@app.route('/home')
def home():
	return render_template('afterlogin.html')

@app.route('/about')
def about():
	return render_template('about.html')


#aboutme routes
@app.route('/aboutme')
def aboutme():
	return render_template('aboutme.html')


# afterlogin routes
@app.route('/afterlogin')
def afterlogin():
	if not session.get("name"):
		return redirect("/login")
	return render_template('afterlogin.html')

#contact class table 
class Details(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(80))
    singer = db.Column(db.String(80))
    date = db.Column(db.String(12))
    

#after clicking 'start app' button index page will open
@app.route('/index')
def index():
	return render_template('index.html')

#choose singer routes
@app.route('/choose_singer', methods = ["POST"])
def choose_singer():
	info['language'] = request.form['language']
	print(info)
	if(request.method=='POST'):
		language =request.form.get('language')
		singer=request.form.get('singer')
		entry = Details(singer=singer,language=language,date=datetime.now())
		db.session.add(entry)
		db.session.commit()
	return render_template('choose_singer.html', data = info['language'])

# emotion routes
@app.route('/emotion_detect', methods=["POST"])
def emotion_detect():
	info['singer'] = request.form['singer']
	if(request.method=='POST'):
		language =request.form.get('language')
		singer=request.form.get('singer')
		entry = Details(singer=singer,language=language,date=datetime.now())
		db.session.add(entry)
		db.session.commit()

	found = False

	cap = cv2.VideoCapture(0)
	while not(found):
		_, frm = cap.read()
		gray = cv2.cvtColor(frm,cv2.COLOR_BGR2GRAY)
		
		faces = cascade.detectMultiScale(gray ,1.3, 5)

		for x,y,w,h in faces:
			found = True
			roi = gray[y:y+h, x:x+w]
			cv2.imwrite("static/face.jpg", roi)

	roi = cv2.resize(roi, (48,48))

	roi = roi/255.0
	
	roi = np.reshape(roi, (1,48,48,1))

	prediction = model.predict(roi)

	print(prediction)

	prediction = np.argmax(prediction)
	prediction = label_map[prediction]

	cap.release()

	link  = f"https://www.youtube.com/results?search_query={info['singer']}+{prediction}+{info['language']}+official song"
	webbrowser.open(link)

	return render_template("emotion_detect.html", data=prediction, link=link)

if __name__ == "__main__":
	app.run(debug=True)
