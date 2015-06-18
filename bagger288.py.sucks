import rg
import random
class Robot:
    turn = -1

    friendly_robots = {}

    def initialize_bagger_bot(self):
        if self.id() in self.friendly_robots:
            bagger_bot = self.friendly_robots[self.id()]
            bagger_bot.update(self.me())
        else:
            bagger_bot = self.BaggerBot(self,self.me())
            self.friendly_robots[self.id()] = bagger_bot
        return bagger_bot

    def id(self):
        return self.me().robot_id

    # return data for the bot currently playing
    def me(self):
        return self.game.robots[self.location]

    def initialize_turn(self):
        if self.game.turn != self.turn:
            self.first_robot = True
            self.turn_data = {}
        else:
            self.first_robot = False

    # indicate that a space will be taken (or attack into)
    def mark_occupied(self, location):
        self.turn_data[location] = True

    # attack a location
    def attack(self, location):
        self.mark_occupied(location)
        return ['attack', location]

    # move to a location
    def move(self, location):
        self.mark_occupied(location)
        return ['move', location]

    # guard in place
    def guard(self):
        self.mark_occupied(location)
        return ['guard']

    # determine if a location is currently unreserved
    def unoccupied(self, location):
        if location in self.turn_data:
            return False
        return True

    def act(self, game):
        self.game = game

        self.initialize_turn()

        bagger_bot = self.initialize_bagger_bot()

        return bagger_bot.act()

    class BaggerBot(object):
        near_threshold = 2

        center = (9,9)

        def __init__(self, robot, data):
            self.main_robot = robot
            self.update(data)
            self.state_stack = [self.wander]

        def id(self):
            return self.main_robot.id()

        def act(self):
            last_index = len(self.state_stack) - 1
            return self.state_stack[last_index]()

        def update(self, data):
            self.data = data;

        def push_state(self, state):
            self.state_stack.append(state)
            return self.act()

        def pop_state(self):
            state = self.state_stack.pop()
            #print "popped out of state: %s" % (state,)
            return self.act()

        # determine if a location is in the spawn zone
        def in_spawn(self):
            return self.location in [(7,1),(8,1),(9,1),(10,1),(11,1),(5,2),(6,2),(12,2),(13,2),(3,3),(4,3),(14,3),(15,3),(3,4),(15,4),(2,5),(16,5),(2,6),(16,6),(1,7),(17,7),(1,8),(17,8),(1,9),(17,9),(1,10),(17,10),(1,11),(17,11),(2,12),(16,12),(2,13),(16,13),(3,14),(15,14),(3,15),(4,15),(14,15),(15,15),(5,16),(6,16),(12,16),(13,16),(7,17),(8,17),(9,17),(10,17),(11,17)]

        def valid_locs(self):
            return rg.locs_around(self.data.location, filter_out=('invalid', 'obstacle'))

        def navigable_locs(self):
            return filter((lambda loc: self.main_robot.unoccupied(loc)), self.valid_locs())

        def enemy_at(self, location):
            if location in self.main_robot.game.get('robots'):
                return self.main_robot.game.get('robots')[location].player_id() != self.id()

        def adjacent_enemies(self, location):
            locs_around = rg.locs_around(location)
            return filter((lambda loc: self.enemy_at(loc)), locs_around)

        def retreatable_locs(self):
            return filter((lambda loc: len(self.adjacent_enemies(loc)) == 0), self.navigable_locs())

        def move(self, location):
            return self.main_robot.move(location)

        def attack(self, location):
            return self.main_robot.attack(location)

        def guard(self):
            return self.main_robot.guard()

        def hp(self):
            return self.data.hp

        # move towards a location
        def move_toward(self, location):
            return self.move(self.toward(location))

        def walking_distance(self, location):
            return rg.wdist(self.data.location, location)

        # attack toward a location
        def attack_toward(self, location):
            return self.attack(self.toward(location))

        # find the location that points towards another
        def toward(self, location):
            return rg.toward(self.data.location, location)

        # return all robots
        def robots(self):
            return [data[1] for data in self.main_robot.game.get('robots').items()]

        # return all enemy robots
        def enemy_robots(self):
            return filter((lambda bot: bot.get('player_id') != self.data.player_id), self.robots())

        # find the nearest enemy
        def nearest_enemy(self):
            return min(self.enemy_robots(), key=lambda bot: self.walking_distance(bot.location))

        # determine if a location is considered nearby
        def location_is_nearby(self, location):
            return rg.wdist(location, self.data.location) <= self.near_threshold

        # determine the neaest enemy which is also considered nearby,
        # may return None
        def nearest_nearby_enemy(self):
            nearest_enemy = self.nearest_enemy()
            if self.location_is_nearby(nearest_enemy.location):
                return nearest_enemy
            return None

        def unoccupied(self, location):
            return self.main_robot.unoccupied(location)

        def nearby_enemy_location(self):
            nearest_nearby_enemy = self.nearest_nearby_enemy()

            if nearest_nearby_enemy != None:
                potential_attack_location = self.toward(nearest_nearby_enemy.location)
                if self.unoccupied(potential_attack_location):
                    return nearest_nearby_enemy.location
            return None

        def wander(self):
            #print "entering wander"
            nearby_enemy_location = self.nearby_enemy_location()
            #print "nearby_enemy_location %s" % (nearby_enemy_location,)
            if nearby_enemy_location != None:
                return self.push_state(self.fight)

            return self.move(random.choice(self.navigable_locs()))

        #def should_retreat(self):
            #return self.hp() < 10:

        def retreat(self):
            path_to_nearest_safe_location = self.path_to_nearest_safe_location()
            if path_to_nearest_safe_location != None:
                self.move(path_to_nearest_safe_location[0])
            else:
                #print "guarding"
                self.guard()
            #if self.surrounded_by_enemies():
                #self.pop_state(self.bushido)

        def bushido(self):
            #print "entering bushido!"
            raise "not implemented"

        def surrounded_by_enemies(self):
            # TODO
            raise "not implemented"

        def fight(self):
            #print "entering fight"
            nearby_enemy_location = self.nearby_enemy_location()
            if nearby_enemy_location == None:
                return self.pop_state()
            return self.attack_toward(nearby_enemy_location)

            #towards_center = self.toward(self.center)
            #if self.unoccupied(towards_center):
                #return self.move_toward(self.center)
#
            #return self.guard()

