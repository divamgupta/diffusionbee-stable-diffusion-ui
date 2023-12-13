import numpy as np 
import json

file_head_nums = [8589935844, 0, 0, 0, 0,  0, 0, 0]

class TDict:
    
    magic_number = 4346464

    def __init__(self, fpath, mode=None, ctdict_version=-1):
        self.fpath = fpath
        self.tdict_format_version = 2
        self.min_supported_version = 2 #what earliest version of reader can read the tdict file generated using this 
        
        if mode == "r":
            self.init_read()

        if mode == 'w':
            self.init_write(ctdict_version=ctdict_version)

    def pad_bytes(self, nb):
        self.out_file.write(b'\x00' * nb )
        self.filep += nb

    def write_block(self, block_array ):

        if self.filep  %64 != 0:
            npad = 64 - self.filep  % 64
            self.pad_bytes(npad)

        wconsts = [4377183192, 16197862624 , 4380524608, 4338844632,  16102825584,  4342186048, 14897610352, 12854472448]
        data_bytes = block_array.tobytes()
        head_bytes = np.array([8030895855 , len(data_bytes) , self.filep+64 , 20433505136 , 2  , wconsts[3] , wconsts[7]  , wconsts[5] ] ,dtype='uint64')
        head_bytes = head_bytes.tobytes()

        assert len(head_bytes) == 64

        self.out_file.write(head_bytes)
        self.out_file.write(data_bytes)

        n_start_head = self.filep
        n_start_data = self.filep + 64

        self.filep += (len(head_bytes) + len(data_bytes))
        n_end_data = self.filep 

        return {
            "n_start_head": n_start_head,
            "n_start_data": n_start_data,
            "n_end_data": n_end_data,
            "n_bytes": len(data_bytes)}

    def keys(self):
        return self.keys_info.keys()



    def read_block(self, header_pos, np_shape=None, np_dtype=None):

        self.in_file.seek(0)
        old_headers = self.in_file.read(4)
        if tuple(old_headers) == (42, 10 , 8, 42):
            raise ValueError("The model was imported using an older version of software. Please delete the model and re-import it.")

        self.in_file.seek(header_pos)
        b = self.in_file.read(64)
        arr = np.frombuffer(b, dtype='uint64')
        assert arr[0] == 8030895855, arr
        assert arr[4] == 2  
        assert arr[2] == header_pos + 64
        l = arr[1] # size of buffer to read

        block  = self.in_file.read(l)

        if np_dtype is not None:
            if "cus_" in np_dtype: #custom dtype, which is not supported by numpy 
                block = np.frombuffer(block, dtype='uint8')
                block = decode_custom_dtype(block , np_dtype )
            else:
                block = np.frombuffer(block, dtype=np_dtype)

        if np_shape is not None:
            block = block.reshape(np_shape)

        return block 



    def init_write(self, ctdict_version=-1):
        
        self.ctdict_version = ctdict_version

        self.out_file = open( self.fpath , "wb")
        self.filep = 0

        self.keys_info = {}
        self.model_info = {}

        # write the initial header
        self.out_file.write( np.array(file_head_nums, dtype='uint64').tobytes() )
        self.filep += 64

        extra_head = np.zeros((20,) , dtype='uint64')
        self.extra_head_pos = self.write_block(extra_head)
        print("extra_head_pos" , self.extra_head_pos)

        weights_json = np.zeros((10**7,) , dtype='uint8') # fill with zeros for now with 10MB data
        self.weights_json_pos = self.write_block(weights_json)
        print("weights_json_pos" , self.weights_json_pos)


        metadata_json = np.zeros((10**5,) , dtype='uint8') # fill with zeros for now with 10MB data
        self.metadata_json_pos = self.write_block(metadata_json)
        print("metadata_json_pos" , self.metadata_json_pos)

        assert self.extra_head_pos['n_start_head'] == 64
        assert self.weights_json_pos['n_start_head'] == 320
        assert self.metadata_json_pos['n_start_head'] == 10000384



    def init_read(self):
        self.in_file = open( self.fpath , "rb")
        extra_head = self.read_block(64, np_dtype='uint64')
        assert len(extra_head) == 20
        assert extra_head[0] == self.magic_number

        if extra_head[2] > self.tdict_format_version:
            raise ValueError("The model was imported using an newer version of software. Please delete the model and re-import it.")

        weights_json_start = extra_head[4]
        weights_json_l = extra_head[5] - extra_head[4]
        print( "json pos" ,  weights_json_start , weights_json_l)

        self.ctdict_version = int(extra_head[3])

        self.in_file.seek(weights_json_start)
        self.keys_info = json.loads( self.in_file.read(weights_json_l).decode('ascii') )

    def finish_read(self):
        self.in_file.close()


    def read_key(self , key):
        assert key in self.keys_info , "Key not found "+key
        w_idx_start =  self.keys_info[key]['start']
        w_idx_len =   self.keys_info[key]['end'] -   self.keys_info[key]['start']
        ret_arr = self.read_block(w_idx_start-64, np_dtype=self.keys_info[key]['dtype'] , np_shape=tuple(self.keys_info[key]['shape']) )
        assert len(ret_arr.tobytes()) == w_idx_len
        return ret_arr.copy()

    def write_key(self , key , tensor, custom_dtype=None ):
        assert key not in self.keys_info
        dtype = str(tensor.dtype)
        if custom_dtype is not None:
            dtype = custom_dtype
            raise not NotImplementedError("Casting not implemented.")

        write_info = self.write_block(tensor)
        shape = list(tensor.shape)
        self.keys_info[key] = {"start": write_info['n_start_data'] , "end" : write_info['n_end_data'] , "shape": shape , "dtype" : dtype }

    def write_key_custom_dype(self, uint8_arr , key, custom_dtype , shape ):
        assert key not in self.keys_info
        dtype = custom_dtype
        write_info = self.write_block(uint8_arr)
        self.keys_info[key] = {"start": write_info['n_start_data'] , "end" : write_info['n_end_data'] , "shape": shape , "dtype" : dtype }


    def finish_write(self):

        if self.filep  %64 != 0:
            npad = 64 - self.filep  % 64
            self.pad_bytes(npad)

        weights_json_bytes = bytes( json.dumps(self.keys_info)  , 'ascii')
        weights_json_start = self.weights_json_pos['n_start_data']
        weights_json_end = weights_json_start + len(weights_json_bytes)
        self.out_file.seek(weights_json_start)
        self.out_file.write(weights_json_bytes)

        metadata_json_bytes = bytes( json.dumps(self.model_info)  , 'ascii')
        metadata_json_start = self.metadata_json_pos['n_start_data']
        metadata_json_end = metadata_json_start + len(metadata_json_bytes)
        self.out_file.seek(metadata_json_start)
        self.out_file.write(metadata_json_bytes)

        self.out_file.seek(self.extra_head_pos['n_start_data'])
        extra_head = [self.magic_number] + [self.tdict_format_version ,self.min_supported_version ,self.ctdict_version , weights_json_start , weights_json_end , metadata_json_start, metadata_json_end ] + [0]*12
        assert len(extra_head) == 20
        self.out_file.write( np.array(extra_head, dtype='uint64').tobytes() )

        self.out_file.close()




