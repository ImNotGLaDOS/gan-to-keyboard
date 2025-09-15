import asyncio
from time import sleep
from copy import deepcopy
from bleak import BleakScanner, BleakClient

from cube_turner import CubeTurner
from named_pipes import PipeSender
from cryptor import Cryptor



# Cube UUID (for GAN12 ui Maglev. You can try use uuids_finder.py to find your cube's uuids)
GAN_NOTIFY_CHARACTERISTIC_UUID = "0000fff6-0000-1000-8000-00805f9b34fb"
GAN_WRITE_CHARACTERISTIC_UUID = "0000fff5-0000-1000-8000-00805f9b34fb"

# All 18 possible moves (Clockwise, Counter-Clockwise, Double)
ALL_MOVES = [face + mod for face in "URFDLB" for mod in ["", "'", "2"]]



class GANCubeController:
  def _print(self, *text) -> None:
    print("[Controller]: ", *text)


  def __init__(self, pipe: PipeSender):
    self.client = None
    self.connected = False
    self.pipe = pipe

    # Initialize state to the solved state [corners, edges]
    self.state = CubeTurner()
    self.last_state = None


  async def connect_to_cube(self):
    devices = None
    self._print("Searching for GAN Smart Cube...")
    devices = await BleakScanner.discover(timeout=5.0)
    # self._print(f'Found devices: {devices}')
    devices = [device for device in devices if device.name and 'GAN' in device.name]
    if not devices:
      wait_time = 2
      self._print(f'Cube not found. It should blink white. Try do (U4)x5')
      self._print(f'Trying again in {wait_time} seconds')
      sleep(wait_time)
      return await self.connect_to_cube()

    self._print(f"Found {devices[0].name}. Connecting...")
    self.client = BleakClient(devices[0].address)
    self.cryptor = Cryptor(devices[0].address)
    await self.client.connect()
    
    # Subscribe to notifications for cube state
    await self.client.start_notify(GAN_NOTIFY_CHARACTERISTIC_UUID, self._notification_handler)
    
    # Request the initial state from the cube
    await self.client.write_gatt_char(GAN_WRITE_CHARACTERISTIC_UUID, self.cryptor.encrypt(b'\x05' + b'\x00' * 19), response=True)

    self.connected = True
    self._print(f"Connected to {devices[0].name} ({devices[0].address})")
    return True
  

  def _notification_handler(self, sender, data: bytearray):
    data = bytearray(self.cryptor.decrypt(data))
    
    try:
      if data[0] == 0x01:  # Last move in notation
        move = self._parce_move(data)
        self.pipe.send([move])
        self.state.apply_moves(move)
    
      elif data[0] == 0xed:  # State as {cp, co, ep, eo}
        current_state = self._parse_cube_data(data)
        if current_state != self.state:
          self._print('Missed some turns!!!')
        self.last_state = current_state

        # Guessing moves independed from notation-move data
        # if self.last_state:
        #   moves = self._guess_moves(self.last_state, current_state)
        #   if moves:
            # self._print(f"guessed move(s): {' '.join(moves)}")
            # self.pipe.send(moves)
        #     pass
      
      else:
        # self._print(f'Got unknown notification: {data.hex()}')
        pass
        
    except Exception as e:
      self._print(f"Error processing cube data: {e}")


  def _parce_move(self, data):
    array = ''.join(format(byte, '08b') for byte in data)
    def getBitWord(array, start, length):
      return array[start: start + length]
    
    direction = getBitWord(array, 64, 2)[1] == '1'
    face = [1, 5, 3, 0, 4, 2][getBitWord(array, 66, 6).find('1')]
    
    return ('BRDFUL'[face] + ' \''[direction]).replace(' ', '')


  def _parse_cube_data(self, data: bytearray) -> CubeTurner:
    """Parses the 20-byte data packet from the GAN cube into a state array."""
    array = ''.join(format(byte, '08b') for byte in data)
    def getBitWord(array, start, length):
      return array[start: start + length]
    
    # self._print(f'last serial: {int(getBitWord(array, 16, 16), 2)}')

    cp = [int(getBitWord(array, 32 + i * 3, 3), 2) for i in range(7)]
    cp.append(28 - sum(cp))

    co = [int(getBitWord(array, 53 + i * 2, 2), 2) for i in range(7)]
    co.append((3 - (sum(co) % 3)) % 3)

    ep = [int(getBitWord(array, 69 + i * 4, 4), 2) for i in range(11)]
    ep.append(66 - sum(ep))

    eo = [int(getBitWord(array, 113 + i, 1), 2) for i in range(11)]
    eo.append((2 - (sum(eo) % 2)) % 2)

    state = {'cp': cp, 'co': co, 'ep': ep, 'eo': eo}
    orig = CubeTurner(scramble='R')
    return CubeTurner(init_state=state)
    

  def _guess_moves(self, old_state: CubeTurner, new_state: CubeTurner) -> list[str]:
    """
    Compares two cube states to find the move that transformed the old state
    into the new one.
    """
    if old_state.state == new_state.state:
      return []

    # Test every possible single move
    for move in ALL_MOVES:
      # Apply the test move to the old state
      predicted_state = deepcopy(old_state)  # Is deepcopy nessesary?
      predicted_state.apply_moves(move)
      # If the result matches the new state, we found our move
      if predicted_state.state == new_state.state:
        return [move]
    
    # Test every possible pair of moves
    for move_1 in ALL_MOVES:
      for move_2 in ALL_MOVES:
        if move_1[0] == move_2[0]:
          continue  # Cancelling out
        predicted_state = deepcopy(old_state)  # Is deepcopy nessesary?
        predicted_state.apply_moves(move_1)
        predicted_state.apply_moves(move_2)
        if predicted_state.state == new_state.state:
          return [move_1, move_2]

    # Something else?
    return 'not_guessed'
  


def _print(*args):
  print("[CubeScript]: ", *args)



async def main():
  pipe = PipeSender()
  pipe.connect()

  controller = GANCubeController(pipe)
  
  try:
    if not await controller.connect_to_cube():
      return
    _print("Cube connected. Waiting for moves... Press Ctrl+C to exit.")
    # await controller.client.write_gatt_char(GAN_WRITE_CHARACTERISTIC_UUID, Encrypt(b'\xd2\x0d\x05\x39\x77\x00\x00\x01\x23\x45\x67\x89\xab\x00\x00\x00\x00\x00\x00\x00'))
    # _print("Reseted.")

    # Keep the script alive while connected
    while controller.connected and controller.client.is_connected:
      # await controller.client.write_gatt_char(GAN_WRITE_CHARACTERISTIC_UUID, Encrypt(b'\xdf\x03' + b'\x00' * 18), response=True)
      await asyncio.sleep(1)
          
  except KeyboardInterrupt:
    _print("\nDisconnecting...")

  except Exception as e:
    _print(f"An error occurred: {e}")

  finally:
    if controller.client and controller.client.is_connected:
      await controller.client.disconnect()
      _print("Disconnected from cube.")


if __name__ == "__main__":
  asyncio.run(main())