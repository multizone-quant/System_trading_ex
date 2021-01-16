# date : 2021/01/17
# upbit 거래소 암호화폐 tick 자료 연속 얻기
#
# 실행결과
#   out_KRW-BTC_tick_2021-01-16.csv
#
# 보다 자세한 내용을 아래 tistory 참고
# https://money-expert.tistory.com/47
#

import requests
import json
import time
import os 
import csv
import glob

#
# for read data from cvs
#
# row : value list

def read_csv(fname) :
    data = []
    with open(fname, 'r', encoding='UTF8') as FILE :
        csv_reader = csv.reader(FILE, delimiter=',', quotechar='"')
        for row in csv_reader :
            data.append(row)
    return data

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

# 예 'https://api.upbit.com/v1/trades/ticks?market=KRW-JST&count=500&daysAgo=0'
# count : 최대 500
# ago : 0 -7까지 (0은 당일, 7은 7일 전)
# to : HH:mm:ss

def get_ticks_history(coin, ago=0, count=500, to=None) :
    base_url = 'https://api.upbit.com/v1/trades/ticks'
    code = '?market=' + coin
    s_count = '&count=' + str(count)
    s_ago = '&daysAgo='+ str(ago)
    url = base_url + code + s_count + s_ago
    if to == None :
        s_to = ''
    else :
        url += ('&to='+to)

    ret = request_get(url)
    return ret

# data 중 frm보다 오래된 데이터는 지운다.
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

# sequential_id는 int 형인데 str로 바꿈
def change_seq_id_to_str(data, key) :
    for each in data :
        each[key] = str(each[key])
    return data

# 이어 받기 용 to(sec) 값을 얻음
def get_next_to(data, key) :
    pre_to = ''
    for i in range(len(data)-1) :
        if data[i][key] != data[i+1][key] :
            pre_to = data[i][key]
    return pre_to

# tick은  from 개념은 없고, ago 값으로 일자 조절함. ago = 0 이면 오늘 1이면 어제 등등 최대 7일 전까지 얻을 수 있음
#    to 는 HH:mm;ss 형태임 (UTC 기준) 혹은 None
#    들어오는 시간 값은 uct 기준임
# 예      'https://api.upbit.com/v1/trades/ticks?market=KRW-JST&count=500&daysAgo=0'

def get_data_continue_tick(coin, count=10, ago=0, frm=None, to=None) :  
    end = False
    cnt = 1

    next_to = to
    seq_id = 0
    # tick 정보는 utc 기준으로 일을 정함
    while(end == False) :
        t = int(time.time())
        ret = get_ticks_history(coin, ago, count, next_to) # ago : 며칠 전인지. ticks는 하루 기준

        if len(ret) > 0 :
            # 마지막 sec 정보는 불안정할 수 있으므로, 연속으로 받을 sec을 구할 때 가장 적은 값보다 적은 sec을 구한다.
            #  즉 최종 sec은 다음 turn에서 다시 받는다. 
            #  그 이유는 한번에 받을 수 있는 자료 수는 제한적이므로, 마지막 sec 정보는 모두 받지 못할 경우가 있음

            next_to = get_next_to(ret, 'trade_time_utc')

            if frm != None : # from보다 이전 데이터인지 확인
                # 마지막 candle이 from보다 적으면 from 이후 candle을 지운다.
                if next_to < frm : 
                    ret = remove_data(ret, frm, 'trade_time_utc')
                    end = True

            ret = change_seq_id_to_str(ret, 'sequential_id')

            # cnt 번호를 추가하여 파일이름 생성
            info = ret[-1]
            fname = coin+'_tick_1_' + format(cnt, '03d') + '_' + info['trade_date_utc'] + '.csv'
            cnt += 1
            save_to_file_csv(fname, ret)
            print ('save ', fname, next_to)
            if next_to == '' :
                return
            if cnt % 10 == 0 :
                time.sleep(2)

        else :
            return

def    merge_excel_file(fname) :
    files = []
    filter = '.\\' + fname + '*.csv'
    for filename in glob.glob(filter): 
        files.append(filename)
    if len(files) == 0 :
        print('not exist files to merge')
        return
    all = []  # 파일에서 읽어들인 모든 데이터를 저장하는 list
    key1 = -1  # sorting할때 사용할 첫 번째 key (sequential_id)
    key2 = -1  # 파일저장할 때 사용할 일자 key (date)
    key3 = -1  # 파일 마지막에 있는 sec 삭제 용 key (time)
    title = []

    num_file = 0
    for name in files :
        data = read_csv(name)
        if data != [] :
            # key 위치 얻기, 처음에 한번만 실행 key1 : timestamp
            if key1 == -1 or key2 == -1 or key3 == -1 :
                title = data[0].copy()
                for i   in range(len(data[0])) :
                    if data[0][i] == 'sequential_id' : 
                        key1 = i
                    if data[0][i] == 'trade_date_utc' : 
                        key2 = i
                    if data[0][i] == 'trade_time_utc' :
                        key3 = i

            # tick의 경우에는 1초에 여러개 들어올 수 있음
            # 500개 제한 때문에 이전에 읽은 데이터는 불안정함
            # 따라서 all 데이터 중 마지막 to 값은 지운다.
            if len(all) > 0 :
                first_tm = all[-1][key3]  # 
                del_pos = []
                for i in range(len(all)-1,0, -1) : # all에 저장된 데이터를 뒤에서 읽으면서
                    if all[i][key3] == first_tm :
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

    dt = merged_data[1][key2]
    
    out_name = '.\\out_' + fname + '_' + dt + '.csv'
    save_list_to_file_csv(out_name, title, merged_data)
    print('merge finished', out_name)


# for tick  
# utc 기반으로 받됨
# 하루 기준으로 받음. 
COIN            = 'KRW-BTC'                    # 원하는 코인 정보
TICK_AGO        = 0             # tick정보는 ago를 to 개념으로 봐야함 ( 0: 오늘 1 : 어제 최대 7일 전 )
TICK_FROM       = '08:05:00'    # HH:mm:ss  (utc 기준임)  or None (00:00:00)
TICK_TO         = '00:05:00'    # HH:mm:ss  (utc 기준임)  or None (최근)

CANDLE_TYPE     = 'tick' # 'min' or 'day'

if __name__ == '__main__':

    print('get tick', COIN, 'ago: ', TICK_AGO)
    get_data_continue_tick(COIN, count=500, ago=TICK_AGO, frm=TICK_FROM, to=TICK_TO)  # tick을 받을 때

    # merge
    filename_prefix = COIN + '_' + CANDLE_TYPE   # 결과를 저장할 prefix
    print(' -- start merging --')
    merge_excel_file(filename_prefix)
