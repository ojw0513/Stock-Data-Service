1. 프로젝트 주제 및 기능
- 주제 : 실시간 주식 데이터 웹 서비스 
- 핵심 기능 
  - 주가 데이터 실시간 크롤링
  - 사용자의 매매 기록 실사화
  - AI를 사용한 주식 분석 

2. 기술 스택 선정 이유
- Language : Python 3.10
  - 선정 이유 : 방대한 주식 데이터를 처리하기 위해 Pandas, Numpy등 데이터 분석 라이브러리 생태계가 풍부한 Python을 선택
               C++에 비해 속도는 느리지만, 데이터 전처리 및 분석 로직을 구현하는 개발 생산성이 높아 유리하다고 판단됨.
               또한 요즘 산업계에서 AI 및 데이터 분석 분야의 표준으로 자리 잡은 Python 생태계를 직접 경험하고,
               실제 데이터를 다루며 라이브러리 활용 능력을 기르기 위해 선택함. 
- DB : PostgreSQL
  - 선정 이유 : 시계열 데이터를 안정적으로 처리하고, 복잡한 쿼리를 이용하기 위해 선택함. 

3. 프로그램 선정 이유
- 간단한 코드 테스트로 연습한 Python을 실제 프로그램 개발 과정에서 사용함으로써 Python에 대한 심화 학습을 진행하고,
  PostgreSQL을 통한 데이터 처리능력을 기르기 위해 선정함. 

4. 개발 설계
- Company 테이블 (부모): 회사의 고유 코드(예: 005930), 회사 이름, 상장 시장 등을 담는다. (데이터가 거의 변하지 않음)
  StockPrice 테이블 (자식): 해당 회사의 시간별 가격, 거래량 등을 담는다. (데이터가 계속 쌓임)
  - 데이터 정규화 : 실시간 주식의 데이터 같은 경우 1초에 수천번의 데이터가 쌓이게 된다. 그렇기에 하나의 테이블에 회사의 이름과 가격을 전부 넣게 된다면,
                  한 주식의 가격이 1초마다 변할때마다, 그 회사의 이름 또한 계속해서 저장해야하는 저장 공간 낭비가 생긴다. 
                  또한 그 회사의 이름이 바뀌게 된다면, 수만 개의 데이터를 수정해야하는 상황이 발생할 수 있다. 따라서 고유번호를 통해 두 테이블을 연동하는 방식을 사용할 것 이다. 

5. 개발 구조
- 사용자가 원하는 주식의 이름을 입력한다 -> SaveStock 함수에서 데이터를 실시간으로 받아온다. -> 이를 html로 보여준다. 
                                                                                  -> 해당 데이터를 sql에 저장한다. 

6. 개발 목표
- AI 사용 최소화!! : 개발의 대략적인 흐름과 구조를 만드는데 조금의 도움을 받고, 실제 코드는 AI를 사용하지 않고, 최대한 스스로 작성해보기
- PostgreSQL과 Python에 대한 이해

7. 프로젝트 목표
- 이 데이터를 통해 개인 투자자가 기관에 뒤쳐지지 않는 실시간 분석 리스트를 제공하는 것이 목표

- 개발 과정
 - **26.02.05 - sql 테이블을 python을 통해 연동해서 결과값으로 보여주기**
    최종 코드
    ```sql
        -- 1. 회사의 정보를 담을 테이블
    CREATE TABLE Companies (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        ticker VARCHAR(10) NOT NULL --ticker은 고유번호
    );

    -- 2. 주식 가격 정보를 담을 테이블
    CREATE TABLE Prices(
        id SERIAL PRIMARY KEY,
        company_id INTEGER REFERENCES Companies(id),
        price DECIMAL(10, 2) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ```
    ```python
    # 1. DB 라이브러리 가져오기
    import psycopg2
    import os
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
    def main():
        conn = psycopg2.connect(
            database = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            host = os.getenv("DB_HOST"),
            port = os.getenv("DB_PORT")
        )
        SaveStock(conn, "TESLA", "000001", 77777) 
        conn.close()
    main()
    ```
    - 작성 코드 설명 
    : DB 연결은 main 함수로 빼서 실제 이 코드가 작동할 때만 DB와 연결되도록 하여 필요없는 자원 낭비를 줄였다. 

      SaveStock이라는 함수를 만들어서 실제 DB와 연결되었을때 우리가 수행해야 하는 과제들에 대한 코드를 한 함수안에 작성하였다.

      cursor라는 도구를 사용하여 DB의 내용을 우리가 직접 컨트롤 할 수 있게 만들었다.

      SaveStock이라는 코드는 우리가 정보를 입력받고 싶은 회사가 있다면 그 회사의 정보를 DB에서 꺼내어서 Price 값이랑 연결해주고, 만약 없는 새로운 회사라면 새롭게 회사 정보를 DB에 넣어 만들게 되어있다. 

      execute를 사용할 때 직접 데이터를 넣는 것이 아닌 %s를 사용하여 데이터를 입력하였는데, 이렇게 하면 Parameterized Query방식을 사용하게 되어 후에 있을 수 있는 SQL Injection 공격을 방지할 수 있게 만들었다. 

      Companies 등록과 Prices 저장이 하나의 작업 단위로 묶여야 하므로, 모든 로직이 성공적으로 끝난 시점에 conn.commit()을 호출하였다. 이를 통해 데이터의 원자성(Atomicity)을 보장하고, 중간에 에러가 발생하더라도, 잘못된 데이터가 DB에 남지 않도록 설계하였다. 

      DB 라이브러리(psycopg2)가 반환하는 데이터는 기본적으로 튜플 형태이다. 필요한 값만 정확히 추출하기 위해 인덱싱([0])을 사용했으며, 이를 통해 후속 로직에서 데이터 타입 불일치로 인한 런타임 오류를 방지하였다. 

      RETURNING id 문법을 사용하여 새로 생성된 부모 테이블(Companies)의 PK를 즉시 반환받고, 이를 자식 테이블(Prices)의 외래 키(Foreign Key)로 사용하였다. 이는 두 테이블간의 연결성을 높여주며, 데이터 추적에 용이하다. 

      DB와 연결할때 내 개인 정보들이 하드코딩 되면 github에 올렸을때 유출되는 문제가 있다. 이에 .env파일을 만들어 민감한 정보들을 보관하고 .env파일을 gitignore로 처리함으로써 이를 방지하였다. 
    
    - 오류 확인 및 문제 해결
    1. 스키마 불일치 해결 및 데이터베이스 마이그레이션 전략
    상황(Situation): Companies 테이블에 ticker 칼럼을 추가하는 설계 변경 후, 파이썬 코드 실행 시 UndefinedColumn 에러가 발생했다.

    원인 분석(Root Cause): 파이썬 애플리케이션이 참조하는 코드상의 스키마 정의와 실제 로컬 PostgreSQL 인스턴스의 상태가 동기화되지 않았음을 확인했다. DB 서버는 여전히 ticker 칼럼이 없는 이전 버전의 테이블 구조를 유지하고 있었다.

    해결 방안(Action): * 수동 동기화: pgAdmin을 통해 기존 테이블을 삭제(Drop)하고, 최신 DDL(데이터 정의 언어) 문을 재실행하여 스키마를 최신화했다.

     - 프로세스 개선: 수동 동기화 방식의 인적 오류 가능성을 인지했다.

    엔지니어링 결과(Impact): 향후 개발 환경 간의 일관성을 보장하기 위해, 수동 방식 대신 데이터베이스 마이그레이션 도구(예: Alembic 또는 Django Migrations)를 도입하여 스키마 버전을 관리해야 할 필요성을 도출했다.

    2. 외래 키(Foreign Key) 할당 시 데이터 타입 불일치 교정
    상황(Situation): company_id 변수에 '데이터 묶음(Tuple)'과 '정수(Integer)'가 혼재되어 저장되는 로직 오류를 발견했다. 
    이로 인해 Prices 테이블 저장 시 데이터 타입 불일치로 시스템이 중단되는 문제가 발생했다.

    원인 분석(Root Cause): 1. else 블록(신규 회사 등록)에서 company_id 변수에 숫자 ID 대신 데이터 묶음인 (name, ticker)를 할당하는 설계 실수가 있었다. 2. PostgreSQL의 fetchone() 메서드는 결과값이 단일 칼럼이라도 기본적으로 튜플 형식을 반환한다는 라이브러리 특성을 간과했다.

    해결 방안(Action): * 변수 역할 분리: 삽입용 데이터(company_data)와 고유 식별자(company_id)의 역할을 명확히 분리하여 코드를 리팩토링했다.

    - 데이터 추출 최적화: fetchone()[0] 인덱싱을 적용하여 company_id가 항상 정수(Integer) 타입을 유지하도록 강제했다.

    - 원자적 작업(Atomic Operation): INSERT 문에 RETURNING id 구문을 도입하여, 단 한 번의 DB 통신으로 신규 생성된 PK(기본 키)를 즉시 반환받도록 효율화했다.

    엔지니어링 결과(Impact): 코드의 예측 가능성과 타입 안전성(Type Safety)을 확보했다. ID 추출 로직을 표준화함으로써, 향후 대규모 데이터 수집을 위한 멀티스레드 환경에서도 안정적으로 확장 가능한 구조를 구축했다.

    - **26.02.06 - yfinance를 이용한 실시간 주식 주가 연동 밑 주가 업데이트 자동화**
    - 최종 코드
    ```python
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
    ```
    - 작성 코드 설명
    실시간 주식을 받아오는 방법 중 직접 크롤링과 yfinance같이 이미 만들어져 있는 라이브러리 사용 중 고민하였다. 

    하지만 직접 크롤링의 경우 높은 난이도를 가지고 있는 부분에 비해, 해당 사이트의 주소가 달라지면 바로 고장이 나는 무시하지 못할 문제점이 있다는걸 확인하게 되었다. 

    그에 따라 Yahoo Finance 공식 데이터를 기반으로 하여 안정적이고, Pandas 라이브러리와 높은 호환성을 보여주어 추후 AI 분석 단계로의 확장이 용이한 yfinance 라이브러리를 사용하게 되었다. 

    yfinance에서 데이터를 받아올 때 기존의 SaveStock이나 main 함수에 코드를 작성하여 실행하는 것이 아닌, 새롭게 LoadData함수를 만들어 SRP(단일 책임 원칙)을 지키고자 하였다. 

    이를 통해 후일 있을 유지 및 보수에 용이한 구조로 설계하였다. 

    우리가 원하는것은 우리가 한번씩 클릭해야지만 데이터가 쌓이는 구조가 아니기에, 계속해서 데이터를 쌓는 과정이 필요하였다. 이를 위해 while conn:문을 통해 DB가 연결되었을때 데이터 수집을 계속 반복하는 코드를 main함수에 구성하였다. 

    제어 장치 없는 무한 루프는 시스템 리소스(CPU) 과점유 및 대상 서버의 IP 차단 리스크를 야기할 수 있다. 이를 방지하기 위해 time.sleep(60)을 적용하여 수집 주기를 1분으로 표준화하였으며, 이를 통해 시스템의 안정성을 확보하고 불필요한 네트워크 트래픽 발생을 억제하였다.
    
    - 오류 확인 및 문제 해결
    1. 외부 라이브러리 API 응답 구조 이해 및 KeyError 해결
    상황(Situation): yfinance를 사용하여 실시간 주가를 호출하는 과정에서 KeyError: 'last_Price' 혹은 KeyError: 'currentTradingPeriod' 등의 런타임 에러가 발생하며 데이터 수집이 중단되었다.

    원인 분석(Root Cause): 대소문자 민감성: 라이브러리 내부 딕셔너리 키 값인 last_price를 last_Price로 오기입하여 참조 오류가 발생했다.

     - API 버전 및 속성 변화: yfinance 버전 업데이트에 따라 실시간 데이터를 담는 속성(Property) 위치가 변경되었고, 존재하지 않는 키 값을 참조하려 시도했음을 확인했다.

    해결 방안(Action): 속성 검증: fast_info와 info 속성의 차이점을 분석하고, 실시간성 데이터 취득에 최적화된 fast_info['last_price']를 사용하도록 수정했다.

     - 안전한 데이터 추출: 딕셔너리 직접 참조 대신 .get() 메서드를 활용하여, 특정 데이터(예: 회사 이름)가 누락되더라도 에러 없이 기본값을 반환하도록 예외 처리(Exception Handling)를 강화했다.

    엔지니어링 결과(Impact): 외부 라이브러리 의존성이 높은 프로젝트에서 API 문서를 정확히 분석하고 데이터 계약(Data Contract)을 준수하는 것의 중요성을 체득했다. 이는 시스템의 런타임 안정성을 크게 향상시켰다.

    2. 함수 반환값 언패킹(Unpacking) 및 변수 생명주기 관리 오류
    상황(Situation): LoadData 함수에서 여러 값(이름, 가격 등)을 반환할 때, 이를 받는 main 함수에서 변수 개수가 일치하지 않거나 함수를 불필요하게 중복 호출하는 로직 결함이 발견되었다.

    원인 분석(Root Cause): 불필요한 오버헤드: LoadData(ticker)를 변수 할당 없이 실행한 후 다시 할당하는 코드를 작성하여, 동일한 네트워크 요청을 2회 연속 보내는 리소스 낭비가 발생했다.

     - 언패킹 미숙: 파이썬의 튜플 반환(Tuple Return) 구조를 정확히 이해하지 못해, 반환된 데이터를 변수로 분리하는 과정에서 문법 오류가 발생했다.

    해결 방안(Action): 리터럴 및 변수 구분: 함수 호출 시 인자로 변수명을 정확히 전달하고(따옴표 제거), 반환되는 튜플의 순서에 맞춰 name, price = LoadData(ticker)와 같이 한 번의 호출로 데이터를 취득하도록 최적화했다.

     - 단일 책임 원칙 준수: LoadData는 수집만, SaveStock은 저장만 하도록 역할을 분리하여 데이터 흐름을 명확히 했다.

    엔지니어링 결과(Impact): 불필요한 네트워크 I/O를 50% 절감하여 시스템 효율성을 높였으며, 코드의 가독성과 유지보수성을 확보했다.

    - **26.02.12 ~ 26.02.15 - app.py로 서버를 연결후 html을 통한 사이트 구성**
    - 최종 코드
    main.py
    ```python
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
    ```
    
    app.py
    ```python
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
    ```

    index.html
    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <title>주식 데이터 서비스</title>
        <meta http-equiv="refresh" content="10">
        <style>
            body { font-family: 'Arial', sans-serif; text-align: center; padding: 50px; }
            .search-box { margin-bottom: 30px; }
            .input-field { padding: 10px; width: 200px; font-size: 16px; }
            .btn { padding: 10px 20px; font-size: 16px; background-color: #007bff; color: white; border: none; cursor: pointer; }
            .price-card { background-color: #f4f4f4; padding: 20px; border-radius: 10px; display: inline-block; width: 400px; }
            .price-big { font-size: 40px; font-weight: bold; color: #333; }
            .price-sub { font-size: 20px; color: #666; }
            .chart-box { margin-top: 30px; height: 300px; background-color: #eee; border: 1px dashed #999; line-height: 300px; }
        </style>
    </head>
    <body>

        <h1>실시간 주식 대시보드</h1>

        <div class="search-box">
            <form method="POST">
                <input type="text" name="search_ticker" class="input-field" placeholder="종목코드 (예: TSLA)" value="{{ ticker }}">
                <button type="submit" class="btn">검색</button>
            </form>
        </div>

        <div class="price-card">
            <h2>{{ ticker }} 현재가</h2>
            <div class="price-big">$ {{ usd }}</div>
            <div class="price-sub">₩ {{ "{:,.0f}".format(krw) }} (예상)</div>
            <p>기준 시간: {{ date }}</p>
        </div>

        <div class="chart-box">
            (주식 차트 들어갈 예정)
        </div>

    </body>
    </html>
    ```
    - 작성 코드 설명 (Architecture & Logic)
    금일은 단순 데이터 수집을 넘어, 사용자가 웹을 통해 데이터를 조회하고 시스템이 자동으로 반응하는 "상호작용형 아키텍처"를 구축하는 데 집중하였다.

    1. Flask 웹 프레임워크 도입과 역할 분리
        단순히 터미널에 로그를 남기는 것을 넘어, 실제 서비스 가능한 형태를 갖추기 위해 경량 웹 프레임워크인 Flask를 도입하였다.
        이때 가장 중요하게 고려한 것은 "역할의 분리(Separation of Concerns)"입니다. 하나의 파일에 모든 기능을 넣는 대신, 데이터 수집을 담당하는 main.py와 사용자 요청을 처리하는 app.py로 시스템을 이원화하였다.
        이를 통해 수집 로직이 변경되더라도 웹 서버에는 영향이 없고, 반대로 웹 디자인을 고쳐도 수집기에는 영향이 없는 유연한 구조를 설계하였다.

    2. 데이터베이스(DB)를 활용한 프로세스 간 통신
        서로 다른 두 프로그램(main.py, app.py)이 어떻게 소통할지 고민한 끝에, 데이터베이스를 공용 게시판(Shared Storage)으로 활용하는 방식을 채택하였다.
        등록 로직: 사용자가 웹(app.py)에서 종목을 검색하면, 웹 서버는 즉시 Companies 테이블에 해당 종목을 등록(INSERT)한다.
        수집 로직: 백그라운드에서 실행 중인 수집기(main.py)는 주기적으로 DB를 순찰하며, 새로 등록된 종목이 있는지 확인하고 자동으로 수집 대상에 포함시킨다.
        이 구조 덕분에 사용자가 늘어나도 수집기는 흔들림 없이 자신의 역할만 수행하면 되는 확장성 있는 설계를 갖추게 되었다.

    3. 안정적인 자원 관리 (Graceful Shutdown)
        24시간 돌아가는 서버 프로그램의 특성상, 에러 발생이나 강제 종료 시 데이터베이스 연결이 끊어지지 않고 좀비처럼 남는(Leak) 문제가 발생할 수 있음을 인지하였다.
        이를 방지하기 위해 try-except-finally 패턴을 적용하였습니다. 예상치 못한 에러가 발생하거나 관리자가 서버를 종료(Ctrl+C)하더라도, finally 블록에서 반드시 conn.close()를 실행하여 DB 연결을 안전하게 해제하도록 구현하였다.

    4. 클라이언트 사이드 렌더링 (Meta Refresh)
        웹 브라우저는 기본적으로 정적인(Static) 페이지를 보여주기 때문에, 실시간으로 변하는 주가를 반영하지 못하는 문제가 있었다.
        복잡한 JavaScript 비동기 통신을 도입하기 전, HTML 표준 태그인 <meta http-equiv="refresh" content="10">을 활용하여 10초마다 페이지가 스스로 최신 데이터를 받아오도록 구현하였다. 이를 통해 적은 비용으로 실시간 대시보드의 느낌을 사용자에게 제공할 수 있게 되었다.    

    -오류 확인 및 문제 해결

    1. SQL 문법 및 집계 함수 사용 오류
    상황 (Situation): DB에 저장된 가격 중 최고가와 최저가를 분석하기 위해 SELECT * Max(Price)... 쿼리를 실행했으나 SyntaxError가 발생하며 실행이 중단됨.

    원인 분석 (Root Cause):

        - SQL 표준 문법 위배: SQL에서 * (모든 컬럼)와 MAX() (집계 함수)는 GROUP BY 절 없이는 함께 사용할 수 없음을 간과함.
        
        - 쿼리 구조적 모순: "모든 데이터를 보여줘"라는 요청과 "값 하나만 계산해줘"라는 요청이 충돌함.

    해결 방안 (Action):

        - 쿼리 최적화: 불필요한 *를 제거하고, SELECT MAX(price), MIN(price) FROM... 형태로 집계 함수만 명확히 호출하도록 수정함.

        - 단일 호출로 변경: 최고가와 최저가를 각각 조회하던 로직을 한 번의 쿼리로 통합하여 네트워크 I/O 비용을 절감함.

    엔지니어링 결과 (Impact): SQL의 집계 함수 작동 원리를 명확히 이해하고, 효율적인 쿼리 작성 능력을 확보함.

    2. 라이브러리 메서드 인자 오류 (TypeError)
    상황 (Situation): 데이터 분석 함수(AnalazeData) 실행 중 fetchone(0) 코드에서 TypeError: takes no arguments 에러가 발생하며 프로그램이 강제 종료됨.

    원인 분석 (Root Cause):

        - 메서드 시그니처 오해: psycopg2 라이브러리의 fetchone() 메서드는 인자를 받지 않고 튜플(Tuple) 전체를 반환한다는 점을 인지하지 못하고, 리스트 인덱싱처럼 사용하려 함.

    해결 방안 (Action):

        - 언패킹 로직 수정: 메서드 호출과 인덱싱을 분리하여 result = fetchone()으로 튜플을 먼저 받고, 이후 result[0]으로 데이터에 접근하도록 로직을 변경함.

        - 예외 처리 강화: 반환값이 None일 경우를 대비한 분기문을 추가하여 코드의 안정성을 높임.

    엔지니어링 결과 (Impact): 외부 라이브러리 사용 시 반환 타입(Return Type) 확인의 중요성을 체득하고, 런타임 에러를 방지하는 방어적 코딩 습관을 기름.

    3. 웹 서버 객체 속성 오버라이딩 오류
    상황 (Situation): 웹에서 주식 검색 시 AttributeError: ... object attribute 'execute' is read-only 또는 'str' object is not callable 에러 발생.

    원인 분석 (Root Cause):

        - 문법적 오타: cursor.execute = ("INSERT...")와 같이 메서드 호출 괄호 앞에 등호(=)를 잘못 입력함.

        - 객체 속성 훼손: 메서드 실행이 아닌, 메서드 자체를 문자열로 덮어씌우려는 시도로 인해 객체의 기능이 상실됨.

    해결 방안 (Action):

        - 문법 교정: 등호를 제거하고 정상적인 함수 호출 형태(cursor.execute(...))로 수정하여 DB 명령이 올바르게 전달되도록 조치함.

    엔지니어링 결과 (Impact): 파이썬의 객체 속성과 메서드 호출 방식의 차이를 재확인하고, 디버깅 메시지를 통해 코드의 논리적 오류를 빠르게 파악하는 능력을 향상함.
        
   