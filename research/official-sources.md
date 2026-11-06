# 官方来源核验记录

文档更新：2026-11-06 16:38（北京时间，UTC+08:00）。原 2026-10-28 核验记录保留；下面新增的核验仅适用于对应页面，不代表所有城市资料重新核验。

## 2026-11-06 追加核验

- 韩国开票简报：当天实际读取 Dream Theatre 公告、世宗文化会馆公告及 NOL 首尔商品页，均 HTTP 200。釜山公开开票 11-11 13:00、首尔 11-11 14:00，均为北京时间。釜山冬季套票购票者预售 11-09 13:00 至 11-10 10:00，会员预售 11-10 13:00 至 11-11 08:00；两种预售有资格限制。首尔首轮只开放 2027-01-21 至 01-24 开幕周一楼 VIP 席。具体核验时刻未记录。
- 当天约 16:37：[World Tour](https://hamiltonmusical.com/world-tour/tickets/) 返回 HTTP 200，仍只列釜山 2026-12-17 至 2027-01-16、首尔 2027-01-21 至 03-20；这两站在当前页面可确认。
- 同次读取：[International Tour](https://hamiltonmusical.com/international-tour/tickets/) 返回 HTTP 200，正文为 “No upcoming tour stops at this time”。不能把它解释成 World Tour 没有韩国站点。
- 同次尝试：用户提供的 note.com 文章和 SCMP 原站文章均 `fetch failed`，因此未独立核实其文章正文、发布时间或原截图。用户摘要仅作待核实线索，不能被归为官方来源。未使用 SCMP 非官方代理域名绕过访问限制。
- 以上未写入程序的 lastVerified。新增线索详见 v1.2 方案，核验状态不得由“收到摘要”自动提升。

## 2026-10-28 原核验记录

核验日期：2026-10-28。链接内容可能随官方更新而变化。

## Hamilton 官方站

- [纽约百老汇票务](https://hamiltonmusical.com/new-york/tickets/) — 纽约驻演的演出日历、购票说明和官方抽签。
- [北美巡演票务日历](https://hamiltonmusical.com/us-tour/tickets/) — 当前页面列出 Tampa、Fort Lauderdale、Naples、Jacksonville、Washington DC、North Charleston、Richmond、Baltimore、Dayton、Lincoln、Minneapolis、Vancouver、Calgary、Edmonton、San Jose、Reno、Los Angeles、Albuquerque 共 18 站，日期延伸至 2027-09-12；官方页面提示后续还会公布更多城市。
- [伦敦制作首页](https://hamiltonmusical.com/london/) — 标注 Victoria Palace Theatre；页面当前提示可预订至 2027 年 10 月。
- [伦敦票务页](https://hamiltonmusical.com/london/tickets/) — 当前票务页提示可预订至 2027 年 3 月。与首页的截止月不一致，应用已明确标注冲突并建议查看实时日历。
- [Korea / World Tour 官方票务入口](https://hamiltonmusical.com/world-tour/tickets/) — 韩国站点所属的官方页面。
- [International Tour 官方票务页](https://hamiltonmusical.com/international-tour/tickets/) — 当前页面显示暂无即将演出的国际巡演站点。
- [UK & Ireland Tour 官方票务页](https://hamiltonmusical.com/uk-tour/tickets/) — 当前页面也显示暂无即将演出的巡演站点。

## 韩国官方页面

- [Dream Theatre 釜山官方公告](https://www.dreamtheatre.co.kr/Info/Notice/NoticeDetail?num=360) — 2026-10-27 发布；釜山演出期 2026-12-17 至 2027-01-16，首轮开票 2026-11-11 14:00 韩国时间，公布票价和演员阵容。
- [世宗文化会馆首尔官方公告](https://www.sejongpac.or.kr/portal/bbs/B0000049/view.do?menuNo=200440&nttId=50223&pageIndex=1) — 首轮开票 2026-11-11 15:00 韩国时间，首轮场次 2027-01-21 至 2027-01-24，演出期至 2027-03-20。
- [NOL 韩国站首尔商品页](https://nol.yanolja.com/ticket/products/26015650) — 可核实商品页、票价和开票预告；不能由此推断 NOL World 国际站也销售同一商品。
- [The Korea Times：Hamilton 韩国首演公告](https://www.koreatimes.co.kr/lifestyle/arts-theater/20261013/broadway-phenomenon-hamilton-set-for-korea-premiere-in-december) — 背景资料：韩国首演、创作信息和作品概述。

## 数据使用规则

- 只把官方页面当前列出的地点放入“当前／即将演出”地图。
- 官方票务页、场馆公告和媒体报道分开标记；媒体报道只作线索，不替代票务来源。
- 不将社交平台宣传帖视为票务入口，不推测未公布日期、余票或价格。
