import numpy as np

try:
  from math import prod
except:
  from functools import reduce
  def prod(iterable):
    return reduce(operator.mul, iterable, 1)
import zipfile
import pickle
import sys
import ast
import re
from fickling.pickle import Pickled
  
if sys.version_info >= (3, 9):
    from ast import unparse
else:
    from astunparse import unparse
  
NO_PICKLE_DEBUG = False

### Unpickling import:
def my_unpickle(fb0):
  key_prelookup = {}
  class HackTensor:
    def __new__(cls, *args):
      #print(args)
      ident, storage_type, obj_key, location, obj_size = args[0][0:5]
      assert ident == 'storage'

      assert prod(args[2]) == obj_size


      ret = np.zeros(args[2], dtype=storage_type)
      if obj_key not in key_prelookup:
        key_prelookup[obj_key] = []

      key_prelookup[obj_key].append((storage_type, obj_size, ret, args[2], args[3]))

      #print(f"File: {obj_key}, references: {len(key_prelookup[obj_key])}, size: {args[2]}, storage_type: {storage_type}")

      return ret

  class HackParameter:
    def __new__(cls, *args):
      #print(args)
      pass

  class Dummy:
    pass

  class MyPickle(pickle.Unpickler):
    def find_class(self, module, name):
      #print(module, name)
      if name == 'FloatStorage':
        return np.float32
      if name == 'LongStorage':
        return np.int64
      if name == 'HalfStorage':
        return np.float16
      if module == "torch._utils":
        if name == "_rebuild_tensor_v2":
          return HackTensor
        elif name == "_rebuild_parameter":
          return HackParameter
      else:
        try:
          return pickle.Unpickler.find_class(self, module, name)
        except Exception:
          return Dummy

    def persistent_load(self, pid):
      return pid

  return MyPickle(fb0).load(), key_prelookup

def fake_torch_load_zipped(fb0, load_weights=True):
  with zipfile.ZipFile(fb0, 'r') as myzip:
    folder_name = [a for a in myzip.namelist() if a.endswith("/data.pkl")]
    if len(folder_name)== 0:
      raise ValueError("Looke like the checkpoints file is in the wrong format")
    folder_name = folder_name[0].replace("/data.pkl" , "").replace("\\data.pkl" , "")
    with myzip.open(folder_name+'/data.pkl') as myfile:
      ret = my_unpickle(myfile)
    if load_weights:
      for k, v_arr in ret[1].items():
        with myzip.open(folder_name + f'/data/{k}') as myfile:
          #print(f"Eating data file {k} now")
          file_data = myfile.read()
          for v in v_arr:
            if v[2].dtype == "object":
              print(f"issue assigning object on {k}")
              continue
            #weight = np.frombuffer(file_data, v[2].dtype).reshape(v[3])
            #np.copyto(v[2], weight)
            np.copyto(v[2], np.frombuffer(file_data, v[2].dtype).reshape(v[3]))
  return ret[0]

### No-unpickling import:
def extract_weights_from_checkpoint(fb0):
  torch_weights = {}
  torch_weights['state_dict'] = {}
  with zipfile.ZipFile(fb0, 'r') as myzip:
    folder_name = [a for a in myzip.namelist() if a.endswith("/data.pkl")]
    if len(folder_name)== 0:
      raise ValueError("Looks like the checkpoints file is in the wrong format")
    folder_name = folder_name[0].replace("/data.pkl" , "").replace("\\data.pkl" , "")
    with myzip.open(folder_name+'/data.pkl') as myfile:
      load_instructions = examine_pickle(myfile)
      for sd_key,load_instruction in load_instructions.items():
        with myzip.open(folder_name + f'/data/{load_instruction.obj_key}') as myfile:
          if (load_instruction.load_from_file_buffer(myfile)):
            torch_weights['state_dict'][sd_key] = load_instruction.get_data()
      #if len(special_instructions) > 0:
      #  torch_weights['state_dict']['_metadata'] = {}
      #  for sd_key,special in special_instructions.items():
      #    torch_weights['state_dict']['_metadata'][sd_key] = special
  return torch_weights

def examine_pickle(fb0, return_special=False):
  ## return_special:
  ## A rabbit hole I chased trying to debug a model that wouldn't import that had 1300 metadata statements
  ## If for some reason it's needed in the future turn it on. It is passed into the class AssignInstructions and 
  ## if turned on collect_special will be True
  ##
  ## If, by 2023, this hasn't been required, I would strip it out.

  #turn the pickle file into text we can parse
  decompiled = unparse(Pickled.load(fb0).ast).splitlines()

  ## Parsing the decompiled pickle:
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
  ## 4: in some pruned models, the last line is instead a combination of 2/3 into the final variable:
  ## result = {'model.diffusion_model.input_blocks.0.0.weight': _var1, 'model.diffusion_model.input_blocks.0.0.bias': _var3, }
  ##
  ## that's it  

  # make some REs to match the above.
  re_rebuild = re.compile('^_var\d+ = _rebuild_tensor_v2\(UNPICKLER\.persistent_load\(\(.*\)$')
  re_assign = re.compile('^_var\d+ = \{.*\}$')
  re_update = re.compile('^_var\d+\.update\(\{.*\}\)$')
  re_ordered_dict = re.compile('^_var\d+ = OrderedDict\(\)$')
  re_result = re.compile('^result = \{.*\}$')

  load_instructions = {}
  assign_instructions = AssignInstructions()

  for line in decompiled:
    ## see if line matches patterns of lines we care about: 
    line = line.strip()
    if re_rebuild.match(line):
      variable_name, load_instruction = line.split(' = ', 1)
      load_instructions[variable_name] = LoadInstruction(line, variable_name)
    elif re_assign.match(line) or re_result.match(line):
      assign_instructions.parse_assign_line(line)
    elif re_update.match(line):
      assign_instructions.parse_update_line(line)
    elif re_ordered_dict.match(line):
      #do nothing
      continue
    elif NO_PICKLE_DEBUG:
      print(f'unmatched line: {line}')


  if NO_PICKLE_DEBUG:
    print(f"Found {len(load_instructions)} load instructions")

  assign_instructions.integrate(load_instructions)

  if return_special:
    return assign_instructions.integrated_instructions, assign_instructions.special_instructions
  return assign_instructions.integrated_instructions

class AssignInstructions:
  def __init__(self, collect_special=False):
    self.instructions = {}
    self.special_instructions = {}
    self.integrated_instructions = {}
    self.collect_special = collect_special;

  def parse_result_line(self, line):
    garbage, huge_mess = line.split(' = {', 1)
    assignments = huge_mess.split(', ')
    del huge_mess
    assignments[-1] = assignments[-1].strip('}')

    #compile RE here to avoid doing it every loop iteration:
    re_var = re.compile('^_var\d+$')

    assignment_count = 0
    for a in assignments:
      if self._add_assignment(a, re_var):
        assignment_count = assignment_count + 1
    if NO_PICKLE_DEBUG:
      print(f"Added/merged {assignment_count} assignments. Total of {len(self.instructions)} assignment instructions")

  def parse_assign_line(self, line):
    # input looks like this:
    # _var2262 = {'model.diffusion_model.input_blocks.0.0.weight': _var1, 'model.diffusion_model.input_blocks.0.0.bias': _var3,\
    #  ...\
    #  'cond_stage_model.transformer.text_model.encoder.layers.3.layer_norm2.weight': _var1999}

    # input looks like the above, but with 'result' in place of _var2262:
    # result = {'model.diffusion_model.input_blocks.0.0.weight': _var1, ... }
    #
    # or also look like: 
    # result = {'state_dict': _var2314}
    # ... which will be ignored later
    garbage, huge_mess = line.split(' = {', 1)
    assignments = huge_mess.split(', ')
    del huge_mess
    assignments[-1] = assignments[-1].strip('}')

    #compile RE here to avoid doing it every loop iteration:
    re_var = re.compile('^_var\d+$')

    assignment_count = 0
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
    if sd_key != 'state_dict' and re_var.match(fickling_var):
      self.instructions[sd_key] = fickling_var
      return True
    elif self.collect_special:
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
      else:
        if NO_PICKLE_DEBUG:
          print(f"no load instruction found for {sd_key}")

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
  def __init__(self, instruction_string, variable_name, extra_debugging = False):
    self.ident = False
    self.storage_type = False
    self.obj_key = False
    self.location = False #unused
    self.obj_size = False
    self.stride = False #unused
    self.data = False
    self.variable_name = variable_name
    self.extra_debugging = extra_debugging
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

    if self.extra_debugging:
      print(f"input: '{instruction_string}'")

    garbage, storage_etc = instruction_string.split('((', 1)
    # storage_etc = 'storage', HalfStorage, '0', 'cpu', 11520)), 0, (320, 4, 3, 3), (36, 9, 3, 1), False, _var0)

    if self.extra_debugging:
      print("storage_etc, reference: ''storage', HalfStorage, '0', 'cpu', 11520)), 0, (320, 4, 3, 3), (36, 9, 3, 1), False, _var0)'")
      print(f"storage_etc, actual: '{storage_etc}'\n")
      
    storage, etc = storage_etc.split('))', 1)
    # storage = 'storage', HalfStorage, '0', 'cpu', 11520
    # etc = , 0, (320, 4, 3, 3), (36, 9, 3, 1), False, _var0)
    if self.extra_debugging:
      print("storage, reference: ''storage', HalfStorage, '0', 'cpu', 11520'")
      print(f"storage, actual: '{storage}'\n")
      print("etc, reference: ', 0, (320, 4, 3, 3), (36, 9, 3, 1), False, _var0)'")
      print(f"etc, actual: '{etc}'\n")

    ## call below maps to: ('storage', HalfStorage, '0', 'cpu', 11520)
    self.ident, self.storage_type, self.obj_key, self.location, self.obj_size = storage.split(', ', 4)

    self.ident = self.ident.strip("'")
    self.obj_key = self.obj_key.strip("'")
    self.location = self.location.strip("'")
    self.obj_size = int(self.obj_size)
    self.storage_type = self._torch_to_numpy(self.storage_type)

    if self.extra_debugging:
      print(f"{self.ident}, {self.obj_key}, {self.location}, {self.obj_size}, {self.storage_type}")

    assert (self.ident == 'storage')

    garbage, etc = etc.split(', (', 1)
    # etc = 320, 4, 3, 3), (36, 9, 3, 1), False, _var0)
    if self.extra_debugging:
      print("etc, reference: '320, 4, 3, 3), (36, 9, 3, 1), False, _var0)'")
      print(f"etc, actual: '{etc}'\n")

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


    if self.extra_debugging:
      print(f"size: {self.size_tuple}, stride: {self.stride}")

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

