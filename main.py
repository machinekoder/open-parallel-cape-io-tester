
import sys
from machinekit import hal
from machinekit import rtapi as rt
from machinekit import config as c
if sys.version_info >= (3, 0):
    import configparser
else:
    import ConfigParser as configparser

_NUM_IOS = 34


def get_pin(name):
    if name in hal.pins:
        return hal.pins[name]
    else:
        return None


c.load_ini('hardware.ini')

io_map = {
    0: '813',
    1: '926',
    2: '811',
    3: '918',
    4: '812',
    5: '942',
    6: '815',
    7: '911',
    8: '816',
    9: '925',
    10: '913',
    11: '921',
    12: '922',
    13: '917',
    14: '807',
    15: '819',
    16: '941',
    17: '923',
    18: '930',
    19: '914',
    20: '931',
    21: '915',
    22: '808',
    23: '810',
    24: '809',
    25: '814',
    26: '817',
    27: '818',
    28: '912',
    29: '916',
    30: '924',
    31: '927',
    32: '928',
    33: '929',
}

output_pins = ','.join(io_map.values())

rt.loadrt('hal_bb_gpio', output_pins=output_pins, input_pins='')
#rt.loadrt(c.find('PRUCONF', 'DRIVER'), 'prucode=%s/%s' % (c.Config().EMC2_RTLIB_DIR, c.find('PRUCONF', 'PRUBIN')),
#          pru=1, num_stepgens=3, num_pwmgens=3, halname='hpg')


servo_thread = 'servo_thread'
rt.newthread(servo_thread, c.find('TASK', 'CYCLE_TIME') * 1e9, fp=True)

#hal.addf('hpg.capture-position', servo_thread)
hal.addf('bb_gpio.read', servo_thread)
# TODO: HAL comps

rcomp = hal.RemoteComponent('io-control', timer=100)
for i in range(_NUM_IOS):
    rcomp.newpin('io-%i.value' % i, hal.HAL_BIT, hal.HAL_IO)
    rcomp.newpin('io-%i.pin' % i, hal.HAL_U32, hal.HAL_OUT)
rcomp.ready()

for io in io_map:
    name = io_map[io]
    port = name[0]
    pin = name[1:]
    pin = hal.pins['bb_gpio.p%s.out-%s' % (port, pin)]
    rcomp.pin('io-%i.value' % io).link(pin)
    rcomp.pin('io-%i.pin' % io).set(int(name))

#hal.addf('hpg.update', servo_thread)
hal.addf('bb_gpio.write', servo_thread)

hal.start_threads()

# start haltalk server after everything is initialized
# else binding the remote components on the UI might fail
hal.loadusr('haltalk')
