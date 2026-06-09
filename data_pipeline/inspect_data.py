import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import os
os.chdir(r'd:\Finternship\backend')
sys.path.insert(0, r'd:\Finternship\backend')
os.environ['DB_PATH'] = r'd:\Finternship\hotel_aditya.db'

from engine.recommender import generate_recommendations, get_recommendation_context

TARGET_DATE = '2026-06-08'  # A Sunday (peak day) — good test
recs = generate_recommendations(TARGET_DATE)
ctx  = get_recommendation_context(TARGET_DATE)

print(f'Recommendations for: {TARGET_DATE}')
print(f'Total items recommended: {len(recs)}')
print()
print('WEATHER CONTEXT:', ctx.get('weather'))
print('FESTIVAL:', ctx.get('festival_today') or 'None')
if ctx.get('upcoming_festivals'):
    print('UPCOMING:', ctx['upcoming_festivals'][:2])
print()
print('TOP 15 BY RECOMMENDED QTY:')
recs_sorted = sorted(recs, key=lambda x: x['recommended_qty'], reverse=True)
for r in recs_sorted[:15]:
    name = r['item_name']
    qty  = r['recommended_qty']
    cat  = r['category']
    reason = r['reason']
    print(f"  {name:<35} qty:{qty:>4}  cat:{cat:<12}  {reason}")

print()
print('CATEGORIES COVERED:', sorted(set(r['category'] for r in recs)))
print()
print('SAMPLE FULL RECOMMENDATION OBJECT:')
import json
print(json.dumps(recs_sorted[0], indent=2))
