# Hamilton Korea Ticket Assistant — 产品交付计划

## 产品范围（严格限定）
本项目只服务于《Hamilton / 汉密尔顿》韩国巡演，不是全国巡演聚合平台，不展示其他音乐剧、演唱会或小红书泛案例。当前确认的站点只有釜山与首尔。

## 已实现的前端交互
- 韩国巡演示意地图：点击首尔/釜山进入城市详情。
- 城市详情：演出期间、场馆、开票时间、票价、来源链接和倒计时。
- 购票方案配置：意向日期、场次偏好、票档、数量与预算估算。
- 购票指南：打开官方入口、登录准备、选日期/场次/票档、付款核对、订单保存。
- 釜山：官方场馆开票公告作为当前确认入口；未找到可核实的直达下单商品页时明确提示，不伪造链接。
- 首尔：NOL 韩国站官方商品页 https://nol.yanolja.com/ticket/products/26015650；海外观众另需检查 NOL World https://world.nol.com/zh-CN/ticket 是否上架同一商品。
- 个人计划本地保存、购票清单 TXT 导出、开票提醒 ICS、计划 JSON 备份。
- 逐项勾选购票准备清单，进度保存在当前浏览器。

## 数据可信度
- 釜山公告：https://www.dreamtheatre.co.kr/Info/Notice/NoticeDetail?num=360
- 首尔公告：https://www.sejongpac.or.kr/portal/bbs/B0000049/view.do?menuNo=200440&nttId=50223&pageIndex=1
- 首尔 NOL 商品页：https://nol.yanolja.com/ticket/products/26015650
- 开票时间以北京时间显示；釜山 2026-11-11 13:00，首尔 2026-11-11 14:00。
- 日期选择仅保存用户意向，不代表当日一定有演出或余票。
- 票价估算不含手续费；实时座位/库存以官方售票页为准。

## 运行与测试
- 从项目根目录打开 index.html；必须保留 data/hamilton.js。
- `tests/TEST_REPORT.md` 记录 23 项逻辑与交互 smoke checks；当前执行环境阻止 Chromium 打开本地页面，因此不声称已完成真实浏览器截图/像素验收。
- 不连接票务账户，不收集第三方密码、验证码或银行卡信息。

## 尚未实现
- 云端账号与跨设备同步。
- 票务平台授权 API、真实库存、座位图、订单同步和支付。
- 公网 HTTPS 部署。
