python-instagram
======
A Python client for the Instagram REST and Search APIs

Installation
-----
pip install python-instagram

Requires
-----
  * httplib2
  * simplejson


Discussion
------

Visit [our Google Group](http://groups.google.com/group/instagram-api-developers) to discuss the Instagram API.


Authentication
-----

Instagram API uses the OAuth2 protocol for authentication, but not all functionality requires authentication.
See the docs for more information: http://instagr.am/developer/auth/

### Obtaining an access token

If you're using a method that requires authentication and need an access token, you can use the provided get_access_token.py script to obtain an access token for yourself.
It will prompt you for your app's Client ID, Client Secret, and Redirect URI, and walk you through instructions for getting your own access token for your app.

### Authenticating a user

The provided sample app shows a simple OAuth flow for authenticating a user and getting an access token for them.

### Using an access token

Once you have an access token (whether via the script or from the user flow), you can  pass that token into the InstagramAPI constructor:

    from instagram.client import InstagramAPI

    access_token = "YOUR_ACCESS_TOKEN"
    api = InstagramAPI(access_token=access_token)
    recent_media, next = instagram_client.user_recent_media(user_id=user.instagram_userid, count=count)
    for media in recent_media:
       print media.caption.text
       
### Making unauthenticated requests

For methods that don't require authentication, you can just pass your client ID and optionally client secret into the InstagramAPI 
constructor:

    api = InstagramAPI(client_id='YOUR_CLIENT_ID', client_secret='YOUR_CLIENT_SECRET')
    popular_media = api.media_popular(count=20)
    for media in popular_media:
        print media.images['standard_resolution'].url


Real-time Subscriptions:
-----

See the docs for more on real-time subscriptions: http://instagr.am/developer/realtime/

You can use the API to subscribe to users, tags, locations, or geographies:

    # Subscribe to updates for all users authenticated to your app
    api.create_subscription(object='user', aspect='media', callback_url='http://mydomain.com/hook/instagram')
    # Subscribe to all media tagged with 'fox'
    api.create_subscription(object='tag', object_id='fox', aspect='media', callback_url='http://mydomain.com/hook/instagram')
    # Subscribe to all media in a given location
    api.create_subscription(object='location', object_id='1257285', aspect='media', callback_url='http://mydomain.com/hook/instagram')
    # Subscribe to all media in a geographic area
    api.create_subscription(object='geography', lat=35.657872, lng=139.70232, radius=1000, aspect='media', callback_url='http://mydomain.com/hook/instagram')
 
Along with that, you would typically register subscription "reactors" for processing the different subscription types:

    # React to user type updates
    reactor = subscriptions.SubscriptionsReactor()
    reactor.register_callback(subscriptions.SubscriptionType.USER, process_user_update)
    
See the provided sample app for an example of making a subscription, reacting to it, an processing the updates.

You can also use the API to list and delete subscriptions:
    api.list_subscriptions()
    api.delete_subscriptions(id=342342)
   

Data Retrieval:
-----

See the endpoints docs for more on these methods: http://instagr.am/developer/endpoints/

The methods with a * return two values, where the second is a pagination parameter. Here's an example of retrieving recent media:

    recent_media, next = api.user_recent_media()
    photos = []
    for media in recent_media:
        photos.append('<img src="%s"/>' % media.images['thumbnail'].url)
            

Users: http://instagr.am/developer/endpoints/users/
    
    api.user(user_id)
    api.user_media_feed()*
    api.user_liked_media()*
    api.user_recent_media(user_id, count, max_id)*
    api.user_search(q, count, lat, lng, min_timestamp, max_timestamp)
    
   
Relationships: http://instagr.am/developer/endpoints/relationships/

    api.user_incoming_requests()
    api.user_follows(user_id)*
    api.user_followed_by(user_id)*
    api.follow_user(user_id)
    api.unfollow_user(user_id)
    api.block_user(user_id)
    api.unblock_user(user_id)
    api.approve_user_request(user_id)
    api.ignore_user_request(user_id)
    api.user_relationship(user_id)


Media: http://instagr.am/developer/endpoints/media/

    api.media(media_id)
    api.media_popular(count, max_id)
    api.media_search(q, count, lat, lng, min_timestamp, max_timestamp)
    
Comments: http://instagr.am/developer/endpoints/comments/

    api.media_comments(media_id)
    api.create_media_comment(media_id, text)
    api.delete_comment(media_id, comment_id)
    
Likes: http://instagr.am/developer/endpoints/likes/

    api.media_likes(media_id)
    api.like_media(media_id)
    api.unlike_media(media_id)
    
Tags: http://instagr.am/developer/endpoints/tags/

    api.tag(tag_name) 
    api.tag_recent_media(count, max_id, tag_name)*
    api.tag_search(q, count)*
 
Locations: http://instagr.am/developer/endpoints/locations/

    api.location(location_id)
    api.location_recent_media(count, max_id, location_id)*
    api.location_search(q, count, lat, lng, foursquare_id)
    
Geographies: http://instagr.am/developer/endpoints/geographies/

    api.geography_recent_media(count, max_id, geography_id)*


Sample app
------
This repository includes a one-file sample app that uses the bottle framework and demonstrates
authentication, subscriptions, and update processing. To try it out:

  * Download bottle if you don't already have it: pip install bottle
  * Set your redirect URI to 'http://localhost:8515/oauth_callback' in your dev profile
  * Open up sample\_app.py, update it with your client\_id and secret, and set redirect URI to 'http://localhost:8515/oauth_callback'
  * Run the file; it will host a local server on port 8515.
  * Try visiting http://localhost:8515 in your browser
