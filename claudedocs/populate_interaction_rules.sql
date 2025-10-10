-- ============================================================================
-- Drug Interaction Rules - Table 3 Population
-- ============================================================================
-- Purpose: Define interaction rules between drug categories
-- Source: DUR guidelines, FDA warnings, clinical guidelines
-- Priority: High-risk and common interactions
-- ============================================================================

-- ----------------------------------------------------------------------------
-- CRITICAL INTERACTIONS (Contraindicated)
-- ----------------------------------------------------------------------------

-- 1. Tetracycline + Antacids (Chelation)
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('테트라사이클린계', '제산제', 'contraindicated', 'moderate',
 '제산제의 금속 이온(Al, Mg, Ca)이 테트라사이클린과 킬레이트를 형성하여 흡수 감소',
 '금속 이온이 테트라사이클린과 불용성 복합체 형성, 위장관 흡수 방해',
 '병용 금기. 최소 2-3시간 간격 필요',
 'DUR');

-- 2. MAO Inhibitors + Tricyclic Antidepressants (Serotonin Syndrome)
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('MAO억제제', '삼환계항우울제', 'contraindicated', 'critical',
 '세로토닌 증후군, 고혈압 위기 등 심각한 부작용 발생 가능',
 '세로토닌 과다로 인한 중추신경계 독성',
 '병용 금기. MAO 억제제 중단 후 최소 2주 경과 필요',
 'FDA');

-- 3. MAO Inhibitors + Sympathomimetics (Hypertensive Crisis)
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('MAO억제제', '교감신경흥분제', 'contraindicated', 'critical',
 '고혈압 위기 발생 위험',
 'MAO 억제로 노르에피네프린 축적, 교감신경흥분제 효과 증강',
 '병용 금기. MAO 억제제 복용 중 및 중단 후 2주간 금지',
 'FDA');

-- 4. MAO Inhibitors + CNS Depressants
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('MAO억제제', '중추신경억제제', 'contraindicated', 'critical',
 '중추신경계 억제 작용 증강, 심각한 진정 및 호흡억제',
 '중추신경 억제 작용의 상승 효과',
 '병용 금기',
 'DUR');

-- 5. NSAIDs + Warfarin (Bleeding Risk)
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('비스테로이드소염진통제', '쿠마린계', 'caution', 'critical',
 'NSAIDs가 항응고제의 효과를 증강시켜 출혈 위험 증가',
 'NSAIDs가 혈소판 기능 억제, 위장관 점막 손상, 와파린 단백 결합 경쟁',
 '병용 시 출혈 징후 모니터링 필수. INR 정기 확인',
 'DUR');

-- 6. Aspirin + Warfarin (Additive Bleeding)
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('혈소판응집억제제', '쿠마린계', 'caution', 'critical',
 '항혈소판제와 항응고제 병용 시 출혈 위험 상승',
 '항응고 작용과 항혈소판 작용의 상가 효과',
 '병용 시 출혈 모니터링 필수. 저용량 아스피린도 주의',
 'FDA');

-- 7. Warfarin + Antibiotics (INR Change)
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('쿠마린계', '테트라사이클린계', 'caution', 'moderate',
 '일부 항생제가 비타민K 생성 장내세균을 억제하여 항응고 효과 증강',
 '장내 비타민K 생성 감소',
 '병용 시 INR 모니터링. 필요시 용량 조절',
 'manual');

-- 8. Fluoroquinolones + Antacids (Absorption)
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('플루오로퀴놀론계', '제산제', 'contraindicated', 'moderate',
 '제산제의 금속 이온이 퀴놀론계 항생제와 킬레이트 형성',
 '금속 이온과의 킬레이트 형성으로 흡수 감소',
 '2시간 이상 간격 필요',
 'DUR');

-- Also for 뉴퀴놀론계
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('뉴퀴놀론계', '제산제', 'contraindicated', 'moderate',
 '제산제의 금속 이온이 퀴놀론계 항생제와 킬레이트 형성',
 '금속 이온과의 킬레이트 형성으로 흡수 감소',
 '2시간 이상 간격 필요',
 'DUR');

-- ----------------------------------------------------------------------------
-- MODERATE INTERACTIONS (Caution Required)
-- ----------------------------------------------------------------------------

-- 9. NSAIDs + Thiazide Diuretics (Reduced Effect)
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('비스테로이드소염진통제', '티아지드계이뇨제', 'monitor', 'moderate',
 'NSAIDs가 이뇨제의 효과를 감소시킬 수 있음',
 'NSAIDs의 프로스타글란딘 합성 억제로 신장 혈류 감소',
 '혈압 및 신기능 모니터링 필요',
 'manual');

-- 10. NSAIDs + Loop Diuretics (Reduced Effect)
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('비스테로이드소염진통제', '루프계이뇨제', 'monitor', 'moderate',
 'NSAIDs가 루프 이뇨제의 효과를 감소시킬 수 있음',
 'NSAIDs의 프로스타글란딘 합성 억제',
 '이뇨 효과 및 신기능 모니터링',
 'manual');

-- 11. Barbiturates + CNS Depressants (Additive Sedation)
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('바르비탈계', '중추신경억제제', 'caution', 'moderate',
 '중추신경 억제 작용 상가',
 '진정 효과의 상가적 증강',
 '용량 조절 필요. 진정 정도 모니터링',
 'manual');

-- 12. Antihistamines + CNS Depressants
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('항히스타민제', '중추신경억제제', 'caution', 'moderate',
 '졸음 및 진정 작용 증강',
 '중추신경 억제 작용의 상가',
 '운전 및 기계 조작 주의',
 'manual');

-- 13. Antihistamines + MAO Inhibitors
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('항히스타민제', 'MAO억제제', 'contraindicated', 'critical',
 '중추신경계 억제 작용 증강 및 항콜린 작용 증강',
 'MAO 억제제의 중추신경 억제 작용과 항히스타민제 작용 상가',
 '병용 금기',
 'DUR');

-- 14. Corticosteroids + NSAIDs (GI Bleeding)
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('스테로이드제', '비스테로이드소염진통제', 'caution', 'moderate',
 '위장관 출혈 및 궤양 위험 증가',
 '두 약물 모두 위점막 보호 기전 약화',
 '위장 보호제 병용 고려. 위장관 증상 모니터링',
 'manual');

-- 15. Sulfonylureas + NSAIDs (Hypoglycemia)
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('설포닐우레아계', '비스테로이드소염진통제', 'caution', 'moderate',
 'NSAIDs가 혈당강하제 효과 증강, 저혈당 위험',
 'NSAIDs가 설포닐우레아의 혈장 단백 결합 치환',
 '혈당 모니터링 필요',
 'manual');

-- 16. Benzodiazepines + Antihistamines
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('벤조디아제핀계', '항히스타민제', 'caution', 'moderate',
 '진정 작용 및 졸음 증강',
 '중추신경 억제의 상가 효과',
 '용량 조절 고려. 운전 주의',
 'manual');

-- 17. Antitussives + Antihistamines (Additive)
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('진해거담제', '항히스타민제', 'monitor', 'mild',
 '진정 작용 및 항콜린 작용 증가 가능',
 '일부 진해제의 중추 억제 작용',
 '졸음 주의',
 'manual');

-- 18. Caffeine + Sympathomimetics (Stimulation)
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('각성제', '교감신경흥분제', 'monitor', 'moderate',
 '중추신경 자극 및 심혈관계 자극 증가',
 '교감신경 자극의 상가 효과',
 '빈맥, 불안 등 증상 모니터링',
 'manual');

-- 19. Laxatives + Diuretics (Electrolyte)
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('완하제', '티아지드계이뇨제', 'caution', 'moderate',
 '전해질 불균형 위험 증가',
 '칼륨 손실의 상가 효과',
 '전해질 모니터링 필요',
 'manual');

INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('완하제', '루프계이뇨제', 'caution', 'moderate',
 '전해질 불균형 위험 증가',
 '칼륨 손실의 상가 효과',
 '전해질 모니터링 필요',
 'manual');

-- 20. Antibiotics + Probiotics (Reduced Efficacy)
INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('항생제', '생균제', 'monitor', 'mild',
 '항생제가 유산균 사멸 가능',
 '항생제의 광범위한 항균 작용',
 '2시간 이상 간격 권장',
 'manual');

INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('테트라사이클린계', '생균제', 'monitor', 'mild',
 '항생제가 유산균 사멸 가능',
 '항생제의 광범위한 항균 작용',
 '2시간 이상 간격 권장',
 'manual');

INSERT INTO drug_interaction_rules (category_a, category_b, interaction_type, severity, description, mechanism, recommendation, source) VALUES
('플루오로퀴놀론계', '생균제', 'monitor', 'mild',
 '항생제가 유산균 사멸 가능',
 '항생제의 광범위한 항균 작용',
 '2시간 이상 간격 권장',
 'manual');

-- ----------------------------------------------------------------------------
-- Statistics
-- ----------------------------------------------------------------------------
SELECT 'Total interaction rules created: ' || COUNT(*) FROM drug_interaction_rules;
SELECT 'Critical severity: ' || COUNT(*) FROM drug_interaction_rules WHERE severity = 'critical';
SELECT 'Moderate severity: ' || COUNT(*) FROM drug_interaction_rules WHERE severity = 'moderate';
SELECT 'Mild severity: ' || COUNT(*) FROM drug_interaction_rules WHERE severity = 'mild';
