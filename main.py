import aiohttp
import json
from astrbot.api import Context, AstrMessageEvent, CommandResult, Plain

API_URL = "https://api.suyanw.cn/api/weather.php"

class Main:
    def __init__(self, context: Context) -> None:
        self.context = context
        # 注册命令: weather [city], 支持 regex 捕获城市
        self.context.register_commands(
            "weather",
            r"^weather\s*(.*)$",
            "查询指定城市的天气信息（例如: weather 北京）",
            1,
            self.get_weather,
            use_regex=True
        )

    async def get_weather(self, message: AstrMessageEvent, context: Context):
        # 提取城市，从消息中获取或默认
        match = message.message_str.split(maxsplit=1)
        city = match[1].strip() if len(match) > 1 else "广州"
        
        if not city:
            return CommandResult(chain=[Plain("请提供城市名称，例如: weather 北京")])

        url = f"{API_URL}?city={city}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return CommandResult(chain=[Plain(f"API 请求失败，HTTP 状态码: {response.status}")])
                    
                    data = await response.json()
                    
                    if data.get("code") != 1:
                        error_msg = data.get("text", "未知错误")
                        # 根据错误码表映射消息
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
                        error_msg = error_codes.get(code, error_msg)
                        return CommandResult(chain=[Plain(f"API 错误: {error_msg} (code: {code})")])
                    
                    weather_data = data["data"]
                    current = weather_data["current"]
                    
                    # 格式化输出
                    result = f"**{current['city']} 天气信息** (更新时间: {current['time']})\n\n"
                    result += f"天气: {current['weather']} ({current['weatherEnglish']})\n"
                    result += f"温度: {current['temp']}°C / {current['fahrenheit']}°F\n"
                    result += f"湿度: {current['humidity']}\n"
                    result += f"风向/风速: {current['wind']} {current['windSpeed']}\n"
                    result += f"能见度: {current['visibility']}\n"
                    result += f"空气质量: PM2.5 {current['air_pm25']} (指数: {current['air']})\n\n"
                    
                    # 生活指数（选部分展示，避免太长）
                    result += "**生活指数**\n"
                    for living in weather_data["living"][:10]:  # 前10个
                        result += f"- {living['name']}: {living['index']} - {living['tips']}\n"
                    
                    # 如果有预警
                    if weather_data.get("warning"):
                        result += "\n**天气预警**: " + json.dumps(weather_data["warning"], ensure_ascii=False)
                    
                    return CommandResult(chain=[Plain(result)])

        except Exception as e:
            return CommandResult(chain=[Plain(f"发生异常: {str(e)}")])