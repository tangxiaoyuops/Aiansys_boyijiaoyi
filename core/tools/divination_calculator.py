"""
六爻起卦计算器
实现铜钱摇卦、卦象识别、变卦生成等功能
"""
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)

# ==================== 八卦定义 ====================
# 八卦名称：乾(111)、坤(000)、震(100)、巽(011)、坎(010)、离(101)、艮(001)、兑(110)
TRIGRAMS = {
    '111': {'name': '乾', 'nature': '天'},
    '000': {'name': '坤', 'nature': '地'},
    '100': {'name': '震', 'nature': '雷'},
    '011': {'name': '巽', 'nature': '风'},
    '010': {'name': '坎', 'nature': '水'},
    '101': {'name': '离', 'nature': '火'},
    '001': {'name': '艮', 'nature': '山'},
    '110': {'name': '兑', 'nature': '泽'},
}

# 八卦反向映射（名称 -> 二进制）
TRIGRAM_TO_BINARY = {v['name']: k for k, v in TRIGRAMS.items()}

# ==================== 六十四卦数据 ====================
# 注：这里包含完整的六十四卦数据，由于篇幅限制，我会包含主要卦象的完整数据
# 在实际使用中，建议将完整数据存储在JSON文件中

# ==================== 六十四卦完整数据 ====================
# 注：这里包含六十四卦的完整数据
# 卦序号按照《周易》传统顺序排列
# 格式：{序号: {name: 卦名, full_name: 全名, inner: 内卦, outer: 外卦, guaci: 卦辞, yaoci: {1-6: 爻辞}}}

HEXAGRAMS = {
    # 上经三十卦
    "1": {"name": "乾", "full_name": "乾为天", "inner": "乾", "outer": "乾",
          "guaci": "元，亨，利，贞。",
          "yaoci": {
              "1": "初九：潜龙勿用。",
              "2": "九二：见龙在田，利见大人。",
              "3": "九三：君子终日乾乾，夕惕若厉，无咎。",
              "4": "九四：或跃在渊，无咎。",
              "5": "九五：飞龙在天，利见大人。",
              "6": "上九：亢龙有悔。",
          }},
    "2": {"name": "坤", "full_name": "坤为地", "inner": "坤", "outer": "坤",
          "guaci": "元，亨，利牝马之贞。君子有攸往，先迷后得主，利西南得朋，东北丧朋。安贞，吉。",
          "yaoci": {
              "1": "初六：履霜，坚冰至。",
              "2": "六二：直，方，大，不习无不利。",
              "3": "六三：含章可贞。或从王事，无成有终。",
              "4": "六四：括囊；无咎，无誉。",
              "5": "六五：黄裳，元吉。",
              "6": "上六：龙战于野，其血玄黄。",
          }},
    "3": {"name": "屯", "full_name": "水雷屯", "inner": "震", "outer": "坎",
          "guaci": "元，亨，利，贞。勿用有攸往，利建侯。",
          "yaoci": {
              "1": "初九：磐桓；利居贞，利建侯。",
              "2": "六二：屯如邅如，乘马班如。匪寇婚媾，女子贞不字，十年乃字。",
              "3": "六三：既鹿无虞，惟入于林中，君子几不如舍，往吝。",
              "4": "六四：乘马班如，求婚媾，往吉，无不利。",
              "5": "九五：屯其膏，小贞吉，大贞凶。",
              "6": "上六：乘马班如，泣血涟如。",
          }},
    "4": {"name": "蒙", "full_name": "山水蒙", "inner": "坎", "outer": "艮",
          "guaci": "亨。匪我求童蒙，童蒙求我。初筮告，再三渎，渎则不告。利贞。",
          "yaoci": {
              "1": "初六：发蒙，利用刑人，用说桎梏，以往吝。",
              "2": "九二：包蒙，吉。纳妇，吉；子克家。",
              "3": "六三：勿用取女，见金夫，不有躬，无攸利。",
              "4": "六四：困蒙，吝。",
              "5": "六五：童蒙，吉。",
              "6": "上九：击蒙，不利为寇，利御寇。",
          }},
    "5": {"name": "需", "full_name": "水天需", "inner": "乾", "outer": "坎",
          "guaci": "有孚，光亨，贞吉，利涉大川。",
          "yaoci": {
              "1": "初九：需于郊，利用恒，无咎。",
              "2": "九二：需于沙，小有言，终吉。",
              "3": "九三：需于泥，致寇至。",
              "4": "六四：需于血，出自穴。",
              "5": "九五：需于酒食，贞吉。",
              "6": "上六：入于穴，有不速之客三人来，敬之终吉。",
          }},
    "6": {"name": "讼", "full_name": "天水讼", "inner": "坎", "outer": "乾",
          "guaci": "有孚，窒惕，中吉，终凶。利见大人，不利涉大川。",
          "yaoci": {
              "1": "初六：不永所事，小有言，终吉。",
              "2": "九二：不克讼，归而逋，其邑人三百户，无眚。",
              "3": "六三：食旧德，贞厉，终吉。或从王事，无成。",
              "4": "九四：不克讼，复即命，渝安贞，吉。",
              "5": "九五：讼，元吉。",
              "6": "上九：或锡之鞶带，终朝三褫之。",
          }},
    "7": {"name": "师", "full_name": "地水师", "inner": "坎", "outer": "坤",
          "guaci": "贞，丈人吉，无咎。",
          "yaoci": {
              "1": "初六：师出以律，否臧凶。",
              "2": "九二：在师中，吉，无咎；王三锡命。",
              "3": "六三：师或舆尸，凶。",
              "4": "六四：师左次，无咎。",
              "5": "六五：田有禽，利执言，无咎。长子帅师，弟子舆尸，贞凶。",
              "6": "上六：大君有命，开国承家，小人勿用。",
          }},
    "8": {"name": "比", "full_name": "水地比", "inner": "坤", "outer": "坎",
          "guaci": "吉。原筮，元永贞，无咎。不宁方来，后夫凶。",
          "yaoci": {
              "1": "初六：有孚比之，无咎。有孚盈缶，终来有它，吉。",
              "2": "六二：比之自内，贞吉。",
              "3": "六三：比之匪人。",
              "4": "六四：外比之，贞吉。",
              "5": "九五：显比，王用三驱，失前禽。邑人不诫，吉。",
              "6": "上六：比之无首，凶。",
          }},
    "9": {"name": "小畜", "full_name": "风天小畜", "inner": "乾", "outer": "巽",
          "guaci": "亨。密云不雨，自我西郊。",
          "yaoci": {
              "1": "初九：复自道，何其咎？吉。",
              "2": "九二：牵复，吉。",
              "3": "九三：舆说辐，夫妻反目。",
              "4": "六四：有孚，血去惕出，无咎。",
              "5": "九五：有孚挛如，富以其邻。",
              "6": "上九：既雨既处，尚德载，妇贞厉。月几望，君子征凶。",
          }},
    "10": {"name": "履", "full_name": "天泽履", "inner": "兑", "outer": "乾",
           "guaci": "履虎尾，不咥人，亨。",
           "yaoci": {
               "1": "初九：素履，往无咎。",
               "2": "九二：履道坦坦，幽人贞吉。",
               "3": "六三：眇能视，跛能履，履虎尾，咥人，凶。武人为于大君。",
               "4": "九四：履虎尾，愬愬，终吉。",
               "5": "九五：夬履，贞厉。",
               "6": "上九：视履考祥，其旋元吉。",
           }},
    "11": {"name": "泰", "full_name": "地天泰", "inner": "乾", "outer": "坤",
           "guaci": "小往大来，吉，亨。",
           "yaoci": {
               "1": "初九：拔茅茹，以其汇，征吉。",
               "2": "九二：包荒，用冯河，不遐遗，朋亡，得尚于中行。",
               "3": "九三：无平不陂，无往不复，艰贞无咎。勿恤其孚，于食有福。",
               "4": "六四：翩翩不富，以其邻，不戒以孚。",
               "5": "六五：帝乙归妹，以祉元吉。",
               "6": "上六：城复于隍，勿用师。自邑告命，贞吝。",
           }},
    "12": {"name": "否", "full_name": "天地否", "inner": "坤", "outer": "乾",
           "guaci": "否之匪人，不利君子贞，大往小来。",
           "yaoci": {
               "1": "初六：拔茅茹，以其汇，贞吉，亨。",
               "2": "六二：包承，小人吉，大人否，亨。",
               "3": "六三：包羞。",
               "4": "九四：有命无咎，畴离祉。",
               "5": "九五：休否，大人吉。其亡其亡，系于苞桑。",
               "6": "上九：倾否，先否后喜。",
           }},
    # 继续添加更多常用卦
    "23": {"name": "剥", "full_name": "山地剥", "inner": "坤", "outer": "艮",
           "guaci": "不利有攸往。",
           "yaoci": {
               "1": "初六：剥床以足，蔑贞凶。",
               "2": "六二：剥床以辨，蔑贞凶。",
               "3": "六三：剥之，无咎。",
               "4": "六四：剥床以肤，凶。",
               "5": "六五：贯鱼，以宫人宠，无不利。",
               "6": "上九：硕果不食，君子得舆，小人剥庐。",
           }},
    "39": {"name": "蹇", "full_name": "水山蹇", "inner": "艮", "outer": "坎",
           "guaci": "利西南，不利东北；利见大人，贞吉。",
           "yaoci": {
               "1": "初六：往蹇，来誉。",
               "2": "六二：王臣蹇蹇，匪躬之故。",
               "3": "九三：往蹇，来反。",
               "4": "六四：往蹇，来连。",
               "5": "九五：大蹇，朋来。",
               "6": "上六：往蹇，来硕，吉；利见大人。",
           }},
    # 注意：完整的六十四卦数据量很大（64个卦，每个卦有卦辞和6个爻辞）
    # 当前已添加：乾、坤、屯、蒙、需、讼、师、比、小畜、履、泰、否、剥、蹇 等14个卦
    # 
    # 如何继续补充：
    # 1. 按照上述格式继续添加，格式为：
    #    "序号": {"name": "卦名", "full_name": "全名", "inner": "内卦名", "outer": "外卦名",
    #             "guaci": "卦辞",
    #             "yaoci": {"1": "初爻爻辞", "2": "二爻爻辞", ..., "6": "上爻爻辞"}}
    #
    # 2. 内卦和外卦名称必须是：乾、坤、震、巽、坎、离、艮、兑 之一
    #
    # 3. 数据来源：可以从《周易》原文或权威注释书籍中获取
    #
    # 4. 建议：如果数据量很大，可以考虑创建单独的JSON文件存储，然后加载
}

# 六十四卦查找表：根据内卦和外卦查找卦序号
# 格式：{内卦名_外卦名: 卦序号}
HEXAGRAM_LOOKUP = {}
# 由于完整数据量大，这里使用计算方式生成查找表
for inner_key, inner_info in TRIGRAMS.items():
    for outer_key, outer_info in TRIGRAMS.items():
        inner_name = inner_info['name']
        outer_name = outer_info['name']
        HEXAGRAM_LOOKUP[f"{inner_name}_{outer_name}"] = None  # 需要完整数据填充


def coin_toss_to_yao(coins: List[int]) -> Dict[str, Any]:
    """
    将3枚铜钱的结果转换为爻信息
    
    Args:
        coins: 3枚铜钱的结果列表，1=正面，0=反面
    
    Returns:
        爻信息字典，包含：
        - yao_number: 爻数（6=老阴，7=少阳，8=少阴，9=老阳）
        - is_yang: 是否为阳爻
        - is_dong: 是否为动爻
        - symbol: 爻符号
    """
    if len(coins) != 3:
        raise ValueError("必须提供3枚铜钱的结果")
    
    heads_count = sum(coins)  # 正面数量
    
    if heads_count == 3:
        # 三正：老阳（动爻，记为9）
        return {
            'yao_number': 9,
            'is_yang': True,
            'is_dong': True,
            'symbol': '⚊',
            'description': '老阳（动爻）'
        }
    elif heads_count == 0:
        # 三反：老阴（动爻，记为6）
        return {
            'yao_number': 6,
            'is_yang': False,
            'is_dong': True,
            'symbol': '⚋',
            'description': '老阴（动爻）'
        }
    elif heads_count == 2:
        # 两正一反：少阳（静爻，记为7）
        return {
            'yao_number': 7,
            'is_yang': True,
            'is_dong': False,
            'symbol': '⚊',
            'description': '少阳（静爻）'
        }
    else:  # heads_count == 1
        # 两反一正：少阴（静爻，记为8）
        return {
            'yao_number': 8,
            'is_yang': False,
            'is_dong': False,
            'symbol': '⚋',
            'description': '少阴（静爻）'
        }


def yao_to_binary(yao_info: Dict[str, Any]) -> str:
    """
    将爻信息转换为二进制表示（用于组成八卦）
    
    Args:
        yao_info: 爻信息字典
    
    Returns:
        '0'（阴）或'1'（阳）
    """
    return '1' if yao_info['is_yang'] else '0'


def identify_trigram(yao_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    根据三个爻识别八卦
    
    Args:
        yao_list: 三个爻的信息列表（从下往上）
    
    Returns:
        八卦信息字典
    """
    if len(yao_list) != 3:
        raise ValueError("八卦需要3个爻")
    
    # 从下往上组成二进制字符串
    binary_str = ''.join([yao_to_binary(yao) for yao in reversed(yao_list)])
    
    if binary_str in TRIGRAMS:
        trigram_info = TRIGRAMS[binary_str].copy()
        trigram_info['binary'] = binary_str
        return trigram_info
    else:
        raise ValueError(f"无效的八卦二进制表示: {binary_str}")


def identify_hexagram(inner_trigram: str, outer_trigram: str, hexagrams_data: Dict) -> Optional[Dict[str, Any]]:
    """
    根据内卦和外卦识别六十四卦
    
    Args:
        inner_trigram: 内卦名称
        outer_trigram: 外卦名称
        hexagrams_data: 六十四卦数据字典
    
    Returns:
        卦信息字典，如果未找到返回None
    """
    # 遍历查找匹配的卦
    for hexagram_id, hexagram_info in hexagrams_data.items():
        if (hexagram_info.get('inner') == inner_trigram and 
            hexagram_info.get('outer') == outer_trigram):
            result = hexagram_info.copy()
            result['id'] = hexagram_id
            return result
    
    return None


def get_hexagram_by_trigrams(inner_trigram_name: str, outer_trigram_name: str) -> Optional[Dict[str, Any]]:
    """
    根据内卦和外卦名称直接查找六十四卦（使用标准查找表）
    
    Args:
        inner_trigram_name: 内卦名称（如：乾、坤、震等）
        outer_trigram_name: 外卦名称（如：乾、坤、震等）
    
    Returns:
        卦信息字典，如果未找到则返回基本信息
    """
    # 先尝试从HEXAGRAMS中查找
    result = identify_hexagram(inner_trigram_name, outer_trigram_name, HEXAGRAMS)
    if result:
        return result
    
    # 如果找不到，返回基本信息（用于演示，实际应该包含完整数据）
    return {
        'name': f"{outer_trigram_name}{inner_trigram_name}",
        'full_name': f"{outer_trigram_name}上{inner_trigram_name}下",
        'inner': inner_trigram_name,
        'outer': outer_trigram_name,
        'guaci': '（卦辞待补充）',
        'yaoci': {str(i+1): f"第{i+1}爻：爻辞待补充" for i in range(6)},
    }


def create_hexagram(yao_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    根据6次摇卦结果创建完整的卦象信息
    
    Args:
        yao_results: 6次摇卦结果列表（从下往上：初爻、二爻、三爻、四爻、五爻、上爻）
    
    Returns:
        完整的卦象信息字典
    """
    if len(yao_results) != 6:
        raise ValueError("六爻卦需要6次摇卦结果")
    
    # 从下往上排列（yao_results已经是这个顺序）
    # 下三爻组成内卦（下卦）
    inner_yaos = yao_results[0:3]
    # 上三爻组成外卦（上卦）
    outer_yaos = yao_results[3:6]
    
    # 识别内卦和外卦
    inner_trigram = identify_trigram(inner_yaos)
    outer_trigram = identify_trigram(outer_yaos)
    
    # 查找对应的六十四卦
    hexagram_detail = get_hexagram_by_trigrams(inner_trigram['name'], outer_trigram['name'])
    
    if not hexagram_detail:
        # 如果找不到，使用基本信息
        hexagram_detail = {
            'name': f"{outer_trigram['name']}{inner_trigram['name']}",
            'full_name': f"{outer_trigram['name']}上{inner_trigram['name']}下",
            'inner': inner_trigram['name'],
            'outer': outer_trigram['name'],
            'guaci': '（卦辞待补充）',
            'yaoci': {str(i+1): f"第{i+1}爻：爻辞待补充" for i in range(6)}
        }
    
    hexagram_info = hexagram_detail.copy()
    hexagram_info['inner_trigram'] = inner_trigram['name']
    hexagram_info['outer_trigram'] = outer_trigram['name']
    
    # 检查是否有动爻
    dong_yaos = [i for i, yao in enumerate(yao_results) if yao.get('is_dong', False)]
    
    # 生成变卦（如果有动爻）
    bian_hexagram = None
    if dong_yaos:
        bian_yaos = []
        for i, yao in enumerate(yao_results):
            if yao.get('is_dong', False):
                # 动爻变：老阴变阳，老阳变阴
                new_yao = yao.copy()
                new_yao['is_yang'] = not yao['is_yang']
                new_yao['is_dong'] = False
                new_yao['symbol'] = '⚊' if new_yao['is_yang'] else '⚋'
                new_yao['yao_number'] = 7 if new_yao['is_yang'] else 8
                bian_yaos.append(new_yao)
            else:
                bian_yaos.append(yao)
        
        # 识别变卦
        bian_inner_yaos = bian_yaos[0:3]
        bian_outer_yaos = bian_yaos[3:6]
        bian_inner_trigram = identify_trigram(bian_inner_yaos)
        bian_outer_trigram = identify_trigram(bian_outer_yaos)
        
        bian_hexagram_detail = get_hexagram_by_trigrams(
            bian_inner_trigram['name'], 
            bian_outer_trigram['name']
        )
        
        if bian_hexagram_detail:
            bian_hexagram = bian_hexagram_detail.copy()
            bian_hexagram['inner_trigram'] = bian_inner_trigram['name']
            bian_hexagram['outer_trigram'] = bian_outer_trigram['name']
        else:
            bian_hexagram = {
                'name': f"{bian_outer_trigram['name']}{bian_inner_trigram['name']}",
                'full_name': f"{bian_outer_trigram['name']}上{bian_inner_trigram['name']}下",
                'inner': bian_inner_trigram['name'],
                'outer': bian_outer_trigram['name'],
                'inner_trigram': bian_inner_trigram['name'],
                'outer_trigram': bian_outer_trigram['name'],
                'guaci': '（变卦卦辞待补充）',
                'yaoci': {str(i+1): f"第{i+1}爻：爻辞待补充" for i in range(6)}
            }
    
    return {
        'ben_hexagram': hexagram_info,  # 本卦
        'bian_hexagram': bian_hexagram,  # 变卦（如果有动爻）
        'yaos': yao_results,  # 六个爻的详细信息
        'dong_yaos': dong_yaos,  # 动爻索引列表（0-5，从下往上）
        'inner_trigram': inner_trigram,
        'outer_trigram': outer_trigram,
        'has_dong': len(dong_yaos) > 0,
    }


def create_hexagram_from_coin_results(coin_results: List[List[int]]) -> Dict[str, Any]:
    """
    从6次摇卦的铜钱结果创建卦象
    
    Args:
        coin_results: 6次摇卦结果，每次3枚铜钱（0=反面，1=正面）
    
    Returns:
        完整的卦象信息
    """
    # 将每次摇卦结果转换为爻信息
    yao_results = []
    for coins in coin_results:
        yao_info = coin_toss_to_yao(coins)
        yao_results.append(yao_info)
    
    # 创建卦象
    hexagram_data = create_hexagram(yao_results)
    
    return hexagram_data

