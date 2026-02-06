# 1. DB 라이브러리 가져오기
import psycopg2
import os
import yfinance as yf
import time
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
    # 2-7. 연결 끊기 (Finally)
        cursor.close() 

def LoadData(ticker):
    ticker = yf.Ticker(ticker)

    Current_Price = ticker.fast_info['last_price']
    name = ticker.info.get('longName')
    print("현재 가격은 " , Current_Price)
    return name, Current_Price

def main():
    conn = psycopg2.connect(
        database = os.getenv("DB_NAME"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        host = os.getenv("DB_HOST"),
        port = os.getenv("DB_PORT")
    )
    # 2.1.1 찾기를 원하는 주식 받기
    ticker = input("찾고자 하는 주식의 고유번호를 입력하시오 : ")
    #LoadData(ticker)
    while conn:
        name, Current_Price = LoadData(ticker) 
        SaveStock(conn, name, ticker, Current_Price ) 
        print("데이터를 정상적으로 저장하였습니다.")
        time.sleep(60)
        
    conn.close()
main()