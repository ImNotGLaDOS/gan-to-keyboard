import logging


logger = logging.getLogger('Bind_Uploader')

def upload_binds() -> tuple[ dict[tuple[str], list[list[str]]], dict[str, any] ]:
  """
  loads binds from binds.txt
  ret: dict[<formula>, [<key bind>, ...]], dict{'delete_mode': 'flush/postfix/keep', 'idle_time': float}
  """
  ret: dict[tuple[str], str] = {}
  constants = {
    'delete_mode': 'flush',
    'idle_time': 10,
    'x_sens': 0,
    'y_sens': 0
  }

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
        name, value = bind[1:].strip().split(maxsplit=1)
        name = name.casefold()
        value = value.casefold()


        if name == 'deletion':
          if value not in ['keep', 'postfix', 'flush']:
            logger.warning(f'Not valid delete_mode: "{bind}"')
          else: constants['delete_mode'] = value
        

        elif name == 'idle_time':
          try:
            value = float(value)
            constants[name] = value
          except ValueError:
            logger.warning(f'Not valid idle_time: "{bind}"')


        elif name.startswith('sens'):
          if value.startswith('x '):
            value = value[2:].strip()
            try: 
              value = float(value)
              constants['x_sens'] = value
            except ValueError:
              logger.warning(f'Not valid sensivity: "{bind}"')

          elif value.startswith('y '):
            value = value[2:].strip()
            try: 
              value = float(value)
              constants['y_sens'] = value
            except ValueError:
              logger.warning(f'Not valid sensivity: "{bind}"')
          
          else:  # Setting both
            try: 
              value = float(value)
              constants['x_sens'] = value
              constants['y_sens'] = value
            except ValueError:
              logger.warning(f'Not valid sensivity: "{bind}"')
        
        else:
          logger.warning(f'Unknown constant: {bind}')
        
        continue  # End of commands
      
      # Regular binds
      if bind.count('-') != 1:
        logger.warning(f'Unreadable bind: "{bind}"')
        
      bind = bind.split('-')
      formula: list[str] = bind[0].strip().split()  # example: ['L', 'R\'', 'U2']
      keys_list: list[str] = bind[1].strip().split()  # ['ctrl+U', '0.5s', 'alt+tab']
      keys_list = [comb.split('+') for comb in keys_list]  # [['ctrl', 'U'], ['0.5s'], ['alt', 'tab']]

      ret[tuple(formula)] = keys_list
  
  ret_repr = '\n'.join([repr(bind) for bind in ret.items()])
  logger.info(f'Readed binds:\n{ret_repr}')
  logger.debug(f'Readed constants:\n{constants}')
  return ret, constants
