# OpenHappyHackingCalendar-Python
《编程日历》的Python实现版本，基于[OpenHappyHackingCalendar](https://github.com/Sneezry/OpenHappyHackingCalendar)项目改编，与原项目基本一致。

## 结果展示

HTML样式展示：[link](./Calendar-2021.html)

PDF样式展示：[link](./Calendar-2021.pdf)

## 环境依赖

Python 3 (Python 3.9.1)

本项目使用了以下几个Python第三方库（加粗者为需要另行安装）：

- json
- **jsonpath**
- **lunar_python** (一个阴历/阳历转换库：[lunar](http://6tail.cn/calendar/api.html#overview.html))
- html
- **requests**

在测试过程中发现：需要电脑安装openssl。

除此之外，因为项目需要爬取维基百科中对编程语言的介绍，所以需要可以访问维基百科。

## 配置文件

在`config.json`中有以下参数可以配置：

- `year`：日历的年份
- `monthly`：是否在日历中显示单独的月份界面
- `punched`：日历是否打孔，效果很差:)
- `qr`：是否在日历中增加二维码

## 运行

下载程序→安装好环境→运行index.py

输出为类似`Calendar-2021.html`的文件
