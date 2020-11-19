# date : 2020/11/19
# Larry Williams 변동성 돌파전략
#
# 보다 자세한 내용을 아래 tistory 참고
# https://money-expert.tistory.com/34
#
import json
from my_util import *
from my_candle import *

class TR_LW() :
    def __init__(self, interval, num) :
        self.interval = interval # min', 'day'
        self.interval_num = num # 1, 5, 20, 60
        self.pre  = None
        self.cur  = None
        self.k = 0.5
        self.bought = 0 # 현재 매수 중인지
        self.history = []
        self.range = 0

        self.ADX = 1
        self.MA = 0

    def update_new_range(self, cur) : # 
        self.pre  = cur
        self.history.append(cur)
        self.range = cur.high - cur.low # 전 candle의 range

    # 진입조건 조사
    def is_enter_condition(self, candle) :  
        enter = 0
        if self.range > 0 :
            buy_price = (candle.open + self.range * self.k)
            if candle.high > buy_price :  # 최고가가 buy_price보다 높으면 매수되었다고 가정
                enter = 1

        # 오늘 candle update
        self.update_new_range(candle)
        
        if enter :
            return buy_price
        return 0

    # 조건 조사
    def is_exit_condition(self, candle) :
        return candle.close  # 일봉 종가에 무조건 판다

if __name__ == '__main__':
    
    print('TR_LW')
