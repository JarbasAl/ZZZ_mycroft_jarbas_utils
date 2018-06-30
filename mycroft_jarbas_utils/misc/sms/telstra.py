from __future__ import print_function
import requests

'''
# Obtain these keys from the Telstra Developer Portal
CONSUMER_KEY="your consumer key"
CONSUMER_SECRET="your consumer secret"

curl -X POST \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "client_id=$9Ni2Ny6uLaVP8AGFP4CyARzdPeh6e8M0&client_secret=ocP8bA26xfuacu3A&grant_type=client_credentials&scope=SMS" \
"https://api.telstra.com/v1/oauth/token"
'''

'''
# * Recipient number should be in the format of "04xxxxxxxx" where x is a digit
# * Authorization header value should be in the format of "Bearer xxx" where xxx is access token returned 
#   from a previous GET https://api.telstra.com/v1/oauth/token request.
RECIPIENT_NUMBER="your number"
TOKEN="<access_token>"

curl -H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d "{\"to\":\"$RECIPIENT_NUMBER\", \"body\":\"Hello!\"}" \
"https://api.telstra.com/v1/sms/messages"
'''


def sendSMS(key, secret, mobile, message):
    r = requests.post("https://api.telstra.com/v1/oauth/token",
                      data={
                          "client_id": key,
                          "client_secret": secret,
                          "grant_type": "client_credentials",
                          "scope": "SMS"
                      },
                      headers={
                          "Content-Type": "application/x-www-form-urlencoded"
                      }
                      )
    print(r)
    response_json = r.json()
    print(response_json)
    access_token = response_json['access_token']
    # print(access_token)

    r = requests.post("https://api.telstra.com/v1/sms/messages",
                      json={
                          "to": mobile,
                          "body": message
                      },
                      headers={
                          "Content-Type": "application/json",
                          "Authorization": "Bearer " + access_token
                      }
                      )


CONSUMER_KEY = u"9Ni2Ny6uLaVP8AGFP4CyARzdPeh6e8M0"
CONSUMER_SECRET = u"ocP8bA26xfuacu3A"
MOBILE_PHONENUMBER = '351964102979'
MESSAGE = "It works!"
sendSMS(CONSUMER_KEY, CONSUMER_SECRET, MOBILE_PHONENUMBER, MESSAGE)
