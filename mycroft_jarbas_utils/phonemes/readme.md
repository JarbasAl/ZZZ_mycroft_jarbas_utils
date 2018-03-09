# phonemes utils

util to get phonemes from any string, useful for example for a skill that changes wake word

checks cmu dict from nltk for phonemes, if not available guesses them

    jarbas - JH AE R B AE S
    alexa - AH0 L EH1 K S AH0
    hey mycroft - H H E Y 1 . M Y K R O W F T
    raspi - R AE S P IH


# usage

    from mycroft_jarbas_utils.phonemes import guess_phonemes

    phonemes = guess_phonemes("jarbas")

