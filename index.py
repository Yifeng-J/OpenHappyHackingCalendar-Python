import json
import jsonpath
from lunar_python import Solar
import html
import requests
import ssl
from urllib.parse import quote

# 以json格式读取文件
lang = open('./lang.json', 'r', encoding='utf8')
lang_json = json.load(lang)

config = open('./config.json')
config_json = json.load(config)

calTemplate = open('cal.html', 'r', encoding='utf8').read()
pageTemplate = open('page.html', 'r', encoding='utf8').read()
monthlyTemplate = open('monthly.html', 'r', encoding='utf8').read()

# 读取config文件
YEAR = config_json['year']
QR = config_json['qr']
PUNCHED = config_json['punched']
MONTHLY = config_json['monthly']

# 编程语言的名字加黑显示
HIGHLIGHT = [
    'markup', 'css', 'clike', 'javascript', 'abap', 'actionscript', 'ada',
    'apacheconf', 'apl', 'applescript', 'arduino', 'asciidoc', 'aspnet',
    'autohotkey', 'autoit', 'bash', 'basic', 'batch', 'bison', 'brainfuck',
    'bro', 'c', 'csharp', 'cpp', 'coffeescript', 'crystal', 'css-extras', 'd',
    'dart', 'django', 'diff', 'docker', 'eiffel', 'elixir', 'erlang', 'fsharp',
    'flow', 'fortran', 'gherkin', 'git', 'glsl', 'go', 'graphql', 'groovy',
    'haml', 'handlebars', 'haskell', 'haxe', 'http', 'icon', 'inform7', 'ini',
    'j', 'java', 'jolie', 'json', 'julia', 'keyman', 'kotlin', 'latex', 'less',
    'livescript', 'lolcode', 'lua', 'makefile', 'markdown', 'matlab', 'mel',
    'mizar', 'monkey', 'n4js', 'nasm', 'nginx', 'nim', 'nix', 'nsis',
    'objectivec', 'ocaml', 'opencl', 'oz', 'parigp', 'parser', 'pascal',
    'perl', 'php', 'php-extras', 'powershell', 'processing', 'prolog',
    'properties', 'protobuf', 'pug', 'puppet', 'pure', 'python', 'q', 'qore',
    'r', 'jsx', 'renpy', 'reason', 'rest', 'rip', 'roboconf', 'ruby', 'rust',
    'sas', 'sass', 'scss', 'scala', 'scheme', 'smalltalk', 'smarty', 'sql',
    'stylus', 'swift', 'tcl', 'textile', 'twig', 'typescript', 'vbnet',
    'verilog', 'vhdl', 'vim', 'wiki', 'xojo', 'yaml'
]

dates = []

# 定义月份的天数
longMonth = [1, 3, 5, 7, 8, 10, 12]
shortMonth = [4, 6, 9, 11]
longMonthLastDay = 31
shortMonthLastDay = 30
leapDay = 29
nonLeapYearFebLastDay = 28

monthLastDayMapping = {2: nonLeapYearFebLastDay}
for i in longMonth:
    monthLastDayMapping[i] = longMonthLastDay

for j in shortMonth:
    monthLastDayMapping[j] = shortMonthLastDay


# 判断一个年份是否是闰年
def isLeapYear(year):
    # 世纪年份能够被400整除为闰年
    if (year % 100 == 0 and year % 400 == 0):
        return True
    # 普通年份能被4整除为闰年
    if (year % 100 != 0 and year % 4 == 0):
        return True
    return False


# 判断day是否是month的最后一天
def isLastDayOfMonth(month, day):
    if (month == 2 and isLeapYear(YEAR)):
        return day == leapDay
    return day == monthLastDayMapping[month]


if (isLeapYear(YEAR)):
    monthLastDayMapping[2] = leapDay
else:
    monthLastDayMapping[2] = nonLeapYearFebLastDay

for month in range(1, 13):
    lastDay = monthLastDayMapping[month]
    for day in range(1, lastDay + 1):
        solar = Solar.fromYmd(YEAR, month, day)
        dates.append(solar)

festivals = {'1001': '国庆节'}

for date in dates:
    f = date.getFestivals() + date.getLunar().getFestivals()
    if len(f):
        month = str(date.getMonth())
        day = str(date.getDay())
        festivals[month.zfill(2) + day.zfill(2)] = f[0]

# 在这里增加想要添加的节日，可以覆盖掉上面的节日
festivals['0101'] = '元旦'

res = []
langs = []
langIndex = 0
while langIndex < len(lang_json):
    codeLang = lang_json[langIndex]
    try:
        url = 'https://zh.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&uselang=zh-cn&titles=' + \
              quote(codeLang[
                  'desc'], 'utf-8')
        # 请求头部
        headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }
        # 利用请求地址和请求头部构造请求对象,发送请求，获得响应
        response = requests.get(url=url, headers=headers)
        response.encoding = 'utf8'
        # 读取响应，获得文本
        wiki = json.loads(response.text)
        desc = jsonpath.jsonpath(wiki, '$..extract')
        codeLang['descWiki'] = desc[0].split('\n')[0]
        langIndex = langIndex + 1
    except Exception as e:
        print("!!!!!!!error!!!!!!!!!!", e)
        continue
    code_string = open('hacking-date/HackingDate.' + codeLang['code'],
                       'r',
                       encoding='utf8')
    # 对内容中的特殊符合进行转义，以在HTML中显示
    codeLang['code'] = html.escape(code_string.read())
    langs.append(codeLang)

pages = "<div class=\"${PUNCHED ? 'page punched' : 'page'}\"> <h1 class=\"title\">Happy Hacking ${YEAR}</h1> </div>"

monthly = []
table = ''
rows = ''
weekly = []
page = ''
weeks = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
months = [
    'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December'
]
langIndex = 0

newMonth = []
pageIndex = 0
calContent = ''

for dateIndex in range(0, len(dates)):
    date = dates[dateIndex]

    if (date.getDay() == 1):
        newMonth.append(pageIndex)

    # 生成日历前面的单独月份
    if (MONTHLY):
        date_day = date.getDay()
        date_month = date.getMonth()

        if (date_day == 1):
            if (PUNCHED):
                table = monthlyTemplate.replace('{{pclass}}', 'page punched')
            else:
                table = monthlyTemplate.replace('{{pclass}}', 'page')
            table = table.replace('{{month}}', months[date_month - 1])
            rows = '<tr>'
            # 一个月的第一天如果不是周日的话，那么前面需要加空白天
            for i in range(0, date.getWeek()):
                rows = rows + '<td></td>'

        # 如果是周日且不是月初，则换一行
        if (date.getWeek() == 0 and date.getDay() != 1):
            rows = rows + '<tr>'

        # 优先级顺序：节假日、节气、阴历月份(如果是初一)、阴历日
        # 只要不是阴历日，就显示为红色
        if str(date_month).zfill(2) + str(date_day).zfill(2) in festivals.keys(
        ):
            lday = festivals[str(date_month).zfill(2) + str(date_day).zfill(2)]
        else:
            lday = date.getLunar().getJieQi()
        lclass = 'lunar red'
        if (len(lday) == 0):
            # 如果是初一则显示阴历月份，否则显示阴历日
            if (date.getLunar().getDayInChinese() == '初一'):
                lday = date.getLunar().getMonthInChinese()
                lclass = 'lunar red'
            else:
                lday = date.getLunar().getDayInChinese()
                lclass = 'lunar'
        rows += "<td><div>" + str(date.getDay()) + "</div><div class=\"" + str(
            lclass) + "\">" + str(lday) + "</div></td>"

        # 如果是这个月的最后一天，那么这一行后面的日期要留为空白
        if (isLastDayOfMonth(date.getMonth(), date.getDay())):
            for emptyDay in range(date.getWeek(), 6):
                rows = rows + '<td></td>'
                rows = rows + '</tr>'
            monthly.append(table.replace('{{rows}}', rows))
        elif (date.getWeek() == 6):
            rows = rows + '</tr>'

    # 生成后面的7天一页的日历
    if (date.getWeek() == 0 or len(page) == 0):
        if (PUNCHED):
            page = pageTemplate.replace('{{pclass}}', 'page punched')
        else:
            page = pageTemplate.replace('{{pclass}}', 'page')

        # 判断是否生成QR
        if (QR):
            page = page.replace('{{fclass}}', 'show_qr')
        else:
            page = page.replace('{{fclass}}', 'hide_qr')

        page = page.replace(
            '{{main-date}}',
            f'{str(date.getYear())}-{str(date.getMonth()).zfill(2)}-{str(date.getDay()).zfill(2)}'
        )
        page = page.replace('{{main-week}}', f'{weeks[date.getWeek()]}')
        page = page.replace('{{mwclass}}', 'main-week')
        if (str(date.getMonth()).zfill(2) + str(date.getDay()).zfill(2)
                in festivals.keys()):
            ldata = festivals[str(date.getMonth()).zfill(2) +
                              str(date.getDay()).zfill(2)]
        else:
            ldata = date.getLunar().getJieQi()
        mlclass = 'main-lunar red'
        if (len(ldata) == 0):
            if (date.getLunar().getMonthInChinese() == '初一'):
                mlclass = 'main-lunar red'
                ldata = date.getLunar().getMonthInChinese()
            else:
                mlclass = 'main-lunar'
                ldata = date.getLunar().getDayInChinese()

        page = page.replace('{{main-ldata}}', ldata)
        page = page.replace('{{mlclass}}', mlclass)

        # 周六或者周日为红色
        if (date.getWeek() == 0 or date.getWeek() == 6):
            page = page.replace('{{mclass}}', 'main-date red')
        else:
            page = page.replace('{{mclass}}', 'main-date')

        # 代码部分替换
        if (langIndex < len(langs)):
            if (langs[langIndex]['lang'] == 'CSS'):
                page = page.replace(
                    '{{code}}', langs[langIndex]['code'].replace(
                        '2018-03-25',
                        f'{date.getYear()}-{str(date.getMonth()).zfill(2)}-{str(date.getDay()).zfill(2)}'
                    ))
            else:
                page = page.replace('{{code}}', langs[langIndex]['code'])
            # 代码名称替换
            page = page.replace('{{lang}}', langs[langIndex]['lang'])

            if (langs[langIndex]['class'] in HIGHLIGHT):
                page = page.replace('{{class}}',
                                    'language-' + langs[langIndex]['class'])
            else:
                page = page.replace('{{class}}', langs[langIndex]['class'])

            page = page.replace('{{desc}}', langs[langIndex]['descWiki'])
            if (QR):
                wiki_url = 'https://zh.wikipedia.org/wiki/' + langs[langIndex][
                    'desc']
                # qr = 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=' + wiki_url
                qr = 'https://chart.apis.google.com/chart?chs=360x360&cht=qr&choe=UTF-8&chld=M|0&chl=' + wiki_url
            else:
                qr = 'data:image/gif;base64,R0lGODlhAQABAAAAACw='
            page = page.replace('{{qr}}', qr)
            langIndex = langIndex + 1
    else:
        page = page.replace('{{week' + str(date.getWeek()) + '}}', weeks[date.getWeek()])
        page = page.replace(f'{{{{date{date.getWeek()}}}}}',  # 此处用fstring时一定要注意{要进行转义
                            str(date.getMonth()).zfill(2) + "-" + str(date.getDay()).zfill(2))
        if (str(date.getMonth()).zfill(2) + str(date.getDay()).zfill(2)
                in festivals.keys()):
            ldata = festivals[str(date.getMonth()).zfill(2) +
                              str(date.getDay()).zfill(2)]
        else:
            ldata = date.getLunar().getJieQi()
        lclass = 'lunar red'
        if len(ldata) == 0:
            if date.getLunar().getMonthInChinese() == '初一':
                lclass = 'lunar red'
                ldata = date.getLunar().getMonthInChinese()
            else:
                lclass = 'lunar'
                ldata = date.getLunar().getDayInChinese()

        page = page.replace('{{ldate' + str(date.getWeek()) + '}}', ldata)
        page = page.replace('{{lclass' + str(date.getWeek()) + '}}', lclass)

    # 换页或者到12月的最后一天,需要将没有填入日期的空格清空
    if (date.getWeek() == 6 or dateIndex == len(dates) - 1):
        for i in range(0, 6):
            page = page.replace(f'{{{{week{i + 1}}}}}', '')
            page = page.replace(f'{{{{date{i + 1}}}}}', '')
            page = page.replace(f'{{{{ldate{i + 1}}}}}', '')
        weekly.append(page)
        page = ''
        pageIndex += 1

# 生成前面的单独月份
for i in range(0, len(monthly)):
    calContent += monthly[i]

# 加入周日历
for j in range(0, len(weekly)):
    calContent += weekly[j]
cal = calTemplate.replace('{{page}}', calContent)

output_name='Calendar-'+str(YEAR)+'.html'
out = open(output_name, 'w', encoding='utf8')
out.write(cal)
out.close()
