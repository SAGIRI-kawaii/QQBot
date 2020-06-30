from mirai import Mirai, Plain, MessageChain, Friend, Image, Group, protocol, Member, At, Face, JsonMessage
# from variable import *
from function import *
import datetime
import re
import requests

adminConfig=["repeat","setu","bizhi","real"]
adminCheck=["group","speakMode","countLimit","setu","bizhi","real","r18"]
hostConfig=["countLimit","r18","speakMode","switch"]
settingCode={"Disable":0,"Enable":1,"on":1,"off":0,"Local":1,"Net":0,"normal":"normal","zuanLow":"zuanLow","zuanHigh":"zuanHigh","rainbow":"rainbow","online":"online","offline":"offline"}

# setting语句处理
def settingProcess(groupId,sender,config,change):
    if sender in getAdmin(groupId):
        if configChangeJudge(config,change):
            if config in adminConfig:
                updateSetting(groupId,config,settingCode[change])
                record("setting:%s set to %s"%(config,change),"none",sender,groupId,True,"function")
            else:
                if not sender==HostQQ:
                    record("setting:Insufficient permissions","none",sender,groupId,False,"function")
                    return [
                        At(target=sender),
                        Plain(text="Insufficient permissions!")
                    ]
                else:
                    updateSetting(groupId,config,settingCode[change])
                    record("setting:%s set to %s"%(config,change),"none",sender,groupId,True,"function")
            if (config=="real" or config=="setu") and change=="Enable" and (getSetting(groupId,"setu") and getSetting(groupId,"real")):
                updateSetting(groupId,"forbiddenCount",0)
        else:
            record("setting:command error","none",sender,groupId,False,"function")
            return [
                At(target=sender),
                Plain("Command error!")
            ]
        return [
            Plain(text="group:%d %s set to %s"%(groupId,config,change))
        ]
    else:
        return [
            At(target=sender),
            Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
        ]

# info语句处理
def infoProcess(groupId,sender,check):
    if sender in getAdmin(groupId):
        if infoCheckJudge(check):
            if check in adminCheck:
                return showSetting(groupId,sender,check)
            else:
                if not sender==HostQQ:
                    record("setting:Insufficient permissions","none",sender,groupId,False,"function")
                    return [
                        At(target=sender),
                        Plain(text="Insufficient permissions!")
                    ]
                else:
                    return showSetting(groupId,sender,check)
        else:
            record("setting:command error","none",sender,groupId,False,"function")
            return [
                At(target=sender),
                Plain("Command error!")
            ]
    else:
        return [
            At(target=sender),
            Plain(text="爬爬爬，你没有管理权限！离人家远一点啦！死变态！")
        ]

#语句处理
async def Process(message,groupId,sender):

    responseCalled=getData("responseCalled")
    responseCalled+=1                               #responseCalled计数
    updateData(responseCalled,"response")

    #message预处理
    messageText=message.toString()

    #setu功能
    if messageText in setuCallText:
        setuCalled=getData("setuCalled")
        setuCalled+=1                               #setuCalled计数  
        updateData(setuCalled,"setu")
        if not getSetting(groupId,"setu"):                    #本群禁止要setu
            forbiddenCount=getSetting(groupId,"forbiddenCount")
            forbiddenCount+=1
            updateSetting(groupId,"forbiddenCount",forbiddenCount)
            record("setu","none",sender,groupId,False,"img")
            if forbiddenCount<=3:
                return [Plain(text="我们是正规群呐，不搞那一套哦，想看去辣种群看哟~")]
            elif forbiddenCount<=6:
                return [Plain(text="Kora!都说了是正规群啦！怎么老要这种东西呀，真是够讨厌的呢！再问我就生气啦！")]
            elif forbiddenCount<=9:
                return [Plain(text="爬爬爬，天天脑子里都是些什么啊，滚呐！爷生气啦！打你哦！")]
            else:
                return [Image.fromFileSystem(angryDist)]
        else:
            if sender in blackList:                     #发送人在黑名单中
                record("setu","none",sender,groupId,False,"img")
                return [
                    At(target=sender),
                    Plain(text="要你🐎？大胆妖孽！我一眼就看出来你不是人！大威天龙！世尊地藏！般若诸佛！般若巴麻空！")
                ]
            
            if getSetting(groupId,"countLimit"):                   #如果有每分钟调用次数限制
                if not getMemberPicStatus(groupId,sender):
                    record("setu","none",sender,groupId,False,"img")
                    return [Plain(text="你已达到限制，每分钟最多只能要%d张setu/real哦~\n歇会儿再来吧！"%getSetting(groupId,"limit"))]
            
            if getSetting(groupId,"setuLocal"):           #是否为本地库
                if getSetting(groupId,"r18"):
                    dist=randomPic(setu18Dist)
                    record("setu18",dist,sender,groupId,True,"img")
                else:
                    dist=randomPic(setuDist)
                    record("setu",dist,sender,groupId,True,"img")
                print("本地setu图片地址：",dist)
                return [Image.fromFileSystem(dist)]  
            else:
                pass                                    #因api变动不稳定，暂时不进行编写     

    #real功能
    elif messageText=="real":
        realCalled=getData("realCalled")
        realCalled+=1                                   #realCalled计数  
        updateData(realCalled,"real")

        if not getSetting(groupId,"real"):                    #本群禁止要real
            forbiddenCount=getSetting(groupId,"forbiddenCount")
            forbiddenCount+=1
            updateSetting(groupId,"forbiddenCount",forbiddenCount)
            record("real","none",sender,groupId,False,"img")
            if forbiddenCount<=3:
                return [Plain(text="我们是正规群呐，不搞那一套哦，想看去辣种群看哟~")]
            elif forbiddenCount<=6:
                return [Plain(text="Kora!都说了是正规群啦！怎么老要这种东西呀，真是够讨厌的呢！再问我就生气啦！")]
            elif forbiddenCount<=9:
                return [Plain(text="爬爬爬，天天脑子里都是些什么啊，滚呐！爷生气啦！打你哦！")]
            else:
                return [Image.fromFileSystem(angryDist)]
        else:
            if sender in blackList:                     #发送人在黑名单中
                record("real",dist,sender,groupId,False,"img")
                return [Plain(text="要要要你🐎？大胆妖孽！我一眼就看出来你不是人！大威天龙！世尊地藏！般若诸佛！般若巴麻空！")]
            
            if getSetting(groupId,"countLimit"):                   #如果有每分钟调用次数限制
                if not getMemberPicStatus(groupId,sender):
                    record("real","none",sender,groupId,False,"img")
                    return [Plain(text="你已达到限制，每分钟最多只能要%d张setu/real哦~\n歇会儿再来吧！"%getSetting(groupId,"limit"))]

            dist=randomPic(realDist)
            record("real",dist,sender,groupId,True,"img")
            print("本地real图片地址：",dist)
            return [Image.fromFileSystem(dist)]  
            
    #bizhi功能
    elif messageText=="bizhi":
        bizhiCalled=getData("bizhiCalled")
        bizhiCalled+=1                                  #bizhiCalled计数  
        updateData(bizhiCalled,"bizhi")

        if not getSetting(groupId,"bizhi"):                    #本群禁止要bizhi
            record("bizhi","none",sender,groupId,False,"img")
            return [Plain(text="bizhi功能被关闭了呐>^<,想打开的话联系下管理员呐~")]
        else:
            if sender in blackList:                     #发送人在黑名单中
                record("bizhi",dist,sender,groupId,False,"img")
                return [Plain(text="要要要你🐎？大胆妖孽！我一眼就看出来你不是人！大威天龙！世尊地藏！般若诸佛！般若巴麻空！")]
        dist=randomPic(bizhiDist)
        print("本地bizhi图片地址：",dist)
        record("bizhi",dist,sender,groupId,True,"img")
        return [Image.fromFileSystem(dist)]  
    
    #批量pic功能
    elif messageText[:5]=="setu*" or messageText[:5]=="real*":
        aim=messageText[:4]
        if aim=="setu":
            aimDist=setuDist
        else:
            aimDist=realDist
        if not ((getSetting(groupId,"setu") and aim=="setu") or (getSetting(groupId,"real") and aim=="real")):                    #本群禁止要setu
            forbiddenCount=getSetting(groupId,"forbiddenCount")
            forbiddenCount+=1
            updateSetting(groupId,"forbiddenCount",forbiddenCount)
            record(messageText,"none",sender,groupId,False,"img")
            if forbiddenCount<=3:
                return [Plain(text="我们是正规群呐，不搞那一套哦，想看去辣种群看哟~")]
            elif forbiddenCount<=6:
                return [Plain(text="Kora!都说了是正规群啦！怎么老要这种东西呀，真是够讨厌的呢！再问我就生气啦！")]
            elif forbiddenCount<=9:
                return [Plain(text="爬爬爬，天天脑子里都是些什么玩意儿，滚呐！爷生气啦！打你哦！")]
            else:
                return [Image.fromFileSystem(angryDist)]
        else:
            try:
                num=int(message.toString()[5:])
                if aim=="setu":
                    setuCalled=getData("setuCalled")
                    setuCalled+=num
                    updateData(setuCalled,"setu")
                else:
                    realCalled=getData("realCalled")
                    realCalled+=num
                    updateData(realCalled,"real")
                if sender in getAdmin(groupId):
                    if sender == HostQQ or num <= 5:
                        picMsg=[]
                        for i in range(num):
                            # if setting[groupId]["setuLocal"]:
                            dist=randomPic(aimDist)
                            picMsg.append(Image.fromFileSystem(dist))
                            record("%s*%d"%(aim,num),dist,sender,groupId,True,"img")
                            # else:
                                # pass
                        return picMsg
                    else:
                        record("%s*%d"%(aim,num),dist,sender,groupId,False,"img")
                        return [Plain(text="管理最多也只能要5张呐~我可不会被轻易玩儿坏呢！！！！")]
                elif num <= 5:
                    record("%s*%d"%(aim,num),"none",sender,groupId,False,"img")
                    return [Plain(text="只有主人和管理员可以使用%s*num命令哦~你没有权限的呐~"%aim)]
                else:
                    record("%s*%d"%(aim,num),"none",sender,groupId,False,"img")
                    return [Plain(text="老色批，要那么多，给你🐎一拳，爬！")]
            except ValueError:
                return [Plain(text="命令错误！%s*后必须跟数字！"%aim)]

    #搜图功能
    elif messageText in searchCallText:
        setSearchReady(groupId,sender,True)
        return [At(target=sender),Plain(text="请发送要搜索的图片呐~")]
    elif message.hasComponent(Image) and getSearchReady(groupId,sender):
        print("searching")
        img = message.getFirstComponent(Image)
        return searchImage(groupId,sender,img)
    
    #获取时间功能（可选背景）
    elif messageText in timeCallText:
        clockCalled=getData("clockCalled")
        clockCalled+=1
        updateData(clockCalled,"clock")
        if getClockChoice(groupId,sender)=="none":
            clockMessage=[
                At(target=sender),
                Plain(text="你还没有选择表盘哦~快来选择一个吧~\n"),
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
        else:
            t = datetime.datetime.now()    #目前时间
            t = t.strftime("%H:%M")
            t = t.replace(":","")
            dist=timeDist+str(getClockChoice(groupId,sender))+"/%s.png"%t
            return [Image.fromFileSystem(dist)]

    #选择表盘（获取时间功能）
    
    elif messageText[:4]=="选择表盘":
        if messageText=="选择表盘":
            return showClock(sender)
        else:
            code=messageText[4:]
            if code.isdigit() and int(code)<=int(getData("dialsCount")):
                recordClock(groupId,sender,int(code))
                return[
                    Plain(text="已经选择了表盘%s呢!\n现在可以问我时间啦~"%code)
                ]
            else:
                return [
                    Plain(text="看中后直接发送选择表盘+序号即可哦~\n"),
                    Plain(text="再检查下有没有输错呢~\n")
                ]

    #天气查询功能
    elif "[At::target=%i] 天气"%BotQQ in messageText:
        weatherCalled=getData("weatherCalled")
        weatherCalled+=1
        updateData(weatherCalled,"weather")
        return getWeather(message,sender)

    #碧蓝航线wiki查询功能
    elif "[At::target=%i] blhx："%BotQQ in messageText:
        name=messageText[28:]
        return blhxWiki(sender,name)
        
    #营销号生成器
    elif "[At::target=%i] 营销号"%BotQQ in messageText:
        _,somebody,something,other_word=messageText.split('、')
        # print(something,somebody,other_word)
        return [
            Plain(text=yingxiaohao(somebody,something,other_word))
        ]

    #设置处理
    elif "[At::target=%i] setting."%BotQQ in messageText:
        command=messageText[16:]
        try:
            print(command)
            name,config,change=command.split('.')
            print(name,'-->'," config:",config,"set to",change)
            return settingProcess(groupId,sender,config,change)
        except ValueError:
            return [
                At(target=sender),
                Plain(text="Command error! Use the '@bot command' command to query the commands you can use!")
            ]
    
    #获取信息处理
    elif "[At::target=%i] info."%BotQQ in messageText:
        command=messageText[16:]
        # try:
        print(command)
        info,check=command.split('.')
        print(info,'-->'," info:",check)
        return infoProcess(groupId,sender,check)
        # except:
        #     return [
        #         At(target=sender),
        #         Plain(text="Command error! Use the '@bot command' command to query the commands you can use!")
        #     ]

    #回复@bot（normal,zuanLow,zuanHigh,rainbow）
    elif "[At::target=%i]"%BotQQ in messageText:
        if sender == HostQQ:
            return [
                Plain(text="诶嘿嘿，老公@我是要找人家玩嘛~纱雾这就来找你玩哟~")
            ]
        else:
            mode_now=getSetting(groupId,"speakMode")
            if not mode_now=="normal":
                # text="@我是要干什么呢？可以通过 @我+menu/command/info/mode 的方式查询信息哟~"
                if mode_now=="zuanHigh":
                    text=requests.get(zuanHighSrc).text
                    record("zuanHigh","none",sender,groupId,True,"function")
                elif mode_now=="zuanLow":
                    text=requests.get(zuanLowSrc).text
                    record("zuanLow","none",sender,groupId,True,"function")
                elif mode_now=="rainbow":
                    text=requests.get(rainbowSrc).text
                    record("rainbow","none",sender,groupId,True,"function")
                return [
                    At(target=sender),
                    Plain(text=text)
                ]

    return "noneReply"