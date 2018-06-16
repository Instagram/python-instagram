import urllib
from .oauth2 import OAuth2Request
import re
from .json_import import simplejson
import hmac
from hashlib import sha256
import six
from six.moves.urllib.parse import quote
import sys

re_path_template = re.compile('{\w+}')


def encode_string(value):
    return value.encode('utf-8') \
        if isinstance(value, six.text_type) else str(value)


class InstagramClientError(Exception):
    def __init__(self, error_message, status_code=None):
        self.status_code = status_code
        self.error_message = error_message

    def __str__(self):
        if self.status_code:
            return "(%s) %s" % (self.status_code, self.error_message)
        else:
            return self.error_message


class InstagramAPIError(Exception):

    def __init__(self, status_code, error_type, error_message, *args, **kwargs):
        self.status_code = status_code
        self.error_type = error_type
        self.error_message = error_message

    def __str__(self):
        return "(%s) %s-%s" % (self.status_code, self.error_type, self.error_message)


def bind_method(**config):

    class InstagramAPIMethod(object):

        path = config['path']
        method = config.get('method', 'GET')
        accepts_parameters = config.get("accepts_parameters", [])
        signature = config.get("signature", False)
        requires_target_user = config.get('requires_target_user', False)
        paginates = config.get('paginates', False)
        root_class = config.get('root_class', None)
        response_type = config.get("response_type", "list")
        include_secret = config.get("include_secret", False)
        objectify_response = config.get("objectify_response", True)
        exclude_format = config.get('exclude_format', False)

        def __init__(self, api, *args, **kwargs):
            self.api = api
            self.as_generator = kwargs.pop("as_generator", False)
            if self.as_generator:
                self.pagination_format = 'next_url'
            else:
                self.pagination_format = kwargs.pop('pagination_format', 'next_url')
            self.return_json = kwargs.pop("return_json", False)
            self.max_pages = kwargs.pop("max_pages", 3)
            self.with_next_url = kwargs.pop("with_next_url", None)
            self.parameters = {}
            self._build_parameters(args, kwargs)
            self._build_path()

        def _build_parameters(self, args, kwargs):
            # via tweepy https://github.com/joshthecoder/tweepy/
            for index, value in enumerate(args):
                if value is None:
                    continue

                try:
                    self.parameters[self.accepts_parameters[index]] = encode_string(value)
                except IndexError:
                    raise InstagramClientError("Too many arguments supplied")

            for key, value in six.iteritems(kwargs):
                if value is None:
                    continue
                if key in self.parameters:
                    raise InstagramClientError("Parameter %s already supplied" % key)
                self.parameters[key] = encode_string(value)
            if 'user_id' in self.accepts_parameters and not 'user_id' in self.parameters \
               and not self.requires_target_user:
                self.parameters['user_id'] = 'self'

        def _build_path(self):
            for variable in re_path_template.findall(self.path):
                name = variable.strip('{}')

                try:
                    value = quote(self.parameters[name])
                except KeyError:
                    raise Exception('No parameter value found for path variable: %s' % name)
                del self.parameters[name]

                self.path = self.path.replace(variable, value)

            if self.api.format and not self.exclude_format:
                self.path = self.path + '.%s' % self.api.format

        def _build_pagination_info(self, content_obj):
            """Extract pagination information in the desired format."""
            pagination = content_obj.get('pagination', {})
            if self.pagination_format == 'next_url':
                return pagination.get('next_url')
            if self.pagination_format == 'dict':
                return pagination
            raise Exception('Invalid value for pagination_format: %s' % self.pagination_format)
          
        def _do_api_request(self, url, method="GET", body=None, headers=None):
            headers = headers or {}
            if self.signature and self.api.client_ips != None and self.api.client_secret != None:
                secret = self.api.client_secret
                ips = self.api.client_ips
                signature = hmac.new(secret, ips, sha256).hexdigest()
                headers['X-Insta-Forwarded-For'] = '|'.join([ips, signature])

            response, content = OAuth2Request(self.api).make_request(url, method=method, body=body, headers=headers)
            if response['status'] == '503' or response['status'] == '429':
                raise InstagramAPIError(response['status'], "Rate limited", "Your client is making too many request per second")
            try:
                content_obj = simplejson.loads(content)
            except ValueError:
                raise InstagramClientError('Unable to parse response, not valid JSON.', status_code=response['status'])
            # Handle OAuthRateLimitExceeded from Instagram's Nginx which uses different format to documented api responses
            if 'meta' not in content_obj:
                if content_obj.get('code') == 420 or content_obj.get('code') == 429:
                    error_message = content_obj.get('error_message') or "Your client is making too many request per second"
                    raise InstagramAPIError(content_obj.get('code'), "Rate limited", error_message)
                raise InstagramAPIError(content_obj.get('code'), content_obj.get('error_type'), content_obj.get('error_message'))
            api_responses = []
            status_code = content_obj['meta']['code']
            self.api.x_ratelimit_remaining = response.get("x-ratelimit-remaining",None)
            self.api.x_ratelimit = response.get("x-ratelimit-limit",None)
            if status_code == 200:
                if not self.objectify_response:
                    return content_obj, None

                if self.response_type == 'list':
                    for entry in content_obj['data']:
                        if self.return_json:
                            api_responses.append(entry)
                        else:
                            obj = self.root_class.object_from_dictionary(entry)
                            api_responses.append(obj)
                elif self.response_type == 'entry':
                    data = content_obj['data']
                    if self.return_json:
                        api_responses = data
                    else:
                        api_responses = self.root_class.object_from_dictionary(data)
                elif self.response_type == 'empty':
                    pass
                return api_responses, self._build_pagination_info(content_obj)
            else:
                raise InstagramAPIError(status_code, content_obj['meta']['error_type'], content_obj['meta']['error_message'])

        def _paginator_with_url(self, url, method="GET", body=None, headers=None):
            headers = headers or {}
            pages_read = 0
            while url and (self.max_pages is None or pages_read < self.max_pages):
                api_responses, url = self._do_api_request(url, method, body, headers)
                pages_read += 1
                yield api_responses, url
            return

        def _get_with_next_url(self, url, method="GET", body=None, headers=None):
            headers = headers or {}
            content, next = self._do_api_request(url, method, body, headers)
            return content, next

        def execute(self):
            url, method, body, headers = OAuth2Request(self.api).prepare_request(self.method,
                                                                                 self.path,
                                                                                 self.parameters,
                                                                                 include_secret=self.include_secret)
            if self.with_next_url:
                return self._get_with_next_url(self.with_next_url, method, body, headers)
            if self.as_generator:
                return self._paginator_with_url(url, method, body, headers)
            else:
                content, next = self._do_api_request(url, method, body, headers)
            if self.paginates:
                return content, next
            else:
                return content

    def _call(api, *args, **kwargs):
        method = InstagramAPIMethod(api, *args, **kwargs)
        return method.execute()

    return _call
