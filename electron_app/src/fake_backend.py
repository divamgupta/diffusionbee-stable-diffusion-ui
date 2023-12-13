import time
import sys
import json
import copy
import random
import os
import cv2

class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


sys.stdout = Unbuffered(sys.stdout)

time.sleep(1)


if len(sys.argv) > 1 and  sys.argv[1] == "convert_model":
    time.sleep(4)
    exit()



sample_path = os.path.join(  os.path.dirname(os.path.abspath(__file__)),  "assets",  "sample.png"  )

print("sdbk mltl downloading model")
for i in range(100):
    time.sleep(0.02)

    print("sdbk mlpr %d"%i ) # model loading percentage
    print("sdbk mlms done %s of 100.0"%i)

print("sdbk mlpr %d"%(-1) )
time.sleep(2)

print("sdbk mdld") # model loaded


def process_opt(opts):
    

    if 'num_imgs' not in opts:
        opts['num_imgs'] = 1

    for nn in range(opts['num_imgs']):

        
        if  opts['seed'] < 20:
            print("sdbk errr just a random error lol")
            return

        print("sdbk dnpr "+str(-1) ) 
        time.sleep(0.8)
        for i in range(0,100,5):
            print("sdbk dnpr "+str(i) ) # done percentage
            time.sleep(0.1)
            # if opts['seed'] > 2:
            #     time.sleep(100.1)
        print("sdbk dnpr "+str(-1) ) 
        time.sleep(0.8)
        impath = sample_path 
        im = cv2.imread(impath)
        im = cv2.resize(im , ( opts['img_width'] , opts['img_height'] ) )
        new_p =  "/tmp/%d_%d.png"%( opts['img_width'] , opts['img_height'])
        cv2.imwrite( new_p ,  im )

        # if 'input_image' in opts:
        #     impath = opts['input_image']
        ret_dict = {"generated_img_path" : (new_p) }

        print("sdbk nwim %s"%(json.dumps(ret_dict)) ) # new image generated
    
while True:
        print("sdbk inrd") # input ready

        inp_str = input()   
        print("got " , inp_str )
        if inp_str.strip() == "":
            continue
        else:
            print("sbdk errr The string is blank")

        if not "b2py t2im" in inp_str:
            continue
        inp_str = inp_str.replace("b2py t2im" , "").strip()
        try:
            d = json.loads(inp_str)
           
            print("sdbk inwk") # working on the input
            process_opt(d)
        except Exception as e:
            print("sbdk errr %s"%(str(e))) 
