# Description
Python script to map GAN smart cubes turns to keyboard presses. Works only on Windows (yet).

# How to use it
1. Ensure you have Python 3 installed and Bluetooth enabled on your system
2. Launch `INSTALL.bat` once to install necessary packages
3. Configure desired binds in `binds.txt` (see explanation below)
4. Run `RUN.bat`

# Binds
Script stores all received turns in buffer. When it notices at the end of buffer formula listed in `binds.txt` it presses corresponding keys. Then flush the buffer and waits for the next match.

## Syntax
`binds.txt` should contain lines of binds in format `<formula> - <key combination> [# <comment>]`.

Example: `R U R' U' - win+D # Close all windows`
1. `<formula>`: cube formula in official notation.
  
    Example: "R U R' U'"
2. ` - ` (a hyphen surrounded by spaces) to separate the formula and keys.
3. `<key combination>`: combination of `ctrl`, `shift`, `alt`, `win`, `tab`, letter/digit keys, `F<number>` keys and delay in seconds (additionally). Keys joined with "+".
  
    Example: `win+shift+G`
4. Everything after the `#` symbol is ignored by the script and may be used for comments.

## Tips and unexpected behavior
Avoid having a formula that is a subsequence of another formula since subformula will trigger script before you perform the full one.

- **Example:**
    You have two binds: `R U R' U' - alt+F4` and `U R' - alt+tab`. You try to do first bind and performed `R U R'`. At this moment before you perform next move, script notices `U R'` at the end of buffer, press `alt+tab` and now the buffer is empty. When you finish doing the formula, in buffer there are only `U'` and `alt+F4` wasn't pressed.

Mind that similar moves in buffer will be merged and can cancel out each other.

- **Example 1:** You have bind `R U R' U' - ctrl+shift`. You do `U R U' R'` (the opposite to the formula). Now when you try to do `R U R' U'`, each move will cancel out the last move in buffer. In the end the buffer is empty and `ctrl+shift` wasn't pressed.

    - **Tip:** Different binds can share the key combinations. For example, to prevent this situation, you can add bind `U R U' R' - ctrl+shift`

- **Example 2:** You have bind `U - W`. You have done `U'` two times and the buffer normalizes this to `U2` (not `U'2`!). When you try to do another `U'` the buffer will be containing `U2` + `U'` = `U` then it will press `W` key.

Remember to hold cube with the right orientation: White center piece up and green center piece front.

The script do not stores the whole history of moves - only last 100 moves.

## Advanced adjustments

You can change the script behavior in following ways:
- You can control how the script treats the buffer after it read some formula. To do it you can add in `binds.txt` line `! FLUSH` (or replace "FLUSH" with name of other mode) .There are three modes:
    - `FLUSH` **(default)**. In this mode script clears the whole buffer after reading any formula
    - `POSTFIX`. In this mode script will delete only the formula itself remaining all previous history of moves.

        **Example:** You have bind `R U F U' - ctrl`. You can do `R U F` 5 times, then do `U'` 5 times and you'll hit `ctrl` 5 times. In default mode it wouldn't be possible. Note that it wouldn't work with formula `R U R' U'` since `R U R'` + `R U R'` = `R U R' R U R'` = `R U U R'` = `R U2 R'`
    
    - `KEEP`. In this mode script never delete anything from the buffer (except it can't store more than 100 moves). Though, the script checking for matching formulas only when it receives new move so it won't hold the key forever if the buffer contains right formula in its end.

        **Example:** You have bind `R U R' U' - F5`. You can do the formula once then do `R R'` continuously. The `R R'` will cancel out each other and the end of the buffer again will match the bind.

- You can adjust how long the script will be holding the combination of keys. To do that you can add `1.0s` (replace the number with yours) to combination as another key. **Example:** `win+shift+D+3.141s`. The default value is `0.01s`.


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

The `cryptor.py` file and some clarifications about how to connect to cube using `bleak` library were taken from https://github.com/Alex-Beng/PySmartCubeGenshin.