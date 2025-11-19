import json
import time
import requests
# import selenium.webdriver as webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By

def save_to_json(data: list, filename: str):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def handle_input():
    user_input = input('搜尋物品: ')
    return user_input

def handle_search_type():
    search_type = input('選擇搜尋方式 (1. requests 2. selenium) [預設 1]: ')
    if search_type == '2':
        return 'selenium'
    else:
        return 'requests'

def web_scrape_request():
    shop_map = {
        'pchome': {
            'search_api': 'https://ecshweb.pchome.com.tw/search/v4.3/all/results',
            'img_api': 'https://img.pchome.com.tw/cs',
            'prod_url': 'https://24h.pchome.com.tw/prod/'
            # search_api = 'https://ecshweb.pchome.com.tw/search/v4.3/all/results?q='
            # prod_api = 'https://ecapi-cdn.pchome.com.tw/ecshop/prodapi/v2/prod?id='
            # fields = '&fields=Seq,Id,Name,Nick,Store,PreOrdDate,SpeOrdDate,Price,Discount,Pic,Weight,ISBN,Qty,Bonus,isBig,isSpec,isCombine,isDiy,isNC17,isRecyclable,isCarrier,isMedical,isBigCart,isSnapUp,isHuge,isEnergySubsidy,isPrimeOnly,isPreOrder24h,isWarranty,isLegalStore,isFresh,isBidding,isSet,isQuickSet,Volume,isArrival24h,isETicket,ShipType,isO2O,RealWH,ShipDay,ShipTag,isEbook,isSubscription,Subscription,isOnSale,isInventoryChecking,PicExtra,YoutubeInfo,SalesName,Tagline,BrandList,CategoryIds,BrandId,RatingValue,ReviewCount,isPick,PickType,Frames'
        }, 
        'momo': {},
        'pxmart': {},
        'carrefour':{}
    }
    shop = 'pchome'
    scrapeCycleDelay = 2
    all_prods_list = []

    def gen_search_url(query: str, page: int, pageCount: int = 40) -> str:
        return f'{shop_map['pchome']["search_api"]}?q={query}&page={page}&pageCount={pageCount}'
    
    def gen_image_url(pic: str) -> str:
        return f'{shop_map['pchome']["img_api"]}{pic}' 

    def gen_product_url(pid: str) -> str:
        return f'{shop_map['pchome']["prod_url"]}{pid}'

    def parse_results(response_json: dict) -> list:
        for prod in response_json['Prods']:
            # print(prod['Id'], prod['Name'], prod['Price'])
            all_prods_list.append({
                'id': prod['Id'],
                'name': prod["Name"],
                'price': prod['Price'],
                'img_url': gen_image_url(prod['PicS']),
                'prod_url' : gen_product_url(prod['Id']),
            })

    def fetch_prods(query: str, page: int) -> dict:
        # url = gen_search_url(query, page)
        url = gen_search_url(query, page, 100)
        return requests.get(url).json()
    
    def fetch_all_prods(query: str):
        response_json = fetch_prods(query, 1)
        total_page = response_json['TotalPage']
        total_rows = response_json['TotalRows']
        if total_rows == 0:
            print('查無資料')
            return -1
        else:
            print(f'找到 {total_rows} 筆資料，共 {total_page} 頁')

        parse_results(response_json)


        for page in range(2, total_page + 1):
            time.sleep(scrapeCycleDelay)
            print(f'正在抓取第 {page} 頁資料...')
            response_json = fetch_prods(query, page)
            parse_results(response_json)

        return 0


    def run():
        query = handle_input()
        start = time.time()
        try:
            ret = fetch_all_prods(query)
        except Exception as e:
            print('發生錯誤:', e)
        ret = fetch_all_prods(query)
        end = time.time()
        print(f'耗時 {end - start:.2f} 秒')
        if ret == -1:
            return
        save_to_json(all_prods_list, f'{query}_{shop}_request.json')
        print(f'已儲存 {len(all_prods_list)} 筆資料至 {query}_{shop}_request.json')
        all_prods_list.clear()

    run()


def web_scrape_selenium():
    shop_map = {
        'pchome': {
            'search_url': 'https://24h.pchome.com.tw/search/?q=',
            'prods_exist_selector' : 'section.u-mb24',
            'next_page_selector' : '.o-iconFonts.o-iconFonts--arrowSolidRight',
            'url_selector' : 'div>a',
            'img_selector' : 'div>img',
            'price_selector' : 'div.c-prodInfoV2__price',
            'name_selector' : 'div.c-prodInfoV2__title'
        }, 
        'momo': {},
        'pxmart': {},
        'carrefour':{}
    }
    shop = 'pchome'
    scrapeCycleDelay = 3
    all_prods_list = []
    last_prod = None
    
    def open_browser():
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized') # Chrome 瀏覽器在啟動時最大化視窗
        options.add_argument('--incognito') # 無痕模式
        options.add_argument('--disable-popup-blocking') # 停用 Chrome 的彈窗阻擋功能。
        driver = webdriver.Chrome(options=options)
        return driver

    def gen_search_url(query: str) -> str:
        return f'{shop_map[shop]["search_url"]}{query}'

    def scroll_down(driver):
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        # time.sleep(scrapeCycleDelay)

    def prods_exist(driver) -> bool:
        try:
            driver.find_element(By.CSS_SELECTOR, shop_map[shop]['prods_exist_selector'])
            return False
        except Exception as e:
            return True
    
    def next_page(driver):
        try:
            return driver.find_element(By.CSS_SELECTOR, shop_map[shop]['next_page_selector'])
        except Exception as e:
            return None
        
    def is_last_page(prods: list) -> bool:
        nonlocal last_prod
        if last_prod != prods[-1] or last_prod is None:
            last_prod = prods[-1]
            return False
        return True
    
    def get_prods_list(driver):
        return driver.find_elements(By.CSS_SELECTOR, 'div.c-listInfoGrid__body ul li>div.c-prodInfoV2')

    def parse_prods(prods :list):
        # print(len(prods))
        for prod in prods:
            url = prod.find_element(By.CSS_SELECTOR, shop_map[shop]['url_selector']).get_attribute('href')
            img = prod.find_element(By.CSS_SELECTOR, shop_map[shop]['img_selector']).get_attribute('src')
            price = prod.find_element(By.CSS_SELECTOR, shop_map[shop]['price_selector']).text
            name = prod.find_element(By.CSS_SELECTOR, shop_map[shop]['name_selector']).text

            # print(url, img, price, name)
            all_prods_list.append({
                'name': name,
                'price': price,
                'img_url': img,
                'prod_url': url
            })

    def fetch_all_prods(query: str):
        driver = open_browser()
        driver.get(gen_search_url(query))
        time.sleep(scrapeCycleDelay)

        if not prods_exist(driver):
            print('查無資料')
            driver.quit()
            return

        while True:
            cur_prods_list = get_prods_list(driver)
            if is_last_page(cur_prods_list):
                print('已到最後一頁')
                break
            parse_prods(cur_prods_list)
            next_page_btn = next_page(driver)
            if next_page_btn is None:
                break
            next_page_btn.click()
            time.sleep(scrapeCycleDelay) 
       
        driver.quit()

    def run():
        query = handle_input()
        start = time.time()
        try:
            fetch_all_prods(query)
        except Exception as e:
            print('發生錯誤:', e)
        end = time.time()
        print(f'耗時 {end - start:.2f} 秒')
        save_to_json(all_prods_list, f'{query}_{shop}_selenium.json')
        print(f'已儲存 {len(all_prods_list)} 筆資料至 {query}_{shop}_selenium.json')
        all_prods_list.clear()
    
    run()

def main():
    search_type = handle_search_type()
    if search_type == 'requests':
        web_scrape_request()
    else:
        web_scrape_selenium()

if __name__ == '__main__':
    main()

