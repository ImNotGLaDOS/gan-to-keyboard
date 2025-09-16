# Description
Python script to map GAN smart cubes turns to keyboard presses. Works only on Windows (yet).

# How to use it
1. Ensure you have Python 3 installed and Bluetooth enabled on your system
2. Launch `INSTALL.bat` once to install necessary packages
3. Set up desired binds in `binds.txt` (see explanation below)
4. Run `RUN.bat`

# Binds
`binds.txt` should contain lines in format `<formula> - <key combination> # <comment, not necessary>`.

Example: `R U R' U' - win+D+0.5s  # Close all windows`
1. `<formula>`: cube formula in official notation.
  
    Example: "R U R' U'"
2. "\_-\_" to separate formula and keys
3. `<key combination>`: combination of 'ctrl', 'shift', 'alt', 'win', 'tab', letter/digit keys and delay in seconds (additionally). Letter keys should be uppercase. Keys joined with "+". Delay tells how long combination will be held (0.01 second by default) should be in format <1.0s>.
  
    Example: "win+shift+G+0.5s"
4. Everything after the "#" symbol is ignored by the script and may be used for comments.

# Tested cubes
List of supported cubes:
1. Gen2-protocol cubes:
    - `NOT TESTED` GAN Mini ui FreePlay
    - `NOT TESTED` GAN12 ui
    - `NOT TESTED` GAN356 i Carry S
    - `NOT TESTED` GAN356 i Carry
    - `NOT TESTED` GAN356 i 3
2. Gen3-protocol cubes:
    - `NOT TESTED` GAN356 i Carry 2
3. Gen4-protocol cubes:
    - GAN12 ui Maglev
    - `NOT TESTED` GAN14 ui FreePlay

Most of the cubes haven't been tested yet. If one of the cubes with same protocol as yours have been tested, most likely your cube also will work. If your cube is in the list and haven't been tested, contact the creator.

# Credits
Almost all information about connection protocol was taken from https://github.com/afedotov/gan-web-bluetooth.

The `cryptor.py` file and some clarifications about how the whole thing works were taken from https://github.com/Alex-Beng/PySmartCubeGenshin.