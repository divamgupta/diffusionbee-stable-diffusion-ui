// For licensing see accompanying LICENSE.md file.
// Copyright (C) 2022 Apple Inc. All Rights Reserved.

import Foundation
import CoreML
import Accelerate
import CoreGraphics
import Dispatch


/// Schedulers compatible with StableDiffusionPipeline
public enum StableDiffusionScheduler {
    /// Scheduler that uses a pseudo-linear multi-step (PLMS) method
    case pndmScheduler
    /// Scheduler that uses a second order DPM-Solver++ algorithm
    case dpmSolverMultistepScheduler
}

/// A pipeline used to generate image samples from text input using stable diffusion
///
/// This implementation matches:
/// [Hugging Face Diffusers Pipeline](https://github.com/huggingface/diffusers/blob/main/src/diffusers/pipelines/stable_diffusion/pipeline_stable_diffusion.py)
@available(iOS 16.2, macOS 13.1, *)

public struct StableDiffusionPipeline: ResourceManaging {

    /// Model to generate embeddings for tokenized input text
    var textEncoder: TextEncoder

    /// Model used to predict noise residuals given an input, diffusion time step, and conditional embedding
    var unet: Unet

    /// Model used to generate final image from latent diffusion process
    var decoder: Decoder

    /// Optional model for checking safety of generated image
    var safetyChecker: SafetyChecker? = nil


    /// Reports whether this pipeline can perform safety checks
    public var canSafetyCheck: Bool {
        safetyChecker != nil
    }

    /// Option to reduce memory during image generation
    ///
    /// If true, the pipeline will lazily load TextEncoder, Unet, Decoder, and SafetyChecker
    /// when needed and aggressively unload their resources after
    ///
    /// This will increase latency in favor of reducing memory
    var reduceMemory: Bool = false

    /// Creates a pipeline using the specified models and tokenizer
    ///
    /// - Parameters:
    ///   - textEncoder: Model for encoding tokenized text
    ///   - unet: Model for noise prediction on latent samples
    ///   - decoder: Model for decoding latent sample to image
    ///   - safetyChecker: Optional model for checking safety of generated images
    ///   - reduceMemory: Option to enable reduced memory mode
    /// - Returns: Pipeline ready for image generation
    public init(textEncoder: TextEncoder,
                unet: Unet,
                decoder: Decoder,
                safetyChecker: SafetyChecker? = nil,
                reduceMemory: Bool = false) {
        self.textEncoder = textEncoder
        self.unet = unet
        self.decoder = decoder
        self.safetyChecker = safetyChecker
        self.reduceMemory = reduceMemory
    }
    
    

    /// Load required resources for this pipeline
    ///
    /// If reducedMemory is true this will instead call prewarmResources instead
    /// and let the pipeline lazily load resources as needed
    public func loadResources() throws {
        if reduceMemory {
            try prewarmResources()
        } else {
            try textEncoder.loadResources()
            try unet.loadResources()
            try decoder.loadResources()
            try safetyChecker?.loadResources()
        }
    }

    /// Unload the underlying resources to free up memory
    public func unloadResources() {
        textEncoder.unloadResources()
        unet.unloadResources()
        decoder.unloadResources()
        safetyChecker?.unloadResources()
    }

    // Prewarm resources one at a time
    public func prewarmResources() throws {
        try textEncoder.prewarmResources()
        print("sdbk mlpr 25")
        print("sdbk mlms done 25 of 100.0")
        try unet.prewarmResources()
        print("sdbk mlpr 50")
        print("sdbk mlms done 75 of 100.0")
        try decoder.prewarmResources()
        print("Decoder prewarmed")
        print("sdbk mlpr 100")
        print("sdbk mlms done 100 of 100.0")
        try safetyChecker?.prewarmResources()
        print("SafetyChecker prewarmed")
    }



    /// Text to image generation using stable diffusion
    ///
    /// - Parameters:
    ///   - prompt: Text prompt to guide sampling
    ///   - negativePrompt: Negative text prompt to guide sampling
    ///   - stepCount: Number of inference steps to perform
    ///   - imageCount: Number of samples/images to generate for the input prompt
    ///   - seed: Random seed which
    ///   - guidanceScale: Controls the influence of the text prompt on sampling process (0=random images)
    ///   - disableSafety: Safety checks are only performed if `self.canSafetyCheck && !disableSafety`
    ///   - progressHandler: Callback to perform after each step, stops on receiving false response
    /// - Returns: An array of `imageCount` optional images.
    ///            The images will be nil if safety checks were performed and found the result to be un-safe
    public func generateImages(
        prompt: String,
        negativePrompt: String = "",
        imageCount: Int = 1,
        stepCount: Int = 50,
        seed: UInt32 = 0,
        guidanceScale: Float = 7.5,
        input_image: CGImage? = nil,
        mask_image: CGImage? = nil,
        input_image_strength: Float = 0.5,
        disableSafety: Bool = false,
        scheduler: StableDiffusionScheduler = .pndmScheduler,
        progressHandler: (Progress) -> Bool = { _ in true }
    ) throws -> [CGImage?] {

        // Encode the input prompt and negative prompt
        let promptEmbedding = try textEncoder.encode(prompt)
        let negativePromptEmbedding = try textEncoder.encode(negativePrompt)

        let stdinQueue = DispatchQueue(label: "my.serial.queue")
        var inputCharacters: [CChar] = []

        let stdinSource = DispatchSource.makeReadSource(fileDescriptor: STDIN_FILENO, queue: stdinQueue)
        stdinSource.setEventHandler(handler: {
            var c = CChar()
            if read(STDIN_FILENO, &c, 1) == 1 {
                inputCharacters.append(c);
            }
        })
        stdinSource.resume()

        // Return next input character, or `nil` if there is none.
        func getch() -> CChar? {
            return stdinQueue.sync {
                inputCharacters.isEmpty ? nil : inputCharacters.remove(at: 0)
            }
        }

        func gets() -> String {
            var input = ""
            while let c = getch() {
                if c == 10 {
                    break
                }
                input.append(Character(UnicodeScalar(UInt8(c))))
            }
            return input
        }

        if reduceMemory {
            textEncoder.unloadResources()
        }

        // Convert to Unet hidden state representation
        // Concatenate the prompt and negative prompt embeddings
        let concatEmbedding = MLShapedArray<Float32>(
            concatenating: [negativePromptEmbedding, promptEmbedding],
            alongAxis: 0
        )

        let hiddenStates = toHiddenStates(concatEmbedding)

        /// Setup schedulers
        let scheduler: [Scheduler] = (0..<imageCount).map { _ in
            switch scheduler {
            case .pndmScheduler: return PNDMScheduler(stepCount: stepCount)
            case .dpmSolverMultistepScheduler: return DPMSolverMultistepScheduler(stepCount: stepCount)
            }
        }
        let stdev = scheduler[0].initNoiseSigma


        // Generate random latent samples from specified seed
        var latents = generateLatentSamples(imageCount, stdev: stdev, seed: seed)

        // De-noising loop
        for (step,t) in scheduler[0].timeSteps.enumerated() {
            let input = gets()
            if input == "b2s t2im __stop__" {
                return []
            }

            // Expand the latents for classifier-free guidance
            // and input to the Unet noise prediction model
            let latentUnetInput = latents.map {
                MLShapedArray<Float32>(concatenating: [$0, $0], alongAxis: 0)
            }

            // Predict noise residuals from latent samples
            // and current time step conditioned on hidden states
            var noise = try unet.predictNoise(
                latents: latentUnetInput,
                timeStep: t,
                hiddenStates: hiddenStates
            )

            noise = performGuidance(noise, guidanceScale)

            // Have the scheduler compute the previous (t-1) latent
            // sample given the predicted noise and current sample
            for i in 0..<imageCount {
                latents[i] = scheduler[i].step(
                    output: noise[i],
                    timeStep: t,
                    sample: latents[i]
                )
            }

            // Report progress
            let progress = Progress(
                pipeline: self,
                prompt: prompt,
                step: step,
                stepCount: stepCount,
                currentLatentSamples: latents,
                isSafetyEnabled: canSafetyCheck && !disableSafety
            )
            if !progressHandler(progress) {
                // Stop if requested by handler
                return []
            }
        }

        if reduceMemory {
            unet.unloadResources()
        }

        // Decode the latent samples to images
        return try decodeToImages(latents, disableSafety: disableSafety)
    }

    func generateLatentSamples(_ count: Int, stdev: Float, seed: UInt32) -> [MLShapedArray<Float32>] {
        // func generateLatentSamples(_ count: Int, stdev: Float, seed: UInt32, input_image: CGImage? = nil, mask_image: CGImage? = nil, input_img_noise_t) -> [MLShapedArray<Float32>] {
        // func generateLatentSamples(_ count: Int, stdev: Float, seed: UInt32, input_image: CGImage? = nil, mask_image: CGImage? = nil, input_img_noise_t: Float) -> [MLShapedArray<Float32>] {
        // var sampleShape = unet.latentSampleShape
        // sampleShape[0] = 1

        // let samples = (0..<count).map { i in
        //     let seed = seed + UInt32(1234*i) % UInt32.max
        //     var random = NumPyRandomSource(seed: seed)
        //     return MLShapedArray<Float32>(
        //         converting: random.normalShapedArray(sampleShape, mean: 0.0, stdev: Double(stdev)))
        // }
        // return samples

///////
//         alphas = [_ALPHAS_CUMPROD[t] for t in timesteps]
//         alphas_prev = [1.0] + alphas[:-1]

//         if input_image is None or self.is_sd_15_inpaint :
//             latent_np = np.random.RandomState(seed).normal(size=(batch_size, n_h, n_w, 4)).astype('float32')
//             latent = tf.convert_to_tensor(latent_np)
//         else:
//             latent = self.encoder_f(input_image[None])
//             latent = self.add_noise(latent, input_img_noise_t, seed)
//             latent = tf.repeat(latent , batch_size , axis=0)
////////
        

        // if input_image == nil {
            var sampleShape = unet.latentSampleShape
            sampleShape[0] = 1

            let samples = (0..<count).map { i in
                let seed = seed + UInt32(1234*i) % UInt32.max
                var random = NumPyRandomSource(seed: seed)
                return MLShapedArray<Float32>(
                    converting: random.normalShapedArray(sampleShape, mean: 0.0, stdev: Double(stdev)))
            }
            return samples
        // } 
    }

    func toHiddenStates(_ embedding: MLShapedArray<Float32>) -> MLShapedArray<Float32> {
        // Unoptimized manual transpose [0, 2, None, 1]
        // e.g. From [2, 77, 768] to [2, 768, 1, 77]
        let fromShape = embedding.shape
        let stateShape = [fromShape[0],fromShape[2], 1, fromShape[1]]
        var states = MLShapedArray<Float32>(repeating: 0.0, shape: stateShape)
        for i0 in 0..<fromShape[0] {
            for i1 in 0..<fromShape[1] {
                for i2 in 0..<fromShape[2] {
                    states[scalarAt:i0,i2,0,i1] = embedding[scalarAt:i0, i1, i2]
                }
            }
        }
        return states
    }

    func performGuidance(_ noise: [MLShapedArray<Float32>], _ guidanceScale: Float) -> [MLShapedArray<Float32>] {
        noise.map { performGuidance($0, guidanceScale) }
    }

    func performGuidance(_ noise: MLShapedArray<Float32>, _ guidanceScale: Float) -> MLShapedArray<Float32> {

        let blankNoiseScalars = noise[0].scalars
        let textNoiseScalars = noise[1].scalars

        var resultScalars =  blankNoiseScalars

        for i in 0..<resultScalars.count {
            // unconditioned + guidance*(text - unconditioned)
            resultScalars[i] += guidanceScale*(textNoiseScalars[i]-blankNoiseScalars[i])
        }

        var shape = noise.shape
        shape[0] = 1
        return MLShapedArray<Float32>(scalars: resultScalars, shape: shape)
    }

    func decodeToImages(_ latents: [MLShapedArray<Float32>],
                        disableSafety: Bool) throws -> [CGImage?] {

        let images = try decoder.decode(latents)
        if reduceMemory {
            decoder.unloadResources()
        }

        // If safety is disabled return what was decoded
        if disableSafety {
            return images
        }

        // If there is no safety checker return what was decoded
        guard let safetyChecker = safetyChecker else {
            return images
        }

        // Otherwise change images which are not safe to nil
        let safeImages = try images.map { image in
            try safetyChecker.isSafe(image) ? image : nil
        }

        if reduceMemory {
            safetyChecker.unloadResources()
        }

        return safeImages
    }

}

@available(iOS 16.2, macOS 13.1, *)
extension StableDiffusionPipeline {
    /// Sampling progress details
    public struct Progress {
        public let pipeline: StableDiffusionPipeline
        public let prompt: String
        public let step: Int
        public let stepCount: Int
        public let currentLatentSamples: [MLShapedArray<Float32>]
        public let isSafetyEnabled: Bool
        public var currentImages: [CGImage?] {
            try! pipeline.decodeToImages(
                currentLatentSamples,
                disableSafety: !isSafetyEnabled)
        }
    }
}
