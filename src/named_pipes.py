import win32pipe, win32file
from time import sleep

class PipeSender:
  def __init__(self, pipe_name='\\\\.\\pipe\\Turns'):
    self.pipe_name = pipe_name
    self.pipe = None


  def _print(self, *text) -> None:
    print("[PipeSender]: ", *text)


  def connect(self):
    self._print(f"Waiting for a client to connect to pipe {self.pipe_name}...")

    # Create the named pipe
    pipe_handle = win32pipe.CreateNamedPipe(
      self.pipe_name,
      win32pipe.PIPE_ACCESS_OUTBOUND,
      win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
      1, 65536, 65536, 0, None)
    
    # This call blocks until a client connects
    win32pipe.ConnectNamedPipe(pipe_handle, None)
    self.pipe = pipe_handle
    self._print("Pipe client connected.")


  def send(self, moves: list[str]) -> None:
    # self._print('Sending moves:', moves)
    if not self.pipe:
      self._print("Cannot send moves, pipe is not connected.")
      return
    
    data = ( ';'.join(moves) + ';' ).encode('utf-8')
    try:
      win32file.WriteFile(self.pipe, data)
    except Exception as e:
      self._print(f"Failed to write to pipe: {e}")
      # Potentially handle pipe disconnection here
      self.pipe = None
  

  def __del__(self):
    win32file.CloseHandle(self.pipe)



class PipeReader:
  def __init__(self, pipe_name='\\\\.\\pipe\\Turns'):
    self.pipe_name = pipe_name
    self.pipe = None


  def _print(self, *text) -> None:
    print("[PipeReader]: ", *text)


  def connect(self):
    self._print(f"Waiting for a client to connect to pipe {self.pipe_name}...")
    sleep(2)  # Wait for the pipe to be created
    
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
      data = data[1].decode('utf-8').strip(';').split(';')
      # data = ''.join(data)
      buffer.extend(data)
      # self._print(f'Read: "{data}"')
      return True
    except win32file.error as e:
      if e.winerror == 232:  # EOF
        return False