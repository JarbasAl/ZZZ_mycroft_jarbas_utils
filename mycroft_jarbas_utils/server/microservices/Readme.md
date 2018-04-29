# JarbasAPI

the microservices should be started before the skills process

# Processing an utterance

    from mycroft.microservices.api import MycroftAPI

    ap = MycroftAPI("api_key")
    json_response = ap.ask_mycroft("hello world")

# Admin functions

some functions require an admin api key

    ap = MycroftAPI("admin_key")

    # get an api key string
    api = ap.get_api()

    # add a new user
    mail = "fakemail@jarbasai.com"
    name = "anon"
    print ap.new_user(api, mail, name)

    # revoke an api
    print ap.revoke_api(api)

# Determining Intents

    from mycroft.microservices.api import MycroftAPI

    ap = MycroftAPI("api_key")

    # what intent will this utterance trigger
    intent = ap.get_intent("hello world")

    # what intents are registered {"skill_id": ["intent", "list"] }
    intent_dict = ap.get_intent_map()

# Determining Vocab

    from mycroft.microservices.api import MycroftAPI

    ap = MycroftAPI("api_key")

    # what vocab is registered {"word": "MatchingKeyword" }
    intent_dict = ap.get_vocab_map()
