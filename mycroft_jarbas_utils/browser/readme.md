# Usage

        from mycroft_jarbas_utils.browser import BrowserControl


# example, querying inspirobot

           def handle_inspirobot_intent(self, message):
                # get a browser control instance
                browser = BrowserControl(self.emitter)
                # get inspirobot url
                open = browser.open_url("http://inspirobot.me/")
                if open is None:
                    self.speak("Could not query inspirobot")
                    return

                # search generate button by xpath
                generate = ".//*[@id='top']/div[1]/div[2]/div/div[2]"
                browser.get_element(data=generate, name="generate", type="xpath")

                # click generate button
                browser.click_element("generate")

                # try until you find generated picture
                fails = 0
                sucess = False
                while fails < 5 and not sucess:
                    # find generated picture by class_name
                    browser.get_element(data="generated-image", name="pic", type="class")
                    # get attribute "src" of "pic" element
                    src = browser.get_attribute('src', 'pic')
                    # check if the adquired url is a generated picture or the default
                    if "generated.inspirobot" not in src:
                        fails += 1
                        sleep(0.5)
                    else:
                        sucess = True

                # tell user if you could not get picture
                if not sucess:
                    self.speak("could not get inspirobot generated picture")
                    return

                # download the image
                out_path = self.save_path + "/" + time.asctime() + ".jpg"
                urlretrieve(src, out_path.replace(" ", "_"))

                # give it to user
                self.speak("Here is your Inspirobot picture")

                # figure out how to display it
                self.display(out_path)

# example, querying cleverbot website

            def handle_ask_cleverbot_intent(self, message):
                ask = message.data.get("Ask")
                # get a browser control instance, optionally set to auto-start/restart browser
                browser = BrowserControl(self.emitter)#, autostart=False)
                # restart webbrowser if it is open (optionally)
                #started = browser.start_browser()
                #if not started:
                #    # TODO throw some error
                #    return
                browser.reset_elements()
                # get clevebot url
                open = browser.open_url("www.cleverbot.com")
                if open is None:
                    return
                # search this element by type and name it "input"
                browser.get_element(data="stimulus", name="input", type="name")
                # clear element named input
                #browser.clear_element("input")
                # send text to element named "input"
                browser.send_keys_to_element(text=ask, name="input", special=False)
                # send a key_press to element named "input"
                browser.send_keys_to_element(text="RETURN", name="input", special=True)

                # wait until you find element by xpath and name it sucess
                received = False
                fails = 0
                response = " "
                while response == " ":
                    while not received and fails < 5:
                        # returns false when element wasnt found
                        # this appears only after cleverbot finishes answering
                        received = browser.get_element(data=".//*[@id='snipTextIcon']", name="sucess", type="xpath")
                        fails += 1

                    # find element by xpath, name it "response"
                    browser.get_element(data=".//*[@id='line1']/span[1]", name="response", type="xpath")
                    # get text of the element named "response"
                    response = browser.get_element_text("response")

                self.speak(response)
                # clean the used elements for this session
                browser.reset_elements()
                # optionally close the browser
                #browser.close_browser()

# skill logs

        2017-06-16 20:16:01,046 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"source": "cli", "user": "unknown", "utterances": ["ask cleverbot what is the purpose of life"]}, "context": null}
        2017-06-16 20:16:01,112 - Skills - DEBUG - {"type": "BrowserSkill:AskCleverbotIntent", "data": {"confidence": 0.125, "target": "cli", "mute": false, "intent_type": "BrowserSkill:AskCleverbotIntent", "user": "unknown", "Ask": "what is purpose of", "utterance": "ask cleverbot what is the purpose of life"}, "context": {"target": "cli"}}
        2017-06-16 20:16:01,116 - Skills - DEBUG - {"type": "browser_reset_elements", "data": {}, "context": null}
        2017-06-16 20:16:01,122 - Skills - DEBUG - {"type": "browser_elements_reset_result", "data": {"elements": {}}, "context": null}
        2017-06-16 20:16:01,415 - Mycroft-Browser - INFO - Browser reset elements: True
        2017-06-16 20:16:01,417 - Skills - DEBUG - {"type": "browser_url_request", "data": {"url": "www.cleverbot.com"}, "context": null}
        2017-06-16 20:16:01,419 - selenium.webdriver.remote.remote_connection - DEBUG - POST http://127.0.0.1:58852/session/a36877c6-06b3-4ab7-8612-ea0753f99967/url {"url": "http://www.cleverbot.com", "sessionId": "a36877c6-06b3-4ab7-8612-ea0753f99967"}
        2017-06-16 20:16:09,034 - selenium.webdriver.remote.remote_connection - DEBUG - Finished Request
        2017-06-16 20:16:09,035 - selenium.webdriver.remote.remote_connection - DEBUG - GET http://127.0.0.1:58852/session/a36877c6-06b3-4ab7-8612-ea0753f99967/url {"sessionId": "a36877c6-06b3-4ab7-8612-ea0753f99967"}
        2017-06-16 20:16:09,065 - selenium.webdriver.remote.remote_connection - DEBUG - Finished Request
        2017-06-16 20:16:09,065 - BrowserSkill - INFO - url: http://www.cleverbot.com/
        2017-06-16 20:16:09,066 - selenium.webdriver.remote.remote_connection - DEBUG - GET http://127.0.0.1:58852/session/a36877c6-06b3-4ab7-8612-ea0753f99967/title {"sessionId": "a36877c6-06b3-4ab7-8612-ea0753f99967"}
        2017-06-16 20:16:09,086 - selenium.webdriver.remote.remote_connection - DEBUG - Finished Request
        2017-06-16 20:16:09,086 - BrowserSkill - INFO - title: Cleverbot.com - a clever bot - speak to an AI with some Actual Intelligence?
        2017-06-16 20:16:09,087 - selenium.webdriver.remote.remote_connection - DEBUG - GET http://127.0.0.1:58852/session/a36877c6-06b3-4ab7-8612-ea0753f99967/url {"sessionId": "a36877c6-06b3-4ab7-8612-ea0753f99967"}
        2017-06-16 20:16:09,106 - selenium.webdriver.remote.remote_connection - DEBUG - Finished Request
        2017-06-16 20:16:09,106 - selenium.webdriver.remote.remote_connection - DEBUG - GET http://127.0.0.1:58852/session/a36877c6-06b3-4ab7-8612-ea0753f99967/title {"sessionId": "a36877c6-06b3-4ab7-8612-ea0753f99967"}
        2017-06-16 20:16:09,122 - selenium.webdriver.remote.remote_connection - DEBUG - Finished Request
        2017-06-16 20:16:09,124 - Skills - DEBUG - {"type": "browser_url_opened", "data": {"page_title": "Cleverbot.com - a clever bot - speak to an AI with some Actual Intelligence?", "result": "http://www.cleverbot.com/", "requested_url": "http://www.cleverbot.com"}, "context": null}
        2017-06-16 20:16:09,227 - Mycroft-Browser - INFO - Browser url open: True
        2017-06-16 20:16:09,229 - Skills - DEBUG - {"type": "browser_get_element", "data": {"type": "name", "data": "stimulus", "element_name": "input"}, "context": null}
        2017-06-16 20:16:09,231 - selenium.webdriver.remote.remote_connection - DEBUG - POST http://127.0.0.1:58852/session/a36877c6-06b3-4ab7-8612-ea0753f99967/element {"using": "css selector", "sessionId": "a36877c6-06b3-4ab7-8612-ea0753f99967", "value": "[name=\"stimulus\"]"}
        2017-06-16 20:16:09,306 - selenium.webdriver.remote.remote_connection - DEBUG - Finished Request
        2017-06-16 20:16:09,310 - Skills - DEBUG - {"type": "browser_element_stored", "data": {"sucess": true, "data": "stimulus", "name": "input", "type": "name"}, "context": null}
        2017-06-16 20:16:09,528 - Mycroft-Browser - INFO - Browser get element: True
        2017-06-16 20:16:09,531 - Skills - DEBUG - {"type": "browser_send_keys_to_element", "data": {"text": "what is purpose of", "special_key": false, "element_name": "input"}, "context": null}
        2017-06-16 20:16:09,532 - selenium.webdriver.remote.remote_connection - DEBUG - POST http://127.0.0.1:58852/session/a36877c6-06b3-4ab7-8612-ea0753f99967/element/98a2bd5a-5706-428f-90be-3247de79779d/value {"text": "what is purpose of", "sessionId": "a36877c6-06b3-4ab7-8612-ea0753f99967", "id": "98a2bd5a-5706-428f-90be-3247de79779d", "value": ["w", "h", "a", "t", " ", "i", "s", " ", "p", "u", "r", "p", "o", "s", "e", " ", "o", "f"]}
        2017-06-16 20:16:09,948 - selenium.webdriver.remote.remote_connection - DEBUG - Finished Request
        2017-06-16 20:16:10,950 - Skills - DEBUG - {"type": "browser_sent_keys", "data": {"sucess": true, "data": "what is purpose of", "name": "input"}, "context": null}
        2017-06-16 20:16:11,030 - Mycroft-Browser - INFO - Browser send keys element: True
        2017-06-16 20:16:11,034 - Skills - DEBUG - {"type": "browser_send_keys_to_element", "data": {"text": "RETURN", "special_key": true, "element_name": "input"}, "context": null}
        2017-06-16 20:16:11,035 - selenium.webdriver.remote.remote_connection - DEBUG - POST http://127.0.0.1:58852/session/a36877c6-06b3-4ab7-8612-ea0753f99967/element/98a2bd5a-5706-428f-90be-3247de79779d/value {"text": "\ue006", "sessionId": "a36877c6-06b3-4ab7-8612-ea0753f99967", "id": "98a2bd5a-5706-428f-90be-3247de79779d", "value": ["\ue006"]}
        2017-06-16 20:16:11,179 - selenium.webdriver.remote.remote_connection - DEBUG - Finished Request
        2017-06-16 20:16:11,186 - Skills - DEBUG - {"type": "browser_sent_keys", "data": {"sucess": true, "data": "RETURN", "name": "input"}, "context": null}
        2017-06-16 20:16:11,332 - Mycroft-Browser - INFO - Browser send keys element: True
        2017-06-16 20:16:11,334 - Skills - DEBUG - {"type": "browser_get_element", "data": {"type": "xpath", "data": ".//*[@id='snipTextIcon']", "element_name": "sucess"}, "context": null}
        2017-06-16 20:16:11,336 - selenium.webdriver.remote.remote_connection - DEBUG - POST http://127.0.0.1:58852/session/a36877c6-06b3-4ab7-8612-ea0753f99967/element {"using": "xpath", "sessionId": "a36877c6-06b3-4ab7-8612-ea0753f99967", "value": ".//*[@id='snipTextIcon']"}
        2017-06-16 20:16:11,410 - selenium.webdriver.remote.remote_connection - DEBUG - Finished Request
        2017-06-16 20:16:11,418 - Skills - DEBUG - {"type": "browser_element_stored", "data": {"sucess": false, "data": ".//*[@id='snipTextIcon']", "name": "sucess", "type": "xpath"}, "context": null}
        2017-06-16 20:16:11,633 - Mycroft-Browser - INFO - Browser get element: True
        2017-06-16 20:16:11,638 - Skills - DEBUG - {"type": "browser_get_element", "data": {"type": "xpath", "data": ".//*[@id='snipTextIcon']", "element_name": "sucess"}, "context": null}
        2017-06-16 20:16:11,639 - selenium.webdriver.remote.remote_connection - DEBUG - POST http://127.0.0.1:58852/session/a36877c6-06b3-4ab7-8612-ea0753f99967/element {"using": "xpath", "sessionId": "a36877c6-06b3-4ab7-8612-ea0753f99967", "value": ".//*[@id='snipTextIcon']"}
        2017-06-16 20:16:11,658 - selenium.webdriver.remote.remote_connection - DEBUG - Finished Request
        2017-06-16 20:16:11,664 - Skills - DEBUG - {"type": "browser_element_stored", "data": {"sucess": false, "data": ".//*[@id='snipTextIcon']", "name": "sucess", "type": "xpath"}, "context": null}
        2017-06-16 20:16:11,934 - Mycroft-Browser - INFO - Browser get element: True
        2017-06-16 20:16:11,936 - Skills - DEBUG - {"type": "browser_get_element", "data": {"type": "xpath", "data": ".//*[@id='snipTextIcon']", "element_name": "sucess"}, "context": null}
        2017-06-16 20:16:11,945 - selenium.webdriver.remote.remote_connection - DEBUG - POST http://127.0.0.1:58852/session/a36877c6-06b3-4ab7-8612-ea0753f99967/element {"using": "xpath", "sessionId": "a36877c6-06b3-4ab7-8612-ea0753f99967", "value": ".//*[@id='snipTextIcon']"}
        2017-06-16 20:16:12,097 - selenium.webdriver.remote.remote_connection - DEBUG - Finished Request
        2017-06-16 20:16:12,102 - Skills - DEBUG - {"type": "browser_element_stored", "data": {"sucess": false, "data": ".//*[@id='snipTextIcon']", "name": "sucess", "type": "xpath"}, "context": null}
        2017-06-16 20:16:12,235 - Mycroft-Browser - INFO - Browser get element: True
        2017-06-16 20:16:12,237 - Skills - DEBUG - {"type": "browser_get_element", "data": {"type": "xpath", "data": ".//*[@id='snipTextIcon']", "element_name": "sucess"}, "context": null}
        2017-06-16 20:16:12,240 - selenium.webdriver.remote.remote_connection - DEBUG - POST http://127.0.0.1:58852/session/a36877c6-06b3-4ab7-8612-ea0753f99967/element {"using": "xpath", "sessionId": "a36877c6-06b3-4ab7-8612-ea0753f99967", "value": ".//*[@id='snipTextIcon']"}
        2017-06-16 20:16:12,268 - selenium.webdriver.remote.remote_connection - DEBUG - Finished Request
        2017-06-16 20:16:12,274 - Skills - DEBUG - {"type": "browser_element_stored", "data": {"sucess": false, "data": ".//*[@id='snipTextIcon']", "name": "sucess", "type": "xpath"}, "context": null}
        2017-06-16 20:16:12,536 - Mycroft-Browser - INFO - Browser get element: True
        2017-06-16 20:16:12,538 - Skills - DEBUG - {"type": "browser_get_element", "data": {"type": "xpath", "data": ".//*[@id='snipTextIcon']", "element_name": "sucess"}, "context": null}
        2017-06-16 20:16:12,540 - selenium.webdriver.remote.remote_connection - DEBUG - POST http://127.0.0.1:58852/session/a36877c6-06b3-4ab7-8612-ea0753f99967/element {"using": "xpath", "sessionId": "a36877c6-06b3-4ab7-8612-ea0753f99967", "value": ".//*[@id='snipTextIcon']"}
        2017-06-16 20:16:12,562 - selenium.webdriver.remote.remote_connection - DEBUG - Finished Request
        2017-06-16 20:16:12,565 - Skills - DEBUG - {"type": "browser_element_stored", "data": {"sucess": false, "data": ".//*[@id='snipTextIcon']", "name": "sucess", "type": "xpath"}, "context": null}
        2017-06-16 20:16:12,837 - Mycroft-Browser - INFO - Browser get element: True
        2017-06-16 20:16:12,840 - Skills - DEBUG - {"type": "browser_get_element", "data": {"type": "xpath", "data": ".//*[@id='line1']/span[1]", "element_name": "response"}, "context": null}
        2017-06-16 20:16:12,840 - selenium.webdriver.remote.remote_connection - DEBUG - POST http://127.0.0.1:58852/session/a36877c6-06b3-4ab7-8612-ea0753f99967/element {"using": "xpath", "sessionId": "a36877c6-06b3-4ab7-8612-ea0753f99967", "value": ".//*[@id='line1']/span[1]"}
        2017-06-16 20:16:12,862 - selenium.webdriver.remote.remote_connection - DEBUG - Finished Request
        2017-06-16 20:16:12,868 - Skills - DEBUG - {"type": "browser_element_stored", "data": {"sucess": true, "data": ".//*[@id='line1']/span[1]", "name": "response", "type": "xpath"}, "context": null}
        2017-06-16 20:16:13,138 - Mycroft-Browser - INFO - Browser get element: True
        2017-06-16 20:16:13,141 - Skills - DEBUG - {"type": "browser_get_element_text", "data": {"element_name": "response"}, "context": null}
        2017-06-16 20:16:13,143 - selenium.webdriver.remote.remote_connection - DEBUG - GET http://127.0.0.1:58852/session/a36877c6-06b3-4ab7-8612-ea0753f99967/element/3620c627-1693-4233-b7af-e55e335e7780/text {"sessionId": "a36877c6-06b3-4ab7-8612-ea0753f99967", "id": "3620c627-1693-4233-b7af-e55e335e7780"}
        2017-06-16 20:16:13,199 - selenium.webdriver.remote.remote_connection - DEBUG - Finished Request
        2017-06-16 20:16:13,203 - Skills - DEBUG - {"type": "browser_element_text", "data": {"text": "The reason you do some", "name": "response"}, "context": null}
        2017-06-16 20:16:13,439 - Mycroft-Browser - INFO - Browser get element text: True
        2017-06-16 20:16:13,442 - Skills - DEBUG - {"type": "speak", "data": {"target": "cli", "mute": false, "expect_response": false, "more": false, "utterance": "The reason you do some", "metadata": {"source_skill": "BrowserSkill"}}, "context": null}
        2017-06-16 20:16:13,442 - Skills - DEBUG - {"type": "browser_reset_elements", "data": {}, "context": null}
        2017-06-16 20:16:13,449 - Skills - DEBUG - {"type": "browser_elements_reset_result", "data": {"elements": {}}, "context": null}
        2017-06-16 20:16:13,741 - Mycroft-Browser - INFO - Browser reset elements: True

