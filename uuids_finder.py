import asyncio
from typing import Set
from bleak import BleakScanner, BleakClient

# The name your cube advertises. "GAN" should be sufficient.
TARGET_NAME = "GAN"

async def main():
  """
  Scans for a BLE device, connects, and lists all services and characteristics.
  """
  print(f"Scanning for BLE devices with a name containing '{TARGET_NAME}'...")
  device = await BleakScanner.find_device_by_name(TARGET_NAME, timeout=5.0)

  if not device:
    print(f"Could not find a device named '{TARGET_NAME}'.")
    print("   Please make sure your cube is charged, awake (it should blink white), and not connected to another device (like your phone). Try to do (U4)x5 or (L4)x5 then relaunch the script")
    return

  print(f"Found device: {device.name} ({device.address}). Connecting")

  try:
    async with BleakClient(device.address) as client:
      if not client.is_connected:
        print(f"Failed to connect to {device.address}")
        return

      print(f"\n\n--- Services and Characteristics for {device.name} ---")
      for service in client.services:
        print(f"\n[Service] UUID: {service.uuid}")
        for char in service.characteristics:
          properties: Set[str] = char.properties
          # This is the most important part: listing the properties
          print(f"  [Characteristic] UUID: {char.uuid}")
          print(f"    Properties: {', '.join(properties)}")

      print("\n--- End of Discovery ---")

  except Exception as e:
    print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
  asyncio.run(main())