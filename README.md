## Description
Python script to map GAN smart cube turns to keyboard presses. Works only on Windows.

## Disclaimer
This project isn't properly tested yet, so if you experience any issues or don't understand something and README isn't helping, please contact the creator. It will not only help you solve the problem but also will help improve the project. Any suggestions and feedback are also welcome.

## How to use it
1. Ensure you have Python 3 installed and Bluetooth enabled on your system.
2. Run `INSTALL.bat` once to install necessary packages.
3. Configure desired binds in `binds.txt` (see explanation below).
4. Run `RUN.bat`.

## Binds
The script stores all received turns in a buffer. When it notices a formula listed in `binds.txt` at the end of the buffer, it presses the corresponding keys. Then it flushes the buffer and waits for the next match.

### Syntax
`binds.txt` should contain lines of binds in the format `<formula> - <key combination> [# <comment>]`.

Example: `R U R' U' - win+D # Close all windows`
1. `<formula>`: cube formula in official notation.
  
    Example: "R U R' U'"
2. ` - ` (a hyphen surrounded by spaces) to separate the formula and keys.
3. `<key combination>`: combination of keyboard keys. Keys are joined with "+" (no spaces).
    
    A full list of supported keys: 
    - Special keys: [`'ctrl'`, `'shift'`, `'tab'`, `'win'`, `'left'`, `'right'`, `'up'`, `'down'`, `'enter'`, `'space'`, `'esc'`/`'escape'`, `'backspace'`, `'del'`/`'delete'`, `'insert'`, `'home'`, `'end'`, `'pageup'`, `'pagedown'`, `'capslock'`, `'alt'`].
    - `F1`-`F12` keys.
    - Letter and digit keys.
    - Symbols: [`'comma' / ','`, `'period' / '.'`, `'slash' / '/'`, `'backslash' / '\'`, `'semicolon' / ';'`, `'quote' / "'"`, `'minus'` (note that `'-'` is reserved for binds separation), `'equals' / '='`, `'leftbracket' / '{'`, `'rightbracket' / '}'`, `'backtick'`].
    - Mouse buttons: [`'lmb' / 'lclick'`, `'rmb' / 'rclick'`]
    - Hold time as `1.1s` (see "Advanced adjustments" for clarification).
  
    Example: `shift+semicolon`, `ctrl+{`, `tab+0.5s+rmb`
4. Everything after the `#` symbol is ignored by the script and may be used for comments.

### Tips and unexpected behavior
Avoid having a formula that is a subsequence of another formula since the subformula will trigger the script before you perform the full one.

- **Example:**
    You have two binds: `R U R' U' - alt+F4` and `U R' - alt+tab`. You try to do the first bind and performe `R U R'`. At this moment before you perform next move, script notices `U R'` at the end of buffer, presses `alt+tab`, and now the buffer is empty. When you finish doing the formula, the buffer contains only `U'` and `alt+F4` wasn't pressed.

Remember that similar moves in buffer will be merged and can cancel out each other.

- **Example 1:** You have a bind `R U R' U' - ctrl+shift`. You do `U R U' R'` (the inverse of the formula). Now when you try to do `R U R' U'`, each move will cancel out the last move in buffer. In the end, the buffer is empty and `ctrl+shift` wasn't pressed.

    - **Tip:** Different binds can share key combinations. For example, to prevent this situation, you can add the bind `U R U' R' - ctrl+shift`.

- **Example 2:** You have a bind `U - W`. You have done `U'` two times, and the buffer normalizes this to `U2` (not `U'2`!). When you try to do another `U'`, the buffer will contain `U2` + `U'` = `U`, then it will press `W` key.

Remember to hold the cube with the right orientation: white center piece up and green center piece front.

The script does not store the whole history of moves -- only the last 100 moves. It also clears the buffer if it does not receive any moves for 10 seconds.

### Advanced adjustments

You can change the script behavior in the following ways:
- You can make more than one key combination in the bind. The combinations should be separated with space. Note that hold time (i.g. `0.5s`) is technically also a combination. **Example:** `R U - win+D 5.0s win+D  # Show the desktop for 5 seconds`

- You can control how the script treats the buffer after it reads a formula. To do this, you can add the line `! DELETION FLUSH` (or replace "FLUSH" with name of other mode) in `binds.txt`. There are three modes:
    - `FLUSH` **(default)**. In this mode, the script clears the whole buffer after reading any formula
    - `POSTFIX`. In this mode, the script will delete only the formula itself leaving all previous history of moves.

        **Example:** You have a bind `R U F U' - ctrl`. You can do `R U F` five times, then do `U'` five times, and you'll hit `ctrl` five times. In default mode, it would not be possible. Note that it would not work with the formula `R U R' U'` since `R U R'` + `R U R'` = `R U R' R U R'` = `R U U R'` = `R U2 R'`.
    
    - `KEEP`. In this mode, the script never deletes anything from the buffer (except it can't store more than 100 moves). However, the script checks for matching formulas only when it receives a new move, so it won't hold the key forever if the buffer contains the right formula in its end.

        **Example:** You have a bind `R U R' U' - F5`. You can do the formula once, then do `R R'` continuously. The `R R'` will cancel each other out, and the end of the buffer will match the bind again.

- You can control after how much time of inactivity the script clears the buffer (default is 10 seconds). To do that, add the line `! IDLE_TIME <float>`, where `<float>` is in seconds (e.g. `0.5`). `! IDLE_TIME 0` disables this feature.

- You can adjust how long the script holds the combination of keys. To do that, you can add `1.0s` (replace the number with your own) to the combination as if it were a key. **Example:** `win+shift+D+3.141s`. The default value is `0.01s`.


## Tested cubes
A list of supported cubes:
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

Most of the cubes have not been tested yet. If a cube with the same protocol as yours has been tested, most likely your cube will also work. If your cube is on the list and has not been tested, please contact the creator.

## Credits
Almost all information about the connection protocol was taken from https://github.com/afedotov/gan-web-bluetooth.

The `cryptor.py` file and some clarifications about how to connect to the cube using the `bleak` library were taken from https://github.com/Alex-Beng/PySmartCubeGenshin.

## Contacts
GitHub: https://github.com/ImNotGLaDOS
Email: zakharov.mark@phystech.edu
Telegram: https://t.me/im_not_glados
Reddit: https://www.reddit.com/user/Im_Not_GLaDOS/