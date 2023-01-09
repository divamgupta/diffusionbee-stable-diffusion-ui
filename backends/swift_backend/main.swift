// For licensing see accompanying LICENSE.md file.
// Copyright (C) 2022 Apple Inc. All Rights Reserved.

import CoreML
import StableDiffusion
import UniformTypeIdentifiers

import Darwin
setbuf(stdout, nil)

enum RunError: Error {
    case resources(String)
    case saving(String)
}

enum SchedulerOption: String {
    case pndm, dpmpp
    var stableDiffusionScheduler: StableDiffusionScheduler {
        switch self {
        case .pndm: return .pndmScheduler
        case .dpmpp: return .dpmSolverMultistepScheduler
        }
    }
}

func log(_ str: String, term: String = "") {
       print(str, terminator: term)
}

let fm = FileManager.default

struct DiffusionBee {
    var resourcePath: String = fm.homeDirectoryForCurrentUser.path+"/.diffusionbee/coreml_models/coreml-stable-diffusion-v1-5_split_einsum_compiled"
    var outputPath: String = fm.homeDirectoryForCurrentUser.path+"/.diffusionbee/images"
    var disableSafety: Bool = true
    var reduceMemory: Bool = true

    var prompt: String = ""
    var negativePrompt: String = ""
    
    var imageCount: Int = 1
    var seed: UInt32 = 93
    var saveEvery: Int = 0
    
    func handleProgress(
            _ progress: StableDiffusionPipeline.Progress,
            _ sampleTimer: SampleTimer
        ) { 
            log("\u{1B}[1A\u{1B}[K")
            log("Step \(progress.step) of \(progress.stepCount) ")
            log(" [")
            log(String(format: "mean: %.2f, ", 1.0/sampleTimer.mean))
            log(String(format: "median: %.2f, ", 1.0/sampleTimer.median))
            log(String(format: "last %.2f", 1.0/sampleTimer.allSamples.last!))
            log("] step/sec")
            // print("sdbk dnpr "+str(i) ) # done percentage
           if saveEvery > 0, progress.step % saveEvery == 0 {
               let saveCount = (try? saveImages(progress.currentImages, step: progress.step, logNames: true))?.count ?? 0
               log(" saved \(saveCount) image\(saveCount != 1 ? "s" : "")")
           }
            log("\n")
            let progressPercentage = Float(progress.step) / Float(progress.stepCount)
            let progressPercentageInt = Int(ceil(progressPercentage * 100))
            print("sdbk dnpr \(progressPercentageInt)")
        }
            
    func saveImages(
            _ images: [CGImage?],
            step: Int? = nil,
            logNames: Bool = false
    ) throws -> [String] {
            let url = URL(filePath: outputPath)
            var saved = [String]()
            for i in 0 ..< images.count {

                guard let image = images[i] else {
                    if logNames {
                        log("Image \(i) failed safety check and was not saved")
                    }
                    continue
                }
                let name = imageName(i, step: step)
                let fileURL = url.appending(path:name)

                guard let dest = CGImageDestinationCreateWithURL(fileURL as CFURL, UTType.png.identifier as CFString, 1, nil) else {
                    throw RunError.saving("Failed to create destination for \(fileURL)")
                }
                CGImageDestinationAddImage(dest, image, nil)
                if !CGImageDestinationFinalize(dest) {
                    throw RunError.saving("Failed to save \(fileURL)")
                }
                if logNames {
                    log("Saved \(name)\n")
                    print("sdbk nwim \(fileURL.path)")
                }
                saved.append(fileURL.path)
            }
            return saved
        }
        func imageName(_ sample: Int, step: Int? = nil) -> String {
        let fileCharLimit = 75
            var name = "\(seed)"
            name += prompt.prefix(fileCharLimit).replacingOccurrences(of: " ", with: "_")
        if imageCount != 1 {
            name += "_\(sample)"
        }
        name += ".png"
        return name
    }

    mutating func run() throws {
        guard FileManager.default.fileExists(atPath: resourcePath) else {
        throw RunError.resources("Resource path does not exist \(resourcePath)")
        }
        let config = MLModelConfiguration()

        print("sdbk mltl Loading Model")
        
        let resourceURL = URL(filePath: resourcePath)
        let computeUnits: MLComputeUnits = .cpuAndNeuralEngine
        
        config.computeUnits = computeUnits
        
        print("sdbk gnms  Loading SD Model"  )
        let pipeline = try StableDiffusionPipeline(resourcesAt: resourceURL,
                                                           configuration: config,
                                                           disableSafety: disableSafety,
                                                           reduceMemory: reduceMemory)
        try pipeline.loadResources()
        print("sdbk mdvr 1.5CoreML")
        

        print("sdbk mlpr -1")
        print("sdbk mdld")

        while true {
             print("sdbk inrd") // input ready
             let input = readLine()!
             if input == "" {
                 continue
             }

             if !input.contains("b2s t2im") {
                 continue
             }

             let inp_str = input.replacingOccurrences(of: "b2s t2im", with: "").trimmingCharacters(in: .whitespacesAndNewlines)

            var d = ["W":512, "H":512, "num_imgs":1, "ddim_steps":25, "scale":7.5, "batch_size":1, "input_image":"", "img_strength":0.5, "negative_prompt":"", "mask_image":"", "model_id":0, "custom_model_path":"", "save_every": 0] as [String : Any]

            let d_ = try JSONSerialization.jsonObject(with: inp_str.data(using: .utf8)!, options: []) as! [String:Any]
            for (k,v) in d_ {
                d[k] = v
            }
            print("sdbk inwk") // working on the input

            print("Sampling ...\n")
            let sampleTimer = SampleTimer()
            sampleTimer.start()


            prompt = d["prompt"] as! String
            negativePrompt = d["negative_prompt"] as! String
            imageCount = d["num_imgs"] as! Int
            saveEvery = d["save_every"] as! Int
            let stepCount = d["ddim_steps"] as! Int
            let guidanceScale = d["scale"] as! Double

            seed = d["seed"] as? UInt32 ?? UInt32.random(in: 0...UInt32.max)

            var scheduler: SchedulerOption = .pndm
            
            let images = try pipeline.generateImages(
                       prompt: prompt,
                       negativePrompt: negativePrompt,
                       imageCount: imageCount,
                       stepCount: stepCount,
                       seed: seed,
                       guidanceScale: Float(guidanceScale),
                       scheduler: scheduler.stableDiffusionScheduler
                   ) { progress in
                       sampleTimer.stop()
                       handleProgress(progress,sampleTimer)
                       if progress.stepCount != progress.step {
                           sampleTimer.start()
                       }
                       return true
                   }
            let _ = try saveImages(images, logNames: true)
            print("sdbk igws")
            

        }
    }
}
if #available(iOS 16.2, macOS 13.1, *) {
    var diffusionbee  = DiffusionBee()
    try diffusionbee.run()
} else {
    print("Unsupported OS")
}
