# Description
Python script to map GAN smart cubes turns to keyboard presses. Works only on Windows (yet).

# How to use it
1. Ensure you have Python 3 installed and Bluetooth enabled on your system
2. Launch `INSTALL.bat` once to install necessary packages
3. Set up desired binds in `binds.txt` (see explanation below)
4. Run `RUN.bat`

# Binds
Script stores all made turns in buffer. When it notices at the end of buffer the formula listed in `binds.txt` it presses corresponding 

Tip: You want to have no formula that is subformula for other since subformula will trigger script before you perform the full one.

> Example:
>
>You have deletion mode set to `POSTFIX` and two binds: `R U R' U' - alt+F4` and `U R' - alt+tab`. You try to do first bind and performed `R U R'`. At this moment before you perform next move, script takes `U R'` from buffer, press `alt+tab` and now the buffer contains only `R`. When you finish doing `R U R' U'`, in buffer there are only `R U'` and `alt+F4` wasn't pressed.

Deletion mode decides how script

### Sintaxis
`binds.txt` should contain lines of binds in format `<formula> - <key combination> # <comment, not necessary>` and one line `! [FLUSH, KEEP, POSTFIX]` – it's the deletion mode.

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