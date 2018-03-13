from mycroft_jarbas_utils.server.microservices.api import MycroftAPI

if __name__ == "__main__":
    # test if admin privileges are properly blocked
    ap = MycroftAPI("test_key666", url="https://165.227.224.64:6712/")
    while True:
        line = raw_input("Input: ")
        res = ap.ask_mycroft(line.lower())
        print "Jarbas: ", res.get("data", {}).get("utterance", "")