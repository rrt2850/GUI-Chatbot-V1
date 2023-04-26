import os
import time
import zipfile
import findfile

from CharacterClass import Character

for z_file in findfile.find_cwd_files(and_key=['.zip'],
                                      exclude_key=['.ignore', 'git', 'SuperResolutionAnimeDiffusion'],
                                      recursive=1):
    with zipfile.ZipFile(z_file, 'r') as zip_ref:
        zip_ref.extractall()

import PIL.Image
import autocuda
from pyabsa.utils.pyabsa_utils import fprint

from diffusers import (
    AutoencoderKL,
    UNet2DConditionModel,
    StableDiffusionPipeline,
    StableDiffusionImg2ImgPipeline,
    DPMSolverMultistepScheduler,
)
import torch
from PIL import Image
import datetime
import time
import psutil
from Waifu2x.magnify import ImageMagnifier
from RealESRGANv030.interface import realEsrgan

magnifier = ImageMagnifier()

start_time = time.time()
is_colab = False

device = autocuda.auto_cuda()
dtype = torch.float16 if device != "cpu" else torch.float32

class Model:
    def __init__(self, name, path="", prefix=""):
        self.name = name
        self.path = path
        self.prefix = prefix
        self.pipe_t2i = None
        self.pipe_i2i = None


models = [
    # Model("anything v3", "Linaqruf/anything-v3.0", "anything v3 style"),
    Model("anything v4.5", "andite/anything-v4.0", "anything v4.5 style"),
]
#Model("Balloon Art", "Fictiverse/Stable_Diffusion_BalloonArt_Model", "BalloonArt ")
#  Model("Spider-Verse", "nitrosocke/spider-verse-diffusion", "spiderverse style "),
#  Model("Elden Ring", "nitrosocke/elden-ring-diffusion", "elden ring style "),
#  Model("Tron Legacy", "dallinmackay/Tron-Legacy-diffusion", "trnlgcy ")
# Model("Pokémon", "lambdalabs/sd-pokemon-diffusers", ""),
# Model("Pony Diffusion", "AstraliteHeart/pony-diffusion", ""),
# Model("Robo Diffusion", "nousr/robo-diffusion", ""),

scheduler = DPMSolverMultistepScheduler(
    beta_start=0.00085,
    beta_end=0.012,
    beta_schedule="scaled_linear",
    num_train_timesteps=1000,
    trained_betas=None,
    #predict_epsilon=True,
    thresholding=False,
    algorithm_type="dpmsolver++",
    solver_type="midpoint",
    solver_order=2,
    # lower_order_final=True,
)

custom_model = None
if is_colab:
    models.insert(0, Model("Custom model"))
    custom_model = models[0]

last_mode = "txt2img"
current_model = models[1] if is_colab else models[0]
current_model_path = current_model.path

if is_colab:
    device = autocuda.auto_cuda()
    dtype = torch.float16 if device != "cpu" else torch.float32
    pipe = StableDiffusionPipeline.from_pretrained(
        current_model.path,
        torch_dtype=dtype,
        scheduler=scheduler,
        safety_checker=lambda images, clip_input: (images, False),
    )

else:  # download all models
    print(f"{datetime.datetime.now()} Downloading vae...")
    device = autocuda.auto_cuda()
    dtype = torch.float16 if device != "cpu" else torch.float32
    vae = AutoencoderKL.from_pretrained(
        current_model.path, subfolder="vae", torch_dtype=dtype
    )
    for model in models:
        try:
            print(f"{datetime.datetime.now()} Downloading {model.name} model...")
            unet = UNet2DConditionModel.from_pretrained(
                model.path, subfolder="unet", torch_dtype=dtype
            )
            model.pipe_t2i = StableDiffusionPipeline.from_pretrained(
                model.path,
                unet=unet,
                vae=vae,
                torch_dtype=dtype,
                scheduler=scheduler,
                safety_checker=None,
            )
            model.pipe_i2i = StableDiffusionImg2ImgPipeline.from_pretrained(
                model.path,
                unet=unet,
                vae=vae,
                torch_dtype=dtype,
                scheduler=scheduler,
                safety_checker=None,
            )
        except Exception as e:
            print(
                f"{datetime.datetime.now()} Failed to load model "
                + model.name
                + ": "
                + str(e)
            )
            models.remove(model)
    pipe = models[0].pipe_t2i

# model.pipe_i2i = torch.compile(model.pipe_i2i)
# model.pipe_t2i = torch.compile(model.pipe_t2i)
pipe = pipe.to(device)

device = autocuda.auto_cuda() if torch.cuda.is_available() else "cpu"

def error_str(error, title="Error"):
    return (
        f"""#### {title}
            {error}"""
        if error
        else ""
    )

def inference(
    model_name,
    prompt,
    guidance,
    steps,
    width=512,
    height=512,
    seed=0,
    img=None,
    strength=0.5,
    neg_prompt="",
    scale="ESRGAN4x",
    scale_factor=2,
    filepath="",
    ):
    fprint(psutil.virtual_memory())  # print memory usage
    
    global current_model
    for model in models:
        if model.name == model_name:
            current_model = model
            model_path = current_model.path

    device = autocuda.auto_cuda()
    dtype = torch.float16 if "cuda" in device else torch.float32
    generator = torch.Generator(device).manual_seed(seed) if seed != 0 else None
    try:
        if img is not None:
            return (
                img_to_img(
                    model_path,
                    prompt,
                    neg_prompt,
                    img,
                    strength,
                    guidance,
                    steps,
                    width,
                    height,
                    generator,
                    scale,
                    scale_factor,
                    filepath,
                ),
                None,
            )
        else:
            return (
                txt_to_img(
                    model_path,
                    prompt,
                    neg_prompt,
                    guidance,
                    steps,
                    width,
                    height,
                    generator,
                    scale,
                    scale_factor,
                    filepath
                ),
                None,
            )
    except Exception as e:
        return None, error_str(e)
    
def txt_to_img(
    model_path,
    prompt,
    neg_prompt,
    guidance,
    steps,
    width,
    height,
    generator,
    scale,
    scale_factor,
    filepath=""
    ):
    print(f"{datetime.datetime.now()} txt_to_img, model: {current_model.name}")
    device = autocuda.auto_cuda()
    dtype = torch.float16 if "cuda" in device else torch.float32
     
    global last_mode
    global pipe
    global current_model_path
    if model_path != current_model_path or last_mode != "txt2img":
        current_model_path = model_path

        if is_colab or current_model == custom_model:
            pipe = StableDiffusionPipeline.from_pretrained(
                current_model_path,
                torch_dtype=dtype,
                scheduler=scheduler,
                safety_checker=lambda images, clip_input: (images, False),
            )
        else:
            # pipe = pipe.to("cpu")
            pipe = current_model.pipe_t2i

        pipe = pipe.to(device)
        
    prompt = current_model.prefix + prompt
    try:
        result = pipe(
            prompt,
            negative_prompt=neg_prompt,
            # num_images_per_prompt=n_images,
            num_inference_steps=int(steps),
            guidance_scale=guidance,
            width=width,
            height=height,
            generator=generator,
        )
    except Exception as e:
        print("Failed to generate image: " + str(e))
        return None

    # result.images[0] = magnifier.magnify(result.images[0], scale_factor=scale_factor)
    # enhance resolution
    if scale_factor > 1:
        if scale == "ESRGAN4x":
            fp32 = True if device == "cpu" else False

            try:
                result.images[0] = realEsrgan(
                    input_dir=result.images[0],
                    suffix="",
                    output_dir="imgs",
                    fp32=fp32,
                    outscale=scale_factor,
                )[0]
            except Exception as e:
                print("Failed to enhance resolution: " + str(e))
        else:
            print("magnifying image")
            result.images[0] = magnifier.magnify(
                result.images[0], scale_factor=scale_factor
            )
    # save image
    if filepath == "":
        print("saving image")
        result.images[0].save(
            "imgs/result-{}.png".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f"))
        )
    else:
        print("saving image, filepath: {}".format(filepath))
        result.images[0].save("characterImages/{}-{}.png".format(filepath, datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")))
    return replace_nsfw_images(result)

def img_to_img(
    model_path,
    prompt,
    neg_prompt,
    img,
    strength,
    guidance,
    steps,
    width,
    height,
    generator,
    scale,
    scale_factor,
    filepath="",):
    device = autocuda.auto_cuda()
    #dtype = torch.float16 if "cuda" in device else torch.float32
    dtype = torch.float32
    global last_mode
    global pipe
    global current_model_path

    if(type(img) == str):
        img = Image.open(img).convert("RGB")
    if model_path != current_model_path or last_mode != "img2img":
        current_model_path = model_path

        if is_colab or current_model == custom_model:
            pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
                model_id_or_path=current_model_path,
                torch_dtype=dtype,
                scheduler=scheduler,
                safety_checker=lambda images, clip_input: (images, False),
            )
        
        else:
            # pipe = pipe.to("cpu")
            pipe = current_model.pipe_i2i

        device = autocuda.auto_cuda()
        pipe = pipe.to(device)

    prompt = current_model.prefix + f" {prompt}"
    last_mode = "img2img"

    ratio = min(height / img.height, width / img.width)
    img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
    
    try:
        result = pipe(
            prompt,
            negative_prompt=neg_prompt,
            # num_images_per_prompt=n_images,
            image=img,
            num_inference_steps=int(steps),
            strength=strength,
            guidance_scale=guidance,
            # width=width,
            # height=height,
            generator=generator,
        )
    except Exception as e:
        print(torch.cuda.memory_summary(device=device, abbreviated=False))
        print(e)
    
    result.images[0].save(
            
            "imgs/result-{}.png".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f"))
        )
    if scale_factor > 1:
        if scale == "ESRGAN4x":
            print("scaling image")
            fp32 = True #if device == "cpu" else False
            result.images[0] = realEsrgan(
                input_dir=result.images[0],
                suffix="",
                output_dir="imgs",
                fp32=fp32,
                outscale=scale_factor,
            )[0]
        else:
            result.images[0] = magnifier.magnify(
                result.images[0], scale_factor=scale_factor
            )
    # save image
    if filepath == "":
        print("saving image")
        result.images[0].save(
            
            "imgs/result-{}.png".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f"))
        )
    else:
        result.images[0].save("characterImages/{}-{}.png".format(filepath, datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")))
    return replace_nsfw_images(result)

def replace_nsfw_images(results):
    # do something with this if you want to put this online (stops you from getting cancelled)
    return results.images[0]
    if is_colab:
        return results.images[0]
    if hasattr(results, "nsfw_content_detected") and results.nsfw_content_detected:
        for i in range(len(results.images)):
            if results.nsfw_content_detected[i]:
                results.images[i] = Image.open("nsfw.png")
    return results.images[0]

def genStanding(filepath: str = None, posValues:str = None, negValues:str = None, character:Character = None):
    model_name = "anything v4.5"
    prompt = "standing, facing camera, full body, vertical, solo, detailed"
    if character is not None:
        if character.gender=="female":
            prompt += ", 1girl"
        elif character.gender=="male":
            prompt += ", 1boy"
        if filepath is None:
            filepath = f"characterImages/{character.name}"
            os.makedirs(filepath, exist_ok=True)
            filepath += f"/{character.name}"
    prompt += ", " + posValues
    guidance = 17
    steps = 70
    width = 720
    height = 1120
    seed=0
    img=None
    strength=.8,
    neg_prompt=negValues + """, background, colorful background, bad result, worst, random, invalid, inaccurate, imperfect, blurry, deformed, disfigured, mutation, mutated, ugly, out of focus, bad anatomy, text, error,
                extra digit, fewer digits, worst quality, low quality, normal quality, noise, jpeg artifact, compression artifact, signature, watermark, username, logo, 
                low resolution, worst resolution, bad resolution, normal resolution, bad detail, bad details, bad lighting, bad shadow, bad shading, bad background,
                worst background."""
    scale="ESRGAN4x"
    scale_factor=2

    inference(model_name=model_name, prompt=prompt, neg_prompt=neg_prompt, img=img, strength=strength, guidance=guidance, steps=steps, width=width, height=height, seed=seed, scale=scale, scale_factor=scale_factor, filename=filepath)

    

if __name__ == "__main__":
    model_name = "anything v4.5"
    prompt = "detailed, sprite sheet, spritesheet, reference sheet, multiple girls, black hair, wavy hair, small breasts"
    guidance = 17
    steps = 30
    width = 2000
    height = 2000
    seed=0
    img="spriteSheet.png"
    strength=.7
    neg_prompt="""shirt, bad result, worst, random, invalid, inaccurate, imperfect, blurry, deformed, disfigured, mutation, mutated, ugly, out of focus, bad anatomy, text, error,
                extra digit, fewer digits, worst quality, low quality, normal quality, noise, jpeg artifact, compression artifact, signature, watermark, username, logo, 
                low resolution, worst resolution, bad resolution, normal resolution, bad detail, bad details, bad lighting, bad shadow, bad shading, bad background,
                worst background."""
    scale="ESRGAN4x"
    scale_factor=8
    inference(model_name, prompt, guidance, steps, width, height, seed, img, strength,neg_prompt, scale, scale_factor)
    