# Hamilton v1.2 测试与交付报告

文档更新：2026-11-06 17:06（北京时间，UTC+08:00）。
本轮实施16:46起，资料核验约16:37／韩国公告具体时刻未记录；不得把测试时间当资料更新时间。

## 测试结果

最终交互／回归重跑：2026-11-06 16:58–17:05，北京时间。官方最终包27/27结束于17:00:58（JSON以UTC记09:00:58Z）。

| 检查 | 结果 | 范围 |
| --- | --- | --- |
| 新版双客户端集成 | Chromium 91/91，Edge 91/91 | 线索隔离／来源弹窗／图层／5种视口／旧计划 |
| 既有网页版 | Chromium 95/95，Edge 95/95 | 地图、层级、筛选、预算、存储与导出 |
| 既有小工具 | Chromium 24/24，Edge 24/24 | 地图／顶部避让／安全文本外链／分享回退 |
| 契约模拟 | 15/15 | 旧内核间距回退、顶部区域、写失败诚实提示；不是实际旧内核测试 |
| 来源数据 | 2/2 | 22官宣+7线索、不可购票字段、分条核验 |
| 独立重复构建 | 1/1 | 仅两文件、canonical数据一致、重复ZIP字节一致 |
| 地图几何 | 2/2 | 边界／跨经线裁切 |
| 既有图标像素检查 | 2/2，本地附加测试 | 原金H保留／深蓝无白边；依赖相邻本地图片，未纳入本轮Git改动 |
| 小红书真实官方模拟器 | 27/27 | 隔离无窗口Edge、精确最终包；非登录账号／真机／发布验收 |

浏览器：Chromium 148.0.7778.96；Microsoft Edge 146.0.3856.109。视口320／360／390／430px与1440px，地图、线索页、来源弹窗、计划页无水平溢出。手机地图顶部约670px，按钮至少44px；长URL可换行，来源弹窗可滚动、Tab限制／Escape关闭和焦点恢复已检验。

测试先失败再修复的项目：旧版无线索页／数据与v1.2包；弹窗误对背景div调用focus；新增信息挤低手机地图；旧内核缺少显式定位与间距回退；嵌套外链文本弹窗未接管焦点，Escape冒泡同时关闭两层。均补用例后修复。

中间脚本问题：宽泛unittest发现会重复运行顶层浏览器脚本并冲突截图，最终改为逐个运行；官方模拟器返回note会卸载guest，追加检查须恢复minitool再定位；两元素相同data-lead需限定可见卡片按钮。不是把中间失败掩盖成通过。

## 最终构建身份

- Web SHA256：CF9B355C20A3315A34A86C521D7A982975EC9CD14AD37D2291051F4FFC2764DC
- Mini ZIP SHA256：1837B344CABE50A934CB35C3992932E06E5F8BBCE7EF26A77E63B076888B9474
- 文件名：Hamilton_World_Atlas_XHS_MiniTool_v1.2-compliant.zip
- ZIP根目录仅index.html／app.js。两处本地包（output与相邻小红书版）统一最终哈希；旧v1.1包保留。
- 官方模拟器本轮最终报告：output/official-runtime-v1.2/official-runtime-qa-report.json；新版截图／JSON：output/playwright/v1.2/chromium及msedge。旧v1.1官方报告未覆盖。

## 可复现命令

在仓库目录，Python3+Playwright；运行浏览器测试前安装Chromium，Edge使用本机已安装版本。

```powershell
python tools/build.py
python tools/build_minitool.py
python tests/test_v12_browser.py
python tests/test_app.py
python tests/test_minitool.py
python tests/test_mini_contract.py
python -m unittest discover -s tests -p test_tour_leads.py -v
python -m unittest discover -s tests -p test_build_minitool.py -v
python -m unittest discover -s tests -p test_map_geometry.py -v
$env:ATLAS_BROWSER='msedge'
python tests/test_v12_browser.py
python tests/test_app.py
python tests/test_minitool.py
node --check minitool/app.js
git diff --check
```

官方运行时脚本tools/official_runtime_qa.cjs仅打开隔离无窗口Edge，不连接真实账号、不读取用户配置。需要Node Playwright，可用NODE_PATH指向本任务bridge/node_modules，或在可用依赖环境运行；不必修改全局浏览器设置。脚本使用公开官方运行时，网络不可用时保存源码并报告失败，不能用旧报告冒充新结果。

## 发布边界

平台候选版本1.2.0。截至文档写作，本轮未提交平台、未读取新审核结果。旧连接pipe已失效，未重弹授权／重启或聚焦用户浏览器。原工具AppID 6aea400c74b80400158a253a不变，原定向私密笔记未修改或重发。

Android／iOS真实设备、Edge主号挂载、活动跨账号奖励资格待验证。模拟器分享仅SDK成功反馈，不证明手机已完成发布。17:05:53已推送代码提交6366372，并实际读回远端main一致；文档补记另提交，不修改程序包。
