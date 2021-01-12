# date : 2021/01/12
# upbit 거래소 암호화폐 분/일봉 자료 얻기
#
# 실행결과
#   out_coin-name_min_1.csv
#
# 보다 자세한 내용을 아래 tistory 참고
# https://money-expert.tistory.com/46
#
# 2021/1/12 오후 3시 이후로 to 값을 변경하면서 과거 데이터를 모두 가져오는 기능이 동작하지 않은 버그 수정 : utc를 이용하고 

import requests
import json
import time
import os 

def save_list_to_file_csv(file_name, titles, data) :
    with open(file_name,'w',encoding="cp949") as make_file: 
        ss = ''
        # title 저장
        for name in titles:
            ss += (name + ',')
        ss += '\n'
        make_file.write(ss)

        for vals in data:
            ss = ''
            for val in vals:
                sval = str(val) 
                sval = sval.replace(',','')
                ss += (sval + ',')
            ss += '\n'
            make_file.write(ss)
    make_file.close()
#
# for writing dic data to cvs format
#
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
def get_candle_history(coin, ty='days', interval=1, count=400, to=None) :
    if ty == 'day' :
        ss = 'days'
    elif ty == 'min' :
        ss = 'minutes/'+str(interval)

    base_url = 'https://crix-api-endpoint.upbit.com/v1/crix/candles/' + ss
    code = '?code=CRIX.UPBIT.' + coin
    s_count = '&count=' + str(count)

    url = base_url + code + s_count
    if to == None :
        s_to = ''
    else :
        url += ('&to='+to)
#    print(url)
    ret = request_get(url)
    return ret 

# data 중 frm보다 오래된 데이터는 지운다.
# candle : 'candleDateTime'
# tick : 'trade_time_utc'
def remove_data(data, frm, key) :
    del_items = 0
    pos = 0
    for each in data :
        if each[key] < frm :
            del_items = pos
            break
        pos += 1

    return data[:pos]

# candle from - 최근 구간 받기
def get_data_continue_candle(coin, ty='day', interval=1, count=10, frm=None, to=None) :  
    end = False
    cnt = 1
    next_to = to
    while(end == False) :
        t = int(time.time())
        ret = get_candle_history(coin, ty, interval, count, next_to)

        if ret != None :
            if len(ret) < 2 : # no more data
                return

            # candle은 내림차순
            # 마지막에 저장된 candle의 시간을 구한다.

            info = ret[-1]  

            tm_kst = info['candleDateTimeKst']

            dt = info['candleDateTimeKst'].split('+')
            tm = dt[0].replace('T', ' ')
            day = tm.split(' ')[0]
                
            if frm != None : # from보다 이전 데이터인지 확인
                # 마지막 candle이 from보다 적으면 from 이후 candle을 지운다.
                if tm_kst < frm : 
                    ret = remove_data(ret, frm, 'candleDateTimeKst')
                    end = True
            
            # 계속 검색을 하는 경우에는 현재 받은 candle의 마지막 시간이 next_to가 된다.
            # 이때 시간은  UTC
            dt = info['candleDateTime'].split('+')
            next_to = tm                    

            # cnt 번호를 추가하여 파일이름 생성
            fname = coin+'_' + ty + '_' + str(interval) + '_' + format(cnt, '03d') + '_' + day + '.csv'
            cnt += 1
            save_to_file_csv(fname, ret)
            print ('save ', fname)


            if ty == 'day' : # day는 400개만 받을 수 있다.ㅣ
                end = True
            else :  # 분 봉은 계속 받을 수 있다.
                time.sleep(1)

        else :
            end = True


#
# for read data from cvs
#
# row : value list
def get_new_item(keys, row) :
    data = {}
    for i in range(len(row)) :
        data[keys[i]] = row[i]
    return data

import csv

# 첫 줄은 title이라고 가정, 이후에 title 값을 key로 갖는 dict로 읽기
def read_csv_to_dict(fname) :
    data = []
    keys =[]
    first = 1
    with open(fname, 'r', encoding='UTF8') as FILE :
        csv_reader = csv.reader(FILE, delimiter=',', quotechar='"')
        for row in csv_reader :
            if first : # make dict keys
                keys = row.copy()
#                for key in row :
#                    keys .append(key)
                first = 0
            else :                
                data.append(get_new_item(keys, row))
    return data

def read_csv(fname) :
    data = []
    with open(fname, 'r', encoding='UTF8') as FILE :
        csv_reader = csv.reader(FILE, delimiter=',', quotechar='"')
        for row in csv_reader :
            data.append(row)
    return data


import glob
def    merge_excel_file(code) :
    files = []
    filter = '.\\' + code + '*.csv'
    for filename in glob.glob(filter): 
        files.append(filename)

    all = []  # 파일에서 읽어들인 모든 데이터를 저장하는 list
    key1 = -1  # sorting할때 사용할 첫 번째 key (time_t)
    title = []

    num_file = 0
    for name in files :
        data = read_csv(name)
        if data != [] :
            # key 위치 얻기, 처음에 한번만 실행 key1 : timestamp
            if key1 == -1 :
                title = data[0].copy()
                for i   in range(len(data[0])) :
                    if data[0][i] == 'timestamp' :
                        key1 = i

            first_tm = data[1][key1]  # key1 = timestamp

            del_pos = []
            for i in range(len(all)-1,0, -1) : # all에 저장된 데이터를 뒤에서 읽으면서
                if all[i][key1] == first_tm :
                    del_pos.append(i)   # 지울 데이터의 row를 저장
                else :
                    break

            for pos in del_pos : # 지울 데이터가 있으면(중복된) 지운다.
                del(all[pos])

            # 방금 읽은 data의 0번째(title)을 지운다.
            del(data[0]) # title은 지운다.
            all += data

        num_file += 1

    # 오름차순으로 정
    merged_data = sorted(all, key = lambda x: (x[key1]), reverse=False)  # key1 번째가 key 
    out_name = '.\\out_' + code + '.csv'
    save_list_to_file_csv(out_name, title, merged_data)
    print('merge finished', out_name)


# upbit 과거 데이터 받기
CANDLE_TYPE     = 'min' # 'min' or 'day'
CANDLE_INTERVAL = 1     # 3,5,10,30,60

COIN            = 'KRW-HUNT'                    # 원하는 코인 정보
FROM            = '2021-01-11T20:00:00+09:00'   # 특정 일자부터 받고 싶을 때 format : candle : '2021-01-12T10:00:00+09:00'
TO              = None                          # to는 None 까지만 test함


if __name__ == '__main__':

    # upbit tick max 500
    print('get candle ', COIN, CANDLE_TYPE, CANDLE_INTERVAL)
    get_data_continue_candle(COIN, ty=CANDLE_TYPE, interval = CANDLE_INTERVAL, count=400, frm=FROM, to=TO)  
    
    # merge
    filename_prefix = COIN + '_' + CANDLE_TYPE + '_'+ str(CANDLE_INTERVAL)  # 결과를 저장할 prefix
    merge_excel_file(filename_prefix)
