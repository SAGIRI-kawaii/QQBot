#coding=utf-8
from mirai import Mirai, Plain, MessageChain, Friend, Image, Group, protocol, Member, At, Face, JsonMessage
from variable import *
from function import *
import datetime
import re
import requests
import json
from VGG16 import predictImage

adminConfig=["repeat","setu","bizhi","real","speakMode","search"]
adminCheck=["group","speakMode","countLimit","setu","bizhi","real","r18","search"]
hostConfig=["countLimit","r18","switch"]
settingCode={"Disable":0,"Enable":1,"on":1,"off":0,"Local":1,"Net":0,"normal":"normal","zuanLow":"zuanLow","zuanHigh":"zuanHigh","rainbow":"rainbow","chat":"chat","online":"online","offline":"offline"}
sleepMuteCallText=["精致睡眠","晚安","晚安，精致睡眠"]
muteAllCallText=["万籁俱寂"]
unmuteAllCallText=["春回大地","万物复苏"]
blackList=[2518357362]

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
                    if change.isnumeric():
                        updateSetting(groupId,config,change)
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

# Wiki语句处理
def wikiProcess(groupId,sender,messageText):
    firstLevelDirectory=["function","management"]
    secondFLevelDirectory=["img","weather","yxh","blhx","ask","translate","speakMode","mute"]
    secondMLevelDirectory=["setting","info"]
    finalFLevelDirectory={"setu":wikiSetu,"real":wikiReal,"bizhi":wikiBizhi,"search":wikiSearch,"predict":wikiPredict,"weather":wikiWeather,"yxh":wikiYxh,"blhx":wikiBlhx,"ask":wikiAsk,"translate":wikiTranslate,"speakMode":wikiSpeakMode,"mute":wikiMute,"linux":wikiLinux,"quotes":wikiQuotes} 
    finalSLevelDirectory={"setuSetting":setuSetting,"r18Setting":r18Setting,"realSetting":realSetting,"bizhiSetting":bizhiSetting,"searchSetting":searchSetting,"countLimitSetting":countLimitSetting,"limitSetting":limitSetting,"blacklistSetting":blacklistSetting,"repeatSetting":repeatSetting,"speakModeSetting":speakModeSetting}
    finalILevelDirectory={"repeatInfo":repeatInfo,"setuLocalInfo":setuLocalInfo,"bizhiLocalInfo":bizhiLocalInfo,"countLimitInfo":countLimitInfo,"setuInfo":setuInfo,"bizhiInfo":bizhiInfo,"realInfo":realInfo,"r18Info":r18Info,"speakModeInfo":speakModeInfo,"switchInfo":switchInfo,"allInfo":allInfo,"sysInfo":sysInfo,"groupInfo":groupInfo}
    print(messageText)
    if messageText.replace("[At::target=%i] "%BotQQ,"")=="wiki" or messageText.replace("[At::target=%i] "%BotQQ,"")=="wiki:wiki":
        return [
            At(target=sender),
            Plain(text="Wiki 下属目录：\n"),
            Plain(text="1.function\n"),
            Plain(text="2.management\n"),
            Plain(text="3.acknowledgement\n"),
            Plain(text="4.requirements\n"),
            Plain(text="使用方法：@bot wiki:name\n"),
            Plain(text="如：@bot wiki:function\n")
        ]
    elif messageText.replace("[At::target=%i] wiki:"%BotQQ,"")=="function":
        nextMenu=messageText.replace("[At::target=%i] wiki:"%BotQQ,"")
        return [
            At(target=sender),
            Plain(text="function 下属目录：\n"),
            Plain(text="1.img(图片功能)\n"),
            Plain(text="2.development(开发相关功能)\n"),
            Plain(text="3.weather(天气功能)\n"),
            Plain(text="4.yxh(营销号生成器功能)\n"),
            Plain(text="5.blhx(blhxWiki查询功能)\n"),
            Plain(text="6.ask(问我问题给出网址解答)\n"),
            Plain(text="7.translate(翻译)\n"),
            Plain(text="8.speakMode(不同回复模式)\n"),
            Plain(text="9.mute(有关禁言的功能)\n"),
            Plain(text="10.quotes(有关群语录)\n"),
            Plain(text="使用方法：@bot wiki:name(不用括号里的)\n"),
            Plain(text="如：@bot wiki:img\n")
        ]
    elif messageText.replace("[At::target=%i] wiki:"%BotQQ,"")=="img":
        return [
            At(target=sender),
            Plain(text="img 下属目录：\n"),
            Plain(text="1.setu(涩图功能)\n"),
            Plain(text="2.real(三次元涩图功能)\n"),
            Plain(text="3.bizhi(壁纸功能)\n"),
            Plain(text="4.search(搜图查询功能)\n"),
            Plain(text="5.predict(搜图查询功能)\n"),
            Plain(text="使用方法：@bot wiki:name(不用括号里的)\n"),
            Plain(text="如：@bot wiki:img\n")
        ]
    elif messageText.replace("[At::target=%i] wiki:"%BotQQ,"")=="development":
        return [
            At(target=sender),
            Plain(text="development 下属目录：\n"),
            Plain(text="1.linux(linux命令查询功能)\n"),
            Plain(text="使用方法：@bot wiki:name(不用括号里的)\n"),
            Plain(text="如：@bot wiki:linux\n")
        ]
    elif messageText.replace("[At::target=%i] wiki:"%BotQQ,"")=="management":
        return [
            At(target=sender),
            Plain(text="management 下属目录：\n"),
            Plain(text="1.setting(设置)\n"),
            Plain(text="2.info(查询)\n"),
            Plain(text="3.wiki(使用方法(开始套娃))\n"),
            Plain(text="使用方法：@bot wiki:name(不用括号里的)\n"),
            Plain(text="如：@bot wiki:setting\n")
        ]
    elif messageText.replace("[At::target=%i] wiki:"%BotQQ,"")=="setting":
        return [
            At(target=sender),
            Plain(text="setting 下属目录：\n"),
            Plain(text="1.imgSetting(图片功能设置)\n"),
            Plain(text="2.blacklist(添加黑名单)\n"),
            Plain(text="3.repeatSetting(复读设置)\n"),
            Plain(text="4.speakModeSetting(不同回复模式设置)\n"),
            Plain(text="使用方法：@bot wiki:name(不用括号里的)\n"),
            Plain(text="如：@bot wiki:imgSetting\n")
        ]
    elif messageText.replace("[At::target=%i] wiki:"%BotQQ,"")=="imgSetting":
        return [
            At(target=sender),
            Plain(text="imgSetting 下属目录：\n"),
            Plain(text="1.setuSetting(涩图功能设置)\n"),
            Plain(text="2.realSetting(三次元涩图功能设置)\n"),
            Plain(text="3.bizhiSetting(壁纸功能设置)\n"),
            Plain(text="4.r18Setting(R18设置)\n"),
            Plain(text="5.searchSetting(搜图功能设置)\n"),
            Plain(text="6.countLimitSetting(限制要图次数(pis/m)功能开关设置)\n"),
            Plain(text="7.limitSetting(限制要图次数(pis/m)功能设置)\n"),
            Plain(text="使用方法：@bot wiki:name(不用括号里的)\n"),
            Plain(text="如：@bot wiki:setuSetting\n")
        ]
    elif messageText.replace("[At::target=%i] wiki:"%BotQQ,"")=="info":
        return [
            At(target=sender),
            Plain(text="info 下属目录：\n"),
            Plain(text="1.allInfo(全部信息)\n"),
            Plain(text="2.groupInfo(群组设置等信息)\n"),
            Plain(text="3.sysInfo(系统信息)\n"),
            Plain(text="4.imgInfo(图片功能设置信息)\n"),
            Plain(text="5.repeatInfo(复读功能设置信息)\n"),
            Plain(text="6.speakModeInfo(聊天模式设置信息)\n"),
            Plain(text="7.switchInfo(机器人开关信息)\n"),
            Plain(text="使用方法：@bot wiki:name(不用括号里的)\n"),
            Plain(text="如：@bot wiki:all\n")
        ]
    elif messageText.replace("[At::target=%i] wiki:"%BotQQ,"")=="imgInfo":
        return [
            At(target=sender),
            Plain(text="imgInfo 下属目录：\n"),
            Plain(text="1.setuInfo(setu设置信息)\n"),
            Plain(text="2.realInfo(real设置信息)\n"),
            Plain(text="3.r18Info(r18设置信息)\n"),
            Plain(text="4.bizhiInfo(bizhi设置信息)\n"),
            Plain(text="5.searchInfo(搜图功能设置信息)\n"),
            Plain(text="6.predictInfo(预测图片功能设置信息)\n"),
            Plain(text="7.setuLocalInfo(setu库位置设置信息)\n"),
            Plain(text="8.bizhiLocalInfo(bizhi库位置设置信息)\n"),
            Plain(text="9.countLimitInfo(每分钟要图限制设置信息)\n"),
            Plain(text="10.limitInfo(每分钟要图数量限制设置信息)\n"),
            Plain(text="使用方法：@bot wiki:name(不用括号里的)\n"),
            Plain(text="如：@bot wiki:setuInfo\n")
        ]
    elif messageText.replace("[At::target=%i] wiki:"%BotQQ,"")=="acknowledgement":
        nextMenu=messageText.replace("[At::target=%i] wiki:"%BotQQ,"")
        return [
            At(target=sender),
            Plain(text="致谢名单:\n"),
            Plain(text="1.Mirai,一个高效率机器人库\n"),
            Plain(text="2.mirai-api-http,提供 http 接口进行接入\n"),
            Plain(text="3.python-mirai,Mirai的Python接口\n")
        ]
    elif messageText.replace("[At::target=%i] wiki:"%BotQQ,"")=="requirements":
        nextMenu=messageText.replace("[At::target=%i] wiki:"%BotQQ,"")
        answer=requirements
        answer.insert(0,At(target=sender))
        return answer
    elif messageText.replace("[At::target=%i] wiki:"%BotQQ,"") in finalFLevelDirectory:
        finalKey=messageText.replace("[At::target=%i] wiki:"%BotQQ,"")
        answer=finalFLevelDirectory[finalKey]
        answer.insert(0,At(target=sender))
        return answer
    elif messageText.replace("[At::target=%i] wiki:"%BotQQ,"") in finalSLevelDirectory:
        finalKey=messageText.replace("[At::target=%i] wiki:"%BotQQ,"")
        answer=finalSLevelDirectory[finalKey]
        answer.insert(0,At(target=sender))
        return answer
    elif messageText.replace("[At::target=%i] wiki:"%BotQQ,"") in finalILevelDirectory:
        finalKey=messageText.replace("[At::target=%i] wiki:"%BotQQ,"")
        answer=finalILevelDirectory[finalKey]
        answer.insert(0,At(target=sender))
        return answer
    else:
        return [
            At(target=sender),
            Plain(text="仔细看看是不是输入错误了呐~")
        ]

# func语句处理
def funcProcess(groupId,sender,func,content,target):
    if sender in getAdmin(groupId):
        if func=="addQuote":
            # print(groupId,target,content,func)
            try:
                target=re.findall(r'\[At::target=(.*?)\]',target,re.S)[0]
            except:
                pass
            return addCelebrityQuotes(groupId,int(target),content,"text")
    else:
        return [
            At(target=sender),
            Plain(text="只有主人和管理员才能添加群语录哦~")
        ]

# 语句处理
async def Process(message,groupId,sender,memberList):

    responseCalled=getData("responseCalled")
    responseCalled+=1                               #responseCalled计数
    updateData(responseCalled,"response")

    # message预处理
    messageText=message.toString()

    # setu功能
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
                if getSetting(groupId,"imgLightning") and randomJudge():
                    record("setu","lightning",sender,groupId,False,"img")
                    return "lightningPic"
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

    # real功能
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
            if getSetting(groupId,"imgLightning") and randomJudge():
                record("real","lightning",sender,groupId,False,"img")
                return "lightningPic"
            dist=randomPic(realDist)
            record("real",dist,sender,groupId,True,"img")
            print("本地real图片地址：",dist)
            return [Image.fromFileSystem(dist)]  
            
    # bizhi功能
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
    
    # 批量pic功能
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

    # 搜图功能
    elif messageText in searchCallText:
        if not getSetting(groupId,"search"):
            return [
                At(target=sender),
                Plain(text="搜图功能关闭了呐~想要打开就联系机器人管理员吧~")
            ]
        setSearchReady(groupId,sender,True)
        return [
            At(target=sender),
            Plain(text="请发送要搜索的图片呐~")
        ]
    elif message.hasComponent(Image) and getSetting(groupId,"search") and getSearchReady(groupId,sender):
        print("searching")
        img = message.getFirstComponent(Image)
        return searchImage(groupId,sender,img)
        
    # 图片预测功能
    elif messageText=="这张图里是什么":
        if not getSetting(groupId,"imgPredict"):
            return [
                At(target=sender),
                Plain(text="图片预测功能关闭了呐~想要打开就联系机器人管理员吧~")
            ]
        setPredictReady(groupId,sender,True)
        return [
            At(target=sender),
            Plain(text="请发送要预测的图片呐(推荐真实图片呐)~")
        ]
    elif message.hasComponent(Image) and getSetting(groupId,"imgPredict") and getPredictReady(groupId,sender):
        print("predicting")
        img = message.getFirstComponent(Image)
        return predictImage(groupId,sender,img)
        
    # 黄图评价功能
    elif messageText=="这张图涩吗":
        if not getSetting(groupId,"yellowPredict"):
            return [
                At(target=sender),
                Plain(text="图片涩度评价功能关闭了呐~想要打开就联系机器人管理员吧~")
            ]
        setYellowPredictReady(groupId,sender,True)
        return [
            At(target=sender),
            Plain(text="请发送要预测的图片呐~")
        ]
    elif message.hasComponent(Image) and getSetting(groupId,"yellowPredict") and getYellowPredictReady(groupId,sender):
        print("judging")
        img = message.getFirstComponent(Image)
        return judgeImageYellow(groupId,sender,img.url)
    
    # 笑话功能
    elif "来点" in messageText and "笑话" in messageText:
        name=re.findall(r'来点(.*?)笑话',messageText,re.S)
        if name==[]:
            return "noneReply"
        else:
            record("joke","none",sender,groupId,True,"function")
            return getJoke(name[0])

    # 群语录功能 celebrityQuotes
    elif messageText=="群语录":
        return getCelebrityQuotes(groupId,memberList)

    # 获取时间功能（可选背景）
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

    # 选择表盘（获取时间功能）
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

    # 天气查询功能
    elif "[At::target=%i] 天气"%BotQQ in messageText:
        weatherCalled=getData("weatherCalled")
        weatherCalled+=1
        updateData(weatherCalled,"weather")
        return getWeather(message,sender)

    # 碧蓝航线wiki查询功能
    elif "[At::target=%i] blhx："%BotQQ in messageText:
        name=messageText[28:]
        return blhxWiki(sender,name)
        
    # 营销号生成器
    elif "[At::target=%i] 营销号"%BotQQ in messageText:
        _,somebody,something,other_word=messageText.split('、')
        # print(something,somebody,other_word)
        return yingxiaohao(somebody,something,other_word)

    # 问你点儿事儿
    elif "[At::target=%i] 问你点儿事儿："%BotQQ in message.toString():
        question=message.toString()[30:]
        question=parse.quote(question)
        return askSth(sender,question)

    #linux命令查询功能
    elif "[At::target=%i] linux"%BotQQ in messageText:
        if '：' in messageText:
            messageText=messageText.replace('：',':')
        command=messageText.replace("[At::target=%i] linux:"%BotQQ,"")
        print("get linux:%s"%command)
        text=getLinuxExplanation(command)
        if text=="error!no command!":
            return [
                At(target=sender),
                Plain(text="未搜索到命令%s!请检查拼写！"%command)
            ]
        else:
            return [
                At(target=sender),
                Plain(text="%s:%s"%(command,text))
            ]

    # 翻译功能
    elif "[At::target=%i] "%BotQQ in messageText and "用" in messageText and "怎么说" in messageText:
        supportLanguage={"中文":"zh","英文":"en","日文":"jp","韩文":"kr","法文":"fr","西班牙文":"es","意大利文":"it","德文":"de","土耳其文":"tr","俄文":"ru","葡萄牙文":"pt","越南文":"vi","印度尼西亚文":"id","马来西亚文":"ms","泰文":"th"}
        tp=re.findall(r'\[At::target=762802224\] (.*?)用(.*?)怎么说',messageText,re.S)[0]
        text=tp[0]
        target=tp[1]
        print("text:%s,target:%s"%(text,target))
        source=textDetect(text.encode("utf-8"))
        if target not in supportLanguage.keys():
            sL=""
            for i in supportLanguage.keys():
                sL+=i
                sL+='、'
            return [
                At(target=sender),
                Plain(text="目前只支持翻译到%s哦~\n要全字匹配哦~看看有没有打错呐~\n翻译格式：text用（目标语言）怎么说"%sL)
            ]
        target=supportLanguage[target]
        # print(target)
        return translate(groupId,sender,text,source,target)

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
    
    # 获取信息处理
    elif "[At::target=%i] info."%BotQQ in messageText:
        command=messageText[16:]
        # try:
        print(command)
        info,check=command.split('.')
        print(info,'-->'," info:",check)
        return infoProcess(groupId,sender,check)

    # wiki处理
    elif "[At::target=%i] wiki"%BotQQ in messageText:
        if '：' in messageText:
            messageText=messageText.replace('：',':')
            print(messageText)
        print("get wiki:%s"%messageText.replace("[At::target=%i] wiki"%BotQQ,""))
        return wikiProcess(groupId,sender,messageText)
        
    # 添加群语录处理 @bot func.addQuote.content.target
    elif "[At::target=%i] func.addQuote."%BotQQ in messageText:
        try:
            _,func,content,target=messageText.split(".")
            return funcProcess(groupId,sender,func,content,target)
        except Exception:
            pass

    # 添加管理员处理
    elif "[At::target=%i] addAdmin"%BotQQ in messageText:
        target=int(re.findall(r'At::target=(.*?)]',message.toString()[19:],re.S)[0])
        print("add admin:%d in group %d"%(target,groupId))
        return addAdmin(groupId,target)


    # 回复@bot（normal,zuanLow,zuanHigh,rainbow）
    elif "[At::target=%i]"%BotQQ in messageText:
        if messageText.replace("[At::target=%d] "%BotQQ,"") in sleepMuteCallText and sender not in getAdmin(groupId):
            return "goodNight"
        elif messageText.replace("[At::target=%d] "%BotQQ,"") in muteAllCallText and sender==HostQQ:
            return "muteAll"
        elif messageText.replace("[At::target=%d] "%BotQQ,"") in unmuteAllCallText and sender==HostQQ:
            return "unmuteAll"
        elif sender == HostQQ and not getSetting(groupId,"speakMode")=="chat":
            return [
                At(target=sender),
                Plain(text="诶嘿嘿，老公@我是要找人家玩嘛~纱雾这就来找你玩哟~")
            ]
        else:
            mode_now=getSetting(groupId,"speakMode")
            if not mode_now=="normal":
                if mode_now=="zuanHigh":
                    text=requests.get(zuanHighSrc).text
                    record("zuanHigh","none",sender,groupId,True,"function")
                elif mode_now=="zuanLow":
                    text=requests.get(zuanLowSrc).text
                    record("zuanLow","none",sender,groupId,True,"function")
                elif mode_now=="rainbow":
                    text=requests.get(rainbowSrc).text
                    record("rainbow","none",sender,groupId,True,"function")
                elif mode_now=="chat":
                    if not len(messageText.replace("[At::target=%i] "%BotQQ,""))==0:
                        text=getChatText(groupId,sender,str(messageText.replace("[At::target=%i] "%BotQQ,"")))
                        record("chat","none",sender,groupId,True,"function")
                    else:
                        return "noneReply"
                return [
                    At(target=sender),
                    Plain(text=text)
                ]

    return "noneReply"