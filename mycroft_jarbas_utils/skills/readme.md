[blog post](https://jarbasai.github.io//posts/2017/11/auto_translatable_skills/)

# usage

    from mycroft_jarbas_utils.skills.auto_translatable import AutotranslatableSkill

    class UniversalSkill(AutotranslatableSkill):
        # just works and speaks everything in configured language,
        # optionally translates utterance (after intent parsing, before handler) !
        # optionally translates some message keys (after intent parsing, before handler) !
        def __init__(self):
            super(UniversalSkill, self).__init__()
            # translate input to this language (optional)
            self.input_lang = "en-us"
            # translate all these keys in the message object (optional)
            self.translate_keys = []
        ...

    from mycroft_jarbas_utils.skills.auto_translatable import AutotranslatableFallback


    class MyFallback(AutotranslatableFallback):
        # just works and speaks everything in configured language,
        # optionally translates input (before fallback handler)

        def __init__(self):
            super(MyFallback, self).__init__()
            # translate input to this language (optional)
            self.input_lang = "en-us"

        ...


# bugs

when using decorators you must provide an intent name

works

    @intent_handler(IntentBuilder("JokingIntent").require("Joke"))

fails

    @intent_handler(IntentBuilder("").require("Joke"))

# examples

aiml fallback, needs english input and always generates english answers, translates input and output to configured language

wiki skill, uses english wikipedia, translates input, search term keys and output to configured language

jokes skill, always generates english answers , translates output to configured language