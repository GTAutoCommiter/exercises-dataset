#!/usr/bin/env python3
"""
Static API Generator for Exercises Dataset
Reads data/exercises.json and generates a structured, static RESTful JSON API in api/v1/
suitable for hosting on GitHub Pages or CDN.
"""

import json
import os
import re
import shutil
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(PROJECT_ROOT, "data", "exercises.json")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "api", "v1")

LANGUAGES = ["en", "it", "tr", "es", "ru", "zh", "hi", "pl", "ko", "fr"]

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    if not text:
        return ""
    return re.sub(r'[^a-z0-9]+', '-', str(text).lower()).strip('-')

def compact_exercise(ex: dict) -> dict:
    """Extract lightweight metadata for list endpoints."""
    return {
        "id": ex.get("id"),
        "name": ex.get("name"),
        "category": ex.get("category"),
        "body_part": ex.get("body_part"),
        "equipment": ex.get("equipment"),
        "target": ex.get("target"),
        "image": ex.get("image"),
        "gif_url": ex.get("gif_url")
    }

def localized_exercise(ex: dict, lang: str) -> dict:
    """Extract exercise data localized to a single language."""
    item = compact_exercise(ex)
    item["muscle_group"] = ex.get("muscle_group", [])
    item["secondary_muscles"] = ex.get("secondary_muscles", [])
    
    instructions = ex.get("instructions", {})
    if isinstance(instructions, dict):
        item["instruction"] = instructions.get(lang) or instructions.get("en", "")
    else:
        item["instruction"] = str(instructions)
        
    steps = ex.get("instruction_steps", {})
    if isinstance(steps, dict):
        item["instruction_steps"] = steps.get(lang) or steps.get("en", [])
    else:
        item["instruction_steps"] = steps if isinstance(steps, list) else []
        
    return item

def main():
    print(f"Loading exercise dataset from {DATA_FILE}...")
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Dataset file not found: {DATA_FILE}")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        exercises = json.load(f)

    print(f"Loaded {len(exercises)} exercises.")

    # Clean output directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Subdirectories
    exercises_dir = os.path.join(OUTPUT_DIR, "exercises")
    by_cat_dir = os.path.join(OUTPUT_DIR, "by-category")
    by_bp_dir = os.path.join(OUTPUT_DIR, "by-body-part")
    by_eq_dir = os.path.join(OUTPUT_DIR, "by-equipment")
    by_target_dir = os.path.join(OUTPUT_DIR, "by-target")
    lang_dir = os.path.join(OUTPUT_DIR, "lang")

    for d in [exercises_dir, by_cat_dir, by_bp_dir, by_eq_dir, by_target_dir, lang_dir]:
        os.makedirs(d, exist_ok=True)

    # 1. Individual exercise files (api/v1/exercises/{id}.json)
    print("Generating individual exercise detail JSONs...")
    for ex in exercises:
        ex_id = ex.get("id")
        if ex_id:
            file_path = os.path.join(exercises_dir, f"{ex_id}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(ex, f, ensure_ascii=False, indent=2)

    # 2. Compact exercises list (api/v1/exercises.json)
    print("Generating lightweight exercises index (api/v1/exercises.json)...")
    compact_list = [compact_exercise(ex) for ex in exercises]
    with open(os.path.join(OUTPUT_DIR, "exercises.json"), "w", encoding="utf-8") as f:
        json.dump(compact_list, f, ensure_ascii=False, indent=2)

    # Helper for grouped endpoints
    def generate_grouped_endpoints(field_name: str, out_dir: str, list_filename: str):
        groups = {}
        for ex in exercises:
            val = ex.get(field_name)
            if not val:
                continue
            slug = slugify(val)
            if slug not in groups:
                groups[slug] = {
                    "name": val,
                    "slug": slug,
                    "count": 0,
                    "items": []
                }
            groups[slug]["count"] += 1
            groups[slug]["items"].append(compact_exercise(ex))

        # Write category list index JSON
        summary_list = []
        for slug in sorted(groups.keys()):
            g = groups[slug]
            rel_url = f"api/v1/{os.path.basename(out_dir)}/{slug}.json"
            summary_list.append({
                "name": g["name"],
                "slug": g["slug"],
                "count": g["count"],
                "url": rel_url
            })
            # Write group items JSON
            with open(os.path.join(out_dir, f"{slug}.json"), "w", encoding="utf-8") as f:
                json.dump(g["items"], f, ensure_ascii=False, indent=2)

        with open(os.path.join(OUTPUT_DIR, list_filename), "w", encoding="utf-8") as f:
            json.dump(summary_list, f, ensure_ascii=False, indent=2)

        return len(summary_list)

    print("Generating category endpoints...")
    cat_count = generate_grouped_endpoints("category", by_cat_dir, "categories.json")

    print("Generating body-part endpoints...")
    bp_count = generate_grouped_endpoints("body_part", by_bp_dir, "body-parts.json")

    print("Generating equipment endpoints...")
    eq_count = generate_grouped_endpoints("equipment", by_eq_dir, "equipment.json")

    print("Generating target endpoints...")
    target_count = generate_grouped_endpoints("target", by_target_dir, "targets.json")

    # 3. Localized single-language endpoints (api/v1/lang/{lang}.json)
    print("Generating single-language endpoints...")
    for lang in LANGUAGES:
        lang_exercises = [localized_exercise(ex, lang) for ex in exercises]
        with open(os.path.join(lang_dir, f"{lang}.json"), "w", encoding="utf-8") as f:
            json.dump(lang_exercises, f, ensure_ascii=False, indent=2)

    # 4. Meta JSON (api/v1/meta.json)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta = {
        "version": "1.0.0",
        "total_exercises": len(exercises),
        "last_updated": now_iso,
        "supported_languages": LANGUAGES,
        "counts": {
            "categories": cat_count,
            "body_parts": bp_count,
            "equipment": eq_count,
            "targets": target_count
        },
        "endpoints": {
            "meta": "api/v1/meta.json",
            "exercises_index": "api/v1/exercises.json",
            "exercise_detail": "api/v1/exercises/{id}.json",
            "categories": "api/v1/categories.json",
            "body_parts": "api/v1/body-parts.json",
            "equipment": "api/v1/equipment.json",
            "targets": "api/v1/targets.json",
            "by_category": "api/v1/by-category/{category_slug}.json",
            "by_body_part": "api/v1/by-body-part/{body_part_slug}.json",
            "by_equipment": "api/v1/by-equipment/{equipment_slug}.json",
            "by_target": "api/v1/by-target/{target_slug}.json",
            "by_language": "api/v1/lang/{lang}.json"
        }
    }
    with open(os.path.join(OUTPUT_DIR, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"Static API generation completed successfully! Output directory: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
