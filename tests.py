#!/usr/bin/env python

import types
import six
try:
    import simplejson as json
except ImportError:
    import json
import getpass
import unittest
from six.moves.urllib.parse import urlparse, parse_qs
from instagram import client, oauth2, InstagramAPIError

TEST_AUTH = False
client_id = "DEBUG"
client_secret = "DEBUG"
access_token = "DEBUG"
redirect_uri = "http://example.com"

class MockHttp(object):

    def __init__(self, *args, **kwargs):
        pass

    def request(self, url, method="GET", body=None, headers={}):
        fail_state = {
            'status':'400'
        }, "{}"

        parsed = urlparse(url)
        options = parse_qs(parsed.query)

        fn_name = str(active_call)
        if fn_name == 'get_authorize_login_url':
            return {
                'status': '200',
                'content-location':'http://example.com/redirect/login'
            }, None

        if not 'access_token' in options and not 'client_id' in options:
            fn_name += '_unauthorized'
        if 'self' in url and not 'access_token' in options:
            fn_name += '_no_auth_user'

        fl = open('fixtures/%s.json' % fn_name)
        content = fl.read()
        fl.close()
        json_content = json.loads(content)
        status = json_content['meta']['code']
        return {
            'status': status
        }, content

oauth2.Http = MockHttp

active_call = None
class TestInstagramAPI(client.InstagramAPI):
    def __getattribute__(self, attr):
        global active_call
        actual_val = super(TestInstagramAPI, self).__getattribute__(attr)
        if isinstance(actual_val, types.MethodType):
            active_call = attr
        return actual_val

class InstagramAuthTests(unittest.TestCase):
    def setUp(self):
        self.unauthenticated_api = TestInstagramAPI(client_id=client_id, redirect_uri=redirect_uri, client_secret=client_secret)

    def test_authorize_login_url(self):
        redirect_uri = self.unauthenticated_api.get_authorize_login_url()
        assert redirect_uri
        print("Please visit and authorize at:\n%s" % redirect_uri)
        code = raw_input("Paste received code (blank to skip): ").strip()
        if not code:
            return

        access_token = self.unauthenticated_api.exchange_code_for_access_token(code)
        assert access_token

    def test_xauth_exchange(self):
        """ Your client ID must be authorized for xAuth access; email
            xauth@instagram.com for access"""
        username = raw_input("Enter username for XAuth (blank to skip): ").strip()
        if not username:
            return
        password =  getpass.getpass("Enter password for XAuth (blank to skip): ").strip()
        access_token = self.unauthenticated_api.exchange_xauth_login_for_access_token(username, password)
        assert access_token

class InstagramAPITests(unittest.TestCase):

    def setUp(self):
        super(InstagramAPITests, self).setUp()
        self.client_only_api = TestInstagramAPI(client_id=client_id)
        self.api = TestInstagramAPI(access_token=access_token)

    def test_media_popular(self):
        self.api.media_popular(count=10)

    def test_media_search(self):
        self.client_only_api.media_search(lat=37.7,lng=-122.22)
        self.api.media_search(lat=37.7,lng=-122.22)

    def test_media_shortcode(self):
        self.client_only_api.media_shortcode('os1NQjxtvF')
        self.api.media_shortcode('os1NQjxtvF')

    def test_media_likes(self):
        self.client_only_api.media_likes(media_id=4)

    def test_like_media(self):
        self.api.like_media(media_id=4)
        self.api.unlike_media(media_id=4)

    """
    TEMP; disabled this test while we add
    a proper response to create_media_comment
    def test_comment_media(self):
        comment = self.api.create_media_comment(media_id=4, text='test')
        self.api.delete_comment(media_id=4, comment_id=comment.id)
    """

    def test_user_feed(self):
        self.api.user_media_feed(count=50)

    def test_generator_user_feed(self):
        generator = self.api.user_media_feed(as_generator=True, max_pages=3, count=2)
        for page in generator:
            str(generator)

    def test_generator_user_feed_all(self):
        generator = self.api.user_media_feed(as_generator=True, max_pages=None)
        for i in range(10):
            page = six.advance_iterator(generator)
            str(generator)

        generator = self.api.user_media_feed(as_generator=True, max_pages=0)
        for page in generator:
            assert False

    def test_user_liked_media(self):
        self.api.user_liked_media(count=10)

    def test_user_recent_media(self):
        media, url = self.api.user_recent_media(count=10)

        self.assertTrue( all( [hasattr(obj, 'type') for obj in media] ) )

        image = media[0]
        self.assertEqual(
                image.get_standard_resolution_url(),
                "http://distillery-dev.s3.amazonaws.com/media/2011/02/02/1ce5f3f490a640ca9068e6000c91adc5_7.jpg")

        self.assertEqual(
                image.get_low_resolution_url(),
                "http://distillery-dev.s3.amazonaws.com/media/2011/02/02/1ce5f3f490a640ca9068e6000c91adc5_6.jpg")

        self.assertEqual(
                image.get_thumbnail_url(),
                "http://distillery-dev.s3.amazonaws.com/media/2011/02/02/1ce5f3f490a640ca9068e6000c91adc5_5.jpg")

        self.assertEqual( False, hasattr(image, 'videos') )

        video = media[1]
        self.assertEqual(
                video.get_standard_resolution_url(),
                video.videos['standard_resolution'].url)

        self.assertEqual(
                video.get_standard_resolution_url(),
                "http://distilleryvesper9-13.ak.instagram.com/090d06dad9cd11e2aa0912313817975d_101.mp4")

        self.assertEqual(
                video.get_low_resolution_url(),
                "http://distilleryvesper9-13.ak.instagram.com/090d06dad9cd11e2aa0912313817975d_102.mp4")

        self.assertEqual(
                video.get_thumbnail_url(),
                "http://distilleryimage2.ak.instagram.com/11f75f1cd9cc11e2a0fd22000aa8039a_5.jpg")





    def test_user_search(self):
        self.api.user_search('mikeyk', 10)

    def test_user_follows(self):
        for page in self.api.user_followed_by(as_generator=True):
            str(page)

    def test_user_followed_by(self):
        for page in self.api.user_followed_by(as_generator=True):
            str(page)

    def test_other_user_followed_by(self):
        self.api.user_followed_by(user_id=3)

    def test_self_info(self):
        self.api.user()
        self.assertRaises(InstagramAPIError, self.client_only_api.user)

    def test_location_recent_media(self):
        self.api.location_recent_media(location_id=1)

    def test_location_search(self):
        self.api.location_search(lat=37.7,lng=-122.22, distance=2500)

    def test_location(self):
        self.api.location(1)

    def test_tag_recent_media(self):
        self.api.tag_recent_media(tag_name='1', count=5, max_tag_id='12345')

    def test_tag_recent_media_paginated(self):
        for page in self.api.tag_recent_media(tag_name='1', count=5, as_generator=True, max_pages=2):
            str(page)

    def test_tag_search(self):
        self.api.tag_search("coff")

    def test_tag(self):
        self.api.tag("coffee")

    def test_user_follows(self):
        self.api.user_follows()

    def test_user_followed_by(self):
        self.api.user_followed_by()

    def test_user_followed_by(self):
        self.api.user_followed_by()

    def test_user_requested_by(self):
        self.api.user_followed_by()

    def test_user_incoming_requests(self):
        self.api.user_incoming_requests()

    def test_change_relationship(self):
        self.api.change_user_relationship(user_id=10, action="follow")
        # test shortcuts as well
        self.api.follow_user(user_id='10')
        self.api.unfollow_user(user_id='10')

    def test_geography_recent_media(self):
        self.api.geography_recent_media(geography_id=1)

if __name__ == '__main__':
    if not TEST_AUTH:
        del InstagramAuthTests

    unittest.main()
