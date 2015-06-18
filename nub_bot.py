import rg
import random

class Robot:
    def act(self, game):
        """act is called once for each living bot, per turn. It returns a move."""

        # TODO the first robot per turn gets 2.5 seconds. It would be best to calculate all the robot's moves during this
        # time. This would allow us to calcuate certain robot's moves first, giving them strategic priority.

        # Store a reference to the passed game, so that we can check what move we are in.
        self.game = game

        # Decide what type of move to make
        if self.is_about_to_die_from_being_in_the_spawn():
            return self.escape_from_spawn()

        if (self.is_very_weak() or self.is_outnumbered()) and self.is_able_to_flee():
            return self.flee()

        if self.is_facing_certain_dealth():
            return self.suicide()

        if self.is_adjacent_to_enemy_bot():
            return self.attack_weakest_nearby_bot()

        if self.is_able_to_move():
            return self.explore()

        return self.guard()

    ### MAIN BOT ACTIONS - These are the main actions that the bot can take, called from the act method
    def escape_from_spawn(self):
        """TODO, this just walks toward the center of the map, a general purpose path-finding algorithm would perform
        much better.
        """
        return self.move_toward(rg.CENTER_POINT)

    def flee(self):
        """Move away from enemy robots (but not into the spawn area if a spawn is about to occur.)"""
        return self.move(self.random_adjcaent_unoccupied_safe_location())

    def explore(self):
        """Move randomly into any location."""
        return self.move(self.random_adjacent_unoccupied_location())

    def attack_weakest_nearby_bot(self):
        """Attacks the weakest nearby bot"""
        # TODO, this only attacks bots that are already adjacent. Attacking bots that are 1 step away may yield better
        # results
        return self.attack_location(self.adjacent_location_with_weakest_enemy_bot())

    ### ROBOT STATE - These methods return info about the current state of the robot
    def is_about_to_die_from_being_in_the_spawn(self):
        """Every 10 turns, when new robots spawn, robots already in the spawn die.
        TODO this assumes that robots will be able to exit the spawn in 2 turns. If the robots is not blocked by
        other robots, it should be able to get out in one turn, unless they are in a corner. Consider making this
        logic more accurate.
        """
        return self.is_in_spawn() and self.game_spawns_robots_in_one_or_two_turns()
    
    def is_very_weak(self):
        """Return True if the robot has less than 13 hp."""
        return self.hp < 13

    def is_outnumbered(self):
        """Returns True if the bot is adjacent to two or more enemies."""
        return len(self.adjacent_locations_with_enemy_bots()) > 1

    def is_able_to_flee(self):
        """Returns True if there is an adjacent unoccupied safe location to flee into."""
        return len(self.adjacent_unoccupied_safe_locations()) > 0

    def is_able_to_move(self):
        """Returns True if the robot is adjacent to any unoccupied locations."""
        return len(self.adjacent_unoccupied_locations()) > 0

    def is_facing_certain_dealth(self):
        """Returns True if the bot is near an enemy, can't flee, and is very weak"""
        return self.is_adjacent_to_enemy_bot() and self.is_able_to_flee() == False and self.is_very_weak()

    def is_adjacent_to_enemy_bot(self):
        """Returns True if the bot is near one or more enemies."""
        return len(self.adjacent_locations_with_enemy_bots()) > 0

    def is_in_spawn(self):
        """Returns True if the robot is in the spawn."""
        return self.is_location_in_spawn(self.location)

    ### GAME STATE METHODS - These methods return info about the current state of the game
    def game_spawns_robots_next_turn(self):
        """Returns True if the game will spawn new robots next turn."""
        # % is the modulo operator. It evaluates to the remainder from the division of the left argument by the right.
        return self.game.turn % 10 == 8

    def game_spawns_robots_in_two_turns(self):
        """Returns True if the game will spawn new robots the turn after next."""
        return self.game.turn % 10 == 7

    def game_spawns_robots_in_one_or_two_turns(self):
        """Every 10 turns, new robots spawn, and robots already in the spawn area die. The first turn is 0, so the 10th 
        is 9. Therefore all turns ending in 9 are turns when spawns happen (expect the last turn, 99.)
        If this turn ends in 7 or 8, it is one or two turns until the spawn occurs.
        """
        return self.game_spawns_robots_in_two_turns() or self.game_spawns_robots_next_turn()

    ### LOCATIONS NEAR ROBOT - These methods return info about the locations adjacent to the robot
    def adjacent_locations(self):
        """Return all locations that are adjacent to the robot."""
        return self.locations_adjacent_to_location(self.location)

    def adjacent_unoccupied_locations(self):
        """Returns all adjacent locations which are not occupied."""
        return filter(self.is_location_unoccupied, self.adjacent_locations())

    def random_adjacent_unoccupied_location(self):
        """Returns a randomly chosen, unoccupied, adjacent location.
        """
        return random.choice(self.adjacent_unoccupied_locations())

    def adjacent_unoccupied_safe_locations(self):
        """Returns all safe, unoccupied, adjacent, locations.
        """
        return filter(self.is_location_safe, self.adjacent_unoccupied_locations())

    def random_adjcaent_unoccupied_safe_location(self):
        """Returns a randomly chosen, adjacent, safe, unoccupied, location."""
        return random.choice(self.adjacent_unoccupied_safe_locations())

    def adjacent_locations_with_enemy_bots(self):
        """Returns all adjacent locations that have enemy robots in them."""
        return self.enemy_locations_adjacent_to_location(self.location)

    def adjacent_location_with_weakest_enemy_bot(self):
        """Return the location of the weakest adjacent bot, or None if there is not one."""
        if len(self.adjacent_locations_with_enemy_bots()) > 0:
            return min(self.adjacent_locations_with_enemy_bots(), key=self.hp_of_bot_at_location)
        return None

    ### BOARD STATE METHODS - These methods return info about a location on the board. You MUST pass a location to use
    # these methods.
    def robot_at_location(self, location):
        """Get the robot at the passed location."""
        return self.game.robots.get(location,None)

    def is_location_occupied_by_an_enemy(self, location):
        """Return True if there is an enemy in the passed location."""
        robot = self.robot_at_location(location)
        if robot != None:
            return robot.player_id != self.player_id

    def is_location_unoccupied(self, location):
        """Returns True if there is no robot at the passed location."""
        return self.robot_at_location(location) == None

    def hp_of_bot_at_location(self, location):
        """Return the health of the bot at a location."""
        return self.game.robots[location].hp
        
    def locations_adjacent_to_location(self, location):
        """Return all the locations that are adjacent to a passed location."""
        return rg.locs_around(location, filter_out=("invalid", "obstacle",))

    def enemy_locations_adjacent_to_location(self, location):
        """Return locations of enemies adjacent to a passed location."""
        return filter(self.is_location_occupied_by_an_enemy, self.locations_adjacent_to_location(location))

    def is_location_adjacent_to_an_enemy(self, location):
        """Return True if the passed location has an enemy adjacent to it."""
        return len(self.enemy_locations_adjacent_to_location(location)) > 0

    def is_location_in_spawn(self, location):
        """Returns True if the location is in the spawn area."""
        return "spawn" in rg.loc_types(location)

    def is_location_safe(self, location):
        """Return True if the location has no adjacent enemy bots (and if it isn't in the spawn area, if the spawn is
        about to occur.
        """
        if self.game_spawns_robots_in_one_or_two_turns() and self.is_location_in_spawn(location):
            return False
        else:
            return self.is_location_adjacent_to_an_enemy(location) == False

    ### MOVE HELPERS - these methods just return moves, but you may choose to improve them
    def move(self, location):
        """TODO Currently, the robot's don't consider the current or intended location of friendly players. They also
        don't consider the current or predicted location of enemies.
        A simple implementation might consist of just storing locations that a friendly robot is planning to move into
        or attack into. A more sophisticated implementation could calculate all robot moves during the first call to
        act in the first turn, allowing high-priporty robots to act first. (For example, nearly dead robots could 
        escape to saftey.
        """
        return ["move", location]

    def attack_location(self, location):
        """Attack the passed location."""
        return ["attack", location]

    def suicide(self):
        return ["suicide"]

    def guard(self):
        return ["guard"]

    def move_toward(self, location):
        """Return a move that puts us closer to the passed location."""
        return self.move(rg.toward(self.location, location))
