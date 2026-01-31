"""
验证64卦数据完整性
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

from core.tools.divination_calculator import HEXAGRAMS, HEXAGRAM_LOOKUP

print(f"HEXAGRAMS数量: {len(HEXAGRAMS)}")
print(f"HEXAGRAM_LOOKUP数量: {len(HEXAGRAM_LOOKUP)}")

# 检查缺失的卦
missing = [i for i in range(1, 65) if str(i) not in HEXAGRAMS]
if missing:
    print(f"缺失的卦: {missing}")
else:
    print("所有64卦都已添加")

# 验证每个卦的数据完整性
print("\n验证数据完整性:")
errors = []
for i in range(1, 65):
    hex_id = str(i)
    if hex_id not in HEXAGRAMS:
        errors.append(f"第{i}卦缺失")
        continue
    
    h = HEXAGRAMS[hex_id]
    
    # 检查必要字段
    required_fields = ['name', 'full_name', 'inner', 'outer', 'guaci', 'yaoci']
    for field in required_fields:
        if field not in h:
            errors.append(f"第{i}卦 ({h.get('name', '未知')}) 缺少字段: {field}")
    
    # 检查爻辞数量
    if 'yaoci' in h:
        if len(h['yaoci']) != 6:
            errors.append(f"第{i}卦 ({h.get('name', '未知')}) 爻辞数量不正确: {len(h['yaoci'])} (应为6)")
        else:
            # 检查是否有缺失的爻
            missing_yaos = [j for j in range(1, 7) if str(j) not in h['yaoci']]
            if missing_yaos:
                errors.append(f"第{i}卦 ({h.get('name', '未知')}) 缺失爻辞: {missing_yaos}")
    
    # 检查卦辞是否为空
    if not h.get('guaci') or h.get('guaci') == '（卦辞待补充）':
        errors.append(f"第{i}卦 ({h.get('name', '未知')}) 卦辞为空或待补充")

if errors:
    print(f"\n发现 {len(errors)} 个错误:")
    for error in errors[:10]:  # 只显示前10个错误
        print(f"  - {error}")
    if len(errors) > 10:
        print(f"  ... 还有 {len(errors) - 10} 个错误")
else:
    print("[OK] 所有64卦数据完整！")

# 验证查找表
print(f"\n验证查找表:")
test_cases = [
    ("乾", "乾", "1"),
    ("坤", "坤", "2"),
    ("震", "坎", "3"),
    ("坎", "艮", "4"),
    ("离", "巽", "37"),  # 家人卦：内卦离，外卦巽
    ("巽", "巽", "57"),  # 巽卦：内卦巽，外卦巽
    ("兑", "巽", "61"),  # 中孚卦：内卦兑，外卦巽
]
for inner, outer, expected in test_cases:
    key = f"{inner}_{outer}"
    result = HEXAGRAM_LOOKUP.get(key)
    if result == expected:
        print(f"  [OK] {key} -> {result}")
    else:
        print(f"  [ERROR] {key} -> {result} (期望: {expected})")

