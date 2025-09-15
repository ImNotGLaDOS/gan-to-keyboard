import win32con, win32api
import logging, time, string

from bind_reader import upload_binds
from named_pipes import PipeReader


MAX_BUFFER_SIZE = 30
DELETE_MODE = ['flush', 'postfix', 'keep'][2]



class KeyEmulator:
  def __init__(self, bind_list: dict[tuple[str], str]):
    self.logger = logging.getLogger('KeyEmulator')
    self.bind_list = bind_list


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
          del turns[-postfix:]
        elif DELETE_MODE == 'keep':
          pass
        else:
          self.logger.warning(f'Invalid DELETE_MODE: {DELETE_MODE}.')
          # DELETE_MODE = 'flush'

        return ret
    return None
  

  def _key_to_codes(self, key: list[str]) -> tuple[list[int], float]:
    """
    key: key press in format ["ctrl", "A"]
    generate list of codes 'win32con.VK_{}'
    """
    ret: list[tuple[int]] = []
    hold_time: float = 0.01

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

      elif subkey in string.digits:
        ret.append(ord(subkey))
      
      elif subkey[-1] == 's' and subkey[:-1].replace('.', '').isdigit():
        try:
          hold_time = float(subkey[:-1])
        except ValueError:
          self.logger.warning(f"Invalid hold time: {subkey}")

      else:
        self.logger.warning(f'Unrecognisible key: {subkey}')

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

  binds = upload_binds()
  key_emulator = KeyEmulator(binds)

  pipe = PipeReader()
  pipe.connect()

  buffer: list[str] = []  # global buffer of moves

  while True:
    if pipe.read(buffer):
      trim_buffer(buffer)
      key_emulator.process_buffer(buffer)
      logger.info(f'Current buffer (last 10) - {buffer[-10:]}')


if __name__ == "__main__":
  main()