import vlc
import time
import json
import syslog
import argparse
from datetime import datetime, timedelta


with open('conf.json', 'r') as conf_file:
    conf = json.load(conf_file)


# find /sys/class/power_supply/ -name 'BAT*' | head -1
ACPI_PATH = conf['acpi_path']
CHARGE_NOW_PATH = conf['acpi_path'] + conf['energy_now_file']
CHARGE_FULL_PATH = conf['acpi_path'] + conf['energy_full_file']
CHARGE_STATUS_PATH = conf['acpi_path'] + conf['energy_status_file']
POSTPONE_PATH = '/tmp/lowbatteryalarm.postpone'

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_file_content(path, convert=None):
    with open(path, 'r') as f:
        content = f.read()
    if convert:
        content = convert(content)
    return content


def datetime_convert(content):
    return datetime.strptime(content, DATETIME_FORMAT)


def check():
    """Returns True if the song should be played"""
    print('checking...')
    charge_now = get_file_content(CHARGE_NOW_PATH, int)
    print('charge_now: ' + str(charge_now))
    charge_full = get_file_content(CHARGE_FULL_PATH, int)
    print('charge_full: ' + str(charge_full))
    charge_status = get_file_content(CHARGE_STATUS_PATH)
    print('charge_status: ' + charge_status)
    charge_percent = charge_now / charge_full * 100
    print('charge_percent: ' + str(charge_percent))
    postponed = get_file_content(POSTPONE_PATH, datetime_convert)
    print('postponed: ' + str(postponed))

    if datetime.utcnow() < postponed:
        return False
    
    return charge_status == 'Discharging\n' and\
        charge_percent < conf['thereshold']


def postpone():
    with open(POSTPONE_PATH, 'w') as f:
        postponed = datetime.utcnow() + timedelta(
            minutes=conf['postpone_minutes']
        )
        f.write(postponed.strftime(DATETIME_FORMAT))


def main():
    p = vlc.MediaPlayer(conf['song_uri'])
    with open(POSTPONE_PATH, 'w') as f:
        postponed = datetime.utcnow() - timedelta(
            minutes=conf['postpone_minutes']
        )
        f.write(postponed.strftime(DATETIME_FORMAT))
    while True:
        sleep_seconds = conf['normal_interval']
        if check():
            if not p.is_playing():
                p.stop()
            status = p.play()
            # is_playing() seems to return 0 if called just after play()
            # so sleep 0.2 seconds
            time.sleep(.2)
            if status != 0:
                syslog.syslog(syslog.LOG_ERR, 'vlc cannot play')
        else:
            p.stop()
        if p.is_playing() == 1:
            sleep_seconds = conf['alarmed_interval']
        time.sleep(sleep_seconds)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Play a song when your laptop battery is almost empty.')
    parser.add_argument(
        '--postpone',
        help='Postpone the alarm by minutes specified in config',
        action='store_true',
    )
    sysargs = parser.parse_args()
    if sysargs.postpone:
        postpone()
    else:
        main()
