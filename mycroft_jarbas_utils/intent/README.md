# mycroft_jarbas_utils.intents

# Intent Layers

Intent Layers is an helper class to activate and deactivate intents, giving state to a mycroft skill

Each layer has different intents available to be executed, this allows for much easier sequential event programming

Depending on the use case it may be better to use Adapt context since it allows something similar and is much simpler, both methods have their advantages and disadvantages

#Konami Code Example - layers with a single intent

    from mycroft_jarbas_utils.intents.layers import IntentLayers

    in initialize

    layers = [["KonamiUpIntent"], ["KonamiUpIntent"], ["KonamiDownIntent"], ["KonamiDownIntent"],
            ["KonamiLeftIntent"], ["KonamiRightIntent"], ["KonamiLeftIntent"], ["KonamiRightIntent"],
            ["KonamiBIntent"], ["KonamiAIntent"]]

    self.layers = IntentLayers(self.emitter, layers)

    to activate next layer/state -> self.layers.next()
    to activate previous layer/state -> self.layers.previous()
    to activate layer/state 0 -> self.layers.reset()
    to get current layer/state -> state = self.layers.current_layer

    to go directly to a layer do -> self.layers.activate_layer(layer_num)

    you can name layers for easy manipulation:

    self.add_named_layer("layer_name", layers)
    self.remove_named_layer("layer_name")
    self.replace_named_layer("layer_name", layers)
    self.activate_named_layer("layer_name")
    self.deactivate_named_layer("layer_name")

    on converse -> parse intent/utterance and manipulate layers if needed (bad sequence)

#Multiple Intent Layers

“Trees” can be made by making a IntentLayer for each intent, we can use layers as branches and do

    self.branch = IntentLayer(self.emitter, layers)
    self.branch.disable()

and to activate later when needed

    self.branch.reset()

intent parsing in converse method can manipulate correct tree branch if needed

this allows for much more complex skills with each intent triggering their own sub-intents / sub - trees

on demand manipulation of branch layers may also open several unforeseen opportunities for intent data structures

    self.branch.add_layer([intent_list])
    self.branch.remove_layer(layer_num)
    self.branch.replace_layer(self, layer_num, intent_list)
    list_of_layers_with_this_intent_on_it = self.branch.find_layer(self, intent_list)
