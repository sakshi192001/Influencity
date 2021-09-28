import json
import re
from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import razorpay
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import date, datetime
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
mysql = MySQL(app)

app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'devfest'


@app.route('/', methods=["GET", "POST"])
def login():
    msg=""
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form and 'domain' in request.form:
        # Create variables for easy access
        email = request.form['email']
        
        password = request.form['password']
        domain = request.form['domain']
        # Check if account exists using MySQL
        if domain=="iregister":
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM iregister WHERE email = %s AND password = %s', (email, password))
            # Fetch one record and return result
            account = cursor.fetchone()
            if account:

                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['email'] = account['email']
                session['Name'] = account['Name']
                # Redirect to home page

                return redirect(url_for('ihome'))
        elif domain=="cregister":
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM cregister WHERE email = %s AND password = %s', (email, password))
            # Fetch one record and return result
            account = cursor.fetchone()
        # If account exists in accounts table in out database
            if account:

                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['email'] = account['email']
                session['Name'] = account['Name']
                # Redirect to home page

                return redirect(url_for('chome'))
        else:
        
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('email', None)
   session.pop('Name', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/register', methods=["GET", "POST"])
def reg():
    if request.method=="POST" and "name" in request.form and "email" in request.form and "password" in request.form and "type" in request.form:
        name= request.form["name"]
        email= request.form["email"]
        password= request.form["password"]
        type = request.form["type"]
        file = request.files['file']
        if type == "iregister":
            return redirect(url_for('register1', name=name, email=email, password=password, file=file))
        elif type == "cregister":
            return redirect(url_for("register2",name=name, email=email, password=password, file = file))
    return render_template('register.html')

@app.route('/register1', methods=["GET", "POST"])
def register1():
    name = request.args.get('name')
    email = request.args.get('email')
    file = request.args.get('file')
    password = request.args.get('password')
    if request.method=="POST" and "domain" in request.form and "insta_id" in request.form and "twitter_id" in request.form and "facebook_id" in request.form and "youtube_channel_link" in request.form and "bio" in request.form and "description" in request.form:
        domain = request.form["domain"]
        insta = request.form["insta_id"]
        twitter = request.form["twitter_id"]
        facebook = request.form["facebook_id"]
        youtube = request.form["youtube_channel_link"]
        bio = request.form["bio"]
        description = request.form["description"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO iregister VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', [name, email, insta, youtube, domain, password, twitter, facebook, bio, description, file])
        mysql.connection.commit()
        return redirect(url_for('login'))
    return render_template('register2.html')

@app.route('/register2', methods=["GET", "POST"])
def register2():
    name = request.args.get('name')
    email = request.args.get('email')
    password = request.args.get('password')
    if request.method=="POST" and "website_link" in request.form and "bio" in request.form and "description" in request.form and "linkedin_link" in request.form:
        web_link = request.form["website_link"]
        bio = request.form["bio"]
        description = request.form["description"]
        linkedin = request.form["linkedin_link"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO cregister VALUES(%s,%s,%s,%s,%s,%s,%s)', [name, email, password, web_link, linkedin, bio, description])
        mysql.connection.commit()
        return redirect(url_for('login'))
    return render_template('register3.html')


@app.route('/payment', methods=["GET", "POST"])
def payment():
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'amount' in request.form:
        email = request.form['email']
        name = request.form['name']
        amount = int(request.form['amount'])*100
        today = date.today()
        sender_email = session['email']
        sender = session['Name']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO cinvoices VALUES(%s,%s,%s,%s,%s, %s)', [today,name, email, amount,sender, sender_email])
        mysql.connection.commit()
        return redirect(url_for('pay', name=name))
    return render_template('index.html')

@app.route('/pay/<name>', methods=["GET", "POST"])
def pay(name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM cinvoices WHERE Name = %s', [name])
    accounts = cursor.fetchone()
    print(accounts)
    amount=int(accounts['Amount'])*100
    client = razorpay.Client(auth = ("rzp_test_gZzzC8qiLG08IF","BI5YmLqom9sz1iAxhI3OIiKo"))
    payment = client.order.create({'amount' : int(amount)*100, 'currency' : 'INR', 'payment_capture' : '1' })
    return render_template('pay.html', name=name, payment=payment)


@app.route('/insights')
def insights():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM iregister WHERE Name = %s', [session['Name']])
    accounts = cursor.fetchone()
    yt_link = accounts['youtube']
    #link1=yt_link.split('/')[-1]
    link1='UCvCyIiKSCA1fHKSCOKJyjXA'
    domain = accounts['domain']
    source = requests.get('https://www.noxinfluencer.com/youtube/realtime-subs-count/'+link1).text
    soup = BeautifulSoup(source, 'lxml')
    abc = soup.find('div', class_='page')
    hd = abc.find('div', class_="page-container")
    sd=hd.find('section', class_='sub-block')
    fajb = sd.find('div', class_='sub-wrapper')
    sub = fajb.find('span', id='sub-number')
    subscribers=sub.text
    

    insta_id = accounts['insta_id']
    source1= requests.get('https://socialstats.info/report/'+insta_id+'/instagram').text
    soup1 = BeautifulSoup(source1, 'lxml')
    # abc1 = soup1.find('div', class_="container")
    sy=soup1.find('div', class_="d-flex") 
    count = sy.find_all('p', class_="report-header-number")
    values=[]
    for i in count:
        values.append(i.text)
    print(values)
    followers=values[0]
    post=values[1]
    engagement=values[2].replace(" ","")
    img = io.BytesIO()


    list4 = [10000,11000,13000,20000,25000,36000,38000,43000,45000,40000,43000,46000]
    score1 = ["Jan","Feb","Mar","April","May","Jun","July","Aug","Sept","Oct","Nov","Dec"]
    plt.xlabel('Month')
    plt.ylabel('FOLLOWERS')

    fig = plt.plot(score1, list4)
    
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    img1 = io.BytesIO()


    list41 = [10100,11010,13010,20010,25010,36001,38010,43100,45010,40010,43010,46001]
    score11 = ["Jan","Feb","Mar","April","May","Jun","July","Aug","Sept","Oct","Nov","Dec"]
    plt.xlabel('Month')
    plt.ylabel('SUBSCRIBERS')

    fig1 = plt.plot(score11, list41)
    
    plt.savefig(img, format='png')
    img1.seek(0)
    plot_url1 = base64.b64encode(img.getvalue()).decode()
    data = {'Task' : 'Hours per Day', 'Work' : 11, 'Eat' : 2, 'Commute' : 2, 'Watching TV' : 2, 'Sleeping' : 7}
    return render_template('insights.html', plot_url=plot_url, domain=domain,plot_url1=plot_url1, data=data, subscribers=subscribers, followers=followers, engagement=engagement)

@app.route('/c_home', methods=["GET", "POST"])
def chome():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM iregister')
    accounts = cursor.fetchall()
    return render_template('c_home.html',accounts=accounts)

@app.route('/i_home', methods=["GET", "POST"])
def ihome():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM cregister')
    accounts = cursor.fetchall()
    cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor1.execute('SELECT * FROM iregister')
    accounts1 = cursor1.fetchall()
    return render_template('i_home.html',accounts=accounts, accounts1=accounts1)
# @app.route('/analysis')
# def analysis():
#     img = io.BytesIO()


#     score1 = [10,20,20,11,15]
#     list4 = [1,2,3,4,5]
#     plt.xlabel('TEST NUMBER')
#     plt.ylabel('SCORE')

#     fig = plt.plot(score1, list4)
    
#     plt.savefig(img, format='png')
#     img.seek(0)

#     plot_url = base64.b64encode(img.getvalue()).decode()

#     return render_template('analysis.html', plot_url=plot_url)

@app.route('/iprofile', methods=["POST", "GET"])
def iprofile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM iregister WHERE email=%s', [session['email']])
    accounts = cursor.fetchone()
    print(accounts)
    if  request.method=="POST" and "recent_link" in request.form:
        print("link")
    if   request.method=="POST" and "personal" in request.form:
        print("personal")
    return render_template('profile_influencer.html',accounts=accounts)

@app.route('/cprofile', methods=["POST", "GET"])
def cprofile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM cregister WHERE email=%s', [session['email']])
    accounts = cursor.fetchone()
    (print(accounts))
    if  request.method=="POST" and "recent_link" in request.form:
        print("link")
    if   request.method=="POST" and "personal" in request.form:
        print("personal")
    return render_template('profile_company.html', accounts=accounts)

@app.route('/iportfolio/<Name>', methods=["GET","POST"])
def iportfolio(Name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM iregister WHERE Name=%s', [Name])
    accounts = cursor.fetchone()
    if request.method=="POST" and request.form['sub_butt']=="Chat":
        return redirect(url_for('cchat'))
    if request.method=="POST" and request.form['sub_butt']=="Support":
        return redirect(url_for('payment'))
    return render_template('portfolio_influencer.html',accounts=accounts)

@app.route('/cportfolio/<Name>', methods=["GET","POST"])
def cportfolio(Name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM cregister WHERE Name=%s', [Name])
    accounts = cursor.fetchone()
    if request.method=="POST" and request.form['sub_butt']=="Chat":
        return redirect(url_for('ichat'))
    return render_template('portfolio_company.html',accounts=accounts)

@app.route('/iinvoices', methods=["GET","POST"])
def invoices():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM cinvoices WHERE Email=%s', [session['email']])
    accounts = cursor.fetchall()
    return render_template('invoice_influencer.html', accounts=accounts)

@app.route('/ichats',methods=["GET","POST"])
def chat():
    name=session['Name']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM chats WHERE Receiver=%s', [name])
    accounts = cursor.fetchall()
    
    if request.method == "POST" and "receiver" in request.form and "msg" in request.form:
        today = date.today()
        now = datetime.now().strftime("%H:%M:%S")
        receiver = request.form['receiver']
        msg = request.form['msg']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO chats VALUES(%s,%s,%s,%s,%s)', [today,now, name, receiver,msg])
        mysql.connection.commit()
        return redirect(url_for('chat'))
    return render_template('chat_i.html',accounts=accounts)

@app.route('/cinvoices', methods=["GET","POST"])
def cinvoices():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM cinvoices WHERE Email=%s', [session['email']])
    accounts = cursor.fetchall()
    return render_template('invoice_company.html', accounts=accounts)

@app.route('/cchats',methods=["GET","POST"])
def cchat():
    name=session['Name']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM chats WHERE Receiver=%s', [name])
    accounts = cursor.fetchall()
    
    if request.method == "POST" and "receiver" in request.form and "msg" in request.form:
        today = date.today()
        now = datetime.now().strftime("%H:%M:%S")
        receiver = request.form['receiver']
        msg = request.form['msg']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO chats VALUES(%s,%s,%s,%s,%s)', [today,now, name, receiver,msg])
        mysql.connection.commit()
        return redirect(url_for('chat'))
    return render_template('chat_c.html',accounts=accounts)

@app.route("/imerch")
def imerch():
    return render_template("imerchandise.html")

@app.route("/cmerch")
def cmerch():
    return render_template("cmerchandise.html")

if __name__=="__main__":
    app.run(debug=True)