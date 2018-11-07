import vlc
import time
import json
import syslog


with open('conf.json', 'r') as conf_file:
    conf = json.load(conf_file)


# find /sys/class/power_supply/ -name 'BAT*' | head -1
ACPI_PATH = conf['acpi_path']
CHARGE_NOW_PATH = conf['acpi_path'] + conf['energy_now_file']
CHARGE_FULL_PATH = conf['acpi_path'] + conf['energy_full_file']
CHARGE_STATUS_PATH = conf['acpi_path'] + conf['energy_status_file']


p = vlc.MediaPlayer(conf['song_uri'])


def get_file_content(path, convert=None):
    with open(path, 'r') as f:
        content = f.read()
    if convert:
        content = convert(content)
    return content


def check():
    """Returns True if the song should be played"""
    charge_now = get_file_content(CHARGE_NOW_PATH, int)
    charge_full = get_file_content(CHARGE_FULL_PATH, int)
    charge_status = get_file_content(CHARGE_STATUS_PATH)
    charge_percent = charge_now / charge_full * 100

    return charge_status == 'Discharging\n' and\
        charge_percent < conf['thereshold']


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
