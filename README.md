# picfinder_take
个人~~缝合~~修改的Hoshino bot搜图插件。

这个插件的主要思路其实是在hoshino上还原隔壁 [@Tsuk1ko](https://github.com/Tsuk1ko) 大佬家的[竹竹](https://github.com/Tsuk1ko/cq-picsearcher-bot)的搜图交互体验（所以插件名是たけ）

代码主体部分来自于 [@Watanabe-Asa](https://github.com/Watanabe-Asa)大佬的 [搜图](https://github.com/pcrbot/Salmon-plugin-transplant#%E6%90%9C%E5%9B%BE)与 [@Cappuccilo](https://github.com/Cappuccilo)大佬的 [以图搜图](https://github.com/pcrbot/cappuccilo_plugins#%E4%BB%A5%E5%9B%BE%E6%90%9C%E5%9B%BE)，感谢各位大佬的代码）

---

6.1更新：增加私聊搜图、截屏识别和代理功能

todo:把requests全换成异步（咕咕咕）

## 特点  

- 搜索SauceNao，在相似率过低时自动补充搜索ascii2d，相似率阈值可在config中调整。搜索结果显示数量可在config中调整。  

- 解析SauceNao和ascii2d搜索结果的作品详细信息。SauceNao全部42个index格式解析都已完成；ascii2d常见格式应该也能解析，一些奇怪格式的外部登录不敢保证）  

- 获取SauceNao和ascii2d的结果缩略图，缩略图可在config中关闭。  

- 搜图结果可由普通回复切换为合并转发回复，减少刷屏情况。发送模式可在config中调整。~~似乎存在合并转发在服务器上概率发不出来的玄学bug，我是实在看不出来哪有问题了，如果有大佬帮忙修了就最好了（躺）~~

- 增加批量搜图模式，解决移动端文字命令+图片发送麻烦的问题。

- 增加搜图每人每日限额，可在config中调整限额。要懂得节制噢.jpg

- New！增加简单的手机截屏识别功能，判断为整屏手机截屏时会拒绝搜索 ~~（你会截你马个图.jpg）~~

- New！增加私聊搜图功能，有效缓解腾讯吞图（但反之临时会话下搜索结果很容易被吞，要稳定使用需加bot好友）

- New！增加代理设置，方便qiang内使用


## 用法

- 申请并在config中配置SauceNao的API key

- 发送'@机器人+单张或多张图片'直接搜索。

- 发送'\[机器人昵称\]搜图'进入搜图模式，直接发送图片搜索；发送'谢谢[机器人昵称]'退出搜图模式，或停止发图等待超时后自动退出。

