#!/usr/bin/env python
"""
Auto-populate medicine_drug_categories table (Table 2)
This script processes all medicines and maps them to drug categories
based on their main_ingredient field and Table 1 mappings.
"""

import sqlite3
import re
from datetime import datetime

DB_PATH = 'db.sqlite3'

def parse_ingredients(main_ingredient_str):
    """
    Parse main_ingredient string into individual ingredients.
    Example: "Ibuprofen/Caffeine/Pseudoephedrine Hydrochloride"
    Returns: ['Ibuprofen', 'Caffeine', 'Pseudoephedrine Hydrochloride']
    """
    if not main_ingredient_str:
        return []

    # Split by '/' delimiter
    ingredients = main_ingredient_str.split('/')

    # Clean up whitespace
    ingredients = [ing.strip() for ing in ingredients if ing.strip()]

    return ingredients


def find_matching_categories(ingredient, cursor):
    """
    Find drug categories for a given ingredient using Table 1.

    Strategy:
    1. Exact match on ingredient_name
    2. Partial match (ingredient contains mapping name)
    3. Case-insensitive match

    Returns: list of (drug_category_ko, confidence, source)
    """
    categories = []

    # Strategy 1: Exact match
    cursor.execute("""
        SELECT DISTINCT drug_category_ko, 1.0 as confidence, 'exact_match' as source
        FROM drug_ingredient_mapping
        WHERE ingredient_name = ?
    """, (ingredient,))

    exact_matches = cursor.fetchall()
    if exact_matches:
        return exact_matches

    # Strategy 2: Partial match (ingredient contains the mapped name)
    # Example: "Pseudoephedrine Hydrochloride" contains "Pseudoephedrine"
    cursor.execute("""
        SELECT DISTINCT drug_category_ko, 0.9 as confidence, 'partial_match' as source
        FROM drug_ingredient_mapping
        WHERE ? LIKE '%' || ingredient_name || '%'
    """, (ingredient,))

    partial_matches = cursor.fetchall()
    if partial_matches:
        return partial_matches

    # Strategy 3: Reverse partial match (mapped name contains ingredient)
    cursor.execute("""
        SELECT DISTINCT drug_category_ko, 0.8 as confidence, 'reverse_match' as source
        FROM drug_ingredient_mapping
        WHERE ingredient_name LIKE '%' || ? || '%'
    """, (ingredient,))

    reverse_matches = cursor.fetchall()
    if reverse_matches:
        return reverse_matches

    return categories


def populate_medicine_categories():
    """
    Main function to populate medicine_drug_categories table.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80)
    print("Populating medicine_drug_categories (Table 2)")
    print("=" * 80)

    # Clear existing data
    print("\n[1/4] Clearing existing medicine_drug_categories...")
    cursor.execute("DELETE FROM medicine_drug_categories")
    conn.commit()
    print(f"      Cleared existing records.")

    # Get all medicines
    print("\n[2/4] Loading medicines from database...")
    cursor.execute("""
        SELECT item_seq, item_name, main_ingredient
        FROM medicines
        WHERE main_ingredient IS NOT NULL
        AND main_ingredient != ''
    """)

    medicines = cursor.fetchall()
    print(f"      Found {len(medicines)} medicines with ingredients.")

    # Process each medicine
    print("\n[3/4] Processing medicines and mapping categories...")

    total_mappings = 0
    medicines_with_categories = 0
    medicines_without_categories = []

    for idx, (item_seq, item_name, main_ingredient) in enumerate(medicines, 1):
        if idx % 500 == 0:
            print(f"      Progress: {idx}/{len(medicines)} medicines processed...")

        # Parse ingredients
        ingredients = parse_ingredients(main_ingredient)

        medicine_categories = set()  # Use set to avoid duplicates

        # Find categories for each ingredient
        for ingredient in ingredients:
            categories = find_matching_categories(ingredient, cursor)

            for drug_category_ko, confidence, source in categories:
                medicine_categories.add((drug_category_ko, confidence, source))

        # Insert into medicine_drug_categories
        if medicine_categories:
            medicines_with_categories += 1

            for drug_category_ko, confidence, source in medicine_categories:
                cursor.execute("""
                    INSERT OR IGNORE INTO medicine_drug_categories
                    (medicine_id, drug_category_ko, confidence, source, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    item_seq,
                    drug_category_ko,
                    confidence,
                    source,
                    datetime.now(),
                    datetime.now()
                ))
                total_mappings += 1
        else:
            medicines_without_categories.append((item_seq, item_name, main_ingredient))

    conn.commit()

    print(f"\n[4/4] Population complete!")
    print(f"\n{'='*80}")
    print("STATISTICS")
    print(f"{'='*80}")
    print(f"Total medicines processed:           {len(medicines):,}")
    print(f"Medicines with categories mapped:    {medicines_with_categories:,}")
    print(f"Medicines without categories:        {len(medicines_without_categories):,}")
    print(f"Total category mappings created:     {total_mappings:,}")
    print(f"Average categories per medicine:     {total_mappings/medicines_with_categories:.2f}")

    # Show sample of unmapped medicines
    if medicines_without_categories:
        print(f"\n{'='*80}")
        print(f"Sample of unmapped medicines (first 10):")
        print(f"{'='*80}")
        for item_seq, item_name, main_ingredient in medicines_without_categories[:10]:
            # Truncate long ingredient lists
            ingredients_display = main_ingredient[:60] + '...' if len(main_ingredient) > 60 else main_ingredient
            print(f"  [{item_seq}] {item_name}")
            print(f"      Ingredients: {ingredients_display}")

    # Category distribution
    print(f"\n{'='*80}")
    print("Category Distribution (Top 10)")
    print(f"{'='*80}")
    cursor.execute("""
        SELECT drug_category_ko, COUNT(*) as count
        FROM medicine_drug_categories
        GROUP BY drug_category_ko
        ORDER BY count DESC
        LIMIT 10
    """)

    for category, count in cursor.fetchall():
        print(f"  {category:30s} {count:5,} medicines")

    # Verification query
    print(f"\n{'='*80}")
    print("Sample mappings (random 5 medicines):")
    print(f"{'='*80}")
    cursor.execute("""
        SELECT
            m.item_name,
            GROUP_CONCAT(mdc.drug_category_ko, ', ') as categories
        FROM medicines m
        JOIN medicine_drug_categories mdc ON m.item_seq = mdc.medicine_id
        GROUP BY m.item_seq, m.item_name
        ORDER BY RANDOM()
        LIMIT 5
    """)

    for item_name, categories in cursor.fetchall():
        print(f"  {item_name:40s} → {categories}")

    conn.close()
    print(f"\n{'='*80}")
    print("✅ Table 2 (medicine_drug_categories) population complete!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    try:
        populate_medicine_categories()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
