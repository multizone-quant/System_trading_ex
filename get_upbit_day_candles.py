# date : 2020/11/16
# upbit 거래소 암호화폐 일봉 자료 얻기
#
# 실행결과
#   coin-name_day1.csv
#   coin-name_day2.csv
#   coin-name_day3.csv
#
# 보다 자세한 내용을 아래 tistory 참고
# https://money-expert.tistory.com/33
#

import requests
import json

def save_to_file_csv(file_name, data) :
    with open(file_name,'w',encoding="cp949") as make_file: 
        # title 저장
        vals = data[0].keys()
        ss = ''
        for val in vals:
            val = val.replace(',','')
            ss += (val + ',')
        ss += '\n'
        make_file.write(ss)

        for dt in data:
            vals = dt.values()
            ss = ''
            for val in vals:
                sval = str(val) 
                sval = sval.replace(',','')
                ss += (sval + ',')
            ss += '\n'
            make_file.write(ss)
    make_file.close()

def save_to_file_json(file_name, data) :
    with open(file_name,'w',encoding="cp949") as make_file: 
       json.dump(data, make_file, ensure_ascii=False, indent="\t") 
    make_file.close()


def request_get(url, headers = 0, echo=0) :
    response = ""
    cnt2 = 0
    while str(response) != '<Response [200]>' and cnt2 < 10:
        if echo :
            print("requests request_get", url)
        try :
            response = requests.get(url, headers=headers)
        except Exception as e:
            print(e)
            time.sleep(20)
            cnt2 += 1
            continue
        if str(response) != '<Response [200]>':
            print('sleep ', url)
            time.sleep(15)
        cnt2 += 1
    return response.json()


# coin : "KRW-BTC" 
# ex       https://crix-api-endpoint.upbit.com/v1/crix/candles/days?code=CRIX.UPBIT.KRW-BTC&count=10&to=2019-09-01%2000:00:00
def get_coin_history_day(coin, count=400, to=None) :
    base_url = 'https://crix-api-endpoint.upbit.com/v1/crix/candles/days'
    code = '?code=CRIX.UPBIT.' + coin
    s_count = '&count=' + str(count)

    url = base_url + code + s_count
    if to == None :
        s_to = ''
    else :
        url += ('&to='+to)
    ret = request_get(url)
    return ret

if __name__ == '__main__':

    coin = 'KRW-STEEM'
    ret = get_coin_history_day(coin, count=400)
    if ret != None :
        fname = coin+'_day1.csv'
        save_to_file_csv(fname, ret)

    # coin_day1.csv 파일을 open한 후 마지막에 저장된 날자를 아래 to에 입력
    to = '2019-10-20 09:00:00'
    ret = get_coin_history_day(coin, count=400, to=to)
    if ret != None :
        fname = coin+'_day2.csv'
        save_to_file_csv(fname, ret)

    to = '2018-09-20 09:00:00'
    ret = get_coin_history_day(coin, count=400, to=to)
    if ret != None :
        fname = coin+'_day3.csv'
        save_to_file_csv(fname, ret)

    print('')
