# 高堡奇驹 — PIHC3

**统一发布版本（2026-09-07）：** [版本整合与可复现构建](docs/releases/unified-20260930-r8.md) · [独立编译版下载](https://github.com/Magolor/HOI4-PIHC-Compiled/releases/tag/unified-20260930-r8)。


PIHC3 是**高堡奇驹**这一《钢铁雄心 IV》大型转换模组的规范
ParaDev 原生源码项目。

**语言：** [English](README.en.md) · [简体中文](README.zh.md)

## 从这里开始

| 我想要…… | English | 简体中文 |
| --- | --- | --- |
| 了解并游玩模组 | [Steam/玩家介绍](docs/steam/STEAM_PROFILE.en.md) | [Steam/玩家介绍](docs/steam/STEAM_PROFILE.zh.md) |
| 使用 ParaDev GUI 帮助创作内容 | [开发指南](docs/development/README.en.md) | [开发指南](docs/development/README.zh.md) |
| 了解已经完成的 PIHC2 → PIHC3 迁移 | [迁移说明](docs/migration/README.md) | [迁移说明](docs/migration/README.md) |

## 无需先成为程序员，也能开发 PIHC3

ParaDev 将 PIHC3 呈现为易于理解的内容模块：理念、事件、角色、国策、
科技、决议、国家、地区、装备、学说、成就，以及超事件、
背包物品、地区传说等 PIHC3 专属系统。大多数贡献者无需
编写 Python，即可在桌面 GUI 中创建或
编辑这些内容。

ParaDev 只要求 Python。我们推荐用 [uv](https://docs.astral.sh/uv/) 自动管理
独立的 Python 工具环境。偏好命名式 Conda 环境的
贡献者也可以选择
Miniforge；Conda 本身并不是 ParaDev 的运行要求。

```bash
uv tool install --python 3.12 \
  "paradev @ git+https://github.com/PIHC-Team/ParaDev.git"
paradev dashboard
```

在 ParaDev 中打开本仓库根目录，也就是包含 `paradev.yaml` 的
文件夹。双语开发指南介绍环境设置、安全编辑、图片与本地化、
清理/缓存/局部编译、测试和拉取请求，并提供创建理念、
事件和国策的分步教程。

## 一个简单的项目模型

```text
src/modules/<family>/<OBJECT_ID> - <readable title>/
├── def.txt                     # gameplay definition
├── main.loc                    # localization
├── preview.png                 # optional editor preview
└── ...                         # family-owned images and other resources

src/collections/                # focus trees and other grouped content
extensions/                     # PIHC3 compiler/entity extensions
```

普通内容作者只需使用 `src/modules/` 和 `src/collections/`。除非开发指南明确
将其标为高级任务，否则不要编辑隐藏的 `.paradev/` 文件、生成输出、编译器扩展
或项目元数据。

## 安全编译

推荐使用 GUI 的 **Build（编译）** 页面。也可以使用已安装的 CLI
进行验证和自动化：

```bash
# Update the complete existing output using validated caches.
paradev build . --emit-artifacts --emit-manifests \
  --no-sync-launcher-descriptor --summary --json

# Remove ParaDev-owned generated output and rebuild everything.
paradev build . --emit-artifacts --emit-manifests --full-rebuild \
  --no-sync-launcher-descriptor --summary --json

# Rebuild one family or one module safely.
paradev build . --family idea --emit-artifacts --emit-manifests \
  --no-sync-launcher-descriptor --summary --json
paradev build . --family idea --module IDEA_C99_EXAMPLE \
  --emit-artifacts --emit-manifests --no-sync-launcher-descriptor \
  --summary --json
```

提交内容前，请阅读[英文开发指南](docs/development/README.en.md)或
[中文开发指南](docs/development/README.zh.md)。

## 仓库状态与再利用

`master` 是 PIHC3 的规范源码；`legacy` 保存合并后的 PIHC2 历史。
本仓库尚未声明覆盖全仓库的开源许可证；请勿默认代码、文案、美术、音乐或
其他资产可以再利用或再分发。贡献者必须拥有提交所有相关
资产的权限。

发布前请运行 `scripts/check_integration.py` 检查中英文依赖；详见 [r4 集成说明](docs/releases/unified-20260906-r4.md)。
