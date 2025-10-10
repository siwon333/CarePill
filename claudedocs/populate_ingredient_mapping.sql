-- ============================================================================
-- Drug Ingredient Mapping - Initial Data Population
-- ============================================================================
-- Table 1: drug_ingredient_mapping
-- Purpose: Core ingredient → category mappings for top 40 drug classes
-- Source: Analysis of medicines DB + DUR guidelines
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. 테트라사이클린계 항생제 (Tetracycline Antibiotics)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Tetracycline', '테트라사이클린계', 'Tetracycline Antibiotics', 'J01AA07', 'manual', 'WHO_ATC'),
('Doxycycline', '테트라사이클린계', 'Tetracycline Antibiotics', 'J01AA02', 'manual', 'WHO_ATC'),
('Oxytetracycline', '테트라사이클린계', 'Tetracycline Antibiotics', 'J01AA06', 'manual', 'WHO_ATC'),
('Minocycline', '테트라사이클린계', 'Tetracycline Antibiotics', 'J01AA08', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 2. 비스테로이드소염진통제 (NSAIDs)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Ibuprofen', '비스테로이드소염진통제', 'NSAIDs', 'M01AE01', 'manual', 'WHO_ATC'),
('Naproxen', '비스테로이드소염진통제', 'NSAIDs', 'M01AE02', 'manual', 'WHO_ATC'),
('Naproxen Sodium', '비스테로이드소염진통제', 'NSAIDs', 'M01AE02', 'manual', 'WHO_ATC'),
('Diclofenac', '비스테로이드소염진통제', 'NSAIDs', 'M01AB05', 'manual', 'WHO_ATC'),
('Ketoprofen', '비스테로이드소염진통제', 'NSAIDs', 'M01AE03', 'manual', 'WHO_ATC'),
('Indomethacin', '비스테로이드소염진통제', 'NSAIDs', 'M01AB01', 'manual', 'WHO_ATC'),
('Piroxicam', '비스테로이드소염진통제', 'NSAIDs', 'M01AC01', 'manual', 'WHO_ATC'),
('Mefenamic Acid', '비스테로이드소염진통제', 'NSAIDs', 'M01AG01', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 3. 제산제 (Antacids)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Aluminium Hydroxide', '제산제', 'Antacids', 'A02AB01', 'manual', 'WHO_ATC'),
('Dried Aluminium Hydroxide Gel', '제산제', 'Antacids', 'A02AB01', 'manual', 'WHO_ATC'),
('Magnesium Hydroxide', '제산제', 'Antacids', 'A02AA04', 'manual', 'WHO_ATC'),
('Magnesium Carbonate', '제산제', 'Antacids', 'A02AA02', 'manual', 'WHO_ATC'),
('Calcium Carbonate', '제산제', 'Antacids', 'A02AC01', 'manual', 'WHO_ATC'),
('Precipitated Calcium Carbonate', '제산제', 'Antacids', 'A02AC01', 'manual', 'WHO_ATC'),
('Aluminium Phosphate Gel', '제산제', 'Antacids', 'A02AB02', 'manual', 'WHO_ATC'),
('Colloidal Aluminium Phosphate', '제산제', 'Antacids', 'A02AB02', 'manual', 'WHO_ATC'),
('Magnesium Aluminosilicate', '제산제', 'Antacids', 'A02AD02', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 4. MAO 억제제 (MAO Inhibitors)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Phenelzine', 'MAO억제제', 'MAO Inhibitors', 'N06AF03', 'manual', 'WHO_ATC'),
('Tranylcypromine', 'MAO억제제', 'MAO Inhibitors', 'N06AF04', 'manual', 'WHO_ATC'),
('Selegiline', 'MAO억제제', 'MAO Inhibitors', 'N04BD01', 'manual', 'WHO_ATC'),
('Rasagiline', 'MAO억제제', 'MAO Inhibitors', 'N04BD02', 'manual', 'WHO_ATC'),
('Moclobemide', 'MAO억제제', 'MAO Inhibitors', 'N06AG02', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 5. 삼환계 항우울제 (Tricyclic Antidepressants)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Amitriptyline', '삼환계항우울제', 'Tricyclic Antidepressants', 'N06AA09', 'manual', 'WHO_ATC'),
('Imipramine', '삼환계항우울제', 'Tricyclic Antidepressants', 'N06AA02', 'manual', 'WHO_ATC'),
('Nortriptyline', '삼환계항우울제', 'Tricyclic Antidepressants', 'N06AA10', 'manual', 'WHO_ATC'),
('Clomipramine', '삼환계항우울제', 'Tricyclic Antidepressants', 'N06AA04', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 6. 바르비탈계 (Barbiturates)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Phenobarbital', '바르비탈계', 'Barbiturates', 'N03AA02', 'manual', 'WHO_ATC'),
('Pentobarbital', '바르비탈계', 'Barbiturates', 'N05CA01', 'manual', 'WHO_ATC'),
('Secobarbital', '바르비탈계', 'Barbiturates', 'N05CA06', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 7. 티아지드계 이뇨제 (Thiazide Diuretics)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Hydrochlorothiazide', '티아지드계이뇨제', 'Thiazide Diuretics', 'C03AA03', 'manual', 'WHO_ATC'),
('Chlorothiazide', '티아지드계이뇨제', 'Thiazide Diuretics', 'C03AA01', 'manual', 'WHO_ATC'),
('Indapamide', '티아지드계이뇨제', 'Thiazide Diuretics', 'C03BA11', 'manual', 'WHO_ATC'),
('Trichlormethiazide', '티아지드계이뇨제', 'Thiazide Diuretics', 'C03AA06', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 8. 쿠마린계 항응고제 (Coumarin Anticoagulants)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Warfarin', '쿠마린계', 'Coumarin Anticoagulants', 'B01AA03', 'manual', 'WHO_ATC'),
('Warfarin Sodium', '쿠마린계', 'Coumarin Anticoagulants', 'B01AA03', 'manual', 'WHO_ATC'),
('Acenocoumarol', '쿠마린계', 'Coumarin Anticoagulants', 'B01AA07', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 9. 루프계 이뇨제 (Loop Diuretics)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Furosemide', '루프계이뇨제', 'Loop Diuretics', 'C03CA01', 'manual', 'WHO_ATC'),
('Bumetanide', '루프계이뇨제', 'Loop Diuretics', 'C03CA02', 'manual', 'WHO_ATC'),
('Ethacrynic Acid', '루프계이뇨제', 'Loop Diuretics', 'C03CC01', 'manual', 'WHO_ATC'),
('Etacrynic Acid', '루프계이뇨제', 'Loop Diuretics', 'C03CC01', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 10. 퀴놀론계/플루오로퀴놀론계 항생제 (Fluoroquinolone Antibiotics)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Ciprofloxacin', '플루오로퀴놀론계', 'Fluoroquinolone Antibiotics', 'J01MA02', 'manual', 'WHO_ATC'),
('Levofloxacin', '플루오로퀴놀론계', 'Fluoroquinolone Antibiotics', 'J01MA12', 'manual', 'WHO_ATC'),
('Moxifloxacin', '플루오로퀴놀론계', 'Fluoroquinolone Antibiotics', 'J01MA14', 'manual', 'WHO_ATC'),
('Ofloxacin', '플루오로퀴놀론계', 'Fluoroquinolone Antibiotics', 'J01MA01', 'manual', 'WHO_ATC'),
('Norfloxacin', '플루오로퀴놀론계', 'Fluoroquinolone Antibiotics', 'J01MA06', 'manual', 'WHO_ATC'),
('Enoxacin', '플루오로퀴놀론계', 'Fluoroquinolone Antibiotics', 'J01MA04', 'manual', 'WHO_ATC');

-- Also map to 뉴퀴놀론계 (Korean variant name)
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Ciprofloxacin', '뉴퀴놀론계', 'New Quinolone Antibiotics', 'J01MA02', 'manual', 'WHO_ATC'),
('Levofloxacin', '뉴퀴놀론계', 'New Quinolone Antibiotics', 'J01MA12', 'manual', 'WHO_ATC'),
('Moxifloxacin', '뉴퀴놀론계', 'New Quinolone Antibiotics', 'J01MA14', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 11. 항히스타민제 (Antihistamines)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Chlorpheniramine', '항히스타민제', 'Antihistamines', 'R06AB04', 'manual', 'WHO_ATC'),
('Chlorpheniramine Maleate', '항히스타민제', 'Antihistamines', 'R06AB04', 'manual', 'WHO_ATC'),
('Diphenhydramine', '항히스타민제', 'Antihistamines', 'R06AA02', 'manual', 'WHO_ATC'),
('Cetirizine', '항히스타민제', 'Antihistamines', 'R06AE07', 'manual', 'WHO_ATC'),
('Loratadine', '항히스타민제', 'Antihistamines', 'R06AX13', 'manual', 'WHO_ATC'),
('Fexofenadine', '항히스타민제', 'Antihistamines', 'R06AX26', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 12. 해열진통제 (Antipyretic Analgesics)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Acetaminophen', '해열진통제', 'Antipyretic Analgesics', 'N02BE01', 'manual', 'WHO_ATC'),
('Paracetamol', '해열진통제', 'Antipyretic Analgesics', 'N02BE01', 'manual', 'WHO_ATC'),
('Aspirin', '해열진통제', 'Antipyretic Analgesics', 'N02BA01', 'manual', 'WHO_ATC'),
('Acetylsalicylic Acid', '해열진통제', 'Antipyretic Analgesics', 'N02BA01', 'manual', 'WHO_ATC');

-- Also map Aspirin to antiplatelet
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Aspirin', '혈소판응집억제제', 'Antiplatelet Agents', 'B01AC06', 'manual', 'WHO_ATC'),
('Acetylsalicylic Acid', '혈소판응집억제제', 'Antiplatelet Agents', 'B01AC06', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 13. 중추신경억제제 (CNS Depressants)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Diazepam', '중추신경억제제', 'CNS Depressants', 'N05BA01', 'manual', 'WHO_ATC'),
('Alprazolam', '중추신경억제제', 'CNS Depressants', 'N05BA12', 'manual', 'WHO_ATC'),
('Lorazepam', '중추신경억제제', 'CNS Depressants', 'N05BA06', 'manual', 'WHO_ATC'),
('Zolpidem', '중추신경억제제', 'CNS Depressants', 'N05CF02', 'manual', 'WHO_ATC');

-- Also map to 벤조디아제핀계
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Diazepam', '벤조디아제핀계', 'Benzodiazepines', 'N05BA01', 'manual', 'WHO_ATC'),
('Alprazolam', '벤조디아제핀계', 'Benzodiazepines', 'N05BA12', 'manual', 'WHO_ATC'),
('Lorazepam', '벤조디아제핀계', 'Benzodiazepines', 'N05BA06', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 14. 설포닐우레아계 (Sulfonylureas - Diabetes)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Glipizide', '설포닐우레아계', 'Sulfonylureas', 'A10BB07', 'manual', 'WHO_ATC'),
('Glyburide', '설포닐우레아계', 'Sulfonylureas', 'A10BB01', 'manual', 'WHO_ATC'),
('Glibenclamide', '설포닐우레아계', 'Sulfonylureas', 'A10BB01', 'manual', 'WHO_ATC'),
('Tolbutamide', '설포닐우레아계', 'Sulfonylureas', 'A10BB03', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- Statistics
-- ----------------------------------------------------------------------------
SELECT 'Total ingredient mappings created: ' || COUNT(*) FROM drug_ingredient_mapping;
SELECT 'Unique ingredients: ' || COUNT(DISTINCT ingredient_name) FROM drug_ingredient_mapping;
SELECT 'Unique categories: ' || COUNT(DISTINCT drug_category_ko) FROM drug_ingredient_mapping;
