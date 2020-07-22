from PIL import Image
import imagehash
import os
import pymysql

def img(img_path):
    """
    图片哈希（类似：4f999cc90979704c）
    :param img_path: 图片路径
    :return: <class 'imagehash.ImageHash'>
    """
    img1 = Image.open(img_path)
    res = imagehash.dhash(img1)
    print(res)
    return res

def hamm_img(res1, res2):
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

def walkFileGetHash(path,pathClass="tribute"):
    """
    path:图库路径
    pathClass:图库类别，用于区分不同种类图库
    """
    conn = pymysql.connect(host="127.0.0.1", user="root", passwd="duyifan2004", db="qqbot", port=3306, charset="utf8")
    cur = conn.cursor()
    for root, dirs, files in os.walk(path):
        for f in files:
            print(os.path.join(root, f))
            try:
                sql = "insert into ImageHash (dir,imageHash,class) values ('%s','%s','%s')"%(pymysql.escape_string(os.path.join(root, f)),img(os.path.join(root, f)),pathClass)
                cur.execute(sql) 
                conn.commit()
            except Exception:
                pass
    conn.close()
    cur.close()


if __name__ == '__main__':
    path=""    # 图库路径
    walkFileGetHash(path) 