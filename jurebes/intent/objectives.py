import random
from threading import Thread
from time import sleep, time
from mycroft.version import CORE_VERSION_BUILD
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from adapt.intent import IntentBuilder
from mycroft.util.log import LOG
from threading import Timer

client = None

logger = LOG

# TODO test and redo, no copy pasta from 5 versions ago
# TODO munged messages update
# TODO intent data PR#1351 update

# TODO change this number to version that gets PR merged
if CORE_VERSION_BUILD < 999:
    raise NotImplementedError(
        "PR#1351 not in " + str(CORE_VERSION_BUILD))


def connect():
    global client
    client.run_forever()


def weighted_random(weights_dict):
    # produce a list with weighted ocurrences of ways
    list = [k for k in weights_dict for dummy in range(weights_dict[k])]
    # choose randomly
    return random.choice(list)


class Objective(object):
    def __init__(self, name):
        self.name = name
        self.goals = {}  # goal_name : [int(way_id)]
        self.ways = {}  # str(way_id):[intent_name: {intent_data}]
        self.goal_weights = {}  # goal_name: goal_weight
        self.way_weights = {}  # intent_name : intent_weight
        self.counter = 0

    def get_current_id(self):
        return self.counter

    def add_goal(self, name):
        self.goals[name]=[]
        return name

    def add_way(self, goal_name, intent_name, data):
        self.counter += 1
        self.ways.setdefault(self.counter, [{intent_name : data}])
        if goal_name not in self.goals.keys():
            self.add_goal(goal_name)
        self.goals[goal_name].append(self.counter)
        return self.counter

    def set_goal_weight(self, goal_name, weight):
        self.goal_weights[goal_name] = weight

    def set_way_weight(self, way_id, weight):
        self.way_weights[str(way_id)] = weight

    def get_goal(self, name):
        return self.goals[name]

    def get_way(self, intent):
        possible = []
        for way in self.ways:
            if way[way.keys()[0]] == intent:
                possible.append(way)
        return possible

    def get_goal_weight(self, goal_name):
        return self.goal_weights[goal_name]

    def get_way_weight(self, way_id):
        return self.way_weights[str(way_id)]


class ObjectiveBuilder(object):
    def __init__(self, objective_name, emitter = None, default_weight=45):
        self.instance = Objective(objective_name)
        self.objective_name = objective_name
        self.objective = self.objective_name, None
        self.keyword = None
        self.timers = []
        global client
        if emitter is None:
            client = WebsocketClient()
            event_thread = Thread(target=connect)
            event_thread.setDaemon(True)
            event_thread.start()
            sleep(1)  # wait for connectr
        else:
            client = emitter
        self.default_weight = default_weight

    def add_goal(self, goal_name, goal_weight=None):
        self.instance.add_goal(goal_name)
        if goal_weight is not None:
            self.instance.set_goal_weight(goal_name, goal_weight)
        else:
            self.instance.set_goal_weight(goal_name, self.default_weight)
        return goal_name

    def add_way(self, goal_name, intent_name, intent_data=None, goal_weight=None, way_weight=None):
        # add way to ways
        if intent_data is None:
            intent_data = {}
        way_id = self.instance.add_way(goal_name, intent_name, intent_data)

        if way_weight is not None:
            self.instance.set_way_weight(str(way_id), way_weight)
        else:
            self.instance.set_way_weight(str(way_id), self.default_weight)
        if goal_weight is not None:
            self.instance.set_goal_weight(goal_name, goal_weight)
        else:
            self.instance.set_goal_weight(goal_name, self.default_weight)
        return way_id

    def require(self, keyword):
        self.keyword = keyword

    def build(self):
        self.objective = self.objective_name, self.instance
        objective_keyword = self.objective_name + "ObjectiveKeyword"
        objective_intent_name = self.objective_name + "ObjectiveIntent"

        # Register_Objective
        client.emit(Message("register_objective",
                            {"name": self.objective_name,
                             "goals": self.instance.goals,
                             "ways": self.instance.ways,
                             "goal_weights": self.instance.goal_weights,
                             "way_weights": self.instance.way_weights
                             }))
        # Register intent
        objective_intent = IntentBuilder(objective_intent_name)
        if self.keyword is None:
            # register vocab for objective intent with objective name
            client.emit(Message("register_vocab", {'start': self.objective_name, 'end': objective_keyword}))
            # Create intent for objective
            objective_intent.require(objective_keyword)
        else:
            objective_intent.require(self.keyword)
        objective_intent.build()

        # get handler
        handler = self.execute_objective
        self.reset()
        # return objective intent and handler
        return objective_intent, handler

    def add_timer(self, time):
        # make timer to trigger objective if provided
        if time > 0:
            client.emit(Message("objective.set.timer",
                                {"Objective": self.objective_name,
                                 "time": time}))

    def reset(self):
        self.instance = Objective(self.objective_name)
        self.objective = self.objective_name, None
        self.keyword = None
        self.timers = []

    # handler to execute objective
    def execute_objective(self, message):
        client.emit(Message("execute_objective", {"Objective": self.objective_name}))


class ObjectivesManager(object):
    def __init__(self, client):
        self.objectives = [] #objectives instance
        self.client = client
        self.client.on("intent_to_skill_response", self.receive_skill_id)
        self.client.on("objective.set.timer", self.set_timer)
        self.last_objective = None
        self.last_goal = None
        self.last_way = None
        self.timers = []

    def register_objective(self, objective_name, goals, ways, goal_weights,
                           way_weights):
        objective = Objective(objective_name)
        objective.ways = ways
        objective.goals = goals
        for goal in goals:
            if goal not in goal_weights.keys():
                goal_weights[goal] = 1
        objective.goal_weights = goal_weights
        for way in ways:
            if way not in way_weights.keys():
                way_weights[way] = 1
        objective.way_weights = way_weights
        self.objectives.append(objective)
        data = {"ways":ways, "goals":goals, "goal_weights":goal_weights, "way_weights":way_weights}
        self.client.emit(Message("objective_registered", {objective_name:data}))

    def intent_to_skill_id(self, intent_name):
        self.waiting = True
        self.id = 0
        self.client.emit(Message("intent_to_skill_request", {"intent_name": intent_name}))
        start_time = time()
        t = 0
        while self.waiting and t < 20:
            t = time() - start_time
        self.waiting = False
        return self.id

    def receive_skill_id(self, message):
        self.id = message.data["skill_id"]
        self.waiting = False

    def execute_objective(self, name):
        goal_name, way_id, intent_name, intent_data, goal_weight, way_weight = self.select_goal_and_way(name)
        self.last_objective = name
        self.last_goal = goal_name
        self.last_way = way_id
        logger.info("objective: " + name)
        logger.info("goal: " + goal_name)
        logger.info("way: " + intent_name)
        logger.info("way data :" + str(intent_data))
        logger.info("goal weight: " + str(goal_weight))
        logger.info("way weight: " + str(way_weight))

        # intent to skill id
        skill_id = self.intent_to_skill_id(intent_name)
        intent_name = str(skill_id) + ":" + intent_name
        self.client.emit(Message(intent_name, intent_data))

        # register objectives skill as last active skill
        # so feedback is processed in this skill
        self.client.emit(Message("objective.executed", {}))
        return intent_name

    def set_timer(self, message):
        objective = message.data["Objective"]
        time = message.data["time"]

        def handler():
            logger.info("Firing Timer for objective " + objective)
            client.emit(Message("execute_objective", {"Objective": objective}))

        timer = Timer(time, handler)
        timer.setDaemon(True)
        self.timers.append(timer)
        self.timers[-1].start()

    def select_goal_and_way(self, objective_name):
        for objective in self.objectives:
            if objective.name == objective_name:
                goal_name = weighted_random(objective.goal_weights)
                goal_weight = objective.goal_weights[goal_name]
                way_id = weighted_random(objective.way_weights)
                way_weight = objective.way_weights[way_id]
                intent_name = objective.ways[way_id][0].keys()[0]
                intent_data = objective.ways[way_id][0][intent_name]
                return goal_name, way_id, intent_name, intent_data, goal_weight, way_weight
        # TODO better error handling
        logger.error("no such objective registered: " + objective_name)
        return None, None, None, None, None, None

    def adjust_goal_weight(self, objective_name=None, ammount=0, increase=True, goal=None):

        if objective_name is None:
            objective_name = self.last_objective
            goal = self.last_goal
        elif goal is None:
            logger.error( "please specify a goal together with objective")
            return

        for objective in self.objectives:
            if objective.name == objective_name:
                size = len(objective.goal_weights)
                if size == 1 or size == 0:
                    size = 2
                # distribute ammount for all other goal weight
                ammount_to_distribute = ammount / (size - 1)
                # calculate new proweightb
                if increase:
                    ammount = objective.goal_weights[goal] + ammount
                else:
                    ammount = objective.goal_weights[goal] - ammount
                if ammount > 100:
                    ammount = 100
                elif ammount < 0:
                    ammount = 0

                # set new weight for all
                for g in objective.goal_weights:
                    if increase:
                        objective.goal_weights[g] -= ammount_to_distribute
                    else:
                        objective.goal_weights[g] += ammount_to_distribute

                # set new weight for target goal
                objective.goal_weights[goal] = ammount
                # TODO save to disk
                return True
        logger.error("could not fin that objective/goal")
        return False

    def adjust_way_weight(self, objective_name=None, ammount=0, increase=True, way=None):

        if objective_name is None:
            objective_name = self.last_objective
            way = self.last_way
        elif way is None:
            logger.error("please specify a way together with objective")
            return

        for objective in self.objectives:
            if objective.name == objective_name:
                for goal in objective.goals.keys():
                    for w in objective.goals[goal]:
                        if int(way) == w:
                            size = len(objective.goals)
                            if size == 1 or size == 0:
                                size = 2
                            # distribute ammount for all other goal weights
                            ammount_to_distribute = ammount / (size - 1)

                            # calculate new weight for way
                            if increase:
                                ammount = objective.way_weights[way] + ammount
                            else:
                                ammount = objective.way_weights[way] - ammount
                            if ammount > 100:
                                ammount = 100
                            elif ammount < 0:
                                ammount = 0
                            # set new weight for other ways
                            for w in objective.goals[goal]:
                                w = str(w)
                                if increase:
                                    objective.way_weights[w] -= ammount_to_distribute
                                else:
                                    objective.way_weights[w] += ammount_to_distribute
                                if objective.way_weights[w] < 0:
                                    objective.way_weights[w] = 0
                                elif objective.way_weights[w] > 100:
                                    objective.way_weights[w] = 100
                            # set new weight for way
                            objective.way_weights[way] = ammount
                            # TODO save to disk
                            return True
        logger.error("could not find that objective/way")
        return False

    def cancel_timers(self):
        for timer in self.timers:
            timer.cancel()
