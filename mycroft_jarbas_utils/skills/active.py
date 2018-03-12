from mycroft.skills.core import MycroftSkill, FallbackSkill


class ActiveSkill(MycroftSkill):
    ''' Skill that remains in active skills list '''

    def __init__(self, name=None, emitter=None):
        MycroftSkill.__init__(self, name, emitter)
        self.make_active()

    def on_deactivate(self):
        self.make_active()


class ActiveFallback(ActiveSkill, FallbackSkill):
    ''' Fallback Skill that remains in active skills list '''

    def __init__(self, name=None, emitter=None):
        FallbackSkill.__init__(self, name, emitter)
        self.make_active()
