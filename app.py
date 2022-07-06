# if __name__ == '__main__':
#     app.run(debug=True)
from flask import request,Flask,render_template
from flask import jsonify
import geocoder

app = Flask(__name__,template_folder='templates')
@app.route("/")
def index():
    return render_template("index.html")
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
        
        url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="+str(ip.city)+"&destinations="+y[i]['name']+"units=imperial&key=AIzaSyAl-KQ2kYmnje9S-BXptm8f2X5a_GFBJzg"
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
        return render_template("table_list.html", data = places,city=Bharuch)) #str(ip.city))
    return '<h1>final list : ' #request.remote_addr
if __name__ == '__main__':
    app.run(debug=True)



