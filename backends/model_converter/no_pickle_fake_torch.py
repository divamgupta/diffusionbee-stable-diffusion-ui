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


def extract_weights_from_checkpoint(fb0):
  torch_weights = {}
  torch_weights['state_dict'] = {}
  with zipfile.ZipFile(fb0, 'r') as myzip:
    folder_name = [a for a in myzip.namelist() if a.endswith("/data.pkl")]
    if len(folder_name)== 0:
      raise ValueError("Looks like the checkpoints file is in the wrong format")
    folder_name = folder_name[0].replace("/data.pkl" , "").replace("\\data.pkl" , "")
    with myzip.open(folder_name+'/data.pkl') as myfile:
      instructions = examine_pickle(myfile)
      for sd_key,load_instruction in instructions.items():
        with myzip.open(folder_name + f'/data/{load_instruction.obj_key}') as myfile:
          if (load_instruction.load_from_file_buffer(myfile)):
            torch_weights['state_dict'][sd_key] = load_instruction.get_data()
         
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

  load_instructions = {}
  assign_instructions = AssignInstructions()

  for line in decompiled:
    ## see if line matches pattern of var =
    line = line.strip()
    if re_rebuild.match(line):
      variable_name, load_instruction = line.split(' = ', 1)
      load_instructions[variable_name] = LoadInstruction(line)
    elif re_assign.match(line):
      assign_instructions.parse_assign_line(line)
    elif re_update.match(line):
      assign_instructions.parse_update_line(line)
    #else:
    #  print('kicking rocks')

  print(f"Found {len(load_instructions)} load instructions")

  assign_instructions.integrate(load_instructions)

  return assign_instructions.integrated_instructions
    

  #output = {}
  #output['state_dict'] = {}

class AssignInstructions:
  def __init__(self):
    self.instructions = {}
    self.integrated_instructions = {}

  def parse_assign_line(self, line):
    # input looks like this:
    # _var2262 = {'model.diffusion_model.input_blocks.0.0.weight': _var1, 'model.diffusion_model.input_blocks.0.0.bias': _var3,\
    #  ...\
    #  'cond_stage_model.transformer.text_model.encoder.layers.3.layer_norm2.weight': _var1999}
    garbage, huge_mess = line.split(' = {')
    assignments = huge_mess.split(', ')
    del huge_mess
    assignments[-1] = assignments[-1].strip('}')
    for a in assignments:
      self._add_assignment(a)
    print(f"Added/merged {len(assignments)} assignments. Total of {len(self.instructions)} assignment instructions")

  def _add_assignment(self, assignment):
    sd_key, fickling_var = assignment.split(': ')
    sd_key = sd_key.strip("'")
    self.instructions[sd_key] = fickling_var

  def integrate(self, load_instructions):
    for sd_key, fickling_var in self.instructions.items():
      if fickling_var in load_instructions:
        self.integrated_instructions[sd_key] = load_instructions[fickling_var]
    print(f"Have {len(self.integrated_instructions)} integrated load/assignment instructions")

  def parse_update_line(self, line):
    # input looks like:
    # _var2262.update({'cond_stage_model.transformer.text_model.encoder.layers.3.layer_norm2.bias': _var2001,\
    # 'cond_stage_model.transformer.text_model.encoder.layers.4.self_attn.k_proj.weight': _var2003,\
    # ...\
    #'cond_stage_model.transformer.text_model.final_layer_norm.bias': _var2261})
    garbage, huge_mess = line.split('({')
    updates = huge_mess.split(', ')
    del huge_mess
    updates[-1] = updates[-1].strip('})')
    for u in updates:
      self._add_assignment(u)
    print(f"Added/merged {len(updates)} updates. Total of {len(self.instructions)} assignment instructions")

class LoadInstruction:
  def __init__(self, instruction_string):
    self.ident = False
    self.storage_type = False
    self.obj_key = False
    self.location = False
    self.obj_size = False
    self.stride = False #args[3] -- unused, I think
    self.data = False;
    self.parse_instruction(instruction_string)

  def parse_instruction(self, instruction_string):
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
    #      ident, storage_type, obj_key, location, obj_size = args[0][0:5]
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
     #key_prelookup[obj_key] = (storage_type, obj_size, ret, args[2], args[3])
     #maps to: where v is the right side of the above assignment 
     #np.copyto(v[2], np.frombuffer(myfile.read(), v[2].dtype).reshape(v[3]))
     #print(f"np.copyto(self.data, np.frombuffer(fb.read(), {self.data.dtype}).reshape({self.size_tuple}))")
     np.copyto(self.data, np.frombuffer(fb.read(), self.data.dtype).reshape(self.size_tuple))
     return True
    
  def get_data(self):
    return self.data



#examine_pickle(open('classicanimation.archive/data.pkl', "rb"))


