from flask import Flask, render_template, request
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

    # DB에서 최신 가격 하나만 가져오는 함수
def get_latest_price(ticker):
        conn = psycopg2.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cursor = conn.cursor()
        
        # 가장 최근 시간의 가격 1개 조회
        # Prices 테이블과 Companies 테이블을 조인해서 가져옴
        sql = """
        SELECT p.price, p.created_at 
        FROM Prices p
        JOIN Companies c ON p.company_id = c.id
        WHERE c.ticker = %s
        ORDER BY p.created_at DESC
        LIMIT 1
        """
        cursor.execute(sql, (ticker,))
        result = cursor.fetchone()
        conn.close()
        
        return result if result else (0, "데이터 없음")

    # 1. 메인 페이지 접속 
@app.route('/', methods=['GET', 'POST'])
def index():
        ticker = "TSLA" # 기본값
        price = 0
        date = ""
        exchange_rate = 1400 # 환율 (일단 고정값, 나중에 라이브러리로 가져오자)

        conn = psycopg2.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cursor = conn.cursor()
        # 검색창에 입력을 했다면?
        if request.method == 'POST':
            ticker = request.form.get('search_ticker')

            cursor.execute("SELECT * From Companies Where ticker = %s",(ticker,))
            result = cursor.fetchone()
        
        #  없으면? -> 회사 등록하고(INSERT) -> ID 받아오기
            if not result :
                cursor.execute("INSERT INTO Companies (name, ticker) VALUES(%s, %s) RETURNING id", (ticker, ticker))
                conn.commit()
            

        # DB에서 가격 가져오기
        data = get_latest_price(ticker)
        price_usd = float(data[0]) # 달러
        price_krw = price_usd * exchange_rate # 원화 계산
        date = data[1]
        conn.close()
        # index.html에 데이터 전달하기
        return render_template('index.html', 
                            ticker=ticker, 
                            usd=price_usd, 
                            krw=price_krw,
                            date=date)
        
if __name__ == '__main__':
    app.run(debug=True)
        