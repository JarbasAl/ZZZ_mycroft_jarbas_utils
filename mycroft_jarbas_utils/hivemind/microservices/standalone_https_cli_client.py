from mycroft_jarbas_utils.hivemind.microservices.api import MycroftMicroServicesAPI


def https_client_run(key="test_key", url="https://0.0.0.0:6712/"):
    ap = MycroftMicroServicesAPI(key, url=url)
    while True:
        line = raw_input("Input: ")
        res = ap.ask_mycroft(line.lower())
        print "Jarbas: ", res.get("data", {}).get("utterance", "")


if __name__ == "__main__":
    https_client_run()
