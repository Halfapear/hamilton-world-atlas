# 数据编辑说明

文档更新：2026-11-06 16:38（北京时间，UTC+08:00）。既有规则最近一次 Git 提交为 2026-11-04 00:25:46；项目数据基线核验日期为 2026-10-28。

时间字段须分开记录：资料发布时间、资料核验时间、程序构建时间、平台提交时间。没有精确时刻时只写日期并注明“具体时刻未记录”，不使用文件修改时间或 Git 提交时间替代事件时间。

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

地图点位的 `dx`、`dy` 从 v1.1 起只调整文字标签位置，不移动城市圆点或巡演连线。`lat` / `lon` 必须是范围内的数值（纬度 -90～90，经度 -180～180）。

## 本地底图

`world-land-110m.json` 来自 [world-atlas@2.0.2](https://github.com/topojson/world-atlas)，其陆地数据源为 [Natural Earth](https://www.naturalearthdata.com/) v4.1.0、1:110m（公开领域）。world-atlas 分发采用 ISC 许可，原文保留在 `world-atlas-LICENSE.txt`。

`tools/map_geometry.py` 解码 TopoJSON，处理跨 ±180° 经线的多边形和南极闭合，并使用同一 `PROJECTION` 生成 SVG。构建工具也把投影参数注入应用，避免底图与站点各用一套坐标。运行时不请求外部地图服务。

`meta.version` 是应用版本，不是票务核验日期；只有重新核实官方资料时才更新核验日期。
