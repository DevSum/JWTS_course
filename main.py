import urllib.request
import http.cookiejar
import threading
import re
import time


class Course:
    def __init__(self, user_id, pwd):
        self.courses = []

        # 输入账号密码
        self.account_number = user_id
        self.pwd = pwd
        self.url_login = "http://jwts.hit.edu.cn/loginLdap?usercode=" + self.account_number + "&password=" + self.pwd

        # 设置 cookie 与 opener
        self.cookie = http.cookiejar.MozillaCookieJar('cookie.txt')
        self.handler = urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(self.handler)
        self.get_cookie()

    def get_cookie(self):
        # get登陆，拿sessionID
        request = urllib.request.Request(self.url_login)
        self.opener.open(request)
        self.cookie.save(ignore_discard=True, ignore_expires=True)  # 保存cookie到cookie.txt中

    def get_course_list(self, course_type="szxx"):  # unfinished
        courses = []
        url_course_list = "http://jwts.hit.edu.cn/xsxk/queryXsxkList?pageSize=100&pageXklb="+course_type+"&pageXnxq="+"2018-20191"
        page = self.opener.open(url_course_list).read().decode()
        print(page)
        temp = re.compile(r'addlist_button"[\s\S]+?xkyq').findall(page)

        for each in temp:
            course = []
            left = each.find("saveXsxk") + 9
            right = each.find(")", left)
            course.append(each[left:right])

            left = each.find("queryKcxx")
            left = each.find(r'return false;">', left) + 15
            right = each.find(r'</a', left)
            course.append(each[left:right])
            courses.append(course)
        self.courses = courses
        print(courses)

    def logout(self):
        url_logout = "http://jwts.hit.edu.cn/logout"
        self.opener.open(url_logout)

    def catch(self, course_id, course_type):
        # 查询课单，拿token
        url_query = "http://jwts.hit.edu.cn/xsxk/queryXsxkList?pageXklb=" + course_type
        temp = re.compile(r'id="token".+?value=".+?"')

        page_query = self.opener.open(url_query).read().decode("utf-8")
        if len(temp.findall(page_query)) == 0:
            print("登陆过期")
            return "登陆过期"
        token = temp.findall(page_query)[0][31:-1]
        print(token)

        # 选课
        url_choose = "http://jwts.hit.edu.cn/xsxk/saveXsxk?pageXklb=" + course_type + "&pageXnxq=2018-20191&rwh=" + course_id + "&token="+token  # pageXnxq: 学年学期（1:秋 2:春 3: 夏）
        response = self.opener.open(url_choose).read().decode("utf-8")

        temp = re.compile(r'alert.+?;')
        response = temp.findall(response)[0]
        print(response)
        return response


##########################
'''
account_number = input("请输入账号")
pwd = input("请输入密码")
course_id = input("请输入课程ID")
course_type = input("请输入课程类别")  # 拼音首字母，如英语 -> yy ,素质选修 -> szxx

'''
student_number = "11703010xx"
password = "xxxxxx"
courses_list = ["2018-2019-1-FL22118-001", "2018-2019-1-HS22128-001"]  # 选课代码

def catch(account_number, pwd, course_id, course_type="szxx"):
    catch = Course(account_number, pwd)
    while True:
        try:
            result = catch.catch(course_id, course_type)
        except:
            pass
        if "选课成功" in result:
            break
        if "登陆过期" in result:
            catch = Course(account_number, pwd)
        if "不在学生选课时间" in result:
            time.sleep(1)
        if "容量已满" in result:
            time.sleep(5)

try:
    for each in courses_list:
        threading.Thread(target=catch, args=(student_number, password, each)).start()
    while True:
        pass
except:
    pass

