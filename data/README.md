# 数据编辑说明

编辑 `hamilton-world.json` 后运行 `python tools/build.py` 生成 `index.html`。

## 顶层字段

- `meta`：项目名称、核验日期与范围说明。
- `regions`：区域定义，用于地图筛选和层级导航。
- `productions`：制作版本（例如 Broadway、North American Tour、London、Korea）。
- `stops`：城市与场馆。每个站点必须有唯一 `id`、有效 `productionId`、经纬度和官方来源 URL。
- `news`：可追溯的最新动态。
- `about`：作品简介与数据卡片。
- `koreaCast`：韩国巡演卡司，来源为釜山官方公告。

## 新增站点的最小字段

`id`, `city`, `cityEn`, `country`, `countryEn`, `region`, `productionId`, `venue`, `lat`, `lon`, `datesLabel`, `status`, `officialUrl`, `bookingUrl`, `bookingLabel`, `bookingNote`, `sourceTitle`, `sourceUrl`。

如果日期尚未官方确认，不要填写猜测日期；如果票价未由官方公布，`prices` 留空。`startDate`, `endDate`, `ticketOpen` 都是可选字段。

地图点位的 `dx`、`dy` 用于微调密集城市的标记位置，避免重叠；它们只影响视觉位置，不改变存储的经纬度。
