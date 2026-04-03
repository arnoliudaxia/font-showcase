import os
import json
import subprocess
import shutil
import urllib.parse
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR
SOURCE_DIR = PROJECT_DIR / '字体库'
SUBSETS_DIR = PROJECT_DIR / 'public' / 'subsets'
SUBSETS_DIR.mkdir(parents=True, exist_ok=True)

CDN_BASE = 'https://1812331343.v.123pan.cn/1812331343/%E7%9B%B4%E9%93%BE%E5%8A%A0%E9%80%9F/font/'

PREVIEW_TEXT = '字体预览 ABCD abcd 1234 岁月静好 设计之美'
UNIQUE_CHARS = ''.join(sorted(set(PREVIEW_TEXT)))

raw_entries = []

for root, dirs, files in os.walk(SOURCE_DIR):
    for f in files:
        if f.lower().endswith(('.ttf', '.otf', '.woff', '.woff2')):
            original_path = Path(root) / f
            rel_path = original_path.relative_to(SOURCE_DIR).as_posix()
            parts = rel_path.split('/')
            name = os.path.splitext(f)[0]
            ext = os.path.splitext(f)[1]
            # category 为完整层级路径，例如 Arno/中文字体/书法
            category = '/'.join(parts[:-1]) if len(parts) > 1 else '其他'
            safe_name = '_'.join(parts[:-1] + [name]).replace(' ', '_')
            subset_filename = safe_name + '.woff2'
            subset_path = SUBSETS_DIR / subset_filename

            original_dest_name = safe_name + ext
            # 原始文件使用 CDN 链接
            original_public_path = CDN_BASE + urllib.parse.quote(rel_path, safe='/')

            # 使用 pyftsubset 生成子集
            try:
                cmd = [
                    'python', '-m', 'fontTools.subset',
                    str(original_path),
                    f'--text={UNIQUE_CHARS}',
                    '--flavor=woff2',
                    f'--output-file={subset_path}',
                    '--layout-features=*',
                    '--glyph-names',
                    '--symbol-cmap',
                    '--legacy-cmap',
                    '--notdef-glyph',
                    '--notdef-outline',
                    '--recommended-glyphs',
                    '--name-IDs=*',
                    '--hinting',
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f'Warning: subset failed for {rel_path}: {result.stderr}')
                    # 如果子集化失败，回退使用原始文件作为子集展示
                    fallback_dir = PROJECT_DIR / 'public' / 'fonts'
                    fallback_dir.mkdir(parents=True, exist_ok=True)
                    fallback_path = fallback_dir / original_dest_name
                    shutil.copy2(original_path, fallback_path)
                    subset_path_relative = 'fonts/' + original_dest_name
                    file_size = fallback_path.stat().st_size
                else:
                    subset_path_relative = 'subsets/' + subset_filename
                    file_size = subset_path.stat().st_size
            except Exception as e:
                print(f'Error processing {rel_path}: {e}')
                continue

            raw_entries.append({
                'id': safe_name,
                'name': name,
                'category': category,
                'originalPath': original_public_path,
                'subsetPath': subset_path_relative,
                'size': file_size,
                'parts': parts,
            })
            print(f'Processed: {name} ({category}) -> subset:{subset_path_relative}, original:{original_public_path}')


def get_family(name):
    if '-' in name:
        return name.rsplit('-', 1)[0]
    return name


def variant_sort_key(item):
    suffix = item['name'].rsplit('-', 1)[1] if '-' in item['name'] else ''
    order = {
        'Thin': 0,
        'ExtraLight': 1,
        'Light': 2,
        'Regular': 3,
        'Normal': 4,
        'Medium': 5,
        'DemiBold': 6,
        'Bold': 7,
        'ExtraBold': 8,
        'Heavy': 9,
        'Black': 10,
    }
    if suffix in order:
        return (0, order[suffix], suffix)
    return (1, suffix, suffix)


# 按 category + family 分组
family_map = defaultdict(list)
for e in raw_entries:
    family = get_family(e['name'])
    family_map[(e['category'], family)].append(e)

fonts = []
for (cat, family), items in family_map.items():
    if len(items) == 1:
        # 单独字体
        item = items[0]
        fonts.append({
            'id': item['id'],
            'name': item['name'],
            'category': item['category'],
            'originalPath': item['originalPath'],
            'subsetPath': item['subsetPath'],
            'size': item['size'],
        })
    else:
        # 合并为家族
        items.sort(key=variant_sort_key)
        base = items[0]
        # 尝试优先用 Regular 作为预览
        regular_items = [i for i in items if i['name'].endswith('-Regular')]
        if regular_items:
            base = regular_items[0]

        safe_family = base['id'].rsplit('_', 1)[0] if '_' in base['id'] else base['id']
        if not safe_family.endswith(family.replace(' ', '_')):
            safe_family = safe_family + '_' + family.replace(' ', '_')

        variants = []
        for item in items:
            suffix = item['name'].rsplit('-', 1)[1] if '-' in item['name'] else 'default'
            variants.append({
                'name': item['name'],
                'weight': suffix,
                'originalPath': item['originalPath'],
                'subsetPath': item['subsetPath'],
                'size': item['size'],
            })

        fonts.append({
            'id': safe_family,
            'name': family,
            'category': cat,
            'originalPath': base['originalPath'],
            'subsetPath': base['subsetPath'],
            'size': base['size'],
            'variants': variants,
        })
        print(f'Merged family: {family} ({cat}) with {len(variants)} variants')

# 写入 src/fonts.json
fonts_json_path = PROJECT_DIR / 'src' / 'fonts.json'
fonts_json_path.parent.mkdir(parents=True, exist_ok=True)
with open(fonts_json_path, 'w', encoding='utf-8') as fp:
    json.dump(fonts, fp, ensure_ascii=False, indent=2)

print(f'\nTotal fonts: {len(fonts)}')
print(f'Fonts data written to {fonts_json_path}')
