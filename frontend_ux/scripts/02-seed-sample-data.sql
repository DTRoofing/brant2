-- Sample data for DT Commercial Roofing platform
-- This script populates the database with sample data for testing

-- Insert sample users
INSERT INTO users (email, password_hash, first_name, last_name, company, role) VALUES
('john.doe@dtroofing.com', '$2b$10$example_hash_1', 'John', 'Doe', 'DT Commercial Roofing', 'estimator'),
('jane.smith@dtroofing.com', '$2b$10$example_hash_2', 'Jane', 'Smith', 'DT Commercial Roofing', 'admin'),
('mike.wilson@contractor.com', '$2b$10$example_hash_3', 'Mike', 'Wilson', 'Wilson Construction', 'estimator');

-- Insert sample projects
INSERT INTO projects (user_id, name, client_name, client_address, square_footage, roof_type, project_status) VALUES
(1, 'Warehouse Complex Roof Replacement', 'ABC Manufacturing', '1234 Industrial Blvd, Manufacturing District', 15000, 'TPO Membrane', 'completed'),
(1, 'Office Building Repair', 'Tech Solutions Inc', '5678 Business Park Dr, Tech Valley', 8500, 'Modified Bitumen', 'in_review'),
(1, 'Retail Center New Installation', 'Shopping Plaza LLC', '9012 Commerce St, Retail District', 12200, 'EPDM', 'draft'),
(2, 'Hospital Roof Renovation', 'City Medical Center', '3456 Health Ave, Medical District', 25000, 'TPO Membrane', 'completed');

-- Insert sample PDF documents
INSERT INTO pdf_documents (project_id, filename, original_filename, file_size, file_path, processing_status) VALUES
(1, 'warehouse_specs_20240115.pdf', 'warehouse-roof-specs.pdf', 2048576, '/uploads/warehouse_specs_20240115.pdf', 'completed'),
(2, 'office_plans_20240114.pdf', 'office-building-plans.pdf', 1536000, '/uploads/office_plans_20240114.pdf', 'processing'),
(3, 'retail_blueprints_20240112.pdf', 'retail-center-blueprints.pdf', 3072000, '/uploads/retail_blueprints_20240112.pdf', 'pending');

-- Insert sample estimates
INSERT INTO estimates (project_id, estimate_number, total_cost, labor_cost, material_cost, permit_cost, equipment_cost, contingency_cost, timeline_weeks, confidence_score, status) VALUES
(1, 'EST-2024-001', 127500.00, 45000.00, 65000.00, 2500.00, 5000.00, 10000.00, 4, 94.5, 'completed'),
(2, 'EST-2024-002', 45200.00, 18000.00, 22000.00, 1200.00, 2000.00, 2000.00, 2, 89.2, 'in_review'),
(3, 'EST-2024-003', 89750.00, 32000.00, 45000.00, 2750.00, 4000.00, 6000.00, 3, 91.8, 'draft');

-- Insert sample estimate line items for the first estimate
INSERT INTO estimate_line_items (estimate_id, category, description, quantity, unit, unit_cost, total_cost, source_type, confidence_score, citation_data) VALUES
-- Materials
(1, 'materials', 'TPO Membrane 60 mil', 16500.00, 'sq ft', 2.85, 47025.00, 'ai_extracted', 96.0, '{"page": 3, "text": "TPO membrane roofing system, 60 mil thickness", "pdf_name": "warehouse-roof-specs.pdf"}'),
(1, 'materials', 'Polyiso Insulation R-30', 15000.00, 'sq ft', 1.20, 18000.00, 'ai_extracted', 92.0, '{"page": 4, "text": "R-30 polyisocyanurate insulation board", "pdf_name": "warehouse-roof-specs.pdf"}'),
(1, 'materials', 'Roofing Fasteners & Plates', 2400.00, 'pieces', 0.75, 1800.00, 'manual_input', NULL, NULL),

-- Labor
(1, 'labor', 'Existing Roof Tear-off', 15000.00, 'sq ft', 1.50, 22500.00, 'ai_extracted', 89.0, '{"page": 2, "text": "Remove existing built-up roofing system", "pdf_name": "warehouse-roof-specs.pdf"}'),
(1, 'labor', 'TPO Installation', 15000.00, 'sq ft', 1.50, 22500.00, 'standard_rate', NULL, NULL),

-- Permits
(1, 'permits', 'Building Permit', 1.00, 'permit', 1500.00, 1500.00, 'manual_input', NULL, NULL),
(1, 'permits', 'Inspection Fees', 3.00, 'inspections', 250.00, 750.00, 'manual_input', NULL, NULL),

-- Equipment
(1, 'equipment', 'Crane Rental', 5.00, 'days', 800.00, 4000.00, 'manual_input', NULL, NULL),
(1, 'equipment', 'Safety Equipment & Barriers', 1.00, 'job', 1200.00, 1200.00, 'manual_input', NULL, NULL),

-- Contingency
(1, 'contingency', 'Weather Delay Contingency', 1.00, 'allowance', 5000.00, 5000.00, 'standard_practice', NULL, NULL),
(1, 'contingency', 'Structural Repair Allowance', 1.00, 'allowance', 5000.00, 5000.00, 'manual_input', NULL, NULL);

-- Insert sample AI processing results
INSERT INTO ai_processing_results (pdf_document_id, processing_type, confidence_score, extracted_data, processing_time_ms) VALUES
(1, 'document_ai', 94.5, '{"building_type": "Commercial Warehouse", "square_footage": "15,000 sq ft", "roof_material": "TPO Membrane"}', 8500),
(1, 'vision_ai', 91.2, '{"measurements": {"length": "300 ft", "width": "50 ft"}, "slope": "1/4 inch per foot"}', 6200),
(1, 'extraction', 96.8, '{"materials": ["TPO Membrane", "Polyiso Insulation"], "specifications": ["R-30", "60 mil"]}', 4800);

-- Insert sample PDF citations
INSERT INTO pdf_citations (pdf_document_id, page_number, extracted_text, confidence_score, data_type) VALUES
(1, 3, 'TPO membrane roofing system, 60 mil thickness', 96.0, 'material'),
(1, 4, 'R-30 polyisocyanurate insulation board', 92.0, 'insulation'),
(1, 2, 'Remove existing built-up roofing system', 89.0, 'labor'),
(1, 5, 'Building dimensions: 300 ft x 50 ft', 94.5, 'measurement');
