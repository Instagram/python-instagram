'''
The bulk of this program is based off of the sample code that Instagram put out to run their API
the myInfo section was written by Tim
 with minor modifications in the models.py so that the username and id number could be shown to the user

To run it:
  * Download bottle if you don't already have it: pip install bottle
  * Download bottle-session if you don't already have it: pip install bottle-session
  * Download and run a redis instance on port 6379, here's their website http://redis.io
  * Run the file; it will host a local server on port 8515.
  * Visit http://localhost:8515 in a web browser
  *
  * Login: as a user we created:
  *     Sandbox username: joejones353
  *             password: DrwnSurfz
'''



import bottle
import beaker.middleware
from bottle import route, redirect, post, run, request, hook
from instagram import client, subscriptions, helper
from instagram.client import InstagramAPI
import time
from datetime import date
from collections import Counter

bottle.debug(True)

session_opts = {
    'session.type': 'file',
    'session.data_dir': './session/',
    'session.auto': True,
}

app = beaker.middleware.SessionMiddleware(bottle.app(), session_opts)

CONFIG = {
    'client_id': '3c83c3ebf36b4445ad069560c0557f70',
    'client_secret': '9b2971e8f6f1440c867b8c7a8a7bc77f',
    'redirect_uri': 'http://localhost:8515/oauth_callback'
}

unauthenticated_api = client.InstagramAPI(**CONFIG)

@hook('before_request')
def setup_request():
    request.session = request.environ['beaker.session']

def process_tag_update(update):
    print(update)

reactor = subscriptions.SubscriptionsReactor()
reactor.register_callback(subscriptions.SubscriptionType.TAG, process_tag_update)
myName = ""

@route('/')
def home():
    try:
        url = unauthenticated_api.get_authorize_url(scope=["likes","comments","relationships","follower_list","basic","public_content"])
        return '<a href="%s">Connect with Instagram</a>' % url
    except Exception as e:
        print(e)


def get_nav():

    nav_menu = ("<body style=\"background-color:lightgrey;\"><font size=\"6\"><h1 style=\"font-family:verdana; text-align:center;\">Tim's and Jeff's Instagram API</h1>"
                "<h2>Main Menu:</h2>"
                "<ul> <font size=\"3\">"
                    "<li><a href='/myInfo'>My information</a></li>"
                    "<li><a href='/myFollowers'>My Followers List</a></li>"
                    "<li><a href='/myRecentLikes'>Posts that I liked, Statistics, and Suggested People to Follow</a></li>"
                "</ul>")
    return nav_menu


@route('/oauth_callback')
def on_callback():
    code = request.GET.get("code")
    if not code:
        return 'Missing code'
    try:
        access_token, user_info = unauthenticated_api.exchange_code_for_access_token(code)
        if not access_token:
            return 'Could not get access token'
        api = InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])
        request.session['access_token'] = access_token

    except Exception as e:
        print(e)
    return get_nav()

@route('/myInfo')
def myInfo():
    content = "<h2>User's Information</h2>"
    access_token = request.session['access_token']
    if not access_token:
        return 'Missing Access Token'
    try:
        api = InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])

        myUser =  api.user() #makes an API call
        #myInformation = api.user_self() #makes another API call

        content += "<img src="+myUser.profile_picture+" alt='Profile Picture' >"
        content +="<p>Username : "+myUser.username+"</p>"
        content +="<p>Full Name: "+myUser.full_name+"</p>"
        content +="<p>ID number: "+myUser.id+"</p>"
        content +="<p>Biography: "+myUser.bio+"</p>"
        content +="<h3>Counts:</h3>"
        content +="<ul><li>Posts: "+ str(myUser.counts.get('media'))+"</li>"
        content +="<li>Followers: "+ str(myUser.counts.get('followed_by'))+"</li>"
        content +="<li>Following: "+ str(myUser.counts.get('follows'))+"</li></ul>"



    except Exception as e:
        print(e)
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content,api.x_ratelimit_remaining,api.x_ratelimit)

@route('/myFollowers')
def myFollowers():
    content = "<h2>User's Followers</h2>"
    access_token = request.session['access_token']
    if not access_token:
        return 'Missing Access Token'
    try:
        api = InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])



        follower_list, next_ = api.user_followed_by()
        counter =0
        content+="<ul>"

        for user in follower_list:
            content+="<li><em>"+user.getName()+"</em></li>"
            counter = counter +1

        content+="</ul>"

        content+="</h2>Total follower count: "+str(counter)+"</h2><p></p><p></p>"


    except Exception as e:
        print(e)
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content,api.x_ratelimit_remaining,api.x_ratelimit)



@route('/myRecentLikes')
def myRecentLikes(): #written by Tim
    content = "<h2>User's Recent Likes</h2>"
    access_token = request.session['access_token']
    if not access_token:
        print "Missing Access Token"
        return 'Missing Access Token'
    try:
        print "in try..."
        api = InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])
        _user_id =(api.user()).id

        liked_media, next = api.user_liked_media(count=10)
        print "API call for 10 most recently liked media made successfully"

        counter = 0;
        photos = []
        filters = []
        usersThatLiked = []
        for media in liked_media:
            filters.append(media.filter)
            #usersThatLiked.extend(media.likes)
            print media.id
            usersThatLiked.extend(api.media_likes(media_id = media.id))
            print usersThatLiked
            counter = counter +1

            photos.append('<div style="float:left;">')
            if(media.type == 'video'):
                content += " this is a video below"
                photos.append('<video controls width height="150"><source type="video/mp4" src="%s"/></video>' % (media.get_standard_resolution_url()))
            else:
                photos.append('<div class="floated_img"><img src="%s"/></div>' % (media.get_standard_resolution_url()))

        content += ''.join(photos) #display media

        #content += "<p> Count: "+str(counter)+"</p>"

        filterCounter = Counter(filters) #makes a counter object based on the list of filters
        usersThatLikedCounter = Counter(usersThatLiked) #counts instances of any person liking the same pictures that the user did

        #outputs a ranked list of the filters used in the liked posts above
        content += "<h2> Filters used (count): </h2><ol>"
        for filterWithCount in filterCounter.most_common():
            content += "<li>" + filterWithCount[0] +"  ("+str(filterWithCount[1])+")</li>"
        content += "</ol>"

        print usersThatLikedCounter
        #outputs the most common users that liked the same media
        content += "<h2> Top users that also liked these posts: </h2><ol>"
        for userWithCount in usersThatLikedCounter.most_common(6):
            if (userWithCount[0].id != _user_id): #makes sure that the current user is not displayed
                content += "<li>" + userWithCount[0].username +"  ("+str(userWithCount[1])+" similar likes)"
                content += ("    <a href='/user_follow/%s'>Follow</a>      Here's a link to their Instagram Profile:" % (userWithCount[0].id))
                content += ("    <a href='https://www.instagram.com/%s'>instagram.com/%s</a></li>" % (userWithCount[0].username, userWithCount[0].username))
        content += "</ol>"

    except Exception as e:
        print "in exception ..."
        print(e)
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content,api.x_ratelimit_remaining,api.x_ratelimit)


@route('/user_follow/<id>')
def user_follow(id):
    content = ""
    print "in User_follow"
    access_token = request.session['access_token']
    if not access_token:
        print "Missing Access Token"
        return 'Missing Access Token'
    try:
        api = InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])
        api.follow_user(user_id = id)
        content += "<h2>Congratulations, you are following that user!</h2>"

    except Exception as e:
        print(e)
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content,api.x_ratelimit_remaining,api.x_ratelimit)

@route('/realtime_callback')
@post('/realtime_callback')
def on_realtime_callback():
    mode = request.GET.get("hub.mode")
    challenge = request.GET.get("hub.challenge")
    verify_token = request.GET.get("hub.verify_token")
    if challenge:
        return challenge
    else:
        x_hub_signature = request.header.get('X-Hub-Signature')
        raw_response = request.body.read()
        try:
            reactor.process(CONFIG['client_secret'], raw_response, x_hub_signature)
        except subscriptions.SubscriptionVerifyError:
            print("Signature mismatch")

bottle.run(app=app, host='localhost', port=8515, reloader=True)
