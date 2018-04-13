import expanddouban
import bs4
import csv
import codecs

"""
return a string corresponding to the URL of
douban movie lists given category and location.
"""


def getMovieUrl(category, location):
    """return a URL string"""
    url = 'https://movie.douban.com/tag/#/?sort=S&range=9,10&tags=电影,{},{}'.format(category, location)
    return url


class Movie:
    """docstring for Movie"""

    def __init__(self, name, rate, location, category, info_link, cover_link):
        self.name = name
        self.rate = rate
        self.location = location
        self.category = category
        self.info_link = info_link
        self.cover_link = cover_link


"""
return a list of Movie objects with the given category and location.
"""


def getMovies(category, location):
    """return a list of obj of films"""
    # 获取url, 调用函数getMovieUrl
    url = getMovieUrl(category, location)
    # 爬取网页,返回html
    html = expanddouban.getHtml(url, loadmore=True, waittime=2)

    soup = bs4.BeautifulSoup(html, "html.parser")
    # 创建各元素(属性)列表
    names = []
    rates = []
    info_links = []
    cover_links = []
    movies_shelf = soup.find(class_="list-wp")  # 锁定页面范围
    # 查找，并为各属性赋值
    for each in movies_shelf.find_all('a'):  # 遍历每一条电影记录, tag=a
        names.append(each.find(class_="title").string)  # .string方法获得tag的唯一子节点
        rates.append(each.find(class_="rate").string)
        info_links.append(each.get("href"))
        cover_links.append(each.find("img").get("src"))  # 获取<img>中的src超链接

    movies = []  # 该列表储存电影对象
    # 创建类Movie的对象，并将对象放入列表movies中
    for index in range(len(names)):
        # 调用类Movies来实例化
        movies.append(Movie(names[index], rates[index], location, category, info_links[index], cover_links[index]))

    return movies


# 手动为category tag赋值
favorite_categories = ['喜剧', '动作', '战争']

# 地区列表
locationList = []
# 爬取网页tag自动获取地区列表
url = 'https://movie.douban.com/tag/#/?sort=S&range=9,10&tags=电影'
html = expanddouban.getHtml(url, loadmore=False, waittime=2)
soup = bs4.BeautifulSoup(html, "html.parser")
# 地区列表的获取
for child in soup.find(class_='tags').find(class_='category').next_sibling.next_sibling:
    location = child.find(class_='tag').get_text()
    if location != '全部地区':
        locationList.append(location)

# 创建存储所有movie对象的列表movies
movies = []
# 遍历并爬取满足tag=category,location的网页并实例化movies
for category in favorite_categories:
    for location in locationList:
        '''创建包含三个类型、所有地区，评分超过9分的完整电影列表'''
        # 实例化movies
        movies += getMovies(category, location)  # 列表加列表
        # 这一步应该如何改进？因为如果此处location选择了全部地区，就无从得知movie对应的地区了？！
        # 但如果遍历地区，效率就会非常低。
        # 有没有两全的方法？

# 创建csv文件并写入movies数据
# 为了指定编码格式，这里用codecs模块
# 先将codecs模块导入，然后使用codecs.open()指定编码格式
with codecs.open('movies.csv', 'w', 'utf_8_sig') as csvfile:
    writer = csv.writer(csvfile)

    # write all movies information
    for m in movies:
        # 分行写入信息
        writer.writerow([m.name, m.rate, m.location, m.category, m.info_link, m.cover_link])

# 分类的movies列表, 三个空列表的列表
# 分别是comedy_movies = [], action_movies = [], war_movies = []
movies_ByCategory = [[], [], []]
# 将movies对象分类
for m in movies:
    for i in range(0, 3):
        if m.category == favorite_categories[i]:
            movies_ByCategory[i].append(m)
            break


# 计算地区频次的函数
def location_count(movies):
    """return a dict stored locations and their counts"""
    location_dict = {}
    for m in movies:
        if m.location not in location_dict:
            location_dict[m.location] = 1
        else:
            location_dict[m.location] += 1

    return location_dict


# 函数location_percent()专门将location_count()中的频次百分化
def location_percent(location_dict):
    """return a location_dict whose location counts expressed as a percentage"""
    total_frequency = sum(location_dict.values())  # 统计location_dict中的电影总数
    # 将频次化为百分数
    for location in location_dict:
        location_dict[location] = round(location_dict[location] / total_frequency, 4)

    return location_dict


# 获得包含地区和频次百分比的字典, 包含comedy_location_dict, action_location_dict和war_location_dict
location_dict_ByCategory = [[], [], []]
for i in range(0, 3):
    location_dict_ByCategory[i] = location_percent(location_count(movies_ByCategory[i]))

# 排序并获取前三的电影对象, 包含comedy_location_max，action_location_max和war_location_max
location_max_ByCategory = [[], [], []]
for i in range(0, 3):
    location_max_ByCategory[i] = sorted(location_dict_ByCategory[i].items(), key=lambda x: x[1], reverse=True)[:3]

# 将结果输出到txt文件中
# 将编码统一指定为 utf-8
with open("output.txt", "w", encoding='utf-8') as f:
    for i in range(0, 3):
        f.write("在电影类别{}中，9-10分电影排名前三的地区是：第一：{}，占比{:.2%}；第二：{}，占比{:.2%}；第三：{}，占比{:.2%}；\n"
                .format(favorite_categories[i],
                        location_max_ByCategory[i][0][0], location_max_ByCategory[i][0][1],
                        location_max_ByCategory[i][1][0], location_max_ByCategory[i][1][1],
                        location_max_ByCategory[i][2][0], location_max_ByCategory[i][2][1]
                        ))

# End
