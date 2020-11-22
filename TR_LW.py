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

        self.trend = 1
        self.MA = 0

    def update_new_range(self, cur) : # 
        self.pre  = cur
        self.history.append(cur)
        self.range = cur.high - cur.low # 전 candle의 range

        self.get_trend() # 추세값 계산
        self.get_MA(7) # 7일 단기 이평
        
    # MA(n)을 구한다.
    def get_MA(self, num_days) :
        hist_len = len(self.history)
        if hist_len >= num_days :
            day_sum = 0
            pos = len(self.history)-1
            for i in range(num_days) :
                candle = self.history[pos]
                pos -= 1
                day_sum += candle.close # 종가 합
            self.MA = day_sum / num_days
            self.MA = float(format(self.MA, '.2f')) # 소숫점 2자리 값으로 변경
        return self.MA

    # 7일간 trend를 구한다.
    # A : 7일간 전체 움직임의 절대값 = abs(전일 가격 - 7일전 가격) 
    # B : 7일간 당일 움직임 절대값의 총합 : abs(7일전 시/종차)+ abs(6일전 시/종차)+ ...... abs(전일 시/종차) = 100
    # trend : A/B   trend = 1 이면 추세 (상방,하방 구분은 없음 단순히 추세, 비추세 구분)
    #             trend < 0.5 혹은 0.4 ( 비 추세 0.5로 할지 0.4로 할지 결정 필요 )
    # https://cafe.naver.com/invest79/939
    def get_trend(self) :
        cur = self.history[-1] # last one

        day_sum = 0
        candle = None
        hist_len = len(self.history)
        if hist_len >= 8 :
            range_total = 0
            pos = len(self.history)-1
            for i in range(7) :
                candle = self.history[pos]
                day_sum += abs(candle.open - candle.close) # candle 시/종가 차이의 절대치 합
                pos -= 1

            period_range = abs(candle.close - cur.close)
            self.trend = period_range / day_sum
            self.trend = float(format(self.trend, '.2f')) # 소숫점 2자리 값으로 변경

        return self.trend
    
    # 진입조건 조사
    def is_enter_condition(self, candle) :  
        enter = 0
        # 아래 세 조건 중에 원하는 조건 선택
#        if self.range > 0 :
#        if self.range > 0 and self.trend > 0.2 # trend 동시 적용
        if self.range > 0 and self.trend > 0.2 and (self.MA != 0 and self.MA < candle.open) : # trend & MA 동시 적용
    
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
