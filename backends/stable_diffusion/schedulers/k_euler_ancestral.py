import numpy as np


def get_alphas_cumprod(beta_start=0.00085, beta_end=0.0120, n_training_steps=1000):
    betas = np.linspace(beta_start ** 0.5, beta_end ** 0.5, n_training_steps, dtype=np.float32) ** 2
    alphas = 1.0 - betas
    alphas_cumprod = np.cumprod(alphas, axis=0)
    return alphas_cumprod


class KEulerAncestralSampler():
    def __init__(self):
        pass


    def set_timesteps(self, n_inference_steps, n_training_steps=1000): #dg
        timesteps = np.linspace(n_training_steps - 1, 0, n_inference_steps)

        alphas_cumprod = get_alphas_cumprod(n_training_steps=n_training_steps)
        sigmas = ((1 - alphas_cumprod) / alphas_cumprod) ** 0.5
        log_sigmas = np.log(sigmas)
        log_sigmas = np.interp(timesteps, range(n_training_steps), log_sigmas)
        sigmas = np.exp(log_sigmas)
        sigmas = np.append(sigmas, 0)
        
        self.sigmas = sigmas
        self.initial_scale = sigmas.max()
        self.timesteps = timesteps
        self.n_inference_steps = n_inference_steps
        self.n_training_steps = n_training_steps


    def get_input_scale(self, step_count=None):
        sigma = self.sigmas[step_count]
        return 1 / (sigma ** 2 + 1) ** 0.5

    # def set_strength(self, strength=1):
    #     start_step = self.n_inference_steps - int(self.n_inference_steps * strength)
    #     self.timesteps = np.linspace(self.n_training_steps - 1, 0, self.n_inference_steps)
    #     self.timesteps = self.timesteps[start_step:]
    #     self.initial_scale = self.sigmas[start_step]
    #     self.step_count = start_step


    def add_noise(self, latent, noise, idx ): #dg
        for i in idx:
            assert idx[0] == i
        sc = self.sigmas[idx[0]]
        return latent + noise*sc

    def step(self, output , t , latents , seed   ): #dg
       

        sigma_from = self.sigmas[t]
        sigma_to = self.sigmas[t + 1]
        sigma_up = sigma_to * (1 - (sigma_to ** 2 / sigma_from ** 2)) ** 0.5
        sigma_down = sigma_to ** 2 / sigma_from
        latents += output * (sigma_down - sigma_from)
        noise = np.random.RandomState(seed).normal(size=latents.shape).astype('float32')
        latents += noise * sigma_up
        return {"prev_sample": latents } #latents