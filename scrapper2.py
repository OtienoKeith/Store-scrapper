from os import name
import os.path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import requests # to get image from the web
import shutil # to save it locally
import firebase_admin
from firebase_admin import credentials, initialize_app, storage
from firebase_admin import firestore  
import csv 
# field names 
fields = ["Status", 'Name', 'Cost', 'Sub-Category', 'Category',"ImageUrl"] 
# name of csv file 
filename = "naivas_vs_jumia.csv"
# initializations 
cred = credentials.Certificate('rabble-87dd5-firebase-adminsdk-huv89-1aa321297a.json')
initialize_app(cred, {'storageBucket': 'rabble-87dd5.appspot.com'})
db = firestore.client()

url_list = []
# path to chromedriver.exe 
path = 'C:\Program Files (x86)\chromedriver.exe'
links = []
naivasHomeURL = 'https://www.naivas.co.ke'
jumiaHome = 'https://www.jumia.co.ke'
# area select url
deliveryAreaURL = 'https://www.naivas.co.ke/delivery-area'

# create instance of webdriver
options = webdriver.ChromeOptions()

# options.add_argument("start-maximized")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(executable_path=path, options=options)

def init():
    # initcsv()
    # Code to open a specific url
    driver.get(naivasHomeURL)
    #select area
    driver.forward()
    time.sleep(2)
    area = driver.find_elements_by_class_name('zone-container')
    if len(area) < 2:
        time.sleep(2)
        init()
    else:
        area[2].click()
        #click continue
        continueButton = driver.find_element_by_class_name('loc-btn')
        continueButton.click()
        # open naivas home url
        time.sleep(2)
        driver.back()
        time.sleep(2)


def get_links():
    all_ul = driver.find_elements_by_class_name("exitList")
    for one_ul in all_ul:
        all_li = one_ul.find_elements_by_tag_name("li")
        for li in all_li:
            li.click()
    #         attr = li.find_elements_by_tag_name("a")
    #         # links.append(attr.get_attribute('href'))
    #         links.append(attr.findElements(By.cssSelector(".submenuitem > a")))
    #     # hrefs_under_ul = [elem.get_attribute('href') for elem in all_li]
    #     # links.extend(hrefs_under_ul)
    # useURLs(links)


def useURLs(list):
    count = 0
    for url in list:
        count += 1
        print(str(count) + " " + str(url))

def search(term, price, cat, sub, url):
    # set the keyword you want to search for
    keyword = term 
    
    try:
    # we find the search bar using it's name attribute value
        searchBar = driver.find_element_by_tag_name('input')
        # first we send our keyword to the search bar followed by the enter # key
        searchBar.send_keys(keyword)
        searchBar.send_keys('\n')
        time.sleep(3)
        driver.forward()
        htl = driver.find_element_by_xpath('//*[@id="jm"]/main/div/div/h2').text
        if("There are no results" in htl):
            row = ["Missing", term, price, sub, cat, url ]
        else:
            row = ["Found", term, price, sub, cat, url  ] 
             
    except:
        row = ["Found", term, price, sub, cat, url  ] 
    addToCSV(row)
    # driver.back()



def goByDropDown():
    # time.sleep(10)
    # list all product category urls
    #drops = WebDriverWait(driver,50).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "dropDownActivator [href]")))
    # drops = driver.find_elements_by_xpath("//a[@class='dropDownActivator']")
    drops = driver.find_elements_by_class_name('category')
    
    print(str(len(drops))+"\n")

    count = 0
    for drop in drops:
        count += 1
        drop.click()
        # print(str(count)+"\n")

def getItemURLs():
    time.sleep(3)
    skip_list = []
    with open('skip2.txt', 'r') as f:
        skip_list = [line.strip() for line in f]
    print(skip_list)
    items = driver.find_elements_by_xpath("//ul[@class='exitList']//a[@class='exit']")
    count = 0
    for a in items:
        count += 1
        url = a.get_attribute('href')
        # Checking if url exists in skip list
        # using in
        if ((url in skip_list) == False):
            url_list.append(url)
            print(url)
            if count == len(items):
                loopURLs(url_list)

def addToSkip(url):
    f = open("skip2.txt", "a+")
    f.write(url.strip())
    f.write('\n')
    f.close()

def initcsv():
    # writing to csv file 
    with open(filename, 'a+') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the fields 
        csvwriter.writerow(fields) 


def addToCSV(row):
    # writing to csv file 
    with open(filename, 'a+') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the data rows 
        csvwriter.writerow(row)
    
    

def loopURLs(url_list):
    count = 0
    for url in url_list:
        getProducts(url, count)
        count += 1


def getProducts(url, count):
    print(url)
    driver.get(url)
    cat_list = ['electronics','health-wellness','snacks','beverages','toiletries','food-cupboard','furniture',
    'baby-kids','fresh-food','beauty-cosmetics','frozen','fats-oil','household','cleaning','stationery','sauces',
    'kitchen-dining','naivas-dry-cereals-nuts','naivas-liquor']
    category = url.split("/")[-2]
    subcat = url.split("/")[-1]
    cat_code = cat_list.index(category)
    subcat_code = count

    for i in  range(15):
        time.sleep(0.4)

        html = driver.find_element_by_tag_name('body')
        html.send_keys(Keys.END)

    time.sleep(1)

    # articles = driver.find_elements_by_tag_name('article')
    images_list = driver.find_elements_by_xpath("//img[@itemprop='image']")
    prices_list = driver.find_elements_by_xpath("//meta[@itemprop='price']")
    totalImg = str(len(images_list))
    print("Images total: "+totalImg)
    
    cnt = 0
    titleList =[]
    priceList = []
    imageUrlList = []
    for article in images_list:
        price = prices_list[cnt].get_attribute('content')
        if(int(price) >= 2000):
            imageTitle = article.get_attribute('title')
            imageurl = article.get_attribute('src')
            titleList.append(imageTitle)
            priceList.append(price)
            imageUrlList.append(imageurl)
        cnt += 1
        
    
    addToSkip(url) 

    pos = 0
    for name in titleList:
        saveImageToFirebaseStorage(name, priceList[pos], category, subcat, imageUrlList[pos])
        pos += 1



def saveImageToFirebaseStorage(name, price, cat, sub, url):
    
    driver.get(jumiaHome)
    search(name, price, cat, sub, url)


init()
# goByDropDown()
getItemURLs()
# search("bread")
# saveImageToStorage()


# ['https://www.naivas.co.ke/sub-category/big-save/big-save','https://www.naivas.co.ke/sub-category/big-save/weekly-offers',',','https://www.naivas.co.ke/sub-category/electronics/washing-machines-iron-boxes','https://www.naivas.co.ke/sub-category/electronics/electricals','https://www.naivas.co.ke/sub-category/electronics/water-dispensers-electric-kettles','https://www.naivas.co.ke/sub-category/electronics/fans-heaters','https://www.naivas.co.ke/sub-category/electronics/microwaves-food-processors','https://www.naivas.co.ke/sub-category/electronics/fridges-freezers','https://www.naivas.co.ke/sub-category/electronics/cookers','https://www.naivas.co.ke/sub-category/electronics/dvds-decoders','https://www.naivas.co.ke/sub-category/electronics/vacuum-cleaners-weigh-scales','https://www.naivas.co.ke/sub-category/electronics/blenders-toasters']