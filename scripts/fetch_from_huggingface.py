"""
从HuggingFace获取《黄帝内经》数据集
"""
import os
import sys
from pathlib import Path
import requests
import json

project_root = Path(__file__).parent.parent
raw_dir = project_root / "data" / "huangdi_neijing" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)


def search_huggingface_datasets():
    """搜索HuggingFace上的黄帝内经数据集"""
    print("=" * 70)
    print("搜索HuggingFace上的《黄帝内经》数据集")
    print("=" * 70)
    print()
    
    # HuggingFace API搜索
    search_url = "https://huggingface.co/api/datasets"
    search_params = {
        "search": "黄帝内经",
        "limit": 10
    }
    
    try:
        print("正在搜索HuggingFace数据集...")
        response = requests.get(search_url, params=search_params, timeout=10)
        if response.status_code == 200:
            results = response.json()
            print(f"找到 {len(results)} 个相关数据集")
            for dataset in results:
                print(f"  - {dataset.get('id', 'unknown')}")
        else:
            print(f"搜索失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"搜索失败: {e}")
    
    print()
    print("=" * 70)
    print("推荐的HuggingFace数据集")
    print("=" * 70)
    print()
    print("可能的数据集ID（需要手动验证）:")
    print("  1. ChineseText/黄帝内经")
    print("  2. garychowcmu/ChineseText (可能包含黄帝内经)")
    print("  3. 搜索关键词: 'huangdi neijing' 或 '黄帝内经'")
    print()
    print("使用方法:")
    print("  1. 访问: https://huggingface.co/datasets")
    print("  2. 搜索: '黄帝内经' 或 'huangdi neijing'")
    print("  3. 找到数据集后，可以使用以下代码下载:")
    print()
    print("```python")
    print("from datasets import load_dataset")
    print("")
    print("# 加载数据集")
    print("dataset = load_dataset('数据集ID')")
    print("")
    print("# 保存为文本文件")
    print("for split in dataset.keys():")
    print("    data = dataset[split]")
    print("    # 处理并保存...")
    print("```")
    print()


def download_from_huggingface(dataset_id: str = None):
    """
    从HuggingFace下载数据集
    
    Args:
        dataset_id: 数据集ID，如果为None则尝试常见ID
    """
    if dataset_id is None:
        # 尝试常见的可能ID
        possible_ids = [
            "ChineseText/黄帝内经",
            "garychowcmu/ChineseText",
        ]
        
        print("尝试从HuggingFace下载...")
        for ds_id in possible_ids:
            try:
                print(f"尝试数据集: {ds_id}")
                # 这里需要安装datasets库: pip install datasets
                try:
                    from datasets import load_dataset
                    
                    dataset = load_dataset(ds_id)
                    print(f"✓ 成功加载数据集: {ds_id}")
                    
                    # 处理数据集
                    process_dataset(dataset, ds_id)
                    return True
                except ImportError:
                    print("需要安装datasets库: pip install datasets")
                    return False
                except Exception as e:
                    print(f"✗ 加载失败: {e}")
                    continue
            except Exception as e:
                print(f"✗ 尝试 {ds_id} 失败: {e}")
                continue
        
        print("\n无法自动找到数据集，请手动搜索并下载")
        return False
    else:
        try:
            from datasets import load_dataset
            dataset = load_dataset(dataset_id)
            process_dataset(dataset, dataset_id)
            return True
        except Exception as e:
            print(f"下载失败: {e}")
            return False


def process_dataset(dataset, dataset_id: str):
    """处理下载的数据集，保存为文本文件"""
    print(f"\n处理数据集: {dataset_id}")
    
    suwen_content = []
    lingshu_content = []
    
    # 遍历数据集的所有split
    for split_name in dataset.keys():
        print(f"处理split: {split_name}")
        split_data = dataset[split_name]
        
        for item in split_data:
            # 根据数据集结构提取内容
            text = item.get('text', '') or item.get('content', '') or str(item)
            
            # 判断是素问还是灵枢
            if '素问' in text or 'suwen' in str(item).lower():
                suwen_content.append(text)
            elif '灵枢' in text or 'lingshu' in str(item).lower():
                lingshu_content.append(text)
            else:
                # 如果无法判断，根据文件名或其他字段判断
                filename = item.get('filename', '') or item.get('file', '')
                if '素问' in filename or 'suwen' in filename.lower():
                    suwen_content.append(text)
                elif '灵枢' in filename or 'lingshu' in filename.lower():
                    lingshu_content.append(text)
    
    # 保存文件
    if suwen_content:
        suwen_file = raw_dir / "suwen.txt"
        with open(suwen_file, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(suwen_content))
        print(f"✓ 素问已保存: {suwen_file} ({len(suwen_content)} 条)")
    
    if lingshu_content:
        lingshu_file = raw_dir / "lingshu.txt"
        with open(lingshu_file, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(lingshu_content))
        print(f"✓ 灵枢已保存: {lingshu_file} ({len(lingshu_content)} 条)")


def main():
    """主函数"""
    print("HuggingFace数据集获取工具")
    print("=" * 70)
    print()
    
    # 搜索数据集
    search_huggingface_datasets()
    
    # 尝试下载
    print("\n" + "=" * 70)
    print("尝试下载数据集")
    print("=" * 70)
    print()
    
    # 检查是否安装了datasets库
    try:
        import datasets
        print("✓ datasets库已安装")
        
        # 尝试下载
        success = download_from_huggingface()
        
        if success:
            print("\n✓ 数据集下载成功！")
            print("下一步: 运行 python core/tools/init_huangdi_kb.py 初始化知识库")
        else:
            print("\n提示: 无法自动下载，请手动操作:")
            print("1. 访问 https://huggingface.co/datasets")
            print("2. 搜索 '黄帝内经' 或 'huangdi neijing'")
            print("3. 找到数据集后，使用以下代码下载:")
            print()
            print("   from datasets import load_dataset")
            print("   dataset = load_dataset('数据集ID')")
            print("   # 然后处理并保存数据")
            
    except ImportError:
        print("✗ datasets库未安装")
        print("安装命令: pip install datasets")
        print()
        print("安装后可以:")
        print("1. 访问 https://huggingface.co/datasets 搜索数据集")
        print("2. 使用 load_dataset() 加载数据集")
        print("3. 处理并保存为文本文件")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

