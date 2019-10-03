"""
Welcome to your first Halite-II bot!

This bot's name is Settler => muke

"""
# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging


# TODO: create a class?

# TODO : consider position of planet in the quadrant
def scorePlanetToNavigate(distanceToPlanet, planetSize) :
    # TODO : don't use magic constants / read from config file
    # TODO : check actual planet sizes and distances
    score = planetSize * 40 - distanceToPlanet
    logging.info("scorePlanetToNavigate. dist=%d, size=%d => score=%d"
        % (planetSize, distanceToPlanet, score))
    return score


class Counter :

    def __init__(self) :
        self.miTotal = 0
        self.miMine = 0
        self.miNotOwned = 0
        # owned by others = total - owned by me - not owned

    def countMine(self) :
        self.miTotal += 1
        self.miMine += 1

    def countNotOwned(self) :
        self.miTotal += 1
        self.miNotOwned += 1

    def countTheirs(self) :
        self.miTotal += 1


# GAME START
# Here we define the bot's name as 'muke' and initialize the game, including communication with the Halite engine.
botName = "muke"
game = hlt.Game(botName)
# Then we print our start message to the logs
logging.info("Starting %s bot!" % botName)

# maps planet : ship
gDictTargetedPlanets = {}

gCounterShips = Counter()
gCounterPlanets = Counter()

while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    lTurnCounterShips = Counter()
    lTurnCounterPlanets = Counter()


    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []
    # For every ship that I control
    lListMyShips = game_map.get_me().all_ships()

    for ship in lListMyShips :

        lTurnCounterShips.countMine()

        # If the ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:

            # Skip this ship (by now)
            continue # next ship
            # TODO : if many docked ships, undock some
            # TODO : how to know if many docked ships?

        if ship in gDictTargetedPlanets.items() :
            # If we can dock, let's (try to) dock. If two ships try to dock at once, neither will be able to.
            # TODO : this is a mess
            if ship.can_dock(planet):
                # We add the command by appending it to the command_queue
                command_queue.append(ship.dock(planet))
                if planet in gDictTargetedPlanets.keys() :
                    # remove from this dict
                    gDictTargetedPlanets.pop(planet)

            # Skip this ship, it has a targeted planet already
            navigate_command = ship.navigate(
                ship.closest_point_to(planet),
                game_map,
                speed = int(hlt.constants.MAX_SPEED/2),
                ignore_ships = True
            )
            continue # next ship

        # for each planet, calculate score for going there ; already targeted
        # planets are discarded ; score depends on size and distance
        lListTup2_shipPlanetScores = []

        lbGotoNextShip = False

        # For each planet in the game (only non-destroyed planets are included)
        for planet in game_map.all_planets():

            # by now, not discarding ships in gDictTargetedPlanets

            # If the planet is owned
            if planet.is_owned():

                if planet.owner == me : # TODO : syntax!
                    lTurnCounterPlanets.countMine()
                else :
                    lTurnCounterPlanets.countTheirs()

                # TODO : depending on game phase, launch attack to owned planets
                #
                # -- this is very important!!!
                # TODO : if planet is not owned by me, remove from gDictTargetedPlanets
                # -- this is very important!!!

                # Skip this planet
                continue

            else : # planet not owned
                lTurnCounterPlanets.countNotOwned()


            # If we can dock, let's (try to) dock. If two ships try to dock at once, neither will be able to.
            if ship.can_dock(planet):
                # We add the command by appending it to the command_queue
                command_queue.append(ship.dock(planet))
                if planet in gDictTargetedPlanets.keys() :
                    # remove from this dict
                    gDictTargetedPlanets.pop(planet)

                lbGotoNextShip = True

                # next planet (will go to next ship too)
                continue

            else:
                planetScore = scorePlanetToNavigate(
                    ship.closest_point_to(planet),
                    planet.radius,
                    # TODO : consider position of planet in the quadrant
                )
                lListTup2_shipPlanetScores.add((planet, planetScore))

        if lbGotoNextShip == True :
            continue # next ship, dont issue a navigation to that planet

        for planet in sorted( lListTup2_shipPlanetScores.items()
            , key = lambda k : k[1]
            , reverse = True ) :

            navigate_command = None

            if planet in gDictTargetedPlanets.keys() :

                # check that the ship is still alive
                if ship not in lListMyShips :
                    # the ship has died
                    gDictTargetedPlanets.pop(planet)
                else :
                    # it will be matched sometime
                    continue

                # a cool planet, nobody going there
                navigate_command = ship.navigate(
                    ship.closest_point_to(planet),
                    game_map,
                    speed = int(hlt.constants.MAX_SPEED/2),
                    ignore_ships = True
                )
                gDictTargetedPlanets[ planet ] = ship

            else :

                # TODO : depending on game phase, consider going there
                # depending on number of available ships

                # TODO : go there if enough ships without a destination for
                # reinforcing the planet conquest

                if True : # TODO : add conditions here

                    closestShipDistance = -1
                    targetEnemyShip = -1
                    # TODO : attack the closest enemy ship
                    # TODO : syntax!!!
                    for enemyShip in game_map.get_enemies().all_ships():
                        distance = Distance( ship.closest_point_to(enemyShip) )
                        if targetEnemyShip == -1 or distance < closestShipDistance :
                            targetEnemyShip = enemyShip
                            closestShipDistance = distance
                        distance = ship.closest_point_to(enemyShip)

                    if not enemyShip == -1 :

                        navigate_command = ship.navigate(
                            ship.closest_point_to(enemyShip),
                            game_map,
                            speed = int(hlt.constants.MAX_SPEED/2),
                            ignore_ships = True
                        )

                    else :

                        logging.warning("ship %d without navigation (else of enemyShip == -1)" % ship)
                        # TODO : navigate somewhere
                        #pass

                else : # TODO : other conditions

                    pass


        # If the move is possible, add it to the command_queue (if there are too many obstacles on the way
        # or we are trapped (or we reached our destination!), navigate_command will return null;
        # don't fret though, we can run the command again the next turn)
        if not navigate_command == None :
            command_queue.append(navigate_command)

        else :
            logging.warning("ship %d without navigation, navigate_command None" % ship)

    # for ship ...

    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)

    # TURN END

# GAME END

