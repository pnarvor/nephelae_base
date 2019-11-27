#! /usr/bin/python3

# READ THIS FIRST ! ############################
# to make a test run the following commands:
# create_mission() -> will create a mission instance
# scenario.aircrafts['200'].execute_mission() -> will send the MISSION_CUSTOM message to update the uav
# update_mission(hdrift=[7.5, 0.5]) -> will send the MISSION_UPDATE update the [vx, vx] on current mission.
# update_mission(zdrift=2.0) -> will send the MISSION_UPDATE update vz on current mission.
################################################



import signal

from nephelae_scenario         import Scenario
from nephelae_paparazzi.common import IvyStop, messageInterface
from nephelae_paparazzi.utils  import send_lwc

scenario = Scenario('config_examples/full_200.yaml')
scenario.load()
scenario.start()

def create_mission(aircraft='200', missionType='Lace', duration=-1.0,
                   start=[-1500.0, 900.0, 700.0], first_turn_direction=1.0,
                   circle_radius=80.0, drift=[-7.5,-0.5,0.0]):
    scenario.aircrafts[aircraft].create_mission(
        missionType=missionType,
        duration=duration,
        start=start,
        first_turn_direction=first_turn_direction,
        circle_radius=circle_radius,
        drift=drift)
# Do a scenario.aircrafts['200'].execute_mission() to send mission to aircraft
# (no mission list managed for now)


def update_mission(aircraft='200', duration=-9.0, **kwargs):
    mission = scenario.aircrafts[aircraft].currentMission
    msgs = mission.build_update_messages(duration, **kwargs)
    for msg in msgs:
        messageInterface.send(msg)
# Examples of update:
# update_mission(hdrift=[7.5, 0.5])
# update_mission(zdrift=3.0)


def stop():
    if scenario.running:
        print("Shutting down... ", end='', flush=True)
        scenario.stop()
        print("Complete.", flush=True)
    IvyStop()
    try:
        get_ipython().ask_exit()
    except NameError:
        sys.exit()
signal.signal(signal.SIGINT, lambda sig,fr: stop())



