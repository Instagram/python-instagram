import oauth2
from bind import bind_method
from models import Media, User, Location, Tag, Comment, Relationship

MEDIA_ACCEPT_PARAMETERS = ["count", "max_id", "min_id", "max_tag_id"]
SEARCH_ACCEPT_PARAMETERS = ["q", "count"]

SUPPORTED_FORMATS = ['json']


class InstagramAPI(oauth2.OAuth2API):

    host = "api.instagram.com"
    base_path = "/v1"
    access_token_field = "access_token"
    authorize_url = "https://api.instagram.com/oauth/authorize"
    access_token_url = "https://api.instagram.com/oauth/access_token"
    protocol = "https"
    api_name = "Instagram"

    def __init__(self, *args, **kwargs):
        format = kwargs.get('format', 'json')
        if format in SUPPORTED_FORMATS:
            self.format = format
        else:
            raise Exception("Unsupported format")
        super(InstagramAPI, self).__init__(*args, **kwargs)

    media_popular = bind_method(
                path="/media/popular",
                accepts_parameters=MEDIA_ACCEPT_PARAMETERS,
                root_class=Media)

    media_search = bind_method(
                path="/media/search",
                accepts_parameters=SEARCH_ACCEPT_PARAMETERS + ['lat', 'lng', 'min_timestamp', 'max_timestamp'],
                root_class=Media)

    media_likes = bind_method(
                path="/media/{media_id}/likes",
                accepts_parameters=['media_id'],
                root_class=User)

    like_media = bind_method(
                path="/media/{media_id}/likes",
                method="POST",
                accepts_parameters=['media_id'],
                response_type="empty")

    unlike_media = bind_method(
                path="/media/{media_id}/likes",
                method="DELETE",
                accepts_parameters=['media_id'],
                response_type="empty")

    create_media_comment = bind_method(
                path="/media/{media_id}/comments",
                method="POST",
                accepts_parameters=['media_id', 'text'],
                response_type="entry",
                root_class=Comment)

    delete_comment = bind_method(
                path="/media/{media_id}/comments/{comment_id}",
                method="DELETE",
                accepts_parameters=['media_id', 'comment_id'],
                response_type="empty")

    media_comments = bind_method(
                path="/media/{media_id}/comments",
                method="GET",
                accepts_parameters=['media_id'],
                response_type="list",
                root_class=Comment)

    media = bind_method(
                path="/media/{media_id}",
                accepts_parameters=['media_id'],
                response_type="entry",
                root_class=Media)

    # max_id 	Return media earlier than this max_id
    # min_id 	Return media later than this min_id
    user_media_feed = bind_method(
                path="/users/self/feed",
                accepts_parameters=MEDIA_ACCEPT_PARAMETERS,
                root_class=Media,
                paginates=True)

    # max_like_id 	Return media liked before this id
    user_liked_media = bind_method(
                path="/users/self/media/liked",
                accepts_parameters=MEDIA_ACCEPT_PARAMETERS,
                root_class=Media,
                paginates=True)

    # max_id 	Return media earlier than this max_id
    # min_id 	Return media later than this min_id
    user_recent_media = bind_method(
                path="/users/{user_id}/media/recent",
                accepts_parameters=MEDIA_ACCEPT_PARAMETERS + ['user_id', 'max_timestamp', 'min_timestamp'],
                root_class=Media,
                paginates=True)

    user_search = bind_method(
                path="/users/search",
                accepts_parameters=SEARCH_ACCEPT_PARAMETERS,
                root_class=User)

    ## pagination not documented
    user_follows = bind_method(
                path="/users/{user_id}/follows",
                accepts_parameters=["user_id"],
                paginates=True,
                root_class=User)

    ## pagination not documented
    user_followed_by = bind_method(
                path="/users/{user_id}/followed-by",
                accepts_parameters=["user_id"],
                paginates=True,
                root_class=User)

    user = bind_method(
                path="/users/{user_id}",
                accepts_parameters=["user_id"],
                root_class=User,
                response_type="entry")

    # max_id 	Return media after this max_id
    # min_id 	Return media before this min_id
    # min_timestamp 	Return media after this UNIX timestamp
    # max_timestamp 	Return media before this UNIX timestamp
    location_recent_media = bind_method(
                path="/locations/{location_id}/media/recent",
                accepts_parameters=MEDIA_ACCEPT_PARAMETERS + ['location_id'],
                root_class=Media,
                paginates=True)

    location_search = bind_method(
                path="/locations/search",
                accepts_parameters=SEARCH_ACCEPT_PARAMETERS + ['lat', 'lng', 'foursquare_id'],
                root_class=Location)

    location = bind_method(
                path="/locations/{location_id}",
                accepts_parameters=["location_id"],
                root_class=Location,
                response_type="entry")

    ## pagination not documented
    geography_recent_media = bind_method(
                path="/geographies/{geography_id}/media/recent",
                accepts_parameters=MEDIA_ACCEPT_PARAMETERS + ["geography_id"],
                root_class=Media,
                paginates=True)

    # max_id 	Return media after this max_id
    # min_id 	Return media before this min_id
    tag_recent_media = bind_method(
                path="/tags/{tag_name}/media/recent",
                accepts_parameters=MEDIA_ACCEPT_PARAMETERS + ['tag_name'],
                root_class=Media,
                paginates=True)

    ## pagination not documented
    tag_search = bind_method(
                path="/tags/search",
                accepts_parameters=SEARCH_ACCEPT_PARAMETERS,
                root_class=Tag,
                paginates=True)

    tag = bind_method(
                path="/tags/{tag_name}",
                accepts_parameters=["tag_name"],
                root_class=Tag,
                response_type="entry")

    user_incoming_requests = bind_method(
                path="/users/self/requested-by",
                root_class=User)

    ## pagination not documented
    change_user_relationship = bind_method(
                method="POST",
                path="/users/{user_id}/relationship",
                root_class=Relationship,
                accepts_parameters=["user_id", "action"],
                paginates=True,
                requires_target_user=True,
                response_type="entry")

    user_relationship = bind_method(
                method="GET",
                path="/users/{user_id}/relationship",
                root_class=Relationship,
                accepts_parameters=["user_id"],
                paginates=False,
                requires_target_user=True,
                response_type="entry")

    def _make_relationship_shortcut(action):
        def _inner(self, *args, **kwargs):
            return self.change_user_relationship(user_id=kwargs.get("user_id"),
                                                 action=action)
        return _inner

    follow_user = _make_relationship_shortcut('follow')
    unfollow_user = _make_relationship_shortcut('unfollow')
    block_user = _make_relationship_shortcut('block')
    unblock_user = _make_relationship_shortcut('unblock')
    approve_user_request = _make_relationship_shortcut('approve')
    ignore_user_request = _make_relationship_shortcut('ignore')

    def _make_subscription_action(method, include=None, exclude=None):
        accepts_parameters = ["object",
                              "aspect",
                              "object_id",  # Optional if subscribing to all users
                              "callback_url",
                              "lat",  # Geography
                              "lng",  # Geography
                              "radius",  # Geography
                              "verify_token"]

        if include:
            accepts_parameters.extend(include)
        if exclude:
            accepts_parameters = [x for x in accepts_parameters if x not in exclude]
        return bind_method(
            path="/subscriptions",
            method=method,
            accepts_parameters=accepts_parameters,
            include_secret=True,
            objectify_response=False
        )

    create_subscription = _make_subscription_action('POST')
    list_subscriptions = _make_subscription_action('GET')
    delete_subscriptions = _make_subscription_action('DELETE', exclude=['object_id'], include=['id'])
