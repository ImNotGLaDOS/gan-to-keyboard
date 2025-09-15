# How to use it
1. You need Python 3 installed and bluetooth turned on
2. Launch `INSTALL.bat` once to it installs necessary packages
3. Set up desired binds in `binds.txt` (see explanation below)
4. Run `RUN.bat`

# Binds
`binds.txt` should contain lines in format `<formula> - <key combination> # <comment, not necessary>`.

Example: `R U R' U' - win+D+0.5s  # Close all windows`
1. `<formula>`: cube formula in official notation.
  
    Example: "R U R' U'"
2. "\_-\_" to separate formula and keys
3. `<key combination>`: combination of 'ctrl', 'shift', 'alt', 'win', 'tab', letter/digit keys and delay in seconds (additionally). Letter keys should be uppercase. Keys joined with "+". Delay tells how long combination will be holded (0.01 second by default) should be in format <1.0s>.
  
    Example: "win+shift+G+0.5s"
4. Everything after the "#" symbol is ignored by the script and may be used for comments.

# Credits
Almost all information about connection protocol were taken from https://github.com/afedotov/gan-web-bluetooth

The `cryptor.py` file and some clarifications about how the whole thing works were taken from https://github.com/Alex-Beng/PySmartCubeGenshin.