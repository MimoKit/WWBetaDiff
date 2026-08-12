<h1 align = "center">WWBetaDiff</h1>
<h4 align = "center">✨基于<a href="https://github.com/KimigaiiWuyi/gsuid_core" target="_blank">GsCore</a>的鸣潮体验服差异查询插件✨</h4>
<div align = "center">
        <a href="#丨我该如何安装该插件">安装方法</a> &nbsp; · &nbsp;
        <a href="#丨指令列表">指令列表</a> &nbsp; · &nbsp;
        <a href="#丨感谢">感谢</a>
</div>

## 丨这个插件是干什么的？

+ 查询鸣潮体验服最近三个快照（V1 / V2 / V3）之间**角色与武器的数值、文案变动**。
+ 数据来自 [nanoka.cc](https://nanoka.cc) 的版本化静态 JSON，本地自动缓存，数据源短暂不可用时回退到最近缓存。
+ 渲染采用 **HTML(htmlkit)** 出图：浅色卡片式排版，新旧值红绿对照，**逐字符 diff 高亮**——改了哪几个字一眼可见。
+ 详情图双列并排展示 `V1→V2`、`V2→V3` 两个阶段，长描述中新增/删除的整句也会被标出。

## 丨我该如何安装该插件？

+ 前提：你已经部署好 [gsuid_core](https://github.com/KimigaiiWuyi/gsuid_core)。
+ 将本仓库克隆到 GsCore 的插件目录：

```bash
cd gsuid_core/gsuid_core/plugins
git clone https://github.com/MimoKit/WWBetaDiff
```

+ 重启核心，发送 `wwng` 即可使用。

## 丨指令列表

| 指令 | 说明 |
|------|------|
| `wwng` | 查看当前三个体验服快照的角色、武器变动总览 |
| `wwng 景燃` | 查看指定角色或武器的两阶段详细差异 |
| `wwng 1212` | 也可以按数据 ID 查询 |

## 丨感谢

- [@KimigaiiWuyi(无疑)](https://github.com/KimigaiiWuyi) - 感谢无疑开发的 [gsuid_core](https://github.com/KimigaiiWuyi/gsuid_core) 框架，本插件基于其插件体系与渲染封装
- [nanoka.cc](https://nanoka.cc) - 体验服版本化数据来源
- [Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC) - 渲染内嵌字体

## 丨其他

+ 如果对本插件有功能建议 & Bug 报告，欢迎提 Issue & PR，每一条都会详细看过
+ 如果本插件对你有帮助，不要忘了点个 Star~
+ 本项目仅供学习使用，请勿用于商业用途
+ [GPL-3.0 License](https://github.com/MimoKit/WWBetaDiff/blob/main/LICENSE)
