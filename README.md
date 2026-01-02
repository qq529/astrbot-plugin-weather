# astrbot-plugin-weather

一个用于 AstrBot 的天气查询插件，使用 suyanw.cn API。

## 简介

本插件允许用户通过简单的指令查询指定城市的实时天气信息、空气质量以及生活指数。

## 安装

1. 确保已安装 [AstrBot](https://github.com/Soulter/AstrBot)。
2. 将本插件放置在 AstrBot 的 `plugins` 目录下。
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
   (注意：AstrBot 通常会自动处理插件依赖)

## 使用方法

### 指令

- `weather <城市名>`
  - 示例：`weather 北京`
  - 描述：查询指定城市的天气信息。如果不提供城市名，默认查询广州。

### 响应内容

插件将返回以下信息：
- 实时天气状况（温度、湿度、风向、风速、能见度等）
- 空气质量 (PM2.5)
- 生活指数（穿衣、运动、防晒等建议）
- 天气预警（如果有）

## 配置

本插件目前无需额外配置文件。

## 许可证

[MIT License](LICENSE)
