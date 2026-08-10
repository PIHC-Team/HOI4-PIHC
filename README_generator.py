
# %%
MORE = {
    "zh": "详见完整版文档。",
    "en": "See full documentation for more details."
}
def manual_cuts_steamdown(file, mode='en'):
    with open(file, "r") as f:
        content = f.read()
    
    sections = content.split('[h2]')
    sections = [sections[0]] + ['[h2]'+sec for sec in sections[1:]]
    
    cutted_contents = []
    cutted_contents.append(
"""[h2] Both English and Chinese are supported! 中英文支持！ [/h2]

[h2][url=https://drive.google.com/file/d/1kHr0KarnZwIWu95U-9BfMzLN-cupUKLD/view?usp=sharing]Full English Documentation[/url][/h2]
[h2][url=https://drive.google.com/file/d/1J3C3PZd9dliNcITBB1DX_YKaopArv1C5/view?usp=sharing]完整中文文档[/url][/h2]

Discord: [url=https://discord.gg/VzUUMF9af5][/url]
QQ Group: 934449651

"""
    )
    for sec in sections:
        if  (  sec.startswith("[h2]Update Log[/h2]")
            or sec.startswith("[h2]更新日志[/h2]")
        ):
            sub_sections = sec.split("[h3]")
            sub_sections = [sub_sections[0]] + ['[h3]'+sub for sub in sub_sections[1:]]
            recent_2 = sub_sections[:3]
            update_log = "".join(recent_2) + f"...\n{MORE[mode]}\n\n"
            cutted_contents.append(update_log)
        elif ( sec.startswith("[h2]Acknowledgement[/h2]")
            or sec.startswith("[h2]致谢[/h2]")
        ):
            ack = (sec.split("    [*]Expanded Resources")[0] + f"[/list]\n...\n{MORE[mode]}\n\n")
            cutted_contents.append(ack)
        elif ( sec.startswith("[h2]Non-steam Installation[/h2]")
            or sec.startswith("[h2]非Steam安装[/h2]")
        ):
            continue
        elif ( sec.startswith("[h2]About HOI4DEV[/h2]") ):
            cutted_contents.append("[h2]About HOI4DEV[/h2]\n" + f"{MORE[mode]}\n\n" )
        elif ( sec.startswith("[h2]关于HOI4DEV[/h2]") ):
            cutted_contents.append("[h2]关于HOI4DEV[/h2]\n" + f"{MORE[mode]}\n\n" )
        elif ( sec.startswith("[h2]Contact[/h2]") ):
            contanct = """[h2]Contact[/h2]

Talirian:

[list]
    [*]QQ: 125657190
    [*]Email: magolorcz@gmail.com
[/list]
"""
            cutted_contents.append(contanct)
        elif ( sec.startswith("[h2]联系方式[/h2]") ):
            contanct = """[h2]联系方式[/h2]

Talirian:

[list]
    [*]QQ: 125657190
    [*]Email: magolorcz@gmail.com
[/list]
"""
            cutted_contents.append(contanct)
        else:
            cutted_contents.append(sec)
    
    cutted_content = "".join(cutted_contents)
    cutted_content = cutted_content.replace('<input checked="" disabled="" type="checkbox">', '')
    cutted_content = cutted_content.replace('<input disabled="" type="checkbox">', '')
    with open(file, "w", encoding='utf-8', errors='ignore') as f:
        f.write(cutted_content)

# %%
from pyheaven import CMD
CMD("steamdown < README.en.md > README.steam.en.md")
CMD("steamdown < README.zh.md > README.steam.zh.md")
manual_cuts_steamdown("README.steam.en.md", mode='en')
manual_cuts_steamdown("README.steam.zh.md", mode='zh')

# %%
