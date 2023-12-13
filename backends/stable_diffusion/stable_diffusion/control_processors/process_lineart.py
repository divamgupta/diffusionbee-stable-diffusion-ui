
import onnxruntime as ort
import numpy as np 
import cv2



def process_image_lineart(inp_fname, out_fname, model_path):

    im = cv2.imread(inp_fname)[... , ::-1 ]
    im_h = im.shape[0]
    im_w = im.shape[1]

    im = cv2.resize(im , (512 , 512 )).astype("float32") #TODO change this 
    im = np.rollaxis(im , 2, 0 )[None]/255.0 

    ort_sess = ort.InferenceSession(model_path)

    dep = ort_sess.run(None, {'input': im })[0][0][0]    

    dep = ((1-dep)*255).clip(0, 255).astype('uint8')[... , None ]
    dep = np.repeat(dep , 3 , axis=2)

    dep = cv2.resize(dep , (im_w , im_h))
    cv2.imwrite(out_fname , dep )


if __name__ == "__main__":
    process_image_lineart("/Users/divamgupta/Downloads/2T6A5407R-scaled.jpg" , "/tmp/a.png" , "/tmp/linart.onnx")
    import os 
    os.system("open /tmp/a.png")