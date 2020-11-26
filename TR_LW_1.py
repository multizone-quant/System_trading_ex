# date : 2020/11/26
# Larry Williams 변동성 돌파전략 refactoring
#
# 보다 자세한 내용을 아래 tistory 참고
# https://money-expert.tistory.com/34
# https://money-expert.tistory.com/38
#
import json
from my_util import *
from my_candle import *

class TR_Basic() :
    def __init__(self, interval, num) :
        self.interval = interval # min', 'day'
        self.interval_num = num # 1, 5, 20, 60
        self.history = []

        self.bought_price = 0 # 매수하였으면 매수가. > 0 매수 중

        self.trend = 1
        self.MA = 0
        
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
        if len(self.history) == 0 :
            return 1
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
        buy_price = self.get_buy_price(candle)
        enter = self.is_meet_buy_cond(candle, buy_price)

        # 오늘 candle update
        self.update_new_candle(candle)
        
        if enter :
            self.bought_price = buy_price
            return buy_price
        return 0

    # 조건 조사
    # cut : 익절(1) 혹은 손절 (2)
    def is_exit_condition(self, candle) :
        exit = 0
        # 아래 세 조건 중에 원하는 조건 선택
        sell_price = self.get_sell_price(candle)
        exit, cut = self.is_meet_sell_cond(candle, sell_price)
        if exit :
            self.bought_price = 0
            return sell_price, cut

class TR_LW_SIM(TR_Basic) :
    def __init__(self, interval, num) :
        super().__init__(interval, num)
        self.range = 0
        self.k = 0.5

    def update_new_candle(self, cur) : # 
        self.history.append(cur)
        self.range = cur.high - cur.low # 전 candle의 range

        self.get_trend() # 추세값 계산
        self.get_MA(7) # 7일 단기 이평

    # 매수 조건을 만족하면 매수가를 돌려준다.
    def get_buy_price(self, candle) :
        if self.range > 0 :
            buy_price = (candle.open + self.range * self.k)
            return buy_price
        return 0

    # 현재 정보를 바탕으로 매수를 해야할지 결정
    # simulation이므로 candle.high > buy_price 이면 매수되었다고 가정한다.
    # 실제 매매할 때는 buy_price와 candle.high 사이 적절한 값을 결정
    def is_meet_buy_cond(self, candle, buy_price) :
        if candle.high > buy_price :  # 최고가가 buy_price보다 높으면 매수되었다고 가정
            return buy_price

    # candle 종가에 판다.
    def get_sell_price(self, candle) :
        return candle.close

    # 무조건 판다.
    def is_meet_sell_cond(self, candle, sell_price) :
        cut = 1 # 익절
        if sell_price < self.bought_price :
            cut = 2 # 손절
        return 1, cut

# 비추세구간은 매수 안함
class TR_LW_TREND(TR_LW_SIM) :
    # 매수 조건을 만족하면 매수가를 돌려준다.
    def get_buy_price(self, candle) :
        if self.range > 0 and self.trend > 0.2 : # trend 동시 적용
            buy_price = (candle.open + self.range * self.k)
            return buy_price
        return 0

# 비추세 + 이평선이 현재가 보다 아래인 경우에만 매수
class TR_LW_TREND_MA(TR_Basic) :
    def get_buy_price(self, candle) :
        if self.range > 0 and self.trend > 0.2 and (self.MA != 0 and self.MA < candle.open) : # trend & MA 동시 적용
            buy_price = (candle.open + self.range * self.k)
            return buy_price
        return 0

if __name__ == '__main__':
    
    print('TR_LW')
