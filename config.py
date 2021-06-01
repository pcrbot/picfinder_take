threshold =70      # SauceNAO相似度阈值，低于该相似度自动追加ascii2d搜索

SAUCENAO_KEY = "xxxxxxxxxxxxxxxxxxxxx"      # SauceNAO 的 API key

SAUCENAO_RESULT_NUM = 3      # SauceNAO搜索结果显示数量

ASCII_RESULT_NUM = 3      # ascii2d搜索结果显示数量

SEARCH_TIMEOUT = 60      # 连续搜索模式超时时长

DAILY_LIMIT = 10      # 搜图每日限额

CHAIN_REPLY = True      # 是否启用合并转发回复模式

THUMB_ON = True      # 是否启用缩略图

CHECK = True      # 是否开启手机截屏判定

proxies={ 
               'http':'',
               'https':''
              }        # 网络代理

helptext='''
[@竹竹+图片] 单张/多张搜图
[竹竹搜图] 进入批量搜图模式
[谢谢竹竹] 退出批量搜图模式
'''.strip()