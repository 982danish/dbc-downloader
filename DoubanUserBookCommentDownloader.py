#coding=utf-8
#Python 2.7.10
##从豆瓣网页中得到用户的所有读书短评

##网页地址类型：http://book.douban.com/people/1000001/collect?sort=time&start=0&filter=all&mode=grid&tags_sort=count
##            http://book.douban.com/people/1000001/collect?sort=time&start=15&filter=all&mode=grid&tags_sort=count

from BeautifulSoup import BeautifulSoup
import codecs
import time
import urllib2
import os

#设置HTTP代理
ans=raw_input('Do you want to use a HTTP Proxy (N/y)? ')
if ans=='y' or ans=='Y':
    print 'HTTP Proxy formart: IP:PORT \nExample: 127.0.0.1:80'
    print 'Do NOT contain any unnecessary characters.'
    proxyInfo=raw_input('Please type in your HTTP Proxy: ')
    proxySupport=urllib2.ProxyHandler({'http':proxyInfo})
    opener=urllib2.build_opener(proxySupport)
    urllib2.install_opener(opener)
else:
    pass
#头信息
hdr= {
   'Accept':'text/html, application/xhtml+xml, image/jxr, */*',
   'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
   'Connection':'Keep-Alive',
   'Cookie':'bid=lkpO8Id/Kbs; __utma=30149280.1824146216.1438612767.1440248573.1440319237.13; __utmz=30149280.1438612767.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); as=http://book.douban.com/people/133476248/; ll=108288; viewed=26274009_1051580; ap=1; ps=y; ct=y; __utmb=30149280.23.10.1440319237; __utmc=30149280; __utmt_douban=1; _pk_id.100001.3ac3=b288f385b4d73e38.1438657126.3.1440319394.1440248628.; __utma=81379588.142106303.1438657126.1440248573.1440319240.3; __utmz=81379588.1440319240.3.2.utmcsr=movie.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; _pk_ses.100001.3ac3=*; __utmb=81379588.23.10.1440319240; __utmt=1; __utmc=81379588; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1440319240%2C%22http%3A%2F%2Fmovie.douban.com%2F%22%5D',
   'Host':'book.douban.com',
   'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240'}

#url=url_1+uId+url_2+Index+url_3
url_1='http://book.douban.com/people/'
url_2='/collect?sort=time&start='
url_3='&filter=all&mode=grid&tags_sort=count'

def is_chinese(uchar):
    """判断一个unicode是否是汉字
    """
    if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
        return True
    else:
        return False

def isChineseBook(title):
    """判断书名是否为中文书名
    """
    for c in title:
        if(is_chinese(c)):
            return True
    return False

def getHtml(url):
    """返回指定的网页内容
    """
    print('Loading: '+url+'......')
    request=urllib2.Request(url,headers=hdr)
    html=urllib2.urlopen(request).read()
    return html

def getBookComment(html):
    """解析网页并返回5个列表：
    书名，出版信息，标记日期，标签，评论
    """
    titleList=[]    #书名
    pubList=[]      #出版信息
    dateList=[]     #标记日期
    tagsList=[]     #标签
    commentList=[]  #评论

    soup=BeautifulSoup(html)
    lis=soup.findAll('li','subject-item')
    for li in lis:
        infoDiv=li.find('div','info')
        commentP=infoDiv.find('p','comment')
        if commentP!=None:
            a=infoDiv.a
            #书名
            title1=a.get('title')
            title2Span=a.span
            if title2Span!=None:
                title2=a.span.text
            else:
                title2=''
            title=title1+title2
            c1=title[0]
            c2=title[-1]
            #如果是中文书名，则加上书名号
            if isChineseBook(title):
                title=u'《'+title+u'》'
            else:   #英文书加斜体
                title='*'+title+'*'
            titleList.append(title)
            #出版信息
            pubDiv=infoDiv.find('div','pub')
            pub=pubDiv.text
            pubList.append(pub)
            #标记日期
            dataSpan=infoDiv.find('span','date')
            words=dataSpan.text.split('\n')
            date=words[0]+words[1]
            dateList.append(date)
            #标签
            tagsSpan=infoDiv.find('span','tags')
            if tagsSpan!=None:
                tags=tagsSpan.text
            else:
                tags=''
            tagsList.append(tags)
            #评论
            comment=commentP.text
            commentList.append(comment)
    return (titleList,pubList,dateList,tagsList,commentList)

def saveBookComment(titleList,pubList,dateList,tagsList,commentList,uId):
    """保存书评至文件
    """
    fileName='booksComments_'+uId+'.md'
    wf=codecs.open(fileName,'a','utf-8')
    size=len(titleList)
    for i in range(size):
        title=titleList[i]
        pub=pubList[i]
        date=dateList[i]
        tags=tagsList[i]
        comment=commentList[i]
        wf.write('## '+title+'\n')
        wf.write(pub+'  \n')
        wf.write(date+'  \n')
        wf.write(tags+'\n\n')
        wf.write(comment+'\n\n')
    wf.close()

def getPageNum(html):
    """解析第一页网页，返回该用户的书评页数
    """
    soup=BeautifulSoup(html)
    paginator=soup.find('div','paginator')
    pas=paginator.findAll('a')
    num=int(pas[-2].text)
    return num

#输入User-Id
print '\n\nYou can find User-Id in the url.'
print 'E.g. Someone\'s homepage\'url is http://book.douban.com/people/1000001/ , the User-Id should be 1000001 .'
uId=raw_input('User-Id: ')
while(uId=='' or uId=='\t' or uId==' '):
	uId=raw_input('User-Id: ')
count=0     #计数器

#读取第一页
index=0
url=url=url_1+uId+url_2+str(index)+url_3
html=getHtml(url)
(titleList,pubList,dateList,tagsList,commentList)=getBookComment(html)
saveBookComment(titleList,pubList,dateList,tagsList,commentList,uId)

count+=len(titleList)
pageNum=getPageNum(html)    #用户读过的书的网页页数
index+=1
#读取后续页
for i in range(index*15,15*pageNum,15):
    print 'Sleep for 5 seconds.'
    time.sleep(5)
    print '%d/%d' %(i/15+1,pageNum)
    url=url=url_1+uId+url_2+str(i)+url_3
    html=getHtml(url)
    (titleList,pubList,dateList,tagsList,commentList)=getBookComment(html)
    count+=len(titleList)
    saveBookComment(titleList,pubList,dateList,tagsList,commentList,uId)
print 'Mission accomplished!'
print '%d comments have been saved.' %count
os.system("pause") 
