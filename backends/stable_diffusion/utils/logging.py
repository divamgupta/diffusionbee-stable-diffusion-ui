import numpy as np
import os
import time
import pickle

def log_numpy( arr  , out_dir , key ):
    outf = os.path.join( out_dir , "%d_%s.npy"%(int(time.time()*1000) , key ) )
    np.save(outf , arr )

def log_pkl( obj  , out_dir , key ):
    outf = os.path.join( out_dir , "%d_%s.pkl"%(int(time.time()*1000) , key ) )
    
    with open(outf , 'wb') as handle:
        pickle.dump(obj , handle, protocol=pickle.HIGHEST_PROTOCOL)


def log_object( obj , out_dir , key="" ):
    if type(obj) is np.ndarray:
        log_numpy( obj  , out_dir , key )
    else:
        log_pkl( obj  , out_dir , key )


    