import hmac
import hashlib
from .json_import import simplejson

class SubscriptionType:
    TAG = 'tag'
    USER = 'user'
    GEOGRAPHY = 'geography'
    LOCATION = 'location'


class SubscriptionError(Exception):
    pass


class SubscriptionVerifyError(SubscriptionError):
    pass


class SubscriptionsReactor(object):

    def __init__(self):
        self.callbacks = {}

    def _process_update(self, update):
        object_callbacks = self.callbacks.get(update['object'], [])

        for callback in object_callbacks:
            callback(update)

    def process(self, client_secret, raw_response, x_hub_signature):
        if not self._verify_signature(client_secret, raw_response, x_hub_signature):
            raise SubscriptionVerifyError("X-Hub-Signature and hmac digest did not match")

        try:
            response = simplejson.loads(raw_response)
        except ValueError:
            raise SubscriptionError('Unable to parse response, not valid JSON.')

        for update in response:
            self._process_update(update)

    def register_callback(self, object_type, callback):
        cb_list = self.callbacks.get(object_type, [])

        if callback not in cb_list:
            cb_list.append(callback)
            self.callbacks[object_type] = cb_list

    def deregister_callback(self, object_type, callback):
        callbacks = self.callbacks.get(object_type, [])
        callbacks.remove(callback)

    def _verify_signature(self, client_secret, raw_response, x_hub_signature):
        digest = hmac.new(client_secret.encode('utf-8'),
                          msg=raw_response.encode('utf-8'),
                          digestmod=hashlib.sha1
                          ).hexdigest()
        return digest == x_hub_signature
