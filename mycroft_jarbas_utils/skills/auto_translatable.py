from builtins import str
from mycroft.skills.core import MycroftSkill, FallbackSkill, Message, \
    dig_for_message, get_handler_name, LOG
from mtranslate import translate
import unicodedata
from langdetect import detect as language_detect
from langdetect.lang_detect_exception import LangDetectException


class AutotranslatableSkill(MycroftSkill):
    ''' Skill that auto translates speak messages '''

    def __init__(self, name=None, emitter=None):
        super(AutotranslatableSkill, self).__init__(name, emitter)
        self.input_lang = None
        self.translate_keys = []

    def language_detect(self, utterance):
        try:
            return language_detect(utterance)
        except LangDetectException:
            return self.lang

    def translate(self, text, lang=None):
        lang = lang or self.lang
        translated = translate(str(text), lang)
        LOG.info("translated " + text + " to " + translated)
        return translated

    def _translate_utterance(self, utterance="", lang=None, context=None):
        lang = lang or self.input_lang
        ut_lang = self.lang
        original = utterance
        if utterance and lang is not None:
            ut_lang = self.language_detect(utterance)
            if "-" in ut_lang:
                ut_lang = ut_lang.split("-")[0]
            if "-" in lang:
                lang = lang.split("-")[0]
            if lang != ut_lang:
                utterance = self.translate(utterance, lang)

        if context is not None:
            message_context = context
            if ut_lang != lang:
                message_context["auto_translated"] = True
                message_context["original_utterance"] = original
            else:
                message_context["auto_translated"] = False
            message_context["source_lang"] = ut_lang
            message_context["target_lang"] = lang
            return utterance, message_context
        return utterance

    def _translate_message(self, message, lang=None):
        # auto_Translate input
        ut = message.data.get("utterance")
        if ut:
            message.data["utterance"] = self._translate_utterance(ut, lang)
        for key in self.translate_keys:
            if key in message.data:
                ut = message.data[key]
                if not isinstance(ut, str):
                    continue
                message.data[key] = self._translate_utterance(ut, lang)
        return message

    def register_intent(self, intent_parser, handler):
        # the dummy is needed because mycroft expects the handler to have a
        #  self, arg count will be wrong without the dummy and things will
        # break
        def universal_intent_handler(message, dummy=None):
            message = self._translate_message(message)
            LOG.info(get_handler_name(handler))
            handler(message)

        super(AutotranslatableSkill, self) \
            .register_intent(intent_parser, universal_intent_handler)

    def register_intent_file(self, intent_file, handler):
        # the dummy is needed because mycroft expects the handler to have a
        #  self, arg count will be wrong without the dummy and things will
        # break
        def universal_intent_handler(message, dummy=None):
            message = self._translate_message(message)
            LOG.info(get_handler_name(handler))
            handler(message)

        super(AutotranslatableSkill, self) \
            .register_intent_file(intent_file, universal_intent_handler)

    def speak(self, utterance, expect_response=False, metadata=None):
        """
            Speak a sentence.

                   Args:
                       utterance:          sentence mycroft should speak
                       expect_response:    set to True if Mycroft should expect
                                           a response from the user and start
                                           listening for response.
                       metadata:           Extra data to be transmitted
                                           together with speech
               """
        metadata = metadata or {}
        # translate utterance for skills that generate speech at runtime
        utterance, message_context = self._translate_utterance(utterance,
                                                               self.lang, {})

        # registers the skill as being active
        self.enclosure.register(self.name)
        data = {'utterance': utterance,
                'expect_response': expect_response,
                "metadata": metadata}
        message = dig_for_message()
        if message:
            self.emitter.emit(message.reply("speak", data, message_context))
        else:
            self.emitter.emit(Message("speak", data, message_context))


class AutotranslatableFallback(AutotranslatableSkill, FallbackSkill):
    ''' Fallback that auto translates speak messages and auto translates
    input utterances '''

    def __init__(self, name=None, emitter=None):
        super(AutotranslatableFallback, self).__init__(name, emitter)
        self.input_lang = None
        self.translate_keys = []

        def handler(message):
            return False

        self._handler = handler
        self._handler_name = ""

    def _universal_fallback_handler(self, message):
        # auto_Translate input
        message = self._translate_message(message)
        LOG.info(self._handler_name)
        success = self._handler(message)
        if success:
            self.make_active()
        return success

    def register_fallback(self, handler, priority):
        """
            register a fallback with the list of fallback handlers
            and with the list of handlers registered by this instance

            modify fallback handler for input auto-translation
        """

        self._handler = handler
        self._handler_name = get_handler_name(handler)

        if self.input_lang:
            self.instance_fallback_handlers.append(
                self._universal_fallback_handler)
            self._register_fallback(self._universal_fallback_handler,
                                    priority)
        else:
            self.instance_fallback_handlers.append(handler)
            self._register_fallback(handler, priority)

