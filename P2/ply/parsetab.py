
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.8'

_lr_method = 'LALR'

_lr_signature = '3FF43A3631BDD47AD5F3ED19F7F962F1'
    
_lr_action_items = {'UNION':([1,3,4,5,7,8,9,10,11,12,],[6,-1,-5,-3,6,-8,-4,-6,-2,-7,]),'$end':([1,3,4,5,8,9,10,11,12,],[0,-1,-5,-3,-8,-4,-6,-2,-7,]),'LPAREN':([0,2,3,4,5,6,8,9,10,11,12,],[2,2,2,-5,-3,2,-8,-4,-6,2,-7,]),'STAR':([4,5,8,9,10,12,],[-5,10,-8,10,-6,-7,]),'RPAREN':([2,3,4,5,7,8,9,10,11,12,],[8,-1,-5,-3,12,-8,-4,-6,-2,-7,]),'CHAR':([0,2,3,4,5,6,8,9,10,11,12,],[4,4,4,-5,-3,4,-8,-4,-6,4,-7,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'chunk':([0,2,6,],[3,3,11,]),'term':([0,2,3,6,11,],[5,5,9,5,9,]),'expr':([0,2,],[1,7,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> expr","S'",1,None,None,None),
  ('expr -> chunk','expr',1,'p_expr_chunk','P2.py',60),
  ('expr -> expr UNION chunk','expr',3,'p_expr_union','P2.py',63),
  ('chunk -> term','chunk',1,'p_chunk_term','P2.py',67),
  ('chunk -> chunk term','chunk',2,'p_chunk_concat','P2.py',70),
  ('term -> CHAR','term',1,'p_term_char','P2.py',74),
  ('term -> term STAR','term',2,'p_term_star','P2.py',77),
  ('term -> LPAREN expr RPAREN','term',3,'p_term_group','P2.py',80),
  ('term -> LPAREN RPAREN','term',2,'p_term_epsilon','P2.py',84),
]