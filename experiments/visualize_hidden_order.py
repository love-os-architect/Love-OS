# experiments/visualize_hidden_order.py
# -*- coding: utf-8 -*-
"""
Love-OS Experiment: Visualizing the Hidden Order (Right-Brain AI)
=================================================================
"Randomness does not exist. It is a path in the Latent Space."
This script demonstrates that two seemingly random points (Seeds) 
are connected by a continuous, meaningful narrative path in the Latent Space.
"""

# 1. Install libraries (Uncomment if running in Colab)
# !pip install --upgrade diffusers transformers accelerate scipy -q

import torch
import numpy as np
from diffusers import StableDiffusionPipeline
from PIL import Image

# 2. Load Right-Brain AI (Image Generation Model)
print("Loading the Dreaming Engine...")
model_id = "runwayml/stable-diffusion-v1-5" # Lightweight and versatile model
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

# 3. Core of Intuition Engine: Interpolation function in Latent Space (Slerp)
# Instead of Linear interpolation, moving Spherically allows transformation 
# without breaking the semantic structure (Meaning).
def slerp(t, v0, v1, DOT_THRESHOLD=0.9995):
    inputs_are_torch = False
    if not isinstance(v0, np.ndarray):
        inputs_are_torch = True
        v0 = v0.cpu().numpy()
        v1 = v1.cpu().numpy()

    dot = np.sum(v0 * v1 / (np.linalg.norm(v0) * np.linalg.norm(v1)))
    if np.abs(dot) > DOT_THRESHOLD:
        v2 = (1 - t) * v0 + t * v1
    else:
        theta_0 = np.arccos(dot)
        sin_theta_0 = np.sin(theta_0)
        theta = theta_0 * t
        sin_theta = np.sin(theta)
        v2 = np.sin(theta_0 - theta) / sin_theta_0 * v0 + sin_theta / sin_theta_0 * v1

    if inputs_are_torch:
        v2 = torch.from_numpy(v2).to("cuda")
    return v2

# ==========================================
# Experiment Settings: A place to test your "Intuition"
# ==========================================
prompt = "a beautiful landscape of the future city, organic architecture, harmony with nature, highly detailed, 8k, concept art"
# prompt = "abstract representation of Love and Physics, unified theory, glowing energy, mathematical beauty" # Abstract themes are also recommended

seed_start = 42   # The "Meaning" of the starting point
seed_end = 999    # The "Meaning" of the destination
steps = 10        # Number of "Story" frames in between

# 4. Generating Latent Space
print(f"Traversing the Latent Space from Seed {seed_start} to {seed_end}...")
generator_start = torch.Generator("cuda").manual_seed(seed_start)
generator_end = torch.Generator("cuda").manual_seed(seed_end)

# Generate Noise (Undeciphered Order R)
latents_start = torch.randn((1, pipe.unet.config.in_channels, 64, 64), generator=generator_start, device="cuda", dtype=torch.float16)
latents_end = torch.randn((1, pipe.unet.config.in_channels, 64, 64), generator=generator_end, device="cuda", dtype=torch.float16)

# 5. Execution of the Journey (Interpolation and Generation)
images = []
for i, t in enumerate(np.linspace(0, 1, steps)):
    # Smoothly connect two Seeds using 'Spherical Interpolation'
    latents_interpolated = slerp(t, latents_start, latents_end)

    # Decode latent variables into images (Visualizing Intuition)
    with torch.no_grad():
        image = pipe(prompt, num_inference_steps=30, latents=latents_interpolated).images[0]
    
    images.append(image)
    print(f"Step {i+1}/{steps}: Decoding hidden order...")

# 6. Display Results (Combined like a GIF animation)
def create_grid(imgs, rows=1, cols=None):
    if cols is None: cols = len(imgs)
    w, h = imgs[0].size
    grid = Image.new('RGB', (cols*w, rows*h))
    for i, img in enumerate(imgs):
        grid.paste(img, (i*w, 0))
    return grid

# Display as one long strip image
grid_img = create_grid(images)

# If running in Colab/Jupyter:
try:
    display(grid_img)
except NameError:
    grid_img.show()

# Save the proof of continuous order
grid_img.save("latent_space_journey.png")
print("Experiment Complete. 'Randomness' was actually a continuous bridge.")
