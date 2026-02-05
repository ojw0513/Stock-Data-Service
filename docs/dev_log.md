1. 프로젝트 주제 밑 기능
- 주제 : 실시간 주식 데이터 웹 서비스 
- 핵심 기능 
  - 주가 데이터 실시간 크롤링
  - 사용자의 매매 기록 실사화
  - AI를 사용한 주식 분석 

2. 기술 스택 선정 이유
- Language : Python 3.10
  - 선정 이유 : 방대한 주식 데이터를 처리하기 위해 Pandas, Numpy등 데이터 분석 라이브러리 생태계가 풍부한 Python을 선택
               C++에 비해 속도는 느리지만, 데이터 전처리 밑 분석 로직을 구현하는 개발 생산성이 높아 유리하다고 판단됨.
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
 - 26.02.05 - sql 테이블을 python을 통해 연동해서 결과값으로 보여주기
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
    작성 코드 설명 
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
    상황(Situation): Companies 테이블에 ticker 칼럼을 추가하는 설계 변경 후, 파이썬 코드 실행 시 UndefinedColumn 에러가 발생했습니다.

    원인 분석(Root Cause): 파이썬 애플리케이션이 참조하는 코드상의 스키마 정의와 실제 로컬 PostgreSQL 인스턴스의 상태가 동기화되지 않았음을 확인했습니다. DB 서버는 여전히 ticker 칼럼이 없는 이전 버전의 테이블 구조를 유지하고 있었습니다.

    해결 방안(Action): * 수동 동기화: pgAdmin을 통해 기존 테이블을 삭제(Drop)하고, 최신 DDL(데이터 정의 언어) 문을 재실행하여 스키마를 최신화했습니다.

     - 프로세스 개선: 수동 동기화 방식의 인적 오류 가능성을 인지했습니다.

    엔지니어링 결과(Impact): 향후 개발 환경 간의 일관성을 보장하기 위해, 수동 방식 대신 데이터베이스 마이그레이션 도구(예: Alembic 또는 Django Migrations)를 도입하여 스키마 버전을 관리해야 할 필요성을 도출했습니다.

    2. 외래 키(Foreign Key) 할당 시 데이터 타입 불일치 교정
    상황(Situation): company_id 변수에 '데이터 묶음(Tuple)'과 '정수(Integer)'가 혼재되어 저장되는 로직 오류를 발견했습니다. 이로 인해 Prices 테이블 저장 시 데이터 타입 불일치로 시스템이 중단되는 문제가 발생했습니다.

    원인 분석(Root Cause): 1. else 블록(신규 회사 등록)에서 company_id 변수에 숫자 ID 대신 데이터 묶음인 (name, ticker)를 할당하는 설계 실수가 있었습니다. 2. PostgreSQL의 fetchone() 메서드는 결과값이 단일 칼럼이라도 기본적으로 튜플 형식을 반환한다는 라이브러리 특성을 간과했습니다.

    해결 방안(Action): * 변수 역할 분리: 삽입용 데이터(company_data)와 고유 식별자(company_id)의 역할을 명확히 분리하여 코드를 리팩토링했습니다.

    - 데이터 추출 최적화: fetchone()[0] 인덱싱을 적용하여 company_id가 항상 정수(Integer) 타입을 유지하도록 강제했습니다.

    - 원자적 작업(Atomic Operation): INSERT 문에 RETURNING id 구문을 도입하여, 단 한 번의 DB 통신으로 신규 생성된 PK(기본 키)를 즉시 반환받도록 효율화했습니다.

    엔지니어링 결과(Impact): 코드의 예측 가능성과 타입 안전성(Type Safety)을 확보했습니다. ID 추출 로직을 표준화함으로써, 향후 대규모 데이터 수집을 위한 멀티스레드 환경에서도 안정적으로 확장 가능한 구조를 구축했습니다.

   