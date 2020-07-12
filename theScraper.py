import time,random,socket,unicodedata
import string, copy, os
import pandas as pd
import requests
try:
    from urlparse import urlparse
except ImportError:
    from six.moves.urllib.parse import urlparse
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

#################VARIABLES###########################
    
maximages = 20
##singlelink = "https://in.pinterest.com/user/board/"    #single link exists
singlelink = None     #single link not there, using csv for multiple files
csvfileloc = r"C:\folder\boardlist.csv"
chromeexecpath = r"C:\folder\chromedriver.exe"
username = "Enter_your_username"
password = "Enter_your_password"
downloadtodir = "C:/folder/Downloaded_images"

#####################################################


def downloadallimages(myinput, direc):
    
    if isinstance(myinput, str) or isinstance(myinput, bytes):
        res = requests.get(myinput)
        res.raise_for_status()
        outfile = direc + "/" + os.path.basename(urlparse(myinput).path)
        toFile = open(outfile, 'wb')
        for chunk in res.iter_content(100000):
            toFile.close()
    elif isinstance(myinput, list):
        for i in myinput:
            download(i, direc)
    else:
        pass


def multiplelinks(pin):
    localmaximg = maximages
    fileread = pd.read_csv(csvfileloc,header=None).values.tolist()
    fp = []
    for i in range(0,len(fileread)):
        fp.append(fileread[i][0])
    
    final = []
    for url in fp:
        eachlink = pin.singlelinkfun(url)
        final = list(set(eachlink + final))
    random.shuffle(final)
    return final 

def u_to_s(uni):
    return unicodedata.normalize('NFKD',uni).encode('ascii','ignore')

class scaperpin(object):

    def singlelinkfun(self, persistence = 120, debug = False):
        localmaximg = maximages
        url = singlelink
        final_results = []
        previmages = []
        tries = 0
        try:
            self.browser.get(url)
            while localmaximg > 0:
                try:
                    results = []
                    images = self.browser.find_elements_by_tag_name("img")
                    if images == previmages:
                        tries += 1
                    else:
                        tries = 0
                    if tries > persistence:
                        if debug == True:
                            print("More than persistence limit")
                        return final_results
                    for i in images:
                        src = i.get_attribute("src")
                        if src:
                            if src.find("/236x/") != -1:
                                src = src.replace("/236x/","/736x/")
                                results.append(u_to_s(src))
                    previmages = copy.copy(images)
                    final_results = list(set(final_results + results))
                    dummy = self.browser.find_element_by_tag_name('a')
                    dummy.send_keys(Keys.PAGE_DOWN)
                    time.sleep(random.uniform(2,4))
                    localmaximg -= 1
                except (StaleElementReferenceException):
                    if debug == True:
                        print("StaleElementReferenceException")
                    localmaximg -= 1
        except (socket.error, socket.timeout):
            if debug == True:
                print("Socket Error")
        except KeyboardInterrupt:
            return final_results
        if debug == True:
            print("Exitting at end")
        return final_results

    
    def __init__(self, login, passw, browser):
        self.browser = browser
        self.browser.get("https://in.pinterest.com")
        emailElem = self.browser.find_element_by_name('id')
        emailElem.send_keys(login)
        passwordElem = self.browser.find_element_by_name('password')
        passwordElem.send_keys(passw)
        passwordElem.send_keys(Keys.RETURN)
        time.sleep(random.uniform(3,6))

#end of class    
    

print ("Using Chrome webdriver")
chrome = webdriver.Chrome(executable_path=chromeexecpath)

print ("Entering username and password")
pin = scraperpin(username,password, chrome)

print ("Choosing between single board link or multiple board links")

if singlelink:
    print ("Chose single link")
    images = pin.singlelinkfun()
else:
    print ("Chose file with multiple links")
    images = multiplelinks(pin)

print ("Before downloading")
imgs = []
for i in images:
    imgs.append(i.decode())
downloadallimages(imgs, downloadtodir)

print ("Finished downloading")
print ("Closing chrome")
chrome.close()
