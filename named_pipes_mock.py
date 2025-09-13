from time import sleep

class PipeSender:
  def __init__(self, pipe_name='\\\\.\\pipe\\Turns'):
    pass


  def _print(self, *text) -> None:
    print("[PipeSender]: ", *text)


  def connect(self):
    self._print(f"Waiting for a client to connect to pipe...")
    self._print("Pipe client connected.")


  def send(self, moves: list[str]) -> None:
    self._print('Sending moves:', moves)



class PipeReader:
  def __init__(self, pipe_name='\\\\.\\pipe\\Turns'):
    self.pipe_name = pipe_name
    self.pipe = None


  def _print(self, *text) -> None:
    print("[PipeReader]: ", *text)


  def connect(self):
    self._print(f"Waiting for a client to connect to pipe {self.pipe_name}...")
    sleep(0.1)  # Wait for the pipe to be created
    
    # Create the named pipe
    pipe_handle = win32file.CreateFile(
                    self.pipe_name,
                    win32file.GENERIC_READ,
                    0,
                    None,
                    win32file.OPEN_EXISTING,  # Crucial: open existing pipe
                    0,  # Default attributes
                    None
                  )
    
    self.pipe = pipe_handle
    self._print("Pipe client connected.")


  def read(self, buffer: list[str]) -> bool:
    """
    read new data from pipe and append it to buffer
    ret: bool("there is new data")
    """
    try:
      if win32pipe.PeekNamedPipe(self.pipe, 0)[1] == 0:
        return False
      data = win32file.ReadFile(self.pipe, 65536)
      buffer.extend(data[1].decode('utf-8').strip().split(' '))
      self._print('Read:', data[1].decode('utf-8').strip())
      return True
    except win32file.error as e:
      if e.winerror == 232:  # EOF
        return False