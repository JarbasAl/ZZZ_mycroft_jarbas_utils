[blog post](https://jarbasai.github.io//posts/2017/11/auto_translatable_skills/)

# usage

    from mycroft_jarbas_utils.skills.auto_translatable import AutotranslatableFallback


    class MyFallback(AutotranslatableFallback):
        def __init__(self):
            super(MyFallback, self).__init__()
            self.input_lang = "en-us"