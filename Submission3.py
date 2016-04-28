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
from instagram import client, subscriptions

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

    nav_menu = ("<h1>Menu for Tim's and Jeff's Instagram API</h1>"
                "<ul>"
                    "<li><a href='/myInfo'>My information</a></li>"
                "</ul>"
                "<ul>"
                    "<li><a href='/myRecentLikes'>Posts that I liked</a></li>"
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
        api = client.InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])
        request.session['access_token'] = access_token

    except Exception as e:
        print(e)
    return get_nav()

@route('/myInfo')
def myInfo():
    content = "<h2>User's Feed</h2>"
    access_token = request.session['access_token']
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])

        myUser =  api.user() #makes an API call

        content +="<p>Hello "+myUser.getName()+", thank you for logging in.</p>"
        content+="<p>Your id number: "+myUser.id+"</p>"

        test1 = api.user_followed_by()

        content += "<p>"+test1.__str__()+"</p>"
        print test1

    except Exception as e:
        print(e)
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content,api.x_ratelimit_remaining,api.x_ratelimit)
@route('/myRecentLikes')
def myRecentLikes():
    content = "<h2>User's Recent Likes</h2>"
    access_token = request.session['access_token']
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])


        myLikedPosts, next = api.user_liked_media()
        print myLikedPosts
        photos = []
        for media in myLikedPosts:
            photos.append('<div style="float:left;">')
            if(media.type == 'video'):
                photos.append('<video controls width height="150"><source type="video/mp4" src="%s"/></video>' % (media.get_standard_resolution_url()))
            else:
                photos.append('<img src="%s"/>' % (media.get_low_resolution_url()))
            photos.append("<br/> <a href='/media_like/%s'>Like</a>  <a href='/media_unlike/%s'>Un-Like</a>  LikesCount=%s</div>" % (media.id,media.id,media.like_count))
        content += ''.join(photos)

        #content +="<p>Here are your recent likes:\n "+myLikedPosts.__str__()+"</p>"

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
