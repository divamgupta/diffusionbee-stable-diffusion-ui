
if __name__ == "__main__":
    inp = "/Volumes/Drive/projects_monorepo/generative_ai/diffusion_bee/bee_mps_backend/mps_backend_maple/data_points/mmm.png"
    mas = "/Volumes/Drive/projects_monorepo/generative_ai/diffusion_bee/bee_mps_backend/mps_backend_maple/data_points/ddd.png"
    sd = StableDiffusion( )


    # for cur_run_id in range(2):
    #     img = sd.generate(
    #         prompt="a haloween bedroom" , 
    #         img_height=512+64, 
    #         img_width=512-64, 
    #         seed=678, 
    #         tdict_path=None,
    #         batch_size=1,
    #         dtype='float16',
    #         scheduler='ddim',
    #         input_image_strength=0.4,
    #         input_image="bedroom2.jpg",
    #         mode="img2img" )
    #     Image.fromarray(img[0]).show()

    # for cur_run_id in range(2):
    #     img = sd.generate(
    #         prompt="modern disney a blue colored baby lion with lots of fur" , 
    #         img_height=512-64, 
    #         img_width=512, 
    #         seed=34, 
    #         num_steps=25,
    #         batch_size=1,
    #         tdict_path="/Users/divamgupta/.diffusionbee/custom_models/moDi-v1-pruned.tdict",
    #         dtype='float16',
    #         scheduler='ddim',
    #         mode="txt2img" )
    #     Image.fromarray(img[0]).show()

    # img = sd.generate(
    #     prompt="modern disney a blue colored baby lion with lots of fur" , 
    #     img_height=512, 
    #     img_width=512, 
    #     seed=34, 
    #     tdict_path=None,
    #     mode="txt2img" )
    # Image.fromarray(img[0]).show()


    img = sd.generate(
        prompt="Face of red cat, high resolution, sitting on a park bench" , 
        img_height=512, 
        img_width=512, 
        seed=443136, 
        input_image=inp, 
        mask_image=mas,  
        tdict_path="/Users/divamgupta/Downloads/sd-v1-5-inpainting.tdict",
        mode="inpaint_15" )
    Image.fromarray(img[0]).show()



