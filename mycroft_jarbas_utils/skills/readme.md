[blog post](https://jarbasai.github.io//posts/2017/11/auto_translatable_skills/)

# usage

    from mycroft_jarbas_utils.skills.auto_translatable import AutotranslatableSkill

    class UniversalSkill(AutotranslatableSkill):
        # just works and speaks everything in configured language
        ...


    from mycroft_jarbas_utils.skills.auto_translatable import AutotranslatableFallback


    class MyFallback(AutotranslatableFallback):
        # just works and speaks everything in configured language,
        # optionally translates input

        def __init__(self):
            super(MyFallback, self).__init__()
            # translate input to this language (optional)
            self.input_lang = "en-us"

        ...


