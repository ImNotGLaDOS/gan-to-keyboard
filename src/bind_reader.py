import logging


logger = logging.getLogger('Bind_Uploader')

def upload_binds() -> tuple[ dict[tuple[str], str], dict[str, any] ]:
  """
  loads binds from binds.txt
  ret: dict[<formula>, <key bind>], dict{'delete_mode': 'flush/postfix/keep', 'idle_time': float}
  """
  ret: dict[tuple[str], str] = {}
  constants = {'delete_mode': 'flush', 'idle_time': 10}
  with open('binds.txt') as file:
    binds = file.read()

    for bind in binds.split('\n'):
      # Empty line check
      if bind.strip() == '':
        continue

      # Deleting comments
      if bind.count('#') > 0:
        bind = bind[:bind.find('#')]
        if bind.strip() == '':
          continue
      
      # Commands
      if bind[0] == '!':
        if len(bind[1:].strip().split()) != 2:
          logger.warning(f'Not valid setting line: "{bind}"')

        name, value = bind[1:].strip().split()
        name = name.casefold()
        value = value.casefold()

        if name == 'deletion':
          if value not in ['keep', 'postfix', 'flush']:
            logger.warning(f'Not valid delete_mode: "{bind}"')
          else: constants[name] = value
        
        elif name == 'idle_time':
          try:
            value = float(value)
            constants[name] = value
          except ValueError:
            logger.warning(f'Not valid idle_time: "{bind}"')

        continue
      
      # Regular binds
      if bind.count('-') != 1:
        logger.warning(f'Unreadable bind: "{bind}"')
        
      bind = bind.split('-')
      formula: list[str] = bind[0].strip().split()  # example: ['L', 'R\'', 'U2']
      key: list[str] = bind[1].strip().replace(' ', '').split('+')  # ['ctrl', 'R', '0.5s']

      ret[tuple(formula)] = key
  
  logger.info(f'Readed binds: {ret}')
  return ret, constants
