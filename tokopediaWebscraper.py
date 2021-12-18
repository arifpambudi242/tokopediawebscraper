from requests.api import request
from selenium import webdriver
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from time import sleep
import re

class TokopediaScraper:
    def __init__(self, url):
        self.total_result_amount = 0
        self.driver = webdriver.Chrome()
        self.url = url
        self._productlinks = []
        self._productToBeScraped = 0
        self._productDetails = {
            'Product Name'  : [],
            'Description'   : [],
            'Image Link'    : [],
            'Price'         : [],
            'Rating 5'      : [],
            'Store Name'    : []
        }

    def get(self, url):
        self.driver.get(url)
    
    def scrollPage(self):
        y = 1000
        for timer in range(0,5):
            self.driver.execute_script("window.scrollTo(0, "+ str(y) +")")
            y += 1000
            sleep(1)

    def htmlParser(self, scroll=False):
        if scroll:
            self.scrollPage()
        html = self.driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML;")
        return bs(html, 'html.parser')
    
    def validateLink(self, link=''):
        self.get(link)
        soup = self.htmlParser()
        if soup == None:
            print('\n url valid \n')
        return soup == None
        
    def getProductLinks(self, page=0):
        # getting store links
        if page:
            self.get(self.url+"&page=%s"%page)
        soup = self.htmlParser(scroll=True)
        # get outer div of product list
        outer_divs = soup.find_all("div", class_="css-1dq1dix e1nlzfl1")
        product_links = [a.find('a') for a in outer_divs[0].find_all("div", class_="css-bk6tzz e1nlzfl3")]
        product_links = [product_link.get('href') for product_link in product_links]
        for pl in product_links:
            validurl = 0
            if self.validateLink(pl):
                print('\n url valid\n')
                product_links.append(pl)
                validurl += 1
                if validurl >= self._productToBeScraped:
                    break
            else:
                continue
        return product_links
    
    def getTotalPages(self):
        self.get(self.url)
        soup = self.htmlParser()
        outer_divs = soup.find_all("div", class_="css-1dq1dix e1nlzfl1")
        self.total_result_amount = int(outer_divs[0].find_all('strong')[1].getText().strip())
    
    def getProductLinksAmount(self, link_amount):
        self._productToBeScraped = link_amount
        self.getTotalPages()
        product_links = []
        for pg in range(1, round(self.total_result_amount/75)):
            if len(product_links) < link_amount:
                for pl in self.getProductLinks(pg):
                    product_links.append(pl)
                    if len(product_links) >= self._productToBeScraped:
                        break
                continue
            else:
                break
        self._productlinks = product_links
        return product_links
    
    @property
    def productlinks(self):
        return self._productlinks
    
    @property
    def productDetails(self):
        return self._productDetails
    
    def getProductDetails(self, links=[]):
        if links:
            self._productlinks = links
        scraped = 0
        for pl in self._productlinks:
            if scraped < self._productToBeScraped:
                try:
                    self.get(pl)
                    soup = self.htmlParser(scroll=True)
                    productName = soup.find('h1', attrs={'data-testid' : 'lblPDPDetailProductName'}).get_text()
                    ProductDescriptions = soup.find('div', attrs={'data-testid' : 'lblPDPDescriptionProduk'}).get_text()
                    imageLink = soup.find('img', attrs={'class' : 'success fade'}).get('src')
                    price = soup.find('div', attrs={'data-testid' : 'lblPDPDetailProductPrice'}).get_text()
                    rating5Stars = soup.find_all('p', attrs={'data-testid' : re.compile(r'^icnStar5-*')})[1].get_text()
                    storeName = soup.find('a', attrs={'data-testid' : 'llbPDPFooterShopName'}).find('h2').get_text()
                    
                    self._productDetails['Product Name'].append(productName)
                    self._productDetails['Description'].append(ProductDescriptions)
                    self._productDetails['Image Link'].append(imageLink)
                    self._productDetails['Price'].append(price)
                    self._productDetails['Rating 5'].append(rating5Stars)
                    self._productDetails['Store Name'].append(storeName)
                    scraped += 1
                except:
                    continue
      
    def saveAs(self, filename='result', ext='csv'):
        df = pd.DataFrame(self._productDetails)
        df.to_csv(f'{filename}.{ext}', index=False, sep=';')
    
    def doScraping(self, productlinksamount):
        self.getProductLinksAmount(productlinksamount)
        self.getProductDetails()
        self.saveAs()
        self.driver.close()
    
if __name__ == "__main__":
    scraper = TokopediaScraper("https://www.tokopedia.com/p/handphone-tablet/handphone?od=5")
    scraper.doScraping(10)