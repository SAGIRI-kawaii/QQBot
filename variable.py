#coding=utf-8
from mirai import Mirai
import datetime
import time

memberSetuNet={}         #每个群每个成员要的网络setu计数（限制每人五张）
memberSetuFobidden={}       #每个群被禁止要setu的成员id
memberPicCount={}           #每个群成员要setu/real的次数
group_repeat={}             #每个群判断是否复读的dict
group_repeat_switch={}      #每个群的复读开关
timeDisable={}              #关闭setu开关的时间
searchReady={}              #接下来要进行搜图的id
pmlimit={}                  #setu/real限制每分钟张数人员记录
limitQuantity={}            #各群限制setu/real每分钟张数


localtime = time.localtime(time.time())
day_set=localtime.tm_mday

setuCount=0         #网络setu编号
count=0             #setu保存编号
bizhiCount=0        #网络壁纸编号
setuCalled=0        #响应setu请求次数
bizhiCalled=0       #响应壁纸请求次数
weatherCalled=0     #响应天气请求次数
realCalled=0        #响应real请求次数
responseCalled=0    #响应请求次数
dragonId=[]         #龙王id（可能有多个）
dragon={}           #各群今日是否已宣布龙王
groupR18={}         #各群组r18开关
management={}       #拥有管理权限的用户id
searchCount=0       #搜图编号
city=[]             #全国城市（地区）列表

n_time = datetime.datetime.now()    #目前时间
start_time = 0    #程序启动时间
d_time = datetime.datetime.strptime(str(datetime.datetime.now().date())+'23:00', '%Y-%m-%d%H:%M')   #龙王宣布时间

setuForbidden=[753400372,757627813]         #禁止要setu的群
realForbidden=[753400372,757627813]         #禁止要real的群
bizhiForbidden=[753400372,757627813]        #禁止要bizhi的群
forbiddenCount={}                           #禁止要setu后要setu的次数


setuSrc=""                   #setu api地址
bizhiSrc=""                                           #壁纸api地址
zuanHighSrc=""                           #祖安（High）api地址
zuanLowSrc=""                  #祖安（Low）api地址
rainbowSrc=""                             #彩虹屁api地址
searchSrc="https://saucenao.com/"                                                       #搜图网址
translateSrc=""          #翻译地址
weatherSrc="" #天气api地址

weatherCalledDist="S:\MiRai_QQRobot\info\weather.txt"           #天气调用数据存储路径
setuCalledDist="S:\MiRai_QQRobot\info\setu.txt"                 #setu调用数据存储路径
bizhiCalledDist="S:\MiRai_QQRobot\info\\bizhi.txt"              #壁纸调用数据存储路径
realCalledDist="S:\MiRai_QQRobot\info\\real.txt"                #real调用数据存储路径
responseCalledDist="S:\MiRai_QQRobot\info\\responseCount.txt"   #响应数据存储路径

setuDist="M:\\Pixiv\\pxer_new\\"                                  #setu存储路径
setu18Dist="M:\\Pixiv\\pxer18_new\\"                              #setuR18存储路径
bizhiDist="M:\\Pixiv\\bizhi\\"                                   #壁纸存储路径
realDist="M:\\Pixiv\\reality\\"                                  #真人setu存储路径
timeDist="M:\\pixiv\\time\\"                                     #时间图片文件夹存储路径
responseDist="S:\MiRai_QQRobot\info\\response.txt"              #日志存储路径
responseOldDist="S:\MiRai_QQRobot\info\\oldResponse.txt"        #旧日志存储路径
adminDist="S:\MiRai_QQRobot\info\\admin.txt"                    #管理员数据存储路径

angryDist="S:\\MiRai_QQRobot\\img\\angry.jpg"                   #生气图片绝对路径
dragonDist="S:\MiRai_QQRobot\info\dragon.txt"                  #龙王数据记录
searchCountDist="S:\MiRai_QQRobot\info\searchCount.txt"        #搜索编号存储路径
setuBotDist="M:\pixiv\\botImage\\"                              #涩图机器人监听保存图片路径
searchDist="M:\pixiv\\search\\"                                 #涩图机器人搜图保存图片路径
clockPreviewDist="M:\pixiv\\time\preview\\"                     #表盘预览图存储路径
clockSaveDist="S:\MiRai_QQRobot\info\\clockChoice.txt"        #表盘选择数据存储路径

reply_word=["啧啧啧","确实","giao","？？？","???","芜湖","是谁打断了复读？","是谁打断了复读?","老复读机了","就这","就这？","就这?"]     #复读关键词
non_reply=["setu","bizhi","","别老摸了，给爷冲！","real","几点了","几点啦","几点啦?","几点了?","冲？","今天我冲不冲？"]      #不复读关键词
setuCallText=["[Image::A3C91AFE-8834-1A67-DA08-899742AEA4E5]","[Image::A0FE77EE-1F89-BE0E-8E2D-62BCD1CAB312]","[Image::04923170-2ACB-5E94-ECCD-953F46E6CAB9]","[Image::3FFFE3B5-2E5F-7307-31A4-2C7FFD2F395F]","[Image::8A3450C7-0A98-4E81-FA24-4A0342198221]","setu","车车","开车","来点色图","来点儿车车"]
searchCallText=["search","搜图"]
timeCallText=["几点啦","几点了","几点啦？","几点了？","time"]
setuBot=[]
setuGroup=[]
repeatBot=[]

command="""command:
    打开setu开关:
        setting.setuEnable
    关闭setu开关:
        setting.setuDisable
    打开r18开关:
        setting.r18Enable
    关闭r18开关:
        setting.r18Disable
    允许某成员要setu:
        setting.memberSetuEnable@member
    禁止某成员要setu:
        setting.memberSetuDisable@member
    设置模式为'normal/zuanHigh/zuanLow/rainbow':
        setting.setMode.'normal/zuanHigh/zuanLow/rainbow'
    设置setu功能关闭时间:
        setting.timeDisable HH:MM to HH:MM
    设置setu功能全天开放:
        setting.timeAllDay
    获取目前全部信息:
        check.all
    获取某成员setu索取计数:
        check.memberSetuCount@member
    获取本群内群成员setu索取计数:
        check.memberSetuCountAll
    获取所有管理人员:
        check.allAdmin"""

hostCommand="""Host Command:
    本地setu:
        setting.setSetuLocal
    网络setu:
        setting.setSetuNet
    本地bizhi:
        setting.setBizhiLocal
    网络bizhi:
        setting.setBizhiNet
    关闭机器人:
        setting.offline
    打开机器人(offline状态下):
        setting.online
    添加管理员:
        setting.addAdmin@member
    删除管理员:
        setting.deleteAdmin@member
    查看系统信息:
        info.sys"""

info="""info:
            setu调用次数：info.setuCount
            bihzi调用次数:info.bizhiCount
            天气调用次数:info.weatherCount"""

menu="""menu:
    1.营销号生成器(暂时关闭)
    2.问我问题
    3.碧蓝航线wiki舰娘/装备查询
    4.天气查询
    5.setu
    6.bizhi
    7.p站搜图
    使用 @机器人 编号 查询使用方法"""

mode="""mode:
    1.normal - 普通模式
    2.zuanHigh - 祖安模式(高能)
    3.zuanLow - 祖安模式(低能)
    4.rainbow - 彩虹屁模式
    使用 @机器人 编号 调用
"""

status={}     #机器人目前状态
# mode_now="normal"   #机器人说话模式（普通、祖安High、祖安Low、彩虹屁）
MemberList={}       #群成员
clockChoice={}      #表盘选择
blackList=[]        #黑名单
