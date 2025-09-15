# How to use it
0. You need python installed and bluetooth turned on
1. Launch INSTALL.bat (you won't have to use it again, it's install necessary packages)
2. Setup desired binds in `binds.txt` (explanation will be below)
3. Run RUN.bat and in case of errors follow provided instructions (if given)
4. If error logs says something about "No permission" and "UUIDs", most likely your cube is not supported yet. Apply to "UUIDs bruteforce" part then contact creator

# Binds
`binds.txt` should contain lines in format "<formula> - <key comb> # <comment, not nessecary>".
1. <formula>: cube formula in official notation. Example: "R U R' U'"
2. "\_-\_" to separate formula and keys
3. <key comb>: combination of 'ctrl', 'shift', 'alt', 'win', 'tab', letter/digit keys and delay in seconds (additionally). Letter keys should be capital. Keys joined with "+". Delay tells how long combination will be holded (0.01 second by default) should be in format <1.0s>. Example: "win+shift+G+0.5s"
4. Script do not read anything in line after "#" symbol so it could be used for comments

# UUIDs bruteforce
1. Launch UUIDS_FINDER.py. If the script connects to your cube, it'll give list of all cube's UUIDs with properties. You need 2 of them: one with "notify" property and one with "write, write-without-responce" properties.
1.1. (TODO: EXAMPLE)
2. 