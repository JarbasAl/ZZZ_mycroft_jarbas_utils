## SSML Builder


        s = SSMLBuilder()
        s.speak("Prosody can be used to change the way words sound. The following words are")
        s.speak_loud("quite a bit louder than the rest of this passage.")
        s.speak("Each morning when I wake up,")
        s.speak_slow("I speak quite slowly and deliberately until I have my coffee.")
        s.speak("I can also change the pitch of my voice using prosody. Do you like")
        s.speak_high_pitch("speech with a pitch that is higher,")
        s.speak("or")
        s.speak_low_pitch("is a lower pitch preferable?")
        
        sentence_ssml = s.build()
        sentence_no_ssml = s.remove_ssml(sentence_ssml)
        
        print sentence_no_ssml
        print sentence_ssml
        
        """
         Prosody can be used to change the way words sound. The following words are quite a bit louder than the rest of this passage. Each morning when I wake up, I speak quite slowly and deliberately until I have my coffee. I can also change the pitch of my voice using prosody. Do you like speech with a pitch that is higher, or is a lower pitch preferable?
        
        <ssml><speak> Prosody can be used to change the way words sound. The following words are <prosody volume='1.6'>quite a bit louder than the rest of this passage.</prosody> Each morning when I wake up, <prosody rate='0.4'>I speak quite slowly and deliberately until I have my coffee.</prosody> I can also change the pitch of my voice using prosody. Do you like <prosody pitch='+10%'>speech with a pitch that is higher,</prosody> or <prosody pitch='-10%'>is a lower pitch preferable?</prosody></speak></ssml>
        
        """