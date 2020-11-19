# date : 2020/11/19
# 시뮬레이션에 사용하는 candle class
#
# 보다 자세한 내용을 아래 tistory 참고
# https://money-expert.tistory.com/34
#

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

    def new_candle(self, data) :  # upbit 데이터로 candle 만들기 
        dt = data['candleDateTimeKst'].split('T')
        self.date = dt[0]
        dtt = dt[1].split('+')
        self.time = dtt[0]
        self.open = float(data['openingPrice'])
        self.high = float(data['highPrice'])
        self.low = float(data['lowPrice'])
        self.close = float(data['tradePrice'])
        self.vol = float(data['candleAccTradeVolume'])

    def print(self) :
        print(self.date, self.time, self.open, self.high, self.low, self.close, self.vol)

if __name__ == '__main__':

    print('my_candle')
