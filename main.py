# 1. DB 라이브러리 가져오기
import psycopg2
import os
import yfinance as yf
import time
import keyboard as kb
from dotenv import load_dotenv
#.env파일 로드
load_dotenv()
# 1-1. DB 연결하기 (비밀번호 필요)

# 2. 저장하는 함수 만들기 (인자는 종목코드, 가격)
def SaveStock(conn, name, ticker, price):
        if conn:
          print("연결이 정상적으로 실행되었습니다.")
        else:
          print("연결이 실행되지 않았습니다. 다시 연결해주세요")
    # 2-1. 커서(심부름꾼) 만들기
        cursor = conn.cursor() 
    # 2-2. 회사 있는지 확인해보기 (SELECT)
        cursor.execute("SELECT * From Companies Where ticker = %s",(ticker,))
        result = cursor.fetchone()
    # 2-3. 있으면? -> ID 가져오기
        if result != None:
              company_id = result[0]
    # 2-4. 없으면? -> 회사 등록하고(INSERT) -> ID 받아오기
        else :
              insert_company = "INSERT INTO Companies (name, ticker) VALUES(%s, %s) RETURNING id"
              company_data = (name, ticker)
              cursor.execute(insert_company, company_data)
              company_id = cursor.fetchone()[0]

        print(f"등록 완료! ID: {company_id}, 종목: {ticker}, price: {price}")
    # 2-5. 가격 저장하기 (INSERT)
        insert_price = ("INSERT INTO Prices (company_id, price) VALUES(%s, %s)")
        price_data = (company_id, price)
        cursor.execute(insert_price, price_data)
    # 2-6. 저장 확정(Commit)
        conn.commit()
        AnalazeData(conn, company_id) ##데이터를 가치있는 정보로 전환
    # 2-7. 연결 끊기 (Finally)
        cursor.close() 

def AnalazeData(conn, company_id):
    Analze_cursor = conn.cursor()
    Analze_cursor.execute("SELECT MAX(Price), MIN(Price) From Prices WHERE Company_id = %s", (company_id,))
    result = Analze_cursor.fetchone()
    Max_Price = result[0]
    Min_Price = result[1]

    

def LoadData(ticker):
    ticker = yf.Ticker(ticker)

    Current_Price = ticker.fast_info['last_price']
    name = ticker.info.get('longName')
    print("현재 가격은 " , Current_Price)
    return name, Current_Price

##def KeyEvent(e):
    if e.KeyEvent == keyboard.Key_DOWN:
        ss
def main():
    try:    
        conn = psycopg2.connect(
            database = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            host = os.getenv("DB_HOST"),
            port = os.getenv("DB_PORT")
        )
        
        #LoadData(ticker)
        while conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ticker FROM Companies")
            company_list = cursor.fetchall() 
            cursor.close()
 
            for company in company_list:
                target_ticker = company[0] # 튜플에서 알맹이 꺼내기 ('TSLA')
                
                try:
                    # 데이터 수집 및 저장
                    print(f" 수집 중: {target_ticker}")
                    name, Current_Price = LoadData(target_ticker) 
                    SaveStock(conn, name, target_ticker, Current_Price)
                    
                except Exception as e:
                    # 특정 종목 수집하다 에러나도(예: 상장폐지) 멈추지 않고 다음 종목으로!
                    print(f" {target_ticker} 에러 발생: {e}")
            
            # 3. 한 바퀴 다 돌았으면 휴식
            print(" 모든 종목 수집 완료. 1분 대기...")
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n사용자가 종료를 요청했습니다.")
    except Exception as e:
        # 여기가 핵심입니다! 어떤 에러가 났는지 범인을 지목합니다.
        print(f"예상치 못한 에러 발생: {e}")
        import traceback
        traceback.print_exc() # 에러가 난 위치를 정확히 추적해줍니다.
    finally:
        if conn:
            conn.close()    
main()