#!/usr/bin/env python
from __future__ import print_function
import logging
from random import randint
import can
from can.bus import BusState
from sensors import RandHistory, SupportedPids

sensors = {
    0x04: { 'name': 'Engine Load', 'sensor': RandHistory(bytesize=1, initval=0, randstep=3)},
    0x05: { 'name': 'Engine Coolant Temp', 'sensor': RandHistory(bytesize=1, initval=128, randstep=1)},
    0x06: { 'name': 'STFT Bank 1', 'sensor': RandHistory(bytesize=1, initval=128, randstep=1)},
    0x07: { 'name': 'LTFT Bank 1', 'sensor': RandHistory(bytesize=1, initval=128, randstep=1)},
    0x08: { 'name': 'STFT Bank 2', 'sensor': RandHistory(bytesize=1, initval=128, randstep=1)},
    0x09: { 'name': 'LTFT Bank 2', 'sensor': RandHistory(bytesize=1, initval=128, randstep=1)},
    0x0A: { 'name': 'Fuel Pressure', 'sensor': RandHistory(bytesize=1, initval=128, randstep=1)},
    0x0B: { 'name': 'Manifold Absolute Pressure', 'sensor': RandHistory(bytesize=1, initval=128, randstep=1)},
    0x0C: { 'name': 'RPM', 'sensor': RandHistory(bytesize=2, initval=2400, randstep=200)},
    0x0D: { 'name': 'Speed', 'sensor': RandHistory(bytesize=1, initval=0, randstep=3)},
    0x0E: { 'name': 'Timing Advance', 'sensor': RandHistory(bytesize=1, initval=128, randstep=1)},
    0x0F: { 'name': 'Intake Air Temp', 'sensor': RandHistory(bytesize=1, initval=128, randstep=1)},
    0x10: { 'name': 'MAF rate', 'sensor': RandHistory(bytesize=2, initval=400, randstep=100)},
    0x11: { 'name': 'Throttle Position', 'sensor': RandHistory(bytesize=1, initval=128, randstep=1)},
}

supportedpid = SupportedPids(sensors)

def service1(bus, msg):
    arbid = msg.data[2]
    if arbid == 0x00:
        logging.info(">> Supported Pids")
        msg = can.Message(arbitration_id=0x7e8,
          data=[0x06, 0x41, arbid] + supportedpid.next(),
          is_extended_id=False)
        bus.send(msg)
    elif arbid in [0x20, 0x40, 0x60, 0x80, 0xA0, 0xC0]:
        logging.info(">> Extented Pid Support")
        msg = can.Message(arbitration_id=0x7e8,
          data=[0x06, 0x41, arbid, 0x00, 0x00, 0x00, 0x00],
          is_extended_id=False)
        bus.send(msg)
    elif arbid in sensors:
        sensor = sensors[arbid]
        logging.info(f">> {sensor['name']}")
        msg = can.Message(arbitration_id=0x7e8,
          data=[ 2 + sensor['sensor'].get_bytesize(), 0x41, arbid] + sensor['sensor'].next(),
          is_extended_id=False)
        bus.send(msg)
    else:
        logging.warning(f"!!! Service 1, unimplemented arbid->{arbid}")

def receive_all():
    bus = can.interface.Bus(bustype='socketcan',channel='can0')
    #bus = can.interface.Bus(bustype='ixxat', channel=0, bitrate=250000)
    #bus = can.interface.Bus(bustype='vector', app_name='CANalyzer', channel=0, bitrate=250000)

    #bus.state = BusState.ACTIVE
    #bus.state = BusState.PASSIVE

    try:
        while True:
            msg = bus.recv(1)
            if msg is not None:
                #logging.debug(msg)
                try: 
                    if msg.arbitration_id == 0x7df and msg.data[1] == 0x01:
                        service1(bus, msg)
                    else:
                        logging.warning(f"Unknown ARBID {msg.arbitration_id}")
                except:
                    logging.exception('Message did not conform to OBD PID statdard.')


    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    receive_all()
