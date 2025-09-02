import asyncio
from bleak import BleakScanner, BleakClient

from named_pipes import PipeSender

# Service and characteristic UUIDs for GAN cubes
GAN_SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
GAN_CHARACTERISTIC_UUID = "0000fff6-0000-1000-8000-00805f9b34fb" # For receiving cube state
GAN_WRITE_CHARACTERISTIC_UUID = "0000fff5-0000-1000-8000-00805f9b34fb" # For sending commands (like requesting state)

# Cube move definitions used for state manipulation
# This dictionary maps a move name to how it permutes and orients pieces.
# For example, 'U' cycles corners 0, 1, 2, 3 and edges 0, 1, 2, 3.
MOVE_DEFINITIONS = {
    'U': {'cp': [3, 0, 1, 2, 4, 5, 6, 7], 'co': [0, 0, 0, 0, 0, 0, 0, 0], 'ep': [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11], 'eo': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
    'R': {'cp': [0, 2, 6, 3, 1, 5, 4, 7], 'co': [0, 1, 2, 0, 2, 0, 1, 0], 'ep': [0, 1, 6, 3, 4, 5, 9, 7, 8, 2, 10, 11], 'eo': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
    'F': {'cp': [0, 1, 3, 7, 4, 5, 2, 6], 'co': [0, 0, 1, 2, 0, 0, 2, 1], 'ep': [0, 1, 2, 7, 4, 5, 6, 10, 8, 9, 3, 11], 'eo': [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0]},
    'D': {'cp': [0, 1, 2, 3, 5, 6, 7, 4], 'co': [0, 0, 0, 0, 0, 0, 0, 0], 'ep': [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 8], 'eo': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
    'L': {'cp': [4, 1, 2, 0, 7, 5, 6, 3], 'co': [1, 0, 0, 2, 2, 0, 0, 1], 'ep': [0, 1, 2, 3, 7, 5, 6, 11, 8, 9, 10, 4], 'eo': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
    'B': {'cp': [1, 5, 2, 3, 0, 4, 6, 7], 'co': [2, 1, 0, 0, 1, 2, 0, 0], 'ep': [1, 8, 2, 3, 4, 5, 6, 7, 0, 9, 10, 11], 'eo': [1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]}
}
# All 18 possible moves (Clockwise, Counter-Clockwise, Double)
ALL_MOVES = [face + mod for face in "URFDLB" for mod in ["", "'", "2"]]



class GANCubeController:
  def __init__(self, pipe: PipeSender):
    self.client = None
    self.connected = False
    self.pipe = pipe

    # Initialize state to the solved state [corners, edges]
    self.last_state = [
        [0, 1, 2, 3, 4, 5, 6, 7], # Corner Permutation
        [0, 0, 0, 0, 0, 0, 0, 0], # Corner Orientation
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], # Edge Permutation
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Edge Orientation
    ]


  def _print(*text) -> None:
    print("[PipeSender]: ", *text)


  async def connect_to_cube(self):
    self._print("Searching for GAN Smart Cube...")
    devices = await BleakScanner.discover(service_uuids=[GAN_SERVICE_UUID], timeout=10.0)
    
    if not devices:
      print("No GAN cube found.")
      return False
    
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
  

  def _parse_cube_data(self, data: bytearray) -> list:
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

    return [cp, co, ep, eo]
  

  def _apply_move(self, state: list, move: str) -> list:
    """Applies a single move (e.g., 'U', "R'") to a given cube state."""
    face = move[0]
    mod = move[1:]
    
    new_state = [s[:] for s in state]  # Deep copy

    if mod == '2':
      # Apply the move twice for a double turn
      new_state = self._apply_move(new_state, face)
      new_state = self._apply_move(new_state, face)
      return new_state
    
    if mod == "'":
      # For an inverse move, apply it three times (equivalent to once counter-clockwise)
      new_state = self._apply_move(new_state, face)
      new_state = self._apply_move(new_state, face)
      new_state = self._apply_move(new_state, face)
      return new_state

    # Apply a single clockwise move
    move_def = MOVE_DEFINITIONS[face]
    old_cp, old_co, old_ep, old_eo = state
    new_cp, new_co, new_ep, new_eo = new_state

    # Permute pieces
    for i in range(8): new_cp[i] = old_cp[move_def['cp'][i]]
    for i in range(12): new_ep[i] = old_ep[move_def['ep'][i]]
    
    # Orient pieces
    for i in range(8): new_co[i] = (old_co[move_def['cp'][i]] + move_def['co'][i]) % 3
    for i in range(12): new_eo[i] = (old_eo[move_def['ep'][i]] + move_def['eo'][i]) % 2

    return [new_cp, new_co, new_ep, new_eo]


  def _detect_moves(self, old_state: list, new_state: list) -> list[str]:
    """
    Compares two cube states to find the move that transformed the old state
    into the new one.
    """
    if old_state == new_state:
      return []

    # Test every possible single move
    for move in ALL_MOVES:
      # Apply the test move to the old state
      predicted_state = self._apply_move(old_state, move)
      # If the result matches the new state, we found our move
      if predicted_state == new_state:
        return [move]
    
    # If no single move matches, something else happened (e.g., a slice move or cube slip)
    # A more advanced implementation could detect double moves here.
    return []


def _print(text: str):
  print("[CubeScript]: ", str)


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