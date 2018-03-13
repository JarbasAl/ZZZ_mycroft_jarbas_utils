import requests
from requests.exceptions import ConnectionError
import time
import json

# filter warnings, this should be removed once we stop using self signed
# certs for debug
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class MycroftAPI(object):
    def __init__(self, api, lang="en-us", url="https://104.236.133.170:6712/"):
        self.api = api
        self.headers = {"Authorization": str(self.api)}
        self.lang = lang
        self.url = url
        self.timeout = 10
        self.wait_time = 0.5

    def hello_world(self):
       try:
           response = requests.get(
               self.url,
               headers=self.headers, verify=False
           )
           return response.text
       except ConnectionError as e:
           raise ConnectionError("Could not connect: " + str(e))

    def new_user(self, key, mail, name):
        ''' add a new user, requires admin api '''
        try:
            response = requests.put(
                self.url+"new_user/"+key+"/"+mail+"/"+name,
                headers=self.headers, verify=False
            )
            try:
                return response.json()
            except:
                print response.text
                raise ValueError("Invalid admin api key")
        except ConnectionError as e:
            raise ConnectionError("Could not connect: " + str(e))

    def revoke_api(self, api):
        ''' add a new user, requires admin api '''
        try:
            response = requests.put(
                self.url+"revoke_api/"+api,
                headers=self.headers, verify=False
            )
            try:
                return response.json()
            except:
                print response.text
                raise ValueError("Invalid admin api key")
        except ConnectionError as e:
            raise ConnectionError("Could not connect: " + str(e))

    def get_api(self):
        ''' get an api key string, requires admin api '''
        try:
            response = requests.get(
                self.url+"get_api",
                headers=self.headers, verify=False
            )
            try:
                return response.json()["api"]
            except:
                print response.text
                raise ValueError("Invalid admin api key")
        except ConnectionError as e:
            raise ConnectionError("Could not connect: " + str(e))

    def get_vocab_map(self, lang=None):
        ''' get intent this utterance will trigger NOT AVAILABLE '''
        lang = lang or self.lang
        try:
            response = requests.get(
                self.url+"vocab_map/"+lang,
                headers=self.headers, verify=False
            )
            try:
                return response.json()
            except:
                print response.text
                raise ValueError("Invalid api key")
        except ConnectionError as e:
            print e
            raise ConnectionError("Could not connect")

    def get_skills_map(self, lang=None):
        ''' get intent this utterance will trigger NOT AVAILABLE '''
        lang = lang or self.lang
        try:
            response = requests.get(
                self.url+"skills_map/"+lang,
                headers=self.headers, verify=False
            )
            try:
                return response.json()
            except:
                print response.text
                raise ValueError("Invalid api key")
        except ConnectionError as e:
            print e
            raise ConnectionError("Could not connect")

    def get_intent_map(self, lang=None):
        ''' get intent this utterance will trigger NOT AVAILABLE '''
        lang = lang or self.lang
        try:
            response = requests.get(
                self.url+"intent_map/"+lang,
                headers=self.headers, verify=False
            )
            try:
                return response.json()
            except:
                print response.text
                raise ValueError("Invalid api key")
        except ConnectionError as e:
            print e
            raise ConnectionError("Could not connect")

    def get_intent(self, utterance, lang=None):
        ''' get intent this utterance will trigger NOT AVAILABLE '''
        lang = lang or self.lang
        try:
            response = requests.get(
                self.url+"get_intent/"+lang+"/"+utterance,
                headers=self.headers, verify=False
            )
            try:
                return response.json()
            except:
                print response.text
                raise ValueError("Invalid api key")
        except ConnectionError as e:
            print e
            raise ConnectionError("Could not connect")

    def ask_mycroft(self, utterance, lang=None):
        ''' ask something to mycroft '''
        lang = lang or self.lang
        try:
            response = requests.put(
                self.url+"ask/"+lang+"/"+utterance,
                headers=self.headers, verify=False
            )
            try:
                ans = response.json()
                if ans["status"] == "processing":
                    # start waiting
                    start = time.time()
                    while ans["status"] == "processing":
                        time.sleep(self.wait_time)
                        if time.time() - start > self.timeout:
                            try:
                                response = requests.put(
                                    self.url + "cancel",
                                    headers=self.headers, verify=False
                                )
                            except Exception as e:
                                print e

                            return {"type": "speak",
                                    "data": {"utterance": "server timed "
                                                          "out"},
                                    "context": {"source": "https server",
                                                "target": self.api}}
                        try:
                            response = requests.get(
                                self.url + "get_answer",
                                headers=self.headers, verify=False
                            )
                            ans = response.json()
                        except Exception as e:
                            raise ValueError("Unexpected Error: " + str(e))
                    return json.loads(ans["answer"])
                else:
                    raise ValueError("Received unexpected status from "
                                     "server: " + str(ans))
            except:
                print response.text
                raise ValueError("Invalid api key: " + str(self.api))
        except ConnectionError as e:
            raise ConnectionError("Could not connect: " + str(e))

if __name__ == "__main__":
    # test if admin privileges are properly blocked
    ap = MycroftAPI("test_key", url="https://104.236.133.170:6712/")

    # test connection
    print ap.hello_world()

    # test functionality
    ap = MycroftAPI("new_key")
    print ap.ask_mycroft("hello world")
    print ap.ask_mycroft("tell me a joke")
    print ap.ask_mycroft("tell me about quantum decoherence")
    print ap.ask_mycroft("do you like pizza")

    print ap.get_intent("hello world")
    print ap.get_intent_map()
    print ap.get_vocab_map()
    print ap.get_skills_map()

    # test admin privileges
    try:
        print ap.new_user("new_key", "0", "test")
        print "whoa, anyone can make himself an user_id"
    except:
        pass
    try:
        print ap.get_api()
        print "whoa, anyone can generate an api key"
    except:
        pass

    ap = MycroftAPI("admin_key")
    print ap.new_user("new_key", "0", "test")
    print ap.get_api()
    print ap.revoke_api("new_key")
    print ap.revoke_api("test_key")
    print ap.revoke_api("invalid_key")



