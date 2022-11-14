import sys
import ast
import re
import numpy as np
import zipfile
from math import prod
from fickling.pickle import Pickled

if sys.version_info >= (3, 9):
    from ast import unparse
else:
    from astunparse import unparse

NO_PICKLE_DEBUG = True

def extract_weights_from_checkpoint(fb0):
  torch_weights = {}
  torch_weights['state_dict'] = {}
  with zipfile.ZipFile(fb0, 'r') as myzip:
    folder_name = [a for a in myzip.namelist() if a.endswith("/data.pkl")]
    if len(folder_name)== 0:
      raise ValueError("Looks like the checkpoints file is in the wrong format")
    folder_name = folder_name[0].replace("/data.pkl" , "").replace("\\data.pkl" , "")
    with myzip.open(folder_name+'/data.pkl') as myfile:
      load_instructions, special_instructions = examine_pickle(myfile)
      for sd_key,load_instruction in load_instructions.items():
        with myzip.open(folder_name + f'/data/{load_instruction.obj_key}') as myfile:
          if (load_instruction.load_from_file_buffer(myfile)):
            torch_weights['state_dict'][sd_key] = load_instruction.get_data()
      for sd_key,special in special_instructions.items():
        torch_weights['state_dict'][sd_key] = special
  return torch_weights

def examine_pickle(fb0):

  decompiled = unparse(Pickled.load(fb0).ast).splitlines()

## LINES WE CARE ABOUT:
## 1: this defines a data file and what kind of data is in it
##   _var1 = _rebuild_tensor_v2(UNPICKLER.persistent_load(('storage', HalfStorage, '0', 'cpu', 11520)), 0, (320, 4, 3, 3), (36, 9, 3, 1), False, _var0)
##
## 2: this massive line assigns the previous data to dictionary entries  
## _var2262 = {'model.diffusion_model.input_blocks.0.0.weight': _var1, [..... continue for ever]}
##
## 3: this massive line also assigns values to keys, but does so differently
## _var2262.update({ 'cond_stage_model.transformer.text_model.encoder.layers.3.layer_norm2.bias': _var2001, [ .... and on  and on ]})
##
## that's it  
  # make some REs to match the above.
  re_rebuild = re.compile('^_var\d+ = _rebuild_tensor_v2\(UNPICKLER\.persistent_load\(\(.*\)$')
  re_assign = re.compile('^_var\d+ = \{.*\}$')
  re_update = re.compile('^_var\d+\.update\(\{.*\}\)$')
  re_ordered_dict = re.compile('^_var\d+ = OrderedDict\(\)$')

  load_instructions = {}
  assign_instructions = AssignInstructions()

  for line in decompiled:
    ## see if line matches patterns of lines we care about: 
    line = line.strip()
    if re_rebuild.match(line):
      variable_name, load_instruction = line.split(' = ', 1)
      load_instructions[variable_name] = LoadInstruction(line)
    elif re_assign.match(line):
      assign_instructions.parse_assign_line(line)
    elif re_update.match(line):
      assign_instructions.parse_update_line(line)
    elif re_ordered_dict.match(line):
      #do nothing
      continue
    else:
      print(f'unmatched line: {line}')


  if NO_PICKLE_DEBUG:
    print(f"Found {len(load_instructions)} load instructions")

  assign_instructions.integrate(load_instructions)

  #return assign_instructions.integrated_instructions, assign_instructions.special_instructions
  return assign_instructions.integrated_instructions, {}

class AssignInstructions:
  def __init__(self):
    self.instructions = {}
    self.special_instructions = {}
    self.integrated_instructions = {}

  def parse_assign_line(self, line):
    # input looks like this:
    # _var2262 = {'model.diffusion_model.input_blocks.0.0.weight': _var1, 'model.diffusion_model.input_blocks.0.0.bias': _var3,\
    #  ...\
    #  'cond_stage_model.transformer.text_model.encoder.layers.3.layer_norm2.weight': _var1999}
    garbage, huge_mess = line.split(' = {', 1)
    assignments = huge_mess.split(', ')
    del huge_mess
    assignments[-1] = assignments[-1].strip('}')
    re_var = re.compile('^_var\d+$')
    assignment_count
    for a in assignments:
      if self._add_assignment(a, re_var):
        assignment_count = assignment_count + 1
    if NO_PICKLE_DEBUG:
      print(f"Added/merged {assignment_count} assignments. Total of {len(self.instructions)} assignment instructions")

  def _add_assignment(self, assignment, re_var):
    # assignment can look like this:
    # 'cond_stage_model.transformer.text_model.encoder.layers.3.self_attn.out_proj.weight': _var2009
    # or assignment can look like this:
    # 'embedding_manager.embedder.transformer.text_model.encoder.layers.6.mlp.fc1': {'version': 1}
    sd_key, fickling_var = assignment.split(': ', 1)
    sd_key = sd_key.strip("'")
    if re_var.match(fickling_var):
      self.instructions[sd_key] = fickling_var
      return True
    else:
      # now convert the string "{'version': 1}" into a dictionary {'version': 1}
      entries = fickling_var.split(',')
      special_dict = {}
      for e in entries:
        e = e.strip("{}")
        k, v = e.split(': ')
        k = k.strip("'")
        v = v.strip("'")
        special_dict[k] = v
      self.special_instructions[sd_key] = special_dict
      return False

  def integrate(self, load_instructions):
    unfound_keys = {}
    for sd_key, fickling_var in self.instructions.items():
      if fickling_var in load_instructions:
        self.integrated_instructions[sd_key] = load_instructions[fickling_var]
      if sd_key in self.special_instructions:
        if NO_PICKLE_DEBUG:
          print(f"Key found in both load and special instructions: {sd_key}")
      else:
        unfound_keys[sd_key] = True;
    #for sd_key, special in self.special_instructions.items():
    #  if sd_key in unfound_keys:
    #    #todo

    if NO_PICKLE_DEBUG:
      print(f"Have {len(self.integrated_instructions)} integrated load/assignment instructions")

  def parse_update_line(self, line):
    # input looks like:
    # _var2262.update({'cond_stage_model.transformer.text_model.encoder.layers.3.layer_norm2.bias': _var2001,\
    # 'cond_stage_model.transformer.text_model.encoder.layers.4.self_attn.k_proj.weight': _var2003,\
    # ...\
    #'cond_stage_model.transformer.text_model.final_layer_norm.bias': _var2261})
    garbage, huge_mess = line.split('({', 1)
    updates = huge_mess.split(', ')
    del huge_mess
    updates[-1] = updates[-1].strip('})')
    re_var = re.compile('^_var\d+$')
    update_count = 0
    for u in updates:
      if self._add_assignment(u, re_var):
        update_count = update_count + 1
    if NO_PICKLE_DEBUG:
      print(f"Added/merged {update_count} updates. Total of {len(self.instructions)} assignment instructions")

class LoadInstruction:
  def __init__(self, instruction_string):
    self.ident = False
    self.storage_type = False
    self.obj_key = False
    self.location = False #unused
    self.obj_size = False
    self.stride = False #unused
    self.data = False;
    self.parse_instruction(instruction_string)

  def parse_instruction(self, instruction_string):
    ## this function could probably be cleaned up/shortened. 
    
    ## this is the API def for _rebuild_tensor_v2:
    ## _rebuild_tensor_v2(storage, storage_offset, size, stride, requires_grad, backward_hooks):
    #
    ## sample instruction from decompiled pickle:
    # _rebuild_tensor_v2(UNPICKLER.persistent_load(('storage', HalfStorage, '0', 'cpu', 11520)), 0, (320, 4, 3, 3), (36, 9, 3, 1), False, _var0)
    #
    # the following comments will show the output of each string manipulation as if it started with the above.

    garbage, storage_etc = instruction_string.split('((', 1)
    # storage_etc = 'storage', HalfStorage, '0', 'cpu', 11520)), 0, (320, 4, 3, 3), (36, 9, 3, 1), False, _var0)
      
    storage, etc = storage_etc.split('))', 1)
    # storage = 'storage', HalfStorage, '0', 'cpu', 11520
    # etc = 0, (320, 4, 3, 3), (36, 9, 3, 1), False, _var0)

    ## call below maps to: ('storage', HalfStorage, '0', 'cpu', 11520)
    self.ident, self.storage_type, self.obj_key, self.location, self.obj_size = storage.split(', ', 4)

    self.ident = self.ident.strip("'")
    self.obj_key = self.obj_key.strip("'")
    self.location = self.location.strip("'")
    self.obj_size = int(self.obj_size)
    self.storage_type = self._torch_to_numpy(self.storage_type)

    assert (self.ident == 'storage')

    garbage, etc = etc.split(', (', 1)
    # etc = 320, 4, 3, 3), (36, 9, 3, 1), False, _var0)

    size, stride, garbage = etc.split('), ', 2)
    # size = 320, 4, 3, 3
    # stride = (36, 9, 3, 1
    stride = stride.strip('(,')
    size = size.strip(',')

    if (size == ''):
      # rare case where there is an empty tuple. SDv1.4 has two of these.
      self.size_tuple = ()
    else:
      self.size_tuple = tuple(map(int, size.split(', ')))

    if (stride == ''):
      self.stride = ()
    else:
      self.stride = tuple(map(int, stride.split(', ')))

    prod_size = prod(self.size_tuple)
    assert prod(self.size_tuple) == self.obj_size # does the size in the storage call match the size tuple

    # zero out the data
    self.data = np.zeros(self.size_tuple, dtype=self.storage_type)

  @staticmethod
  def _torch_to_numpy(storage_type):
    if storage_type == 'FloatStorage': 
      return np.float32
    if storage_type == 'HalfStorage': 
      return np.float16
    if storage_type == 'LongStorage': 
      return np.int64
    if storage_type == 'IntStorage': 
      return np.int32
    raise Exception("Storage type not defined!")

  def load_from_file_buffer(self, fb):
    if self.data.dtype == "object":
      print(f"issue assigning object on {self.obj_key}")
      return False
    else:
     np.copyto(self.data, np.frombuffer(fb.read(), self.data.dtype).reshape(self.size_tuple))
     return True
    
  def get_data(self):
    return self.data

