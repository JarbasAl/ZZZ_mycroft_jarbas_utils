from mycroft.messagebus.message import Message
import time

__author__ = "jarbas"


class BrowserControl(object):
    def __init__(self, emitter, timeout=20, logger=None, autostart=False):
        self.emitter = emitter
        if logger is None:
            from mycroft.util.log import LOG as logger
        self.logger = logger
        self.timeout = timeout
        self.waiting = False
        self.result = {}
        self.waiting_for = ""
        self.emitter.on("browser_element_cleared", self.end_wait)
        self.emitter.on("browser_available_elements", self.end_wait)
        self.emitter.on("browser_elements_reset_result", self.end_wait)
        self.emitter.on("browser_sent_keys", self.end_wait)
        self.emitter.on("browser_element_stored", self.end_wait)
        self.emitter.on("browser_elements_stored", self.end_wait)
        self.emitter.on("browser_element_text", self.end_wait)
        self.emitter.on("browser_element_clicked", self.end_wait)
        self.emitter.on("browser_element_cleared", self.end_wait)
        self.emitter.on("browser_closed", self.end_wait)
        self.emitter.on("browser_restart_result", self.end_wait)
        self.emitter.on("browser_go_back_result", self.end_wait)
        self.emitter.on("browser_current_url_result", self.end_wait)
        self.emitter.on("browser_url_opened", self.end_wait)
        self.emitter.on("browser_add_cookies_response", self.end_wait)
        self.emitter.on("browser_get_cookies_response", self.end_wait)
        self.emitter.on("browser_title_response", self.end_wait)
        self.emitter.on("browser_get_atr_response", self.end_wait)
        if autostart:
            self.start_browser()

    def get_attribute(self, atr, element):
        self.waiting_for = "browser_get_atr_response"
        self.emitter.emit(Message("browser_get_atr_request", {"atr":atr, "element_name":element}))
        self.wait()
        return self.result.get("result")

    def get_cookies(self):
        self.waiting_for = "browser_get_cookies_response"
        self.emitter.emit(Message("browser_get_cookies_request", {}))
        self.wait()
        return self.result.get("cookies", [])

    def get_title(self):
        self.waiting_for = "browser_title_response"
        self.emitter.emit(Message("browser_title_request", {}))
        self.wait()
        return self.result.get("title", None)

    def add_cookies(self, cookies):
        self.waiting_for = "browser_add_cookies_response"
        self.emitter.emit(Message("browser_add_cookies_request", {"cookies":cookies}))
        self.wait()
        return self.result.get("success", False)

    def go_back(self):
        self.waiting_for = "browser_go_back_result"
        self.emitter.emit(Message("browser_go_back_request", {}))
        self.wait()
        return self.result.get("success", False)

    def get_current_url(self):
        self.waiting_for = "browser_current_url_result"
        self.emitter.emit(Message("browser_current_url_request", {}))
        self.wait()
        return self.result.get("url", None)

    def end_wait(self, message):
        if message.type == self.waiting_for:
            self.waiting = False
            self.result = message.data

    def wait(self):
        self.waiting = True
        start = time.time()
        elapsed = 0
        while self.waiting and elapsed <= self.timeout:
            elapsed = time.time() - start
            time.sleep(0.3)
        result = not self.waiting
        self.waiting = False
        return result

    def get_data(self):
        return self.result

    def start_browser(self):
        self.waiting_for = "browser_restart_result"
        self.emitter.emit(Message("browser_restart_request", {}))
        self.wait()
        return self.result.get("success", False)

    def close_browser(self):
        self.waiting_for = "browser_closed"
        self.emitter.emit(Message("browser_close_request", {}))
        return self.wait()

    def open_url(self, url):
        self.waiting_for = "browser_url_opened"
        self.emitter.emit(Message("browser_url_request", {"url":url}))
        self.wait()
        return self.result.get("result", None)

    def get_element(self, data, name="temp", type="name"):
        self.waiting_for = "browser_element_stored"
        self.emitter.emit(Message("browser_get_element", {"type":type, "data":data, "element_name":name}))
        self.wait()
        return self.result.get("success", False)

    def get_elements(self, data, name="temp", type="name"):
        self.waiting_for = "browser_elements_stored"
        self.emitter.emit(Message("browser_get_elements", {"type":type, "data":data, "element_name":name}))
        self.wait()
        return self.result.get("success", False)

    def get_element_text(self, name="temp"):
        self.waiting_for = "browser_element_text"
        self.emitter.emit(Message("browser_get_element_text", {"element_name":name}))
        self.wait()
        return self.result.get("text", None)

    def get_available_elements(self):
        self.waiting_for = "browser_available_elements"
        self.emitter.emit(Message("browser_available_elements_request", {}))
        self.wait()
        return self.result.get("elements", {})

    def reset_elements(self):
        self.waiting_for = "browser_elements_reset_result"
        self.emitter.emit(Message("browser_reset_elements", {}))
        return self.wait()

    def clear_element(self, name="temp"):
        self.waiting_for = "browser_element_cleared"
        self.emitter.emit(Message("browser_clear_element", {"element_name":name}))
        self.wait()
        return self.result.get("success", False)

    def click_element(self, name="temp"):
        self.waiting_for = "browser_element_clicked"
        self.emitter.emit(Message("browser_click_element", {"element_name":name}))
        self.wait()
        return self.result.get("success", False)

    def send_keys_to_element(self, text, name="temp", special=False):
        self.waiting_for = "browser_sent_keys"
        self.emitter.emit(Message("browser_send_keys_to_element", {"element_name": name, "special_key":special, "text":text}))
        self.wait()
        return self.result.get("success", False)

    def shutdown(self):
        self.emitter.remove("browser_element_cleared", self.end_wait)
        self.emitter.remove("browser_available_elements", self.end_wait)
        self.emitter.remove("browser_elements_reset_result", self.end_wait)
        self.emitter.remove("browser_sent_keys", self.end_wait)
        self.emitter.remove("browser_element_stored", self.end_wait)
        self.emitter.remove("browser_elements_stored", self.end_wait)
        self.emitter.remove("browser_element_text", self.end_wait)
        self.emitter.remove("browser_element_clicked", self.end_wait)
        self.emitter.remove("browser_element_cleared", self.end_wait)
        self.emitter.remove("browser_closed", self.end_wait)
        self.emitter.remove("browser_restart_result", self.end_wait)
        self.emitter.remove("browser_go_back_result", self.end_wait)
        self.emitter.remove("browser_current_url_result", self.end_wait)
        self.emitter.remove("browser_url_opened", self.end_wait)
        self.emitter.remove("browser_add_cookies_response", self.end_wait)
        self.emitter.remove("browser_get_cookies_response", self.end_wait)
        self.emitter.remove("browser_title_response", self.end_wait)
        self.emitter.remove("browser_get_atr_response", self.end_wait)

