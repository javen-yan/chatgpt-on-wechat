# encoding:utf-8

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common.log import logger
from plugins import *
from config import conf
import requests
import json


not_found_template = """
>>>>>>《{name}》搜索结果如下<<<<<<

搜索无结果

温馨提示：别错字、漏字、多字

如果不确定剧名，就搜剧名前几个或后面几个字！

>>>>>>感谢您的支持<<<<<<
"""

found_ok_template = """
>>>>>>《{name}》搜索结果如下<<<<<<

{result}

>>>>>>感谢您的支持<<<<<<
"""


@plugins.register(
    name="Soupan",
    desire_priority=-1,
    hidden=True,
    desc="A plugin for resource search",
    version="0.1",
    author="javen",
)

class Soupan(Plugin):
    soupan_uri = "https://www.esoua.com:3001/v2/ali/search"
    soupan_check_uri = "https://www.esoua.com:3001/v2/ali/checkLink2"
    quark_uri = "https://pan.quark.cn/s"
    baidu_uri = "https://pan.baidu.com/s"

    def __init__(self):
        super().__init__()
        try:
            self.config = super().load_config()
            if not self.config:
                self.config = self._load_config_template()
            self.soupan_uri = self.config.get("soupan_uri", self.soupan_uri)
            self.soupan_check_uri = self.config.get("soupan_check_uri", self.soupan_check_uri)
            self.quark_uri = self.config.get("quark_uri", self.quark_uri)
            self.baidu_uri = self.config.get("baidu_uri", self.baidu_uri)
            logger.info("[Soupan] inited")
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        except Exception as e:
            logger.error(f"[Soupan]初始化异常：{e}")
            raise "[Soupan] init failed, ignore "

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [
            ContextType.TEXT,
        ]:
            return
        msg: ChatMessage = e_context["context"]["msg"]

        content = e_context["context"].content
        logger.debug("[Soupan] on_handle_context. content: %s" % content)
        # content 以"搜"开头
        if content.startswith("搜"):
            reply = Reply()
            reply.type = ReplyType.TEXT
            # 执行搜索
            keyword = content[1:]
            if keyword:
                result = self._search(keyword)
                if result:
                    reply.content = result
                else:
                    reply.content = not_found_template.format(name=keyword)
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

    def get_help_text(self, **kwargs):
        help_text = "输入'搜xxxxx'会自动搜索网盘视频\n"
        return help_text

    def _load_config_template(self):
        logger.debug("No Soupan plugin config.json, use plugins/Soupan/config.json.template")
        try:
            plugin_config_path = os.path.join(self.path, "config.json.template")
            if os.path.exists(plugin_config_path):
                with open(plugin_config_path, "r", encoding="utf-8") as f:
                    plugin_conf = json.load(f)
                    return plugin_conf
        except Exception as e:
            logger.exception(e)

    def _search(self, keyword):
        try:
            logger.info(f"[Soupan] search keyword: {keyword}")
            payload = json.dumps({
                "pageSize": 30,
                "pageNum": 1,
                "title": keyword,
                "root": 0,
                "cat": "all"
            })
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json',
                'Origin': 'https://ps.esoua.com',
                'Referer': 'https://ps.esoua.com/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"'
            }
            response = requests.request("POST", self.soupan_uri, headers=headers, data=payload)
            return self._response_process(keyword, response)
        except Exception as e:
            logger.error(f"[Soupan] search error: {e}")
            return None

    def _response_process(self, keyword, response):
        try:
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    results = ""
                    data = result.get("data")
                    if data:
                        for item in data:
                            title = item.get("title")
                            key = item.get("key")
                            root = item.get("root")
                            if root == 4:
                                link = f"{self.baidu_uri}/{key}"
                                results += f"{title}\n百度网盘:{link}\n"
                            else:
                                if self._check_link(item):
                                    link = f"{self.quark_uri}/{key}"
                                    results += f"{title}\n夸克网盘:{link}\n"
                        return found_ok_template.format(name=keyword, result=results)
        except Exception as e:
            logger.error(f"[Soupan] response process error: {e}")
            return None

    def _check_link(self, item):
        try:
            payload = {
                "id": item.get("id"),
                "key": item.get("key"),
                "root": item.get("root"),
                "shareUserName": "热心网友"
            }
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json',
                'Origin': 'https://ps.esoua.com',
                'Referer': 'https://ps.esoua.com/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"'
            }
            logger.info(f"[Soupan] check url {item.get('title')}")
            response = requests.request("POST", self.soupan_check_uri, headers=headers, data=payload)
            if response.status_code == 200:
                result = response.json()
                return result.get("code") == 200
        except Exception as e:
            logger.error(f"[Soupan] response process error: {e}")
            return None



