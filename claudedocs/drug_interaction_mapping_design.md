# Drug Interaction Mapping System Design

## Analysis Summary

### 1. Interaction Field Analysis (3,295 records)
**Top Drug Categories Found:**
- 테트라사이클린계 (Tetracycline antibiotics): 679 mentions
- 삼환계 (Tricyclic): 484 mentions
- 해열진통제 (Antipyretics): 482 mentions
- 바르비탈계 (Barbiturates): 467 mentions
- 소염진통제 (NSAIDs): 398 mentions
- 티아지드계 이뇨제 (Thiazide diuretics): 349 mentions
- 쿠마린계 (Coumarin anticoagulants): 266 mentions
- MAO 억제제 (MAO inhibitors): 914 mentions
- 루프계 이뇨제 (Loop diuretics): 161 mentions
- 뉴퀴놀론계 (Fluoroquinolones): 86 mentions

### 2. Ingredient Pattern Analysis
**Common ingredient patterns:**
- Hydrochloride salts
- Sodium/Potassium salts
- Acid forms
- Natural extracts (Root, Bark, Fruit)

**Example Mappings Identified:**
- Naproxen, Ibuprofen, Diclofenac → NSAIDs (비스테로이드소염진통제)
- Tetracycline, Doxycycline → Tetracycline antibiotics (테트라사이클린계)

## Proposed Database Schema

### Table 1: `drug_ingredient_mapping`
Maps individual ingredients to drug categories

```sql
CREATE TABLE drug_ingredient_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name VARCHAR(200) NOT NULL,  -- English ingredient name
    drug_category_ko VARCHAR(100) NOT NULL,  -- Korean category (테트라사이클린계)
    drug_category_en VARCHAR(100),           -- English category (Tetracycline)
    atc_code VARCHAR(20),                    -- WHO ATC code (optional)
    confidence_level VARCHAR(20) DEFAULT 'manual',  -- manual, verified, ai_generated
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    UNIQUE(ingredient_name, drug_category_ko)
);

CREATE INDEX idx_ingredient_name ON drug_ingredient_mapping(ingredient_name);
CREATE INDEX idx_drug_category_ko ON drug_ingredient_mapping(drug_category_ko);
```

### Table 2: `drug_interaction_rules`
Stores interaction rules between drug categories

```sql
CREATE TABLE drug_interaction_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_a VARCHAR(100) NOT NULL,  -- First drug category
    category_b VARCHAR(100) NOT NULL,  -- Second drug category
    interaction_type VARCHAR(20) NOT NULL,  -- contraindicated, caution, monitor
    severity VARCHAR(20),               -- critical, moderate, mild
    description TEXT,                   -- Detailed description
    source VARCHAR(100),                -- DUR, FDA, manual, etc.
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    UNIQUE(category_a, category_b)
);

CREATE INDEX idx_category_a ON drug_interaction_rules(category_a);
CREATE INDEX idx_category_b ON drug_interaction_rules(category_b);
```

## Mapping Strategy

### Phase 1: Build Core Mappings (Top 40 Categories)
1. **테트라사이클린계** → Tetracycline, Doxycycline, Oxytetracycline, Minocycline
2. **비스테로이드소염진통제** → Ibuprofen, Naproxen, Diclofenac, Ketoprofen
3. **삼환계항우울제** → Amitriptyline, Imipramine, Nortriptyline
4. **MAO억제제** → Phenelzine, Tranylcypromine, Selegiline
5. **바르비탈계** → Phenobarbital, Pentobarbital
6. **티아지드계이뇨제** → Hydrochlorothiazide, Chlorothiazide
7. **쿠마린계** → Warfarin, Acenocoumarol
8. **루프계이뇨제** → Furosemide, Bumetanide
9. **퀴놀론계/뉴퀴놀론계** → Ciprofloxacin, Levofloxacin, Moxifloxacin
10. **칼슘제제** → Calcium Carbonate, Calcium Citrate

### Phase 2: Extract from Medicines Table
Auto-generate mappings by analyzing:
- Ingredient names containing category keywords (e.g., "Tetracycline" → 테트라사이클린계)
- Cross-reference with interaction field mentions

### Phase 3: DUR Data Integration
Use provided links to enhance mappings:
1. WHO ATC Index: Standard drug classification codes
2. 식약처 DUR: Official Korean interaction data
3. 건강보험심사평가원: Comprehensive medicine DB

## Interaction Check Logic

### Algorithm:
```python
def check_interaction(medicine_a_id, medicine_b_id):
    # 1. Get ingredients for both medicines
    ingredients_a = get_ingredients(medicine_a_id)
    ingredients_b = get_ingredients(medicine_b_id)

    # 2. Map ingredients to categories
    categories_a = map_ingredients_to_categories(ingredients_a)
    categories_b = map_ingredients_to_categories(ingredients_b)

    # 3. Check interaction rules
    interactions = []
    for cat_a in categories_a:
        for cat_b in categories_b:
            rule = check_interaction_rule(cat_a, cat_b)
            if rule:
                interactions.append(rule)

    # 4. Also check direct text mentions in interaction field
    text_mentions = check_text_mentions(
        medicine_a.interaction,
        categories_b
    )

    return {
        'has_interaction': len(interactions) > 0 or len(text_mentions) > 0,
        'rule_based': interactions,
        'text_based': text_mentions,
        'severity': get_max_severity(interactions, text_mentions)
    }
```

## Next Steps

1. ✅ Extract 40 major drug categories
2. ⏳ Build initial ingredient → category mapping (Top 100 ingredients)
3. ⏳ Create Django models for mapping tables
4. ⏳ Implement basic interaction check API
5. ⏳ Enhance with DUR data from provided sources
6. ⏳ Add fuzzy matching for ingredient name variations

## Data Sources for Mapping

### Priority 1: Manual Mapping
- Top 40 drug categories
- Top 100 most common ingredients
- High-risk interactions (MAO inhibitors, anticoagulants, etc.)

### Priority 2: DUR Public Data
- 식약처 DUR 공공데이터 (https://nedrug.mfds.go.kr/index)
- 건강보험심사평가원 의약품DB

### Priority 3: WHO ATC Classification
- WHO ATC Index 2024 (https://atcddd.fhi.no/atc_ddd_index/)
- Standard international drug classification

---
*Created: 2025-10-08*
*Status: Design Phase*
