# QubitHub Qiskit Fall Fest 2026 —— 十道量子计算挑战

[English](README.md) | 简体中文

十道由浅入深、带引导的编程挑战，专为一天的量子计算黑客松设计，基于 **Qiskit 2.x** 编写。
每道挑战都是一个 Jupyter Notebook，包含背景故事、核心概念、需要你完成的 **TODO** 函数、可立即反馈结果的公开检查，以及从含蓄到直白逐级展开的提示。全部内容都能在普通笔记本电脑（仅 CPU）上运行：**无需账号、无需 API 密钥、无需付费服务，也无需量子硬件。**

| # | 挑战 | 难度 | 预计用时* | 练习内容 | Colab |
|---|---|---|---|---|---|
| 1 | 显微镜下的叠加态 | 1 - 基础 | 15-25 分钟 | 振幅与概率、精确结果与采样结果 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_01_superposition/challenge_01_superposition.ipynb) |
| 2 | 纠缠侦探 | 1 - 基础 | 20-30 分钟 | Bell 态、多组基下的关联、区分纠缠态与直积态 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_02_entanglement/challenge_02_entanglement.ipynb) |
| 3 | 量子门外科医生 | 1 - 基础 | 20-30 分钟 | 阅读并修复线路、比特顺序、等价线路 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_03_gate_surgeon/challenge_03_gate_surgeon.ipynb) |
| 4 | 传送量子比特 | 2 - 算法与应用 | 40-60 分钟 | 带中途测量和经典控制的量子隐形传态 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_04_teleportation/challenge_04_teleportation.ipynb) |
| 5 | 寻找隐藏的态 | 2 - 算法与应用 | 40-60 分钟 | Grover 搜索：Oracle、扩散算子、迭代次数 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_05_grover/challenge_05_grover.ipynb) |
| 6 | 对抗噪声 | 2 - 算法与应用 | 40-60 分钟 | 噪声模型、总变差距离、误差缓解真的有用吗？（需要 `qiskit-aer`） | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_06_noise/challenge_06_noise.ipynb) |
| 7 | 量子网络切割 | 2 - 算法与应用 | 45-60 分钟 | 将 Max-Cut 表示为哈密顿量、QAOA、正确性与解的质量 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_07_qaoa_maxcut/challenge_07_qaoa_maxcut.ipynb) |
| 8 | 教量子线路学习 | 3 - 进阶 | 60-90 分钟 | 变分分类器、训练、训练/测试数据泄漏、诚实的基线对比 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_08_quantum_ml/challenge_08_quantum_ml.ipynb) |
| 9 | 保护逻辑量子比特 | 3 - 进阶 | 50-80 分钟 | 三比特比特翻转码、校验子、前馈控制，以及它无法防护的错误 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_09_error_correction/challenge_09_error_correction.ipynb) |
| 10 | 硬件架构师 | 3 - 进阶 | 45-75 分钟 | 针对给定耦合图进行编译（transpile）：线路深度与双比特门数量 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_10_transpilation/challenge_10_transpilation.ipynb) |

\* 用时为**估计值**，并非实测。建议从挑战 1 开始；难度逐级递增，但每道挑战都可以独立完成。

**第一次来？** 点击任意 **Colab** 徽章即可在 Google Colab 中打开对应 Notebook，无需安装（见 [Colab](#colab)）；也可以按照[快速开始 - 本地 Jupyter](#快速开始---本地-jupyter) 在自己的电脑上操作。

## 环境要求

* Python 3.11 或更高版本（已测试 3.11、3.12、3.13 和 3.14；不支持 Python 3.10，因为锁定版本的 `qiskit-aer` 无法在其上安装），约 1 GB 可用磁盘空间，以及本地 Jupyter 环境或一个（免费的）用于 Colab 的 Google 账号。
* 项目**测试时**使用的确切库版本锁定在 [`requirements.txt`](requirements.txt) 中（Qiskit 2.6.0、NumPy 2.4.6、SciPy 1.17.1、Matplotlib 3.11.2、pytest 9.1.1；Qiskit Aer 0.18.0 仅用于挑战 6）。`pyproject.toml` 列出了*兼容的版本范围*，其他组合应该也能运行，但**未经测试**。
* **Windows on ARM** 笔记本（骁龙处理器）无法使用锁定版本：Qiskit 2.6.0 没有现成的安装包，`pip` 会尝试从源码编译。请改用 Colab，或安装 x64 版本的 Python（未测试）。
* 只有**挑战 6** 需要 `qiskit-aer`（支持噪声的模拟器），其他九道挑战有意不依赖它。挑战 6 的设置单元格会在缺失时自动安装（需要联网），你也可以提前运行 `pip install qiskit-aer==0.18.0`。

## 快速开始 - 本地 Jupyter

```bash
python -m venv .venv
# Windows (PowerShell):   .venv\Scripts\Activate.ps1
# Windows (cmd):          .venv\Scripts\activate.bat
# macOS / Linux:          source .venv/bin/activate
pip install -r requirements.txt
pip install -e . --no-deps
pip install jupyterlab        # 也可以用 VS Code 打开 Notebook；本项目未锁定 JupyterLab 版本
jupyter lab
```

然后打开 `challenges/challenge_01_superposition/challenge_01_superposition.ipynb`，从上到下依次运行各单元格。
请在本目录下启动 Jupyter（或从这里打开 Notebook）：第一个单元格会在 Notebook 所在目录及其上级目录中查找 `pyproject.toml` 来定位项目。

## Colab

最快的方式无需在电脑上安装任何东西：**在本页顶部的表格中点击对应挑战的 “Open in Colab” 徽章**。

1. Colab 会直接从 GitHub 打开 Notebook。运行时 Colab 会提示该 Notebook 并非由 Google 编写——所有来自 GitHub 的 Notebook 都会出现这一标准提示，选择 *仍然运行（Run anyway）* 即可（Notebook 运行的所有内容都在本仓库中）。
2. 运行第一个单元格（*Setup*）。由于 Colab 只打开了 Notebook，该单元格会**从 GitHub 拉取整个项目**到 Colab 机器上（几秒钟），连同兼容的 Qiskit 版本一起安装（首次约一分钟），并打印检测到的库版本。Colab 自带的版本与测试版本不同：如果某项检查表现异常，该单元格会指出哪些版本存在差异。
3. 按照下文 *打开一道挑战* 的说明完成 Notebook。Colab **不会**把修改保存到 GitHub 原始仓库，而且每个 Notebook 都运行在一台独立的、初始为空的机器上：离开前请使用 *文件 > 在云端硬盘中保存副本*（或 *文件 > 下载 .ipynb*）——运行时被回收后所有内容都会丢失。打开下一道挑战时，设置单元格会再次拉取项目。
4. 提交作业时，运行最后一个单元格：它会在 `/content` 中生成 `submission_cNN.py`。打开 *文件* 面板（文件夹图标），右键该文件并选择 *下载*。

项目团队于 2026-11-01 在真实的 Colab 运行时上完整验证了这一流程：挑战 1 从点击徽章一直到提交单元格，以及在另一台全新运行时上的挑战 6（详见 *已验证与未验证的内容*）。

**如果徽章无法使用**——例如组织者给你的是一个 zip 压缩包——请自行上传项目。Colab 中每个 Notebook 都运行在独立的空白机器上，所以需要*在你正在使用的 Notebook 中*操作，并且每打开一道挑战都要重复一次。项目团队曾在真实 Colab 运行时上走通过这一流程（2026-10-30，Python 3.13）：在 Colab 界面中完成挑战 1 从上传到提交的全过程，并在该机器上运行了全部十个 Notebook。

1. 在电脑上解压文件，找到你的挑战 Notebook：`challenges/challenge_NN_<name>/challenge_NN_<name>.ipynb`。在 Colab 中选择 *文件 > 上传笔记本*，选中该 Notebook。
2. 在第一个单元格上方添加一个代码单元格（将鼠标悬停在第一个单元格顶部边缘，点击 *+ 代码*）并运行：

   ```python
   from google.colab import files
   files.upload()                                   # 选择你收到的 zip 文件
   !unzip -q participant_package.zip
   %cd participant_package
   ```

   （如果你收到的是仓库地址，请使用 `!git clone <该地址>`，再用 `%cd` 进入生成的文件夹。）
3. 运行设置单元格（Notebook 的第一个单元格）。当项目位于当前工作目录、其上级目录或其直接子目录时，它都能找到项目，并安装辅助包（`pip install -e .`）以及 `pyproject.toml` 中兼容的 Qiskit 版本，约需一分钟。如果提示找不到项目，请先在其上方的单元格中运行 `%cd /content/participant_package`。安装完成后若 Colab 弹出重启会话的提示，请重启后再运行一次设置单元格。
4. 运行时被回收后 Colab 中的文件会消失：离开前请下载你的 Notebook（*文件 > 下载 .ipynb*）。最后一个单元格会把 `submission_cNN.py` 写入你用 `%cd` 进入的目录。

Colab 会不定期更新运行时镜像，如果某个步骤与描述不符，请告知组织者。

## 打开一道挑战

每个 `challenges/challenge_NN_<name>/` 目录包含：

| 文件 | 说明 |
|---|---|
| `challenge_NN_<name>.ipynb` | 带引导的 Notebook——**打开这个** |
| `starter.py` | 以普通 Python 文件形式提供的同一组 TODO 函数框架（便于在编辑器和命令行中使用） |
| `README.md` | 一页纸的题目说明、函数约定和验收标准 |

Notebook 的使用方式：阅读背景故事，按顺序运行单元格，完成标记为 **TODO** 的单元格，然后运行**公开检查**单元格。它会把每项检查列为 `[PASS]`、`[FAIL]`（附说明）或 `[TODO]`（该函数仍抛出 `NotImplementedError`）。提示请逐个打开——先含蓄、后直白。
当某个 TODO 尚未完成时，依赖它的单元格会打印“not ready yet”而不是报错，因此你随时都可以运行整个 Notebook。

在 Jupyter 之外操作：

```bash
pytest tests/public/test_c01_public.py --impl challenges/challenge_01_superposition/starter.py     # 你修改后的 starter 文件
pytest tests/public/test_c01_public.py --impl path/to/your_notebook.ipynb                            # 你的 Notebook
```

提交作业时，保存 Notebook 或运行最后一个单元格：它会把 `submission_cNN.py` 写入 Notebook 运行所在的目录（通常是 Notebook 所在目录；在 Colab 中为 `/content` 或你用 `%cd` 进入的目录，可在 *文件* 面板中找到并下载）。

## 评分方式

* 你自己可以运行的**公开检查**只是*冒烟测试*：用于确认基本功能正常。通过它们是必要条件，但不是充分条件。
* 组织者会运行**额外的隐藏测试**，覆盖更多输入、边界情况（非法输入必须抛出 `ValueError`）、不同规模和不同随机种子。
  硬编码答案没有用：测试会改变输入，检查结果的*数学性质*（态矢量、酉矩阵、概率），而从不检查你使用了哪些具体的门——任何正确的构造都会被接受。
* 精确量以 1e-9 的绝对容差进行比较；由有限次采样得到的量使用固定随机种子和有文档说明的统计容差。
* 含优化环节的挑战（7、8、10）会分别评估**正确性**和**解的质量**：从不要求随机优化器做到完美。
* 典型评分比例：正确性 60%、边界情况 20%、思考题回答 10%、代码清晰度 10%（挑战 7、8、10 为 50 / 15 / 15（质量）/ 10 / 10）。
  *附加*任务最多可额外获得 10 分，但拿满分并不需要完成它们。

## 公平竞赛规则

* 欢迎查阅提示和文档；卡住时可以向组织者求助。不要抄袭其他队伍的答案。
* 不要修改 `src/` 和 `tests/` 中的文件——检查必须对所有人保持一致。
* 切勿分享包含凭据或个人数据的 Notebook 输出；本项目不需要任何此类信息。

## 常见问题排查

| 现象 | 解决方法 |
|---|---|
| `ModuleNotFoundError: qiskit_fest` | 在本目录下启动 Jupyter，或在本目录中运行 `pip install -e . --no-deps` |
| 线路图退化为文本显示 | `pip install pylatexenc`（已包含在 `requirements.txt` 中） |
| 挑战 6：`ModuleNotFoundError: qiskit_aer` | `pip install qiskit-aer==0.18.0`（需要联网） |
| `pip install -r requirements.txt` 提示找不到 `qiskit` 或 `qiskit-aer` 的版本，或开始编译 Qiskit | 检查 `python --version`（需要 3.11 或更高版本）；在 Windows 上确认笔记本是否为 ARM 架构（见 *环境要求*）；使用 Colab 可同时避开这两个问题 |
| Linux 上的挑战 6：导入 `qiskit_aer` 时出现 `ImportError: ... cannot allocate memory in static TLS block` | 启动 Python / Jupyter 前设置环境变量 `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`（例如在运行 `jupyter lab` 前于终端执行 `export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`）；必须在程序启动前设置。我们在一个普通 Linux 容器中遇到过此问题，你的机器是否受影响尚不确定 |
| 设置单元格警告版本不一致 | 通常仍能正常运行；在全新的虚拟环境中执行 `pip install -r requirements.txt` 即可复现测试版本 |
| 检查结果显示 `[TODO]` | 该函数仍抛出 `NotImplementedError`——完成 TODO 单元格后重新运行 |
| Notebook 找不到项目 | 从本目录打开 Notebook（Colab 用户请参阅 *Colab* 一节） |
| Colab：设置单元格报错 `Could not fetch the project from ...` | Colab 机器无法访问 GitHub，或仓库地址已变更：再运行一次；如果仍然失败，请使用 *Colab* 一节中的上传方式，并告知组织者 |

## 问题反馈

请在活动现场告知组织者；如果你是通过代码仓库获得本项目的，也可以在仓库中提交 issue。一份有用的反馈最好包括：

* 挑战编号，以及失败的单元格或检查项（公开检查打印的名称）；
* **完整的**错误信息，请复制为文本而不是截图；
* `python -c "import qiskit_fest; print(qiskit_fest.environment_report())"` 的输出，以及你的系统名称（Windows、macOS、Linux、Colab）；
* 你已经尝试过的方法。

请不要在反馈中粘贴凭据或个人数据；本项目不需要任何此类信息。

## 已验证与未验证的内容

挑战题库在 **Windows 11 + CPython 3.11.9 虚拟环境**中开发和检查，使用的正是 `requirements.txt` 中的版本。项目自身的测试套件（针对参考答案运行的公开测试与隐藏测试）也在 **Linux 容器**中通过：使用锁定版本时覆盖 Python 3.11、3.12、3.13 和 3.14；使用版本范围允许的最新版本（Qiskit 2.6.1、NumPy 2.5.4、SciPy 1.18.1）时覆盖 Python 3.12 和 3.13。在 Windows 上，用 `requirements.txt` 构建的全新虚拟环境通过各自的设置单元格运行了全部十个 Notebook（挑战 6 特意先卸载了 `qiskit-aer`，以确保设置单元格必须自行安装）；一个模拟 Colab 的环境（Ubuntu 24.04、Python 3.12、允许的最新库版本、项目解压在 Notebook 旁）也无错误地运行了全部十个 Notebook。

在 **Google Colab** 上（2026-10-30：Python 3.13.18、Qiskit 2.6.1、NumPy 2.1.3、SciPy 1.16.3、Matplotlib 3.10.0、pytest 8.4.2），挑战 1 在 Colab 界面中被手动完整做了一遍，全部十个 Notebook 都在 Colab 机器上运行过；那次运行发现挑战 6 在没有 Aer 的机器上首次运行时存在问题（所有检查都被跳过），该问题已修复。一键方式（**Colab** 徽章；设置单元格通过 `git` 从本仓库拉取项目）于 2026-11-01 在 Google Colab 上测试，同样使用 Python 3.13.18 和 Qiskit 2.6.1：挑战 1 从徽章到提交单元格——设置单元格用 13 秒拉取并安装了项目，公开检查对未完成的代码报告 `[TODO]`，函数完成后报告 `[PASS]`；并在另一台全新机器上测试了挑战 6（设置单元格同时安装了 `qiskit-aer`，全部 15 项公开检查都已运行，无一被跳过）。其余八个 Notebook 未通过徽章手动打开，但它们的设置单元格代码完全相同。测试套件也在使用与上述 Colab 完全相同库版本的 Linux 容器中通过。

macOS 以及 2.6.0 / 2.6.1 以外的 Qiskit 版本**未经测试**；对于 macOS，我们仅用 `pip` 确认了所有锁定的库都有现成安装包（Apple 芯片和 Intel，Python 3.11 至 3.14）。锁定版本不支持 Windows on ARM（见 *环境要求*）。
你可以运行 `python -c "import qiskit_fest; print(qiskit_fest.environment_report())"` 查看*你自己*环境的情况。

## 许可证

本项目基于 [MIT 许可证](LICENSE) 发布：你可以使用、复制、修改和分享这些 Notebook、辅助代码和测试（例如用来举办自己的工作坊），只要保留许可证文本和版权声明即可。本项目不提供任何担保。Qiskit、Qiskit Aer、NumPy、SciPy、Matplotlib 和 pytest 是各自独立的项目，遵循各自的许可证；本项目不是 Qiskit 或 IBM 的官方产品。
