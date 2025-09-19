import logging


logger = logging.getLogger('Bind_Uploader')

def upload_binds() -> tuple[ dict[tuple[str], str], str ]:
  """
  loads binds from binds.txt
  ret: dict[<formula>, <key bind>], DELETE_MODE ['keep', 'postfix', 'flush']
  """
  ret: dict[tuple[str], str] = {}
  DELETE_MODE = 'flush'
  with open('binds.txt') as file:
    binds = file.read()

    for bind in binds.split('\n'):
      # Deleting comments
      if bind.count('#') > 0:
        bind = bind[:bind.find('#')]
        if bind.strip() == '':
          continue
      
      if bind[0] == '!':
        bind = bind[1:].strip()
        if bind not in ['keep', 'postfix', 'flush']:
          logger.warning(f'Not valid delete_mode: {bind}')
        else: DELETE_MODE = bind
        continue
      
      if bind.count('-') != 1:
        logger.warning(f'Unreadable bind: {bind}')
        
      bind = bind.split('-')
      formula: list[str] = bind[0].strip().split()  # example: ['L', 'R\'', 'U2']
      key: list[str] = bind[1].strip().replace(' ', '').split('+')  # ['ctrl', 'R', '0.5s']

      ret[tuple(formula)] = key
  
  logger.info(f'Readed binds: {ret}')
  logger.info(f'Deletion mode: {DELETE_MODE}')
  return ret, DELETE_MODE
