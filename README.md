# How to use it
1. You need python installed and bluetooth turned on
2. Launch `INSTALL.bat` once (it installs necessary packages)
3. Setup desired binds in `binds.txt` (explanation is below)
4. Run `RUN.bat`

# Binds
`binds.txt` should contain lines in format `<formula> - <key comb> # <comment, not necessary>`.

Example: `R U R' U' - win+D+0.5s  # Close all windows`
1. `<formula>`: cube formula in official notation.
  
    Example: "R U R' U'"
2. "\_-\_" to separate formula and keys
3. `<key comb>`: combination of 'ctrl', 'shift', 'alt', 'win', 'tab', letter/digit keys and delay in seconds (additionally). Letter keys should be capital. Keys joined with "+". Delay tells how long combination will be holded (0.01 second by default) should be in format <1.0s>.
  
    Example: "win+shift+G+0.5s"
4. Everything after the "#" symbol is invisible for script so it could be used for comments

# Credits
Almost all information about connection protocol were taken from https://github.com/afedotov/gan-web-bluetooth

The `cryptor.py` file and some clarifications about how the whole thing works were taken from https://github.com/Alex-Beng/PySmartCubeGenshin.