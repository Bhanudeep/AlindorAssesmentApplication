
from flask import Flask, flash, request, redirect, url_for,render_template,session
from pymongo import MongoClient
import os,os.path
import bcrypt
import openai
from flask_cors import CORS
app = Flask(__name__, static_url_path='/static')
CORS(app)
app.secret_key = '?&Kjhd$^ljm>x21'
API_KEY=''
openai.api_key=API_KEY
prompt="give the score of candidate from 1 to 10 and an explanation of the score based on the job description and candidate information, brief the explanation in just 4 sentences."
Role="you are the hiring manager, you need to analyse the 'job description' and 'candidate information' stringently and give me a score out of 10 on how the job description and profile matches. Scoring should be not too generous or not too strict"
MONGO_URI =''
cluster = MongoClient(MONGO_URI)  
db=cluster["AppLogin"]
collection=db["users"]
import os,os.path
from pypdf import PdfReader

def PdfHandler():
    image = request.files["pdf"]
    filename=str(os.getcwd())
    app.config["PDF_UPLOADS"]=filename
    filename1="resume.pdf"
    image.save(os.path.join(app.config["PDF_UPLOADS"], filename1))
    app.config["PDF_UPLOADS"]=filename
    reader = PdfReader('resume.pdf') 
    page = reader.pages[0] 
    Profile=page.extract_text()
    return Profile 


def OpenAi_API_Handler(content,profile):
    if content=="NONE":
        response="Please enter Job description"
    else:
        response=openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role":"system", "content":Role
                },
                {
                    "role":"user","content":"job description:"+content+"candidate information:"+profile+prompt
                }
            ]
        )
        response=response['choices'][0]['message']['content']
        response=response.strip("\n").strip()
    return response

@app.route('/', methods=['POST','GET'])
def home():
    if 'username' in session:
        users = collection
        login_user = users.find_one({'username' : session['username']})
        name=login_user["firstname"]+" "+login_user["lastname"]
        if login_user['username']==login_user['username']:
            return render_template('/admin/Update_Encodes.html',username=name)
        
        return render_template('details.html',username=name)
    return render_template('login.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if 'username' in session:
        return """<center><h2>Please logout to login as another user...<br><br> Click <a href="/">here</a> to Go back</h2></center>"""
    else:
        alert="alert"
        if request.method == 'POST':
            users = collection
            login_user = users.find_one({'username' : request.form['UserName']})
            login_mail=users.find_one({'mailid': request.form['UserName']})
            if login_user:
                if bcrypt.hashpw(request.form['Password'].encode('utf-8'), login_user['password']) == login_user['password']:
                    user = login_user['username']
                    session['username'] = user
                    return redirect(url_for('home'))
            elif login_mail:
                if bcrypt.hashpw(request.form['Password'].encode('utf-8'), login_mail['password']) == login_mail['password']:
                    user = login_mail['username']
                    session['username'] = user
                    return redirect(url_for('home'))
            flash("Username or Password is invalid")
        return render_template("login.html",failed=alert)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if 'username' in session:
        return """<center><h2>Please logout to register as a new user...<br><br> Click <a href="/">here</a> to Go back</h2></center>"""
    else:
        alert="alert"
        if request.method == 'POST':
            users = collection
            # OTPS = mongo.db.OTPS
            Admin = users.find_one({'username' : 'ADMIN'})
            if(Admin):
                Admin_mailid = Admin['mailid']
                # passcode = OTPS.find_one({'mailid': Admin_mailid})
            existing_user = users.find_one({'username' : request.form['UserName']})
            existing_mail= users.find_one({'mailid': request.form['Mailid']})
            if existing_user is None and existing_mail is None:
                hashpass = bcrypt.hashpw(request.form['Password'].encode('utf-8'), bcrypt.gensalt())
                users.insert_one({'username' : request.form['UserName'], 'password' : hashpass , 'firstname' : request.form['First_Name'] , 'lastname' : request.form['Last_Name'], 'mailid': request.form['Mailid']})
                flash('successfully registered ...')
                return render_template("login.html",passed=alert)
            flash('Username or Mailid is already exist')
            return render_template('register.html')
        return render_template('register.html')


@app.route("/logout",methods=["POST","GET"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route('/admin_page',methods=['GET','POST'])
def admin_page():
    if 'username' in session:
        users = collection
        login_user = users.find_one({'username' : session['username']})
        name=login_user["firstname"]+" "+login_user["lastname"]
        if login_user["username"] == login_user["username"]:
            return render_template('/admin/Update_Encodes.html',username=name)
        else:
            return """<center><h2>Unautnorised Access found... You are not logged in<br><br> Click <a href="/">here</a> to Go back</h2></center>"""
    else:
        return """<center><h2>Unautnorised Access found... You are not logged in<br><br> Click <a href="/">here</a> to Go back</h2></center>"""


@app.route('/Update_Notes_page',methods=['GET','POST'])
def Update_Notes_page():
    if 'username' in session:
        users = collection
        login_user = users.find_one({'username' : session['username']})
        name=login_user["firstname"]+" "+login_user["lastname"]
        if login_user["username"] == login_user["username"]:
           
            return render_template('/admin/Update_Encodes.html',username=name)
        else:
            return """<center><h2>Unautnorised Access found... You are not logged in<br><br> Click <a href="/">here</a> to Go back</h2></center>"""
    else:
        return """<center><h2>Unautnorised Access found... You are not logged in<br><br> Click <a href="/">here</a> to Go back</h2></center>"""


@app.route('/Update_Note',methods=['GET','POST'])
def Update_Note():
    if 'username' in session:
        content=request.form["Message"]
        content=str(content)# job description
        profile=PdfHandler() #candidate profile
        response=OpenAi_API_Handler(content,profile)
        try:
            flash(response)
            return redirect(url_for("Update_Notes_page") )
        except:
            flash("No note found fo")
            return redirect(url_for("Update_Notes_page") )
        
if __name__ == "__main__":
    app.run()
# host=ip_addr,port="5000",use_reloader=True,debug=True