
from .scheduling_ddim import DDIMScheduler
from .scheduling_lms_discrete  import LMSDiscreteScheduler
from .scheduling_pndm import PNDMScheduler
from .k_euler_ancestral import KEulerAncestralSampler
from .k_euler import KEulerSampler
from .karras_scheduler import KarrasSampler

def get_scheduler(name):
    if name == "ddim":
        return DDIMScheduler(
            beta_start=0.00085,
            beta_end=0.012,
            beta_schedule="scaled_linear",
            clip_sample= False,
            num_train_timesteps= 1000,
            set_alpha_to_one=False,
            # steps_offset= 1,
            trained_betas= None,
            tensor_format="np",
        )

    if name == "ddim_v":
        return DDIMScheduler(
            beta_start=0.00085,
            beta_end=0.012,
            beta_schedule="scaled_linear",
            clip_sample= False,
            num_train_timesteps= 1000,
            set_alpha_to_one=False,
            # steps_offset= 1,
            trained_betas= None,
            tensor_format="np",
            prediction_type="v_prediction"
        )

    if name == "lmsd":
        return LMSDiscreteScheduler(
            beta_start=0.00085,
            beta_end=0.012,
            beta_schedule="scaled_linear",
            tensor_format="np")

    if name == "pndm":
        return PNDMScheduler(
            beta_start=0.00085,
            beta_end=0.012,
            beta_schedule="scaled_linear",
            skip_prk_steps = True,
            tensor_format="np")

    if name == "k_euler_ancestral":
        return KEulerAncestralSampler()

    if name == "k_euler":
        return KEulerSampler()
    
    
    if name == "karras":
        return KarrasSampler()
