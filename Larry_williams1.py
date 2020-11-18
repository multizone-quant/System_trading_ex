# date : 2020/11/18
# Larry Willams 변동성 돌파 시뮬레이션
#
# 보다 자세한 내용을 아래 tistory 참고
# https://money-expert.tistory.com/33
#

import json
import requests
import csv

#
# for read data from cvs
#
# row : value list
def get_new_item(keys, row) :
    data = {}
    for i in range(len(row)) :
        data[keys[i]] = row[i]
    return data

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

#
# for writing data to cvs format
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


# basic functions for candle
class Candle :
    def __init__(self) :
        self.clear()

    def add(self, info) :
        self.vol += info['vol']
        self.date = info['date']
        self.time = ''
        if 'time' in info :
            self.time = info['time']
        if self.open == 0 :
            self.open = info['open']
            self.high = info['high']
            self.low = info['low']
            self.close = info['close']
        if self.high < info['high'] :
            self.high = info['high']
        if self.low > info['low'] :
            self.low = info['low']
        self.close = info['close']

        if info['rate'] != '0' :
            # 수정 주가 대상인 경우에만 반영
            # todo
            self.rate = float(info['rate'])
            self.rate_type = int(info['rate_type'])

    def clear(self) :
        self.date = ''
        self.time = ''
        self.open = 0
        self.high = 0
        self.low = 0
        self.close = 0
        self.vol = 0
        self.rate = 0
        self.rate_type = 0


class TR_LW() :
    def __init__(self, interval, num) :
        self.interval = interval # min', 'day'
        self.interval_num = num # 1, 5, 20, 60
        self.pre  = None
        self.cur  = None
        self.k = 0.5
        self.bought = 0 # 현재 매수 중인지
        self.history = []

    def update_new_range(self, cur) : # 
        self.pre  = cur
        self.history.append(cur)
        self.range = self.pre.high - self.pre.low # 전 candle의 range

    def is_enter_candle(self, candle) :  
        enter = 0
        buy_price = (candle.open + self.range * self.k)
        if candle.high > buy_price :  # 최고가가 buy_price보다 높으면 매수되었다고 가정
            enter = 1

        # 오늘 candle update
        self.update_new_range(candle)
        
        if enter :
            return buy_price
        return 0


def make_candle_info(data) :
    dt = data['candleDateTimeKst'].split('T')
    pre = Candle()
    pre.date = dt[0]
    dtt = dt[1].split('+')
    pre.time = dtt[0]
    pre.open = float(data['openingPrice'])
    pre.high = float(data['highPrice'])
    pre.low = float(data['lowPrice'])
    pre.close = float(data['tradePrice'])
    pre.vol = float(data['candleAccTradeVolume'])
    return pre


def simulation(ticker, sim_file, tr_login) :
    # simulation 데이터를 읽는다.
    candle_data = read_csv_to_dict(sim_file)
    if candle_data == [] :
        print('not exist ', sim_file)
        return

    # simulation 중 파일에 저장할 변수들 추가
    candle_data[-1]['buying'] = 0 # buy 여부 저장
    candle_data[-1]['profit'] = 0 # profit 저장
    candle_data[-1]['total_profit'] = 0 # total_profit 저장
    candle_data[-1]['dd'] = 0 # downd draw 저장

    # 제일 마지막 일봉이 어제 candle
    yest = candle_data[len(candle_data)-1]

    # 가장 오래된 일봉 데이터로 candle을 만든다.
    candle = make_candle_info(yest)
    
    # 어제 일봉 setting
    tr_logic.update_new_range(candle)

    deposit = 1000000   # 1회 최대 1백만원 매수
    balance = deposit   # 현재 잔고

    bought = 0
    num_trading = 0
    total_profit = 0
    total_fee = 0
    num_winning = 0
    num_losing = 0
    max_loss = 0
    max_gain = -10000000
    mdd = 0
    trading_fee = 0.00035  # 0.1%

    for i in range(len(candle_data)-2,-1,-1)  :# 내림차순으로 저장되어 있으므로 뒤에서 한개씩
        #현재 simulation 데이터로 candle을 만든다.
        candle = make_candle_info(candle_data[i])
                
        # simulation 중 파일에 저장할 변수들 추가
        #   simulation 결과를 검증하기 위하여 buy하는 일봉에 대하여 buying 가격, 수익, dd 값을 저장
        candle_data[i]['buying'] = 0 # buy 여부 저장
        candle_data[i]['profit'] = 0 # profit 저장
        candle_data[i]['total_profit'] = 0 # total_profit 저장
        candle_data[i]['dd'] = 0 # dd(draw down) 저장

        buy_price = tr_logic.is_enter_candle(candle) 
        if buy_price > 0 : # 매수조건임

            # 1. 매수 금액 결정, min(balance, deposit) 초기 deposit 금액 혹은 balance가 초기 deposit 이하이면 balance
            buying_amount = min(balance, deposit)

            # 2. 일봉 종가에 판다고 가정
            num_buying = buying_amount / buy_price    # 매수 주수
            profit = (candle.close - buy_price) * num_buying
            balance += profit

            # 3. 매수 수수료
            fee = num_buying * buy_price * trading_fee
            total_fee += fee
            balance -= fee
            # 매도 수수료
            fee = num_buying * candle.close  * trading_fee
            total_fee += fee
            balance -= fee


            # 4. update statistics
            num_trading += 1  # 매수한 주문 수
            total_profit += profit # 누적 수익
            if profit > 0 :
                num_winning += 1
            else :
                num_losing += 1

            # 최대 손실, 최고 이익 값 update
            if max_loss > total_profit :
                max_loss = total_profit
            if max_gain < total_profit :
                max_gain = total_profit
                    
            # draw down 계산
            dd = 100.0 * (max_gain - total_profit) / max_gain
            if dd > mdd :
                mdd = dd  # mdd 계산

            # 5. adding log
            candle_data[i]['profit'] = profit # buying 결과 수익 추가
            candle_data[i]['total_profit'] = total_profit # 
            candle_data[i]['buying'] = buy_price  # buying한 매수가 추가
            candle_data[i]['dd'] = dd # draw down 값


    fname = ticker + '-LW-result-all.csv'
    save_to_file_csv(fname, candle_data)

    # print simulation results
    print('ticker : ', ticker)
    print('total # trading  : ', num_trading)
    print('total profit     : ', format(total_profit, ",.2f"))
    print('trading fee      : ', format(total_fee, ",.2f"))
    print('total Net Profit : ', format(total_profit - total_fee, ",.2f"))
    print('# winning        : ', num_winning)
    print('# losing         : ', num_losing)
    print('MDD              : ', format(mdd,'3.2f'))
    print('max loss         : ', format(max_loss, '10,.2f'))
    print('max gain         : ', format(max_gain, '10,.2f'))

    # save simulation results
    fname = ticker + '-LW-result-all.txt'
    file = open(fname, 'w')
    file.write('ticker : {0}\n'.format(ticker))
    file.write('total # trading : {0} \n total profit: {1}\n'.format(num_trading, total_profit))
    s = 'trading fee : ' + format(total_fee, ".2f") + '\n'
    file.write(s)
    s ='total profit with fee :' + format((total_profit - total_fee), ".2f") + '\n'
    file.write(s)
    file.write('# winning : {0} # losing: {1} \n'.format(num_winning, num_losing))
    file.write('MDD: {0}  max loss: {1}  max gain : {2} \n'.format(mdd,  max_loss,  max_gain))
    file.close()

    print('exit')


if __name__ == '__main__':

    # back data
    fname = '.\\sim_data\\BTC_day-2017-09-25-2020-11-12.csv'
    ticker = 'KRW-STEEM'

    # Larry William 변동성 돌파, 일봉 사용
    tr_logic = TR_LW('day', 1)

    simulation(ticker, fname, tr_logic)
    print('')
