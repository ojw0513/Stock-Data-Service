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