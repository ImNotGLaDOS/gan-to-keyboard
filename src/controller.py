import sys
sys.coinit_flags = 0  # MTA thread mode

import asyncio
from bleak import BleakScanner, BleakClient
import logging

from named_pipes import PipeSender
from cryptor import Cryptor
from uuids_list import UUIDS_LIST



async def _choose_protocol(client: BleakClient) -> tuple[str, str]:
  uuids_list = []
  for service in client.services:
    for char in service.characteristics:
      uuids_list.append(char.uuid)
  
  for gen in 'Gen2', 'Gen3', 'Gen4':
    if UUIDS_LIST[gen]['notify'] in uuids_list:
      return gen
  
  return None



class GANCubeController:
  def __init__(self, send):
    """
    send(moves: list[str]) -> None.
    send(moves) called when controller wants to send list of recieved moves
    """
    self.logger = logging.getLogger('Controller')

    self.client = None
    self.send = send

    self.protocol = None  # Gen2, Gen3, Gen4
    self.move_count = None


  async def connect_to_cube(self):
    # Scanning for devices
    self.logger.info("Searching for GAN Smart Cube...")
    devices = await BleakScanner.discover(timeout=5.0)
    gan_devices = [device for device in devices if device.name and 'GAN' in device.name]
    if not gan_devices:
      if not devices:
        self.logger.critical('Couldn\'t find any device. Most likely, something wrong with bluetooth.')
      else:
        self.logger.warning('Couldn\'t find the cube, but the bluetooth is working.')
      return False

    # Connecting
    self.logger.info(f"Found {gan_devices[0].name}. Connecting...")
    self.client = BleakClient(gan_devices[0])
    await self.client.connect()
    self.logger.info(f"Connected to {gan_devices[0].name} ({gan_devices[0].address}).")

    # Choosing right protocol
    self.protocol = await _choose_protocol(self.client)
    if not self.protocol:
      self.logger.critical("Unknown protocol. Disconnecting...")
      await self.client.disconnect()
      return False
    else:
      self.logger.debug(f'Choosed protocol: {self.protocol}')
      self.NOTIFY_UUID = UUIDS_LIST[self.protocol]['notify']
      self.WRITE_UUID = UUIDS_LIST[self.protocol]['write']
      
    self.cryptor = Cryptor(gan_devices[0].address)
    
    # Subscribe to notifications
    if self.protocol == 'Gen2':
      await self.client.start_notify(self.NOTIFY_UUID, self._notification_handler_gen2)
      # Request the initial state from the cube. For gen2 it's necessary
      await self.client.write_gatt_char(self.WRITE_UUID, self.cryptor.encrypt(b'\x04' + b'\x00' * 19), response=True)

    elif self.protocol == 'Gen3':
      await self.client.start_notify(self.NOTIFY_UUID, self._notification_handler_gen3)
      # Request the initial state from the cube
      await self.client.write_gatt_char(self.WRITE_UUID, self.cryptor.encrypt(b'\x68' + b'\x01' + b'\x00' * 18), response=True)

    else:  # self.protocol == 'Gen4'
      await self.client.start_notify(self.NOTIFY_UUID, self._notification_handler_gen4)
      # Request the initial state from the cube
      await self.client.write_gatt_char(self.WRITE_UUID, self.cryptor.encrypt(b'\x05' + b'\x00' * 19), response=True)
    
    
    
    return True
  

  ###########################   Notification handlers   ###########################
  def _notification_handler_gen4(self, sender, data: bytearray):
    data = bytearray(self.cryptor.decrypt(data))
    
    try:
      if data[0] == 0x01:  # Last move in notation
        self.logger.debug(f'Got move data: {data.hex()}')
        move = self._parce_move_gen4(data)
        self.logger.debug(f'Parced move: {move}')
        self.send([move])
      else:
        self.logger.debug(f'Got unknown notification: {data.hex()}')
        
    except Exception as e:
      self.logger.critical(f"Error processing cube data: {e}")


  def _notification_handler_gen3(self, sender, data: bytearray):
    data = bytearray(self.cryptor.decrypt(data))
    
    try:
      if data[0] != 0x55 and data[2] != 0x00:  
        return

      if data[1] == 0x01:  # Last move in notation
        self.logger.debug(f'Got move data: {data.hex()}')
        move = self._parce_moves_gen3(data)
        self.logger.debug(f'Parced move: {move}')
        self.send([move])
      else:
        self.logger.debug(f'Got unknown notification: {data.hex()}')
        
    except Exception as e:
      self.logger.critical(f"Error processing cube data: {e}")


  def _notification_handler_gen2(self, sender, data: bytearray):
    data = bytearray(self.cryptor.decrypt(data))
    self.logger.debug(f'Got notification: {data.hex()}')
    
    try:
      if data[0] >> 4 == 0x02:  # Moves in notation
        self.logger.debug(f'Got move data.')

        if self.move_count is None:  # Can process moves only after getting facelets state
          self.logger.debug('Got moves but don\'t know initial state')
          return
        moves = self._parce_moves_gen2(data)
        if moves:
          self.logger.debug(f'Parced moves: {moves}')
          self.send(moves)

      elif data[0] >> 4 == 0x04:  # Facelets
        self.logger.debug('Got facelets data')
        array = ''.join(format(byte, '08b') for byte in data)
        def getBitWord(array, start, length):
          return array[start: start + length]
        
        self.move_count = int(getBitWord(array, 4, 8), 2)
        pass  # There can be logic of reconstucting facelets

      else:
        self.logger.debug(f'Unknown notification.')
        
    except Exception as e:
      self.logger.warning(f"Error processing cube data: {e}")


  ###########################       Data parcers       ###########################
  def _parce_move_gen4(self, data):
    array = ''.join(format(byte, '08b') for byte in data)
    def getBitWord(array, start, length):
      return array[start: start + length]
    
    direction = getBitWord(array, 64, 2)[1] == '1'
    face = [1, 5, 3, 0, 4, 2][getBitWord(array, 66, 6).find('1')]
    
    return ('BRDFUL'[face] + ' \''[direction]).replace(' ', '')


  def _parce_move_gen3(self, data):
    array = ''.join(format(byte, '08b') for byte in data)
    def getBitWord(array, start, length):
      return array[start: start + length]
    
    direction = getBitWord(array, 72, 2)[1] == '1'
    face = [1, 5, 3, 0, 4, 2][getBitWord(array, 74, 6).find('1')]
    
    return ('BRDFUL'[face] + ' \''[direction]).replace(' ', '')
  

  def _parce_moves_gen2(self, data):
    array = ''.join(format(byte, '08b') for byte in data)
    def getBitWord(array, start, length):
      return array[start: start + length]
    
    move_count = int(getBitWord(array, 4, 8), 2)
    sended_count = min((move_count - self.move_count) & 0xff, 7)  # TODO: move_count suppose to cicle like u_int8 and "& 0xff" is for 255->0 transition. Does it work correctly in Python?
    self.move_count = move_count
    if sended_count <= 0:
      self.logger.warning('Not positive sended_count.')
      return []

    ret = []
    for i in range(sended_count - 1, -1, -1):
      direction = int(getBitWord(array, 16 + 5 * i, 1), 2)
      face = int(getBitWord(array, 12 + 5 * i, 4), 2)
      
      if face > 5:
        self.logger.warning('Reseived corrupted move data (face_mapper > 5)')
        i -= 1
        continue

      move = ('URFDLB'[face] + ' \''[direction]).replace(' ', '')
      ret.append(move)

      i -= 1

    return ret[::-1]  # TODO: Does move send in reverse?



logger = logging.getLogger('CubeScript')

async def main():
  # Configuring logging
  logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
      datefmt='%H:%M:%S'
  )

  pipe = PipeSender()
  pipe.connect()

  controller = GANCubeController(lambda lst: pipe.send(lst))
  
  try:
    while not await controller.connect_to_cube():
      wait_time = 2
      controller.logger.warning('Cube not found. It should blink white.')
      controller.logger.warning('Check that the cube isn\'t connected to your PC. Try do (U4)x5.')
      controller.logger.info(f'Trying again in {wait_time} seconds.\n')
      await asyncio.sleep(wait_time)
    logger.info("Cube connected.")

    # Keep the script alive (forever)
    while True:
      if not controller.client.is_connected:
        logger.critical('Connection lost.')
        return
      await asyncio.sleep(2)
          
  except KeyboardInterrupt:
    logger.info("Keyboard Interrupt. Disconnecting...")

  except Exception as e:
    logger.critical(f"An error occurred: {e}")

  finally:
    if controller.client and controller.client.is_connected:
      await controller.client.disconnect()
    logger.critical("Disconnected from cube.")


if __name__ == "__main__":
  try:
    asyncio.run(main())
  except Exception as e:
    print(f"Fatal error: {e}")
    import traceback
    traceback.print_exc()
  finally:
    logger.debug('Ended.')