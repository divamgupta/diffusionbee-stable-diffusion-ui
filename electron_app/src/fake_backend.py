import time
import sys
import json
import copy
import random

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


print("sdbk mltl downloading model")
for i in range(100):
    time.sleep(0.06)
    print("sdbk mlpr %d"%i ) # model loading percentage
    print("sdbk mlms done %s of 100.0"%i)


print("sdbk mdld") # model loaded


def process_opt(opts):
    if random.randint(0,10) > 7:
        print("sdbk errr just a random error lol")
        return

    for _ in range(opts['num_imgs']):
        for i in range(0,100,5):
            print("sdbk dnpr "+str(i) ) # done percentage
            time.sleep(0.1)
        impath = "/Users/divamgupta/Downloads/output_fork.png?%d"%random.randint(0,10000)

        

        print("sdbk nwim %s"%(impath) ) # new image generated
    
while True:
        print("sdbk inrd") # input ready

        inp_str = input()

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
