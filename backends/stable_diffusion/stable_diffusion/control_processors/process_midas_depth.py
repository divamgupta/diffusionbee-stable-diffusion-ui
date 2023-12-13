
import onnxruntime as ort
import numpy as np 
import cv2



def process_image_midas_depth(inp_fname, out_fname, model_path):

    im = cv2.imread(inp_fname)[... , ::-1 ]
    im_h = im.shape[0]
    im_w = im.shape[1]

    im = cv2.resize(im , (384 , 384 )).astype("float32")
    im = np.rollaxis(im , 2, 0 )[None]/127.5 - 1.0


    ort_sess = ort.InferenceSession(model_path)

    dep = ort_sess.run(None, {'0': im })[0][0]
    dep = dep - dep.min()
    dep = dep / dep.max()

    dep = (dep*255).astype('uint8')[... , None ]
    dep = np.repeat(dep , 3 , axis=2)

    is_normal = False 

    if is_normal:
        depth_np = dep[... , 0]
        a=np.pi * 2.0
        bg_th=0.1

        x = cv2.Sobel(depth_np, cv2.CV_32F, 1, 0, ksize=3)
        y = cv2.Sobel(depth_np, cv2.CV_32F, 0, 1, ksize=3)
        z = np.ones_like(x) * a
        x[depth_np < bg_th] = 0
        y[depth_np < bg_th] = 0
        normal = np.stack([x, y, z], axis=2)
        normal /= np.sum(normal ** 2.0, axis=2, keepdims=True) ** 0.5
        normal_image = (normal * 127.5 + 127.5).clip(0, 255).astype(np.uint8)
        dep = normal_image

    
    dep = cv2.resize(dep , (im_w , im_h))
    cv2.imwrite(out_fname , dep )


if __name__ == "__main__":
    process_image_midas_depth("/Users/divamgupta/Downloads/2T6A5407R-scaled.jpg" , "/tmp/a.png" , "/Users/divamgupta/Downloads/midas_monodepth.onnx")
    import os 
    os.system("open /tmp/a.png")