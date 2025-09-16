-- DT Commercial Roofing Database Schema
-- This script creates the database structure for the roofing estimation platform

-- Users table for authentication and user management
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    company VARCHAR(255),
    role VARCHAR(50) DEFAULT 'estimator',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Projects table for storing project information
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    client_name VARCHAR(255),
    client_address TEXT,
    square_footage INTEGER,
    roof_type VARCHAR(100),
    project_status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PDF documents table for storing uploaded files
CREATE TABLE IF NOT EXISTS pdf_documents (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size INTEGER,
    file_path VARCHAR(500),
    upload_status VARCHAR(50) DEFAULT 'uploaded',
    processing_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI processing results table
CREATE TABLE IF NOT EXISTS ai_processing_results (
    id SERIAL PRIMARY KEY,
    pdf_document_id INTEGER REFERENCES pdf_documents(id) ON DELETE CASCADE,
    processing_type VARCHAR(50) NOT NULL, -- 'document_ai', 'vision_ai', 'extraction'
    confidence_score DECIMAL(5,2),
    extracted_data JSONB,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Estimates table for storing generated estimates
CREATE TABLE IF NOT EXISTS estimates (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    estimate_number VARCHAR(50) UNIQUE NOT NULL,
    total_cost DECIMAL(12,2) NOT NULL,
    labor_cost DECIMAL(12,2) DEFAULT 0,
    material_cost DECIMAL(12,2) DEFAULT 0,
    permit_cost DECIMAL(12,2) DEFAULT 0,
    equipment_cost DECIMAL(12,2) DEFAULT 0,
    contingency_cost DECIMAL(12,2) DEFAULT 0,
    timeline_weeks INTEGER,
    confidence_score DECIMAL(5,2),
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Estimate line items for detailed breakdown
CREATE TABLE IF NOT EXISTS estimate_line_items (
    id SERIAL PRIMARY KEY,
    estimate_id INTEGER REFERENCES estimates(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL, -- 'materials', 'labor', 'permits', 'equipment', 'contingency'
    description TEXT NOT NULL,
    quantity DECIMAL(10,2),
    unit VARCHAR(50),
    unit_cost DECIMAL(10,2),
    total_cost DECIMAL(12,2) NOT NULL,
    source_type VARCHAR(50), -- 'ai_extracted', 'manual_input', 'standard_rate'
    confidence_score DECIMAL(5,2),
    citation_data JSONB, -- stores PDF citation information
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PDF citations table for linking extracted data to source documents
CREATE TABLE IF NOT EXISTS pdf_citations (
    id SERIAL PRIMARY KEY,
    pdf_document_id INTEGER REFERENCES pdf_documents(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    extracted_text TEXT,
    bounding_box JSONB, -- coordinates of the extracted text
    confidence_score DECIMAL(5,2),
    data_type VARCHAR(100), -- 'material', 'measurement', 'specification', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Processing queue for managing AI processing tasks
CREATE TABLE IF NOT EXISTS processing_queue (
    id SERIAL PRIMARY KEY,
    pdf_document_id INTEGER REFERENCES pdf_documents(id) ON DELETE CASCADE,
    processing_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'queued', -- 'queued', 'processing', 'completed', 'failed'
    priority INTEGER DEFAULT 5,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_pdf_documents_project_id ON pdf_documents(project_id);
CREATE INDEX IF NOT EXISTS idx_estimates_project_id ON estimates(project_id);
CREATE INDEX IF NOT EXISTS idx_estimate_line_items_estimate_id ON estimate_line_items(estimate_id);
CREATE INDEX IF NOT EXISTS idx_processing_queue_status ON processing_queue(status);
CREATE INDEX IF NOT EXISTS idx_ai_processing_results_pdf_id ON ai_processing_results(pdf_document_id);
