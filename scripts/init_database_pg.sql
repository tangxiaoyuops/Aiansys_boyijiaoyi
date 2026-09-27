-- 博弈交易法智能分析系统 - 数据库初始化脚本（纯PostgreSQL版）
-- 适配已有 postgres_db 容器 (PostgreSQL 15, user: kevin, db: boyi_trading)

-- ========== 时序数据表 ==========

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

CREATE INDEX IF NOT EXISTS idx_stock_daily_code ON stock_daily (stock_code, time DESC);
CREATE INDEX IF NOT EXISTS idx_stock_daily_time ON stock_daily (time DESC);

-- 股票分钟数据表
CREATE TABLE IF NOT EXISTS stock_minute (
    time        TIMESTAMPTZ NOT NULL,
    stock_code  VARCHAR(10) NOT NULL,
    open        DECIMAL(10,2),
    high        DECIMAL(10,2),
    low         DECIMAL(10,2),
    close       DECIMAL(10,2),
    volume      BIGINT,
    amount      DECIMAL(18,2),
    PRIMARY KEY (time, stock_code)
);

CREATE INDEX IF NOT EXISTS idx_stock_minute_code ON stock_minute (stock_code, time DESC);

-- 资金流向数据表
CREATE TABLE IF NOT EXISTS capital_flow (
    time            TIMESTAMPTZ NOT NULL,
    stock_code      VARCHAR(10) NOT NULL,
    main_inflow     DECIMAL(18,2),
    main_outflow    DECIMAL(18,2),
    retail_inflow   DECIMAL(18,2),
    retail_outflow  DECIMAL(18,2),
    net_inflow      DECIMAL(18,2),
    main_net_inflow DECIMAL(18,2),
    PRIMARY KEY (time, stock_code)
);

CREATE INDEX IF NOT EXISTS idx_capital_flow_code ON capital_flow (stock_code, time DESC);

-- Agent分析结果表
CREATE TABLE IF NOT EXISTS agent_analysis_results (
    id              SERIAL PRIMARY KEY,
    time            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    stock_code      VARCHAR(10) NOT NULL,
    analysis_type   VARCHAR(50) NOT NULL,
    result          JSONB NOT NULL,
    confidence      DECIMAL(5,2),
    agent_version   VARCHAR(20),
    UNIQUE(time, stock_code, analysis_type)
);

CREATE INDEX IF NOT EXISTS idx_agent_results_stock ON agent_analysis_results (stock_code, time DESC);
CREATE INDEX IF NOT EXISTS idx_agent_results_type ON agent_analysis_results (analysis_type);

-- ========== 关系数据表 ==========

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

CREATE INDEX IF NOT EXISTS idx_stock_info_industry ON stock_info(industry);

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

-- 用户配置表
CREATE TABLE IF NOT EXISTS user_configs (
    user_id         INTEGER PRIMARY KEY REFERENCES users(user_id),
    risk_preference VARCHAR(20) DEFAULT 'MODERATE',
    trading_style   VARCHAR(20) DEFAULT 'MEDIUM',
    focus_sectors   TEXT[],
    target_profit   DECIMAL(5,2) DEFAULT 30.0,
    max_position    DECIMAL(5,2) DEFAULT 0.8,
    stop_loss_rule  VARCHAR(50) DEFAULT 'TIGHT',
    notification_config JSONB DEFAULT '{}'::jsonb,
    agent_params    JSONB DEFAULT '{}'::jsonb,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 自选股表
CREATE TABLE IF NOT EXISTS watchlist (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(user_id),
    stock_code      VARCHAR(10) NOT NULL,
    added_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags            TEXT[],
    notes           TEXT,
    UNIQUE(user_id, stock_code)
);

CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlist(user_id);

-- 持仓记录表
CREATE TABLE IF NOT EXISTS positions (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(user_id),
    stock_code      VARCHAR(10) NOT NULL,
    stock_name      VARCHAR(50),
    buy_price       DECIMAL(10,2) NOT NULL,
    buy_quantity    INTEGER NOT NULL,
    buy_date        TIMESTAMP NOT NULL,
    current_price   DECIMAL(10,2),
    stop_loss_price DECIMAL(10,2),
    target_price    DECIMAL(10,2),
    position_ratio  DECIMAL(5,2),
    status          VARCHAR(20) DEFAULT 'HOLDING',
    buy_reason      TEXT,
    buy_strategy    VARCHAR(50),
    current_phase   VARCHAR(10),
    agent_suggestion VARCHAR(20),
    agent_confidence DECIMAL(5,2),
    sell_price      DECIMAL(10,2),
    sell_date       TIMESTAMP,
    sell_reason     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_positions_user ON positions(user_id);
CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status);

-- 交易记录表
CREATE TABLE IF NOT EXISTS trading_records (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(user_id),
    stock_code      VARCHAR(10) NOT NULL,
    stock_name      VARCHAR(50),
    operation       VARCHAR(10) NOT NULL,
    price           DECIMAL(10,2) NOT NULL,
    quantity        INTEGER NOT NULL,
    amount          DECIMAL(18,2),
    reason          TEXT,
    strategy        VARCHAR(50),
    signal_type     VARCHAR(50),
    agent_decision  JSONB,
    profit          DECIMAL(18,2),
    profit_rate     DECIMAL(10,4),
    traded_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trading_records_user ON trading_records(user_id);
CREATE INDEX IF NOT EXISTS idx_trading_records_time ON trading_records(traded_at DESC);

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
    status          VARCHAR(20) DEFAULT 'PENDING',
    executed_time   TIMESTAMP,
    executed_by     INTEGER REFERENCES users(user_id),
    execution_result JSONB
);

CREATE INDEX IF NOT EXISTS idx_signals_type ON trading_signals(signal_type);
CREATE INDEX IF NOT EXISTS idx_signals_status ON trading_signals(status);
CREATE INDEX IF NOT EXISTS idx_signals_time ON trading_signals(signal_time DESC);

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
    read_time       TIMESTAMP,
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    related_signal_id INTEGER REFERENCES trading_signals(id)
);

CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_time ON alerts(create_time DESC);

-- Agent决策日志表
CREATE TABLE IF NOT EXISTS agent_decision_logs (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(user_id),
    stock_code      VARCHAR(10),
    decision_type   VARCHAR(50) NOT NULL,
    decision        VARCHAR(20) NOT NULL,
    confidence      DECIMAL(5,2),
    analysis_process JSONB,
    reasoning       TEXT,
    agent_id        VARCHAR(50),
    agent_version   VARCHAR(20),
    input_data      JSONB,
    output_result   JSONB,
    feedback        VARCHAR(20),
    feedback_reason TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_agent_logs_stock ON agent_decision_logs(stock_code);
CREATE INDEX IF NOT EXISTS idx_agent_logs_type ON agent_decision_logs(decision_type);
CREATE INDEX IF NOT EXISTS idx_agent_logs_time ON agent_decision_logs(created_at DESC);

-- 知识库表
CREATE TABLE IF NOT EXISTS knowledge_base (
    id              SERIAL PRIMARY KEY,
    knowledge_type  VARCHAR(50) NOT NULL,
    title           VARCHAR(200) NOT NULL,
    content         TEXT NOT NULL,
    tags            TEXT[],
    keywords        TEXT[],
    category        VARCHAR(50),
    source          VARCHAR(200),
    author          VARCHAR(50),
    view_count      INTEGER DEFAULT 0,
    last_used       TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_knowledge_type ON knowledge_base(knowledge_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_tags ON knowledge_base USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_knowledge_keywords ON knowledge_base USING GIN(keywords);

-- 策略配置表
CREATE TABLE IF NOT EXISTS strategy_configs (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(user_id),
    strategy_name   VARCHAR(50) NOT NULL,
    strategy_type   VARCHAR(50) NOT NULL,
    parameters      JSONB NOT NULL,
    is_active       BOOLEAN DEFAULT TRUE,
    backtest_result JSONB,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 报告表
CREATE TABLE IF NOT EXISTS reports (
    id              SERIAL PRIMARY KEY,
    report_type     VARCHAR(50) NOT NULL,
    report_date     DATE NOT NULL,
    content         JSONB NOT NULL,
    summary         TEXT,
    generated_by    VARCHAR(50),
    generated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(report_type, report_date)
);

CREATE INDEX IF NOT EXISTS idx_reports_type ON reports(report_type);
CREATE INDEX IF NOT EXISTS idx_reports_date ON reports(report_date DESC);

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    config_key      VARCHAR(100) PRIMARY KEY,
    config_value    JSONB NOT NULL,
    description     TEXT,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by      INTEGER REFERENCES users(user_id)
);

-- 任务执行日志表
CREATE TABLE IF NOT EXISTS task_execution_logs (
    id              SERIAL PRIMARY KEY,
    task_name       VARCHAR(100) NOT NULL,
    task_type       VARCHAR(50) NOT NULL,
    status          VARCHAR(20) NOT NULL,
    start_time      TIMESTAMP NOT NULL,
    end_time        TIMESTAMP,
    duration        INTEGER,
    result          JSONB,
    error_message   TEXT,
    retry_count     INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_task_logs_name ON task_execution_logs(task_name);
CREATE INDEX IF NOT EXISTS idx_task_logs_status ON task_execution_logs(status);

-- ========== 初始化默认数据 ==========

-- 创建默认用户
INSERT INTO users (username, password_hash, email, role)
VALUES ('admin', 'hashed_password_here', 'admin@boyi.com', 'ADMIN')
ON CONFLICT (username) DO NOTHING;

-- 创建默认用户配置
INSERT INTO user_configs (user_id, risk_preference, trading_style, notification_config)
SELECT 1, 'MODERATE', 'MEDIUM', '{"buy_signal": true, "sell_signal": true, "risk_alert": true, "daily_report": true}'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM user_configs WHERE user_id = 1);

-- 插入系统配置
INSERT INTO system_configs (config_key, config_value, description)
VALUES
    ('system_status', '{"status": "active", "version": "1.0.0"}', '系统状态'),
    ('agent_config', '{"model": "GLM-5", "temperature": 0.7}', 'Agent配置'),
    ('data_source', '{"primary": "tushare", "backup": "akshare"}', '数据源配置')
ON CONFLICT (config_key) DO NOTHING;

-- ========== 完成提示 ==========
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '数据库初始化完成！';
    RAISE NOTICE '========================================';
    RAISE NOTICE '数据库: boyi_trading';
    RAISE NOTICE '用户: kevin';
    RAISE NOTICE '创建的表:';
    RAISE NOTICE '  时序数据: stock_daily, stock_minute, capital_flow, agent_analysis_results';
    RAISE NOTICE '  关系数据: stock_info, users, user_configs, watchlist';
    RAISE NOTICE '  交易管理: positions, trading_records, trading_signals';
    RAISE NOTICE '  预警系统: alerts, agent_decision_logs';
    RAISE NOTICE '  知识系统: knowledge_base, strategy_configs, reports';
    RAISE NOTICE '  系统管理: system_configs, task_execution_logs';
    RAISE NOTICE '========================================';
END $$;
