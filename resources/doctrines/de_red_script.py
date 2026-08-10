# %%
from PIL import Image

def is_reddish(pixel, red_threshold=100, black_threshold=50):
    r, g, b, a = pixel
    return (r > g+b or (r <= black_threshold and g <= black_threshold and b <= black_threshold) )

def remove_red_black_pixels(image_path):
    img = Image.open(image_path)
    pixels = img.load()

    for i in range(img.size[0]):
        for j in range(img.size[1]):
            if is_reddish(pixels[i, j]):
                r, g, b, a = pixels[i, j]
                pixels[i, j] = (r, g, b, a//3) # Keep some alpha so that the border is not too sharp
    return img

de_red_folders = set(open("de_red_doctrines.txt", "r").read().split("\n"))

# Path to the input PNG image
from pyheaven import *
for folder in ListFolders("./"):
    if folder in de_red_folders:
        continue
    img = remove_red_black_pixels(pjoin(folder, "default.png"))
    img.save(pjoin(folder, "default.png"))
    de_red_folders.add(folder)

# %%
with open("de_red_doctrines.txt", "w") as f:
    f.write("\n".join(de_red_folders))

# %%