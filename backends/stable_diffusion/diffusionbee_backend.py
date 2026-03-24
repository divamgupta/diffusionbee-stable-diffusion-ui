print("starting backend")
import json
import multiprocessing
import sys
import time
import traceback

try:
    from .applets.applets import register_applet, run_applet
    from .applets.frame_interpolator import FrameInterpolator
    from .service import DiffusionBeeService, generation_result_payload
except ImportError:
    from applets.applets import register_applet, run_applet
    from applets.frame_interpolator import FrameInterpolator
    from service import DiffusionBeeService, generation_result_payload


# b2py t2im {"prompt": "sun glasses" , "img_width":640 , "img_height" : 640 , "num_imgs" : 10 , "input_image":"/Users/divamgupta/Downloads/inn.png" , "mask_image" : "/Users/divamgupta/Downloads/maa.png" , "is_inpaint":true  }

service = DiffusionBeeService()



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





def diffusion_bee_main():

    time.sleep(2)
    register_applet(service._get_generator().model_container , FrameInterpolator)

    print("sdbk mltl Loading Model")

    def callback(state="" , progress=-1):
        print("sdbk dnpr "+str(progress) )
        if state != "Generating":
            print("sdbk gnms " + state)

        if is_avail():
            if "__stop__" in get_input():
                return "stop"

    service._progress_callback = callback
    service._get_generator()

    print("sdbk mdld")

    while True:
        print("sdbk inrd") # input ready

        inp_str = get_input()

        print("got" , inp_str)

        if inp_str.strip() == "":
            continue

        if  ((not "b2py t2im" in inp_str ) and (not "b2py rapp" in inp_str) ) or "__stop__" in inp_str:
            continue

        if "b2py t2im" in inp_str:
            inp_str = inp_str.replace("b2py t2im" , "").strip()
            try:
                d = json.loads(inp_str)
                print("sdbk inwk") # working on the input
                result = service.generate_images(d, progress_callback=callback)
                for image in generation_result_payload(result)["images"]:
                    print("sdbk nwim %s"%(json.dumps(image)) )
                
            except Exception as e:
                traceback.print_exc()
                print("sdbk errr %s"%(str(e)))
                print("py2b eror " + str(e))

        elif "b2py rapp" in inp_str:
            inp_str = inp_str.replace("b2py rapp" , "").strip()
            applet_name = inp_str.split(" ")[0]
            inp_str = inp_str.replace(applet_name , "").strip()

            try:
                d = json.loads(inp_str)
                print("sdbk inwk") # working on the input
                run_applet(applet_name , d )
            except Exception as e:
                traceback.print_exc()
                print("sdbk errr %s"%(str(e)))


from stable_diffusion.utils.stdin_input import is_avail, get_input


if __name__ == "__main__":
    multiprocessing.freeze_support()  # for pyinstaller

    if len(sys.argv) > 1 and sys.argv[1] == 'convert_model':
        checkpoint_filename = sys.argv[2]
        out_filename = sys.argv[3]
        service.convert_model(checkpoint_filename, out_filename)
        print("model converted ")
    else:
        diffusion_bee_main()
