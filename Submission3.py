'''
The bulk of this program is based off of the sample code that Instagram put out to run their API
the myInfo section was written by Tim
 with minor modifications in the models.py so that the username and id number could be shown to the user

To run it:
  * Download bottle if you don't already have it: pip install bottle
  * Download bottle-session if you don't already have it: pip install bottle-session
  * Download and run a redis instance on port 6379, here's their website http://redis.io
  *     To do this:
  *     1)   wget http://download.redis.io/releases/redis-stable.tar.gz
  *     2)   tar xzf redis-stable.tar.gz
  *     3)   cd redis-stable
  *     4)   make test
  *     5)   sudo make install
  *     6)   redis-server
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
                    "<li><a href='/myFollowing'>My Following List</a></li>"
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
def myInfo(): #written by Tim
    content = "<h2>User's Information</h2>"
    access_token = request.session['access_token']
    if not access_token:
        return 'Missing Access Token'
    try:
        api = InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])

        myUser =  api.user() #makes an API call

        content += "<img src="+myUser.profile_picture+" alt='Profile Picture' >"
        content +="<p>Username : "+myUser.username+"</p>"
        content +="<p>Full Name: "+myUser.full_name+"</p>"
        content +="<p>ID number: "+myUser.id+"</p>"
        content +="<p>Biography: "+myUser.bio+"</p>"
        content +="<h3>Counts:</h3>"
        content +="<ul><li>Posts: "+ str(myUser.counts.get('media'))+"</li>"
        content +="<li><a href='/myFollowers'>Followers: </a>"+ str(myUser.counts.get('followed_by'))+"</li>"
        content +="<li><a href='/myFollowing'>Following: </a>"+ str(myUser.counts.get('follows'))+"</li></ul>"




    except Exception as e:
        print(e)
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content,api.x_ratelimit_remaining,api.x_ratelimit)

@route('/myFollowers')
def myFollowers(): #written by Tim
    content = "<h2>My Followers</h2>"
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

@route('/myFollowing')
def myFollowing(): #written by Tim
    content = "<h2>Accounts I Follow</h2>"
    access_token = request.session['access_token']
    if not access_token:
        return 'Missing Access Token'
    try:
        api = InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])



        follow_list, next_ = api.user_follows()
        counter =0
        content+="<ul>"

        for user in follow_list:
            content+="<li><em>"+user.getName()+"</em></li>"
            counter = counter +1

        content+="</ul>"

        content+="</h2>Total following count: "+str(counter)+"</h2><p></p><p></p>"


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

        api = InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])
        _user_id =(api.user()).id

        liked_media, next = api.user_liked_media(count=9)

        print "Webpage is loading...."


        counter = 0;
        photos = []
        filters = []
        usersThatLiked = []

        content += "<div id='liked_media'>"
        content +="<style>figure{   width:33.3%;   float:left;   margin:0px;   text-align:center;  padding:0px;} </style>"
        for media in liked_media:
            content += "<figure>"
            filters.append(media.filter)
            usersThatLiked.extend(api.media_likes(media_id = media.id))
            counter = counter +1

            #photos.append('<div style="float:left;">')
            if(media.type == 'video'):
                content += ('<video controls width height="150"><source type="video/mp4" src="%s"/></video>' % (media.get_standard_resolution_url()))
                #photos.append('<video controls width height="150"><source type="video/mp4" src="%s"/></video>' % (media.get_standard_resolution_url()))
            else:
                content+= ("<img src=%s/>" % (media.get_low_resolution_url()))
                content+= ("<figcaption>@%s" % (media.user.username))
                content+= "</figcaption>"
                #photos.append('<div class="floated_img"><img src="%s"/></div>' % (media.get_thumbnail_url()))

            content+="</figure>"


        content+= "</div><br>"


        filterCounter = Counter(filters) #makes a counter object based on the list of filters
        usersThatLikedCounter = Counter(usersThatLiked) #counts instances of any person liking the same pictures that the user did

        #outputs a ranked list of the filters used in the liked posts above
        content += "<h2> Filters used (count): </h2><ol>"
        for filterWithCount in filterCounter.most_common():
            content += "<li>" + filterWithCount[0] +"  ("+str(filterWithCount[1])+")</li>"
        content += "</ol>"

        #gets a list of people that our user follows (used to make accurate suggestions of people to follow)
        following_list, next_ = api.user_follows()

        #make a set of user id numbers
        following_ids = set()
        for user in following_list:
            following_ids.add(user.id)


        #outputs the most common users that liked the same media
        content += "<h2> Top users that also liked these posts: </h2><p>Below is a list of users who also liked the posts above, if you are not already following them, there will be a link.<ol>"
        for userWithCount in usersThatLikedCounter.most_common(11):
            if (userWithCount[0].id != _user_id): #makes sure that the current user is not displayed
                content += "<li>" + userWithCount[0].username +"  ("+str(userWithCount[1])+" similar likes)"
                if(userWithCount[0].id not in following_ids):
                    content += ("    <a href='/user_follow/%s'>Follow</a>" % (userWithCount[0].id))
                content +=    (" <p>Here's a link to their Instagram Profile:" )
                content += ("    <a href='https://www.instagram.com/%s'>instagram.com/%s</a></p></li>" % (userWithCount[0].username, userWithCount[0].username))
        content += "</ol>"

    except Exception as e:
        print "in exception ..."
        print(e)
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content,api.x_ratelimit_remaining,api.x_ratelimit)


@route('/user_follow/<id>')
def user_follow(id): #written by Tim
    content = ""
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
