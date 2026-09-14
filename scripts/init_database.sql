-- 博弈交易法智能分析系统 - 数据库初始化脚本
-- PostgreSQL + TimescaleDB

-- ========== 启用TimescaleDB扩展 ==========
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ========== 时序数据库表 (TimescaleDB) ==========

-- 股票日线数据表
CREATE TABLE IF NOT EXISTS stock_daily (
    time        TIMESTAMPTZ NOT NULL,
    stock_code  VARCHAR(10) NOT NULL,
    open        DECIMAL(10,2),
    high        DECIMAL(10,2),
    low         DECIMAL(10,2),
    close       DECIMAL(10,2),
    volume      BIGINT,
    amount      DECIMAL(18,2),
    turnover    DECIMAL(10,2),
    
    PRIMARY KEY (time, stock_code)
);

-- 转换为超表
SELECT create_hypertable('stock_daily', 'time', if_not_exists => TRUE, chunk_time_interval => INTERVAL '1 month');

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_stock_daily_code ON stock_daily (stock_code, time DESC);
CREATE INDEX IF NOT EXISTS idx_stock_daily_time ON stock_daily (time DESC);

-- Agent分析结果表
CREATE TABLE IF NOT EXISTS agent_analysis_results (
    time            TIMESTAMPTZ NOT NULL,
    stock_code      VARCHAR(10) NOT NULL,
    analysis_type   VARCHAR(50) NOT NULL,
    result          JSONB NOT NULL,
    confidence      DECIMAL(5,2),
    agent_version   VARCHAR(20),
    
    PRIMARY KEY (time, stock_code, analysis_type)
);

SELECT create_hypertable('agent_analysis_results', 'time', if_not_exists => TRUE, chunk_time_interval => INTERVAL '1 month');

-- ========== 关系数据库表 (PostgreSQL) ==========

-- 股票基本信息表
CREATE TABLE IF NOT EXISTS stock_info (
    stock_code      VARCHAR(10) PRIMARY KEY,
    stock_name      VARCHAR(50) NOT NULL,
    industry        VARCHAR(50),
    sector          VARCHAR(50),
    list_date       DATE,
    total_shares    BIGINT,
    float_shares    BIGINT,
    market_cap      DECIMAL(18,2),
    status          VARCHAR(20) DEFAULT 'ACTIVE',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户信息表
CREATE TABLE IF NOT EXISTS users (
    user_id         SERIAL PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    email           VARCHAR(100) UNIQUE,
    role            VARCHAR(20) DEFAULT 'USER',
    status          VARCHAR(20) DEFAULT 'ACTIVE',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 自选股表
CREATE TABLE IF NOT EXISTS watchlist (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(user_id),
    stock_code      VARCHAR(10) NOT NULL REFERENCES stock_info(stock_code),
    added_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, stock_code)
);

-- 持仓记录表
CREATE TABLE IF NOT EXISTS positions (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(user_id),
    stock_code      VARCHAR(10) NOT NULL REFERENCES stock_info(stock_code),
    stock_name      VARCHAR(50),
    buy_price       DECIMAL(10,2) NOT NULL,
    buy_quantity    INTEGER NOT NULL,
    buy_date        TIMESTAMP NOT NULL,
    current_price   DECIMAL(10,2),
    stop_loss_price DECIMAL(10,2),
    target_price    DECIMAL(10,2),
    status          VARCHAR(20) DEFAULT 'HOLDING',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 交易信号表
CREATE TABLE IF NOT EXISTS trading_signals (
    id              SERIAL PRIMARY KEY,
    signal_type     VARCHAR(20) NOT NULL,
    stock_code      VARCHAR(10) NOT NULL,
    stock_name      VARCHAR(50),
    price           DECIMAL(10,2),
    position_ratio  DECIMAL(5,2),
    reason          TEXT,
    confidence      DECIMAL(5,2),
    agent_decision  JSONB,
    signal_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until     TIMESTAMP,
    status          VARCHAR(20) DEFAULT 'PENDING'
);

-- 预警表
CREATE TABLE IF NOT EXISTS alerts (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(user_id),
    alert_type      VARCHAR(20) NOT NULL,
    stock_code      VARCHAR(10),
    title           VARCHAR(100) NOT NULL,
    message         TEXT,
    priority        INTEGER DEFAULT 5,
    agent_analysis  JSONB,
    status          VARCHAR(20) DEFAULT 'UNREAD',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 知识库表
CREATE TABLE IF NOT EXISTS knowledge_base (
    id              SERIAL PRIMARY KEY,
    knowledge_type  VARCHAR(50) NOT NULL,
    title           VARCHAR(200) NOT NULL,
    content         TEXT NOT NULL,
    tags            TEXT[],
    keywords        TEXT[],
    category        VARCHAR(50),
    embedding       VECTOR(1536),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建向量索引
CREATE EXTENSION IF NOT EXISTS vector;
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding ON knowledge_base 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    config_key      VARCHAR(100) PRIMARY KEY,
    config_value    JSONB NOT NULL,
    description     TEXT,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== 初始化默认数据 ==========

-- 创建默认用户
INSERT INTO users (username, password_hash, email, role)
VALUES ('admin', 'hashed_password_here', 'admin@boyi.com', 'ADMIN')
ON CONFLICT (username) DO NOTHING;

-- 插入系统配置
INSERT INTO system_configs (config_key, config_value, description)
VALUES 
    ('system_status', '{"status": "active"}', '系统状态'),
    ('agent_config', '{"model": "gpt-4", "temperature": 0.7}', 'Agent配置')
ON CONFLICT (config_key) DO NOTHING;

-- ========== 数据压缩策略 ==========
SELECT add_compression_policy('stock_daily', INTERVAL '3 months', if_not_exists => TRUE);
SELECT add_compression_policy('agent_analysis_results', INTERVAL '1 month', if_not_exists => TRUE);

-- ========== 数据保留策略 ==========
-- 分钟数据保留1年
-- SELECT add_retention_policy('stock_minute', INTERVAL '1 year', if_not_exists => TRUE);

-- ========== 完成提示 ==========
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '数据库初始化完成！';
    RAISE NOTICE '========================================';
    RAISE NOTICE '创建的表:';
    RAISE NOTICE '  - stock_daily (时序数据)';
    RAISE NOTICE '  - agent_analysis_results (Agent分析)';
    RAISE NOTICE '  - stock_info (股票信息)';
    RAISE NOTICE '  - users (用户)';
    RAISE NOTICE '  - watchlist (自选股)';
    RAISE NOTICE '  - positions (持仓)';
    RAISE NOTICE '  - trading_signals (交易信号)';
    RAISE NOTICE '  - alerts (预警)';
    RAISE NOTICE '  - knowledge_base (知识库)';
    RAISE NOTICE '  - system_configs (系统配置)';
    RAISE NOTICE '========================================';
END $$;
