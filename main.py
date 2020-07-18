#coding=utf-8
from mirai import Mirai, Plain, MessageChain, Friend, Image, Group, protocol, Member, At, Face, JsonMessage
from mirai import MemberJoinEvent,MemberLeaveEventKick,MemberLeaveEventQuit,MemberSpecialTitleChangeEvent,MemberSpecialTitleChangeEvent,MemberPermissionChangeEvent,MemberMuteEvent,MemberUnmuteEvent,BotJoinGroupEvent,GroupRecallEvent
from mirai import exceptions
# from variable import *
from process import *
import pymysql
from itertools import chain
import threading
import asyncio
from function import *

BotQQ =  getConfig("BotQQ")  # 字段 qq 的值 1785007019
HostQQ = getConfig("HostQQ") #主人QQ
authKey = getConfig("authKey") # 字段 authKey 的值
mirai_api_http_locate = getConfig("mirai_api_http_locate") # httpapi所在主机的地址端口,如果 setting.yml 文件里字段 "enableWebsocket" 的值为 "true" 则需要将 "/" 换成 "/ws", 否则将接收不到消息.
app = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={BotQQ}")

memberSetuNet={}            #每个群每个成员要的网络setu计数（限制每人五张）
memberPicCount={}           #每个群成员要setu/real的次数
group_repeat={}             #每个群判断是否复读的dict
group_repeat_switch={}      #每个群的复读开关
timeDisable={}              #关闭setu开关的时间
MemberList={}               #成员列表

localtime = time.localtime(time.time())
day_set=localtime.tm_mday

dragonId=[]                             #龙王id（可能有多个）
dragon={}                               #各群今日是否已宣布龙王

n_time = datetime.datetime.now()    #目前时间
start_time = 0    #程序启动时间
d_time = datetime.datetime.strptime(str(datetime.datetime.now().date())+'23:00', '%Y-%m-%d%H:%M')   #龙王宣布时间
group_repeat={}             #每个群判断是否复读的dict

reply_word=["啧啧啧","确实","giao","？？？","???","芜湖","是谁打断了复读？","是谁打断了复读?","老复读机了","就这","就这？","就这?"]     #复读关键词
non_reply=["setu","bizhi","","别老摸了，给爷冲！","real","几点了","几点啦","几点啦?","几点了?","冲？","今天我冲不冲？"]      #不复读关键词
setuCallText=["[Image::A3C91AFE-8834-1A67-DA08-899742AEA4E5]","[Image::A0FE77EE-1F89-BE0E-8E2D-62BCD1CAB312]","[Image::04923170-2ACB-5E94-ECCD-953F46E6CAB9]","[Image::3FFFE3B5-2E5F-7307-31A4-2C7FFD2F395F]","[Image::8A3450C7-0A98-4E81-FA24-4A0342198221]","setu","车车","开车","来点色图","来点儿车车"]
searchCallText=["search","搜图"]
timeCallText=["几点啦","几点了","几点啦？","几点了？"]
setuBot=[]
setuGroup=[]
repeatBot=[]

@app.subroutine
async def subroutine1(app: Mirai):
    print("subroutine1 started")
    global bizhiCalled
    global setuCalled
    global realCalled
    global weatherCalled
    global responseCalled
    global count
    global start_time
    global timeDisable
    global searchCount
    global city
    start_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    groupList = await app.groupList()
    print(groupList)
    checkGroupInit(groupList)
    for i in groupList:
        memberPicCount[i.id]={}
        member_dict={}
        member_fobidden={}
        memberList = await app.memberList(i.id)
        MemberList[i.id]=memberList
        for j in memberList:
            member_dict[j.id]=0
            member_fobidden[j.id]=False
        memberSetuNet[i.id]=member_dict
        memberSetuFobidden[i.id]=member_fobidden
        dragon[i.id]=False
        group_repeat[i.id]={"lastMsg":"","thisMsg":"","stopMsg":""}
    # for i in groupList:
    #     await app.sendGroupMessage(i,[
    #         Plain(text="爷来啦~")
    #     ])
        #读取信息并存储

    # with open(dragonDist,"r") as f:
    #     today=datetime.datetime.now().strftime("%Y-%m-%d")
    #     text = f.readline().strip()
    #     print(text,today)
    #     if not text==str(today):
    #         return
    #     while 1:
    #         text = f.readline().strip()
    #         if not text:
    #             break
    #         groupid,memberid,count=text.split(":")
    #         groupid=int(groupid)
    #         memberid=int(memberid)
    #         memberPicCount[groupid][memberid]=int(count)

@app.receiver("FriendMessage")
async def event_gm(app: Mirai, friend: Friend, message:MessageChain):
    print("friend Message")
    if friend.id==HostQQ:
        if message.toString()[:5]=="发布消息：":
            msg=message.toString().replace("发布消息：","")
            groupList = await app.groupList()
            for i in groupList:
                await app.sendGroupMessage(i,msg)
        elif message.hasComponent(Image):
            botSetuCount=getData("botSetuCount")+1
            dist="%s%s.png"%(setuBotDist,botSetuCount)
            img = message.getFirstComponent(Image)
            img=requests.get(img.url).content
            image=IMG.open(BytesIO(img))
            image.save(dist)
            updateData(botSetuCount,"botSetuCount")
            await app.sendFriendMessage(friend,[
                Plain(text="Image saved!")
            ])
            record("save img from Host",dist,HostQQ,0,True,"img")

@app.receiver("GroupMessage")
async def GMHandler(app: Mirai, group:Group, message:MessageChain, member:Member):
    sender=member.id
    groupId=group.id
    print("来自群%s("%getSetting(groupId,"groupName"),groupId,")中成员%s("%qq2name(MemberList[groupId],sender),sender,")的消息:",message.toString(),sep='')
    group_repeat[member.group.id]["lastMsg"]=group_repeat[member.group.id]["thisMsg"]
    group_repeat[member.group.id]["thisMsg"]=message.toString()
    if not group_repeat[member.group.id]["lastMsg"]==group_repeat[member.group.id]["thisMsg"]:
        group_repeat[member.group.id]["stopMsg"]=""
    if getSetting(groupId,"repeat") and group_repeat[groupId]["lastMsg"]==group_repeat[groupId]["thisMsg"] and message.toString() not in non_reply and "[At::target=%i]"%BotQQ not in message.toString():
        if not group_repeat[member.group.id]["stopMsg"]==group_repeat[member.group.id]["thisMsg"]:
            msg=[]
            index=0
            for i in message:
                if index<1:
                    index+=1
                else:
                    msg.append(i)
            try:
                await app.sendGroupMessage(group,msg)
            except exceptions.BotMutedError:
                pass
            group_repeat[member.group.id]["stopMsg"]=group_repeat[member.group.id]["thisMsg"]
            record("repeat %s"%message.toString(),"none",sender,groupId,True,"function")
    if message.hasComponent(Image) and getSearchReady(groupId,sender):
        try:
            await app.sendGroupMessage(group,[
                At(target=sender),
                Plain(text="正在搜索请稍后呐~没反应了可能就是卡了呐~多等等呐~")
            ])
        except exceptions.BotMutedError:
            pass
    Msg= await Process(message,groupId,sender,MemberList[groupId])
    if Msg=="noneReply":
        pass
    elif Msg=="goodNight":
        try:
            await app.sendGroupMessage(group,[
                    At(target=sender),
                    Plain(text="晚安，睡个好觉呐~")
                ]) 
        except exceptions.BotMutedError:
            pass
        await app.mute(group,member,28800)
    elif Msg=="muteAll":
        try:
            await app.sendGroupMessage(group,[
                    Plain(text="万马齐喑！")
                ]) 
        except exceptions.BotMutedError:
            pass
        await app.muteAll(group)
    elif Msg=="unmuteAll":
        try:
            await app.sendGroupMessage(group,[
                    Plain(text="春回大地！")
                ]) 
        except exceptions.BotMutedError:
            pass
        await app.unmuteAll(group)
    elif Msg=="lightningPic":
        try:
            await app.mute(group,member,60)
            try:
                await app.sendGroupMessage(group,[
                        Plain(text="啊这。。。啊 正 道 的 光~劈 在 了 涩 批 上~他将在医院里呆上整整一分钟!(p=0.30)")
                    ]) 
            except exceptions.BotMutedError:
                pass
        except PermissionError:
            try:
                await app.sendGroupMessage(group,[
                        Plain(text="啊这。。。啊 正 道 的 光~劈 在 了 涩 批 上~但可惜我权限不足呐~没有进医院真是幸运呐~")
                    ]) 
            except exceptions.BotMutedError:
                pass
    else:
        try:
            msg = await app.sendGroupMessage(group,Msg)
            if getSetting(groupId,"r18") and "setu" in message.toString():
                await asyncio.sleep(10)
                await app.revokeMessage(msg)
        except exceptions.BotMutedError:
            pass

# 加入群
@app.receiver("MemberJoinEvent")
async def member_join(app: Mirai, event: MemberJoinEvent):
    try:
        await app.sendGroupMessage(
            event.member.group.id,[
                At(target=event.member.id),
                Plain(text="我是本群小可爱纱雾哟~欢迎呐~一起快活鸭~")
            ]
        )
    except exceptions.BotMutedError:
        pass

# 被踢了
@app.receiver("MemberLeaveEventKick")
async def member_join(app: Mirai, event: MemberLeaveEventKick):
    try:
        await app.sendGroupMessage(
            event.member.group.id,[
                Plain(text="%s滚蛋了呐~"%qq2name(MemberList[event.member.group.id],event.member.id))
            ]
        )
    except exceptions.BotMutedError:
        pass

# 退群了
@app.receiver("MemberLeaveEventQuit")
async def member_join(app: Mirai, event: MemberLeaveEventQuit):
    try:
        await app.sendGroupMessage(
            event.member.group.id,[
                Plain(text="%s滚蛋了呐~"%qq2name(MemberList[event.member.group.id],event.member.id))
            ]
        )
    except exceptions.BotMutedError:
        pass

# 群头衔更改
@app.receiver("MemberSpecialTitleChangeEvent")
async def member_join(app: Mirai, event: MemberSpecialTitleChangeEvent):
    try:
        await app.sendGroupMessage(
            event.member.group.id,[
                Plain(text="啊嘞嘞？%s的群头衔变成%s了呐~"%(qq2name(MemberList[event.member.group.id],event.member.id),event.current))
            ]
        )
    except exceptions.BotMutedError:
        pass

# 成员权限变更
@app.receiver("MemberPermissionChangeEvent")
async def member_join(app: Mirai, event: MemberPermissionChangeEvent):
    try:
        await app.sendGroupMessage(
            event.member.group.id,[
                Plain(text="啊嘞嘞？%s的权限变成%s了呐~"%(qq2name(MemberList[event.member.group.id],event.member.id),event.current))
            ]
        )
    except exceptions.BotMutedError:
        pass

# 成员被禁言
@app.receiver("MemberMuteEvent")
async def member_join(app: Mirai, event: MemberMuteEvent):
    if not event.operator==None:
        try:
            await app.sendGroupMessage(
                event.member.group.id,[
                    Plain(text="哦~看看是谁被关进小黑屋了？\n哦我的上帝啊~是%s！他将在小黑屋里呆%s哦~"%(qq2name(MemberList[event.member.group.id],event.member.id),sec2Str(event.durationSeconds)))
                ]
            )
        except exceptions.BotMutedError:
            pass

# 成员解除禁言
@app.receiver("MemberUnmuteEvent")
async def member_join(app: Mirai, event: MemberUnmuteEvent):
    try:
        await app.sendGroupMessage(
            event.member.group.id,[
                Plain(text="啊嘞嘞？%s被放出来了呢~"%qq2name(MemberList[event.member.group.id],event.member.id))
            ]
        )
    except exceptions.BotMutedError:
        pass

# 加入新群（初始化信息等）
@app.receiver("BotJoinGroupEvent")
async def member_join(app: Mirai, event: BotJoinGroupEvent):
    print("add group")
    try:
        await app.sendGroupMessage(
            event.group.id,[
                Plain(text="欸嘿嘿~我来啦！宇宙无敌小可爱纱雾酱华丽登场！")
            ]
        )
    except exceptions.BotMutedError:
        pass
    await addGroupinit(event.group.id,event.group.name)
1
# 防撤回
# @app.receiver("GroupRecallEvent")
# async def member_join(app: Mirai, event: GroupRecallEvent):
#     if event.operator==event.authorId:
#         text="%s撤回了他的一条消息呢~↓\n"%qq2name(MemberList[event.group.id],event.operator)
#         revokeMsg=Mirai.messageFromId(event.messageId)
#         print(revokeMsg)
#         revokeMsg.insert(0,Plain(text=text))
#         await app.sendGroupMessage(event.group.id,revokeMsg)

if __name__ == "__main__":
    app.run()  