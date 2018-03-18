# contents

- auto translatable skills -> try to work in any language
- active skills -> converse is ALWAYS called
- audio skill -> automatically selects backend for audio service, registers AudioBackend adapt keyword, cleans utterance remainder to be used as query, allow to set prefered backend in skill

# Auto Translatable skills

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

[duckduck go](https://github.com/JarbasAl/universal-fallback-duckduckgo), [wolframalpha](https://github.com/JarbasAl/universal-fallback-wolfram-alpha) and [aiml](https://github.com/JarbasAl/universal-fallback-aiml) fallback, need english input
and always generate english answers, translates input and output to configured language

[wiki](https://github.com/JarbasAl/skill-wiki-universal) skill, uses english wikipedia, translates input, search term keys and
 output to configured language

[jokes skill](https://github.com/JarbasAl/skill-joke-universal), always generates english answers , translates output to
configured language


# Active skills

These skills remain in the active skill list, on 5 minute timeout they are
reactivated automatically

Depends on [PR#1468](https://github.com/MycroftAI/mycroft-core/pull/1468/files) to allow a skill to know when it was kicked from the
active list

This will allow you to do things like passive skills that are always active, for example always mutating an utterance

    def converse(self, utterances, lang="en-us"):
        if utterances[0] != self.last_mutation:
            self.last_mutation = self.mutate(utterances[0])
            self.emitter.emit(Message("recognizer_loop:utterance", {"utterances": [self.last_mutation])
            return True
        return False

Other examples would be monitoring utterances and setting contexts, or displaying them in a web UI, or training a chatbot…

# usage

    from mycroft_jarbas_utils.skills.active import ActiveSkill

    class MySkill(ActiveSkill):
        def __init__(self):
            super(ActiveSkill, self).__init__()
        # do everything else as usual, this skill is always in active list
