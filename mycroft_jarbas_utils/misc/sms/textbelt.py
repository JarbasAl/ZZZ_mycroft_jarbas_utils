from __future__ import print_function
# The Wrapper Implementation Of Textbelt SMS API
# @author ksdme

# Based On Requests
from builtins import str
from builtins import object
import requests


# The Namespace Class
class Textbelt(object):
    # API URL
    API_URL = 'http://0.0.0.0:9090/'

    # The Recipient Class
    class Recipient(object):
        # Available Regions
        REGIONS = {"us": "text", "ca": "canada", "intl": "intl"}

        def __init__(self, phone, region="us", tag=None):
            self.region = region
            self.phone = phone
            self.tag = tag

        @property
        def phone(self):
            return self._phone

        @phone.setter
        def phone(self, phone):
            self._phone = str(phone)

        @property
        def region(self):
            return self._region

        @region.setter
        def region(self, region):
            assert region in Textbelt.Recipient.REGIONS, "Bad Region Code"
            self._region = Textbelt.Recipient.REGIONS[region]

        @property
        def tag(self):
            return self._tag

        @tag.setter
        def tag(self, tag):
            self._tag = tag
            return self

        # Send The Message
        def send(self, message):
            message = str(message)
            assert len(message) > 1, "Message Too Short"

            # API URL
            mAPI = Textbelt.API_URL + self.region

            mResponse = requests.post(mAPI, {
                'number': self.phone,
                'message': message
            })
            return mResponse.json()


Recipient = Textbelt.Recipient("+351964102979", "intl")
reponse = Recipient.send("Hello World!")
print(reponse)
# reponse = Recipient.send("Its me, The Bot.")
