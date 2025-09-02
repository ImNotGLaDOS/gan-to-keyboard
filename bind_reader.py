def upload_binds() -> dict[tuple[str], str]:
  """
  loads binds from binds.txt
  ret: dict[<formula>, <key bind>]
  """
  ret: dict[tuple[str], str] = {}
  with open('binds.txt') as file:
    binds = file.read()

    for bind in binds.split('\n'):
      if bind.count('#') > 0:  # Deleting comments
        bind = bind[:bind.find('#')]
      
      bind = bind.split('-')
      formula: list[str] = bind[0].strip().split(' ')  # example: ['L', 'R\'', 'U2']
      key: list[str] = bind[1].strip().replace(' ', '').split('+')  # ['ctrl', 'R', '0.5s']

      ret[tuple(formula)] = key
  return ret