# date : 2020/11/19
# Larry Willams 변동성 돌파 시뮬레이션
#
# 보다 자세한 내용을 아래 tistory 참고
# https://money-expert.tistory.com/35
#

import json
import csv

from my_util import *
from my_candle import *
from TR_LW import *

def save_sim_result(fname, ticker, stat) :
    file = open(fname, 'w')
    file.write('total # trading  : '+ str(stat.num_trading))
    file.write('total profit     : '+ format(stat.total_profit, ",.2f"))
    file.write('trading fee      : '+ format(stat.total_fee, ",.2f"))
    file.write('total Net Profit : '+ format(stat.total_profit - stat.total_fee, ",.2f"))
    file.write('# winning        : '+ str(stat.num_winning))
    file.write('# losing         : '+ str(stat.num_losing))
    file.write('MDD              : '+ format(stat.mdd,'3.2f'))
    file.write('max loss         : '+ format(stat.max_loss, '10,.2f'))
    file.write('max gain         : '+ format(stat.max_gain, '10,.2f'))
    file.close()

def print_sim_result(ticker, stat) :
    print('ticker : ', ticker)
    print('total # trading  : ', stat.num_trading)
    print('total profit     : ', format(stat.total_profit, ",.2f"))
    print('trading fee      : ', format(stat.total_fee, ",.2f"))
    print('total Net Profit : ', format(stat.total_profit - stat.total_fee, ",.2f"))
    print('# winning        : ', stat.num_winning)
    print('# losing         : ', stat.num_losing)
    print('MDD              : ', format(stat.mdd,'3.2f'))
    print('max loss         : ', format(stat.max_loss, '10,.2f'))
    print('max gain         : ', format(stat.max_gain, '10,.2f'))

def save_mid_values(candle_data, buy_price, sell_price, profit, total_profit, dd) :
    candle_data['buy_price'] = buy_price # buy 여부 저장
    candle_data['sell_price'] = sell_price # buy 여부 저장
    candle_data['profit'] = profit # profit 저장
    candle_data['total_profit'] = total_profit # total_profit 저장
    candle_data['dd'] = dd # downd draw 저장

def handle_fee(balance, stat, num_buying, price,  trading_fee) :
    fee = num_buying * price * trading_fee
    stat.total_fee += fee
    balance -= fee
    return balance

#
# simulation 통계와 관련된 함수들
#
class sim_stat :
    def __init__(self) :
        self.num_trading = 0
        self.total_profit = 0
        self.total_fee = 0
        self.num_winning = 0
        self.num_losing = 0
        self.max_loss = 0
        self.max_gain = -10000000
        self.mdd = 0

    def update_stat(self, profit) :
        self.total_profit += profit # 누적 수익
        if profit > 0 :
            self.num_winning += 1
        else :
            self.num_losing += 1

        # 최대 손실, 최고 이익 값 update
        if self.max_loss > self.total_profit :
            self.max_loss = self.total_profit
        if self.max_gain < self.total_profit :
            self.max_gain = self.total_profit
                    
        # draw down 계산
        dd = 100.0 * (self.max_gain - self.total_profit) / self.max_gain
        if dd > self.mdd :
            self.mdd = dd  # mdd 계산
        return dd

def simulation(ticker, sim_file, tr_login) :
    # simulation 데이터를 읽는다.
    candle_data = read_csv_to_dict(sim_file)
    if candle_data == [] :
        print('not exist ', sim_file)
        return

    # simulation 중 파일에 저장할 변수들 추가
    save_mid_values(candle_data[-1], 0, 0, 0, 0, 0)

    # 제일 마지막 일봉이 어제 candle
    yest = candle_data[len(candle_data)-1]

    # 가장 오래된 일봉 데이터로 candle을 만든다.
    candle = Candle()
    candle.new_candle(yest)
    
    # 어제 일봉 setting
    tr_logic.update_new_range(candle)

    deposit = 1000000   # 1회 최대 1백만원 매수
    balance = deposit   # 현재 잔고

    bought = 0          # 매수 중인지 여부
    trading_fee = 0.00035  # 매매 수수료
    num_buying = 0      # 현재 매수 수량
    
    stat = sim_stat()   # 통계 변수용 class

    for i in range(len(candle_data)-2,-1,-1)  :# 내림차순으로 저장되어 있으므로 뒤에서 한개씩
        #현재 simulation 데이터로 candle을 만든다.
        candle = Candle()
        candle.new_candle(candle_data[i])
                        
        # simulation 중 파일에 저장할 변수들 추가
        save_mid_values(candle_data[i], 0, 0, 0, 0, 0)

        buy_price = tr_logic.is_enter_condition(candle) 
        if buy_price > 0 : # 매수조건임
            # 1. 매수 금액 결정, min(balance, deposit) 초기 deposit 금액 혹은 balance가 초기 deposit 이하이면 balance
            buying_amount = min(balance, deposit)
            num_buying = buying_amount / buy_price    # 매수 주수

            # 3. 수수료
            balance = handle_fee(balance, stat, num_buying, buy_price,  trading_fee) # 매수 수수료

            # 4. update statistics
            stat.num_trading += 1  # 매수한 주문 수
            
            # 5. adding log
            save_mid_values(candle_data[i], buy_price, candle_data[i]['sell_price'], 0, stat.total_profit, 0)

            # 매수 중이라고 설정
            bought = 1

        if bought : # exit 조건 확인
            sell_price = tr_logic.is_exit_condition(candle)
            if sell_price > 0 : # exit 조건
                # 2. 일봉 종가에 판다고 가정
                profit = (candle.close - buy_price) * num_buying
                balance += profit

                # 3. 매도 수수료
                balance = handle_fee(balance, stat, num_buying, sell_price, trading_fee) # 매도 수수료

                # 4. update statistics
                dd = stat.update_stat(profit)
                
                # 5. adding log
                save_mid_values(candle_data[i], candle_data[i]['buy_price'], sell_price, profit, stat.total_profit, dd)

                # 매도 완료
                bought = 0

    fname = ticker + '-LW-result-all.csv'
    save_to_file_csv(fname, candle_data)

    # print simulation results
    print_sim_result(ticker, stat)

    # save simulation results
    fname = ticker + '-LW-result-all.txt'
    save_sim_result(fname, ticker, stat)

    print('exit')


if __name__ == '__main__':

    #  back data
    fname = '.\\sim_data\\BTC_day-2017-09-25-2020-11-12.csv'
    ticker = 'KRW-BTC'

    # Larry William 변동성 돌파, 일봉 사용
    tr_logic = TR_LW('day', 1)

    simulation(ticker, fname, tr_logic)
    print('')
