import time
import sys
import json
import copy

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


print("utds loading_msg___U_P_D_A_T_E___\" Loading model \"" ) 
print("utds loading_percentage___U_P_D_A_T_E___-1" ) 

time.sleep(4)

print("utds is_model_loaded___U_P_D_A_T_E___true") # model loaded
print("utds loading_msg___U_P_D_A_T_E___\"\"" ) 


def process_opt():
	for i in range(100):
		print("utds loading_percentage___U_P_D_A_T_E___"+str(i) ) 
		time.sleep(0.1)
	impath = "/Users/divamgupta/Downloads/aaaa.png"
	print("utds generated_image___U_P_D_A_T_E___\"%s\""%(impath) )


while True:
        print("utds is_textbox_avail___U_P_D_A_T_E___true") # model loaded # disable input
        print("utds loading_msg___U_P_D_A_T_E___\"\"") 

        inp_str = input()

        if inp_str.strip() == "":
            continue

        if not "b2py t2im" in inp_str:
            continue
        inp_str = inp_str.replace("b2py t2im" , "").strip()
        try:
            d = json.loads(inp_str)
           
            print("utds is_textbox_avail___U_P_D_A_T_E___false") # model loaded # disable input
            print("utds loading_msg___U_P_D_A_T_E___\"Generating Image\"") 
            print("utds generated_image___U_P_D_A_T_E___\"\"") 
            print("utds backedn_error___U_P_D_A_T_E___\"\"") 
            process_opt( )
        except Exception as e:
            print("utds backedn_error___U_P_D_A_T_E___\"%s\""%(str(e))) 
            print("py2b eror " + str(e))
