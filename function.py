#coding=utf-8
from mirai import Mirai, Plain, MessageChain, Friend, Image, Group, protocol, Member, At, Face, JsonMessage
import os, random, shutil
from os.path import join, getsize
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
import base64
import io
from variable import *
import imagehash

# 从config中获取配置
def getConfig(config):
    with open('config.json', 'r', encoding='utf-8') as f:  # 从json读配置
        configs = json.loads(f.read())
    if config in configs.keys():
        return configs[config]
    else:
        print("getConfig Error:%s"%config)

BotQQ = getConfig("BotQQ") # 字段 qq 的值
HostQQ = getConfig("HostQQ") #主人QQ
dbPass = getConfig("dbPass")
host = getConfig("dbHost")
user = getConfig("dbUser")
db = getConfig("dbName")
settingCode={"Disable":0,"Enable":1,"on":1,"off":0,"Local":1,"Net":0,"normal":"normal","zuanLow":"zuanLow","zuanHigh":"zuanHigh","rainbow":"rainbow","chat":"chat","online":"online","offline":"offline"}

# 初始化city列表
city=[]
conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
cur = conn.cursor()
sql = "select cityZh from city"
cur.execute(sql) 
data = cur.fetchall()
city=list(chain.from_iterable(data))
cur.close()
conn.close()

# 数据更新
def updateData(data,operationType):
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
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
    elif operationType=='quotes':
        sql = "UPDATE calledCount SET quotesCount=%d"%data
    else:
        print("error: none operationType named %s!"%operationType)
        return
    cur.execute(sql) 
    cur.close()
    conn.commit()
    conn.close()

# 日志记录
def record(operation,picUrl,sender,groupId,result,operationType):
    timeNow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(timeNow)
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
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

# 添加群信息（数据库）
def addGroupinit(groupId,groupName):
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
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
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
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
            (groupId,groupName,`repeat`,setuLocal,bizhiLocal,countLimit,`limit`,setu,bizhi,`real`,r18,search,imgPredict,yellowPredict,imgLightning,speakMode,switch,forbiddenCount) 
            VALUES 
            (%d,'%s',%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,'%s','%s',0)
            """%(i.id,i.name,True,True,True,True,6,True,True,True,True,False,True,True,True,"normal","online")
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
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
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
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
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
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
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
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "SELECT adminId from admin WHERE groupId=%d"%groupId
    cur.execute(sql) 
    data=cur.fetchall()
    admin=list(chain.from_iterable(data))
    cur.close()
    conn.close()
    return admin

# 是否要对图片做响应
def getReady(groupId,sender,targetDB):
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "SELECT `status` from %s WHERE groupId=%d and memberId=%d"%(targetDB,groupId,sender)
    cur.execute(sql) 
    try:
        result=cur.fetchone()[0]
    except TypeError:
        sql="INSERT INTO %s (groupId,memberId,`status`) VALUES (%d,%d,%d)"%(targetDB,groupId,sender,False)
        cur.execute(sql) 
        conn.commit()
        return False
    cur.close()
    conn.close()
    return result

# 修改判断状态
def setReady(groupId,sender,status,targetDB):
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "SELECT `status` from %s WHERE groupId=%d and memberId=%d"%(targetDB,groupId,sender)
    cur.execute(sql) 
    try:
        result=cur.fetchone()[0]
        sql="UPDATE %s SET `status`=%d WHERE groupId=%d and memberId=%d"%(targetDB,status,groupId,sender)
        cur.execute(sql) 
    except TypeError:
        sql="INSERT INTO %s (groupId,memberId,Status) VALUES (%d,%d,%d)"%(targetDB,groupId,sender,status)
        cur.execute(sql) 
    cur.close()
    conn.commit()
    conn.close()

# 随机图片路径
def randomPic(dir):
    pathDir = os.listdir(dir)
    # seed = int(time.time())
    # random.seed(seed)
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
    setReady(groupId,sender,False,"searchReady")
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
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
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
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
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
    if (config=="limit" or config=="tributeQuantity") and change.isnumeric():
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
    elif config=="tribute" and change==True or change==False:
        return True
    elif config=="listen" and change==True or change==False:
        return True
    elif (config=="setu" or config=="real" or config=="bizhi" or config=="r18" or config=="search" or config=="imgPredict" or config=="imgLightning") and change==True or change==False:
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
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
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
    if qq==0:
        return "public"
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
    app_id=getConfig("app_id")
    app_key =getConfig("app_key")
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
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
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
    app_id=getConfig("app_id")
    app_key =getConfig("app_key")
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
    app_id=getConfig("app_id")
    app_key =getConfig("app_key")
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
    APP_KEY = getConfig("app_key")
    app_key = getConfig("app_key")
    paramsKeys=sorted(params.keys())
    # print(paramsKeys)
    # print(params)
    sign=""
    for i in paramsKeys:
        if not params[i]=='':
            sign+="%s=%s&"%(i,parse.quote(params[i], safe=''))
    sign+="app_key=%s"%app_key
    # print("sign:",sign)
    sign=curlmd5(sign)
    print("signMD5:",sign)
    return sign

# 获取图片大小
def get_size(file):
    # 获取文件大小:KB
    size = os.path.getsize(file)
    return size / 1024

# 拼接输出文件地址
def get_outfile(infile, outfile):
    if outfile:
        return outfile
    dir, suffix = os.path.splitext(infile)
    outfile = '{}-out{}'.format(dir, suffix)
    return outfile

# 图片压缩
def compress_image(infile, outfile='', mb=900, step=10, quality=80):
    """不改变图片尺寸压缩到指定大小
    :param infile: 压缩源文件
    :param outfile: 压缩文件保存地址
    :param mb: 压缩目标，KB
    :param step: 每次调整的压缩比率
    :param quality: 初始压缩比率
    :return: 压缩文件地址，压缩文件大小
    """
    o_size = get_size(infile)
    if o_size <= mb:
        return infile
    outfile = get_outfile(infile, outfile)
    while o_size > mb:
        im = Image.open(infile)
        im.save(outfile, quality=quality)
        if quality - step < 0:
            break
        quality -= step
        o_size = get_size(outfile)
    return outfile

def base_64(pic_path):
    size = os.path.getsize(pic_path) / 1024
    if size > 900:
        print('>>>>压缩<<<<')
        with IMG.open(pic_path) as img:
            w, h = img.size
            newWidth = 500
            newHeight = round(newWidth / w * h)
            img = img.resize((newWidth, newHeight), IMG.ANTIALIAS)
            img_buffer = io.BytesIO()  # 生成buffer
            img.save(img_buffer, format='PNG', quality=70)
            byte_data = img_buffer.getvalue()
            base64_data = base64.b64encode(byte_data)
            code = base64_data.decode()
            return code
    with open(pic_path, 'rb') as f:
        coding = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
        return coding.decode()

# 图片鉴黄
def judgeImageYellow(groupId,sender,img_url,saveDir):
    setReady(groupId,sender,False,"yellowPredictReady")
    yellowPredictCount=getData("searchCount")+1
    # print(yellowPredictCount)
    updateData(yellowPredictCount,"search")
    dist="%s%s.png"%(saveDir,yellowPredictCount)
    img_content=requests.get(img_url).content
    image=IMG.open(BytesIO(img_content))
    image.save(dist)
    imgBase64=base_64(dist)
    url="https://api.ai.qq.com/fcgi-bin/vision/vision_porn"
    # 请求时间戳（秒级），用于防止请求重放（保证签名5分钟有效)
    t = time.time()
    time_stamp = str(int(t))
    # 请求随机字符串，用于保证签名不可预测  
    nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    # 应用标志，这里修改成自己的id和key
    app_id=getConfig("app_id")
    app_key =getConfig("app_key")
    params = {  'app_id' : app_id,
                'time_stamp':time_stamp,
                'nonce_str':nonce_str,
                'image':imgBase64
             }
    params['sign'] = getSign(params)
    # params['image']=parse.quote(params['image'], safe='')
    # print(params)
    r = requests.post(url,data=params)
    # print(r.text)
    print(r.text)
    if r.json()["ret"]>0:
        record("yellowJudge",dist,sender,groupId,0,"img")
        return [
        At(target=sender),
        Plain("Error!:\nReason:"),
        Plain(text="%s"%r.json()["msg"])
        ]
    elif r.json()["ret"]==0:
        record("yellowJudge",dist,sender,groupId,1,"img")
        return [
            At(target=sender),
            Plain("\nPossiblity Result:\n"),
            Plain("Normal :%d%%\n"%r.json()["data"]["tag_list"][0]["tag_confidence"]),
            Plain("Hot :%d%%\n"%r.json()["data"]["tag_list"][1]["tag_confidence"]),
            Plain("Sexy :%d%%\n"%r.json()["data"]["tag_list"][2]["tag_confidence"]),
            Plain("Total :%d%%"%r.json()["data"]["tag_list"][9]["tag_confidence"])
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
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "select adminId from admin where groupId=%d and adminId=%d"%(groupId,adminId)
    cur.execute(sql) 
    admin = cur.fetchone()
    if admin==None:
        sql = "insert into admin (groupId,adminId) values (%d,%d)"%(groupId,adminId)
        cur.execute(sql) 
        conn.commit()
    else:
        return [Plain(text="id:%d is already in group:%d's admin list!"%(adminId,groupId))]
    cur.close()
    conn.close()
    return [Plain(text="id:%d add into group:%d's admin list!"%(adminId,groupId))]

# 删除管理员
def deleteAdmin(groupId,adminId):
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "delete from admin where groupId=%d and adminId=%d"%(groupId,adminId)
    cur.execute(sql) 
    admin = cur.fetchone()
    cur.close()
    conn.close()
    return [Plain(text="id:%d deleted from group:%d's admin list!"%(adminId,groupId))]

# 获取黑名单
def getBlacklist():
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "select * from blacklist"
    cur.execute(sql) 
    data = cur.fetchall()
    blacklist=list(chain.from_iterable(data))
    return blacklist

# 加入黑名单
def addToBlacklist(memberId):
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "INSERT INTO blacklist (id) values (%d)"%memberId
    cur.execute(sql) 
    conn.commit()
    cur.close()
    conn.close()
    return [Plain(text="id:%d add into blacklist"%memberId)]

# 移除黑名单
def removeFromBlacklist(memberId):
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "delete from blacklist where id=%d"%memberId
    cur.execute(sql) 
    cur.close()
    conn.close()
    return [Plain(text="id:%d removed from blacklist!"%memberId)]

# 返回笑话
def getJoke(name):
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
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

# 返回特殊关键词笑话
def getKeyJoke(key):
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "select * from %sJokes order by rand() limit 1"%key
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
        print(joke)
        return [Plain(text=joke)]

# 返回群语录
def getCelebrityQuotes(groupId,memberList,nickname,Type):
    if Type=="random":
        conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
        cur = conn.cursor()
        sql = "select * from celebrityQuotes where groupId=%d order by rand() limit 1"%groupId
        cur.execute(sql) 
        quotes = cur.fetchone()
        # print(quotes)
        if quotes==None:
            cur.close()
            conn.close()
            return [Plain(text="本群还没有群语录哟~快来添加吧~")]
        else:
            memberId=quotes[1]      # 说出名言的人
            content=quotes[2]       # 内容，可能为地址/文本
            quoteFormat=quotes[3]   # 语录形式 img/text
            cur.close()
            conn.close()
            if quoteFormat=="text":
                return [
                    Plain(text=content),
                    Plain(text="\n————%s"%qq2name(memberList,memberId))
                ]
            elif quoteFormat=="img":
                return [
                    # At(target=memberId),
                    Image.fromFileSystem(content)
                    # Plain(text="\n————%s"%qq2name(memberList,memberId))
                ]
            else:
                return [Plain(text="quoteFormat error!(%s)"%quoteFormat)]
    else:
        conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
        cur = conn.cursor()
        sql = "select memberId from nickname where groupId=%d and nickname='%s'"%(groupId,nickname[0])
        cur.execute(sql)
        memberId = cur.fetchone()
        # print(quotes)
        if memberId==None:
            cur.close()
            conn.close()
            return [Plain(text="%s是谁我不知道呐~快来添加别名吧~"%nickname[0])]
        else:
            sql = "select * from celebrityQuotes where groupId=%d and memberId=%d order by rand() limit 1"%(groupId,memberId[0])
            cur.execute(sql) 
            quotes = cur.fetchone()
            cur.close()
            conn.close()
            if quotes==None:
                cur.close()
                conn.close()
                return [Plain(text="%s还没有语录哦~快来添加吧~"%nickname[0])]
            content=quotes[2]       # 内容，可能为地址/文本
            quoteFormat=quotes[3]   # 语录形式 img/text
            if quoteFormat=="text":
                return [
                    Plain(text=content),
                    Plain(text="\n————%s"%nickname[0])
                ]
            elif quoteFormat=="img":
                return [
                    # At(target=memberId),
                    Image.fromFileSystem(content)
                    # Plain(text="\n————%s"%qq2name(memberList,memberId))
                ]
            else:
                return [Plain(text="quoteFormat error!(%s)"%quoteFormat)]


# 添加群语录
def addCelebrityQuotes(groupId,memberId,content,quoteFormat):
    # print(groupId,memberId,content,quoteFormat)
    try:
        conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
        cur = conn.cursor()
        sql = "insert into celebrityQuotes (groupId, memberId, content, `format`)values(%d,%d,'%s','%s')"%(groupId,memberId,content,quoteFormat)
        cur.execute(sql) 
        cur.close()
        conn.commit()
        conn.close()
        return [Plain(text="语录添加成功！")]
    except Exception as e:
        return [Plain(text="%s"%e)]

# 添加别名
def addNickname(groupId,memberId,nickname):
    try:
        conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
        cur = conn.cursor()
        sql = """INSERT INTO nickname (groupId, memberId, nickname) SELECT
                    %d, %d, '%s'
                FROM
                    DUAL
                WHERE
                    NOT EXISTS (
                        SELECT
                            groupId, memberId, nickname
                        FROM
                            nickname
                        WHERE
                        groupId = %d
                        AND nickname = '%s')"""%(groupId,memberId,nickname,groupId,nickname)
        cur.execute(sql) 
        cur.close()
        conn.commit()
        conn.close()
        return [Plain(text="别名添加成功！")]
    except Exception as e:
        return [Plain(text="%s"%e)]

# 疫情查询
def getEpidemic():
    virusSrc="https://api.yonyoucloud.com/apis/dst/ncov/country"
    # virusSrc="https://c.m.163.com/ug/api/wuhan/app/data/list-total"
    headers={"authoration":"apicode","apicode":getConfig("epidemicApicode")}
    response=requests.get(virusSrc,headers=headers)
    try:
        dataJson=response.json()
    except TypeError:
        return "Song not found!"
    # print(dataJson)
    confirmedCount=dataJson["data"]["confirmedCount"]
    confirmedAdd=dataJson["data"]["confirmedAdd"]
    suspectedCount=dataJson["data"]["suspectedCount"]
    suspectedAdd=dataJson["data"]["suspectedAdd"]
    curedCount=dataJson["data"]["curedCount"]
    curedAdd=dataJson["data"]["curedAdd"]
    deadCount=dataJson["data"]["deadCount"]
    deathAdd=dataJson["data"]["deathAdd"]
    updateTime=dataJson["data"]["updateTime"]
    sourceDesc=dataJson["data"]["sourceDesc"]
    description=dataJson["data"]["description"]
    virus=re.findall(r'病毒: (.*?);',description,re.S)[0]
    sourceOfInfection=re.findall(r'传染源: (.*?);',description,re.S)[0]
    wayForSpreading=re.findall(r'传播途径: (.*?);',description,re.S)[0]
    susceptiblePopulation=re.findall(r'易感人群： (.*?);',description,re.S)[0]
    incubationPeriod=re.findall(r'潜伏期： (.*?);',description,re.S)[0]
    host=re.findall(r'宿主： (.*?)',description,re.S)[0]
    Json="""
    {
        "app":"com.tencent.miniapp",
        "desc":"",
        "view":"notification",
        "ver":"0.0.0.1",
        "prompt":"[疫情统计]",
        "appID":"",
        "sourceName":"",
        "actionData":"",
        "actionData_A":"",
        "sourceUrl":"",
        "meta":{
            "notification":{
                "appInfo":{
                    "appName":"全国疫情数据统计",
                    "appType":4,
                    "appid":1109659848,
                    "iconUrl":"http://gchat.qpic.cn/gchatpic_new/719328335/-2010394141-6383A777BEB79B70B31CE250142D740F/0"
                },
                "data":[
                    {
                        "title":"确诊",
                        "value":"%d"
                    },
                    {
                        "title":"新增确诊",
                        "value":"%d"
                    },
                    {
                        "title":"疑似",
                        "value":"%d"
                    },
                    {
                        "title":"新增疑似",
                        "value":"%d"
                    },
                    {
                        "title":"治愈",
                        "value":"%d"
                    },
                    {
                        "title":"新增治愈",
                        "value":"%d"
                    },
                    {
                        "title":"死亡",
                        "value":"%d"
                    },
                    {
                        "title":"新增死亡",
                        "value":"%d"
                    },
                    {
                        "title":"更新时间",
                        "value":"%s"
                    }],
                "title":"中国加油!",
                "emphasis_keyword":""
            }
        },
        "text":"",
        "sourceAd":""
    }"""%(confirmedCount,confirmedAdd,suspectedCount,suspectedAdd,curedCount,curedAdd,deadCount,deathAdd,updateTime)
    # print(Json)
    return Json

# 点歌
def songOrder(songName):
    songSearchSrc="http://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={%s}&type=1&offset=0&total=true&limit=1"%songName
    response=requests.get(songSearchSrc)
    dataJson=response.json()
    Id=dataJson["result"]["songs"][0]["id"]
    detailSrc="http://musicapi.leanapp.cn/song/detail?ids=%d"%Id
    response=requests.get(detailSrc)
    dataJson=response.json()
    name=dataJson["songs"][0]["name"]
    picUrl=dataJson["songs"][0]["al"]["picUrl"]
    name=dataJson["songs"][0]["name"]
    desc=dataJson["songs"][0]["ar"][0]["name"]
    Json="""
    {
        "config":{
            "autosize":true,
            "ctime":1595171310,
            "type":"normal",
            "forward":true,
            "token":"f55af0d5746b18b3d142bfd9a80f9de5"
        },
        "prompt":"[分享]%s",
        "app":"com.tencent.structmsg",
        "ver":"0.0.0.1",
        "view":"music",
        "meta":{
            "music":{
                "appid":100495085,
                "preview":"%s",
                "android_pkg_name":"",
                "musicUrl":"http:\/\/music.163.com\/song\/media\/outer\/url?id=%d",
                "sourceMsgId":"0",
                "desc":"%s",
                "title":"%s",
                "action":"",
                "source_url":"",
                "tag":"假装自己是网易云音乐的屑机器人",
                "jumpUrl":"http:\/\/music.163.com\/song\/%d",
                "app_type":1,
                "source_icon":""
            }
        },
        "desc":"音乐"
    }
    """%(name,picUrl,Id,desc,name,Id)
    return Json

# 查询上贡信息
def getTributeInfo(memberId,target):
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "SELECT %s from tributes WHERE memberId=%d"%(target,memberId)
    cur.execute(sql) 
    try:
        result=cur.fetchone()[0]
    except TypeError:
        sql="INSERT INTO tributes (memberId, tributeCount, VIP) VALUES (%d,%d,%d)"%(memberId,0,False)
        cur.execute(sql) 
        conn.commit()
        if target=="VIP":
            return False
        elif target=="tributeCount":
            return 0
        elif target=="startTime" or target=="endTime":
            return datetime.strptime('Apr-27-00 20:12:56','%b-%d-%y %H:%M:%S')
    cur.close()
    conn.close()
    return result
    
# 修改上贡信息
def setTributeInfo(sender,status,target):
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "SELECT * from tributes WHERE memberId=%d"%sender
    cur.execute(sql) 
    try:
        result=cur.fetchone()[0]
        if target=="tributeCount":
            sql="UPDATE tributes SET tributeCount=%d WHERE memberId=%d"%(status,sender)
        elif target=="VIP":
            sql="UPDATE tributes SET VIP=%d WHERE memberId=%d"%(status,sender)
        elif target=="startTime":
            sql="UPDATE tributes SET startTime='%s' WHERE memberId=%d"%(status,sender)
        elif target=="endTime":
            sql="UPDATE tributes SET endTime='%s' WHERE memberId=%d"%(status,sender)
        cur.execute(sql) 
    except TypeError:
        sql="INSERT INTO tributes (memberId, tributeCount, VIP) VALUES (%d,%d,%d)"%(sender,0,0)
        cur.execute(sql) 
    cur.close()
    conn.commit()
    conn.close()

# 图片哈希
def imgHash(img_path):
  """
  图片哈希（类似：4f999cc90979704c）
  :param img_path: 图片路径
  :return: <class 'imagehash.ImageHash'>
  """
  img1 = IMG.open(img_path)
  res = imagehash.dhash(img1)
  print(res)
  return res

# 计算图片汉明距离
def imgHamm(res1, res2):
    """
    汉明距离，汉明距离越小说明越相似，等 0 说明是同一张图片，大于10越上，说明完全不相似
    :param res1:
    :param res2:
    :return:
    """
    str1 = str(res1)  # <class 'imagehash.ImageHash'> 转成 str
    str2 = str(res2)
    num = 0  # 用来计算汉明距离
    for i in range(len(str1)):
        if str1[i] != str2[i]:
            num += 1
    return num

# 图片相似度判断
def imgSimilarJudge(tImgHash,path,value):
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    sql="select imageHash from imageHash where class='%s'"%path
    cur.execute(sql) 
    data = cur.fetchall()
    Hash=list(chain.from_iterable(data))
    for i in Hash:
        if imgHamm(i,tImgHash)<=value:
            return (True,imgHamm(i,tImgHash))
    return (False,"none")

# 将新图片哈希值存入数据库
def insertHash(path,imageHash,pathClass):
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    try:
        sql = "insert into ImageHash (dir,imageHash,class) values ('%s','%s','%s')"%(pymysql.escape_string(path),imageHash,pathClass)
        cur.execute(sql) 
        conn.commit()
    except Exception:
        pass
    conn.close()
    cur.close()

# 查询b站直播间
def getBilibiliRoomInfo(roomId):
    bilibiliSrc="https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom"
    roomLink="https://live.bilibili.com/%s"%roomId
    res = requests.get(bilibiliSrc, params={'room_id': roomId})
    data=res.json()
    if "data" in data.keys():
        live_status=data["data"]["room_info"]["live_status"]
        title=data["data"]["room_info"]["title"]
        anchor_info=data["data"]["anchor_info"]["base_info"]["uname"]
        area_name=data["data"]["room_info"]["area_name"]
        parent_area_name=data["data"]["room_info"]["parent_area_name"]
        # print(data)
        time.sleep(0.2)
        return (True,live_status,title,anchor_info,area_name,parent_area_name,roomLink)
    else:
        return (False,"none","none","none","none","none","none")

# 添加订阅
def addSubscribe(groupId,sender,roomId,platform):
    if platform=="bilibili":
        if getBilibiliRoomInfo(roomId)[0]:
            conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
            cur = conn.cursor()
            try:
                sql = "insert into subscribe (groupId, memberId, roomId, platform) values (%s,%s,%s,'%s')"%(groupId,sender,roomId,"bilibili")
                sql = """INSERT INTO subscribe (groupId, memberId, roomId, platform) SELECT
                    %s,%s,%s,'%s'
                FROM
                    DUAL
                WHERE
                    NOT EXISTS (
                        SELECT
                            roomId, platform
                        FROM
                            subscribe
                        WHERE
                            memberId = %s
                        AND  roomId = %s
                        AND  platform = '%s'
                        )"""%(groupId,sender,roomId,"bilibili",sender,roomId,"bilibili")
                cur.execute(sql) 
                conn.commit()
                sql = """INSERT INTO subscribeListen (roomId, platform) SELECT
                    %s, '%s'
                FROM
                    DUAL
                WHERE
                    NOT EXISTS (
                        SELECT
                            roomId, platform
                        FROM
                            subscribeListen
                        WHERE
                            roomId = %s
                        AND  platform = '%s')"""%(roomId,"bilibili",roomId,"bilibili")
                # sql = "insert into subscribeListen (roomId, platform) values (%s,'%s')"%(roomId,"bilibili")
                cur.execute(sql) 
                conn.commit()
            except Exception as e:
                return [
                    At(target=sender),
                    Plain(text="error!%s"%e)
                ]
            conn.close()
            cur.close()
            return [
                At(target=sender),
                Plain(text="\n直播间%s添加成功！"%roomId)
            ]
        else:
            return [
                At(target=sender),
                Plain(text="\n直播间号错误！请检查后重新发送！")
            ]

# 返回网抑云
def getWyy():
    response=requests.get(wyySrc)
    Json=response.json()
    return [Plain(text=Json[0]["text"])]

# 群平安
def safe(groupId,memberList):
    text="%s平安经\n"%getSetting(groupId,"groupName")
    for i in memberList:
        text+="%s 平安,\n"%qq2name(memberList,i.id)
    text=text[:-2]
    return [Plain(text=text)]

#找到龙王
def FindDragonKing(groupId,memberList):
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    sql="select * from dragon where groupId=%d order by count desc"%groupId
    cur.execute(sql) 
    lspRank = cur.fetchall()
    conn.close()
    cur.close()
    print(lspRank)
    msg=[]
    text="啊嘞嘞，从启动到现在都没有人要过涩图的嘛!呜呜呜~\n人家。。。人家好寂寞的，快来找我玩嘛~"
    if lspRank==():
        return [Plain(text=text)]
    else:
        timeNow = datetime.datetime.now().strftime("%Y-%m-%d")
        text="今天是%s\n"%timeNow
        text+="今日获得老色批龙王称号的是：\n"
        msg.append(Plain(text=text))
        lspChampionCount=lspRank[0][3]
        if lspChampionCount==0:
            text="啊嘞嘞，从启动到现在都没有人要过涩图的嘛!呜呜呜~\n人家。。。人家好寂寞的，快来找我玩嘛~"
            return [Plain(text=text)]
        for i in lspRank:
            if i[3]==lspChampionCount:
                msg.append(At(target=i[2]))
                msg.append(Plain(text="\n"))
            else:
                break
        text="让我们恭喜他！\n今日lsp排行榜："
        msg.append(Plain(text=text))
        text=""
        index=0
        addBool=False
        add=0
        last=-1
        for i in lspRank:
            if i[3]==0:
                break
            if i[3]==last:
                add+=1
                addBool=True
            else:
                if addBool:
                    index+=add
                index+=1
                add=0
                addBool=False
                last=i[3]
            text+="\n%i.%-20s %3d"%(index,qq2name(memberList,i[2]),i[3])
        msg.append(Plain(text=text))
        return msg

# 更新龙王数据
def updateDragon(groupId,memberId,obj):
    timeNow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    if obj=="all":
        sql="update dragon set count=0 where groupId=%d"%groupId
    else:
        sql = """INSERT INTO dragon (time, groupId, memberId) SELECT
                        '%s',%d,%d
                    FROM
                        DUAL
                    WHERE
                        NOT EXISTS (
                            SELECT
                                groupId, memberId
                            FROM
                                dragon
                            WHERE
                                groupId = %d
                            AND  memberId = %d
                            )"""%(timeNow,groupId,memberId,groupId,memberId)
        cur.execute(sql) 
        sql="update dragon set count=count+1 where groupId=%d and memberId=%d"%(groupId,memberId)
    cur.execute(sql) 
    conn.commit()
    conn.close()
    cur.close()

# 获得监听成员列表
def getListenId(groupIdList):
    listenId={}
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    for i in groupIdList:
        listenId[i]=[]
        sql="select memberId from listen where groupId=%d"%i
        cur.execute(sql) 
        data = cur.fetchall()
        if data==():
            pass
        else:
            for j in data:
                listenId[i].append(j[0])
    conn.close()
    cur.close()
    return listenId
    
# 微博热搜
def getWeiboHot():
    response=requests.get(weiboHotSrc)
    data=response.json()
    data=data["data"]
    text="微博实时热榜:"
    index=0
    for i in data:
        index+=1
        text+="\n%d.%s"%(index,i["word"])
    text=text.replace("#","")
    return [Plain(text=text)]