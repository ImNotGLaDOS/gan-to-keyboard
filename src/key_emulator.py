import win32con, win32api
import logging, time, string

from bind_reader import upload_binds
from named_pipes import PipeReader


MAX_BUFFER_SIZE = 100



class KeyEmulator:
  def __init__(self, bind_list: dict[tuple[str], list[list[str]]], constants: dict[str, any] | None = None):
    self.logger = logging.getLogger('KeyEmulator')
    self.bind_list = bind_list

    if not constants:
      constants = {'delete_mode': 'flush', 'idle_time': 10}
    self.delete_mode = constants['delete_mode']


  def process_buffer(self, buffer: list[str]) -> None:
    if keys := self._recognize(buffer):
      for comb in keys:
        self._press_keys(*self._key_to_codes(comb))  # _key_to_codes returns (codes, hold_time)
  

  def _recognize(self, turns: list[str]) -> list[list[str]] | None:
    """
    Search matches with binds in `turns`
    ret: key to press (i.g. [['ctrl', 'A'], ['0.5s'], ['alt', 'tab']])
    """
    for formula in self.bind_list.keys():
      if len(formula) <= len(turns) and turns[-len(formula):] == list(formula):
        ret = self.bind_list[formula]

        if self.delete_mode == 'flush':
          turns.clear()
        elif self.delete_mode == 'postfix':
          del turns[-len(formula):]
        elif self.delete_mode == 'keep':
          pass
        else:
          self.logger.warning(f'Invalid DELETE_MODE: {self.delete_mode}. Switching to \'flush\'...')
          self.delete_mode = 'flush'

        return ret
    return None
  

  def _key_to_codes(self, key: list[str]) -> tuple[list[int], float]:
    """
    key: key press in format ["ctrl", "A"]
    generate list of codes 'win32con.VK_{}'
    """
    ret: list[int] = []
    hold_time: float = 0.01

    # Mapping for special keys
    special_keys = {
      'ctrl': win32con.VK_CONTROL,
      'shift': win32con.VK_SHIFT,
      'tab': win32con.VK_TAB,
      'win': win32con.VK_LWIN,
      'left': win32con.VK_LEFT,
      'right': win32con.VK_RIGHT,
      'up': win32con.VK_UP,
      'down': win32con.VK_DOWN,
      'enter': win32con.VK_RETURN,
      'space': win32con.VK_SPACE,
      'esc': win32con.VK_ESCAPE,
      'escape': win32con.VK_ESCAPE,
      'backspace': win32con.VK_BACK,
      'del': win32con.VK_DELETE,
      'delete': win32con.VK_DELETE,
      'insert': win32con.VK_INSERT,
      'home': win32con.VK_HOME,
      'end': win32con.VK_END,
      'pageup': win32con.VK_PRIOR,
      'pagedown': win32con.VK_NEXT,
      'capslock': win32con.VK_CAPITAL,
      'alt': win32con.VK_MENU
    }

    symbol_map = {
        # Symbol names
        'comma': 0xBC,         # VK_OEM_COMMA
        'period': 0xBE,        # VK_OEM_PERIOD
        'slash': 0xBF,         # VK_OEM_2      ("/?" on US keyboard)
        'backslash': 0xDC,     # VK_OEM_5      ("\|" on US keyboard)
        'semicolon': 0xBA,     # VK_OEM_1      (";:" on US keyboard)
        'quote': 0xDE,         # VK_OEM_7      ("'\"" on US keyboard)
        'minus': 0xBD,         # VK_OEM_MINUS  ("-_" on US keyboard)
        'equals': 0xBB,        # VK_OEM_PLUS   ("=+" on US keyboard)
        'leftbracket': 0xDB,   # VK_OEM_4      ("[{" on US keyboard)
        'rightbracket': 0xDD,  # VK_OEM_6      ("]}" on US keyboard)
        'backtick': 0xC0,      # VK_OEM_3      ("`~" on US keyboard)
        
        # Single character symbols
        ',': 0xBC,  # VK_OEM_COMMA
        '.': 0xBE,  # VK_OEM_PERIOD
        '/': 0xBF,  # VK_OEM_2
       '\\': 0xDC,  # VK_OEM_5
        ';': 0xBA,  # VK_OEM_1
        "'": 0xDE,  # VK_OEM_7
        # '-': 0xBD,  # VK_OEM_MINUS  '-' reserved for separation
        '=': 0xBB,  # VK_OEM_PLUS
        '[': 0xDB,  # VK_OEM_4
        ']': 0xDD,  # VK_OEM_6
        '`': 0xC0,  # VK_OEM_3
    }

    for subkey in key:
      subkey = subkey.casefold()
      
      # Check for hold time
      if subkey.endswith('s') and subkey[:-1].replace('.', '').isdigit():
        try:
          hold_time = float(subkey[:-1])
        except ValueError:
          self.logger.warning(f"Invalid hold time: {subkey}")
        continue

      # Check special keys
      elif subkey in special_keys.keys():
        ret.append(special_keys[subkey])

      # Check special symbpls
      elif subkey in symbol_map.keys():
        ret.append(symbol_map[subkey])
      
      # Check function keys (F1-F12)
      elif subkey.startswith('f') and subkey[1:].isdigit():
        fn_num = int(subkey[1:])
        if 1 <= fn_num <= 12:
          ret.append(getattr(win32con, f'VK_F{fn_num}'))
        else:
          self.logger.warning(f'Unsupported F key: {subkey}')
      
      # Check single character keys
      elif len(subkey) == 1:
        if subkey in string.ascii_lowercase:
          ret.append(ord(subkey.upper()))
        elif subkey in string.digits:
          ret.append(ord(subkey))
        else:
          self.logger.warning(f'Unrecognized character key: {subkey}')
      
      else:
        self.logger.warning(f'Unrecognizable key: {subkey}')

    return ret, hold_time


  def _press_keys(self, keys: list[int], hold_time: float) -> None:
    """
    press the provided coded keys (then unpress)
    """
    for key in keys:
      win32api.keybd_event(key, 0, 0, 0)
    time.sleep(hold_time)
    for key in reversed(keys):
      win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
      time.sleep(0.01)


logger = logging.getLogger('KeyScript')


def trim_buffer(buffer: list[str]) -> None:
  while len(buffer) > 0:
    if buffer[-1][0] not in 'ULFRBD':
      logger.warning(f'Strange thing in buffer: {buffer[-1]}. Deleting it')
      del buffer[-1]
      continue

    if len(buffer) == 1:
      break

    if buffer[-1][0] != buffer[-2][0]:
      break

    # Merge/cancel out similar turns
    n1 = buffer[-1][1:]
    if n1 == '\'': n1 = 3
    elif n1 != '': n1 = int(n1)
    else:          n1 = 1
    
    n2 = buffer[-2][1:]
    if n2 == '\'': n2 = 3
    elif n2 != '': n2 = int(n2)
    else:          n2 = 1

    del buffer[-1]

    sm = (n1 + n2) % 4

    if sm == 0:   del buffer[-1]
    elif sm == 1: buffer[-1] = buffer[-1][0]
    elif sm == 2: buffer[-1] = buffer[-1][0] + '2'
    else:         buffer[-1] = buffer[-1][0] + '\''

  if len(buffer) > MAX_BUFFER_SIZE:
    del buffer[:-MAX_BUFFER_SIZE]
    trim_buffer(buffer)


def main():
  # Configuring logger
  logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
      datefmt='%H:%M:%S'
  )

  binds, constants = upload_binds()
  key_emulator = KeyEmulator(binds, constants)

  pipe = PipeReader()
  pipe.connect()

  buffer: list[str] = []  # global buffer of moves

  last_ts = time.time()

  while True:
    if moves := pipe.read():
      for move in moves:  # Emulating reading one-by-one
        last_ts = time.time()
        buffer.append(move)

        trim_buffer(buffer)
        key_emulator.process_buffer(buffer)
        logger.info(f'Current buffer (last 10) - {buffer[-10:]}')
    
    elif constants['idle_time'] != 0:
      if time.time() - last_ts > constants['idle_time'] and len(buffer) != 0:
        buffer.clear()
        logger.info('Cleared the buffer due to inactivity. []')
        last_ts = time.time()


if __name__ == "__main__":
  main()