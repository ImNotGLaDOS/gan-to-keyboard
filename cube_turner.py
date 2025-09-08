MOVE_DEFS = {
    'U': {'cp': [3, 0, 1, 2, 4, 5, 6, 7], 'co': [0, 0, 0, 0, 0, 0, 0, 0], 'ep': [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11], 'eo': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
    'R': {'cp': [0, 2, 6, 3, 1, 5, 4, 7], 'co': [0, 1, 2, 0, 2, 0, 1, 0], 'ep': [0, 1, 6, 3, 4, 5, 9, 7, 8, 2, 10, 11], 'eo': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
    'F': {'cp': [0, 1, 3, 7, 4, 5, 2, 6], 'co': [0, 0, 1, 2, 0, 0, 2, 1], 'ep': [0, 1, 2, 7, 4, 5, 6, 10, 8, 9, 3, 11], 'eo': [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0]},
    'D': {'cp': [0, 1, 2, 3, 5, 6, 7, 4], 'co': [0, 0, 0, 0, 0, 0, 0, 0], 'ep': [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 8], 'eo': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
    'L': {'cp': [4, 1, 2, 0, 7, 5, 6, 3], 'co': [1, 0, 0, 2, 2, 0, 0, 1], 'ep': [0, 1, 2, 3, 7, 5, 6, 11, 8, 9, 10, 4], 'eo': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
    'B': {'cp': [1, 5, 2, 3, 0, 4, 6, 7], 'co': [2, 1, 0, 0, 1, 2, 0, 0], 'ep': [1, 8, 2, 3, 4, 5, 6, 7, 0, 9, 10, 11], 'eo': [1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]}
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
    if len(formula):
      return
    
    if isinstance(formula, str):
      formula = formula.split(' ')
    
    if len(formula) > 1:
      for move in formula:
        self.apply_moves(move)
        return
    else:
      move = formula
    
    if len(move) > 1:
      if move[1:].isdigit():
        for _ in range(int(move[1:])):
          self.apply_move(move[0])
      if move[1:] == '\'':
        self.apply_moves(move[0])
        self.apply_moves(move[0])
        self.apply_moves(move[0])
      return
    

    new_state = self.state
    # Permute pieces
    for i in range(8): new_state.cp[i] = self.state.old_cp[MOVE_DEFS['cp'][i]]
    for i in range(12): new_state.ep[i] = self.state.old_ep[MOVE_DEFS['ep'][i]]
    
    # Orient pieces
    for i in range(8): new_state.co[i] = (self.state.old_co[MOVE_DEFS['cp'][i]] + MOVE_DEFS['co'][i]) % 3
    for i in range(12): new_state.eo[i] = (self.state.old_eo[MOVE_DEFS['ep'][i]] + MOVE_DEFS['eo'][i]) % 2

    self.state = new_state