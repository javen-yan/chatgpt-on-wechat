## 插件说明

可以根据需求设置入群欢迎、群聊拍一拍、退群等消息的自定义提示词，也支持为每个群设置对应的固定欢迎语。

该插件也是用户根据需求开发自定义插件的示例插件，参考[插件开发说明](https://github.com/zhayujie/chatgpt-on-wechat/tree/master/plugins)

## 插件配置

将 `plugins/soupan` 目录下的 `config.json.template` 配置模板复制为最终生效的 `config.json`。 (如果未配置则会默认使用`config.json.template`模板中配置)。

以下是插件配置项说明：

```json
{
  "soupan_uri": "https://www.esoua.com:3001/v2/ali/search",
  "soupan_check_uri": "https://www.esoua.com:3001/v2/ali/checkLink2",
  "soupan_auth": {
    "user": "",
    "password": ""
  }
}
```


