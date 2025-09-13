import asyncio
from bleak import BleakScanner, BleakClient

import os
os.execl('pip', 'install bleak')

from cube_turner import CubeTurner
from named_pipes_mock import PipeSender

# Service and characteristic UUIDs for GAN cubes
GAN_SERVICE_UUID = "0000fe56-0000-1000-8000-00805f9b34fb"
GAN_CHARACTERISTIC_UUID = "8ec90003-f315-4f60-9fb8-838830daea50" # For receiving cube state
GAN_WRITE_SERVICE_UUID = "00000010-0000-fff7-fff6-fff5fff4fff0"
GAN_WRITE_CHARACTERISTIC_UUID = "0000fff5-0000-1000-8000-00805f9b34fb" # For sending commands (like requesting state)
# 0000fff<4-7>-...

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


  async def connect_to_cube(self):
    devices = None
    self._print("Searching for GAN Smart Cube...")
    while not devices:
      devices = await BleakScanner.discover(service_uuids=[GAN_SERVICE_UUID, GAN_WRITE_CHARACTERISTIC_UUID], timeout=10.0)
    
    self._print(f"Found {devices[0].name}. Connecting...")
    self.client = BleakClient(devices[0].address)
    await self.client.connect()
    
    # Subscribe to notifications for cube state
    await self.client.start_notify(GAN_CHARACTERISTIC_UUID, self._notification_handler)
    
    # Request the initial state from the cube
    await self.client.write_gatt_char(GAN_WRITE_CHARACTERISTIC_UUID, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', response=True)

    self.connected = True
    self._print(f"Connected to {devices[0].name} ({devices[0].address})")
    return True
  

  def _notification_handler(self, sender, data: bytearray):
    if len(data) != 18:
      return # Not a full state update packet
    
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
  

  def _parse_cube_data(self, data: bytearray) -> CubeTurner:
    """Parses the 18-byte data packet from the GAN cube into a state array."""
    # Corner Permutation: 8 bytes, values 0-7
    cp = list(data[0:8])

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

    return CubeTurner(init_state={'cp': cp, 'co': co, 'ep': ep, 'eo': eo})


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
      predicted_state = old_state
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
    
    # Keep the script alive while connected
    while controller.connected and controller.client.is_connected:
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