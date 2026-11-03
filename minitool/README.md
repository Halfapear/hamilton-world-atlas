# Hamilton 小红书小工具 v1.1

`index.html` 和 `app.js` 是小工具沙箱版，和网页版保持不同的链接、存储与分享处理。共享首页样式与韩国入口来自 `../src/`，在构建时嵌入，运行时不依赖 CDN。

```powershell
python tools/build_minitool.py
# 输出 output/Hamilton_World_Atlas_XHS_MiniTool_v1.1-compliant.zip
python tests/test_minitool.py
python tests/test_mini_contract.py # 契约模拟，不是真机验收
```

ZIP 根目录只有 index.html 与 app.js；底图 ISC 许可已嵌入 HTML 注释，完整许可另存 world-atlas-LICENSE.txt。默认构建完全在本仓库内进行，不依赖作者电脑路径。

作者原有本地工作流可显式使用 `python tools/build_minitool.py --sync-sibling`，将这两个文件同步到相邻的 `小红书版/MiniTool`，并把新 ZIP 放到 `小红书版` 下；此命令会覆盖那两个同步目标，使用前保存独立编辑。不会删除旧 ZIP 或其他文件。

上传前必须核对创作者账号并完成平台要求的本人实名认证；审核通过后才可在笔记中添加小工具。360 上传账号与 Edge 发笔记账号不同，跨账号是否能选择该工具需在发布页确认。

普通浏览器测试不作为小工具验收依据。必须对相同 ZIP 完成创服平台模拟器、Android 真机扫码、iOS 真机扫码验证。顶部保留保守空间，9.49+ 使用原生按钮矩形动态避让；外部票务链接在文本弹窗中展示；9.46+ 优先原生存储，写失败明确提示未持久保存。需验证容器返回、文字选取、原生分享和保存后关闭重开。Chrome 61 兼容性及真机性能未实测。没有实时余票或代抢能力。票务数据核验日期仍为 2026-10-28。
