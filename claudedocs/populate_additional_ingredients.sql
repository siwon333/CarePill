-- ============================================================================
-- Additional Ingredient Mappings - Common Western Medicine Ingredients
-- ============================================================================
-- Adds mappings for frequently used ingredients that were missed in initial mapping
-- Focus: Western medicine ingredients, vitamins, common OTC drugs
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 15. 진해거담제 (Antitussives and Expectorants)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Guaifenesin', '진해거담제', 'Antitussives/Expectorants', 'R05CA03', 'manual', 'WHO_ATC'),
('Bromhexine Hydrochloride', '진해거담제', 'Antitussives/Expectorants', 'R05CB02', 'manual', 'WHO_ATC'),
('Carbocisteine', '진해거담제', 'Antitussives/Expectorants', 'R05CB03', 'manual', 'WHO_ATC'),
('Noscapine', '진해거담제', 'Antitussives/Expectorants', 'R05DA07', 'manual', 'WHO_ATC'),
('Dextromethorphan', '진해거담제', 'Antitussives/Expectorants', 'R05DA09', 'manual', 'WHO_ATC'),
('Levocloperastine', '진해거담제', 'Antitussives/Expectorants', 'R05DA10', 'manual', 'WHO_ATC'),
('Levocloperastine Fendizoate', '진해거담제', 'Antitussives/Expectorants', 'R05DA10', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 16. 비타민제 (Vitamins)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Ascorbic Acid', '비타민제', 'Vitamins', 'A11GA01', 'manual', 'WHO_ATC'),
('Ascorbic Acid Granules 97%', '비타민제', 'Vitamins', 'A11GA01', 'manual', 'WHO_ATC'),
('Riboflavin', '비타민제', 'Vitamins', 'A11HA04', 'manual', 'WHO_ATC'),
('Riboflavin Sodium Phosphate', '비타민제', 'Vitamins', 'A11HA04', 'manual', 'WHO_ATC'),
('Thiamine Hydrochloride', '비타민제', 'Vitamins', 'A11DA01', 'manual', 'WHO_ATC'),
('Thiamine Nitrate', '비타민제', 'Vitamins', 'A11DA01', 'manual', 'WHO_ATC'),
('Pyridoxine Hydrochloride', '비타민제', 'Vitamins', 'A11HA02', 'manual', 'WHO_ATC'),
('Cyanocobalamin', '비타민제', 'Vitamins', 'B03BA01', 'manual', 'WHO_ATC'),
('Cyanocobalamin Powder 1%', '비타민제', 'Vitamins', 'B03BA01', 'manual', 'WHO_ATC'),
('Mecobalamin', '비타민제', 'Vitamins', 'B03BA03', 'manual', 'WHO_ATC'),
('Nicotinamide', '비타민제', 'Vitamins', 'A11HA01', 'manual', 'WHO_ATC'),
('Calcium Pantothenate', '비타민제', 'Vitamins', 'A11HA30', 'manual', 'WHO_ATC'),
('Biotin', '비타민제', 'Vitamins', 'A11HA05', 'manual', 'WHO_ATC'),
('Tocopherol Acetate', '비타민제', 'Vitamins', 'A11HA03', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 17. 소화효소제 (Digestive Enzymes)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Diastase', '소화효소제', 'Digestive Enzymes', 'A09AA02', 'manual', 'WHO_ATC'),
('Biodiastase 500', '소화효소제', 'Digestive Enzymes', 'A09AA02', 'manual', 'WHO_ATC'),
('Lipase', '소화효소제', 'Digestive Enzymes', 'A09AA02', 'manual', 'WHO_ATC'),
('Protease', '소화효소제', 'Digestive Enzymes', 'A09AA02', 'manual', 'WHO_ATC'),
('Cellulase', '소화효소제', 'Digestive Enzymes', 'A09AA02', 'manual', 'WHO_ATC'),
('Bromelain', '소화효소제', 'Digestive Enzymes', 'A09AA02', 'manual', 'WHO_ATC'),
('Beta-Galactosidase', '소화효소제', 'Digestive Enzymes', 'A09AA02', 'manual', 'WHO_ATC'),
('Beta-Galactosidase (Aspergillus)', '소화효소제', 'Digestive Enzymes', 'A09AA02', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 18. 진정제 (Sedatives)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Dimenhydrinate', '진정제', 'Sedatives/Antiemetics', 'R06AA52', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 19. 교감신경흥분제 (Sympathomimetics)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Pseudoephedrine Hydrochloride', '교감신경흥분제', 'Sympathomimetics', 'R01BA02', 'manual', 'WHO_ATC'),
('DL-Methylephedrine Hydrochloride', '교감신경흥분제', 'Sympathomimetics', 'R01BA03', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 20. 스테로이드제 (Corticosteroids)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Betamethasone', '스테로이드제', 'Corticosteroids', 'D07AC01', 'manual', 'WHO_ATC'),
('Betamethasone Valerate', '스테로이드제', 'Corticosteroids', 'D07AC01', 'manual', 'WHO_ATC'),
('Prednisolone', '스테로이드제', 'Corticosteroids', 'H02AB06', 'manual', 'WHO_ATC'),
('Dexamethasone', '스테로이드제', 'Corticosteroids', 'H02AB02', 'manual', 'WHO_ATC'),
('Hydrocortisone', '스테로이드제', 'Corticosteroids', 'H02AB09', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 21. 지사제 (Antidiarrheals)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Loperamide Hydrochloride', '지사제', 'Antidiarrheals', 'A07DA03', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 22. 완하제/하제 (Laxatives)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Bisacodyl', '완하제', 'Laxatives', 'A06AB02', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 23. 항생제 (Various Antibiotics)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Sodium Fusidate', '항생제', 'Antibiotics', 'D06AX01', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 24. 소독제/방부제 (Antiseptics)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Povidone Iodine', '소독제', 'Antiseptics', 'D08AG02', 'manual', 'WHO_ATC'),
('Chlorhexidine Gluconate', '소독제', 'Antiseptics', 'D08AC02', 'manual', 'WHO_ATC'),
('Chlorhexidine Gluconate Solution', '소독제', 'Antiseptics', 'D08AC02', 'manual', 'WHO_ATC'),
('Cetylpyridinium Chloride', '소독제', 'Antiseptics', 'D08AJ02', 'manual', 'WHO_ATC'),
('Cetylpyridinium Chloride Hydrate', '소독제', 'Antiseptics', 'D08AJ02', 'manual', 'WHO_ATC'),
('Nitrofurazone', '소독제', 'Antiseptics', 'D08AF01', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 25. 아미노산/영양제 (Amino Acids / Nutritional Supplements)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('L-Arginine Hydrochloride', '아미노산제', 'Amino Acids', 'A16AA01', 'manual', 'WHO_ATC'),
('Glycine', '아미노산제', 'Amino Acids', 'A16AA01', 'manual', 'WHO_ATC'),
('DL-Carnitine Hydrochloride', '아미노산제', 'Amino Acids', 'A16AA01', 'manual', 'WHO_ATC'),
('Citrulline Malate', '아미노산제', 'Amino Acids', 'A16AA02', 'manual', 'WHO_ATC'),
('Glutathione (Reduced)', '아미노산제', 'Amino Acids/Antioxidants', 'V03AB32', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 26. 기타 치료제 (Other Therapeutic Agents)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Ubidecarenone', '심혈관계약', 'Cardiovascular Agents', 'C01EB09', 'manual', 'WHO_ATC'),
('Cytidine', '간장질환치료제', 'Liver Therapy', 'A05BA', 'manual', 'WHO_ATC'),
('Ursodeoxycholic Acid', '간장질환치료제', 'Liver Therapy', 'A05AA02', 'manual', 'WHO_ATC'),
('Sodium Hyaluronate', '관절염치료제', 'Joint Therapy', 'M09AX01', 'manual', 'WHO_ATC'),
('Polydeoxyribonucleotide Sodium', '상처치료제', 'Wound Healing', 'D03AX', 'manual', 'manual');

-- ----------------------------------------------------------------------------
-- 27. 생균제 (Probiotics)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Lactobacillus Acidophilus', '생균제', 'Probiotics', 'A07FA01', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 28. 각질용해제 (Keratolytics)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Salicylic Acid', '각질용해제', 'Keratolytics', 'D11AF', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 29. 자극완화제 (Antipruritic/Soothing)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Crotamiton', '진양제', 'Antipruritics', 'D04AX', 'manual', 'WHO_ATC'),
('Guaiazulene', '항염증제', 'Anti-inflammatory', 'A02BX', 'manual', 'manual');

-- ----------------------------------------------------------------------------
-- 30. 카페인 (Caffeine - Stimulant)
-- ----------------------------------------------------------------------------
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Anhydrous Caffeine', '각성제', 'Stimulants', 'N06BC01', 'manual', 'WHO_ATC'),
('Caffeine', '각성제', 'Stimulants', 'N06BC01', 'manual', 'WHO_ATC');

-- ----------------------------------------------------------------------------
-- 31. 한방제제/생약제제 (Herbal/Traditional Medicine)
-- ----------------------------------------------------------------------------
-- Map common herbal ingredients to general category
INSERT INTO drug_ingredient_mapping (ingredient_name, drug_category_ko, drug_category_en, atc_code, confidence_level, source) VALUES
('Ginseng', '한방제제', 'Herbal Medicine', NULL, 'manual', 'manual'),
('Licorice', '한방제제', 'Herbal Medicine', NULL, 'manual', 'manual'),
('Atractylodes Rhizome', '한방제제', 'Herbal Medicine', NULL, 'manual', 'manual'),
('Platycodon Root', '한방제제', 'Herbal Medicine', NULL, 'manual', 'manual'),
('Pueraria Root', '한방제제', 'Herbal Medicine', NULL, 'manual', 'manual'),
('Polygala Root', '한방제제', 'Herbal Medicine', NULL, 'manual', 'manual'),
('Cinnamon Bark', '한방제제', 'Herbal Medicine', NULL, 'manual', 'manual'),
('Magnolia Bark', '한방제제', 'Herbal Medicine', NULL, 'manual', 'manual'),
('Ephedra Herb', '한방제제', 'Herbal Medicine', NULL, 'manual', 'manual'),
('Citrus Unshiu Peel', '한방제제', 'Herbal Medicine', NULL, 'manual', 'manual'),
('Liriope Tuber', '한방제제', 'Herbal Medicine', NULL, 'manual', 'manual'),
('Cattle Gallstone', '한방제제', 'Herbal Medicine', NULL, 'manual', 'manual');

-- ----------------------------------------------------------------------------
-- Statistics
-- ----------------------------------------------------------------------------
SELECT 'Additional ingredient mappings created: ' || COUNT(*) FROM drug_ingredient_mapping WHERE id > 76;
SELECT 'Total ingredient mappings now: ' || COUNT(*) FROM drug_ingredient_mapping;
SELECT 'Unique categories now: ' || COUNT(DISTINCT drug_category_ko) FROM drug_ingredient_mapping;
