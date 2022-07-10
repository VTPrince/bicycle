# if __name__ == '__main__':
#     app.run(debug=True)
from flask import request,Flask,render_template,session,redirect
from flask import jsonify
from datetime import timedelta
from flask_session import Session
import geocoder
import firebase_admin
from firebase_admin.auth import UserRecord
import pyrebase
import json
from firebase_admin import credentials, auth
from firebase import firebase
from functools import wraps
emaily=[]
jwtoken=[]
namely=[]
passwordy=[]
app = Flask(__name__,template_folder='templates')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.permanent_session_lifetime = timedelta(minutes=10)
Session(app)


@app.route("/")
def index():
    
    return render_template("index.html")
@app.route('/user_signup',methods=['POST','GET'])
def user_signup():
    return render_template('user_signup.html')

@app.route('/user_login',methods=['POST','GET'])
def user_login():
    return render_template('user_login.html')
#Connect to firebase
cred = credentials.Certificate('fbAdminConfig.json')
firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('fbconfig.json')))
db = pb.database()
#Data source
users = []
#Api route to get users

#Api route to sign up a new user
@app.route('/signup',methods=["GET","POST"])
def signup():
    email = request.form['email'] 
    password = request.form['password']
    name=request.form['name']
    emaily.append(email)
    passwordy.append(password)
    namely.append(name)
    if email is None or password is None:
        return {'message': 'Error missing email or password'},400
    try:
        user = auth.create_user(
               email=email,
               password=password,display_name=name
        )
        data = {"name": name,"email":email}
        db.child("users").child(name).set(data)

        return {'message': f'Successfully created user {user.display_name}'},200
        #return redirext('/token')
    except Exception as e:
        print(e)
        return {'message': "error"},400

#Api route to get a new token for a valid user
@app.route('/token',methods=["POST","GET"])
def token():
    #email = request.form.get('email')
    email=emaily[0]
    password=passwordy[0]
    #password = request.form.get('password')
    try:
        user = pb.auth().sign_in_with_email_and_password(email, password)
        jwt = user['idToken']
        jwtoken.append(jwt)
        return {'token': jwt}, 200
    except:
        return {'message': 'There was an error logging in'},400
def check_token(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if not jwtoken[0]: #request.headers.get('authorization'):
            return {'message': 'No token provided'},400
        try:
            user = auth.verify_id_token(jwtoken[0])#request.headers['authorization'])
            users.append(user)
            request.user = user
        except:
            return {'message':'Invalid token provided.'},400
        return f(*args, **kwargs)
    return wrap

#Logout User
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/')

#Login User
@app.route('/login',methods=['GET','POST'])
def login():
    email = request.form.get('email')
    #emaily=emaily[0]
    emaily.append(email)
    user_name=db.child("users").order_by_child("email").equal_to('kohli@gmail.com').get()
    for un in user_name.each():
        namely.append(un.key()) 
    print(namely[0])
    #password=passwordy[0]
    password = request.form.get('password')
    passwordy.append(password)
    try:
        user = pb.auth().sign_in_with_email_and_password(email, password)
        session['user']=user
        return redirect('/')
        #return {'message': "user logged in"}, 200
    except Exception as e:
        print(e)
        return {'messahe':'failed'},400


@app.route('/userinfo')
@check_token
def userinfo():
    return {'data': users}, 200



#store user data to database





@app.route("/service")
def service():
    return render_template("service.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/my_form',methods=['POST',"GET"])
def my_form():
    return render_template('my_form.html')


@app.route("/get_my_ip", methods=["GET","POST"])
def get_my_ip():
    if 'X-Forwarded-For' in request.headers:
        proxy_data = request.headers['X-Forwarded-For']
        ip_list = proxy_data.split(',')
        user_ip = ip_list[0]  # first address in list is User IP
    else:
        user_ip = request.remote_addr
    ip = geocoder.ip(user_ip)
    import requests, json
    import googlemaps
    # enter your api key here
    api_key = 'AIzaSyAl-KQ2kYmnje9S-BXptm8f2X5a_GFBJzg'

    # url variable store url
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

    # The text string on which to search
    text = request.form['text']
    processed_text = text.upper()
    query = processed_text #input('Search query: ')
    query = query+str(ip.city)
    # get method of requests module
    # return response object
    r = requests.get(url + 'query=' + query +
                            '&key=' + api_key)
    gmaps = googlemaps.Client(key=api_key)
    # json method of response object convert
    # json format data into python format data
    x = r.json()

    # now x contains list of nested dictionaries
    # we know dictionary contain key value pair
    # store the value of result key in variable y
    y = x['results']
    distances=[]
    hotels=[]
    # keep looping upto length of y
    for i in range(len(y)):
        
        #url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="+str(ip.city)+"&destinations="+y[i]['name']+"units=imperial&key=AIzaSyAl-KQ2kYmnje9S-BXptm8f2X5a_GFBJzg"
        print(str(ip.city))
        print(y[i]['name'])
        #hotels.append(y[i]['name'])
        #payload={}
        #headers = {}
        #response = requests.request("GET", url, headers=headers, data=payload)
        places={}
        try:
            my_dist = gmaps.distance_matrix(str(ip.city),y[i]['name'])['rows'][0]['elements'][0]["distance"]["text"]
            #print(my_dist)
            
            distances.append(my_dist)
            hotels.append(y[i]['name'])
            print(distances)
            print(hotels)
            
        except KeyError:
            continue
    #print(places)
    
    for x in range(len(distances)):
        places[hotels[x]]=distances[x]
    print(places)

    for key,value in places.items():
        return render_template("table_list.html", data = places,city=str(ip.city))
    return render_template("table_list.html", data = places,city=str(ip.city))

@app.route('/adddestination/<string:place>',methods=['GET','POST'])
def adddestination(place):
    user_place=place
    print(namely[0])
    db.child("users").child(namely[0]).update({"place": user_place}) 
    return {'message':'destination added'},200
if __name__ == '__main__':
    app.run(debug=True)



