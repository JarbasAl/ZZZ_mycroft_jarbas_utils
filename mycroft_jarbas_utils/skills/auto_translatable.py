from mycroft.skills.core import MycroftSkill, FallbackSkill, Message, \
    dig_for_message, get_handler_name, LOG
from mtranslate import translate
import unicodedata
from langdetect import detect as language_detect


class AutotranslatableSkill(MycroftSkill):
    ''' Skill that auto translates speak messages '''

    def __init__(self, name=None, emitter=None):
        MycroftSkill.__init__(self, name, emitter)
        self.input_lang = None
        self.translate_keys = []

    def language_detect(self, utterance):
        utterance = unicodedata.normalize('NFKD', unicode(utterance)).encode(
            'ascii',
            'ignore')
        return language_detect(utterance)

    def translate(self, text, lang=None):
        lang = lang or self.lang
        sentence = translate(unicode(text), lang)
        translated = unicodedata.normalize('NFKD', unicode(sentence)).encode(
            'ascii',
            'ignore')
        self.log.info("translated " + text + " to " + translated)
        return translated

    def translate_utterance(self, ut="", lang=None, context=None):
        lang = lang or self.input_lang
        ut_lang = self.lang
        if ut and lang is not None:
            ut_lang = self.language_detect(ut)
            if "-" in ut_lang:
                ut_lang = ut_lang.split("-")[0]
            if "-" in lang:
                lang = lang.split("-")[0]
            if lang != ut_lang:
                ut = self.translate(ut, lang)

        if context is not None:
            message_context = context
            if ut_lang != lang:
                message_context["auto_translated"] = True
            else:
                message_context["auto_translated"] = False
            message_context["source_lang"] = ut_lang
            message_context["target_lang"] = lang
            return ut, message_context
        return ut

    def translate_message(self, message):
        # auto_Translate input
        ut = message.data.get("utterance")
        if ut:
            message.data["original_utterance"] = ut
            message.data["utterance"] = self.translate_utterance(ut)
        for key in self.translate_keys:
            if key in message.data:
                ut = message.data[key]
                message.data[key] = self.translate_utterance(ut)
        return message

    def register_intent(self, intent_parser, handler):
        # the dummy is needed because mycroft expects the handler to have a
        #  self, arg count will be wrong without the dummy and things will
        # break
        def universal_intent_handler(message, dummy=None):
            message = self.translate_message(message)
            LOG.info(get_handler_name(handler))
            handler(message)

        super(AutotranslatableSkill, self) \
            .register_intent(intent_parser, universal_intent_handler)

    def register_intent_file(self, intent_file, handler):
        # the dummy is needed because mycroft expects the handler to have a
        #  self, arg count will be wrong without the dummy and things will
        # break
        def universal_intent_handler(message, dummy=None):
            message = self.translate_message(message)
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
        # translate utterance for skills that generate speech at runtime
        utterance, message_context = self.translate_utterance(utterance,
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
        FallbackSkill.__init__(self, name, emitter)
        self.input_lang = None
        self.translate_keys = []

        def handler(message):
            return False

        self._handler = handler
        self._handler_name = ""

    def _universal_fallback_handler(self, message):
        # auto_Translate input
        message = self.translate_message(message)
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
