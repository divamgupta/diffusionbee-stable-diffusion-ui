import numpy as np

class KarrasOperations:
    def __init__(self, linear_start, linear_end, timesteps, steps):
        self.linear_start = linear_start
        self.linear_end = linear_end
        self.timesteps = timesteps
        self.steps = steps

    @property
    def betas(self):
        start = np.sqrt(self.linear_start)
        length = np.sqrt(self.linear_end) - start
        betas = [start + i * length / (self.timesteps - 1) for i in range(self.timesteps)]
        return [beta**2 for beta in betas]

    @property
    def alphas_cumprod(self):
        cumprod = 1.0
        return [cumprod := cumprod * (1 - beta) for beta in self.betas]

    def karras_sigmas(self, range_, rho=7.0):
        assert len(range_) == 2 
        min_inv_rho = range_[0]**(1.0 / rho)
        max_inv_rho = range_[1]**(1.0 / rho)
        sigmas = [
            (max_inv_rho + i * (min_inv_rho - max_inv_rho) / (self.steps - 1))**rho
            for i in range(self.steps)
        ]
        sigmas.append(0)
        return sigmas

    def fixed_step_sigmas(self, range_, sigmas_for_timesteps):
        sigmas = []
        for i in range(self.steps):
            timestep = (self.steps - 1 - i) / (self.steps - 1) * (self.timesteps - 1)
            low_idx = int(np.floor(timestep))
            high_idx = min(low_idx + 1, self.timesteps - 1)
            w = timestep - low_idx
            log_sigma = (1 - w) * np.log(sigmas_for_timesteps[low_idx]) + w * np.log(sigmas_for_timesteps[high_idx])
            sigmas.append(np.exp(log_sigma))
        sigmas.append(0)
        return sigmas

    @staticmethod
    def sigmas_from_alphas_cumprod(alphas_cumprod):
        return [np.sqrt((1 - alpha) / alpha) for alpha in alphas_cumprod]

    @staticmethod
    def timestep(sigma, sigmas):
        if sigma <= sigmas[0]:
            return 0
        elif sigma >= sigmas[-1]:
            return float(len(sigmas) - 1)

        high_idx = len(sigmas) - 1
        low_idx = 0

        while low_idx < high_idx - 1:
            mid_idx = (low_idx + high_idx) // 2
            if sigma < sigmas[mid_idx]:
                high_idx = mid_idx
            else:
                low_idx = mid_idx

        assert sigmas[high_idx - 1] <= sigma <= sigmas[high_idx]

        low = np.log(sigmas[high_idx - 1])
        high = np.log(sigmas[high_idx])
        log_sigma = np.log(sigma)
        w = min(max((low - log_sigma) / (low - high), 0), 1)
        return (1.0 - w) * float(high_idx - 1) + w * float(high_idx)





class KarrasSampler():
    def __init__(self ):
        pass 

    def set_timesteps(self, n_inference_steps, n_training_steps=1000): #dg

        self.karras = KarrasOperations(linear_start=0.00085, linear_end=0.012, timesteps=n_training_steps, steps=n_inference_steps )

        # timesteps = np.linspace(n_training_steps - 1, 0, n_inference_steps)

        sigmasForTimesteps =  KarrasOperations.sigmas_from_alphas_cumprod(self.karras.alphas_cumprod) 
        sigmas =  self.karras.karras_sigmas(range_=np.array([sigmasForTimesteps[0], sigmasForTimesteps[999] ]))
        sigmas = np.array(sigmas)


        timesteps = [ self.karras.timestep(sigma=s , sigmas=sigmasForTimesteps ) for s in sigmas[:-1]  ]
        timesteps = np.array(timesteps)

        self.sigmas = sigmas
        self.initial_scale = sigmas.max()
        self.timesteps = timesteps
        self.n_inference_steps = n_inference_steps
        self.n_training_steps = n_training_steps
        self.step_count = 0

        self.oldDenoised = None


    def get_input_scale(self, step_count=None):
        if step_count is None:
            step_count = self.step_count
        sigma = self.sigmas[step_count]
        return 1 / (sigma ** 2 + 1) ** 0.5

    def add_noise(self, latent, noise, idx ): #dg
        for i in idx:
            assert idx[0] == i
        sc = self.sigmas[idx[0]]
        return latent + noise*sc

    # output is predicted noise et
    # step is the step id, found using t_to_i
    def step(self, output , step_count , latents , seed=None ): #dg
        
        sigma = self.sigmas[step_count]
        cOut = -1*sigma
        sigmas = self.sigmas
        
        x = latents.copy()

        denoised = x + cOut * output
        h = np.log(self.sigmas[step_count]) - np.log(self.sigmas[step_count + 1])

        if self.oldDenoised is not None and step_count < self.karras.steps - 1 :
            oldDenoised = self.oldDenoised

            hLast = np.log(sigmas[step_count - 1]) - np.log(sigmas[step_count])
            r = (h / hLast) / 2
            denoisedD = (1 + r) * denoised - r * oldDenoised
            w = sigmas[step_count + 1] / sigmas[step_count]
            x = w * x - (w - 1) * denoisedD
        elif step_count ==  self.karras.steps - 1:
            x = denoised

        else:
            w = sigmas[step_count + 1] / sigmas[step_count]
            x = w * x - (w - 1) * denoised
    
        self.oldDenoised = denoised
        return {"prev_sample": x } #latents
    



if __name__ == "__main__":



    # model = Karras(linear_start=0.1, linear_end=0.9, timesteps=10, steps=5)
    model = KarrasOperations(linear_start=0.00085, linear_end=0.012, timesteps=1_000, steps=10 )

    alphas_cumprod =  model.alphas_cumprod
    sigmasForTimesteps =  KarrasOperations.sigmas_from_alphas_cumprod(model.alphas_cumprod) 
    sigmas = model.karras_sigmas(range_=np.array([sigmasForTimesteps[0], sigmasForTimesteps[-1] ]))

    print(sigmas )
    # print("Sigmas From Alphas Cumprod:", KarrasOperations.sigmas_from_alphas_cumprod(model.alphas_cumprod))



    # print("Betas:", model.betas)
    # print("Alphas Cumprod:", model.alphas_cumprod)
    # print("Fixed Step Sigmas:", model.fixed_step_sigmas(range_=np.array([0.1, 0.9]), sigmas_for_timesteps=model.betas))
    # print("Timestep:", Karras.timestep(sigma=0.5, sigmas=model.karras_sigmas(range_=np.array([0.1, 0.9]))))