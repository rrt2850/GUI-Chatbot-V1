# -*- coding: utf-8 -*-
# file: protogen.py
# time: 14:27 2023/1/9
# author: yangheng <hy345@exeter.ac.uk>
# github: https://github.com/yangheng95
# huggingface: https://huggingface.co/yangheng
# google scholar: https://scholar.google.com/citations?user=NPq5a_0AAAAJ&hl=en
# Copyright (C) 2021. All Rights Reserved.

from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import torch
import random

prompt = "white background, detailed, full body visible, 1girl, standing, petite, nerdy, bookworm, warm smile, urge to help, brown hair, long hair, wavy hair, blue eyes, fair, loli, small boobs, naked, small nipples, pussy"
#model_id = "darkstorm2150/Protogen_x3.4_Official_Release"
model_id = "andite/anything-v4.0"
pipe = StableDiffusionPipeline.from_pretrained(
    model_id, torch_dtype=torch.float16, safety_checker=None
)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe = pipe.to("cuda")

guidance = 7.5
width = 768
height = 512
image = pipe(
    prompt,
    num_inference_steps=25,
    guidance_scale=guidance,
    width=width,
    height=height,
).images[0]

image.save("./result.jpg")
