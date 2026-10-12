# limbus-zh

Arch Linux 上的《边狱公司 / Limbus Company》零协会汉化命令行安装更新工具，适用于 Steam + Proton。独立编写，非零协会官方工具。Python 标准库实现，字体解压依赖 Arch 的 `7zip`。

## 开始使用

先退出游戏，在本目录运行：

```sh
sudo pacman -S --needed python 7zip
./limbus-zh find
./limbus-zh install
```

首次安装后，在游戏加载前的语言列表选择 `LLC_zh-CN`。基础语言建议选英文，避免字体不一致。Proton 仍由 Steam 管理；此工具向游戏根目录的 `LimbusCompany_Data/Lang/LLC_zh-CN` 部署语言资源，无需 .NET 或 Windows 工具箱。

普通 Steam、额外 Steam 游戏库以及 Flatpak Steam 均自动识别。未找到游戏或找到多份安装时，显式指定游戏根目录：

```sh
./limbus-zh install --game-dir '/mnt/Games/steamapps/common/Limbus Company'
```

`--game-dir` 可用于下面所有操作；目录必须包含 `LimbusCompany.exe` 和 `LimbusCompany_Data`。安装命令以普通用户运行，游戏目录需有写权限。

## 日常操作

```sh
./limbus-zh status       # 查看本地记录和上游语言包版本文件，不联网
./limbus-zh check        # 从 GitHub 检查最新版本
./limbus-zh update       # 安装最新版，版本相同则跳过
./limbus-zh update --force  # 重新下载文本和字体，修复安装
./limbus-zh rollback     # 恢复上次语言目录，当前版本保留为备份
```

更新和覆盖已有安装时，完整旧语言目录保存到旁边的 `LLC_zh-CN.limbus-zh-backup`。为避免无意删除备份，如果该目录已存在，后续更新默认停止。保存/移走备份后再更新，或者明确允许删除上次备份：

```sh
./limbus-zh update --discard-backup
```

该选项在下载、校验、解压成功后才删除上次备份，然后保存本次更新前的版本。只保留一份备份。回滚后，备份与当前版本互换。首次安装没有旧目录时没有备份。

本工具替换整个 `LLC_zh-CN` 目录，自定义字体和自行修改的文本会留在备份中，需自行合并。不会安装旧 BepInEx，也不会修改 Proton 前缀、Steam 启动选项或游戏语言设置。

## 安装到系统 / Arch 打包

本目录包含本地 `PKGBUILD`，不需要上传到 AUR：

```sh
sudo pacman -S --needed base-devel
makepkg -si
limbus-zh install
```

也可以手动安装至个人命令目录：

```sh
install -Dm755 limbus-zh "$HOME/.local/bin/limbus-zh"
```

需确保 `~/.local/bin` 在 PATH 中。

## 下载与保护措施

- 文本来自 GitHub Releases 的 `LimbusLocalize_*.zip`，用 GitHub 发布元数据提供的 SHA-256 校验；上游无摘要或改变格式时停止。
- 字体来自上游 `Fonts/LLCCN-Font.7z`，用 Git blob SHA-1 核对内容与 GitHub 元数据。它用于一致性校验，不是独立签名。
- 仅使用 GitHub，不调用零协会下载服务器/API。可使用系统 `https_proxy`/`HTTPS_PROXY` 环境变量。GitHub 可能限流；错误时稍后重试。
- 压缩包路径校验、符号链接拒绝、独占锁；先在同文件系统暂存，完成后通过目录重命名部署。替换失败时恢复旧目录。
- 检测游戏进程，发现运行中则停止。仍应主动退出游戏。

突然断电或强制终止恰好发生在目录交换期间，可能留下备份而缺少当前语言目录，可运行 `rollback` 恢复。若存在 `.limbus-zh-swap`，工具会停止，需人工检查并恢复对应目录。备份和临时目录需要额外磁盘空间。

`check` 比较工具记录的文本发布版本；手动安装视为未记录，不判断字体是否变化。修复损坏文件或单独刷新字体使用 `update --force`。

## 验证范围

已用真实上游文本包和字体包在临时游戏目录中验证安装、强制更新、备份、回滚和再次更新；另测试额外 Steam 库（含空格路径）、路径穿越拒绝、链接拒绝及替换失败恢复。用户已在实际 Arch Linux + Steam/Proton 游戏环境中确认菜单、剧情文本和字体显示正常。音频保持游戏原有韩语：上游语言包不包含中文配音。Proton 版本、Steam 安装方式和系统版本尚未记录，其他环境仍需反馈。

```sh
python -m unittest discover -v
```

默认跳过需要下载样例的集成测试。设置 `LLC_FIXTURES` 指向含 `text.zip`、`font.7z`、GitHub API `release.json`、递归 `tree.json` 的目录后可运行该测试。

## 署名与许可

工具原创代码：MIT，见 `LICENSE`。不随工具分发翻译文本或字体。

汉化内容由[都市零协会 / LocalizeLimbusCompany](https://github.com/LocalizeLimbusCompany/LocalizeLimbusCompany)提供，遵守上游 CC BY-NC-SA 4.0；语言包中的 `Info/LICENSE` 会保留。字体依其随附/上游许可使用。详见[官方手动安装](https://www.zeroasso.top/docs/install/install/)与[开发者说明](https://www.zeroasso.top/docs/devNotes/)。
