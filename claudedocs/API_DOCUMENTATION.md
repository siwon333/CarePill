# Drug Interaction API Documentation

## Overview
This API allows you to check drug interactions between medicines based on their pharmaceutical categories.

## System Architecture

### Database Tables
1. **medicines**: Master medicine data (4,800 medicines)
2. **drug_ingredient_mapping**: Ingredient to drug category mapping (150 ingredients, 38 categories)
3. **medicine_drug_categories**: Pre-computed medicine to category cache (5,453 mappings)
4. **drug_interaction_rules**: Category interaction rules (24 rules)

### Coverage
- Mapped medicines: 3,150 (66%)
- Mapping confidence: 91% from WHO ATC, 74% exact match
- Interaction rules: 6 critical, 14 moderate, 4 mild

## API Endpoints

### 1. Check Drug Interaction

**Endpoint**: `POST /api/check-interaction/`

**Request Body**:
```json
{
  "medicine_a_id": 195900043,
  "medicine_b_id": 197400207
}
```

**Response** (Interaction Found):
```json
{
  "has_interaction": true,
  "interaction_count": 1,
  "interactions": [
    {
      "category_a": "제산제",
      "category_b": "테트라사이클린계",
      "interaction_type": "contraindicated",
      "severity": "moderate",
      "description": "제산제의 금속 이온(Al, Mg, Ca)이 테트라사이클린과 킬레이트를 형성하여 흡수 감소",
      "mechanism": "금속 이온이 테트라사이클린과 불용성 복합체 형성, 위장관 흡수 방해",
      "recommendation": "병용 금기. 최소 2-3시간 간격 필요",
      "source": "DUR"
    }
  ],
  "medicine_a": {
    "id": 195900043,
    "name": "아네모정",
    "manufacturer": "삼진제약(주)",
    "ingredients": "Dried Aluminium Hydroxide Gel/Magnesium Carbonate/...",
    "categories": ["제산제"]
  },
  "medicine_b": {
    "id": 197400207,
    "name": "테트라사이클린정",
    "manufacturer": "대웅제약",
    "ingredients": "Tetracycline",
    "categories": ["테트라사이클린계"]
  }
}
```

**Response** (No Interaction):
```json
{
  "has_interaction": false,
  "interaction_count": 0,
  "interactions": [],
  "medicine_a": { ... },
  "medicine_b": { ... }
}
```

**Error Responses**:
- `400`: Missing medicine IDs
- `404`: Medicine not found
- `500`: Server error

---

### 2. Search Medicine

**Endpoint**: `GET /api/search-medicine/?q={query}`

**Parameters**:
- `q`: Search query (minimum 2 characters)

**Example Request**:
```
GET /api/search-medicine/?q=이부프로펜
```

**Response**:
```json
{
  "results": [
    {
      "id": 123456,
      "name": "부루펜정200밀리그램(이부프로펜)",
      "manufacturer": "삼진제약(주)",
      "ingredients": "Ibuprofen",
      "categories": ["비스테로이드소염진통제"]
    },
    {
      "id": 123457,
      "name": "부루펜정400밀리그램(이부프로펜)",
      "manufacturer": "삼진제약(주)",
      "ingredients": "Ibuprofen",
      "categories": ["비스테로이드소염진통제"]
    }
  ],
  "count": 2,
  "query": "이부프로펜"
}
```

**Error Responses**:
- `400`: Query too short (< 2 characters)
- `500`: Server error

---

### 3. Medicine Detail

**Endpoint**: `GET /api/medicine/{medicine_id}/`

**Example Request**:
```
GET /api/medicine/195900043/
```

**Response**:
```json
{
  "id": 195900043,
  "name": "아네모정",
  "name_eng": null,
  "manufacturer": "삼진제약(주)",
  "ingredients": "Dried Aluminium Hydroxide Gel/Magnesium Carbonate/...",
  "effect": "이 약은 위산과다, 속쓰림, 위부불쾌감...",
  "usage": "성인 1회 2정, 1일 3회 식간(식사와 식사때 사이) 및 취침시에 복용합니다.",
  "warning_critical": null,
  "warning_general": "투석요법을 받고 있는 환자...",
  "interaction": "위장진통ㆍ진경제, 테트라사이클린계 항생제와 함께 복용하지 마십시오.",
  "side_effect": "발진, 충혈되어 붉어짐, 가려움...",
  "storage": "습기와 빛을 피해 보관하십시오...",
  "categories": [
    {
      "name": "제산제",
      "confidence": 1.0,
      "source": "ingredient_mapping"
    }
  ],
  "potential_interactions": [
    {
      "interacts_with": "테트라사이클린계",
      "type": "contraindicated",
      "severity": "moderate",
      "description": "제산제의 금속 이온(Al, Mg, Ca)이 테트라사이클린과 킬레이트를 형성하여 흡수 감소"
    },
    {
      "interacts_with": "플루오로퀴놀론계",
      "type": "contraindicated",
      "severity": "moderate",
      "description": "제산제의 금속 이온이 퀴놀론계 항생제와 킬레이트 형성"
    }
  ]
}
```

**Error Responses**:
- `404`: Medicine not found
- `500`: Server error

---

## Interaction Types

| Type | Description |
|------|-------------|
| `contraindicated` | Absolute contraindication - do not use together |
| `caution` | Use with caution - monitoring required |
| `monitor` | Monitor for effects - generally safe but watch for issues |
| `avoid` | Avoid if possible - seek alternatives |

## Severity Levels

| Severity | Description |
|----------|-------------|
| `critical` | Life-threatening or severe adverse effects |
| `moderate` | Significant clinical impact, requires intervention |
| `mild` | Minor clinical impact, manageable |

## Example Use Cases

### Case 1: Simple Interaction Check
```python
import requests

response = requests.post('http://localhost:8000/api/check-interaction/', json={
    'medicine_a_id': 195900043,  # 아네모정 (제산제)
    'medicine_b_id': 197400207   # 테트라사이클린정
})

data = response.json()
if data['has_interaction']:
    for interaction in data['interactions']:
        print(f"Warning: {interaction['severity']} - {interaction['description']}")
```

### Case 2: Search and Check
```python
# 1. Search for medicine
response = requests.get('http://localhost:8000/api/search-medicine/', params={'q': '부루펜'})
medicines = response.json()['results']

# 2. Get medicine details
medicine_id = medicines[0]['id']
response = requests.get(f'http://localhost:8000/api/medicine/{medicine_id}/')
medicine_detail = response.json()

# 3. Check potential interactions
print(f"Potential interactions for {medicine_detail['name']}:")
for interaction in medicine_detail['potential_interactions']:
    print(f"  - With {interaction['interacts_with']}: {interaction['severity']}")
```

## Data Sources

- **WHO ATC Classification**: International standard drug classification (91% of mappings)
- **Korean DUR Guidelines**: Drug utilization review data from MFDS
- **FDA Guidelines**: US FDA drug interaction warnings
- **Clinical Guidelines**: Evidence-based pharmacology references

## Limitations

1. **Coverage**: 66% of medicines are mapped. Unmapped medicines will not show interaction warnings.
2. **Herbal Medicines**: Traditional Korean medicines are mapped to general "herbal medicine" category with limited interaction data.
3. **Rare Combinations**: Only common and clinically significant interactions are included (24 rules).
4. **Not Medical Advice**: This system is for informational purposes. Always consult healthcare professionals.

## Testing

Run the test script to verify API functionality:
```bash
python scripts/test_interaction_api.py
```

## Future Enhancements

1. Add more interaction rules (targeting 200+ rules)
2. Improve herbal medicine mapping
3. Add dose-dependent interactions
4. Include food-drug interactions
5. Multi-drug interaction checking (3+ medicines)
6. Real-time DUR data integration

---

Last Updated: 2025-10-08
