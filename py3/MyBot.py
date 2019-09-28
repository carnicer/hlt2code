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
    logging.info("scorePlanetToNavigate. dist=%d, size=%d => score=%d" % (planetSize, distanceToPlanet, score))
    return score


# GAME START
# Here we define the bot's name as 'muke' and initialize the game, including communication with the Halite engine.
botName = "muke"
game = hlt.Game(botName)
# Then we print our start message to the logs
logging.info("Starting %s bot!" % botName)

while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    # maps planet : ship
    myTargetedPlanets = {}

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []
    # For every ship that I control
    for ship in game_map.get_me().all_ships():
        # If the ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:

            # Skip this ship (by now)
            continue
            # TODO : if many docked ships, undock some
            # TODO : how to know if many docked ships?

        if ship in myTargetedPlanets.values() :
            # Skip this ship, it has a planet already
            continue

        # for each planet, calculate score for going there ; already targeted
        # planets are discarded ; score depends on size and distance
        lListTup2_shipPlanetScores = []

        # For each planet in the game (only non-destroyed planets are included)
        for planet in game_map.all_planets():
            # by now, not discarding ships in myTargetedPlanets

            # If the planet is owned
            if planet.is_owned():
                # TODO : depending on game phase, launch attack to owned planets
                #
                # -- this is very important!!!
                # TODO : if planet is not owned by me, remove from myTargetedPlanets
                # -- this is very important!!!

                # Skip this planet
                continue

            # If we can dock, let's (try to) dock. If two ships try to dock at once, neither will be able to.
            if ship.can_dock(planet):
                # We add the command by appending it to the command_queue
                command_queue.append(ship.dock(planet))
                if planet in myTargetedPlanets.keys() :
                    # remove from this dict
                    gDictTargetedPlanets.pop(planet)

                # next planet
                continue

            else:
                planetScore = scorePlanetToNavigate(
                    ship.closest_point_to(planet),
                    getSize(planet),
                    # TODO : consider position of planet in the quadrant
                )
                lListTup2_shipPlanetScores.add((planet, planetScore))

        # TODO : py3, can i get the tuple like that?
        # TODO : lambda decreasing
        for planet, score in lListTup2_shipPlanetScores :

            navigate_command = None

            if planet not in myTargetedPlanets.keys() :
                # a cool planet, nobody going there
                navigate_command = ship.navigate(
                    ship.closest_point_to(planet),
                    game_map,
                    speed = int(hlt.constants.MAX_SPEED/2),
                    ignore_ships = True
                )
                myTargetedPlanets[ planet ] = ship

            else :

                # TODO : depending on game phase, consider going there
                # depending on number of available ships

                # TODO : go there if enough ships without a destination for
                # reinforcing the planet conquest

                if True : # TODO : add conditions here

                    closestShipDistance = -1
                    targetEnemyShip = -1
                    # TODO : attack the closest enemy ship
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

                else : # TODO : other conditions
                    pass

            # If the move is possible, add it to the command_queue (if there are too many obstacles on the way
            # or we are trapped (or we reached our destination!), navigate_command will return null;
            # don't fret though, we can run the command again the next turn)
            if not navigate_command == None :
                command_queue.append(navigate_command)

    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)

    # TURN END

# GAME END
