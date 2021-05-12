import time
import pyupbit
import datetime
import requests

access = "your access"
secret = "your secret"
myToken = "xoxb-your-token"
def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

def get_20minutes_high(ticker):
    df = pyupbit.get_ohlcv(ticker, interval='minute1', count=20)
    max_open = df['open'].max()
    max_close = df['close'].max()
    return max(max_open, max_close)

def get_10minutes_low(ticker):
    df = pyupbit.get_ohlcv(ticker, interval='minute1', count=10)
    min_open = df['open'].min()
    min_close = df['close'].min()
    return min(min_open, min_close)

def get_ATR(ticker):
    df = pyupbit.get_ohlcv(ticker, interval='minute1', count=20)
    df['ATR'] = df['high'] - df['low']
    means = df.mean()
    return means['ATR']




# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
post_message(myToken,"#crypto", "autotrade start")
# 자동매매 시작
# 터틀트레이딩 규칙
# 1. 20일 신고가 상향 돌파시 매수
# 2. 10일 신저가 하향 돌파시 매도
# 3. 주가 < 매수가 - 2*ATR 시 손절
# 4. 전체 계좌의 2% = 2*ATR 이 되는 금액만큼만 매수하고, 가격이 ATR 상승시 추가 매수

krw = get_balance('KRW')
if krw > 10000:
    have = 0
else:
    have = 1

ticker = 'KRW-DOGE'

while True:
    try:
        if have == 0: # 매수한 코인이 없을 때
            target_price = get_20minutes_high(ticker)
            current_price = get_current_price(ticker)
            if target_price < current_price: # 20분 신고가를 상향 돌파시 매수
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order(ticker, krw * 0.9995)
                    have = 1
                    post_message(myToken, "#crypto", "BTC buy : " + str(buy_result))
        else: # 이미 코인을 보유중일 때
            ATR = get_ATR(ticker)
            abp = upbit.get_avg_buy_price(ticker) # 매수 평균가
            target_price = get_10minutes_low(ticker) # 10일 신저가
            current_price = get_current_price(ticker)
            btc = get_balance('DOGE')
            if target_price >= current_price: # 10분 신저가를 하향 돌파시 매도
                #if btc > 0.00008:
                sell_result = upbit.sell_market_order(ticker, btc)
                post_message(myToken, "#crypto", "BTC buy : " + str(sell_result))
                have = 0
            elif current_price < (abp - 3 * ATR):  # 주가 < 매수가 - 3*ATR 시 손절
                #if btc > 0.00008:
                sell_result = upbit.sell_market_order(ticker, btc)
                post_message(myToken, "#crypto", "BTC buy : " + str(sell_result))
                have = 0

        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken, "#crypto", e)
        time.sleep(1)