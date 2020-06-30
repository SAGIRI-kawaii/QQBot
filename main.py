from mirai import Mirai, Plain, MessageChain, Friend, Image, Group, protocol, Member, At, Face, JsonMessage
# from variable import *
from process import *
import pymysql
from itertools import chain


BotQQ = 762802224 # 字段 qq 的值
HostQQ = 1900384123 #主人QQ
authKey = '1234567890' # 字段 authKey 的值
mirai_api_http_locate = 'localhost:8080/' # httpapi所在主机的地址端口,如果 setting.yml 文件里字段 "enableWebsocket" 的值为 "true" 则需要将 "/" 换成 "/ws", 否则将接收不到消息.
app = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={BotQQ}")


memberSetuNet={}         #每个群每个成员要的网络setu计数（限制每人五张）
memberPicCount={}           #每个群成员要setu/real的次数
group_repeat={}             #每个群判断是否复读的dict
group_repeat_switch={}      #每个群的复读开关
timeDisable={}              #关闭setu开关的时间

localtime = time.localtime(time.time())
day_set=localtime.tm_mday

setuCount=0                             #网络setu编号
count=0                                 #setu保存编号
bizhiCount=0                            #网络壁纸编号
dragonId=[]                             #龙王id（可能有多个）
dragon={}                               #各群今日是否已宣布龙王
groupR18={}                             #各群组r18开关
management={}                           #拥有管理权限的用户id
searchCount=0                           #搜图编号
city=[]                                 #全国城市（地区）列表

n_time = datetime.datetime.now()    #目前时间
start_time = 0    #程序启动时间
d_time = datetime.datetime.strptime(str(datetime.datetime.now().date())+'23:00', '%Y-%m-%d%H:%M')   #龙王宣布时间

setuForbidden=[753400372,757627813]         #禁止要setu的群
realForbidden=[753400372,757627813]         #禁止要real的群
bizhiForbidden=[753400372,757627813]        #禁止要bizhi的群
forbiddenCount={}                           #禁止要setu后要setu的次数

reply_word=["啧啧啧","确实","giao","？？？","???","芜湖","是谁打断了复读？","是谁打断了复读?","老复读机了","就这","就这？","就这?"]     #复读关键词
non_reply=["setu","bizhi","","别老摸了，给爷冲！","real","几点了","几点啦","几点啦?","几点了?","冲？","今天我冲不冲？"]      #不复读关键词
setuCallText=["[Image::A3C91AFE-8834-1A67-DA08-899742AEA4E5]","[Image::A0FE77EE-1F89-BE0E-8E2D-62BCD1CAB312]","[Image::04923170-2ACB-5E94-ECCD-953F46E6CAB9]","[Image::3FFFE3B5-2E5F-7307-31A4-2C7FFD2F395F]","[Image::8A3450C7-0A98-4E81-FA24-4A0342198221]","setu","车车","开车","来点色图","来点儿车车"]
searchCallText=["search","搜图"]
timeCallText=["几点啦","几点了","几点啦？","几点了？"]
setuBot=[1702485633,1816899243,656162369,1553136451,3371686746,1823535226,3028799143,1739014771,2498853789]
setuGroup=[]
repeatBot=[2858306369]
MemberList={}





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

    with open(dragonDist,"r") as f:
        today=datetime.datetime.now().strftime("%Y-%m-%d")
        text = f.readline().strip()
        print(text,today)
        if not text==str(today):
            return
        while 1:
            text = f.readline().strip()
            if not text:
                break
            groupid,memberid,count=text.split(":")
            groupid=int(groupid)
            memberid=int(memberid)
            memberPicCount[groupid][memberid]=int(count)

@app.receiver("FriendMessage")
async def event_gm(app: Mirai, friend: Friend, message:MessageChain):
    print("friend Message")
    if friend.id==HostQQ:
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
    groupId=member.group.id
    print("来自群%s("%getSetting(groupId,"groupName"),groupId,")中成员%s("%qq2name(MemberList[groupId],sender),sender,")的消息:",message.toString(),sep='')
    if message.hasComponent(Image) and getSearchReady(groupId,sender):
        await app.sendGroupMessage(group,[
            At(target=sender),
            Plain(text="正在搜索请稍后呐~没反应了可能就是卡了呐~多等等呐~")
        ])
    Msg= await Process(message,groupId,sender)
    if Msg=="noneReply":
        pass
    else:
        msg = await app.sendGroupMessage(group,Msg)
        if getSetting(groupId,"r18"):
            app.revokeMessage(msg)

if __name__ == "__main__":
    app.run()