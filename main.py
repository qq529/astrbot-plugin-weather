import aiohttp
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger  # 可选，用于日志

@register(
    name="weather",
    author="qq529",
    description="查询天气信息，使用 suyanw.cn API",
    version="1.0.1",
    repo="https://github.com/qq529/astrbot-plugin-weather"
)
class Main(Star):  # 类名可以是 Main 或 WeatherPlugin 等
    def __init__(self, context: Context):
        super().__init__(context)
        self.context = context

        # 注册命令：weather [城市]
        @filter.command("weather", aliases=["天气"])  # 可加别名，如 "天气 北京"
        async def weather_handler(event: AstrMessageEvent):
            message_str = event.message_str.strip()
            parts = message_str.split(maxsplit=1)
            city = parts[1].strip() if len(parts) > 1 else "广州"

            if not city:
                yield event.plain_result("请提供城市名称，例如: weather 北京")

            url = f"https://api.suyanw.cn/api/weather.php?city={city}"

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            yield event.plain_result(f"API 请求失败，状态码: {response.status}")
                            return

                        data = await response.json()

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
                            code = data.get("code")
                            error_msg = error_codes.get(code, data.get("text", "未知错误"))
                            yield event.plain_result(f"API 错误: {error_msg} (code: {code})")
                            return

                        weather_data = data["data"]
                        current = weather_data["current"]

                        result = f"**{current['city']} 天气信息** (更新: {current['time']})\n\n"
                        result += f"天气: {current['weather']} ({current['weatherEnglish']})\n"
                        result += f"温度: {current['temp']}°C ({current['fahrenheit']}°F)\n"
                        result += f"湿度: {current['humidity']}\n"
                        result += f"风力: {current['wind']} {current['windSpeed']}\n"
                        result += f"能见度: {current['visibility']}\n"
                        result += f"空气质量: PM2.5 {current['air_pm25']} (AQI: {current['air']})\n\n"

                        result += "**生活指数（部分）**\n"
                        for item in weather_data["living"][:10]:
                            result += f"- {item['name']}: {item['index']} —— {item['tips']}\n"

                        # 发送天气图标图片（可选）
                        if current.get("image"):
                            yield event.image_result(current["image"])

                        yield event.plain_result(result)

            except Exception as e:
                logger.error(f"Weather plugin error: {str(e)}")
                yield event.plain_result(f"发生异常: {str(e)}")
