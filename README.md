- - -

**_This project is not actively maintained. Proceed at your own risk!_**

- - - 

[![Build Status](https://api.travis-ci.org/Instagram/python-instagram.svg)](https://travis-ci.org/Instagram/python-instagram)

python-instagram
======
A Python 2/3 client for the Instagram REST and Search APIs

Installation
-----
```
pip install python-instagram
```
Requires
-----
  * httplib2
  * simplejson
  * six


Instagram REST and Search APIs
------------------------------
Our [developer site](http://instagram.com/developer) documents all the Instagram REST and Search APIs.


Blog
----------------------------
The [Developer Blog] features news and important announcements about the Instagram Platform. You will also find tutorials and best practices to help you build great platform integrations. Make sure to subscribe to the RSS feed not to miss out on new posts: [http://developers.instagram.com](http://developers.instagram.com).


Community
----------------------
The [Stack Overflow community](http://stackoverflow.com/questions/tagged/instagram/) is a great place to ask API related questions or if you need help with your code. Make sure to tag your questions with the Instagram tag to get fast answers from other fellow developers and members of the Instagram team.


Authentication
-----

Instagram API uses the OAuth2 protocol for authentication, but not all functionality requires authentication.
See the docs for more information: http://instagram.com/developer/authentication/

### Obtaining an access token

If you're using a method that requires authentication and need an access token, you can use the provided get_access_token.py script to obtain an access token for yourself.
It will prompt you for your app's Client ID, Client Secret, and Redirect URI, and walk you through instructions for getting your own access token for your app.

### Authenticating a user

The provided sample app shows a simple OAuth flow for authenticating a user and getting an access token for them.

### Using an access token

Once you have an access token (whether via the script or from the user flow), you can  pass that token into the InstagramAPI constructor:

``` python
from instagram.client import InstagramAPI

access_token = "YOUR_ACCESS_TOKEN"
client_secret = "YOUR_CLIENT_SECRET"
api = InstagramAPI(access_token=access_token, client_secret=client_secret)
recent_media, next_ = api.user_recent_media(user_id="userid", count=10)
for media in recent_media:
   print media.caption.text
```
       
### Making unauthenticated requests

For methods that don't require authentication, you can just pass your client ID and optionally client secret into the InstagramAPI 
constructor:

``` python
api = InstagramAPI(client_id='YOUR_CLIENT_ID', client_secret='YOUR_CLIENT_SECRET')
popular_media = api.media_popular(count=20)
for media in popular_media:
    print media.images['standard_resolution'].url
```

Real-time Subscriptions:
-----

See the docs for more on real-time subscriptions: http://instagr.am/developer/realtime/

You can use the API to subscribe to users, tags, locations, or geographies:

``` python
# Subscribe to updates for all users authenticated to your app
api.create_subscription(object='user', aspect='media', callback_url='http://mydomain.com/hook/instagram')

# Subscribe to all media tagged with 'fox'
api.create_subscription(object='tag', object_id='fox', aspect='media', callback_url='http://mydomain.com/hook/instagram')

# Subscribe to all media in a given location
api.create_subscription(object='location', object_id='1257285', aspect='media', callback_url='http://mydomain.com/hook/instagram')

# Subscribe to all media in a geographic area
api.create_subscription(object='geography', lat=35.657872, lng=139.70232, radius=1000, aspect='media', callback_url='http://mydomain.com/hook/instagram')
```

Along with that, you would typically register subscription "reactors" for processing the different subscription types:

``` python
# React to user type updates
reactor = subscriptions.SubscriptionsReactor()
reactor.register_callback(subscriptions.SubscriptionType.USER, process_user_update)
```
    
See the provided sample app for an example of making a subscription, reacting to it, an processing the updates.

You can also use the API to list and delete subscriptions:

``` python
api.list_subscriptions()
api.delete_subscriptions(id=342342)
```
   

Data Retrieval:
-----

See the endpoints docs for more on these methods: http://instagr.am/developer/endpoints/

The methods with a * return two values, where the second is a pagination parameter. Here's an example of retrieving recent media:

``` python
recent_media, next_ = api.user_recent_media()
photos = []
for media in recent_media:
    photos.append('<img src="%s"/>' % media.images['thumbnail'].url)
```            

And an example of exhaustively pursuing a paginated endpoint:

``` python
follows, next_ = api.user_follows()
while next_:
    more_follows, next_ = api.user_follows(with_next_url=next_)
    follows.extend(more_follows)
```

Users: http://instagr.am/developer/endpoints/users/
    
``` python
api.user(user_id)
api.user_media_feed()*
api.user_liked_media()*
api.user_recent_media(user_id, count, max_id)*
api.user_search(q, count, lat, lng, min_timestamp, max_timestamp)
```    
   
Relationships: http://instagr.am/developer/endpoints/relationships/

``` python
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
```

Media: http://instagr.am/developer/endpoints/media/

``` python
api.media(media_id)
api.media_popular(count, max_id)
api.media_search(q, count, lat, lng, min_timestamp, max_timestamp)
```
    
Comments: http://instagr.am/developer/endpoints/comments/

``` python
api.media_comments(media_id)
api.create_media_comment(media_id, text)
api.delete_comment(media_id, comment_id)
```
    
Likes: http://instagr.am/developer/endpoints/likes/

``` python
api.media_likes(media_id)
api.like_media(media_id)
api.unlike_media(media_id)
```
    
Tags: http://instagr.am/developer/endpoints/tags/

``` python
api.tag(tag_name) 
api.tag_recent_media(count, max_tag_id, tag_name)*
api.tag_search(q, count)*
```
 
Locations: http://instagr.am/developer/endpoints/locations/

``` python
api.location(location_id)
api.location_recent_media(count, max_id, location_id)*
api.location_search(q, count, lat, lng, foursquare_id, foursquare_v2_id)
```
    
Geographies: http://instagr.am/developer/endpoints/geographies/

``` python
api.geography_recent_media(count, max_id, geography_id)*
```

Error handling
------
Importing the bind module allows handling of specific error status codes. An example is provided below:
``` python
from instagram.bind import InstagramAPIError

try:
   # your code goes here
except InstagramAPIError as e:
   if (e.status_code == 400):
      print "\nUser is set to private."
```

Trouble Shooting
------

If you get an error of a module not being defined during the Instagram import call, this might update a necessary package.
```
sudo pip install --upgrade six
```

Sample app
------
This repository includes a one-file sample app that uses the bottle framework and demonstrates
authentication, subscriptions, and update processing. To try it out:

  * Download bottle if you don't already have it: pip install bottle
  * Download bottle-session if you don't already have it: pip install bottle-session
  * Download and run a redis instance on port 6379 if you don't already have it. Check http://redis.io for instructions.
  * Set your redirect URI to 'http://localhost:8515/oauth_callback' in your dev profile
  * Open up sample\_app.py, update it with your client\_id and secret, and set redirect URI to 'http://localhost:8515/oauth_callback'
  * Run the file; it will host a local server on port 8515.
  * Try visiting http://localhost:8515 in your browser

Contributing
------------
In the spirit of [free software](http://www.fsf.org/licensing/essays/free-sw.html), **everyone** is encouraged to help improve this project.

Here are some ways *you* can contribute:

* by using alpha, beta, and prerelease versions
* by reporting bugs
* by suggesting new features
* by writing or editing documentation
* by writing specifications
* by writing code (**no patch is too small**: fix typos, add comments, clean up inconsistent whitespace)
* by refactoring code
* by closing [issues](http://github.com/Instagram/python-instagram/issues)
* by reviewing patches


Submitting an Issue
-------------------
We use the [GitHub issue tracker](https://github.com/Instagram/python-instagram/issues) to track bugs and
features. Before submitting a bug report or feature request, check to make sure it hasn't already
been submitted. You can indicate support for an existing issue by voting it up. When submitting a
bug report, please include a [Gist](http://gist.github.com/) that includes a stack trace and any
details that may be necessary to reproduce the bug, including your version number, and
operating system. Ideally, a bug report should include a pull request with failing specs.


Submitting a Pull Request
-------------------------
1. Fork the project.
2. Create a topic branch.
3. Implement your feature or bug fix.
4. Run <tt>python tests.py </tt>.
5. Add a test for your feature or bug fix.
6. Run <tt>python tests.py </tt>. If your changes are not 100% covered, go back to step 5.
7. Commit and push your changes.
8. Submit a pull request.
9. If you haven't already, complete the Contributor License Agreement ("CLA").

Contributor License Agreement ("CLA")
_____________________________________
In order to accept your pull request, we need you to submit a CLA. You only need
to do this once to work on any of Instagram's or Facebook's open source projects.

Complete your CLA here: [https://code.facebook.com/cla](https://code.facebook.com/cla)


Copyright
---------
Copyright (c) 2014, Facebook, Inc. All rights reserved.
By contributing to python-instagram, you agree that your contributions will be licensed under its BSD license.
See [LICENSE](https://github.com/Instagram/python-instagram/blob/master/LICENSE.md) for details.
