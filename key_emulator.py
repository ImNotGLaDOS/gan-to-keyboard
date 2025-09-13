import win32con, win32api
import time, string

from bind_reader import upload_binds
from named_pipes import PipeReader


MAX_BUFFER_SIZE = 30
DELETE_MODE = ['flush', 'postfix', 'keep'][0]



class KeyEmulator:
  def __init__(self, bind_list: dict[tuple[str], str]):
    self.bind_list = bind_list
    self._print("Created")


  def _print(self, *text) -> None:
    print("[KeyEmlator]: ", *text)


  def process_buffer(self, buffer: list[str]) -> None:
    if keys := self._recognize(buffer):
      self._press_keys(*self._key_to_codes(keys))  # _key_to_codes returns (codes, hold_time)
  

  def _recognize(self, turns: list[str]) -> list[str] | None:
    """
    Search matches with binds in `turns`
    ret: key to press (e.g. ['ctrl', 'A'])
    """
    for postfix in range(len(turns), 0, -1):
      if tuple(turns[-postfix:]) in self.bind_list.keys():
        ret = self.bind_list[tuple(turns[-postfix:])]

        if DELETE_MODE == 'flush':
          turns.clear()
        elif DELETE_MODE == 'postfix':
          del turns[-postfix:]  # NOT TESTED
        elif DELETE_MODE == 'keep':
          pass  # NOT TESTED
        else:
          self._print(f'Invalid DELETE_MODE: {DELETE_MODE}')

        return ret
    return None
  

  def _key_to_codes(self, key: list[str]) -> tuple[list[int], float]:
    """
    key: key press in format ["ctrl", "A"]
    generate list of codes 'win32con.VK_{}'
    """
    ret: list[tuple[int]] = []
    hold_time: float = 0.003

    for subkey in key:
      if subkey == 'ctrl':
        ret.append(win32con.VK_CONTROL)

      elif subkey == 'shift':
        ret.append(win32con.VK_SHIFT)

      elif subkey == 'alt':
        ret.append(win32con.VK_MENU)

      elif subkey == 'tab':
        ret.append(win32con.VK_TAB)
      
      elif subkey == 'win':
        ret.append(win32con.VK_LWIN)

      elif subkey in string.ascii_uppercase:
        ret.append(ord(subkey))
      
      elif subkey[-1] == 's' and subkey[:-1].replace('.', '').isdigit():
        try:
          hold_time = float(subkey[:-1])
        except ValueError:
          self._print(f"Invalid hold time: {subkey}")

      else:
        self._print("How should I encode " + subkey + '?!')
        # assert False

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


def trim_buffer(buffer: list[str]) -> None:
  while len(buffer) > 1 and buffer[-1][0] == buffer[-2][0]:
    n1 = buffer[-1][1:]
    if n1 == '\'': n1 = 3
    elif n1 != '': n1 = int(n1)
    else: n1 = 1
    del buffer[-1]
    
    n2 = buffer[-1][1:]
    if n2 == '\'': n2 = 3
    elif n2 != '': n2 = int(n2)
    else: n2 = 1

    n2 = (n1 + n2) % 4

    if n2 == 0:
      del buffer[-1]
    elif n2 == 1:
      buffer[-1] = buffer[-1][0]
    elif n2 == 2:
      buffer[-1] = buffer[-1][0] + '2'
    else:  # n2 == 3
      buffer[-1] = buffer[-1][0] + '\''

  if len(buffer) > MAX_BUFFER_SIZE:
    del buffer[:-MAX_BUFFER_SIZE]


def main():
  print('[KeyEmlater]: Starting...')
  binds = upload_binds()
  key_emulator = KeyEmulator(binds)

  pipe = PipeReader()
  pipe.connect()

  buffer: list[str] = []  # global buffer of moves

  while True:
    if pipe.read(buffer):
      trim_buffer(buffer)
      key_emulator.process_buffer(buffer)
      print('[KeyEmlator]: current buffer - ', buffer)


if __name__ == "__main__":
  main()