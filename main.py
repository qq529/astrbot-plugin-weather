import aiohttp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register(
    "weather",                                      # 插件名称
    "qq529",                                        # 作者
    "查询实时天气和生活指数，使用 suyanw.cn 免费天气 API",  # 描述
    "1.0.0",                                        # 版本
    "https://github.com/qq529/astrbot_plugin_weather.git"  # 仓库地址（建议填写正确）
)
class Main(Star):
    def __init__(self, context: Context):
        super().__init__(context)

        @filter.command("weather", aliases=["天气", "tq", "wq"])
        async def weather_handler(self, event: AstrMessageEvent):
            """
            支持命令：
            weather 北京
            天气 上海
            tq 广州
            wq 深圳
            如果不写城市，默认查询广州
            """
            message_str = event.message_str.strip()
            parts = message_str.split(maxsplit=1)
            city = parts[1].strip() if len(parts) > 1 else "广州"

            if not city:
                yield event.plain_result("请提供城市名称，例如：weather 北京 或 天气 上海")
                return

            url = f"https://api.suyanw.cn/api/weather.php?city={city}"

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as response:
                        if response.status != 200:
                            yield event.plain_result(f"请求天气 API 失败，状态码：{response.status}")
                            return

                        data = await response.json()

                        # API 返回错误
                        if data.get("code") != 1:
                            error_codes = {
                                400: "请求参数错误！",
                                403: "请求被服务器拒绝！",
                                405: "客户端请求中的方法被禁止！",
                                408: "请求时间过长！",
                                500: "服务端内部错误！",
                                501: "服务端不支持请求的功能，无法完成请求！",
                                503: "系统维护中！"
                            }
                            code = data.get("code", 0)
                            msg = error_codes.get(code, data.get("text", "未知错误"))
                            yield event.plain_result(f"天气 API 返回错误：{msg} (code: {code})")
                            return

                        weather_data = data["data"]
                        current = weather_data["current"]

                        # 构建文字信息
                        result = f"🌤️ **{current['city']} 实时天气**\n"
                        result += f"更新时间：{current['time']}\n\n"
                        result += f"天气：{current['weather']} ({current['weatherEnglish']})\n"
                        result += f"温度：{current['temp']}°C (体感 {current['fahrenheit']}°F)\n"
                        result += f"湿度：{current['humidity']}\n"
                        result += f"风力：{current['wind']} {current['windSpeed']}\n"
                        result += f"能见度：{current['visibility']}\n"
                        result += f"空气质量：PM2.5 {current['air_pm25']} (AQI {current['air']})\n\n"

                        # 精选生活指数（避免消息过长）
                        selected = ["穿衣指数", "感冒指数", "紫外线强度指数", "洗车指数", "运动指数", "舒适度指数", "防晒指数"]
                        result += "📊 **生活指数精选**\n"
                        for item in weather_data["living"]:
                            if item["name"] in selected:
                                result += f"• {item['name']}：{item['index']} —— {item['tips']}\n"

                        # 先发送天气图标（如果有）
                        if current.get("image"):
                            yield event.image_result(current["image"])

                        # 再发送文字内容
                        yield event.plain_result(result)

            except aiohttp.ClientError as ce:
                logger.error(f"网络请求错误: {ce}")
                yield event.plain_result("网络连接失败，请稍后再试。")
            except Exception as e:
                logger.error(f"天气插件未知错误: {str(e)}")
                yield event.plain_result(f"查询出错：{str(e)}")