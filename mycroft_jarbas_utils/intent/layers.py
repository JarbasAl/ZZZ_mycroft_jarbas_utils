from mycroft.messagebus.message import Message
from mycroft.util.log import LOG
from time import sleep
from mycroft.version import CORE_VERSION_BUILD, CORE_VERSION_MAJOR, \
    CORE_VERSION_MINOR, CORE_VERSION_STR


class IntentLayers(object):
    def __init__(self, emitter, layers=None, override=False):
        layers = layers or []
        self.emitter = emitter
        # make intent levels for N layers
        self.layers = layers
        self.current_layer = 0
        self.activate_layer(0)
        self.named_layers = {}
        if CORE_VERSION_BUILD < 3 and CORE_VERSION_MAJOR < 18 and \
                CORE_VERSION_MINOR < 2 and not override:
            raise NotImplementedError("PR#860 not in " + CORE_VERSION_STR)
            # you can do this in main skill and pass override=True

            # def initialize(self):
            #    self.layers = IntentLayers(self.emitter)
            #
                # TODO remove once PR#860 is merged
            #    try:
            #        self.handle_enable_intent(
            #            Message("", {"intent_name": "dummy"}))
            #    except:
            #        self.layers.disable_intent = self.disable_intent
            #        self.layers.enable_intent = self.enable_intent

            # def enable_intent(self, intent_name):
            #    """Reenable a registered intent"""
            #    if ":" in intent_name:
            #        intent_name = intent_name.split(":")[0]
            #    for (name, intent) in self.registered_intents:
            #        if name == intent_name:
            #            self.registered_intents.remove((name, intent))
            #            intent.name = name
            #            self.register_intent(intent, None)
            #            LOG.debug('Enabling intent ' + intent_name)
            #            return True
            #    LOG.error('Could not enable ' + intent_name +
            #              ', it hasn\'t been registered.')
            #    return False

    def disable_intent(self, intent_name):
        """Disable a registered intent"""
        self.emitter.emit(Message("disable_intent", {"intent_name": intent_name}))

    def enable_intent(self, intent_name):
        """Reenable a registered self intent"""
        self.emitter.emit(Message("enable_intent", {"intent_name": intent_name}))

    def reset(self):
        LOG.info("Reseting Intent Layers")
        self.activate_layer(0)

    def next(self):
        LOG.info("Going to next Intent Layer")
        self.current_layer += 1
        if self.current_layer > len(self.layers):
            LOG.info("Already in last layer, going to layer 0")
            self.current_layer = 0
        self.activate_layer(self.current_layer)

    def previous(self):
        LOG.info("Going to previous Intent Layer")
        self.current_layer -= 1
        if self.current_layer < 0:
            self.current_layer = len(self.layers)
            LOG.info("Already in layer 0, going to last layer")
        self.activate_layer(self.current_layer)

    def add_layer(self, intent_list=None):
        intent_list = intent_list or []
        self.layers.append(intent_list)
        LOG.info("Adding intent layer: " + str(intent_list))

    def add_named_layer(self, name, intent_list=None):
        intent_list = intent_list or []
        self.named_layers[name] = len(self.layers)
        self.layers.append(intent_list)
        LOG.info("Setting layer " + name + " to: " + str(intent_list))

    def activate_named_layer(self, name):
        if name in self.named_layers:
            i = self.named_layers[name]
            LOG.info("activating layer named: " + name)
            self.activate_layer(i)
        else:
            LOG.error("no layer named: " + name)

    def deactivate_named_layer(self, name):
        if name in self.named_layers:
            i = self.named_layers[name]
            LOG.info("deactivating layer named: " + name)
            self.deactivate_layer(i)
        else:
            LOG.error("no layer named: " + name)

    def remove_named_layer(self, name):
        if name in self.named_layers:
            i = self.named_layers[name]
            LOG.info("removing layer named: " + name)
            self.remove_layer(i)
        else:
            LOG.error("no layer named: " + name)

    def replace_named_layer(self, name, intent_list=None):
        if name in self.named_layers:
            i = self.named_layers[name]
            LOG.info("deactivating layer named: " + name)
            self.replace_layer(i, intent_list)
        else:
            LOG.error("no layer named: " + name)

    def replace_layer(self, layer_num, intent_list=None):
        intent_list = intent_list or []
        self.layers[layer_num] = intent_list
        LOG.info("Adding layer" + str(intent_list) + " in position " + str(layer_num))

    def remove_layer(self, layer_num):
        if layer_num >= len(self.layers):
            return False
        self.layers.pop(layer_num)
        LOG.info("Removing layer number " + str(layer_num))
        return True

    def find_layer(self, intent_name):
        layer_list = []
        for i in range(0, len(self.layers)):
            if intent_name in self.layers[i]:
                layer_list.append(i)
        return layer_list

    def disable(self):
        LOG.info("Disabling layers")
        # disable all layers
        for i in range(0, len(self.layers)):
            self.deactivate_layer(i)

    def activate_layer(self, layer_num):
        # error check
        if layer_num < 0 or layer_num > len(self.layers):
            LOG.error("invalid layer number")
            return False

        self.current_layer = layer_num

        # disable other layers
        self.disable()

        # TODO in here we should wait for all intents to be detached
        # sometimes detach intent from this step comes after register from next
        sleep(0.3)

        # enable layer
        LOG.info("Activating Layer " + str(layer_num))
        if layer_num < len(self.layers) and len(self.layers):
            for intent_name in self.layers[layer_num]:
                self.enable_intent(intent_name)
            return True
        return False

    def deactivate_layer(self, layer_num):
        # error check
        if layer_num < 0 or layer_num > len(self.layers):
            LOG.error("invalid layer number")
            return False
        LOG.info("Deactivating Layer " + str(layer_num))
        for intent_name in self.layers[layer_num]:
            self.disable_intent(intent_name)
        return True
