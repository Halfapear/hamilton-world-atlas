# 汉密尔顿数据维护

编辑 `hamilton.js` 中的 `window.HAMILTON.cities` 数组即可更新站点信息。当前只包含官方已确认的韩国两站：釜山与首尔。

## 字段说明
- `id`：城市唯一标识（busan / seoul）
- `startDate`、`endDate`：演出期间，不代表期间内每天都有演出
- `ticketOpen`：ISO 8601 开票时间，带北京时间时区偏移
- `prices`：官方公布的票档价格（韩元）
- `sourceUrl`：官方场馆公告
- `bookingStatus`：`direct` 表示已核实的售票商品页；`notice_only` 表示目前只确认到官方公告
- `bookingUrl`：首选入口；如果尚无可核实的直达下单页，不要填写猜测的 URL
- `internationalUrl`：NOL World 国际站入口；不要据此推断该演出已在国际站上架
- `venueInfoUrl`、`seatMapUrl`：场馆官方信息/座位图链接
- `lastVerified`：最后核验日期

## 维护原则
1. 只收录《Hamilton / 汉密尔顿》本次巡演的官方确认信息。
2. 不将小红书宣传帖当成售票入口。
3. 不推测具体场次、实时余票、座位库存或票务链接。
4. 每次改动日期、票价或入口时，同时更新 `lastVerified` 和 README 来源说明。
