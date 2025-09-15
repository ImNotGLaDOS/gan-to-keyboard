from copy import deepcopy


MOVE_DEFS = {
    'U': {'cp': [3, 0, 1, 2, 4, 5, 6, 7], 'co': [0, 0, 0, 0, 0, 0, 0, 0], 'ep': [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11], 'eo': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
    'R': {'cp': [4, 1, 2, 0, 7, 5, 6, 3], 'co': [2, 0, 0, 1, 1, 0, 0, 2], 'ep': [8, 1, 2, 3, 11, 5, 6, 7, 4, 9, 10, 0], 'eo': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
    'F': {'cp': [1, 5, 2, 3, 0, 4, 6, 7], 'co': [1, 2, 0, 0, 2, 1, 0, 0], 'ep': [0, 9, 2, 3, 4, 8, 6, 7, 1, 5, 10, 11], 'eo': [0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0]},
    'D': {'cp': [0, 1, 2, 3, 5, 6, 7, 4], 'co': [0, 0, 0, 0, 0, 0, 0, 0], 'ep': [0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11], 'eo': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
    'L': {'cp': [0, 2, 6, 3, 4, 1, 5, 7], 'co': [0, 1, 2, 0, 0, 2, 1, 0], 'ep': [0, 1, 10, 3, 4, 5, 9, 7, 8, 2, 6, 11], 'eo': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
    'B': {'cp': [0, 1, 3, 7, 4, 5, 2, 6], 'co': [0, 0, 1, 2, 0, 0, 2, 1], 'ep': [0, 1, 2, 11, 4, 5, 6, 10, 8, 9, 3, 7], 'eo': [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1]}
}


class CubeTurner:
  def __init__(self, scramble='', init_state=None):
    if init_state is None:
      self.state = {'cp': [0, 1, 2, 3, 4, 5, 6, 7],                # Corner Permutation
                    'co': [0, 0, 0, 0, 0, 0, 0, 0],                # Corner Orientation
                    'ep': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],  # Edge   Permutation
                    'eo': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}    # Edge   Orientation
    else:
      self.state = init_state

    if scramble != '':
      self.apply_moves(scramble)
  

  def apply_moves(self, formula: str | list[str] =''):
    if len(formula) == 0:
      return
    
    if isinstance(formula, str):
      formula = formula.split(' ')
    
    if len(formula) > 1:
      for move in formula:
        self.apply_moves(move)
        return
    else:
      move = formula[0]
    
    if len(move) > 1:
      if move[1:].isdigit():
        for _ in range(int(move[1:])):
          self.apply_moves(move[0])
      if move[1:] == '\'':
        self.apply_moves(move[0])
        self.apply_moves(move[0])
        self.apply_moves(move[0])
      return
    

    new_state = deepcopy(self.state)
    # Permute pieces
    for i in range(8): new_state['cp'][i] = self.state['cp'][MOVE_DEFS[move]['cp'][i]]
    for i in range(12): new_state['ep'][i] = self.state['ep'][MOVE_DEFS[move]['ep'][i]]
    
    # Orient pieces
    for i in range(8): new_state['co'][i] = (self.state['co'][MOVE_DEFS[move]['cp'][i]] + MOVE_DEFS[move]['co'][i]) % 3
    for i in range(12): new_state['eo'][i] = (self.state['eo'][MOVE_DEFS[move]['ep'][i]] + MOVE_DEFS[move]['eo'][i]) % 2

    self.state = new_state