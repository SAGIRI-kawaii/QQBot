#coding=utf-8
from mirai import Mirai, Plain, MessageChain, Friend, Image, Group, protocol, Member, At, Face, JsonMessage,XmlMessage,LightApp,Quote,AtAll
from mirai import MemberJoinEvent,MemberLeaveEventKick,MemberLeaveEventQuit,MemberSpecialTitleChangeEvent,MemberSpecialTitleChangeEvent,MemberPermissionChangeEvent,MemberMuteEvent,MemberUnmuteEvent,BotJoinGroupEvent,GroupRecallEvent,MemberLeaveEventKick
from mirai import exceptions
import BilibiliLiveDanmaku
from variable import *
from process import *
import pymysql
from itertools import chain
import threading
import asyncio
from taskTimerClass import *

BotQQ =  getConfig("BotQQ")  # 字段 qq 的值
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
listenId={}                 #监听成员列表

localtime = time.localtime(time.time())
day_set=localtime.tm_mday

dragonId=[]                             #龙王id（可能有多个）
dragon={}                               #各群今日是否已宣布龙王

n_time = datetime.datetime.now()    #目前时间
start_time = 0    #程序启动时间
d_time = datetime.datetime.strptime(str(datetime.datetime.now().date())+' 23:00', '%Y-%m-%d %H:%M')   #龙王宣布时间
group_repeat={}             #每个群判断是否复读的dict

non_reply=["setu","bizhi","","别老摸了，给爷冲！","real","几点了","几点啦","几点啦?","几点了?","冲？","今天我冲不冲？","车车","wyy"]      #不复读关键词
setuCallText=["[Image::A3C91AFE-8834-1A67-DA08-899742AEA4E5]","[Image::A0FE77EE-1F89-BE0E-8E2D-62BCD1CAB312]","[Image::04923170-2ACB-5E94-ECCD-953F46E6CAB9]","[Image::3FFFE3B5-2E5F-7307-31A4-2C7FFD2F395F]","[Image::8A3450C7-0A98-4E81-FA24-4A0342198221]","setu","车车","开车","来点色图","来点儿车车"]
searchCallText=["search","搜图"]
timeCallText=["几点啦","几点了","几点啦？","几点了？"]
setuBot=[]
setuGroup=[]
repeatBot=[]
groupIdList=[]

@app.subroutine
async def subroutine1(app: Mirai):
    print("subroutine1 started")
    global listenId
    start_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    groupList = await app.groupList()
    print(groupList)
    checkGroupInit(groupList)
    for i in groupList:
        groupIdList.append(i.id)
        memberPicCount[i.id]={}
        member_dict={}
        member_fobidden={}
        memberList = await app.memberList(i.id)
        MemberList[i.id]=memberList
        for j in memberList:
            member_dict[j.id]=0
            member_fobidden[j.id]=False
        group_repeat[i.id]={"lastMsg":"","thisMsg":"","stopMsg":""}
    listenId=getListenId(groupIdList)
    print(listenId)
    # for i in groupList:
    #     await app.sendGroupMessage(i,[
    #         Plain(text="爷来啦~")
    #     ])

'''
@app.subroutine
async def listenSubscribe(app: Mirai):
    print("listenSubscribe start")
    conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
    cur = conn.cursor()
    sql = "select roomid from subscribelisten where platform='bilibili'"
    cur.execute(sql) 
    data = cur.fetchall()
    roomId=list(chain.from_iterable(data))
    sql = "select * from subscribe where platform='bilibili'"
    cur.execute(sql) 
    data = cur.fetchall()
    sql = "select count(*) from subscribe where platform='bilibili'"
    cur.execute(sql) 
    count = cur.fetchone()[0]
    conn.close()
    cur.close()
    subscribeList={}
    for i in data:
        subscribeList[i[2]]=[]
    for i in data:
        subscribeList[i[2]].append({"groupId":i[0],"memberId":i[1]})
    status={}
    for i in roomId:
        status[i]=True
    while(1):
        conn = pymysql.connect(host=host, user=user, passwd=dbPass, db=db, port=3306, charset="utf8")
        cur = conn.cursor()
        sql = "select count(*) from subscribe where platform='bilibili'"
        cur.execute(sql) 
        newCount = cur.fetchone()[0]
        if count==newCount:
            conn.close()
            cur.close()
        else:
            print("new record!") 
            sql = "select roomid from subscribelisten where platform='bilibili'"
            cur.execute(sql) 
            data = cur.fetchall()
            roomId=list(chain.from_iterable(data))
            sql = "select * from subscribe where platform='bilibili'"
            cur.execute(sql) 
            data = cur.fetchall()
            sql = "select count(*) from subscribe where platform='bilibili'"
            cur.execute(sql) 
            count = cur.fetchone()[0]
            conn.close()
            cur.close()
            subscribeList={}
            for i in data:
                subscribeList[i[2]]=[]
                subscribeList[i[2]].append({"groupId":i[0],"memberId":i[1]})
            status={}
            for i in roomId:
                status[i]=True
        print("start listening room")
        # print(subscribeList)
        for i in roomId:
            last=status[i]
            roomInfo=getBilibiliRoomInfo(i)
            status[i]=roomInfo[1]
            if last==False and status[i]==True:
                print("get %s online"%i)
                print(subscribeList[i])
                for memberDict in subscribeList[i]:
                    msgList=[]
                    # msgList.append(At(target=memberDict["memberId"]))
                    # msgList.append(Plain("\n"))
                    msgList.append(Plain(text="你关注的主播 %s 开播啦~\n"%roomInfo[3]))
                    msgList.append(Plain(text="快来看看吧~\n"))
                    msgList.append(Plain(text="地址:%s"%roomInfo[6]))
                    # await app.sendGroupMessage(memberDict["groupId"],msgList)
                    try:
                        await app.sendTempMessage(memberDict["groupId"],memberDict["memberId"],msgList)
                    except Exception:
                        pass
        print("end listening room")
        await asyncio.sleep(10)
'''

async def dragon(groupIdList):
    print("dragon")
    print(groupIdList)
    for i in groupIdList:
        if i!=696562079:
            if getSetting(i,"setu") or getSetting(i,"real"):
                msg=FindDragonKing(i,MemberList[i])
                updateDragon(i,0,"all")
                try:
                    await app.sendGroupMessage(i,msg)
                except Exception:
                    pass
            else:
                pass

def func1(groupList):
    print("func")
    loop =  asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(dragon(groupList))

async def notice(groupIdList,text):
    for i in groupIdList:
        if i!=696562079:
            try:
                await app.sendGroupMessage(i,Plain(text=text))
            except Exception:
                pass

def noticeText(groupList,text):
    print("noticeText")
    loop =  asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(notice(groupList,text))

async def daka(text,groupId):
    try:
        await app.sendGroupMessage(groupId,[AtAll(),Plain(text=text)])
    except Exception as e:
        print(e)

def dakaFun(text,groupId):
    print("dakaFun")
    loop =  asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(daka(text,groupId))

timer = TaskTimer() 
timer.join_task(func1, [groupIdList], timing=22.5) # 每天22:30执行 ·
# timer.join_task(noticeText, [groupIdList,"兄弟姐妹们！17点啦！别忘了防疫体温打卡鸭!"], timing=17.0) # 每天17:00执行
# timer.join_task(noticeText, [groupIdList,"兄弟姐妹们！21点啦！别忘了防疫每日签到鸭!"], timing=21.0) # 每天21:00执行
timer.join_task(dakaFun, ["兄弟姐妹们！17:00啦！别忘了防疫体温打卡鸭!",groupId], timing=17.0) # 每天17:00执行
timer.join_task(dakaFun, ["兄弟姐妹们！21:00啦！别忘了防疫每日签到鸭!",groupId], timing=21.0) # 每天21:00执行
timer.join_task(dakaFun, ["兄弟姐妹们！17:40啦！防疫体温打卡还有20分钟就结束了鸭!冲冲冲！",groupId], timing=17.6667) # 每天17:40执行
timer.join_task(dakaFun, ["兄弟姐妹们！21:40啦！防疫每日签到还有20分钟就结束了鸭!冲冲冲！",groupId], timing=21.6667) # 每天21:40执行
# timer.join_task(dakaFun, ["test 22.25",], timing=22.25) # 每天21:00执行
timer.start()

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
            img = message.getAllofComponent(Image)
            for i in img:
                botSetuCount=getData("botSetuCount")+1
                updateData(botSetuCount,"botSetuCount")
                dist="%s%s.png"%(setuBotDist,botSetuCount)
                imgContent=requests.get(i.url).content
                image=IMG.open(BytesIO(imgContent))
                image.save(dist)
                insertHash("%s%d.png"%(setuBotDist,botSetuCount),imgHash("%s%d.png"%(setuBotDist,botSetuCount)),"tribute")
            await app.sendFriendMessage(friend,[
                Plain(text="%d Image saved!"%len(img))
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
            try:
                record("repeat %s"%message.toString(),"none",sender,groupId,True,"function")
            except pymysql.err.InternalError:
                pass


    if message.toString()=="test" and sender==HostQQ:
        # getListenId(groupIdList)
        # msg=FindDragonKing(groupId,MemberList[groupId])
        # msg=showGithub()
        msg = getHistoryToday()
        await app.sendGroupMessage(group,msg)

    if message.toString()=="test2" and sender==HostQQ:
        test2="""{
	"app": "com.tencent.giftmall.giftark",
	"desc": "",
	"view": "giftArk",
	"ver": "1.0.4.1",
	"prompt": "[礼物]小纱雾酱的博客",
	"appID": "",
	"sourceName": "",
	"actionData": "",
	"actionData_A": "",
	"sourceUrl": "",
	"meta": {
		"giftData": {
			"sender": "0",
			"isFree": "1",
			"giftName": "纱雾酱的博客",
			"desc": "小纱雾酱赛高！",
			"orderNum": "http://mirror.blog.sagiri-web.com",
			"toUin": "1900384123",
			"unopenIconUrl": "\/aoi\/sola\/20190402111555_yWazmedH08.png",
			"openIconUrl": "\/aoi\/sola\/20190505171810_Tq5J6Wtxj8.png",
			"boxZipUrl": "",
			"giftZipUrl": "",
			"giftParticleUrl": "",
			"msgId": "6725255579486284051"
		}
	},
	"config": {
		"forward": 0
	}
}"""
        test3="""{
	"prompt": "[欢迎入群]",
	"extraApps": [],
	"sourceUrl": "",
	"appID": "",
	"sourceName": "",
	"desc": "",
	"app": "com.tencent.qqpay.qqmp.groupmsg",
	"ver": "1.0.0.7",
	"view": "groupPushView",
	"meta": {
		"groupPushData": {
			"fromIcon": "",
			"fromName": "name",
			"time": "",
			"report_url": "http:\\/\\/kf.qq.com\\/faq\\/180522RRRVvE180522NzuuYB.html",
			"cancel_url": "http:\\/\\/www.baidu.com",
			"summaryTxt": "",
			"bannerTxt": "欸嘿~欢迎进群呐~进来了就不许走了哦~",
			"item1Img": "",
			"bannerLink": "",
			"bannerImg": "http:\\/\\/gchat.qpic.cn\\/gchatpic_new\\/12904366\\/1046209507-2584598286-E7FCC807BECA2938EBE5D57E7E4980FF\\/0?term=2"
		}
	},
	"actionData": "",
	"actionData_A": ""
}"""
        test4="""{"prompt":"已关机","extraApps":[],"sourceUrl":"","appID":"","sourceName":"","desc":"","app":"com.tencent.qqpay.qqmp.groupmsg","ver":"1.0.0.7","view":"groupPushView","meta":{"groupPushData":{"fromIcon":"","fromName":"name","time":"","report_url":"http:\\/\\/kf.qq.com\\/faq\\/180522RRRVvE180522NzuuYB.html","cancel_url":"http:\\/\\/www.baidu.com","summaryTxt":"靓仔心伤","bannerTxt":"靓仔心伤爱别离大宝贝","item1Img":"","bannerLink":"","bannerImg":"http:\\/\\/gchat.qpic.cn\\/gchatpic_new\\/1796534579\\/1090269581-2846079729-FFB9E9FE88D37B8C73B631B1F0E4846B\\/0?term=2"}},"actionData":"","actionData_A":""}"""
        await app.sendGroupMessage(group,[LightApp(test3)])
    if message.hasComponent(Image) and getReady(groupId,sender,"searchReady"):
        updateUserCalled(groupId,sender,"search",1)
        try:
            await app.sendGroupMessage(group,[
                At(target=sender),
                Plain(text="正在搜索请稍后呐~没反应了可能就是卡了呐~多等等呐~")
            ])
        except exceptions.BotMutedError:
            pass
    elif message.hasComponent(Image) and getSetting(groupId,"listen") and sender in listenId[groupId]:      # 图片监听保存
        botSetuCount=getData("botSetuCount")+1
        dist="%s%s.png"%(setuBotDist,botSetuCount)
        img = message.getFirstComponent(Image)
        img=requests.get(img.url).content
        image=IMG.open(BytesIO(img))
        image.save(dist)
        updateData(botSetuCount,"botSetuCount")
        print("Image saved from group %s!"%group.name)
        record("save img from group",dist,groupId,0,True,"img")
    try:
        Msg = await Process(message,groupId,sender,MemberList[groupId])
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
        elif Msg[0]=="上贡":
            source=message.getSource()
            Msg=Msg[1:]
            try:
                msg = await app.sendGroupMessage(group,Msg,quoteSource=source)
            except exceptions.BotMutedError:
                # NVML_PAGE_RETIREMENT_CAUSE_MULTIPLE_SINGLE_BIT_ECC_ERRORS
                pass
        elif Msg[0]=="pic*":
            Msg=Msg[1:]
            try:
                for i in Msg:
                    await app.sendGroupMessage(group,[i])
            except exceptions.BotMutedError:
                pass
        elif str(type(Msg[0]))=="<class 'str'>" and Msg[0][:10]=="addListen.":
            _,gid,mid=Msg[0].split(".")
            if int(mid) not in listenId[int(gid)]:
                listenId[int(gid)].append(int(mid))
            Msg=Msg[1:]
            await app.sendGroupMessage(group,Msg)
        else:
            try:
                msg = await app.sendGroupMessage(group,Msg)
                if getSetting(groupId,"r18") and "setu" in message.toString() and str(type(Msg[0]))=="<class 'mirai.image.LocalImage'>":
                    await asyncio.sleep(10)
                    await app.revokeMessage(msg)
            except exceptions.BotMutedError:
                pass
    except Exception as e:
        await app.sendGroupMessage(group,[Plain(text="Error:\n%s"%e)])
    

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
        welcome="""{
	"prompt": "[欢迎入群]",
	"extraApps": [],
	"sourceUrl": "",
	"appID": "",
	"sourceName": "",
	"desc": "",
	"app": "com.tencent.qqpay.qqmp.groupmsg",
	"ver": "1.0.0.7",
	"view": "groupPushView",
	"meta": {
		"groupPushData": {
			"fromIcon": "",
			"fromName": "name",
			"time": "",
			"report_url": "http:\\/\\/kf.qq.com\\/faq\\/180522RRRVvE180522NzuuYB.html",
			"cancel_url": "http:\\/\\/www.baidu.com",
			"summaryTxt": "",
			"bannerTxt": "欸嘿~欢迎进群呐~进来了就不许走了哦~",
			"item1Img": "",
			"bannerLink": "",
			"bannerImg": "http:\\/\\/gchat.qpic.cn\\/gchatpic_new\\/12904366\\/1046209507-2584598286-E7FCC807BECA2938EBE5D57E7E4980FF\\/0?term=2"
		}
	},
	"actionData": "",
	"actionData_A": ""
}"""
        await app.sendGroupMessage(event.member.group.id,[LightApp(welcome)])
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
                Plain(text="%s怎么走了呐~是纱雾不够可爱吗嘤嘤嘤"%qq2name(MemberList[event.member.group.id],event.member.id))
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