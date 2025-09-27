import win32pipe, win32file
import logging
from time import sleep

class PipeSender:
  def __init__(self, pipe_name='turns'):
    self.pipe_name = '\\\\.\\pipe\\' + pipe_name
    self.pipe = None

    self.logger = logging.getLogger('PipeSender ' + pipe_name)


  def connect(self):
    self.logger.debug(f"Connecting to pipe...")

    # Create the named pipe
    pipe_handle = win32pipe.CreateNamedPipe(
      self.pipe_name,
      win32pipe.PIPE_ACCESS_OUTBOUND,
      win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
      1, 65536, 65536, 0, None)
    
    # This call blocks until a client connects
    win32pipe.ConnectNamedPipe(pipe_handle, None)
    self.pipe = pipe_handle
    self.logger.debug("Pipe client connected.")


  def send(self, data: list[str]) -> None:
    """
    Send data to pipe, separated by ';'
    """
    self.logger.debug(f'Sending moves: {data}')
    if not self.pipe:
      self.logger.critical("Cannot send moves, pipe is not connected.")
      return
    
    data = ( ';'.join(data) + ';' ).encode('utf-8')
    try:
      win32file.WriteFile(self.pipe, data)
    except Exception as e:
      self.logger.critical(f"Failed to write to pipe: {e}")
      self.pipe = None
  

  def __del__(self):
    win32file.CloseHandle(self.pipe)



class PipeReader:
  def __init__(self, pipe_name='turns'):
    self.pipe_name = '\\\\.\\pipe\\' + pipe_name
    self.pipe = None

    self.logger = logging.getLogger('PipeReader' + pipe_name)


  def connect(self):
    self.logger.debug(f"Waiting for a client to connect to pipe {self.pipe_name}...")
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
    self.logger.debug("Pipe client connected.")


  def read(self) -> list[str] | None:
    """
    read new data from pipe
    ret: list of readed data or None
    """
    try:
      if win32pipe.PeekNamedPipe(self.pipe, 0)[1] == 0:
        return None
      data = win32file.ReadFile(self.pipe, 65536)
      data = data[1].decode('utf-8').strip(';').split(';')

      self.logger.debug(f'Read: "{data}"')
      return data
    except win32file.error as e:
      if e.winerror == 232:  # EOF
        self.logger.debug(f'Recieved EOF')
        return False