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
    prods_list = []

    def gen_search_url(query: str, page: int, pageCount: int = 40) -> str:
        return f'{shop_map['pchome']["search_api"]}?q={query}&page={page}&pageCount={pageCount}'
    
    def gen_image_url(pic: str) -> str:
        return f'{shop_map['pchome']["img_api"]}{pic}' 

    def gen_product_url(pid: str) -> str:
        return f'{shop_map['pchome']["prod_url"]}{pid}'

    def parse_results(response_json: dict) -> list:
        for prod in response_json['Prods']:
            # print(prod['Id'], prod['Name'], prod['Price'])
            prods_list.append({
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
        ret = fetch_all_prods(query)
        end = time.time()
        print(f'耗時 {end - start:.2f} 秒')
        if ret == -1:
            return
        save_to_json(prods_list, f'{query}_pchome_results.json')
        print(f'已儲存 {len(prods_list)} 筆資料至 {query}_pchome_results.json')
        prods_list.clear()

    run()


def web_scrape_selenium():
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
    prods_list = []
    pass


def main():
    web_scrape_request()

if __name__ == '__main__':
    main()

