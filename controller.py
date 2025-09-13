import asyncio
from time import sleep
from copy import deepcopy
from bleak import BleakScanner, BleakClient

from cube_turner import CubeTurner
from named_pipes import PipeSender

from cryptor import Encrypt, Decrypt

"""
# Service and characteristic UUIDs for GAN cubes
GAN_SERVICE_UUID = "00001800-0000-1000-8000-00805f9b34fb"
GAN_CHARACTERISTIC_UUID = "8ec90003-f315-4f60-9fb8-838830daea50" # For receiving cube state
# GAN_CHARACTERISTIC_UUID = "00002a04-0000-1000-8000-00805f9b34fb" # For receiving cube state
GAN_WRITE_SERVICE_UUID = "00000010-0000-fff7-fff6-fff5fff4fff0"
char_n = 7
GAN_WRITE_CHARACTERISTIC_UUID = f"0000fff{char_n}-0000-1000-8000-00805f9b34fb" # For sending commands (like requesting state)
# GAN_WRITE_CHARACTERISTIC_UUID = f"00002aa6-0000-1000-8000-00805f9b34fb" # For sending commands (like requesting state)
# 0000fff<4-7>-...
"""
# GAN_SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
GAN_NOTIFY_CHARACTERISTIC_UUID = "0000fff6-0000-1000-8000-00805f9b34fb"
# GAN_NOTIFY_CHARACTERISTIC_UUID = "8ec90003-f315-4f60-9fb8-838830daea50"
GAN_WRITE_CHARACTERISTIC_UUID = "0000fff5-0000-1000-8000-00805f9b34fb"
# GAN_WRITE_CHARACTERISTIC_UUID = "8ec90003-f315-4f60-9fb8-838830daea50"

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
    self._print(f'Found devices: {devices}')
    devices = [device for device in devices if device.name and 'GAN' in device.name]
    if not devices:
      wait_time = 2
      self._print(f'Cube not found. Trying again in {wait_time} seconds')
      sleep(wait_time)
      return await self.connect_to_cube()


    self._print(f"Found {devices[0].name}. Connecting...")
    self.client = BleakClient(devices[0].address)
    await self.client.connect()
    
    # Subscribe to notifications for cube state
    await self.client.start_notify(GAN_NOTIFY_CHARACTERISTIC_UUID, self._notification_handler)
    
    # Request the initial state from the cube
    await self.client.write_gatt_char(GAN_WRITE_CHARACTERISTIC_UUID, Encrypt(b'\x05' + b'\x00' * 19), response=True)

    self.connected = True
    self._print(f"Connected to {devices[0].name} ({devices[0].address})")
    return True
  

  def _notification_handler(self, sender, data: bytearray):
    data = bytearray(Decrypt(data))
    # self._print(f'Got notification: {data.hex()}')
    if data[0] != 0xed:
      if data[0] == 0x01:
        move = self._parce_move(data)
        # self._print(f'!!!!Got move: {move}')
        self.pipe.send(move)
      return
    
    return  #!!!!!!!!!!!!!!!!!!!!!!!
    self._print(f'Got state: {data.hex()}')
    
    try:
      # Parse the new state from the raw byte data
      current_state = self._parse_cube_data(data)
      
      # If there is a previous state, detect the move made
      if self.last_state:
        moves = self._detect_moves(self.last_state, current_state)
        if moves:
          self._print(f"Detected move(s): {' '.join(moves)}")
          self.pipe.send(moves)
              
      # Update the last known state
      self.last_state = current_state
        
    except Exception as e:
      self._print(f"Error processing cube data: {e}")
  

  def _parce_move(self, data):
    array = ''.join(format(byte, '08b') for byte in data)
    def getBitWord(array, start, length):
      return array[start: start + length]
    
    direction = getBitWord(array, 64, 2)[1] == '1'
    face = [1, 5, 3, 0, 4, 2][getBitWord(array, 66, 6).find('1')]
    
    return 'BRDFUL'[face] + ' \''[direction]


  def _parse_cube_data(self, data: bytearray) -> CubeTurner:
    """Parses the 20-byte data packet from the GAN cube into a state array."""
    """
    # Corner Permutation: 8 bytes, values 0-7
    cp = list(data[0:7])

    # Edge Permutation: 12 half-bytes, values 0-11
    ep = [(data[8] >> 4), (data[8] & 0x0f), (data[9] >> 4), (data[9] & 0x0f),
          (data[10] >> 4), (data[10] & 0x0f), (data[11] >> 4), (data[11] & 0x0f),
          (data[12] >> 4), (data[12] & 0x0f), (data[13] >> 4), (data[13] & 0x0f)]
    
    # Corner Orientation: 8 three-bit values packed into 3 bytes
    co_raw = (data[14] << 16) | (data[15] << 8) | data[16]
    co = [(co_raw >> (3 * (7 - i))) & 0x07 for i in range(8)]

    # Edge Orientation: 12 two-bit values packed into 3 bytes
    eo_raw = (data[14] << 16) | (data[15] << 8) | data[17] # Note: Uses byte 17
    eo = [(eo_raw >> (2 * (11 - i))) & 0x03 for i in range(12)]
    """
    array = ''.join(format(byte, '08b') for byte in data)
    def getBitWord(array, start, length):
      return array[start: start + length]
    
    self._print(f'last serial: {int(getBitWord(array, 16, 16), 2)}')

    cp = [int(getBitWord(array, 32 + i * 3, 3), 2) for i in range(7)]
    cp.append(28 - sum(cp))

    co = [int(getBitWord(array, 53 + i * 2, 2), 2) for i in range(7)]
    co.append((3 - (sum(co) % 3)) % 3)

    ep = [int(getBitWord(array, 69 + i * 4, 4), 2) for i in range(11)]
    ep.append(66 - sum(ep))

    eo = [int(getBitWord(array, 113 + i, 1), 2) for i in range(11)]
    eo.append((2 - (sum(co) % 2)) % 2)

    state = {'cp': cp, 'co': co, 'ep': ep, 'eo': eo}
    orig = CubeTurner(scramble='R')
    self._print('State built')
    if state != orig.state:
      self._print(f'Current state is: {state}')
      self._print(f'Needed state is: {orig.state}')
    return CubeTurner(init_state=state)
    


  def _detect_moves(self, old_state: CubeTurner, new_state: CubeTurner) -> list[str]:
    """
    Compares two cube states to find the move that transformed the old state
    into the new one.
    """
    if old_state.state == new_state.state:
      return []

    # Test every possible single move
    for move in ALL_MOVES:
      # Apply the test move to the old state
      predicted_state = deepcopy(old_state)  # Is nessesary?
      predicted_state.apply_moves(move)
      # If the result matches the new state, we found our move
      if predicted_state.state == new_state.state:
        return [move]
    
    # Something else?
    return []
  


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
    controller.client.write_gatt_char(GAN_WRITE_CHARACTERISTIC_UUID, Encrypt(b'\xd2\x0d\x05\x39\x77\x00\x00\x01\x23\x45\x67\x89\xab\x00\x00\x00\x00\x00\x00\x00'))
    _print("Reseted.")
    # _print(f'Cube\'s services: {controller.client.services}')
    # _print(f'Service\'s uuid: {[i for i in controller.client.services][0].uuid}')
    # _print(f'Service\'s characteristics: {[char.uuid for char in [i for i in controller.client.services][0].characteristics]}')

    # Keep the script alive while connected
    while controller.connected and controller.client.is_connected:
      await controller.client.write_gatt_char(GAN_WRITE_CHARACTERISTIC_UUID, Encrypt(b'\xdf\x03' + b'\x00' * 18), response=True)
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