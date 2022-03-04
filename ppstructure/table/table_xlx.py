# -*- coding: utf-8 -*-
# @Time  : 2022/2/25 13:35
# @Author  : 呆呆
# @Email : 2821212670@qq.com
# @FileName  : table_xlx.py
# @Software  : PyCharm
import asyncio
import os
import random
import time

import cv2
import numpy as np
import pandas as pd
import uvicorn
import xlwt
import json
from pydantic import BaseModel
from fastapi import FastAPI, BackgroundTasks, Request, Response
import uuid
from paddleocr import PPStructure, draw_structure_result, save_structure_res
from loguru import logger
import requests as requests

time1 = time.time()
table_engine = PPStructure(show_log=False)
from PIL import Image

save_dir = r"D:\python\PaddleOCR-release-2.4\ppstructure\table\\"

uuids: dict = {}


class Item(BaseModel):
    file_list: str


# save_folder = './output/table'
# img_path = r'C:\Users\admin\Desktop\35.jpg'

# print("result",result)
# save_structure_res(result, save_folder,os.path.basename(img_path).split('.')[0])
# for line in result:
#     line.pop('img')
#     # print(line)
#     print(line)
app = FastAPI(title='Hello world')


def generate_random_str(randomlength=16):
    """
    生成一个指定长度的随机字符串
    """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


def json_excel(data, xls_file):
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
    workbook.save(xls_file)


def image_ocr(file_list):
    all_date = []
    for i in file_list:
        print("i", i)
        # img_path = i
        img = cv2.imread(i)
        result = table_engine(img)
        boxes, txts, scores = [], [], []

        for region in result:
            if region['type'] == 'Table':
                pass
            else:
                for box, rec_res in zip(region['res'][0], region['res'][1]):
                    boxes.append(np.array(box).reshape(-1, 2))
                    txts.append(rec_res[0])
                    scores.append(rec_res[1])
        re = txts[0]
        my_date = txts[:15]
        if "农村土地承包经营权" in my_date[14]:  # 当联系电话为空的时候
            del my_date[14]
            del my_date[0]
            my_date.insert(11, '')
            my_date.insert(0, "农村土地承包经营权证编码:")
            my_date.insert(1, re[re.find('3'):])
        if my_date[14].isdigit():  # 当联系电话有值的时候
            phone_number = my_date[14]
            del my_date[14]
            del my_date[0]
            my_date.insert(11, phone_number)
            my_date.insert(0, "农村土地承包经营权证编码:")
            my_date.insert(1, re[re.find('3'):])

        phone_number2, coding = 0
        for i in my_date:
            if i.isdecimal() and len(i) == 6:
                coding = i
            if i.isdecimal():
                phone_number2 = i

        # print("处理后：", my_date)
        my_res = dict(zip(my_date[::2], my_date[1::2]))
        print("my_res", my_res)
        my_res["邮政编码"] = coding
        my_res["联系电话"] = phone_number2
        all_date.append(my_res)

    return all_date


def read_directory(directory_name):
    file_list = []
    for filename in os.listdir(directory_name):
        # print(filename)
        file_list.append(directory_name + "\\" + filename)
        # print(directory_name + "/" + filename)
    return file_list


async def process(file_list, xlsx_file, uid):
    tasks = [do_main(file_list, xlsx_file, uid)]
    logger.info("start processing")
    result = await asyncio.gather(*tasks)
    for i in result:
        logger.info(i)


async def do_main(file_list, xlsx_file, uid):
    try:
        all_date = image_ocr(file_list)
        df = pd.DataFrame(all_date)
        print("xlsx_file", xlsx_file)
        df.to_excel(xlsx_file, sheet_name='data', index=False)
        uuids[uid] = True
    except ValueError as e:
        print("error")
        print(e)


@app.get("/check_complete/{uid}")
def check_complete(uid: uuid.UUID):
    if uuids[uid]:
        return {"code": 0}

    return {"code": 1}


@app.post("/run_ocr")
async def run_do(background_tasks: BackgroundTasks, item: Item):
    file_list = read_directory(item.file_list)
    xlsx_file = save_dir + generate_random_str() + ".xlsx"
    print("xlsx_file", xlsx_file)
    print("file_list", file_list)
    uid = uuid.uuid4()
    uuids[uid] = False
    background_tasks.add_task(process, file_list, xlsx_file, uid)
    # all_date = image_ocr(file_list)
    # df = pd.DataFrame(all_date)

    # print("xlsx_file", xlsx_file)
    # df.to_excel(xlsx_file, sheet_name='data', index=False)
    # json_excel(all_date, item.xls_file)
    return {"code": 0, "uuid": uid}


# img = cv2.imread(directory_name + "/" + filename)


if __name__ == '__main__':
    uvicorn.run(app, debug=True, host='0.0.0.0', port=9298)
