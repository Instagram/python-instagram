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
                    "<li><a href='/feed'>Feed</a></li>"
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

@route('/feed')
def on_feed():
    content = "<h2>User's Feed</h2>"
    access_token = request.session['access_token']
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])

        myUser =  api.user()

        content +="<p>Hello "+myUser.getName()+", thank you for logging in.</p>"

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
