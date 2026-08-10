# PIHC3 Steam/player profiles

This folder owns the long-form player introduction separately from the
repository's developer-facing `README.md`.

| File | Ownership |
| --- | --- |
| `STEAM_PROFILE.en.md` | Editable English player-profile source. |
| `STEAM_PROFILE.zh.md` | Editable Chinese player-profile source. |
| `STEAM_PROFILE.steam.en.md` | Generated English Steam markup. Do not hand-edit. |
| `STEAM_PROFILE.steam.zh.md` | Generated Chinese Steam markup. Do not hand-edit. |
| `generate_steam_profiles.py` | Generator and freshness checker. |

After changing either editable profile, regenerate and verify both outputs:

```bash
python3 docs/steam/generate_steam_profiles.py
python3 docs/steam/generate_steam_profiles.py --check
```

The generator requires the installed PIHC3/ParaDev Python dependencies and
Steamdown. The repository landing pages remain `README.md`, its exact English
copy `README.en.md`, and the aligned Chinese translation `README.zh.md`.

## 中文

本文件夹单独维护面向玩家的长篇模组介绍，不再与仓库根目录中面向开发者的
`README.md` 混用。

| 文件 | 归属 |
| --- | --- |
| `STEAM_PROFILE.en.md` | 可编辑的英文玩家介绍源文件。 |
| `STEAM_PROFILE.zh.md` | 可编辑的中文玩家介绍源文件。 |
| `STEAM_PROFILE.steam.en.md` | 生成的英文 Steam 标记；不要手动编辑。 |
| `STEAM_PROFILE.steam.zh.md` | 生成的中文 Steam 标记；不要手动编辑。 |
| `generate_steam_profiles.py` | 生成器与新鲜度检查工具。 |

修改任一可编辑介绍后，请重新生成并校验两份输出：

```bash
python3 docs/steam/generate_steam_profiles.py
python3 docs/steam/generate_steam_profiles.py --check
```

生成器需要已经安装 PIHC3/ParaDev 的 Python 依赖与 Steamdown。仓库入口仍为
`README.md`、其完全一致的英文副本 `README.en.md`，以及对齐的中文翻译
`README.zh.md`。
