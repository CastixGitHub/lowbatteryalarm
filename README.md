This simple script plays a song with [python-vlc](https://pypi.org/project/python-vlc/)
when your laptop's battery is running out.

This is useful for windows managers such as [i3wm](i3wm.org) or if you do use graphic interfaces at all.

## Installation

### Dependencies

- Python 3
- VLC

### Manual Installation (development)

- get the source code with `git clone` or download and unzip

  ```bash
  git clone https://github.com/CastixGitHub/lowbatteryalarm
  cd lowbatteryalarm
  ```
- install python-vlc

  ```bash
  pip install --user python-vlc
  ```

- [customize your config file](#Configuration)

- test it:

  + remember to unplug your AC

  + check that you set a thereshold just a bit bigger than your % of charge

  + run the script in background. [read this small guide](https://kb.iu.edu/d/afnw)
    if you need help on managing background processes

    ```bash
    python lowbatteryalarm.py &
    ```

  + wait some minutes

  + when your battery level is less than the thereshold you still have to

  + wait **normal_interval** seconds and enjoy the selected song :)

    * otherwise open a new issue :(

  + plug your AC cable and wait up to **alerted_interval**
    
    * the song should stop, otherwise open a new issue :(

- **make this script start automatically on login**
  Assuming you do not use a DM (Display Manager)
  edit your ``~/.bash_profile`` or (``~/.zprofile`` if you use [zsh](zsh.org))
  to get something similar to the following example:

  ```bash
  if [[ -z $DISPLAY ]] && [[ $(tty) = /dev/tty1 ]]; then
    # Low Battery Alarm
    cd ~/lowbatteryalarm
    python lowbatteryalarm.py &
    cd ~
    # End Low Battery Alarm

    # start X.org server
    exec startx
  fi
  ```
  so make sure to login from tty1 when your pc boots.

  Pull requests with integration for systemd, openrc, runit, upstart and so on will be well accepted.


## Configuration

configuration is handled in the file ``conf.json``

here an explaination of all the confirurable fields:

- **thereshold** integer, when your battery percentage is lower than thereshold, the song plays

- **acpi_path** string, path to your battery, run ``find /sys/class/power_supply/ -name 'BAT*' | head -1`` to get it

- **energy_now_file** string, filename of the file under **acpi_path** that contains the current energy of your battery

- **energy_full_file** string, filename of the file under **acpi_path** that contains the battery capacity

- **energy_status_file** string, filename of the file under **acpi_path** that contains the status of your battery (example: Discharging, Charging)

- **song_uri** string, uri given to vlc to the file you want to play

- **normal_interval** integer, interval to poll the battery when the song is not playing, 60 is a reasonable choise

- **alarmed_interval** integer, interval to poll the battery when the song is playing, 5 is a reasonable choise

- **postpone_minutes** integer, postpone the alarm by that minutes

## POSTPONE

from the directory where this script is, launch the ``postpone.sh`` executable or ``python lowbatteryalarm.py --postpone`` and after **alarmed_interval** seconds it will stop playing for **postpone_minutes** minutes, then if it's still discarging it will play again

if you're using i3wm then add the following line to your config file (~/.config/i3/config) so you can postpone it easly

```bash
bindsym $mod+p exec /home/castix/lowbatteryalarm/postpone.sh
```