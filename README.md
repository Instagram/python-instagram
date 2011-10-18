python-instagram
======
A Python client for the Instagram REST and Search APIs

Installation
-----
pip install instagram

Requires
-----
  * httplib2
  * simplejson

Follow @instagramapi on Twitter
----------------------------
You can [follow @instagramapi on Twitter](http://twitter.com/#!/instagramapi) for announcements,
updates, and news about the Instagram gem.

Obtaining an access token
-----
You can use the provided get_access_token.py script to obtain an access token for yourself. 
It will prompt you for your app's Client ID, Client Secret, and Redirect URI, 
and walk you through instructions for getting your own access token for your app.

Usage
-----
    from instagram.client import InstagramAPI

    access_token = "..."
    api = InstagramAPI(access_token=access_token)
    media_popular = api.media_popular(count=20)
	for media in media_popular:
	    print media.images['standard_resolution'].url

Sample app
------
We also provide a one-file sample app using bottle (you'll have to 'pip install bottle' first). To try it out:

  * Set your redirect URI to 'http://localhost:8515' in your dev profile
  * Open up sample\_app.py, update it with your client\_id and secret
  * Run the file; it will host a local server on port 8515.
  * Try visiting http://localhost:8515 in your browser


