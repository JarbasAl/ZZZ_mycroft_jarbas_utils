# MycroftAudioSkill

This MycroftSkill base class manages a few aspects about audio

* automatically initialize a AudioService instance as self.audio
* create settingsmeta.json automatically with a "default_backend" field if it does not exist
* create an adapt keyword for all active backends in config file
* select backend automatically if adaptkeyword is present
* remove backend references from any number of fields in message.data
* detect backend keyword even if adapt missed it
* if no backend is specified use default_backend
* skills may request a prefered order, the first available will be used
* create a AudioBackend.entity with all backends for padatious intents to use

# use-case example

to use this base class import it and use it instead of MycroftSkill

    from mycroft_jarbas_utils.skills.audio import AudioSkill

    class YoutubeSkill(AudioSkill):
        def __init__(self):
            super(YoutubeSkill, self).__init__()

in my [youtube skill](https://github.com/JarbasAl/skill-youtube-play) i have an adapt intent, this triggers whenever i say
"play X in youtube", or "youtube play X in vlc"

    @intent_handler(IntentBuilder("YoutubePlay").require(
        "youtube").require("play"))
    def handle_play_song_intent(self, message):
        # use adapt if youtube is included in the utterance
        # use the utterance remainder as query
        title = message.utterance_remainder()
        self.youtube_play(title)

adapt registered all backends, the skill added it to the intent
automatically as an optional keyword, the utterance_remainder will not search
garbage!

there is another more generic padatious intent, this one triggers with "play
X", a AudioBackend.entity was generated and registered for use in .intent
files, but it is not needed in this case

    @intent_file_handler("youtube.intent")
    def handle_play_song_padatious_intent(self, message):
        # handle a more generic play command and extract name with padatious
        title = message.data.get("music")
        self.youtube_play(title)


to avoid searching youtube for "X in vlc" you can use the add_filter method

    def __init__(self):
        super(YoutubeSkill, self).__init__()
        self.add_filter("music")

this changed the message.data "music" field to remove backend references, this way we still have a clean search term

since we are using padatious, adapt did not catch the AudioBackend keyword, but it is also automatically available in the message.data

you should not initialize the audio service yourself, it was done already, use self.audio when needed

    def youtube_play(self, title):
        # Play the song requested
        if self.audio.is_playing:
            self.audio.stop()
        self.speak_dialog("searching.youtube", {"music": title})
        wait_while_speaking()
        videos = self.youtube_search(title)

        # deactivate mouth animation
        self.enclosure.deactivate_mouth_events()
        # music code
        self.enclosure.mouth_display("IIAEAOOHGAGEGOOHAA", x=10, y=0,
                                         refresh=True)

        self.audio.play(videos)

no need to create a settingsmeta.json, it is automatically generated and default backend can be selected in home.mycroft.ai


# audio service

if you need to use the audioservice outside a skill you can do

    from mycroft_jarbas_utils.skills.audio import AudioService_B as AudioService

    audio = AudioService(emitter)

    # will use config file default
    audio.play(["my_track.mp3"])
    sleep(5)
    audio.stop()

    # use vlc if no backend is asked instead of the config default
    audio.set_prefered("vlc")

    # will use vlc
    audio.play(["my_track.mp3"])
    sleep(5)
    audio.stop()

    # will use mpv
    audio.play(["my_track.mp3"], "mpv")
    sleep(5)

    # in all "backend.change" messages the backend will be set if "AudioBackend" field is available
    audio.register_backend_update("backend.change")

    # clean shutdown
    audio.shutdown()

