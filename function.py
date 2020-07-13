#coding=utf-8
from mirai import Mirai, Plain, MessageChain, Friend, Image, Group, protocol, Member, At, Face, JsonMessage
import os, random, shutil
from os.path import join, getsize
from variable import *
from PIL import Image as IMG
from io import BytesIO
import re
import requests
from urllib import parse
import pymysql
from itertools import chain
import wmi
import hashlib
import string
from urllib.parse import quote
from pynvml import *


BotQQ =  # 字段 qq 的值 
HostQQ =  #主人QQ

# 初始化city列表
city=[]
conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
cur = conn.cursor()
sql = "select cityZh from city"
cur.execute(sql) 
data = cur.fetchall()
city=list(chain.from_iterable(data))
cur.close()
conn.close()

# 日志记录
def record(operation,picUrl,sender,groupId,result,operationType):
    global responseCalled
    responseCalled+=1
    timeNow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(timeNow)
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    if operationType=='img':
        sql = "INSERT INTO imgCalled (time,operation,picUrl,sender,groupId,result) VALUES ('%s','%s','%s',%d,%d,%d)"%(timeNow,operation,pymysql.escape_string(picUrl),sender,groupId,result)
    elif operationType=='function':
        sql = "INSERT INTO functionCalled (time,operation,sender,groupId,result) VALUES ('%s','%s',%d,%d,%d)"%(timeNow,operation,sender,groupId,result)
    cur.execute(sql) 
    cur.close()
    conn.commit()
    conn.close()
    print("data recorded!")

# 数据更新
def updateData(data,operationType):
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    if operationType=='setu':
        sql = "UPDATE calledCount SET setuCalled=%d"%data
    elif operationType=='real':
        sql = "UPDATE calledCount SET realCalled=%d"%data
    elif operationType=='bizhi':
        sql = "UPDATE calledCount SET bizhiCalled=%d"%data
    elif operationType=='weather':
        sql = "UPDATE calledCount SET weatherCalled=%d"%data
    elif operationType=='response':
        sql = "UPDATE calledCount SET responseCalled=%d"%data
    elif operationType=='clock':
        sql = "UPDATE calledCount SET clockCalled=%d"%data
    elif operationType=='search':
        sql = "UPDATE calledCount SET searchCount=%d"%data
    elif operationType=='botSetuCount':
        sql = "UPDATE calledCount SET botSetuCount=%d"%data
    elif operationType=='predict':
        sql = "UPDATE calledCount SET predictCount=%d"%data
    elif operationType=='yellow':
        sql = "UPDATE calledCount SET yellowPredictCount=%d"%data
    else:
        print("error: none operationType named %s!"%operationType)
        return
    cur.execute(sql) 
    cur.close()
    conn.commit()
    conn.close()

# 添加群信息（数据库）
def addGroupinit(groupId,groupName):
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = """
    INSERT INTO setting 
    (groupId,groupName,`repeat`,setuLocal,bizhiLocal,countLimit,`limit`,setu,bizhi,`real`,r18,search,speakMode,switch,forbiddenCount) 
    VALUES 
    (%d,'%s',%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,'%s','%s',0)
    """%(groupId,groupName,True,True,True,True,6,True,True,True,False,True,"normal","online")
    cur.execute(sql) 
    cur.close()
    conn.commit()
    conn.close()
    print("add group info init finished!")

# 检查有无群组变更(初始化)
def checkGroupInit(groupList):
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "select groupId from setting"
    cur.execute(sql) 
    data = cur.fetchall()
    groupId=list(chain.from_iterable(data))
    print(groupId)
    for i in groupList:
        print(i.id,':',i.name)
        if i.id not in groupId:
            sql = """
            INSERT INTO setting 
            (groupId,groupName,`repeat`,setuLocal,bizhiLocal,countLimit,`limit`,setu,bizhi,`real`,r18,search,speakMode,switch,forbiddenCount) 
            VALUES 
            (%d,'%s',%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,'%s','%s',0)
            """%(i.id,i.name,True,True,True,True,6,True,True,True,False,True,"normal","online")
            cur.execute(sql) 
            sql = """
            INSERT INTO admin 
            (groupId,adminId) 
            VALUES 
            (%d,%d)
            """%(i.id,HostQQ)
            cur.execute(sql) 
    sql = "select groupId from admin"
    cur.execute(sql) 
    data = cur.fetchall()
    groupId=list(chain.from_iterable(data))
    for i in groupList:
        if i.id not in groupId:
            sql = """
            INSERT INTO admin 
            (groupId,adminId) 
            VALUES 
            (%d,%d)
            """%(i.id,HostQQ)
            cur.execute(sql) 
    cur.close()
    conn.commit()
    conn.close()

# 获取调用次数数据
def getData(data):
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "SELECT %s from calledCount"%data
    cur.execute(sql) 
    data=cur.fetchone()[0]
    cur.close()
    conn.close()
    return data

# 获取本群设置
def getSetting(groupId,name):
    sqlKeyWord=["repeat","real","limit"]
    if name in sqlKeyWord:
        name='`'+name+'`'
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "SELECT %s from setting WHERE groupId=%d"%(name,groupId)
    # print(sql)
    cur.execute(sql) 
    data=cur.fetchone()[0]
    cur.close()
    conn.close()
    return data

# 更新本群设置
def updateSetting(groupId,name,new):
    strKeyWord=["speakMode","switch"]
    sqlKeyWord=["repeat","real","limit"]
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    if name in sqlKeyWord:
        name='`'+name+'`'
    if name in strKeyWord:
        sql = "UPDATE setting SET %s='%s' WHERE groupId=%d"%(name,new,groupId)
    else:
        sql = "UPDATE setting SET %s=%s WHERE groupId=%d"%(name,new,groupId)
    cur.execute(sql) 
    cur.close()
    conn.commit()
    conn.close()

# 获取本群管理员
def getAdmin(groupId):
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "SELECT adminId from admin WHERE groupId=%d"%groupId
    cur.execute(sql) 
    data=cur.fetchall()
    admin=list(chain.from_iterable(data))
    cur.close()
    conn.close()
    return admin

# 是否要搜图
def getSearchReady(groupId,sender):
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "SELECT `status` from searchReady WHERE groupId=%d and memberId=%d"%(groupId,sender)
    cur.execute(sql) 
    try:
        result=cur.fetchone()[0]
    except TypeError:
        sql="INSERT INTO searchReady (groupId,memberId,`status`) VALUES (%d,%d,%d)"%(groupId,sender,False)
        cur.execute(sql) 
        conn.commit()
        return False
    cur.close()
    conn.close()
    return result

# 是否要预测
def getPredictReady(groupId,sender):
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "SELECT `status` from predictReady WHERE groupId=%d and memberId=%d"%(groupId,sender)
    cur.execute(sql) 
    try:
        result=cur.fetchone()[0]
    except TypeError:
        sql="INSERT INTO predictReady (groupId,memberId,`status`) VALUES (%d,%d,%d)"%(groupId,sender,False)
        cur.execute(sql) 
        conn.commit()
        return False
    cur.close()
    conn.close()
    return result
    
# 是否要评价黄图
def getYellowPredictReady(groupId,sender):
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "SELECT `status` from yellowPredictReady WHERE groupId=%d and memberId=%d"%(groupId,sender)
    cur.execute(sql) 
    try:
        result=cur.fetchone()[0]
    except TypeError:
        sql="INSERT INTO yellowPredictReady (groupId,memberId,`status`) VALUES (%d,%d,%d)"%(groupId,sender,False)
        cur.execute(sql) 
        conn.commit()
        return False
    cur.close()
    conn.close()
    return result

# 修改搜图判断状态
def setSearchReady(groupId,sender,status):
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "SELECT `status` from searchReady WHERE groupId=%d and memberId=%d"%(groupId,sender)
    cur.execute(sql) 
    try:
        result=cur.fetchone()[0]
        sql="UPDATE searchReady SET `status`=%d WHERE groupId=%d and memberId=%d"%(status,groupId,sender)
        cur.execute(sql) 
    except TypeError:
        sql="INSERT INTO searchReady (groupId,memberId,Status) VALUES (%d,%d,%d)"%(groupId,sender,status)
        cur.execute(sql) 
    cur.close()
    conn.commit()
    conn.close()

# 修改预测图片判断状态
def setPredictReady(groupId,sender,status):
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "SELECT `status` from predictReady WHERE groupId=%d and memberId=%d"%(groupId,sender)
    cur.execute(sql) 
    try:
        result=cur.fetchone()[0]
        sql="UPDATE predictReady SET `status`=%d WHERE groupId=%d and memberId=%d"%(status,groupId,sender)
        cur.execute(sql) 
    except TypeError:
        sql="INSERT INTO predictReady (groupId,memberId,Status) VALUES (%d,%d,%d)"%(groupId,sender,status)
        cur.execute(sql) 
    cur.close()
    conn.commit()
    conn.close()

# 修改评价黄图判断状态
def setYellowPredictReady(groupId,sender,status):
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "SELECT `status` from yellowPredictReady WHERE groupId=%d and memberId=%d"%(groupId,sender)
    cur.execute(sql) 
    try:
        result=cur.fetchone()[0]
        sql="UPDATE yellowPredictReady SET `status`=%d WHERE groupId=%d and memberId=%d"%(status,groupId,sender)
        cur.execute(sql) 
    except TypeError:
        sql="INSERT INTO yellowPredictReady (groupId,memberId,Status) VALUES (%d,%d,%d)"%(groupId,sender,status)
        cur.execute(sql) 
    cur.close()
    conn.commit()
    conn.close()

# 随机图片路径
def randomPic(dir):
    pathDir = os.listdir(dir)
    dist = random.sample(pathDir, 1)[0]
    return dir+dist

# 获取天气
def getWeather(message,sender):
    global city
    point=message.toString()[25:]
    print("天气查询，城市：",point)
    if point not in city:
        return [
            At(target=sender),
            Plain(text="请检查城市名称，只支持中国城市及部分地区哦~")
        ]
    weather_src=weatherSrc+point
    response=requests.get(weather_src)
    html=response.text
    html.replace("\/","/")
    html.replace("//",'/')
    html=html.encode('utf-8').decode('unicode_escape')
    wea=re.findall(r'wea":"(.*?)"',html,re.S)[0]
    tem=re.findall(r'"tem":"(.*?)"',html,re.S)[0]
    tem_day=re.findall(r'"tem_day":"(.*?)"',html,re.S)[0]
    tem_night=re.findall(r'"tem_night":"(.*?)"',html,re.S)[0]
    win=re.findall(r'"win":"(.*?)"',html,re.S)[0]
    win_speed=re.findall(r'"win_speed":"(.*?)"',html,re.S)[0]
    win_meter=re.findall(r'"win_meter":"(.*?)"',html,re.S)[0]
    air=re.findall(r'"air":"(.*?)"',html,re.S)[0]
    return [
        Plain(text="%s今日天气\n"%point),
        Plain(text="天气情况：%s\n"%wea),
        Plain(text="实时温度：%s℃\n"%tem),
        Plain(text="最高温：%s℃\n"%tem_day),
        Plain(text="最低温：%s℃\n"%tem_night),
        Plain(text="风向：%s\n"%win),
        Plain(text="风力等级：%s\n"%win_speed),
        Plain(text="风速：%s\n"%win_meter),
        Plain(text="空气质量：%s"%air)
    ]
 
# 营销号生成器
def yingxiaohao(somebody,something,other_word):
    txt = '''    {somebody}{something}是怎么回事呢？{somebody}相信大家都很熟悉，但是{somebody}{something}是怎么回事呢，下面就让小编带大家一起了解吧。
    {somebody}{something}，其实就是{somebody}{other_word}，大家可能会很惊讶{somebody}怎么会{something}呢？但事实就是这样，小编也感到非常惊讶。
    这就是关于{somebody}{something}的事情了，大家有什么想法呢，欢迎在评论区告诉小编一起讨论哦！'''
    return [Plain(text=txt.format(somebody=somebody, something=something, other_word=other_word))]

# 问你点儿事儿
def askSth(sender,question):
    return [
        At(target=sender),
        Plain(text="啧啧啧，都多大了，还不会百度嘛，不会的话谷歌也行啊\n"),
        Plain(text="什么？你说还不会？你可真是个小憨批呢\n"),
        Plain(text="没办法呢，就让聪明的我来帮帮你吧！\n"),
        Plain(text="https://baidu.sagiri-web.com/?%s"%question)
    ]

# 图片搜索
def searchImage(groupId,sender,img):
    setSearchReady(groupId,sender,False)
    searchCount=getData("searchCount")+1
    print(searchCount)
    updateData(searchCount,"search")
    dist="%s%s.png"%(searchDist,searchCount)
    img_content=requests.get(img.url).content
    image=IMG.open(BytesIO(img_content))
    image.save(dist)
    #url for headers
    url = 'https://saucenao.com/search.php'
    #picture url
    picUrl = img.url
    #json requesting url
    url2 = f'https://saucenao.com/search.php?db=999&output_type=2&testmode=1&numres=1&url={picUrl}'
    #data for posting.
    data = {
        'url' : picUrl,
        'numres' : 1,
        'testmode' : 1,
        'db' : 999,
        'output_type' : 2,
    }

    #header to fool the website.
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'Sec-Fetch-Dest' : 'document',
        'Sec-Fetch-Mode' : 'navigate',
        'Sec-Fetch-Site' : 'none',
        'Sec-Fetch-User' : '?1',
        'Referer' : url,
        'Origin' : 'https://saucenao.com',
        'Host' : 'saucenao.com'
    }

    page = requests.post(url, headers=headers, data=data)
    # html=page.text
    json_data = page.json()
    #print thumbnail URL.
    # print(json_data)
    # print(json_data['results'][0]['header']['thumbnail'])

    dist="M:\pixiv\Thumbnail\\%s.png"%searchCount
    response=requests.get(json_data['results'][0]['header']['thumbnail'])
    imgContent=response.content
    image=IMG.open(BytesIO(imgContent))
    image.save(dist)
    similarity=json_data['results'][0]['header']['similarity']
    try:
        pixiv_url=json_data['results'][0]['data']['ext_urls'][0]
    except KeyError:
        pixiv_url="None"
    if 'pixiv_id' not in json_data['results'][0]['data']:
        if 'source' not in json_data['results'][0]['data']:   
            record("search",dist,sender,groupId,False,"img")
            return [Plain(text="8好意思~没有找到相似的图诶~")]
        else:
            try:
                creator=json_data['results'][0]['data']['creator'][0]
            except Exception:
                creator="Unknown!"   
            record("search",dist,sender,groupId,True,"img")
            return [
                At(target=sender),
                Plain(text="这个结果相似度很低诶。。。。要不你康康？\n"),
                Image.fromFileSystem(dist),
                Plain(text="\n相似度:%s%%\n"%(similarity)),
                Plain(text="原图地址:%s\n"%pixiv_url),
                Plain(text="作者:%s\n"%creator),
                Plain(text="如果不是你想找的图的话可能因为这张图是最近才画出来的哦，网站还未收录呢~过段日子再来吧~")
            ]
    else:
        pixiv_id=json_data['results'][0]['data']['pixiv_id']
        user_name=json_data['results'][0]['data']['member_name']
        user_id=json_data['results'][0]['data']['member_id']           
        record("search",dist,sender,groupId,True,"img")
        return [
            At(target=sender),
            Image.fromFileSystem(dist),
            Plain(text="\n相似度:%s%%\n"%(similarity)),
            Plain(text="原图地址:%s\n"%pixiv_url),
            Plain(text="作品id:%s\n"%pixiv_id),
            Plain(text="作者名字:%s\n"%user_name),
            Plain(text="作者id:%s\n"%user_id)
        ]

# 碧蓝航线wiki网址
def blhxWiki(sender,name):
    return [
        At(target=sender),
        Plain(text="以下是%s的wiki网址，可在其中查到%s的各种信息哦：\n"%(name,name)),
        Plain(text="https://wiki.biligame.com/blhx/%s"%parse.quote(name))
    ]

# 获取全部数据
def getAllData(groupId):
    setuCalled=getData("setuCalled")            #响应setu请求次数
    bizhiCalled=getData("bizhiCalled")          #响应壁纸请求次数
    weatherCalled=getData("weatherCalled")      #响应天气请求次数
    realCalled=getData("realCalled")            #响应real请求次数
    responseCalled=getData("responseCalled")    #响应请求次数
    clockCalled=getData("clockCalled")          #响应time次数
    text="""Current State:
    setu:{setu}
    r18:{r18}
    real:{real}
    bizhi:{bizhi}
    repeat:{repeat}
    setuPosition:{setuPosition}
    bizhiPosition:{bizhiPosition}
    setuStored:{setuCount}
    setuR18Stored:{setuR18Count}
    bizhiStored:{bizhiCount}
    realStored:{realCount}
    totalStored:{totalCount}
    setuCalls:{setuCalls}
    realCalls:{realCalls}
    bizhiCalls:{bizhiCalls}
    weatherCalls:{weatherCalls}
    clockCalls:{clockCalls}
    totalResponseTimes:{totalEesponseTimes}
    Console-Pure Version: 0.5.2"""
    if getSetting(groupId,"setu"):
        setu="True"
    else:
        setu="False"
    if getSetting(groupId,"r18"):
        r18="True"
    else:
        r18="False"
    if getSetting(groupId,"real"):
        real="True"
    else:
        real="False"
    if getSetting(groupId,"bizhi"):
        bizhi="True"
    else:
        bizhi="False"
    if getSetting(groupId,"repeat"):
        repeat="True"
    else:
        repeat="False"
    if getSetting(groupId,"setuLocal"):
        setuPosition="Local"
    else:
        setuPosition="Net"
    if getSetting(groupId,"bizhiLocal"):
        bizhiPosition="Local"
    else:
        bizhiPosition="Net"
    setuCount=len(os.listdir(os.path.dirname(setuDist)))
    setuR18Count=len(os.listdir(os.path.dirname(setu18Dist)))
    bizhiCount=len(os.listdir(os.path.dirname(bizhiDist)))
    realCount=len(os.listdir(os.path.dirname(realDist)))
    totalCount=setuCount+setuR18Count+bizhiCount+realCount
    setuCalls=setuCalled
    bizhiCalls=bizhiCalled
    weatherCalls=weatherCalled
    realCalls=realCalled
    clockCalls=clockCalled
    totalResponseTimes=responseCalled
    return text.format(
        setu=setu,
        r18=r18,
        real=real,
        bizhi=bizhi,
        repeat=repeat,
        setuPosition=setuPosition,
        bizhiPosition=bizhiPosition,
        setuCount=setuCount,
        setuR18Count=setuR18Count,
        bizhiCount=bizhiCount,
        realCount=realCount,
        totalCount=totalCount,
        setuCalls=setuCalls,
        realCalls=realCalls,
        bizhiCalls=bizhiCalls,
        weatherCalls=weatherCalls,
        clockCalls=clockCalls,
        totalResponseTimes=totalResponseTimes
    )

# 获取表盘选择
def getClockChoice(groupId,sender):
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "SELECT choice from clockChoice WHERE groupId=%d and memberId=%d"%(groupId,sender)
    cur.execute(sql) 
    try:
        result=cur.fetchone()[0]
    except TypeError:
        # sql="INSERT INTO clockChoice (groupId,memberId,choice) VALUES (%d,%d,%d)"%(groupId,sender,False)
        # cur.execute(sql) 
        # conn.commit()
        return "none"
    print(result)
    cur.close()
    conn.close()
    return result

# 展示表盘
def showClock(sender):
    clockMessage=[
        At(target=sender),
        Plain(text="看中后直接发送选择表盘+序号即可哦~\n"),
        Plain(text="如:选择表盘1\n"),
        Plain(text="表盘预览:")
    ]
    clockList = os.listdir(clockPreviewDist)
    clockList.sort(key=lambda x:int(x[:-4]))
    index=1
    for i in clockList:
        clockMessage.append(Plain(text="\n%s."%index))
        clockMessage.append(Image.fromFileSystem(clockPreviewDist+i))
        index+=1
    return clockMessage

# 记录表盘选择
def recordClock(groupId,sender,choice):
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "SELECT choice from clockChoice WHERE groupId=%d and memberId=%d"%(groupId,sender)
    cur.execute(sql) 
    try:
        result=cur.fetchone()[0]
        sql="UPDATE clockChoice SET choice=%d WHERE groupId=%d and memberId=%d"%(choice,groupId,sender)
        cur.execute(sql) 
    except TypeError:
        sql="INSERT INTO clockChoice (groupId,memberId,choice) VALUES (%d,%d,%d)"%(groupId,sender,choice)
        cur.execute(sql) 
    conn.commit()
    cur.close()
    conn.close()

# 判断setting选项合法性
def configChangeJudge(config,change):
    if config=="limit" and change.isnumeric():
        return True
    if change not in settingCode:
        return False
    change=settingCode[change]
    if config=="repeat" and change==True or change==False:
        return True
    elif (config=="setuLocal" or config=="bizhiLocal") and change==True or change==False:
        return True
    elif config=="countLimit" and change==True or change==False:
        return True
    elif (config=="setu" or config=="real" or config=="bizhi" or config=="r18" or config=="search" or config=="imgPredict") and change==True or change==False:
        return True
    elif config=="speakMode" and change=="normal" or change=="zuanHigh" or change=="zuanLow" or change=="rainbow" or change=="chat":
        return True
    elif config=="switch" and change=="online" or change=="offline":
        return True
    return False

# 判断info选项合法性
def infoCheckJudge(check):
    info=["sys","setu","real","bizhi","switch","all","group","countLimit","speakMode","r18"]
    if check in info:
        return True
    return False

# 获取文件夹大小
def getFileSize(dir):
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([getsize(join(root, name)) for name in files])
    return size

# 返回主机状态
def getSysInfo():
    w=wmi.WMI()
    processor=w.Win32_Processor()
    m=w.Win32_ComputerSystem()
    operator = w.Win32_OperatingSystem()
    text="     systemInfo     \n"
    text+="--------------------\n"
    text+="CPU:\n"
    for cpu in processor:
        text+="CPU Model:%s\n"%cpu.Name
        text+="Frequency:%sMHz\n"%cpu.CurrentClockSpeed
        text+="Number of cores:%s\n"%cpu.NumberOfCores
        text+="Usage rate:%s%%\n"%cpu.LoadPercentage
    text+="--------------------\n"
    text+="GPU:\n"
    for gpu in w.Win32_VideoController():
        text+="GPU Model:%s\n"%gpu.caption
    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(0)
    meminfo = nvmlDeviceGetMemoryInfo(handle)
    text+="Total memory:%2.2fG\n"%(float(meminfo.total)/1024/1024/1024)
    text+="Used memory:%2.2fG\n"%(float(meminfo.used)/1024/1024/1024)
    text+="Free memory:%2.2fG\n"%(float(meminfo.free)/1024/1024/1024)
    text+="--------------------\n"
    text+="Memory:\n"
    for memory in m:
        tm=float(memory.TotalPhysicalMemory)/1024/1024/1024
        text+="Total memory:%.2fG\n"%tm
    for os in operator:
        text+="Used memory:%.2fG\n"%(tm-float(os.FreePhysicalMemory)/1024/1024)
        text+="Free memory:%.2fG\n"%(float(os.FreePhysicalMemory)/1024/1024)
    text+="--------------------\n"
    text+="Disk:\n"
    diskSize="300.00G"
    setuSize=getFileSize("M:\pixiv\pxer_new\\")
    setu18Size=getFileSize("M:\pixiv\pxer18_new\\")
    bizhiSize=getFileSize("M:\pixiv\\bizhi\\")
    realSize=getFileSize("M:\pixiv\\reality\\")
    text+="Drive Size:%s\n"%diskSize
    text+="Setu folder Size:%.2fG\n"%(setuSize/1024/1024/1024)
    text+="Setu18 folder Size:%.2fG\n"%(setu18Size/1024/1024/1024)
    text+="Bizhi folder Size:%.2fG\n"%(bizhiSize/1024/1024/1024)
    text+="Real folder Size:%.2fG\n"%(realSize/1024/1024/1024)
    text+="Total folder Size:%.2fG\n"%((setuSize+setu18Size+bizhiSize+realSize)/1024/1024/1024)
    text+="--------------------\n"
    time_now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text+="time:%s\n"%time_now
    text+="---------------End\n"
    return text

# 返回群组全部设置
def getGroupAllSetting(groupId):
    groupName=getSetting(groupId,"groupName")
    repeat=getSetting(groupId,"repeat")
    setuLocal=getSetting(groupId,"setuLocal")
    bizhiLocal=getSetting(groupId,"bizhiLocal")
    countLimit=getSetting(groupId,"countLimit")
    setu=getSetting(groupId,"setu")
    bizhi=getSetting(groupId,"bizhi")
    real=getSetting(groupId,"real")
    r18=getSetting(groupId,"r18")
    speakMode=getSetting(groupId,"speakMode")
    groupSetting=Plain(text="""
    groupId:%s
    groupName:%s
    repeat:%s
    setuLocal:%s
    bizhiLocal:%s
    countLimit:%s
    setu:%s
    real:%s
    bizhi:%s
    r18:%s
    speakMode:%s"""%(groupId,groupName,repeat,setuLocal,bizhiLocal,countLimit,setu,bizhi,real,r18,speakMode))
    return groupSetting

# 返回设置等信息
def showSetting(groupId,sender,check):
    settingList=["groupId","groupName","repeat","setuLocal","bizhiLocal","countLimit","setu","bizhi","real","r18","speakMode","switch"]
    if check=="sys":
        return [
            At(target=sender),
            Plain(text=getSysInfo())
        ]
    elif check=="all":
        title=Plain(text="\n-----------setting-----------\n")
        groupSetting=getGroupAllSetting(groupId)
        split=Plain(text="\n-----------System-----------\n")
        sysInfo=getSysInfo()
        return [
            At(target=sender),
            title,
            groupSetting,
            split,
            Plain(text=sysInfo)
        ]
    elif check=="group":
        title=Plain(text="\n-----------setting-----------\n")
        groupSetting=getGroupAllSetting(groupId)
        return [
            At(target=sender),
            title,
            groupSetting
        ]
    else:
        setting=getSetting(groupId,check)
        return [
            At(target=sender),
            Plain(text="group:%d %s:%d"%(groupId,check,setting))
        ]

# 判断成员能否要图（countLimit模式下）
def getMemberPicStatus(groupId,sender):
    limit=getSetting(groupId,"limit")
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "select count from memberPicCount where groupId=%d and memberId=%d"%(groupId,sender)
    cur.execute(sql) 
    data = cur.fetchone()
    if not data==None:
        data=data[0]
        sql = "select `time` from memberPicCount where groupId=%d and memberId=%d"%(groupId,sender)
        cur.execute(sql) 
        time = cur.fetchone()[0]
        if int(data)>=limit and (datetime.datetime.now()-time).seconds<60:
            return False
        elif int(data)<limit and (datetime.datetime.now()-time).seconds<60:
            sql = "update memberPicCount set count=%d where groupId=%d and memberId=%d"%(int(data)+1,groupId,sender)
        elif (datetime.datetime.now()-time).seconds>60:
            sql = "update memberPicCount set count=1,`time`='%s' where groupId=%d and memberId=%d"%(datetime.datetime.now(),groupId,sender)
        cur.execute(sql) 
    else:
        sql = "insert memberPicCount set groupId=%d,memberId=%d,time='%s',count=1"%(groupId,sender,datetime.datetime.now())
        cur.execute(sql) 
        
    cur.close()
    conn.commit()
    conn.close()
    return True

# qq号转名字
def qq2name(memberList,qq):
    for i in memberList:
        if i.id==qq:
            return i.memberName
    return "qq2Name::Error"

# 秒数转时间str
def sec2Str(seconds):
    if seconds<60:
        return str(int(seconds))+"秒"
    elif seconds<3600:
        return str(int(seconds/60))+"分"+str(int(seconds%60))+"秒"
    elif seconds<86400:
        return str(int(seconds/3600))+"时"+str(int(seconds%3600/60))+"分"+str(int(seconds%60))+"秒"
    else:
        return str(int(seconds/86400))+"天"+str(int(seconds%86400/3600))+"时"+str(int(seconds%3600/60))+"分"+str(int(seconds%60))+"秒"

# 将得到的MD5值所有字符转换成大写
def curlmd5(src):
    m = hashlib.md5(src.encode('UTF-8'))
    return m.hexdigest().upper()

def getParams(groupId,sender,plus_item):
    # 请求时间戳（秒级），用于防止请求重放（保证签名5分钟有效)
    t = time.time()
    time_stamp = str(int(t))
    # 请求随机字符串，用于保证签名不可预测  
    nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    # 应用标志，这里修改成自己的id和key
    app_id = ''
    app_key = ''
    params = {  'app_id' : app_id,
                'question' : plus_item,
                'time_stamp':time_stamp,
                'nonce_str':nonce_str,
                'session':getChatSession(groupId,sender)
             }

    sign_before = ''
    # 要对key排序再拼接  
    for key in sorted(params):
        # 键值拼接过程value部分需要URL编码，URL编码算法用大写字母，例如%E8。quote默认大写。  
        sign_before += '{}={}&'.format(key, quote(params[key], safe=''))
    # 将应用密钥以app_key为键名，拼接到字符串sign_before末尾
    sign_before += 'app_key={}'.format(app_key)
    # 对字符串sign_before进行MD5运算，得到接口请求签名  
    sign = curlmd5(sign_before)
    params['sign'] = sign
    return params

# 智能闲聊返回文字
def getChatText(groupId,sender,plus_item):
    # 聊天的API地址    
    url = "https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat"
    # 获取请求参数  
    plus_item = plus_item.encode('utf-8')
    payload = getParams(groupId,sender,plus_item)
    r = requests.get(url,params=payload)
    # r = requests.post(url,data=payload)
    # print(r.text)
    # print(r.json()["data"]["answer"])
    return r.json()["data"]["answer"]

# 获取智能闲聊session
def getChatSession(groupId,sender):
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "select `session` from chatSession where groupId=%d and memberId=%d"%(groupId,sender)
    cur.execute(sql) 
    data = cur.fetchone()
    print(data)
    if not data==None:
        session=data[0]
        cur.close()
        conn.close()
        print("智能闲聊 sender:%s,session:%s"%(sender,session))
        return str(session)
    else:
        sql = "select MAX(`session`) from chatSession"
        cur.execute(sql) 
        data = cur.fetchone()[0]
        print(data)
        if data==None:
            session=1
        else:
            session=int(data)+1
        print("session:",session)
        sql="INSERT INTO chatSession (groupId,memberId,`session`) VALUES (%d,%d,%d)"%(groupId,sender,session)
        cur.execute(sql) 
        cur.close()
        conn.commit()
        conn.close()
        print("智能闲聊 sender:%s,session:%s"%(sender,session))
        return str(session)

# 翻译功能
def translate(groupId,sender,text,source,target):
    url="https://api.ai.qq.com/fcgi-bin/nlp/nlp_texttranslate"
    # 请求时间戳（秒级），用于防止请求重放（保证签名5分钟有效)
    t = time.time()
    time_stamp = str(int(t))
    # 请求随机字符串，用于保证签名不可预测  
    nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    # 应用标志，这里修改成自己的id和key
    app_id = ''
    app_key = ''
    params = {  'app_id' : app_id,
                'text' : text,
                'time_stamp':time_stamp,
                'nonce_str':nonce_str,
                'source':source,
                'target':target
             }
 
    sign_before = ''
    for key in sorted(params):
        sign_before += '{}={}&'.format(key, quote(params[key], safe=''))
    sign_before += 'app_key={}'.format(app_key)
    sign = curlmd5(sign_before)
    params['sign'] = sign
    r = requests.get(url,params=params)
    # print(r.text)
    record("translate %s->%s"%(source,target),"none",sender,groupId,True,"function")
    return [
        At(target=sender),
        Plain("translate:\n"),
        Plain(text="%s"%r.json()["data"]["target_text"])
    ]

# 检测语言
def textDetect(text):
    url="https://api.ai.qq.com/fcgi-bin/nlp/nlp_textdetect"
    # 请求时间戳（秒级），用于防止请求重放（保证签名5分钟有效)
    t = time.time()
    time_stamp = str(int(t))
    # 请求随机字符串，用于保证签名不可预测  
    nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    # 应用标志，这里修改成自己的id和key
    app_id = ''
    app_key = ''
    params = {  'app_id' : app_id,
                'candidate_langs':'',
                'force':'1',
                'nonce_str':nonce_str,
                'text' : text,
                'time_stamp':time_stamp
             }
    sign=getSign(params)
    params['sign'] = sign
    r = requests.get(url,params=params)
    # print(r.text)
    return r.json()["data"]["lang"]

# 接口签名算法
def getSign(params):
    APP_KEY = ''
    app_key = ''
    paramsKeys=sorted(params.keys())
    print(paramsKeys)
    # print(params)
    sign=""
    for i in paramsKeys:
        if not params[i]=='':
            sign+="%s=%s&"%(i,parse.quote(params[i], safe=''))
    sign+="app_key=%s"%app_key
    print("sign:",sign)
    sign=curlmd5(sign)
    print("signMD5:",sign)
    return sign

#图片鉴黄
def judgeImageYellow(groupId,sender,image_url):
    setYellowPredictReady(groupId,sender,False)
    # yellowPredictCount=getData("yellowPredictCount")+1
    # print(yellowPredictCount)
    # updateData(yellowPredictCount,"yellow")
    # dist="%s%s.png"%(searchDist,searchCount)
    url="https://api.ai.qq.com/fcgi-bin/vision/vision_porn"
    # 请求时间戳（秒级），用于防止请求重放（保证签名5分钟有效)
    t = time.time()
    time_stamp = str(int(t))
    # 请求随机字符串，用于保证签名不可预测  
    nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    # 应用标志，这里修改成自己的id和key
    app_id = ''
    app_key = ''
    params = {  'app_id' : app_id,
                'time_stamp':time_stamp,
                'nonce_str':nonce_str,
                'image_url':str(image_url)
             }
    params['sign'] = getSign(params)
    print(params)
    r = requests.post(url,params=params)
    print(r.text)
    if r.json()["ret"]>0:
        return [
        At(target=sender),
        Plain("Error!:\nReason:"),
        Plain(text="%s"%r.json()["msg"])
        ]
    elif r.json()["ret"]==0:
        return [
        At(target=sender),
        Plain("Possiblity Result:\n"),
        Plain("Normal :%"),
        Plain(text="%d"%r.json()["data"]["tag_list"][0]["tag_confidence"]),
        Plain("Hot :%"),
        Plain(text="%d"%r.json()["data"]["tag_list"][1]["tag_confidence"]),
        Plain("Sexy :%"),
        Plain(text="%d"%r.json()["data"]["tag_list"][2]["tag_confidence"]),
        Plain("Total :%"),
        Plain(text="%d"%r.json()["data"]["tag_list"][9]["tag_confidence"])
        ]


# 返回Linux命令介绍
def getLinuxExplanation(command):
    if command in linuxDict:
        return linuxDict[command]["d"]
    else:
        return "error!no command!"
    
# 按照概率随机返回
def randomJudge():
    seed = int(time.time())
    random.seed(seed)
    random.random()
    p=random.randint(0,100)
    print(p)
    if p<=30:
        return True
    return False

# 添加管理员
def addAdmin(groupId,adminId):
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "select adminId from admin where groupId=%d"%groupId
    cur.execute(sql) 
    data = cur.fetchall()
    admin=list(chain.from_iterable(data))
    if admin==[]:
        sql = "insert into adminId (groupId,admionId) values (%d,%d))"%(groupId,adminId)
        cur.execute(sql) 
        conn.commit()
    else:
        return [Plain(text="id:%d is already in group:%d's admin list!")]
    cur.close()
    conn.close()
    return [Plain(text="id:%d add into group:%d's admin list!")]

# 返回笑话
def getJoke(name):
    conn = pymysql.connect(host='127.0.0.1', user = "root", passwd="", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "select * from jokes order by rand() limit 1"
    cur.execute(sql) 
    joke = cur.fetchone()
    if joke==(None,):
        cur.close()
        conn.close()
        return [Plain(text="笑话数据库为空！")]
    else:
        cur.close()
        conn.close()
        joke=joke[0]
        joke=joke.replace("%name%",name)
        joke=joke.replace("\n","")
        return [Plain(text=joke)]
