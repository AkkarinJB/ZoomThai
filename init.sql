CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE procurement_announcements (
    announcement_id VARCHAR(50) PRIMARY KEY,
    agency VARCHAR(20) NOT NULL,
    title TEXT NOT NULL,
    method VARCHAR(50),
    fiscal_year INT,
    budget_amount NUMERIC(15, 2),
    submission_deadline TIMESTAMPTZ,
    tor_pdf_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE procurement_items (
    id SERIAL PRIMARY KEY,
    announcement_id VARCHAR(50) REFERENCES procurement_announcements(announcement_id) ON DELETE CASCADE,
    line_no INT,
    item_code VARCHAR(50),
    description TEXT,
    quantity NUMERIC(10, 2),
    unit VARCHAR(50),
    unit_price_estimate NUMERIC(15, 2),
    total_price_estimate NUMERIC(15, 2)
);

CREATE TABLE document_chunks (
    id VARCHAR(255) PRIMARY KEY,
    announcement_id VARCHAR(50) REFERENCES procurement_announcements(announcement_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding VECTOR(768)
);

CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    announcement_id VARCHAR(50) REFERENCES procurement_announcements(announcement_id) ON DELETE CASCADE,
    page_ref VARCHAR(20),
    chunk_text TEXT,
    embedding vector(1536) 
);

CREATE INDEX ON embeddings USING hnsw (embedding vector_l2_ops);
CREATE INDEX idx_agency ON procurement_announcements(agency);
CREATE INDEX idx_budget ON procurement_announcements(budget_amount);