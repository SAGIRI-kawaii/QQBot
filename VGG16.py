# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import matplotlib.pyplot as plt
from function import setPredictReady,getData,updateData,record
from variable import *
from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input, decode_predictions
import numpy as np
from PIL import Image as IMG
from io import BytesIO
from mirai import Mirai, Plain, MessageChain, Friend, Image, Group, protocol, Member, At, Face, JsonMessage
import requests
import numpy as np

def percent(value):
    return '%.2f%%' % (value * 100)

# include_top=True，表示會載入完整的 VGG16 模型，包括加在最後3層的卷積層
# include_top=False，表示會載入 VGG16 的模型，不包括加在最後3層的卷積層，通常是取得 Features
# 若下載失敗，請先刪除 c:\<使用者>\.keras\models\vgg16_weights_tf_dim_ordering_tf_kernels.h5
def predictImage(groupId,sender,img):
    setPredictReady(groupId,sender,False)
    predictCount=getData("predictCount")
    print(predictCount)
    updateData(predictCount+1,"predict")
    dist="%s%s.jpg"%(predictDist,predictCount)
    img_content=requests.get(img.url).content
    image=IMG.open(BytesIO(img_content))
    image.save(dist)

    img_path=dist
    model = VGG16(weights='imagenet', include_top=True)

    # Input：要辨識的影像
    # img = image.load_img(img_path, target_size=(224, 224))
    x = np.array(IMG.open(dist).resize((224, 224)))
    # x = image.img_to_array(img) #转化为浮点型
    x = np.expand_dims(x, axis=0)#转化为张量size为(1, 224, 224, 3)
    x = preprocess_input(x)
    # 預測，取得features，維度為 (1,1000)
    features = model.predict(x)
    # 取得前五個最可能的類別及機率
    pred=decode_predictions(features, top=5)[0]
    #整理预测结果,value
    values = []
    bar_label = []
    for element in pred:
        values.append(element[2])
        bar_label.append(element[1])
    print(img_path)
    for i in range(5):
        print(bar_label[i],values[i])
    record("predict",dist,sender,groupId,True,"img")
    msg=[At(target=sender),Plain(text="\nPredict Result:")]
    for i in range(5):
        msg.append(Plain(text="\n%s:%2.2f%%"%(bar_label[i],values[i]*100)))
    record("predict",dist,sender,groupId,True,"img")
    return msg
    
