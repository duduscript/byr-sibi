__author__ = 'duduscript'

from sys import argv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import time
from PIL import Image

def fullpage_screenshot(driver, file):
    print("Starting chrome full page screenshot workaround ...")
    
    total_width = driver.execute_script("return document.body.offsetWidth")
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
    viewport_width = driver.execute_script("return document.body.clientWidth")
    viewport_height = driver.execute_script("return window.innerHeight")
    print("Total: ({0}, {1}), Viewport: ({2},{3})".format(total_width, total_height,viewport_width,viewport_height))
    rectangles = []

    i = 0
    while i < total_height:
        ii = 0
        top_height = i + viewport_height

        if top_height > total_height:
            top_height = total_height

        while ii < total_width:
            top_width = ii + viewport_width

            if top_width > total_width:
                top_width = total_width
            
            print("Appending rectangle ({0},{1},{2},{3})".format(ii, i, top_width, top_height))
            rectangles.append((ii, i, top_width,top_height))

            ii = ii + viewport_width
        
        i = i + viewport_height

    stitched_image = Image.new('RGB', (total_width, total_height))
    previous = None
    part = 0

    for rectangle in rectangles:
        if not previous is None:
            driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
            time.sleep(0.2)
            #driver.execute_script("document.getElementById('topnav').setAttribute('style', 'position: absolute; top: 0px;');")
            #time.sleep(0.2)
            print("Scrolled To ({0},{1})".format(rectangle[0], rectangle[1]))
            time.sleep(0.2)

        file_name = "part_{0}.png".format(part)
        print("Capturing {0} ...".format(file_name))

        driver.get_screenshot_as_file(file_name)
        screenshot = Image.open(file_name)

        if rectangle[1] + viewport_height > total_height:
            offset = (rectangle[0], total_height - viewport_height)
        else:
            offset = (rectangle[0], rectangle[1])

        print("Adding to stitched image with offset ({0}, {1})".format(offset[0],offset[1]))
        stitched_image.paste(screenshot, offset)

        del screenshot
        os.remove(file_name)
        part = part + 1
        previous = rectangle

    stitched_image.save(file)
    print("Finishing chrome full page screenshot workaround...")
    return True

def merge(img_paths,path):
    max_width,total_height = 0,0
    for img_path in img_paths:
        with Image.open(img_path) as img:
            width,height = img.size
            max_width = max(max_width,width)
            total_height += height
    final_img = Image.new('RGB',(max_width,total_height))
    x,y = 0,0
    for img_path in img_paths:
        with Image.open(img_path) as img:
            width,height = img.size
            final_img.paste(img,(x,y))
            y += height
    final_img.save(path)
    

class User(object):
    def __init__(self,username,password):
        self.username = username
        self.password = password


class Crawler(object):
    def __init__(self):
        self.url = "https://bbs.byr.cn"
        self.nextpage_xpath = '//*[@id="body"]/div[4]/div[1]/ul/li[2]/ol/li[last()]/a'
        self.title_xpath = '//*[@id="body"]/div[2]/span[2]'
        self.driver = webdriver.Chrome()
        self.driver.get(self.url)
        self.driver.maximize_window()
        #self.s = None
        time.sleep(3)
        print('--------get--------')
    def login(self,user):
        print(user.username,user.password)
        username_form = self.driver.find_element_by_name('id')
        password_form = self.driver.find_element_by_name('passwd')
        username_form.send_keys(user.username)
        password_form.send_keys(user.password)
        self.driver.find_element_by_id('b_login').click()
        time.sleep(5)
    def travel(self,url):
        def hasnext():
            return self.driver.find_element_by_xpath(self.nextpage_xpath).text == '>>'
        self.driver.get(url)
        time.sleep(5)
        title = self.driver.find_element_by_xpath(self.title_xpath).text
        if title not in os.listdir():
            os.makedirs(os.getcwd()+'/'+title)
        pagenum = 1
        pngpath = str(hash(url))+'?p='+str(pagenum)+'.png'
        self.fullpage_screenshot('/'.join([os.getcwd(),title,pngpath]))
        while hasnext():
            pagenum += 1
            self.driver.find_element_by_xpath(self.nextpage_xpath).click()
            time.sleep(2)
            pngpath = str(hash(url))+'?p='+str(pagenum)+'.png'
            self.fullpage_screenshot('/'.join([os.getcwd(),title,pngpath]))
            #pngs.append(pngpath)
        #merge(pngs,str(hash(url))+'.png')

    def fullpage_screenshot(self,filename):
        fullpage_screenshot(self.driver,filename)



if __name__ == '__main__':
    username = os.environ.get('BYR_ID')
    password = os.environ.get('BYR_PWD')
    print(username,password)
    user = User(username,password)
    crawler = Crawler() 
    crawler.login(user)
    crawler.travel(argv[1])
