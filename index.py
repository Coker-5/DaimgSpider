# -*- ecoding: utf-8 -*-
# @ModuleName: index
# test
# @Author:
# @Time: 2023/10/11 15:09
import os
from tkinter import messagebox

import requests
from lxml import etree
from tqdm import tqdm
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import tkinter as tk


class PictrueSpider:
    def __init__(self):
        # 请求头部信息
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": "http://www.daimg.com/pic/%E5%B8%83%E8%BE%BE%E6%8B%89%E5%AE%AB.html",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 Edg/117.0.2045.60"
        }

        # Cookie信息
        self.cookies = {
            "__51cke__": "",
            "PHPSESSID": "4d1761bc81c94d84ef275245ad9412ca",
            "DedeUserID": "558372",
            "DedeUserID__ckMd5": "6286a07ae607ece3",
            "DedeLoginTime": "1697008508",
            "DedeLoginTime__ckMd5": "3b05d583e3fad5ec",
            "__tins__21295873": "%7B%22sid%22%3A%201697007725315%2C%20%22vd%22%3A%2021%2C%20%22expires%22%3A%201697010344555%7D",
            "__51laig__": "21"
        }
        self.words = []

    # 控制函数，接收关键字参数

    def control(self, keys):
        self.keys = keys
        # 调用搜索函数

        re = self.search(keys=keys)
        # 调用解析函数

        self.parse_result(re)

    # 搜索函数，发送搜索请求并返回结果

    def search(self, keys):
        url = "http://www.daimg.com/pic/{}.html".format(keys)
        # 发送请求
        try:
            response = requests.get(url=url, cookies=self.cookies, headers=self.headers, timeout=28)
            response.encoding = "utf-8"

            # assert截断，如果不是200状态码则抛出异常
            assert response.status_code == 200
            with open("data.txt","w",encoding="utf-8") as fp:
                fp.write(response.text)
            return response.text
        except Exception as e:
            print("Something wrong was happend,The status_code is {}".format(e))

    # 解析搜索结果函数，提取链接和标题
    def parse_result(self, h_text):
        # xpath解析器
        html = etree.HTML(h_text)

        try:
            # 通过html文档结构进行定位
            link = html.xpath("//*[@class='ibox2_list']/li/a/@href")

            title = html.xpath("//*[@class='ibox2_list']/li/a/@title")

            print("{}共有{}张图片".format(self.keys, len(link)))
            # 因为获取的是多张图片，所以需要遍历
            for i in link:
                html = self.get_info(i, title)

                self.parse_info(html)
            print("图片全部下载完成")

        except Exception as e:
            print("Something wrong was happend in parse_result,The infomation is {}".format(e))

    # 获取详细信息函数，发送请求获取详细信息页面内容

    def get_info(self, url, title):
        try:
            response = requests.get(url=url, cookies=self.cookies, headers=self.headers, timeout=28)
            # 因为这个网页的编码不是utf-8，而是gb2312，在html文档head可以看到
            response.encoding = "gb2312"

            # assert截断，如果不是200状态码则抛出异常

            assert response.status_code == 200

            return response.text
        except Exception as e:
            print("Something wrong was happend in get_info,The infomation is {}".format(e))

    # 解析详细信息函数，提取图片链接、标题、精度和标签

    def parse_info(self, html):
        html = etree.HTML(html)
        try:
            link = html.xpath("//*[@class='n_img']/img/@src")
            link = "".join(link)

            title = html.xpath("//*[@class='n_img']/img/@alt")
            title = "".join(title)

            jindu = html.xpath("/html/body/div[4]/div[1]/ul[6]/span[6]/text()")
            jindu = "".join(jindu)

            jindu = jindu.replace("素材精度：", "")
            tags = html.xpath("//*[@class='n_listr']/span/text()")

            self.save_tags(tags)
            content = self.download_img(url=link)

            self.save_img(title, jindu, content)
        except Exception as e:
            print("Something wrong was happend in parse_info,The infomation is {}".format(e))

    # 下载图片函数，发送请求下载图片并返回二进制数据

    def download_img(self, url):
        try:
            response = requests.get(url=url, cookies=self.cookies, headers=self.headers, stream=True, timeout=28)

            self.response_data = response

            assert response.status_code == 200

            return response.content
        except Exception as e:
            print("Something wrong was happend in download_img,The infomation is {}".format(e))

    # 保存图片函数，将二进制数据保存为图片文件

    def save_img(self, title, jindu, file_bytes):
        path = "./图片资源/{}".format(self.keys)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        img_path = "./图片资源/{}/{}-{}.jpg".format(self.keys, title, jindu)

        # 使用 tqdm 显示进度条
        with open(img_path, 'wb') as file:
            # 获取文件长度
            total_size = int(self.response_data.headers.get('content-length', 0))
            # 遍历下载
            progress_bar = tqdm(total=total_size,
                                unit='B',
                                unit_scale=True,
                                desc=f"正在下载：{title}",
                                miniters=1)

            # 实时更新进度
            for data in self.response_data.iter_content(chunk_size=1024):
                file.write(data)
                progress_bar.update(len(data))

            progress_bar.close()

    # 保存标签函数，将标签保存至文件中

    def save_tags(self, tags):
        try:
            self.words.extend(tags)
            word_path = "./图片资源/{}/words.txt".format(self.keys)
            os.makedirs(os.path.dirname(word_path), exist_ok=True)

            total_words = "".join(self.words)

            with open(word_path, "a", encoding="utf-8") as f:
                f.write(total_words)
        except Exception as e:
            print("Something wrong happened in save_tags. The information is {}".format(e))

    # 创建词云函数，根据标签生成词云图
    def cre_wordcloud(self):
        try:
            word_path = "./图片资源/{}/words.txt".format(self.keys)
            with open(word_path, 'r', encoding='utf-8') as file:
                text = file.read()
            # 使用结巴分词进行中文分词
            seg_list = jieba.cut(text)

            # 将分词结果拼接成字符串
            seg_text = ' '.join(seg_list)


            print(seg_text)

            # 自定义停用词
            my_stopwords = set(['的', '了', '是', '我', '你', '高清', '大图', '旅游', '摄影', '图片素材', '素材'])

            # 创建词云对象
            wordcloud = WordCloud(background_color='lightblue',
                                  width=1920,  # 宽
                                  height=1080,  # 高
                                  max_font_size=180,
                                  stopwords=my_stopwords,
                                  font_path='SimHei.ttf').generate(seg_text)

            # 保存词云图
            wordimg_path = "./图片资源/{}/wordcloud.png".format(self.keys)

            wordcloud.to_file(wordimg_path)

            # 绘制词云图
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.show()
        except Exception as e:
            print("Something wrong was happend in cre_wordcloud,The infomation is {}".format(e))


# 界面类

class MainGui:
    def __init__(self):
        self.window = tk.Tk()
        # 设置窗口大小为400x300（宽度x高度）
        self.window.geometry("400x200")

        # 添加frame，标题区域
        self.Frame_title = tk.Frame(self.window)
        self.Frame_title.pack(side="top")

        # 添加frame，输入框区域

        self.Frame_search = tk.Frame(self.window, pady=27)
        self.Frame_search.pack()

        # 添加frame，提交按钮区域

        self.Frame_sub = tk.Frame(self.window, pady=20)
        self.Frame_sub.pack()

        self.ready_frame()

    def ready_frame(self):
        self.window.title("大图网")

        # 设置内容
        Lable_title = tk.Label(self.Frame_title,
                               text="欢迎使用大图网爬虫程序", font=("Arial", 12),
                               fg="red")
        Lable_keys = tk.Label(self.Frame_search,
                              text="关键词：")
        keys_input = tk.Entry(self.Frame_search,
                              bd=5)

        # 调用回调函数处理按钮反馈事件

        def callback():
            spider = PictrueSpider()
            keyword = keys_input.get()

            # 判断是否输入数据
            if keyword:
                spider.control(keyword)
                res = messagebox.askyesno(title="提示", message="爬取完成，是否生成词云图？")
                if res == True:
                    spider.cre_wordcloud()
                else:
                    pass
            else:
                messagebox.showinfo("提示", "请输入关键词!!!")

        # 设置按钮样式
        Button_sub = tk.Button(self.Frame_sub,
                               text="爬取",
                               activebackground='blue',
                               activeforeground='white',
                               width=7, command=callback)

        Lable_title.pack()
        Lable_keys.pack(side="left")
        keys_input.pack(side="right")
        Button_sub.pack()

        # 设置主事件循环
        self.window.mainloop()

    def fenxi(self, keyword):
        print(keyword)


if __name__ == '__main__':
    MainGui()
