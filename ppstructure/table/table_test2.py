# -*- coding: utf-8 -*-
# @Time  : 2022/2/24 15:57
# @Author  : 呆呆
# @Email : 2821212670@qq.com
# @FileName  : table_test.py
# @Software  : PyCharm


import os
import time

import cv2
import numpy as np
import pandas as pd
import xlwt
import json

from paddleocr import PPStructure, draw_structure_result, save_structure_res

time1 = time.time()
table_engine = PPStructure(show_log=True)
from PIL import Image

# save_folder = './output/table'
# img_path = r'C:\Users\admin\Desktop\35.jpg'
img_path = r'C:\Users\admin\Desktop\image_file\39.jpg'

img = cv2.imread(img_path)
result = table_engine(img)


# print("result",result)
# save_structure_res(result, save_folder,os.path.basename(img_path).split('.')[0])
# for line in result:
#     line.pop('img')
#     # print(line)
#     print(line)

def json_excel(data):
    # 创建excel工作表
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet')
    # 写表头
    for index, val in enumerate(data[0].keys()):
        worksheet.write(0, index, label=val)

    # 写数据
    for row, list_item in enumerate(data):
        row += 1
        col = 0
        for key, value in list_item.items():
            worksheet.write(row, col, value)
            col += 1
    # 保存
    workbook.save('./数据.xls')


boxes, txts, scores = [], [], []

for region in result:
    if region['type'] == 'Table':
        pass
    else:
        for box, rec_res in zip(region['res'][0], region['res'][1]):
            boxes.append(np.array(box).reshape(-1, 2))
            txts.append(rec_res[0])
            scores.append(rec_res[1])
# print("rrr",txts)

# print("结果", txts[:15])
# print("截取：", txts[0])

re = txts[0]
# print("农村土地承包经营权证编码", re[re.find('3'):])
my_date = txts[:15]
# print("my_date", my_date)
print(my_date[0])
if "农村土地承包经营权证编码"in my_date[0]:  # 当联系电话为空的时候
    del my_date[0]
    # my_date.insert(11, '')
    my_date.insert(0, "农村土地承包经营权证编码:")
    my_date.insert(1, re[re.find('3'):])
    print("处理(电话为空)后", my_date)



if my_date[14] == "土地承包经营权证编码":  # 当联系电话为空的时候
    del my_date[14]
    del my_date[0]
    my_date.insert(11, '')
    my_date.insert(0, "农村土地承包经营权证编码:")
    my_date.insert(1, re[re.find('3'):])
    print("处理(电话为空)后", my_date)

if my_date[14].isdigit():  # 当联系电话有值的时候
    phone_number = my_date[14]
    del my_date[14]
    del my_date[0]
    my_date.insert(11, phone_number)
    my_date.insert(0, "农村土地承包经营权证编码:")
    my_date.insert(1, re[re.find('3'):])
    print("处理处理(电话有值)后后：", my_date)

print("处理后：", my_date)
new_date =my_date[:12]
# print(f'奇数位：{my_date[::2]}\n偶数位：{my_date[1::2]}')
for i in my_date:
    if i.isdecimal() and len(i) == 6:
        coding = i
        print("coding",coding)
    if i.isdecimal()and len(i) >= 11:
        phone_number2 = i

new_date = my_date[:12]
new_date.append("邮政编码")
new_date.append(coding)
new_date.append("联系电话")
new_date.append(phone_number2)
# my_res = dict(zip(my_date[::2], my_date[1::2]))
my_res = dict(zip(new_date[::2], new_date[1::2]))
print("my_res", my_res)
# my_res["邮政编码"] = coding
# my_res["联系电话"] = phone_number2
all_date = []
all_date.append(my_res)


print("all_date", all_date)
df = pd.DataFrame(all_date)

df.to_excel("info.xlsx",sheet_name='data',index=False)

# json_excel(all_date)


time2 = time.time()
print(time2 - time1)
font_path = '../doc/fonts/simfang.ttf'  # PaddleOCR下提供字体包
image = Image.open(img_path).convert('RGB')
im_show = draw_structure_result(image, result, font_path=font_path)
im_show = Image.fromarray(im_show)
im_show.show('result.jpg')
