# 使用 ParaDev 开发 PIHC3

[English](README.en.md) · [仓库首页](../../README.md) · [模组介绍](../steam/STEAM_PROFILE.zh.md)

本指南面向文案、翻译、美术、测试、策划和钢铁雄心 IV 模组作者。
你**不需要**精通 Python。ParaDev 桌面 GUI 负责常规的创建、编辑、校验和
编译流程；文本文件和 Python SDK 则在你希望进一步控制时
使用。

## 1. 十分钟上手

### 所需环境

- Python 3.10–3.13。
- 当前源码安装与克隆需要 Git；也可使用维护者提供的 ParaDev wheel 和仓库 ZIP 包。
- 提交改动需要 GitHub 账号；`PIHC-Team/HOI4-PIHC` 可公开读取。
- 只有在游戏中测试生成的模组时才需要安装钢铁雄心 IV。

Python 是唯一的运行要求；不需要 Conda、Node.js、Rust 或 IDE。
我们推荐 uv 作为最简洁的隔离环境方案；偏好命名式环境时，也可以选择
兼容 Conda 的 Miniforge。

### 使用 uv 安装 ParaDev（推荐）

ParaDev 的首个 PyPI 版本正在准备中。在正式发布前，请从当前公开源码
安装。uv 会把 ParaDev 及其依赖保存在独立环境中，也可以自动获取
Python 3.12：

```bash
uv tool install --python 3.12 \
  "paradev @ git+https://github.com/PIHC-Team/ParaDev.git"
```

若安装后找不到 `paradev`，请运行 `uv tool update-shell` 并重启终端。
使用 `uv tool upgrade paradev` 升级源码安装。
ParaDev 发布至 PyPI 后，
新安装可简化为 `uv tool install --python 3.12 paradev`。

请按照 [uv 官方说明](https://docs.astral.sh/uv/getting-started/installation/)
安装 uv。uv 的独立安装器不要求电脑预先安装 Python。

### 可选：使用 Miniforge 环境

[Miniforge](https://github.com/conda-forge/miniforge) 提供由 conda-forge
支持的精简 Conda 兼容环境。安装 Miniforge 后，创建项目环境并在其中
安装 ParaDev：

```bash
conda create --name pihc3 python=3.12 -y
conda activate pihc3
python -m pip install \
  "paradev @ git+https://github.com/PIHC-Team/ParaDev.git"
```

启动 ParaDev 前请先激活 `pihc3`。此流程受到支持，但只是便利选项，
并非项目要求。不要把软件包安装进 Miniforge 的
`base` 环境。

### 可选：使用现有 Python 虚拟环境

如果你已经自行管理 Python，也可以使用标准虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install \
  "paradev @ git+https://github.com/PIHC-Team/ParaDev.git"
```

在 Windows PowerShell 中，请使用 `.venv\Scripts\Activate.ps1` 激活环境。
每次启动 ParaDev 时都要保留该环境；uv tool 和 Miniforge 可以避免
ParaDev 与无关 Python 软件包意外混用。

### 获取 PIHC3 并打开 GUI

```bash
git clone https://github.com/PIHC-Team/HOI4-PIHC.git
cd HOI4-PIHC
paradev dashboard
```

在 ParaDev 中选择 **Open project（打开项目）**，然后选择包含 `paradev.yaml`
的 `HOI4-PIHC` 文件夹。在 macOS 上也可以安装可从 Finder 或程序坞启动的应用：

```bash
paradev dashboard --install-app --yes
open "$HOME/Applications/ParaDev.app"
```

如果系统 WebView 无法打开，`paradev dashboard --browser` 会使用普通浏览器标签页，
`paradev dashboard --app` 会使用已安装的 Chromium 浏览器。

### 确认项目可以工作

打开 **Build（编译）**，选择 **Update existing output（更新现有输出）**，再点击
**Build**。干净的项目应当在没有阻断诊断的情况下完成。首次编译会建立完整输出
基线，之后的缓存编译和局部更新会更快。

如果暂时不想写入游戏输出，可以运行只读计划：

```bash
paradev build . --summary --json
```

## 2. 项目模型

每一项普通内容都是一个自包含模块：

```text
src/modules/<family>/<OBJECT_ID> - <readable title>/
├── def.txt                     # gameplay definition
├── main.loc                    # localized name and description
├── preview.png                 # optional ParaDev preview
└── ...                         # family-owned icons, pictures, and resources
```

对象 ID 是稳定的游戏与编译器身份。` - ` 后的标题便于
浏览，通常使用 PIHC3 的首选语言中文。请使用 ParaDev 的 **Name（名称）**、
**Rename（重命名）** 或 **Duplicate（复制）** 操作，确保引用与文件夹名称
同步更新。

集合 (Collection) 管理国策树等成组内容：

```text
src/collections/focus/<TREE_ID> - <readable title>/
```

重要的顶层文件夹如下：

| 路径 | 编辑者 | 用途 |
| --- | --- | --- |
| `src/modules/` | 大多数贡献者 | 独立的理念、事件、国策、角色、科技及其他内容。 |
| `src/collections/` | 内容策划 | 国策树及其他成组内容。 |
| `extensions/` | 高级 ParaDev/Python 开发者 | PIHC3 专属 Entity 模式、资源槽、编译器和树编辑器提供者。 |
| `scripts/` | 维护者 | 校验和项目维护工具。 |
| `.paradev/`、`build/`、生成的模组输出 | ParaDev | 缓存、清单、隐藏路由和生成文件。不要手动编辑或提交。 |

不要创建 `_component`、`_asset_component`、`legacy` 或 `inactive_modules`
源文件夹。定义、本地化和图片应放在拥有它们的语义模块中。
若要暂时停用模块，请使用 GUI 的 **Inactive（停用）** 字段；ParaDev 只会保存
最少的必要元数据。

## 3. 第一次贡献

1. 从最新 `master` 创建一个目标明确的分支。
2. 在 ParaDev 中打开 PIHC3，并先运行一次全项目缓存编译。
3. 创建或编辑一项逻辑完整的内容。
4. 迭代时使用模块或家族局部更新。
5. 最后运行一次全项目缓存编译；修改扩展、大量移动资源或怀疑输出陈旧时，
   再使用清理重编译。
6. 提交前检查 GUI 诊断和 `git diff`。
7. 发起拉取请求，说明玩法意图和测试方法。

```bash
git switch -c content/c99-friendship-workshops
git status --short
git diff --check
```

不要在一次贡献中混入无关的平衡、本地化、图片和架构改动。小而可玩的改动
更容易审查和修复。

## 4. 教程：无需编程创建理念 (Idea)

本示例添加一个使民用工厂产出提高 2% 的民族精神。

1. 在项目浏览器中打开 **Country（国家）→ Ideas（理念）**。
2. 选择 **Create module（创建模块）**。
3. 输入对象 ID `IDEA_C99_FRIENDSHIP_WORKSHOPS`。
4. 将 **Name（名称）** 设为 `友谊工坊`。
5. 添加一段说明玩法效果的简短描述。
6. 将 **Civilian industry factor（民用工业系数）** 设为 `0.02`。ParaDev
   使用小数修正，因此 `0.02` 代表 2%，而不是 0.02%。
7. 除非设计确有需要，否则将 **Category（类别）** 保持为 `country`，
   其他高级字段保持默认值。
8. 检查生成文件计划，然后选择 **Create module（创建模块）**。
9. 打开新模块，检查 **Definition（定义）** 和 **Localization（本地化）**。
10. 在 **Build → Buildable items（可编译项）** 中选择该理念并执行
    **Safe partial update（安全局部更新）**。提交前再完成一次全项目缓存编译。

ParaDev 会创建：

```text
src/modules/idea/IDEA_C99_FRIENDSHIP_WORKSHOPS - 友谊工坊/
├── def.txt
└── main.loc
```

若需要自定义图标，对初学者最简单的做法是选择一个已经拥有图标的
干净理念，点击 **Duplicate（复制）**，输入新对象 ID，检查复制计划，
再在新模块的资源编辑器中替换图片。这能让 DDS/GFX 文件名和源码归属
始终保持一致。不要创建独立
资产模块。

### 可选的 Python 等价写法

```python
from paradev import Project

project = Project.load(".")
plan = project.create_module(
    "idea",
    "IDEA_C99_FRIENDSHIP_WORKSHOPS",
    values={
        "title": "友谊工坊",
        "description": "社区工坊让民用生产更有效率。",
        "cic": 0.02,
    },
)
if plan["blocked"]:
    raise RuntimeError(plan["diagnostics"])
```

PIHC3 的首选语言是中文，因此通常可以省略 `language` 字段。SDK、GUI、CLI、
REST、MCP 和 AI 创作流程都使用同一个经过校验的模板与
受保护写入事务。

## 5. 教程：创建事件 (Event)

本示例在一个新命名空间中创建单个国家事件。

1. 打开 **Events（事件）→ Events**，选择
   **Create module（创建模块）**。
2. 输入命名空间/对象 ID `C99_FRIENDSHIP_FAIR`。
3. 将 **Name（名称）** 设为 `第一届友谊工坊展览会`。
4. 在 **Description（描述）** 中
   编写事件正文。
5. 将 **Option title（选项标题）** 设为 `让展览开始吧！`。
6. 检查并创建模块。
7. 打开 **Definition（定义）**。模板会创建事件
   `C99_FRIENDSHIP_FAIR.1`，设置 `is_triggered_only = yes` 并提供一个选项。
   只有剧情需要时才添加触发器、效果或更多选项。
8. 对该事件运行安全局部更新，然后在钢铁雄心 IV 控制台中测试：

```text
event C99_FRIENDSHIP_FAIR.1
```

新文件夹为：

```text
src/modules/event/C99_FRIENDSHIP_FAIR - 第一届友谊工坊展览会/
├── def.txt
└── main.loc
```

请使用唯一且可读的命名空间。同一故事序列中的所有事件及其本地化和图片应
放在同一模块中。若事件需要图片，可以复制一个相似的干净事件模块并替换其自有
图片资源；事件家族接受模块内 `gfx/event_pictures/` 和 `interface/events/` 下的文件。

## 6. 教程：在树编辑器中添加国策

不要创建单独的“国策树模块”。集合拥有整棵树；每个国策仍是可独立编辑的模块。

1. 打开 **Politics（政治）→ Focuses（国策）**，再选择
   **Open Focus tree（打开国策树）**。
2. 在画布上方的范围选择器中选择正确的树。
3. 选择预期的父国策。ParaDev 会自动填充树、位置父项、前置条件，
   以及下一行位置。
4. 选择 **Add graph item（添加图项目）**。
5. 输入稳定的国策 ID，例如 `FOCUS_C99_FRIENDSHIP_WORKSHOPS`。
6. 输入名称和描述；在高级字段中检查 X/Y 位置、前置国策和
   图标精灵。
7. 检查准确计划并应用。
8. 在图中检查新节点，然后运行模块局部更新。

若要创建全新树，请先创建 **Focus tree（国策树）** 集合，再用同一图编辑器
打开。树成员关系属于系统维护的隐藏元数据；请使用集合选择器或树编辑器，
不要手动编辑。

科技与军事工业组织视图遵循同样模式。科技和学说节点都是独立模块。
在 MIO 视图中，**Add graph item（添加图项目）** 会在选中的组织中创建一个
子特质。

## 7. 本地化、定义与图片

### 本地化

`main.loc` 使用 ParaDev 易读的块格式。同一个自有本地化文件可以包含多种语言：

```text
[zh.IDEA_C99_FRIENDSHIP_WORKSHOPS]
友谊工坊

[zh.IDEA_C99_FRIENDSHIP_WORKSHOPS_desc]
社区工坊让民用生产更有效率。

[en.IDEA_C99_FRIENDSHIP_WORKSHOPS]
Friendship Workshops

[en.IDEA_C99_FRIENDSHIP_WORKSHOPS_desc]
Community workshops make civilian production more efficient.
```

请保持键稳定，并在家族要求描述时添加 `_desc` 键。
尽量使用本地化编辑器：它会校验键，并避免直接编写钢铁雄心 IV YAML 时
常见的编码和文件头
错误。

### 定义

`def.txt` 包含 Clausewitz/PDX 玩法脚本。ParaDev 为常用字段提供引导表单，
并为高级效果、触发器、AI 权重和嵌套块提供源码编辑器。
请从**同一家族**复制邻近的可用写法，只修改必要的 ID 与效果，
并立即编译该模块。

### 图片与图标

- `preview.png` 是可选的创作预览。
- 编译后的 DDS 和 GFX 文件应留在模块的家族自有资源路径中。
- 通过资源编辑器替换资产，让 ParaDev 校验文件类型、目标路径和并发改动。
- 需要可靠的多文件图片布局时，请复制一个相似模块。
- 绝不要把图标放进独立 `_asset_component` 文件夹或共享素材堆。

当前家族模板和资源编辑器是可接受资源槽的
事实来源。
如果界面未提供某种新文件，请让 ParaDev 扩展开发者添加资源槽，
而不要把它藏进无关内容。

## 8. 应该选择哪一种模块？

| 目标 | 从这里开始 | 说明 |
| --- | --- | --- |
| 添加民族精神或限时效果 | Idea（理念） | 名称、描述、修正和可选图标放在一起。 |
| 讲述故事或让玩家选择 | Event（事件） | 一个命名空间模块可以拥有相关事件序列及图片。 |
| 添加政治/经济行动 | Decision（决议） | 选择或创建对应的决议类别集合。 |
| 扩展国家路线 | Focus（国策） | 通过国策树图添加。 |
| 添加研究或研究树节点 | Technology（科技） | 使用科技树设置位置和前置关系。 |
| 添加领袖、顾问或特工 | Character（角色） | 肖像和本地化与角色放在一起。 |
| 修改国家或地图区域 | Country、State、Strategic Region | 优先使用引导表单；地图改动需要仔细游戏测试。 |
| 添加部队或军事内容 | Division、Equipment、Doctrine、Building | 以现有相关模块作为设计参考。 |
| 添加军工机构 | Military Industrial Organization | 在 MIO 树视图中编辑其特质图。 |
| 添加 PIHC3 自定义剧情系统 | Superevent、Inventory Item、State Lore | 它们是项目本地扩展家族，与内置类型一样编译。 |
| 添加共享脚本行为 | Scripted Effect、Scripted Trigger、On Action | 高级 PDX 工作；记录调用者并在游戏中测试。 |

GUI 会列出当前所有可创作家族，
包括尚无实例的家族。
如果不确定，请先按玩法概念搜索现有模块，再决定是否创建新类型或共享文件。

## 9. 编译模式及使用时机

| GUI 操作 | CLI 等价命令 | 使用场景 |
| --- | --- | --- |
| **Update existing output（更新现有输出）** | `paradev build . --emit-artifacts --emit-manifests --no-sync-launcher-descriptor` | 使用已校验缓存进行普通全项目验证。 |
| **Clean output and rebuild（清理输出并重编译）** | 添加 `--full-rebuild` | 首次发布、扩展/布局变更或怀疑生成输出陈旧。 |
| 对家族执行 **Safe partial update（安全局部更新）** | 添加 `--family idea` | 迭代同一类型的多个模块。 |
| 对模块执行 **Safe partial update（安全局部更新）** | 添加 `--family idea --module IDEA_C99_FRIENDSHIP_WORKSHOPS` | 快速验证单个模块。 |
| 只读计划 | 省略 `--emit-artifacts --emit-manifests` | 不写生成输出，仅校验和检查。 |

常用命令：

```bash
# Cached whole-project publication.
paradev build . --emit-artifacts --emit-manifests \
  --no-sync-launcher-descriptor --summary --json

# Clean/full publication.
paradev build . --emit-artifacts --emit-manifests --full-rebuild \
  --no-sync-launcher-descriptor --summary --json

# One module.
paradev build . --family idea --module IDEA_C99_FRIENDSHIP_WORKSHOPS \
  --emit-artifacts --emit-manifests --no-sync-launcher-descriptor \
  --summary --json
```

局部编译会维护有效的全项目基线，但不能代替最终全项目检查。
“Validating publication（校验发布）”停在 75% 是 PIHC3 大规模输出的真实安全
阶段，并不表示编译冻结。

## 10. 诊断与常见错误

| 现象 | 处理方法 |
| --- | --- |
| 项目无法打开 | 选择包含 `paradev.yaml` 的仓库根目录，不要选择 `src/` 或某个模块文件夹。 |
| 对象 ID 重复 | 先搜索该家族，并选择全局唯一且稳定的 ID。 |
| `ID - title` 文件夹格式错误 | 通过 ParaDev 重命名；不要只在 Finder/资源管理器中修改文件夹名。 |
| 缺少本地化 | 在模块的 `main.loc` 中添加必需的名称/描述键。 |
| 游戏内缺少图标/图片 | 确认 DDS、GFX 声明和引用的精灵都位于同一模块。 |
| 局部编译成功但完整编译失败 | 修复全项目诊断；局部成功只覆盖选定目标。 |
| 隐藏 `.paradev` 文件出现改动 | 不要手动编辑。还原意外改动；若确为 ParaDev 生成的迁移，请询问维护者。 |
| 编译写入了错误位置 | 在 ParaDev Config 中设置项目输出/模组根目录，然后运行全项目编译。 |

不要静默或绕过阻断诊断。它通常在保护模块身份、数据归属、路径可移植性或
生成输出安全。

## 11. AI 辅助内容创作

ParaDev 向 AI 对话、MCP、REST、CLI 和 Python SDK 暴露同一套创作模板。在 GUI
中选择 **Create content plan（创建内容计划）** 配置，
然后提出小而明确的批量请求，例如：

> 创建五个名为 A、B、C、D、E 的理念，民用工业系数分别为
> 2%、5%、8%、12% 和 16%。

应用前请检查每个对象 ID、字段、文件和诊断。智能体会先创建计划；
只有匹配的受保护计划才能应用，也不会覆盖被独立修改的模块。
AI 输出仍需由贡献者进行设定、平衡、本地化、编译和
游戏内审查。

## 12. 发起拉取请求前

- [ ] 改动只有一个明确的玩法或内容目的。
- [ ] 对象 ID 唯一，文件夹名称符合 `ID - readable title`。
- [ ] 定义、本地化、图片和元数据都与其拥有者放在一起。
- [ ] 未添加 `_component`、`_asset_component`、`legacy` 或 `inactive_modules` 文件夹。
- [ ] 未包含生成的 `.paradev`、build 或模组输出文件。
- [ ] 目标模块/家族的局部编译通过。
- [ ] 最终全项目缓存编译通过，且没有阻断诊断。
- [ ] 适用时已在钢铁雄心 IV 中测试新玩法。
- [ ] 中英文文本已审校，或已明确报告缺失翻译。
- [ ] `git diff --check` 通过，拉取请求说明了测试过程。

## 13. 延伸阅读与求助

- [ParaDev README](https://github.com/PIHC-Team/ParaDev)
- [ParaDev 入门指南](https://github.com/PIHC-Team/ParaDev/blob/master/docs/user-manual/getting-started.md)
- [模块与集合](https://github.com/PIHC-Team/ParaDev/blob/master/docs/user-manual/modules-and-collections.md)
- [编译与诊断](https://github.com/PIHC-Team/ParaDev/blob/master/docs/user-manual/build-and-diagnostics.md)
- [Python SDK 指南](https://github.com/PIHC-Team/ParaDev/blob/master/docs/user-manual/sdk-python.md)
- [PIHC3 迁移完成说明](../migration/README.md)

求助时请提供模块家族与对象 ID、预期结果、完整诊断文本，以及问题出现在
局部、缓存还是清理编译。截图很有帮助，
但可复制的诊断文本更有价值。
