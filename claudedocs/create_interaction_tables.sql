-- ============================================================================
-- Drug Interaction System - Table Schema
-- ============================================================================
-- Purpose: Enable efficient drug-drug interaction checking
-- Strategy: 3-table hybrid approach with caching
-- Created: 2025-10-08
-- ============================================================================

-- ----------------------------------------------------------------------------
-- TABLE 1: drug_ingredient_mapping
-- Purpose: Master mapping of ingredients to drug categories
-- Update: Manual (when new ingredients/categories are identified)
-- Size: ~500-1,000 rows
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS drug_ingredient_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name VARCHAR(200) NOT NULL,           -- English ingredient name (from medicines.main_ingredient)
    drug_category_ko VARCHAR(100) NOT NULL,          -- Korean category name (테트라사이클린계)
    drug_category_en VARCHAR(100),                   -- English category name (Tetracycline Antibiotics)
    atc_code VARCHAR(20),                            -- WHO ATC classification code
    confidence_level VARCHAR(20) DEFAULT 'manual',   -- manual, verified, ai_generated
    source VARCHAR(100) DEFAULT 'manual',            -- Data source (DUR, WHO, FDA, manual)
    notes TEXT,                                      -- Additional notes
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ingredient_name, drug_category_ko)
);

CREATE INDEX IF NOT EXISTS idx_ingredient_name ON drug_ingredient_mapping(ingredient_name);
CREATE INDEX IF NOT EXISTS idx_drug_category_ko ON drug_ingredient_mapping(drug_category_ko);
CREATE INDEX IF NOT EXISTS idx_atc_code ON drug_ingredient_mapping(atc_code);

-- ----------------------------------------------------------------------------
-- TABLE 2: medicine_drug_categories
-- Purpose: Cache of medicine → drug categories (pre-computed for performance)
-- Update: Auto-generated from Table 1 + medicines table
-- Size: ~10,000-15,000 rows (multiple categories per medicine)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medicine_drug_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_id INTEGER NOT NULL,                    -- FK to medicines.item_seq
    drug_category_ko VARCHAR(100) NOT NULL,          -- Drug category (from Table 1)
    confidence FLOAT DEFAULT 1.0,                    -- Confidence score (0.0-1.0)
    source VARCHAR(50) DEFAULT 'ingredient_mapping', -- ingredient_mapping, text_analysis, manual
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(medicine_id, drug_category_ko),
    FOREIGN KEY (medicine_id) REFERENCES medicines(item_seq) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_medicine_id ON medicine_drug_categories(medicine_id);
CREATE INDEX IF NOT EXISTS idx_mdc_category ON medicine_drug_categories(drug_category_ko);
CREATE INDEX IF NOT EXISTS idx_mdc_composite ON medicine_drug_categories(medicine_id, drug_category_ko);

-- ----------------------------------------------------------------------------
-- TABLE 3: drug_interaction_rules
-- Purpose: Rules defining interactions between drug categories
-- Update: Manual (based on DUR, FDA, clinical guidelines)
-- Size: ~200-500 rows
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS drug_interaction_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_a VARCHAR(100) NOT NULL,                -- First drug category
    category_b VARCHAR(100) NOT NULL,                -- Second drug category
    interaction_type VARCHAR(20) NOT NULL,           -- contraindicated, caution, monitor, avoid
    severity VARCHAR(20) NOT NULL,                   -- critical, moderate, mild
    description TEXT,                                -- Detailed description of interaction
    mechanism TEXT,                                  -- Pharmacological mechanism
    recommendation TEXT,                             -- Clinical recommendation
    source VARCHAR(100) DEFAULT 'manual',            -- DUR, FDA, WHO, manual
    reference_url TEXT,                              -- Reference documentation URL
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_a, category_b),
    CHECK(interaction_type IN ('contraindicated', 'caution', 'monitor', 'avoid')),
    CHECK(severity IN ('critical', 'moderate', 'mild'))
);

CREATE INDEX IF NOT EXISTS idx_category_a ON drug_interaction_rules(category_a);
CREATE INDEX IF NOT EXISTS idx_category_b ON drug_interaction_rules(category_b);
CREATE INDEX IF NOT EXISTS idx_severity ON drug_interaction_rules(severity);
CREATE INDEX IF NOT EXISTS idx_interaction_type ON drug_interaction_rules(interaction_type);

-- ============================================================================
-- Sample Data Insertion
-- ============================================================================

-- Sample data will be inserted via separate scripts:
-- 1. populate_ingredient_mapping.sql (Table 1)
-- 2. populate_medicine_categories.py (Table 2 - auto-generated)
-- 3. populate_interaction_rules.sql (Table 3)

-- ============================================================================
-- Usage Example Query
-- ============================================================================
-- Check interaction between medicine A (id=195900043) and medicine B (id=197400207)
/*
SELECT DISTINCT
    dir.interaction_type,
    dir.severity,
    dir.description,
    dir.recommendation,
    mdc1.drug_category_ko as medicine_a_category,
    mdc2.drug_category_ko as medicine_b_category
FROM medicine_drug_categories mdc1
JOIN medicine_drug_categories mdc2
    ON mdc1.medicine_id = 195900043
    AND mdc2.medicine_id = 197400207
JOIN drug_interaction_rules dir
    ON (dir.category_a = mdc1.drug_category_ko AND dir.category_b = mdc2.drug_category_ko)
    OR (dir.category_b = mdc1.drug_category_ko AND dir.category_a = mdc2.drug_category_ko)
WHERE dir.severity IN ('critical', 'moderate');
*/

-- ============================================================================
-- Maintenance Queries
-- ============================================================================

-- Rebuild Table 2 cache (run after updating Table 1)
/*
DELETE FROM medicine_drug_categories;
-- Then run populate_medicine_categories.py script
*/

-- Find medicines without category mappings
/*
SELECT m.item_seq, m.item_name, m.main_ingredient
FROM medicines m
LEFT JOIN medicine_drug_categories mdc ON m.item_seq = mdc.medicine_id
WHERE mdc.medicine_id IS NULL
LIMIT 100;
*/

-- Statistics
/*
SELECT 'Total Ingredient Mappings' as metric, COUNT(*) as count FROM drug_ingredient_mapping
UNION ALL
SELECT 'Total Medicine Categories', COUNT(*) FROM medicine_drug_categories
UNION ALL
SELECT 'Total Interaction Rules', COUNT(*) FROM drug_interaction_rules
UNION ALL
SELECT 'Medicines with Categories', COUNT(DISTINCT medicine_id) FROM medicine_drug_categories;
*/
