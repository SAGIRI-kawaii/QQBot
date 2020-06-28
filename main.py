from mirai import Mirai, Plain, MessageChain, Friend, Image, Group, protocol, Member, At, Face, JsonMessage
from mirai.face import QQFaces
import asyncio
import re
import requests
from PIL import Image as IMG
from io import BytesIO
import time
from urllib import parse
import datetime
import os, random, shutil
import wmi
from os.path import join, getsize
import json
from googletrans import Translator
import base64
# import Arnold


BotQQ =  # 字段 qq 的值
HostQQ =  #主人QQ
authKey = '1234567890' # 字段 authKey 的值
mirai_api_http_locate = 'localhost:8080/' # httpapi所在主机的地址端口,如果 setting.yml 文件里字段 "enableWebsocket" 的值为 "true" 则需要将 "/" 换成 "/ws", 否则将接收不到消息.

member_setu_dict={}         #每个群每个成员要的网络setu计数（限制每人五张）
member_setu_fobidden={}     #每个群被禁止要setu的成员id
member_setu_count={}        #每个群成员要setu的次数
group_repeat={}             #每个群判断是否复读的dict
group_repeat_switch={}      #每个群的复读开关
timeDisable={}              #关闭setu开关的时间
search_next={}              
pmlimit={}                  #10分钟限制setu次数

setting={"repeat":False,"setuLocal":True,"bizhiLocal":True,"countLimit":True}

localtime = time.localtime(time.time())
day_set=localtime.tm_mday

setu_count=0    #网络setu编号
count=0         #setu保存编号
bizhi_count=0   #网络壁纸编号
setu_info=0     #响应setu请求次数
bizhi_info=0    #响应壁纸请求次数
weather_info=0  #响应天气请求次数
real_info=0     #响应real请求次数
response_info=0 #响应请求次数
dragonid=[]     #龙王id（可能有多个）
dragon={}       #各群今日是否已宣布龙王
group_r18={}    #各群组r18开关
management={}   #拥有管理权限的用户id
searchCount=0   #搜图编号

n_time = datetime.datetime.now()    #目前时间
start_time = 0    #程序启动时间
d_time = datetime.datetime.strptime(str(datetime.datetime.now().date())+'23:00', '%Y-%m-%d%H:%M')   #龙王宣布时间

setu_forbidden=[753400372,757627813]    #禁止要setu的群
forbidden_count=0          #禁止要setu后要setu的次数


setu_src=""      #setu api地址
bizhi_src=""                              #壁纸api地址
zuanHigh_src=""              #祖安（High）api地址
zuanLow_src=""     #祖安（Low）api地址
rainbow_src=""                #彩虹屁api地址
search_src="https://saucenao.com/"                                          #搜图网址
translate_src="https://translate.google.cn/#view=home&op=translate&sl=auto&tl="    #翻译地址

weather_info_dist="S:\MiRai_QQRobot\info\weather.txt"   #天气调用数据存储路径
setu_info_dist="S:\MiRai_QQRobot\info\setu.txt"         #setu调用数据存储路径
bizhi_info_dist="S:\MiRai_QQRobot\info\\bizhi.txt"      #壁纸调用数据存储路径
forbidden_dist="S:\\MiRai_QQRobot\\img\\angry.jpg"      #生气图片绝对路径
setu_dist="M:\Pixiv\pxer_new\\"                         #setu存储路径
setu18_dist="M:\Pixiv\pxer18_new\\"                     #setu18+存储路径
bizhi_dist="M:\Pixiv\\bizhi\\"                          #壁纸存储路径
admin_info_dist="S:\MiRai_QQRobot\info\\admin.txt"      #管理员数据存储路径
response_info_dist="S:\MiRai_QQRobot\info\\response.txt"#日志存储路径
response_oldinfo_dist="S:\MiRai_QQRobot\info\\oldResponse.txt"#旧日志存储路径
responseCount_dist="S:\MiRai_QQRobot\info\\responseCount.txt" #响应数据存储路径
real_info_dist="S:\MiRai_QQRobot\info\\real.txt" #real调用数据存储路径
dragon_dist="S:\MiRai_QQRobot\info\dragon.txt"  #龙王数据记录
search_info_dist="S:\MiRai_QQRobot\info\searchCount.txt"  #搜索编号存储路径
setuBot_dist="M:\pixiv\\botImage\\"   #涩图机器人监听保存图片路径
search_dist="M:\pixiv\\search\\"    #涩图机器人搜图保存图片路径
real_dist="M:\Pixiv\\reality\\"     #真人setu存储路径
time_dist="M:\pixiv\\time\\"        #时间图片文件夹存储路径
clockPreview_dist="M:\pixiv\\time\preview\\"    #表盘预览图存储路径
clock_info_dist="S:\MiRai_QQRobot\info\\clockChoice.txt"    #表盘选择数据存储路径

reply_word=["啧啧啧","确实","giao","？？？","???","芜湖","是谁打断了复读？","是谁打断了复读?","老复读机了","就这","就这？","就这?"]     #复读关键词
non_reply=["setu","bizhi","","别老摸了，给爷冲！","real","几点了","几点啦","几点啦?","几点了?","冲？","今天我冲不冲？","搜图","search"]      #不复读关键词
setuCalled=["[Image::A3C91AFE-8834-1A67-DA08-899742AEA4E5]","[Image::A0FE77EE-1F89-BE0E-8E2D-62BCD1CAB312]","[Image::04923170-2ACB-5E94-ECCD-953F46E6CAB9]","[Image::3FFFE3B5-2E5F-7307-31A4-2C7FFD2F395F]","[Image::8A3450C7-0A98-4E81-FA24-4A0342198221]","setu","车车","开车","来点色图","来点儿车车"]
setuBot=[]
setuGroup=[]
repeatBot=[]
forbidden=[]

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
mode_now="normal"   #机器人说话模式（普通、祖安High、祖安Low、彩虹屁）
MemberList={}       #群成员
clockChoice={}      #表盘选择

app = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={BotQQ}")

#随机本地setu
def random_setu(dir):
    pathDir = os.listdir(dir)
    dist = random.sample(pathDir, 1)[0]
    return dir+dist

#重置禁止要setu后要setu的次数
def set_forbidden_count():
    forbidden_count=0

#营销号文字生成函数
def yingxiaohao(somebody,something,other_word):
    txt = '''    {somebody}{something}是怎么回事呢？{somebody}相信大家都很熟悉，但是{somebody}{something}是怎么回事呢，下面就让小编带大家一起了解吧。
    {somebody}{something}，其实就是{somebody}{other_word}，大家可能会很惊讶{somebody}怎么会{something}呢？但事实就是这样，小编也感到非常惊讶。
    这就是关于{somebody}{something}的事情了，大家有什么想法呢，欢迎在评论区告诉小编一起讨论哦！
    '''
    return txt.format(somebody=somebody, something=something, other_word=other_word)

#获取全部数据
def getStatus(groupid):
    text="""Current State:
    setu:{setu}
    r18:{r18}
    setuPosition:{setuPosition}
    bizhiPosition:{bizhiPosition}
    status:{online}
    setuStored:{setuCount}
    setuR18Stored:{setuR18Count}
    bizhiStored:{bizhiCount}
    realStored:{realCount}
    totalStored:{totalCount}
    setuCalls:{setuCalls}
    bizhiCalls:{bizhiCalls}
    weatherCalls:{weatherCalls}
    realCalls:{realCalls}
    totalEesponseTimes:{totalEesponseTimes}
    Console-Pure Version: 0.5.1"""
    if groupid not in setu_forbidden:
        setu="True"
    else:
        setu="False"
    if group_r18[groupid]:
        r18="True"
    else:
        r18="False"
    if setting["setuLocal"]:
        setuPosition="Local"
    else:
        setuPosition="Net"
    if setting["bizhiLocal"]:
        bizhiPosition="Local"
    else:
        bizhiPosition="Net"
    setuCount=len(os.listdir(os.path.dirname(setu_dist)))
    setuR18Count=len(os.listdir(os.path.dirname(setu18_dist)))
    bizhiCount=len(os.listdir(os.path.dirname(bizhi_dist)))
    realCount=len(os.listdir(os.path.dirname(real_dist)))
    totalCount=setuCount+setuR18Count+bizhiCount+realCount
    setuCalls=setu_info
    bizhiCalls=bizhi_info
    weatherCalls=weather_info
    realCalls=real_info
    totalEesponseTimes=response_info
    return text.format(setu=setu,r18=r18,setuPosition=setuPosition,bizhiPosition=bizhiPosition,online=status[groupid],setuCount=setuCount,setuR18Count=setuR18Count,bizhiCount=bizhiCount,realCount=realCount,totalCount=totalCount,setuCalls=setuCalls,bizhiCalls=bizhiCalls,weatherCalls=weatherCalls,realCalls=realCalls,totalEesponseTimes=totalEesponseTimes)

#找到龙王
def FindDragonKing(groupid):
    global dragonid
    group_dict=member_setu_count[groupid]
    group_dict=sorted(group_dict.items(),key=lambda item: item[1],reverse=True)
    id_name={}
    for i in member_setu_count[groupid].keys():
        id_name[i]="Null"
    # print(group_dict)
    for i in MemberList[groupid]:
        if i.id in id_name.keys():
            id_name[i.id]=i.memberName

    text="本次程序启动时间:%s\n"%start_time
    text+="啊嘞嘞，从启动到现在都没有人要过涩图的嘛!呜呜呜~\n人家。。。人家好寂寞的，快来找我玩嘛~"
    if member_setu_count[groupid]:
        dragonid=[]
        dragonCount=max(member_setu_count[groupid].values())
        for key,value in member_setu_count[groupid].items():
            if(value == max(member_setu_count[groupid].values())):
                dragonid.append(key)
        text="本次程序启动时间:%s\n"%start_time
        text+="今日获得老色批龙王称号的是：\n"
        for id in dragonid:
            if id in forbidden:
                text+="这个老色批被禁了竟然还能当上龙王？打他->"
            text+="id:"
            text+=str(id)
            text+="\n"
        text+="他们今日每人都要了%i张涩图(setu+real)！\n"%dragonCount
        text+="让我们恭喜他们！\n"
        text+="今日setu排行榜：\n"
        index=0
        addBool=False
        add=0
        last=-1
        print(group_dict)
        print(id_name)
        for i in group_dict:
            if i[1]==last:
                add+=1
                addBool=True
            else:
                if addBool:
                    index+=add
                index+=1
                add=0
                addBool=False
                last=i[1]
            text+="%i.%s  %i\n"%(index,id_name[i[0]],i[1])
        # text+="以上成员将自愿(被迫)向图库中贡献十张涩图哦~"
        # print(text)
    return text

#qq号转为昵称
def qq2name(memberList,qq):
    for i in memberList:
        if i.id==qq:
            return i.memberName
    return "qq2Name::Error"

#目前群内成员要setu次数统计
def showSetuCount(groupid):
    group_dict=member_setu_count[groupid]
    group_dict=sorted(group_dict.items(),key=lambda item: item[1],reverse=True)
    id_name={}
    for i in member_setu_count[groupid].keys():
        id_name[i]="Null"
    # print(group_dict)
    for i in MemberList[groupid]:
        if i.id in id_name.keys():
            id_name[i.id]=i.memberName
    text="本次程序启动时间:%s\n"%start_time
    text+="啊嘞嘞？到现在都没有人要setu的嘛。。。。\n"
    text+="是。。。是不要人家了嘛。。。呜呜呜\n"
    text+="明明。。明明我也有很努力的啊！！！\n"
    text+="都在干什么啊快来找我要setu啊kora！"
    if member_setu_count[groupid]:
        text="本次程序启动时间:%s\n"%start_time
        text+="今日setu排行榜：\n"
        index=0
        addBool=False
        add=0
        last=-1
        for i in group_dict:
            if i[1]==last:
                add+=1
                addBool=True
            else:
                if addBool:
                    index+=add
                index+=1
                add=0
                addBool=False
                last=i[1]
            text+="%i.%s  %i张\n"%(index,id_name[i[0]],i[1])
    return text

#查看管理员名单
def showAdmin(groupid):
    text="Adminastrator:\n"
    index=1
    for i in management[groupid]:
        text+="%i.%i\n"%(index,i)
        index+=1
    return text

def randomRush():
    return random.choice(["必须的！冲！冲他一发！","不行！这伤身体！不冲了！","必须的！冲！冲他一发！","必须的！冲！冲他一发！","不行！这伤身体！不冲了！","必须的！冲！冲他一发！","不行！这伤身体！不冲了！","不行！这伤身体！不冲了！","不行！这伤身体！不冲了！","必须的！冲！冲他一发！"])

def record(data):
    global response_info
    response_info+=1
    with open(responseCount_dist,"w") as w:
        w.write(str(response_info))
    lines=open(response_info_dist,'r').readlines()
    count=len(lines)
    n_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if count>=1000:
        with open(response_oldinfo_dist,"a+") as w:
            for i in lines:
                w.write(i)
        with open(response_info_dist,'w') as w:
            w.write("%s  %s\n"%(n_time,data))
    else:
        with open(response_info_dist,'a+') as w:
            w.write("%s  %s\n"%(n_time,data))
    print("data recorded!")

def getFileSize(dir):
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([getsize(join(root, name)) for name in files])
    return size

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
    # print(diskSize,setuSize,setu18Size,bizhiSize)
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
    # print(text)
    return text

def recordDragon():
    today=datetime.datetime.now().strftime("%Y-%m-%d")
    with open(dragon_dist,"w") as w:
        w.write("%s\n"%today)
        for group in member_setu_count.keys():
            for member in member_setu_count[group].keys():
                w.write("%s:%s:%s\n"%(group,member,member_setu_count[group][member]))
    record("record:dragon")
    
def recordClock():
    with open(clock_info_dist,"w") as w:
        for group in clockChoice.keys():
            for member in clockChoice[group].keys():
                w.write("%s:%s:%s\n"%(group,member,clockChoice[group][member]))
    record("record:clock")

# def encryption(dist):
    # base64_data="Encrypt Error!"
    # with open(dist,"rb") as f:#转为二进制格式
    #     base64_data = base64.b64encode(f.read())#使用base64进行加密
    #     print(base64_data)

#初始化
@app.subroutine
async def subroutine1(app: Mirai):
    print("subroutine1 started")
    global bizhi_info
    global setu_info
    global real_info
    global response_info
    global weather_info
    global count
    global start_time
    global timeDisable
    global searchCount
    start_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    groupList = await app.groupList()
    # print(groupList)
    for i in groupList:
        member_setu_count[i.id]={}
        member_dict={}
        member_fobidden={}
        memberList = await app.memberList(i.id)
        MemberList[i.id]=memberList
        for j in memberList:
            member_dict[j.id]=0
            member_fobidden[j.id]=False
        member_setu_dict[i.id]=member_dict
        member_setu_fobidden[i.id]=member_fobidden
        dragon[i.id]=False
        group_repeat[i.id]={"lastMsg":"","thisMsg":"","stopMsg":""}
        group_r18[i.id]=False
        management[i.id]=[]
        timeDisable[i.id]={"start":"23:59","end":"0:00"}
        status[i.id]="online"
        search_next[i.id]={}
        clockChoice[i.id]={}
        pmlimit[i.id]={}
        # print(group_repeat[i.id])
    # for i in groupList:
    #     await app.sendGroupMessage(i,[
    #         Plain(text="哦雷瓦Bot哒哟~爷上线了desu~")
    #     ])
        #读取信息并存储
    with open("M:\pixiv\setu\count.txt","r") as f:
        count=f.read()
        # print(count)
        count.split()
        count=int(count)
        count+=1

    with open("M:\\bizhi\count.txt","r") as f:
        bizhi_count=f.read()
        # print(count)
        bizhi_count.split()
        bizhi_count=int(bizhi_count)
        bizhi_count+=1
        
    with open(bizhi_info_dist,"r") as f:
        bizhi_info=f.read()
        # print(count)
        bizhi_info.split()
        bizhi_info=int(bizhi_info)
        print(bizhi_info)

    with open(weather_info_dist,"r") as f:
        weather_info=f.read()
        # print(count)
        weather_info.split()
        weather_info=int(weather_info)
        print(weather_info)

    with open(setu_info_dist,"r") as f:
        setu_info=f.read()
        setu_info=int(setu_info)
        print(setu_info)
        
    with open(real_info_dist,"r") as f:
        real_info=f.read()
        real_info=int(real_info)
        print(real_info)

    with open(responseCount_dist,"r") as f:
        response_info=f.read()
        response_info=int(response_info)
        print(response_info)
        
    with open(admin_info_dist,"r") as f:
        while 1:
            text = f.readline().strip()
            if not text:
                break
            print(text)
            groupid,adminid=text.split(":")
            print(groupid)
            print(adminid)
            # adminid.remove("\n")
            management[int(groupid)].append(int(adminid))
        for i in management.keys():
            management[i].append(HostQQ)
        print("admin",management)

    with open(dragon_dist,"r") as f:
        today=datetime.datetime.now().strftime("%Y-%m-%d")
        text = f.readline().strip()
        print(text,today)
        if not text==str(today):
            return
        while 1:
            text = f.readline().strip()
            if not text:
                break
            # print(text)
            groupid,memberid,count=text.split(":")
            # print(groupid)
            # print(memberid)
            # print(count)
            groupid=int(groupid)
            memberid=int(memberid)
            member_setu_count[groupid][memberid]=int(count)
            # print(member_setu_count)
    
    with open(clock_info_dist,"r") as f:
        while 1:
            text = f.readline().strip()
            if not text:
                break
            groupid,memberid,clock=text.split(":")
            groupid=int(groupid)
            memberid=int(memberid)
            clockChoice[groupid][memberid]=int(clock)
            print(clockChoice)

    with open(search_info_dist,"r") as f:
        searchCount=f.read()
        # print(count)
        searchCount.split()
        searchCount=int(searchCount)
        searchCount+=1

    record("@app.subroutine")




@app.receiver("FriendMessage")
async def event_gm(app: Mirai, friend: Friend, message:MessageChain):
    print("friend Message")
    if friend.id==HostQQ:
        with open("S:\MiRai_QQRobot\info\\botSetuCount.txt","r") as f:
            botSetuCount=int(f.read())+1
        dist="%s%s.png"%(setuBot_dist,botSetuCount)
        img = message.getFirstComponent(Image)
        img=requests.get(img.url).content
        image=IMG.open(BytesIO(img))
        image.save(dist)
        with open("S:\MiRai_QQRobot\info\\botSetuCount.txt","w") as w:
            w.write(str(botSetuCount))
        await app.sendFriendMessage(friend,[
            Plain(text="Image saved!")
        ])
        record("setuConvey:%s friend:%s"%(dist,friend.id))

@app.receiver("GroupMessage")
async def GMHandler(app: Mirai, group:Group, message:MessageChain, member:Member):
    global setu_src
    global setu_info
    global real_info
    global bizhi_info
    global weather_info
    global mode_now
    global status
    global group_repeat
    global member_setu_count
    global dragon
    global timeDisable
    global searchCount
    send=member.id
    groupid=member.group.id
    print(groupid,send,message.toString(),sep=" :: ")
    group_repeat[member.group.id]["lastMsg"]=group_repeat[member.group.id]["thisMsg"]
    group_repeat[member.group.id]["thisMsg"]=message.toString()
    # print(getStatus(member.group.id))
    n_time = datetime.datetime.now()
    print(n_time)
    print(d_time)

    if send in setuBot:         #setu监听保存
        try:
            img = message.getFirstComponent(Image)
            img=requests.get(img.url).content
            image=IMG.open(BytesIO(img))
            with open("S:\MiRai_QQRobot\info\\botSetuCount.txt","r") as f:
                botSetuCount=int(f.read())+1
            dist="%s%s.png"%(setuBot_dist,botSetuCount)
            image.save(dist)
            with open("S:\MiRai_QQRobot\info\\botSetuCount.txt","w") as w:
                w.write(str(botSetuCount))
            print("setu Saved from %s"%send)
            record("setu Saved from %s group:%s"%(send,groupid))
        except AttributeError:
            print("none img from %s"%send)

    if not group_repeat[member.group.id]["lastMsg"]==group_repeat[member.group.id]["thisMsg"]:
        group_repeat[member.group.id]["stopMsg"]=""
    if n_time<d_time:
        dragon[groupid]=False
    if status[groupid]=="offline":
        if send == HostQQ and message.toString()=="[At::target=%i] setting.online"%BotQQ:
            status[groupid]="online"
            await app.sendGroupMessage(group,[
                Plain(text="Bot.online")
            ])
            record("setting.online group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif n_time>d_time and not dragon[groupid] and groupid not in setu_forbidden:
        text=FindDragonKing(member.group.id)
        msg=MessageChain()
        for i in dragonid:
            msg.__add__(At(target=i))
            msg.__add__(Plain(text="\n"))
        msg.__add__(Plain(text=text))
        dragon[member.group.id]=True
        await app.sendGroupMessage(group,msg)
        record("dragon group:%s"%groupid)
        record("dragonAnnounced group:%s"%groupid)
    elif group_repeat[member.group.id]["lastMsg"]==group_repeat[member.group.id]["thisMsg"] and message.toString() not in non_reply and "[At::target=%i]"%BotQQ not in message.toString():
        if not group_repeat[member.group.id]["stopMsg"]==group_repeat[member.group.id]["thisMsg"]:
            msg=[]
            index=0
            for i in message:
                if index<1:
                    index+=1
                else:
                    msg.append(i)
            await app.sendGroupMessage(group,msg)
            group_repeat[member.group.id]["stopMsg"]=group_repeat[member.group.id]["thisMsg"]
            record("repeat group:%s member:%s text=%s"%(groupid,send,msg))
    elif message.toString()=="[At::target=%i] menu"%BotQQ:
        await app.sendGroupMessage(group,[
            Plain(text=menu)
        ])
        record("menu group:%s member:%s"%(groupid,send))

    elif message.toString()=="[At::target=%i] test"%BotQQ and send==HostQQ:     #测试函数用接口
        pass



    elif message.toString()=="[At::target=%i] command"%BotQQ:
        await app.sendGroupMessage(group,[
            Plain(text=command)
        ])
        record("command group:%s member:%s"%(groupid,send))
    elif message.toString()=="[At::target=%i] hostCommand"%BotQQ:
        await app.sendGroupMessage(group,[
            Plain(text=hostCommand)
        ])
        record("hostCommand group:%s member:%s"%(groupid,send))
    elif message.toString()=="[At::target=%i] mode"%BotQQ:
        await app.sendGroupMessage(group,[
            Plain(text=mode)
        ])
        record("mode group:%s member:%s"%(groupid,send))
    elif message.toString()=="[At::target=%i] 1"%BotQQ:
        await app.sendGroupMessage(group,[
            Plain(text="请按照格式输入：\n"),
            Plain(text="@机器人营销号、主体、事件、另一种说法\n"),
            Plain(text="如：@机器人营销号、桃子核、不能吞下去、核太大了，吞下去容易噎着")
        ])
        record("yingxiaohao_info group:%s member:%s"%(groupid,send))
    elif message.toString()=="[At::target=%i] 2"%BotQQ:
        await app.sendGroupMessage(group,[
            Plain(text="请按照格式输入：\n"),
            Plain(text="@机器人问你点儿事儿:question\n"),
            Plain(text="如：@机器人问你点儿事儿：1+1=？(：为中文字符)")
        ])
        record("ask_info group:%s member:%s"%(groupid,send))
    elif message.toString()=="[At::target=%i] 3"%BotQQ:
        await app.sendGroupMessage(group,[
            Plain(text="请按照格式输入：\n"),
            Plain(text="@机器人blhx：舰娘名字\n"),
            Plain(text="如：@机器人blhx：企业(：为中文字符且舰娘名字务必完整)"),
            Plain(text="或：@机器人blhx：试作型双联装457mm主炮MKAT0(：为中文字符且装备名字务必完整)")
        ])
        record("blhx_info group:%s member:%s"%(groupid,send))
    elif message.toString()=="[At::target=%i] 4"%BotQQ:
        await app.sendGroupMessage(group,[
            Plain(text="请按照格式输入：\n"),
            Plain(text="@机器人城市天气城市\n"),
            Plain(text="如：@机器人天气北京"),
        ])
        record("weather_info group:%s member:%s"%(groupid,send))     
    elif message.toString()=="[At::target=%i] 5"%BotQQ:
        await app.sendGroupMessage(group,[
            Plain(text="随机setu：\n"),
            Plain(text="直接输入setu即可\n"),
            Plain(text="如：setu"),
            Plain(text="注：是否为r18由管理设置")
        ])
        record("setu_info group:%s member:%s"%(groupid,send))    
    elif message.toString()=="[At::target=%i] 6"%BotQQ:
        await app.sendGroupMessage(group,[
            Plain(text="随机bizhi：\n"),
            Plain(text="直接输入bizhi即可\n"),
            Plain(text="如：bizhi"),
        ])
        record("bizhi_info group:%s member:%s"%(groupid,send))    
    elif message.toString()=="[At::target=%i] 7"%BotQQ:
        await app.sendGroupMessage(group,[
            Plain(text="请按照格式输入：\n"),
            Plain(text="@机器人search search 搜图\n"),
            Plain(text="然后发送照片\n"),
            Plain(text="如：@机器人search"),
            Plain(text="或：search"),
            Plain(text="或：搜图"),
            Plain(text="随后发送照片")
        ])
        record("search_info group:%s member:%s"%(groupid,send))    
    elif "[At::target=%i] 营销号"%BotQQ in message.toString():
        _,somebody,something,other_word=message.toString().split('、')
        # print(something,somebody,other_word)
        await app.sendGroupMessage(group,[
            Plain(text=yingxiaohao(somebody,something,other_word))
        ])
        record("yingxiaohao_method group:%s member:%s"%(groupid,send))
    elif "[At::target=%i] search"%BotQQ in message.toString() or "搜图" in message.toString() or "search" in message.toString():  
        search_next[groupid][send]=True;   
        await app.sendGroupMessage(group,[
            At(target=send),
            Plain(text="请发送要搜索的图片呐~")
        ])
        print("search_next[%i][%i]=%i"%(groupid,send,search_next[groupid][send]))
    elif message.hasComponent(Image):
        if send in search_next[groupid] and search_next[groupid][send] == True:
            await app.sendGroupMessage(group,[
                At(target=send),
                Plain(text="正在搜索请稍后呐~")
            ])
            search_next[groupid][send]=False
            with open("S:\MiRai_QQRobot\info\\searchCount.txt","r") as f:
                searchCount=int(f.read())+1
            dist="%s%s.png"%(search_dist,searchCount)
            img = message.getFirstComponent(Image)
            img_content=requests.get(img.url).content
            image=IMG.open(BytesIO(img_content))
            image.save(dist)
            # setuBot_dist
            with open("S:\MiRai_QQRobot\info\\searchCount.txt","w") as w:
                w.write(str(searchCount))    
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
                    await app.sendGroupMessage(group,[
                        Plain(text="8好意思~没有找到相似的图诶~")
                    ])
                else:
                    try:
                        creator=json_data['results'][0]['data']['creator'][0]
                    except Exception:
                        creator="Unknown!"
                    await app.sendGroupMessage(group,[
                        At(target=send),
                        Plain(text="这个结果相似度很低诶。。。。要不你康康？\n"),
                        Image.fromFileSystem(dist),
                        Plain(text="\n相似度:%s%%\n"%(similarity)),
                        Plain(text="原图地址:%s\n"%pixiv_url),
                        Plain(text="作者:%s\n"%creator),
                        Plain(text="如果不是你想找的图的话可能因为这张图是最近才画出来的哦，网站还未收录呢~过段日子再来吧~")
                    ])
            else:
                pixiv_id=json_data['results'][0]['data']['pixiv_id']
                user_name=json_data['results'][0]['data']['member_name']
                user_id=json_data['results'][0]['data']['member_id']
                await app.sendGroupMessage(group,[
                    At(target=send),
                    Image.fromFileSystem(dist),
                    Plain(text="\n相似度:%s%%\n"%(similarity)),
                    Plain(text="原图地址:%s\n"%pixiv_url),
                    Plain(text="作品id:%s\n"%pixiv_id),
                    Plain(text="作者名字:%s\n"%user_name),
                    Plain(text="作者id:%s\n"%user_id)
                ])
            record("search_img group:%s member:%s searchNumber:%s result:%s"%(groupid,send,searchCount,'pixiv_id' in json_data['results'][0]))


    elif "[At::target=%i] 问你点儿事儿："%BotQQ in message.toString():
        question=message.toString()[30:]
        question=parse.quote(question)
        await app.sendGroupMessage(group,[
            Plain(text="啧啧啧，都多大了，还不会百度嘛，不会的话谷歌也行啊\n"),
            Plain(text="什么？你说还不会？你可真是个小憨批呢\n"),
            Plain(text="没办法呢，就让聪明的我来帮帮你吧！\n"),
            Plain(text="https://baidu.sagiri-web.com/?%s"%question)
        ])
        record("ask_method group:%s member:%s"%(groupid,send))
    elif "[At::target=%i] blhx："%BotQQ in message.toString():
        name=message.toString()[28:]
        await app.sendGroupMessage(group,[
            Plain(text="以下是%s的wiki网址，可在其中查到%s的各种信息哦：\n"%(name,name)),
            Plain(text="https://wiki.biligame.com/blhx/%s"%parse.quote(name))
        ])
        record("blhx_method group:%s member:%s"%(groupid,send))
    elif "[At::target=%i] 天气"%BotQQ in message.toString():
        weather_info+=1
        with open("S:\MiRai_QQRobot\info\\weather.txt","w") as w:
            w.write(str(weather_info))
        point=message.toString()[25:]
        weather_src="https://www.tianqiapi.com/free/day?appid=51475357&appsecret=Y56ID6xP&city=%s"%(point)
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
        await app.sendGroupMessage(group,[
            Plain(text="%s今日天气\n"%point),
            Plain(text="天气情况：%s\n"%wea),
            Plain(text="实时温度：%s℃\n"%tem),
            Plain(text="最高温：%s℃\n"%tem_day),
            Plain(text="最低温：%s℃\n"%tem_night),
            Plain(text="风向：%s\n"%win),
            Plain(text="风力等级：%s\n"%win_speed),
            Plain(text="风速：%s\n"%win_meter),
            Plain(text="空气质量：%s"%air)
        ])
        record("weather_method group:%s member:%s"%(groupid,send))

    #setting
    elif message.toString()=="[At::target=%i] setting.setuEnable"%BotQQ:
        if send in management[groupid]:
            if groupid in setu_forbidden:
                set_forbidden_count()
                setu_forbidden.remove(groupid)
                await app.sendGroupMessage(group,[
                    Plain(text="群%s涩图开关已打开！"%groupid)
                ])
            else:
                await app.sendGroupMessage(group,[
                    Plain(text="涩图开关已经是打开状态啦！")
                ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
            ])
        record("setting.setuEnable group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()=="[At::target=%i] setting.setuDisable"%BotQQ:
        if send in management[groupid]:
            if groupid in setu_forbidden:
                await app.sendGroupMessage(group,[
                    Plain(text="涩图开关已经是关闭状态啦！")
                ])
            else:
                setu_forbidden.append(groupid)
                await app.sendGroupMessage(group,[
                    Plain(text="群%s涩图开关已关闭！"%groupid)
                ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
            ])
        record("setting.setuDisable group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()=="[At::target=%i] setting.r18Disable"%BotQQ:
        if send in management[groupid]:
            if not group_r18[groupid]:
                await app.sendGroupMessage(group,[
                    Plain(text="r18开关已经是关闭状态啦！")
                ])
            else:
                group_r18[groupid]=False
                setu_src=setu_src[:-6]
                await app.sendGroupMessage(group,[
                    Plain(text="群%sr18开关已关闭！"%groupid)
                ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
            ])
        record("setting.r18Disable group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()=="[At::target=%i] setting.r18Enable"%BotQQ:
        if send in management[groupid]:
            if group_r18[groupid]:
                await app.sendGroupMessage(group,[
                    Plain(text="r18开关已经是打开状态啦！")
                ])
            else:
                group_r18[groupid]=True
                setu_src+="&r18=1"
                await app.sendGroupMessage(group,[
                    Plain(text="群%sr18开关已打开！"%groupid)
                ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
            ])
        record("setting.r18Enable group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()[0:47]=="[At::target=%i] setting.memberSetuEnable"%BotQQ:
        print(message.toString()[47:])
        print(re.findall(r'At::target=(.*?)]',message.toString()[47:],re.S))
        target=int(re.findall(r'At::target=(.*?)]',message.toString()[47:],re.S)[0])
        if send in management[groupid]:
            if not member_setu_fobidden[groupid][target]:
                await app.sendGroupMessage(group,[
                    Plain(text="成员%s一直可以要setu哦！"%target)
                ])
            else:
                member_setu_fobidden[groupid][target]=False
                await app.sendGroupMessage(group,[
                    Plain(text="成员%s从现在开始可以要setu啦！"%target)
                ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
            ])
        record("setting.memberSetuEnable group:%s member:%s target:%s callResult:%s"%(groupid,send,target,send in management))
    elif message.toString()[0:48]=="[At::target=%i] setting.memberSetuDisable"%BotQQ:
        print(message.toString()[48:])
        print(re.findall(r'target=(.*?)]',message.toString()[48:],re.S))
        target=int(re.findall(r'target=(.*?)]',message.toString()[48:],re.S)[0])
        if send in management[groupid]:
            if member_setu_fobidden[groupid][target]:
                await app.sendGroupMessage(group,[
                    Plain(text="成员%s一直不可以要setu哦！"%target)
                ])
            else:
                member_setu_fobidden[groupid][target]=True
                await app.sendGroupMessage(group,[
                    Plain(text="成员%s从现在开始不可以要setu啦！"%target)
                ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
            ])
        record("setting.memberSetuDisable group:%s member:%s target:%s callResult:%s"%(groupid,send,target,send in management))
    elif message.toString()=="[At::target=%i] setting.setMode.normal"%BotQQ:
        global mode_now
        if send in management[groupid]:
            mode_now="normal"
            await app.sendGroupMessage(group,[
                Plain(text="Mode:set to normal")
            ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
            ])
        record("setting.setMode.normal group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()=="[At::target=%i] setting.setMode.zuanHigh"%BotQQ:
        if send in management[groupid]:
            mode_now="zuanHigh"
            await app.sendGroupMessage(group,[
                Plain(text="Mode:set to zuanHigh\n"),
                Plain(text="各单位请注意无事不要@机器人\n"),
                Plain(text="以免误伤~")
            ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
            ])
        record("setting.setMode.zuanHigh group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()=="[At::target=%i] setting.setMode.zuanLow"%BotQQ:
        if send in management[groupid]:
            mode_now="zuanLow"
            await app.sendGroupMessage(group,[
                Plain(text="Mode:set to zuanLow\n"),
                Plain(text="各单位请注意无事不要@机器人\n"),
                Plain(text="以免误伤~")
            ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
            ])
        record("setting.setMode.zuanLow group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()=="[At::target=%i] setting.setMode.rainbow"%BotQQ:
        if send in management[groupid]:
            mode_now="rainbow"
            await app.sendGroupMessage(group,[
                Plain(text="Mode:set to rainbow")
            ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
            ])
        record("setting.setMode.rainbow group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()[0:42]=="[At::target=%i] setting.timeAllDay"%BotQQ:
        if send in management[groupid]:
            timeDisable[groupid]["start"]="23:59"
            timeDisable[groupid]["end"]="00:00"
            await app.sendGroupMessage(group,[
                Plain(text="setu功能将全天打开")
            ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
            ])
        record("setting.timeAllDay  group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()[0:43]=="[At::target=%i] setting.timeDisable "%BotQQ:
        start,end=message.toString()[43:].split(" to ")
        if send in management[groupid]:
            timeDisable[groupid]["start"]=start
            timeDisable[groupid]["end"]=end
            await app.sendGroupMessage(group,[
                Plain(text="setu功能在%s-%s将为关闭状态"%(timeDisable[groupid]["start"],timeDisable[groupid]["end"]))
            ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
            ])
        record("setting.timeDisable set to:%s-%s group:%s member:%s callResult:%s"%(timeDisable[groupid]["start"],timeDisable[groupid]["end"],groupid,send,send in management))
    elif message.toString()=="[At::target=%i] setting.setSetuLocal"%BotQQ:
        if send == HostQQ:
            if setting["setuLocal"]:
                await app.sendGroupMessage(group,[
                    Plain(text="setuLocal开关已经是Local状态啦！")
                ])
            else:
                setting["setuLocal"]=True
                await app.sendGroupMessage(group,[
                    Plain(text="setuLocal开关已切换到Local！")
                ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你不是我的主人！离人家远一点啦！死变态！")
            ])
        record("setting.setSetuLocal group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()=="[At::target=%i] setting.setSetuNet"%BotQQ:
        if send == HostQQ:
            if not setting["setuLocal"]:
                await app.sendGroupMessage(group,[
                    Plain(text="setuLocal开关已经是Net状态啦！")
                ])
            else:
                setting["setuLocal"]=False
                await app.sendGroupMessage(group,[
                    Plain(text="setuLocal开关已切换到Net！")
                ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你不是我的主人！离人家远一点啦！死变态！")
            ])
        record("setting.setSetuNet group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()=="[At::target=%i] setting.setBizhiLocal"%BotQQ:
        if send == HostQQ:
            if setting["bizhiLocal"]:
                await app.sendGroupMessage(group,[
                    Plain(text="bizhiLocal开关已经是Local状态啦！")
                ])
            else:
                setting["bizhiLocal"]=True
                await app.sendGroupMessage(group,[
                    Plain(text="bizhiLocal开关已切换到Local！")
                ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你不是我的主人！离人家远一点啦！死变态！")
            ])
        record("setting.setBizhiLocal group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()=="[At::target=%i] setting.setBizhiNet"%BotQQ:
        if send == HostQQ:
            if not setting["bizhiLocal"]:
                await app.sendGroupMessage(group,[
                    Plain(text="bizhiLocal开关已经是Net状态啦！")
                ])
            else:
                setting["bizhiLocal"]=False
                await app.sendGroupMessage(group,[
                    Plain(text="bizhiLocal开关已切换到Net！")
                ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你不是我的主人！离人家远一点啦！死变态！")
            ])
        record("setting.setBizhiNet group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()=="[At::target=%i] setting.offline"%BotQQ:
        if send == HostQQ:
            status[groupid]="offline"
            await app.sendGroupMessage(group,[
                Plain(text="Bot.offline")
            ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你不是我的主人！离人家远一点啦！死变态！")
            ])
        record("Bot.offline group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()[0:39]=="[At::target=%i] setting.addAdmin"%BotQQ:
        print(message.toString()[39:])
        # print(re.findall(r'At::target=(.*?)]',message.toString()[39:],re.S))
        target=int(re.findall(r'At::target=(.*?)]',message.toString()[39:],re.S)[0])
        if send == HostQQ:
            if target not in management[groupid]:
                management[groupid].append(target)
                await app.sendGroupMessage(group,[
                    At(target=target),
                    Plain(text="成员%s被设为管理员了哟~！\n请输入@机器人command来查看你可以执行的命令desu~"%target)
                ])
                with open("S:\MiRai_QQRobot\info\\admin.txt","w") as w:
                    for i in management[groupid]:
                        if not i==HostQQ:
                            w.write("%i:%i\n"%(groupid,i))
            else:
                await app.sendGroupMessage(group,[
                    Plain(text="成员%s已经是管理员了哟~！"%target)
                ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你不是我的主人！离人家远一点啦！死变态！")
            ])
        record("setting.addAdmin group:%s member:%s target=%s callResult:%s"%(groupid,send,target,send==HostQQ))
    elif message.toString()[0:42]=="[At::target=%i] setting.deleteAdmin"%BotQQ:
        print(message.toString()[42:])
        # print(re.findall(r'At::target=(.*?)]',message.toString()[42:],re.S))
        target=int(re.findall(r'At::target=(.*?)]',message.toString()[42:],re.S)[0])
        if send == HostQQ:
            if target not in management[groupid]:
                management[groupid].append(target)
                await app.sendGroupMessage(group,[
                    At(target=target),
                    Plain(text="成员%s本来就不是管理员哟~"%target)
                ])
            else:
                management[groupid].remove(target)
                await app.sendGroupMessage(group,[
                    At(target=target),
                    Plain(text="成员%s已经不是管理员了哟~！"%target)
                ])
                with open("S:\MiRai_QQRobot\info\\admin.txt","w") as w:
                    for i in management[groupid]:
                        if not i==HostQQ:
                            w.write("%i:%i\n"%(groupid,i))
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你不是我的主人！离人家远一点啦！死变态！")
            ])
        record("setting.deleteAdmin group:%s member:%s target=%s callResult:%s"%(groupid,send,target,send==HostQQ))

    #check
    elif message.toString()=="[At::target=%i] check.all"%BotQQ:
        if send in management[groupid]:
            await app.sendGroupMessage(group,[
                Plain(text=getStatus(member.group.id))
            ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
            ])
        record("check.all group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()=="[At::target=%i] check.memberSetuCountAll"%BotQQ:
        if send in management[groupid]:
            await app.sendGroupMessage(group,[
                Plain(text=showSetuCount(groupid))
            ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
            ])
        record("check.memberSetuCountAll group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()[0:44]=="[At::target=%i] check.memberSetuCount"%BotQQ:
        print(message.toString()[54:])
        print(re.findall(r'At::target=(.*?)]',message.toString()[44:],re.S))
        target=int(re.findall(r'At::target=(.*?)]',message.toString()[44:],re.S)[0])
        if send in management[groupid]:
            if target not in member_setu_count[groupid]:
                await app.sendGroupMessage(group,[
                    Plain(text="成员%s今日还没有要过涩图呢！快来试试吧！"%(target))
                ])
            elif member_setu_count[groupid][target] < 5:
                await app.sendGroupMessage(group,[
                    Plain(text="成员%s今日已经要了%i张涩图了！再接再厉哦！"%(target,member_setu_count[groupid][target]))
                ])
            else:
                await app.sendGroupMessage(group,[
                    Plain(text="成员%s今日已经要了%i张涩图了！老色批了！"%(target,member_setu_count[groupid][target]))
                ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
            ])
        record("check.memberSetuCount group:%s member:%s target=%s callResult:%s"%(groupid,send,target,send in management))
    elif message.toString()=="[At::target=%i] check.allAdmin"%BotQQ:
        if send in management[groupid]:
            await app.sendGroupMessage(group,[
                Plain(text=showAdmin(groupid))
            ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
            ])
        record("check.allAdmin group:%s member:%s callResult:%s"%(groupid,send,send in management))

    #info

    elif message.toString()=="[At::target=%i] info.setu"%BotQQ:
        await app.sendGroupMessage(group,[
            Plain(text="setu已调用%s次，要注意身体哦~setu虽好，可不要贪杯哦~"%setu_info)
        ])
        record("info.setu group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()=="[At::target=%i] info.weather"%BotQQ:
        await app.sendGroupMessage(group,[
            Plain(text="weather已调用%s次，出门前一定要看看天气预报哦~"%weather_info)
        ])
        record("info.weather group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()=="[At::target=%i] info.bizhi"%BotQQ:
        await app.sendGroupMessage(group,[
            Plain(text="bizhi已调用%s次，哟西哟西~"%bizhi_info)
        ])
        record("info.bizhi group:%s member:%s callResult:%s"%(groupid,send,send in management))
    elif message.toString()=="[At::target=%i] info.sys"%BotQQ:
        if send==HostQQ:
            await app.sendGroupMessage(group,[
                Plain(text=getSysInfo())
            ])
        else:
            await app.sendGroupMessage(group,[
                Plain(text="爬爬爬，你不是我的主人！离人家远一点啦！死变态！")
            ])
        record("info.sys group:%s member:%s callResult:%s"%(groupid,send,send == HostQQ))
    elif message.toString()[0:3]=="莉莉说":
        if message.toString()[3:] in setuCalled:
            if send not in member_setu_count[groupid]:
                member_setu_count[groupid][send]=1
            else:
                member_setu_count[groupid][send]+=1
            recordDragon()
    elif message.toString() in setuCalled:
        setu_info+=1
        with open("S:\MiRai_QQRobot\info\\setu.txt","w") as w:
            w.write(str(setu_info))
        if groupid in setu_forbidden:
            global forbidden_dist
            global forbidden_count
            forbidden_count+=1
            if forbidden_count>=9:
                global forbidden_dist
                await app.sendGroupMessage(group, [
                    Image.fromFileSystem(forbidden_dist)
                ])
            elif forbidden_count>=6:
                await app.sendGroupMessage(group, [
                    Plain(text="WDNMD，天天脑子里都是些什么玩意儿，滚呐！爷生气啦！揍你哦！")
                ])
            elif forbidden_count>=3:
                await app.sendGroupMessage(group, [
                    Plain(text="Kora!都说了是正规群啦！怎么老要setu，真是够讨厌的呢！再问我就生气啦！")
                ])
            else:
                await app.sendGroupMessage(group, [
                    Plain(text="我们是正规群呐，不搞setu那一套哦，想看setu去setu群desu~")
                ])
            record("setu:Default group:%s member:%s Status:Disable"%(groupid,send))
        else:
            if member_setu_dict[groupid][send]>=5:
                await app.sendGroupMessage(group, [
                    Plain(text="你今天都要了尼玛5张了，想干嘛啊？遭反？天天就尼玛冲冲冲，你咋不上天呢？乖乖等明天吧弟弟！")
                ])
                record("setu:Default group:%s member:%s Status:memberOverlimit"%(groupid,send))
            else:
                msg=""
                # try:
                #     html=requests.get(setu_src).text
                #     msg=re.findall(r'"msg":"(.*?)"',html,re.S)[0]
                # except Exception as e:
                 #     pass
                disStart=datetime.datetime.strptime(str(datetime.datetime.now().date())+'%s'%timeDisable[groupid]["start"], '%Y-%m-%d%H:%M')
                disEnd=datetime.datetime.strptime(str(datetime.datetime.now().date())+'%s'%timeDisable[groupid]["end"], '%Y-%m-%d%H:%M')
                if msg=="达到调用额度限制，如需更多额度请阅读 https:\/\/yww.uy\/setuapi" and not setting["setuLocal"]:
                    await app.sendGroupMessage(group, [
                        Plain(text="今日的setu供给么的额度了喵~")
                    ])
                    record("setu:Default group:%s member:%s Status:NetOverlimit"%(groupid,send))
                elif n_time >= disStart and n_time <= disEnd:
                    await app.sendGroupMessage(group, [
                        Plain(text="setu功能今日%s-%s为关闭状态哦~等开启了再来吧~"%(timeDisable[groupid]["start"],timeDisable[groupid]["end"]))
                    ])
                    record("setu:Default group:%s member:%s Status:timeDisable"%(groupid,send))
                elif member_setu_fobidden[groupid][send]:
                    await app.sendGroupMessage(group, [
                        Plain(text="你被禁止要涩图了哦~好好想想过去的所作所为吧！")
                    ])
                    record("setu:Default group:%s member:%s Status:setuDisable"%(groupid,send))
                elif send in forbidden:
                    await app.sendGroupMessage(group,[
                        Plain(text="要你🐎涩图？大胆妖孽！我一眼就看出来你不是人！大威天龙！世尊地藏！般若诸佛！般若巴麻空！")
                    ])
                else:
                    if send not in repeatBot and not send == HostQQ:
                        if send not in member_setu_count[groupid]:
                            member_setu_count[groupid][send]=1
                        else:
                            member_setu_count[groupid][send]+=1
                        recordDragon()
                    # member_setu_count[groupid][send]+=1
                    # print(member_setu_count)
                    global count
                    global setu_count
                    if setting["countLimit"]:
                        if send not in pmlimit[groupid]:
                            pmlimit[groupid][send]={}
                            pmlimit[groupid][send]["time"]=datetime.datetime.now()
                            pmlimit[groupid][send]["count"]=1
                        else:
                            if (datetime.datetime.now()-pmlimit[groupid][send]["time"]).seconds<60 and pmlimit[groupid][send]["count"]>=6:
                                await app.sendGroupMessage(group,[
                                    At(target=send),
                                    Plain(text="你已达到限制，每分钟最多只能要6张setu/real哦~\n歇会儿再来吧！")
                                ])
                                return
                            elif (datetime.datetime.now()-pmlimit[groupid][send]["time"]).seconds>60:
                                pmlimit[groupid][send]["time"]=datetime.datetime.now()
                                pmlimit[groupid][send]["count"]=1
                            elif (datetime.datetime.now()-pmlimit[groupid][send]["time"]).seconds<60 and pmlimit[groupid][send]["count"]<6:
                                pmlimit[groupid][send]["count"]+=1
                    if setting["setuLocal"]:
                        if group_r18[groupid]:
                            dist=random_setu(setu18_dist)
                        else:
                            dist=random_setu(setu_dist)
                        print(dist)
                    else:
                        src=re.findall(r'"url":"(.*?)"',html,re.S)[0]
                        src=src.replace("\\","")
                        print(src)
                        dist="M:\\pixiv\\setu\\%s.png"%str(count)

                        with open("M:\pixiv\setu\count.txt","w") as w:
                            w.write(str(count))

                        setu_count=setu_count+1
                        img=requests.get(src).content
                        image=IMG.open(BytesIO(img))
                        image.save(dist)
                        member_setu_dict[groupid][send]+=1
                    message_info = await app.sendGroupMessage(group, [
                        Image.fromFileSystem(dist)
                    ])
                    if not group_r18[groupid] and message.toString()=="[Image::A3C91AFE-8834-1A67-DA08-899742AEA4E5]":
                        if send not in repeatBot and not send == HostQQ:
                            member_setu_count[groupid][send]+=1
                        await app.sendGroupMessage(group, [
                            Image.fromFileSystem(random_setu(setu_dist))
                        ])
                    # encryption(dist)
                    if group_r18[groupid]:
                        message_warning=await app.sendGroupMessage(group,[
                            Plain(text="阿嘞！竟然是r18的！10s后自动撤回哦，想保存的GKD！")
                        ])
                        time.sleep(10)
                        await app.revokeMessage(message_info)
                        await app.revokeMessage(message_warning)
                        record("setu18:%s group:%s member:%s Status:Enable"%(dist,groupid,send))
                    else:
                        record("setu:%s group:%s member:%s Status:Enable"%(dist,groupid,send))
                    if not setting["setuLocal"]:
                        await app.sendGroupMessage(group,[
                            Plain(text="神秘链接："),
                            Plain(text=src)
                        ])
                        await app.sendGroupMessage(group,[
                            Plain(text="id:%s\n"%send),
                            Plain(text="今日Net额度：5张\n"),
                            Plain(text="已用Net额度：%i张"%member_setu_dict[groupid][send])
                        ])
                        record("setu:%s group:%s member:%s Status:Enable"%(dist,groupid,send))
    elif message.toString()[:5]=="setu*":
        if groupid in setu_forbidden:
            # global forbidden_dist
            # global forbidden_count
            forbidden_count+=1
            if forbidden_count>=9:
                # global forbidden_dist
                await app.sendGroupMessage(group, [
                    Image.fromFileSystem(forbidden_dist)
                ])
            elif forbidden_count>=6:
                await app.sendGroupMessage(group, [
                    Plain(text="WDNMD，天天脑子里都是些什么玩意儿，滚呐！爷生气啦！揍你哦！")
                ])
            elif forbidden_count>=3:
                await app.sendGroupMessage(group, [
                    Plain(text="Kora!都说了是正规群啦！怎么老要setu，真是够讨厌的呢！再问我就生气啦！")
                ])
            else:
                await app.sendGroupMessage(group, [
                    Plain(text="我们是正规群呐，不搞setu那一套哦，想看setu去setu群desu~")
                ])
            record("setu:Default group:%s member:%s Status:Disable"%(groupid,send))
        else:
            num=int(message.toString()[5:])
            setu_count+=num
            if send in management[groupid]:
                if send == HostQQ or num <= 3:
                    with open(setu_info_dist,"w") as w:
                        w.write(str(setu_info))
                    for i in range(num):
                        if setting["setuLocal"]:
                            dist=random_setu(setu_dist)
                        else:
                            dist="M:\\bizhi\\%s.png"%str(setu_count)
                            img=requests.get(setu_src).content
                            image=IMG.open(BytesIO(img))
                            image.save(dist)
                            with open("M:\\bizhi\count.txt","w") as w:
                                w.write(str(setu_count))
                            bizhi_count+=1
                        await app.sendGroupMessage(group, [
                            Image.fromFileSystem(dist)
                        ])
                        record("setu:%s group:%s member:%s Status:Enable"%(dist,groupid,send))
                else:
                    await app.sendGroupMessage(group, [
                        Plain(text="管理最多也只能要三张呐~我可不会被轻易玩儿坏呢！！！！")
                    ])
            elif num <= 5:
                await app.sendGroupMessage(group, [
                    Plain(text="只有主人和管理员可以使用setu*num命令哦~你没有权限的呐~")
                ])
            else:
                await app.sendGroupMessage(group, [
                    Plain(text="老色批，要那么多，给你🐎一拳，爬！")
                ])
    elif message.toString()=="bizhi":
        bizhi_info+=1
        with open(bizhi_info_dist,"w") as w:
            w.write(str(bizhi_info))
        if send in forbidden:
            await app.sendGroupMessage(group,[
                Plain(text="要你🐎bizhi？大胆妖孽！我一眼就看出来你不是人！大威天龙！世尊地藏！般若诸佛！般若巴麻空！")
            ])
        else:
            if setting["bizhiLocal"]:
                dist=random_setu(bizhi_dist)
            else:
                dist="M:\\bizhi\\%s.png"%str(bizhi_count)
                img=requests.get(bizhi_src).content
                image=IMG.open(BytesIO(img))
                image.save(dist)
                with open("M:\\bizhi\count.txt","w") as w:
                    w.write(str(bizhi_count))
                bizhi_count+=1
            await app.sendGroupMessage(group, [
                Image.fromFileSystem(dist)
            ])
        record("bizhi:%s group:%s member:%s Status:Enable"%(dist,groupid,send))
    elif message.toString()=="real":
        real_info+=1
        if not send==HostQQ:
            if send not in member_setu_count[groupid]:
                member_setu_count[groupid][send]=1
            else:
                member_setu_count[groupid][send]+=1
            recordDragon()
        with open(real_info_dist,"w") as w:
            w.write(str(real_info))
        if send in forbidden:
            await app.sendGroupMessage(group,[
                Plain(text="要你🐎real？大胆妖孽！我一眼就看出来你不是人！大威天龙！世尊地藏！般若诸佛！般若巴麻空！")
            ])
        else:
            if setting["countLimit"]:
                if send not in pmlimit[groupid]:
                    pmlimit[groupid][send]={}
                    pmlimit[groupid][send]["time"]=datetime.datetime.now()
                    pmlimit[groupid][send]["count"]=1
                else:
                    if (datetime.datetime.now()-pmlimit[groupid][send]["time"]).seconds<60 and pmlimit[groupid][send]["count"]>=6:
                        await app.sendGroupMessage(group,[
                            At(target=send),
                            Plain(text="你已达到限制，每分钟最多只能要6张setu/real哦~\n歇会儿再来吧！")
                        ])
                        return
                    elif (datetime.datetime.now()-pmlimit[groupid][send]["time"]).seconds>60:
                        pmlimit[groupid][send]["time"]=datetime.datetime.now()
                        pmlimit[groupid][send]["count"]=1
                    elif (datetime.datetime.now()-pmlimit[groupid][send]["time"]).seconds<60 and pmlimit[groupid][send]["count"]<6:
                        pmlimit[groupid][send]["count"]+=1
            dist=random_setu(real_dist)
            await app.sendGroupMessage(group, [
                Image.fromFileSystem(dist)
            ])
            record("real:%s group:%s member:%s Status:Enable"%(dist,groupid,send))
    elif message.toString()=="[At::target=%i] 今天我冲不冲？"%BotQQ or message.toString()=="[At::target=%i] 今天我冲不冲"%BotQQ or message.toString()=="今天我冲不冲" or message.toString()=="冲？":
        await app.sendGroupMessage(group,[
            At(target=send),
            Plain(text=(randomRush()))
        ])
        record("rush group:%s member:%s"%(groupid,send))
    elif message.toString()[0:27]=="[At::target=%i] fuck"%BotQQ and send==HostQQ:
        print(message.toString()[0:27])
        print(re.findall(r'At::target=(.*?)]',message.toString()[27:],re.S))
        target=int(re.findall(r'At::target=(.*?)]',message.toString()[27:],re.S)[0])
        for i in range(10):
            text=requests.get(zuanLow_src).text
            await app.sendGroupMessage(group,[
                At(target=target),
                Plain(text)
            ])
        record("fuck group:%s member:%s target:%s callResult:%s"%(groupid,send,target,send in management))
    elif "[At::target=%i]"%BotQQ in message.toString():
        # transText,transTo=re.findall(r'[At::target=%i] (.*?)用(.*?)怎么说.*?',message.toString(),re.S)[0]
        # if not len(transText)==0:
        #     targetLanguageSrc="https://translate.google.cn/#view=home&op=translate&sl=zh-CN&tl=en&text=%s"%transTo
        #     trResponse=requests.get(targetLanguageSrc)
        #     trhtml=trResponse.text
            
        #     tarnsSrc=translate_src + "&text=%s"%transText
        # else:
        if send == HostQQ:
            await app.sendGroupMessage(group, [
                Plain(text="诶嘿嘿，老公@我是要找人家玩嘛~纱雾这就来找你玩哟~")
            ])
            record("HostQQ @ group:%s member:%s"%(groupid,send))
        else:
            if not mode_now=="normal":
                # text="@我是要干什么呢？可以通过 @我+menu/command/info/mode 的方式查询信息哟~"
                if mode_now=="zuanHigh":
                    text=requests.get(zuanHigh_src).text
                    record("zuanHigh @ group:%s member:%s"%(groupid,send))
                elif mode_now=="zuanLow":
                    text=requests.get(zuanLow_src).text
                    record("zuanLow @ group:%s member:%s"%(groupid,send))
                elif mode_now=="rainbow":
                    text=requests.get(rainbow_src).text
                    record("rainbow @ group:%s member:%s"%(groupid,send))
                await app.sendGroupMessage(group, [
                    At(target=send),
                    Plain(text=text)
                ])
    elif message.toString()=="嘀嘀嘀" or message.toString()=="ddd" or message.toString()=="滴滴滴":
        await app.sendGroupMessage(group, [
            Plain(text="滴什么滴？少年，来点儿涩图不？")
        ])
        record("ddd group:%s member:%s"%(groupid,send))
    elif "纱雾" in message.toString() and "可爱" in message.toString() and "不" not in message.toString():
        await app.sendGroupMessage(group, [
            Plain(text="欸嘿嘿，纱雾超可爱的呢=v=！！！")
        ])
        record("赞美纱雾 group:%s member:%s"%(groupid,send))
    elif "纱雾" in message.toString() and "不可爱" in message.toString():
        await app.sendGroupMessage(group, [
            Plain(text="哼！谁说的！纱雾明明超可爱的>^<！！！")
        ])
        record("纱雾不可爱？ group:%s member:%s"%(groupid,send))
    elif "老婆" in message.toString() and send==HostQQ:
        await app.sendGroupMessage(group, [
            At(target=HostQQ),
            Plain(text="欸嘿嘿，爱你哟老公！")
        ])
        record("赞美纱雾 group:%s member:%s"%(groupid,send))
    elif "摸" in message.toString() and "纱雾" in message.toString():
        if send == HostQQ:
            await app.sendGroupMessage(group, [
                At(target=send),
                Plain(text="欸嘿嘿，如果是你的话，可以的哟~尽情摸个够吧！")
            ])
        elif send==2858306369:
            await app.sendGroupMessage(group, [
                At(target=send),
                Plain(text="你就是个没脑子的替身使者，爷不鸟你！")
            ])
        else:
            text=requests.get(zuanLow_src).text
            await app.sendGroupMessage(group, [
                At(target=send),
                Plain(text=text)
            ])
        record("反摸纱雾 group:%s member:%s"%(groupid,send))
    elif "摸" in message.toString() and not message.toString()=="摸什么摸，给爷爬！":
        if send == HostQQ:
            await app.sendGroupMessage(group, [
                Plain(text="欸嘿嘿，摸摸摸！")
            ])
        # else:
        #     await app.sendGroupMessage(group, [
        #         Plain(text="摸什么摸，给爷爬！")
        #     ])
        record("摸 group:%s member:%s"%(groupid,send))
    elif "有无" in message.toString() and ("x37" in message.toString() or "X37" in message.toString() or "纱雾" in message.toString() or "SAGIRI" in message.toString() or "sagiri" in message.toString()) and not send == HostQQ:
        text=requests.get(zuanLow_src).text
        await app.sendGroupMessage(group, [
            At(target=send),Plain(text=text)
        ])
        record("反辱骂x37有无 group:%s member:%s"%(groupid,send))
    elif "有无" in message.toString():
        await app.sendGroupMessage(group, [
            Plain(text="无")
        ])
        record("有无 group:%s member:%s"%(groupid,send))
    elif "选择表盘" in message.toString():
        if message.toString() == "选择表盘":
            clockMessage=[
                At(target=send),
                Plain(text="看中后直接发送选择表盘+序号即可哦~\n"),
                Plain(text="如:选择表盘1\n"),
                Plain(text="表盘预览:")
            ]
            clockList = os.listdir(clockPreview_dist)
            # print(clockList)
            clockList.sort(key=lambda x:int(x[:-4]))
            # print(clockList)
            index=1
            for i in clockList:
                clockMessage.append(Plain(text="\n%s."%index))
                clockMessage.append(Image.fromFileSystem(clockPreview_dist+i))
                index+=1
            await app.sendGroupMessage(group,clockMessage)
            record("GetChoiceClock group:%s member:%s"%(groupid,send))
        else:
            code=message.toString()[4:]
            if code.isdigit():
                clockChoice[groupid][send]=int(code)
                await app.sendGroupMessage(group,[
                    Plain(text="已经选择了表盘%s呢!\n现在可以问我时间啦~"%code)
                ])
                recordClock()
            else:
                await app.sendGroupMessage(group,[
                    Plain(text="看中后直接发送选择表盘+序号即可哦~\n"),
                    Plain(text="再检查下有没有输错呢~\n")
                ])
            record("ChoiceClock group:%s member:%s"%(groupid,send))
    elif "几点啦" in message.toString() or "几点了" in message.toString():
        if send not in clockChoice[groupid]:
            clockMessage=[
                At(target=send),
                Plain(text="你还没有选择表盘哦~快来选择一个吧~\n"),
                Plain(text="看中后直接发送选择表盘+序号即可哦~\n"),
                Plain(text="如:选择表盘1\n"),
                Plain(text="表盘预览:")
            ]
            clockList = os.listdir(clockPreview_dist)
            clockList.sort(key=lambda x:int(x[:-4]))
            index=1
            for i in clockList:
                clockMessage.append(Plain(text="\n%s."%index))
                clockMessage.append(Image.fromFileSystem(clockPreview_dist+i))
                index+=1
            await app.sendGroupMessage(group,clockMessage)
            record("UnChoiceClock group:%s member:%s"%(groupid,send))
        else:
            t = datetime.datetime.now()    #目前时间
            t = t.strftime("%H:%M")
            t = t.replace(":","")
            dist=time_dist+str(clockChoice[groupid][send])+"/%s.png"%t
            await app.sendGroupMessage(group, [
                Image.fromFileSystem(dist)
            ])
            record("GetTime group:%s member:%s"%(groupid,send))

if __name__ == "__main__":
    app.run()
