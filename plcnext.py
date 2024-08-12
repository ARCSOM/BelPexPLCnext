from pyPLCn import pyPLCn
import time

def run_plc_operations():
    Plc = pyPLCn()

    Plc.set_var_names(['LevelMinimum', 'LevelMaximum', 'LevelCurrent'])
    Plc.connect('10.0.2.31', login='admin', password='8058c2d8', poll_time=100)
    while True:
        Plc.set_var('LevelMinimum', '500')
        Plc.set_var('LevelMaximum', '800')
        print('#####################################')
        print('LevelMinimum - {}'.format(Plc.get_var('LevelMinimum')))
        print('LevelMaximum - {}'.format(Plc.get_var('LevelMaximum')))
        print('LevelCurrent - {}'.format(Plc.get_var('LevelCurrent')))
        print('#####################################')
        time.sleep(0.5)
        Plc.set_var('LevelMinimum', '300')
        Plc.set_var('LevelMaximum', '500')
        print('#####################################')
        print('LevelMinimum - {}'.format(Plc.get_var('LevelMinimum')))
        print('LevelMaximum - {}'.format(Plc.get_var('LevelMaximum')))
        print('LevelCurrent - {}'.format(Plc.get_var('LevelCurrent')))
        print('#####################################')
        time.sleep(0.5)

if __name__ == '__main__':
    run_plc_operations()