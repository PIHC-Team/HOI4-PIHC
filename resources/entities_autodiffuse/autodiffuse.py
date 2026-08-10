from hoi4dev import *

N_COUNTRIES = 67

def AutoDiffuse(ordered_layers, src_config, tgt_config, save_path, extra_imgs=list()):
    tgt_config = src_config | tgt_config
    ordered_layer_imgs = list()
    for layer in ordered_layers:
        layer_key = layer.split('_')[-1].split('.')[0]
        layer_img = ImageLoad(layer)
        if layer_key in src_config:
            src_color, tgt_color = src_config[layer_key], tgt_config[layer_key]
            if not isinstance(src_color, str): src_color = rgb2hex(src_color)
            if not isinstance(tgt_color, str): tgt_color = rgb2hex(tgt_color)
            if src_color != tgt_color:
                layer_img = ImageColorTransfer(layer_img, src_color, tgt_color, intensity=0.3)
        ordered_layer_imgs.append(layer_img)
    comp_img = ImageComposite(list(reversed(extra_imgs + ordered_layer_imgs)))
    CreateFile(save_path); ImageSave(comp_img, save_path)

ENTITIES_PATH = "../entities/viento/"
COUNTRIES_PATH = "../countries/"
def pihc_autodiffuse_pony_imperial_add_logo(logo):
    # 0. Adjust the logo color
    logo = ImageGammaCorrection(logo)
    
    # img = ImageLoad("pony/imperial/layers/layers_0006_bg.png")
    # 1. Add logo on the helmet
    helmet_logo_zoomed = ImageZoom(logo, 0.014)
    helmet_logo_rotated = ImageRotate(helmet_logo_zoomed, -50)
    helmet_logo_shifted = ImageShift(helmet_logo_rotated, 356, -139)
    helmet_logo = helmet_logo_shifted.clone()
    
    # 2. Add logo on the saddle
    saddle_logo_zoomed = ImageZoom(logo, 0.030)
    saddle_logo_rotated = ImageRotate(saddle_logo_zoomed, 47)
    saddle_logo_shifted = ImageShift(saddle_logo_rotated, 185, 235)
    saddle_logo = saddle_logo_shifted.clone()
    
    return [helmet_logo, saddle_logo]

def pihc_autodiffuse_pony_resistance_add_logo(logo):
    # 0. Adjust the logo color
    logo = ImageGammaCorrection(logo)
    
    # 1. Add logo on the helmet
    helmet_logo_zoomed = ImageZoom(logo, 0.030)
    helmet_logo_rotated = ImageRotate(helmet_logo_zoomed, 0)
    helmet_logo_shifted = ImageShift(helmet_logo_rotated, -72, 465)
    helmet_logo = helmet_logo_shifted.clone()
    
    return [helmet_logo]

def pihc_autodiffuse_pony_imperial():
    path = "pony/imperial/"
    src_config = LoadJson(pjoin(path, "color_panel.json"))
    ordered_layers = ListFiles(pjoin(path, "layers"), with_path=True, ordered=True)
    tgt_configs = {
        f.split('/')[-1].split('.')[0]: LoadJson(f)
        for f in ListFiles(pjoin(path, "configs"), with_path=True, ordered=True)
    }
    for config_name, tgt_config in tgt_configs.items():
        country_logo_path = pjoin(COUNTRIES_PATH, f"{config_name}", "logos", "default.png")
        if ExistFile(country_logo_path):
            logo = ImageLoad(country_logo_path)
            extra_imgs = pihc_autodiffuse_pony_imperial_add_logo(logo)
        else:
            extra_imgs = list()
        AutoDiffuse(ordered_layers, src_config, tgt_config, pjoin(path, "outputs", f"{config_name}", "diffuse.dds"), extra_imgs=extra_imgs)
    
    entities_path = pjoin(ENTITIES_PATH, path)
    for config_name in tgt_configs.keys():
        CreateFolder(pjoin(entities_path, config_name))
        CopyFile(pjoin(path, "outputs", config_name, "diffuse.dds"), pjoin(entities_path, config_name, "diffuse.dds"))
        info = LoadJson(pjoin(entities_path, "info.json"))
        for idx, entity in enumerate(info['entities']):
            if 'apply' in entity:
                info['entities'][idx]['apply']['countries'] = [f"{config_name}"]
            if ('attach' in entity) and ('infantry' in entity['attach']):
                info['entities'][idx]['attach']['infantry'] = f"VIENTO_PONY_IMPERIAL_{config_name}_entity"
        SaveJson(info, pjoin(entities_path, config_name, "info.json"), indent=4)
    
def pihc_autodiffuse_air_airship_add_flag(flag):
    zoomed_flag = ImageZoom(flag, r=0.175)
    mask = CreateBlankImage(zoomed_flag.width, zoomed_flag.height, color=rgb2hex((32, 32, 32)))
    mask.vignette(sigma=10, x=20, y=20)
    mask.negate(channel='rgb_channels')
    masked_flag = ImageMask(zoomed_flag, mask)
    shifted_flag = ImageShift(masked_flag, 150, -150)
    return shifted_flag

def pihc_autodiffuse_air_airship():
    path = "air/airship/"
    entities_path = pjoin(ENTITIES_PATH, path)
    airship_img = ImageLoad(pjoin(ENTITIES_PATH, "air", "airship", "diffuse.dds"))
    for i in range(N_COUNTRIES):
        c = f"C{i:02d}"
        country_flag = ImageLoad(pjoin(COUNTRIES_PATH, f"{c}", "flags", "default.png"))
        img = airship_img.clone()
        flag_img = pihc_autodiffuse_air_airship_add_flag(country_flag)
        img.composite(flag_img, gravity='center')
        # img.composite(flag_img, operator='darken', gravity='center')
        CreateFolder(pjoin(entities_path, c))
        ImageSave(img, pjoin(entities_path, c, "diffuse.dds"))
        info = LoadJson(pjoin(entities_path, "info.json"))
        for idx, entity in enumerate(info['entities']):
            if 'apply' in entity:
                info['entities'][idx]['apply']['countries'] = [f"{c}"]
        SaveJson(info, pjoin(entities_path, c, "info.json"), indent=4)

def pihc_autodiffuse_pony_resistance():
    path = "pony/resistance/"
    src_config = LoadJson(pjoin(path, "color_panel.json"))
    ordered_layers = ListFiles(pjoin(path, "layers"), with_path=True, ordered=True)
    tgt_configs = {
        f.split('/')[-1].split('.')[0]: LoadJson(f)
        for f in ListFiles(pjoin(path, "configs"), with_path=True, ordered=True)
    }
    for config_name, tgt_config in tgt_configs.items():
        country_logo_path = pjoin(COUNTRIES_PATH, f"{config_name}", "logos", "default.png")
        if ExistFile(country_logo_path):
            logo = ImageLoad(country_logo_path)
            extra_imgs = pihc_autodiffuse_pony_resistance_add_logo(logo)
        else:
            extra_imgs = list()
        AutoDiffuse(ordered_layers, src_config, tgt_config, pjoin(path, "outputs", f"{config_name}", "diffuse.dds"), extra_imgs=extra_imgs)
    
    entities_path = pjoin(ENTITIES_PATH, path)
    for config_name in tgt_configs.keys():
        CreateFolder(pjoin(entities_path, config_name))
        CopyFile(pjoin(path, "outputs", config_name, "diffuse.dds"), pjoin(entities_path, config_name, "diffuse.dds"))
        info = LoadJson(pjoin(entities_path, "info.json"))
        for idx, entity in enumerate(info['entities']):
            if 'apply' in entity:
                info['entities'][idx]['apply']['countries'] = [f"{config_name}"]
            if ('attach' in entity) and ('infantry' in entity['attach']):
                info['entities'][idx]['attach']['infantry'] = f"VIENTO_PONY_RESISTANCE_{config_name}_entity"
        SaveJson(info, pjoin(entities_path, config_name, "info.json"), indent=4)

def pihc_autodiffuse():
    pihc_autodiffuse_pony_imperial()
    pihc_autodiffuse_air_airship()
    pihc_autodiffuse_pony_resistance()

if __name__=="__main__":
    pihc_autodiffuse()
