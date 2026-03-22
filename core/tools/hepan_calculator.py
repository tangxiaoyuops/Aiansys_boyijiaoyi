"""
八字合盘计算器
实现两个命盘的匹配度分析
"""
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

# ==================== 合盘常量定义 ====================

# 地支六合（相合）
DI_ZHI_LIU_HE = {
    ('子', '丑'): '土',  # 子丑合化土
    ('寅', '亥'): '木',  # 寅亥合化木
    ('卯', '戌'): '火',  # 卯戌合化火
    ('辰', '酉'): '金',  # 辰酉合化金
    ('巳', '申'): '水',  # 巳申合化水
    ('午', '未'): '火',  # 午未合化火
}

# 地支六冲（相冲）
DI_ZHI_LIU_CHONG = [
    ('子', '午'),  # 子午冲
    ('丑', '未'),  # 丑未冲
    ('寅', '申'),  # 寅申冲
    ('卯', '酉'),  # 卯酉冲
    ('辰', '戌'),  # 辰戌冲
    ('巳', '亥'),  # 巳亥冲
]

# 地支三合
DI_ZHI_SAN_HE = {
    '申子辰': '水',  # 申子辰三合水局
    '亥卯未': '木',  # 亥卯未三合木局
    '寅午戌': '火',  # 寅午戌三合火局
    '巳酉丑': '金',  # 巳酉丑三合金局
}

# 天干五合
TIAN_GAN_WU_HE = {
    ('甲', '己'): '土',  # 甲己合化土
    ('乙', '庚'): '金',  # 乙庚合化金
    ('丙', '辛'): '水',  # 丙辛合化水
    ('丁', '壬'): '木',  # 丁壬合化木
    ('戊', '癸'): '火',  # 戊癸合化火
}

# 五行相生关系
WUXING_SHENG = {
    '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
}

# 五行相克关系
WUXING_KE = {
    '木': '土', '火': '金', '土': '水', '金': '木', '水': '火'
}

# 天干五行
TIAN_GAN_WUXING = {
    '甲': '木', '乙': '木',
    '丙': '火', '丁': '火',
    '戊': '土', '己': '土',
    '庚': '金', '辛': '金',
    '壬': '水', '癸': '水',
}

# 地支五行
DI_ZHI_WUXING = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水',
}

# 天干阴阳
TIAN_GAN_YINYANG = {
    '甲': '阳', '乙': '阴', '丙': '阳', '丁': '阴',
    '戊': '阳', '己': '阴', '庚': '阳', '辛': '阴',
    '壬': '阳', '癸': '阴',
}

# 十神定义（日主为中心）
# 十神：正财、偏财、正官、偏官（七杀）、正印、偏印、比肩、劫财、食神、伤官
SHISHEN_NAMES = {
    ('同', '同'): '比肩',  # 同我者，阴阳相同
    ('同', '异'): '劫财',  # 同我者，阴阳不同
    ('生', '同'): '食神',  # 我生者，阴阳相同
    ('生', '异'): '伤官',  # 我生者，阴阳不同
    ('克', '同'): '偏财',  # 我克者，阴阳相同
    ('克', '异'): '正财',  # 我克者，阴阳不同
    ('克我', '同'): '偏官',  # 克我者，阴阳相同（七杀）
    ('克我', '异'): '正官',  # 克我者，阴阳不同
    ('生我', '同'): '偏印',  # 生我者，阴阳相同
    ('生我', '异'): '正印',  # 生我者，阴阳不同
}

# 夫妻星定义
# 男命以财星为妻星，女命以官星为夫星
SPOUSE_STAR = {
    '男': ['正财', '偏财'],  # 男命财星为妻
    '女': ['正官', '偏官'],  # 女命官星为夫
}


# ==================== 核心计算函数 ====================

def get_all_gan_zhi(sizhu: Dict) -> Tuple[List[str], List[str]]:
    """
    获取四柱中所有的天干和地支
    
    Args:
        sizhu: 四柱数据
    
    Returns:
        (天干列表, 地支列表)
    """
    gans = []
    zhis = []
    
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        zhu = sizhu.get(zhu_name, {})
        gan = zhu.get('tian_gan', '')
        zhi = zhu.get('di_zhi', '')
        if gan:
            gans.append(gan)
        if zhi:
            zhis.append(zhi)
    
    return gans, zhis


def get_shishen_for_gan(rizhu_gan: str, target_gan: str) -> str:
    """
    根据日主天干和目标天干计算十神
    
    Args:
        rizhu_gan: 日主天干
        target_gan: 目标天干
    
    Returns:
        十神名称
    """
    if rizhu_gan not in TIAN_GAN_WUXING or target_gan not in TIAN_GAN_WUXING:
        return ''
    
    wx_rizhu = TIAN_GAN_WUXING[rizhu_gan]
    wx_target = TIAN_GAN_WUXING[target_gan]
    
    # 判断阴阳关系
    yinyang_rizhu = TIAN_GAN_YINYANG.get(rizhu_gan, '')
    yinyang_target = TIAN_GAN_YINYANG.get(target_gan, '')
    yinyang_rel = '同' if yinyang_rizhu == yinyang_target else '异'
    
    # 判断五行关系
    if wx_rizhu == wx_target:
        relation = '同'
    elif WUXING_SHENG.get(wx_rizhu) == wx_target:
        relation = '生'
    elif WUXING_KE.get(wx_rizhu) == wx_target:
        relation = '克'
    elif WUXING_KE.get(wx_target) == wx_rizhu:
        relation = '克我'
    elif WUXING_SHENG.get(wx_target) == wx_rizhu:
        relation = '生我'
    else:
        return ''
    
    return SHISHEN_NAMES.get((relation, yinyang_rel), '')


def analyze_spouse_star_match(
    sizhu_a: Dict, 
    sizhu_b: Dict, 
    gender_a: str = '男', 
    gender_b: str = '女'
) -> Dict[str, Any]:
    """
    分析夫妻星匹配（十神配合分析）
    
    传统合婚规则：
    - 男命日主看对方的财星（妻星）
    - 女命日主看对方的官星（夫星）
    
    Args:
        sizhu_a: 命盘A的四柱数据
        sizhu_b: 命盘B的四柱数据
        gender_a: 命盘A性别
        gender_b: 命盘B性别
    
    Returns:
        夫妻星匹配分析结果
    """
    gans_a, _ = get_all_gan_zhi(sizhu_a)
    gans_b, _ = get_all_gan_zhi(sizhu_b)
    
    rizhu_a = sizhu_a.get('ri_zhu_tiangan', '')
    rizhu_b = sizhu_b.get('ri_zhu_tiangan', '')
    
    if not rizhu_a or not rizhu_b:
        return {'score': 0, 'desc': '无法确定日主', 'details': []}
    
    details = []
    score = 0
    
    # 分析命盘A对命盘B的夫妻星
    spouse_stars_a = SPOUSE_STAR.get(gender_a, [])
    for gan_b in gans_b:
        shishen = get_shishen_for_gan(rizhu_a, gan_b)
        if shishen in spouse_stars_a:
            details.append({
                'type': 'a_to_b',
                'desc': f'命盘A日主{rizhu_a}见命盘B{gan_b}为{shishen}（{"妻星" if gender_a == "男" else "夫星"}）',
                'positive': True
            })
            score += 4
    
    # 分析命盘B对命盘A的夫妻星
    spouse_stars_b = SPOUSE_STAR.get(gender_b, [])
    for gan_a in gans_a:
        shishen = get_shishen_for_gan(rizhu_b, gan_a)
        if shishen in spouse_stars_b:
            details.append({
                'type': 'b_to_a',
                'desc': f'命盘B日主{rizhu_b}见命盘A{gan_a}为{shishen}（{"夫星" if gender_b == "女" else "妻星"}）',
                'positive': True
            })
            score += 4
    
    # 分析日主相生关系（已有逻辑，此处补充十神视角）
    wx_a = TIAN_GAN_WUXING.get(rizhu_a, '')
    wx_b = TIAN_GAN_WUXING.get(rizhu_b, '')
    
    if wx_a and wx_b:
        # 男命日主生女命日主，有情
        if gender_a == '男' and WUXING_SHENG.get(wx_a) == wx_b:
            details.append({
                'type': 'rizhu_sheng',
                'desc': f'男命日主{rizhu_a}生女命日主{rizhu_b}，夫对妻有情',
                'positive': True
            })
            score += 3
        # 女命日主生男命日主，也有情
        elif gender_b == '女' and WUXING_SHENG.get(wx_b) == wx_a:
            details.append({
                'type': 'rizhu_sheng',
                'desc': f'女命日主{rizhu_b}生男命日主{rizhu_a}，妻对夫有情',
                'positive': True
            })
            score += 3
    
    return {
        'score': min(15, score),
        'desc': f'夫妻星匹配得分{min(15, score)}分',
        'details': details
    }


def analyze_di_zhi_he_chong(zhis_a: List[str], zhis_b: List[str]) -> Dict[str, Any]:
    """
    分析两个命盘地支之间的六合、六冲、三合关系
    
    Args:
        zhis_a: 命盘A的地支列表
        zhis_b: 命盘B的地支列表
    
    Returns:
        地支关系分析结果
    """
    he_relations = []  # 六合关系
    chong_relations = []  # 六冲关系
    san_he_relations = []  # 三合关系
    
    # 合并两个命盘的地支
    all_zhis = set(zhis_a + zhis_b)
    
    # 检查六合
    for zhi_a in zhis_a:
        for zhi_b in zhis_b:
            pair = (zhi_a, zhi_b)
            reverse_pair = (zhi_b, zhi_a)
            
            if pair in DI_ZHI_LIU_HE:
                he_relations.append({
                    'zhi_a': zhi_a,
                    'zhi_b': zhi_b,
                    'hua': DI_ZHI_LIU_HE[pair],
                    'desc': f'{zhi_a}{zhi_b}合化{DI_ZHI_LIU_HE[pair]}'
                })
            elif reverse_pair in DI_ZHI_LIU_HE:
                he_relations.append({
                    'zhi_a': zhi_a,
                    'zhi_b': zhi_b,
                    'hua': DI_ZHI_LIU_HE[reverse_pair],
                    'desc': f'{zhi_a}{zhi_b}合化{DI_ZHI_LIU_HE[reverse_pair]}'
                })
    
    # 检查六冲
    for zhi_a in zhis_a:
        for zhi_b in zhis_b:
            pair = (zhi_a, zhi_b)
            reverse_pair = (zhi_b, zhi_a)
            
            if pair in DI_ZHI_LIU_CHONG or reverse_pair in DI_ZHI_LIU_CHONG:
                chong_relations.append({
                    'zhi_a': zhi_a,
                    'zhi_b': zhi_b,
                    'desc': f'{zhi_a}{zhi_b}相冲'
                })
    
    # 检查三合（双方地支合并后检查）
    for san_he_key, hua_wuxing in DI_ZHI_SAN_HE.items():
        zhi_list = list(san_he_key)  # 例如 ['申', '子', '辰']
        # 检查是否所有三个地支都存在于双方命盘中
        if all(zhi in all_zhis for zhi in zhi_list):
            # 分析每个地支来自哪个命盘
            zhi_sources = []
            for zhi in zhi_list:
                in_a = zhi in zhis_a
                in_b = zhi in zhis_b
                if in_a and in_b:
                    source = '双方都有'
                elif in_a:
                    source = '命盘A'
                else:
                    source = '命盘B'
                zhi_sources.append({'zhi': zhi, 'source': source})
            
            san_he_relations.append({
                'combination': san_he_key,
                'hua': hua_wuxing,
                'zhi_sources': zhi_sources,
                'desc': f'{san_he_key}三合{hua_wuxing}局'
            })
    
    return {
        'liu_he': he_relations,
        'liu_chong': chong_relations,
        'san_he': san_he_relations,
        'he_count': len(he_relations),
        'chong_count': len(chong_relations),
        'san_he_count': len(san_he_relations),
    }


def analyze_tian_gan_he(gans_a: List[str], gans_b: List[str]) -> Dict[str, Any]:
    """
    分析两个命盘天干之间的五合关系
    
    Args:
        gans_a: 命盘A的天干列表
        gans_b: 命盘B的天干列表
    
    Returns:
        天干合化分析结果
    """
    he_relations = []
    
    for gan_a in gans_a:
        for gan_b in gans_b:
            pair = (gan_a, gan_b)
            reverse_pair = (gan_b, gan_a)
            
            if pair in TIAN_GAN_WU_HE:
                he_relations.append({
                    'gan_a': gan_a,
                    'gan_b': gan_b,
                    'hua': TIAN_GAN_WU_HE[pair],
                    'desc': f'{gan_a}{gan_b}合化{TIAN_GAN_WU_HE[pair]}'
                })
            elif reverse_pair in TIAN_GAN_WU_HE:
                he_relations.append({
                    'gan_a': gan_a,
                    'gan_b': gan_b,
                    'hua': TIAN_GAN_WU_HE[reverse_pair],
                    'desc': f'{gan_a}{gan_b}合化{TIAN_GAN_WU_HE[reverse_pair]}'
                })
    
    return {
        'wu_he': he_relations,
        'he_count': len(he_relations),
    }


def analyze_wuxing_match(sizhu_a: Dict, sizhu_b: Dict) -> Dict[str, Any]:
    """
    分析两个命盘的五行互补情况
    
    Args:
        sizhu_a: 命盘A的四柱数据
        sizhu_b: 命盘B的四柱数据
    
    Returns:
        五行互补分析结果
    """
    # 获取两个命盘的五行分布
    gans_a, zhis_a = get_all_gan_zhi(sizhu_a)
    gans_b, zhis_b = get_all_gan_zhi(sizhu_b)
    
    # 统计五行数量
    def count_wuxing(gans: List[str], zhis: List[str]) -> Dict[str, int]:
        count = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
        for gan in gans:
            if gan in TIAN_GAN_WUXING:
                count[TIAN_GAN_WUXING[gan]] += 1
        for zhi in zhis:
            if zhi in DI_ZHI_WUXING:
                count[DI_ZHI_WUXING[zhi]] += 1
        return count
    
    wuxing_a = count_wuxing(gans_a, zhis_a)
    wuxing_b = count_wuxing(gans_b, zhis_b)
    
    # 分析互补情况
    complement = []  # 互补的五行
    conflict = []    # 冲突的五行
    
    for wx in ['金', '木', '水', '火', '土']:
        total = wuxing_a[wx] + wuxing_b[wx]
        
        # 一方缺，另一方有 - 互补
        if wuxing_a[wx] == 0 and wuxing_b[wx] > 0:
            complement.append({
                'wuxing': wx,
                'desc': f'命盘A缺{wx}，命盘B有{wx}，可互补'
            })
        elif wuxing_b[wx] == 0 and wuxing_a[wx] > 0:
            complement.append({
                'wuxing': wx,
                'desc': f'命盘B缺{wx}，命盘A有{wx}，可互补'
            })
        
        # 双方都过多 - 可能冲突
        if wuxing_a[wx] >= 2 and wuxing_b[wx] >= 2:
            conflict.append({
                'wuxing': wx,
                'desc': f'双方{wx}都偏多，可能导致{wx}气过旺'
            })
    
    return {
        'wuxing_a': wuxing_a,
        'wuxing_b': wuxing_b,
        'complement': complement,
        'conflict': conflict,
        'complement_count': len(complement),
        'conflict_count': len(conflict),
    }


def analyze_rizhu_relation(sizhu_a: Dict, sizhu_b: Dict) -> Dict[str, Any]:
    """
    分析两个命盘日主之间的关系
    
    Args:
        sizhu_a: 命盘A的四柱数据
        sizhu_b: 命盘B的四柱数据
    
    Returns:
        日主关系分析结果
    """
    # 获取日主
    rizhu_a = sizhu_a.get('ri_zhu_tiangan', '')
    rizhu_b = sizhu_b.get('ri_zhu_tiangan', '')
    
    if not rizhu_a or not rizhu_b:
        return {'relation': 'unknown', 'desc': '无法确定日主关系'}
    
    wx_a = TIAN_GAN_WUXING.get(rizhu_a, '')
    wx_b = TIAN_GAN_WUXING.get(rizhu_b, '')
    
    if not wx_a or not wx_b:
        return {'relation': 'unknown', 'desc': '无法确定日主五行'}
    
    relations = []
    
    # 检查相生关系
    if WUXING_SHENG.get(wx_a) == wx_b:
        relations.append({
            'type': 'sheng',
            'direction': 'a_to_b',
            'desc': f'命盘A日主({rizhu_a}{wx_a})生命盘B日主({rizhu_b}{wx_b})，有情'
        })
    
    if WUXING_SHENG.get(wx_b) == wx_a:
        relations.append({
            'type': 'sheng',
            'direction': 'b_to_a',
            'desc': f'命盘B日主({rizhu_b}{wx_b})生命盘A日主({rizhu_a}{wx_a})，有情'
        })
    
    # 检查相克关系
    if WUXING_KE.get(wx_a) == wx_b:
        relations.append({
            'type': 'ke',
            'direction': 'a_to_b',
            'desc': f'命盘A日主({rizhu_a}{wx_a})克命盘B日主({rizhu_b}{wx_b})，需注意'
        })
    
    if WUXING_KE.get(wx_b) == wx_a:
        relations.append({
            'type': 'ke',
            'direction': 'b_to_a',
            'desc': f'命盘B日主({rizhu_b}{wx_b})克命盘A日主({rizhu_a}{wx_a})，需注意'
        })
    
    # 检查相同关系
    if wx_a == wx_b:
        relations.append({
            'type': 'same',
            'desc': f'双方日主同属{wx_a}，性格相近'
        })
    
    # 判断整体关系
    sheng_count = sum(1 for r in relations if r['type'] == 'sheng')
    ke_count = sum(1 for r in relations if r['type'] == 'ke')
    
    if ke_count > 0 and sheng_count == 0:
        overall = 'challenging'
        overall_desc = '日主相克，需要互相包容理解'
    elif sheng_count > 0 and ke_count == 0:
        overall = 'harmonious'
        overall_desc = '日主相生，天然有默契'
    elif sheng_count > 0 and ke_count > 0:
        overall = 'mixed'
        overall_desc = '日主关系复杂，需要互相磨合'
    else:
        overall = 'neutral'
        overall_desc = '日主关系平和，相处融洽'
    
    return {
        'rizhu_a': rizhu_a,
        'rizhu_b': rizhu_b,
        'wuxing_a': wx_a,
        'wuxing_b': wx_b,
        'relations': relations,
        'overall': overall,
        'overall_desc': overall_desc,
    }


def calculate_hepan_score(
    di_zhi_result: Dict,
    tian_gan_result: Dict,
    wuxing_result: Dict,
    rizhu_result: Dict,
    spouse_star_result: Dict = None,
    hepan_type: str = 'couple'
) -> Dict[str, Any]:
    """
    计算合盘匹配度得分
    
    评分权重：
    - 地支六合六冲三合: 25%
    - 五行互补: 25%
    - 日主关系: 20%
    - 天干合化: 15%
    - 十神配合（夫妻星匹配）: 15%
    
    Args:
        di_zhi_result: 地支关系分析结果
        tian_gan_result: 天干合化分析结果
        wuxing_result: 五行互补分析结果
        rizhu_result: 日主关系分析结果
        spouse_star_result: 夫妻星匹配结果（可选）
        hepan_type: 合盘类型 ('couple' | 'business')
    
    Returns:
        评分结果
    """
    scores = {}
    
    # 1. 地支评分 (满分25分) - 纳入三合
    he_count = di_zhi_result.get('he_count', 0)
    chong_count = di_zhi_result.get('chong_count', 0)
    san_he_count = di_zhi_result.get('san_he_count', 0)
    
    # 每个六合+5分，每个三合+6分，每个六冲-8分
    di_zhi_score = min(25, max(0, 10 + he_count * 5 + san_he_count * 6 - chong_count * 8))
    scores['di_zhi'] = di_zhi_score
    
    desc_parts = []
    if he_count > 0:
        desc_parts.append(f'六合{he_count}组')
    if san_he_count > 0:
        desc_parts.append(f'三合{san_he_count}组')
    if chong_count > 0:
        desc_parts.append(f'六冲{chong_count}组')
    scores['di_zhi_desc'] = '，'.join(desc_parts) if desc_parts else '无明显组合'
    
    # 2. 五行互补评分 (满分25分)
    complement_count = wuxing_result.get('complement_count', 0)
    conflict_count = wuxing_result.get('conflict_count', 0)
    
    # 每个互补+5分，每个冲突-5分
    wuxing_score = min(25, max(0, 15 + complement_count * 3 - conflict_count * 5))
    scores['wuxing'] = wuxing_score
    scores['wuxing_desc'] = f'互补{complement_count}项，冲突{conflict_count}项'
    
    # 3. 日主关系评分 (满分20分)
    overall = rizhu_result.get('overall', 'neutral')
    if overall == 'harmonious':
        rizhu_score = 20
    elif overall == 'neutral':
        rizhu_score = 15
    elif overall == 'mixed':
        rizhu_score = 10
    else:  # challenging
        rizhu_score = 5
    scores['rizhu'] = rizhu_score
    scores['rizhu_desc'] = rizhu_result.get('overall_desc', '')
    
    # 4. 天干合化评分 (满分15分)
    gan_he_count = tian_gan_result.get('he_count', 0)
    tian_gan_score = min(15, gan_he_count * 5)
    scores['tian_gan'] = tian_gan_score
    scores['tian_gan_desc'] = f'天干五合{gan_he_count}组'
    
    # 5. 十神配合评分 (满分15分) - 使用夫妻星匹配分析
    if spouse_star_result and spouse_star_result.get('score', 0) > 0:
        shishen_score = spouse_star_result.get('score', 0)
        scores['shishen'] = shishen_score
        scores['shishen_desc'] = spouse_star_result.get('desc', '')
        scores['shishen_details'] = spouse_star_result.get('details', [])
    else:
        # 回退到简化版：根据日主相生关系加分
        sheng_relations = [r for r in rizhu_result.get('relations', []) if r.get('type') == 'sheng']
        shishen_score = min(15, len(sheng_relations) * 8)
        scores['shishen'] = shishen_score
        scores['shishen_desc'] = f'日主相生关系{len(sheng_relations)}组'
        scores['shishen_details'] = []
    
    # 总分
    total = scores['di_zhi'] + scores['wuxing'] + scores['rizhu'] + scores['tian_gan'] + scores['shishen']
    scores['total'] = total
    
    # 等级评定
    if total >= 80:
        grade = '优秀'
        grade_desc = '命盘契合度极高，是难得的良配'
    elif total >= 65:
        grade = '良好'
        grade_desc = '命盘契合度较高，适合长期发展'
    elif total >= 50:
        grade = '中等'
        grade_desc = '命盘契合度一般，需要互相磨合'
    else:
        grade = '较弱'
        grade_desc = '命盘契合度较低，需要更多包容理解'
    
    scores['grade'] = grade
    scores['grade_desc'] = grade_desc
    
    return scores


def generate_suggestions(
    scores: Dict,
    di_zhi_result: Dict,
    wuxing_result: Dict,
    rizhu_result: Dict,
    spouse_star_result: Dict = None,
    hepan_type: str = 'couple'
) -> List[str]:
    """
    生成合盘建议
    
    Args:
        scores: 评分结果
        di_zhi_result: 地支关系分析结果
        wuxing_result: 五行互补分析结果
        rizhu_result: 日主关系分析结果
        spouse_star_result: 夫妻星匹配结果
        hepan_type: 合盘类型
    
    Returns:
        建议列表
    """
    suggestions = []
    
    # 地支建议
    if di_zhi_result.get('chong_count', 0) > 0:
        suggestions.append('地支有冲，建议在生活中多沟通，避免因小事争执')
    if di_zhi_result.get('he_count', 0) >= 2:
        suggestions.append('地支多组合，缘分深厚，感情基础稳固')
    if di_zhi_result.get('san_he_count', 0) > 0:
        san_he_desc = '、'.join([sh['desc'] for sh in di_zhi_result.get('san_he', [])])
        suggestions.append(f'地支有三合局（{san_he_desc}），能量互助，合作默契')
    
    # 五行建议
    for comp in wuxing_result.get('complement', []):
        suggestions.append(comp['desc'] + '，在生活中可以互相补益')
    for conf in wuxing_result.get('conflict', []):
        suggestions.append(conf['desc'] + '，需注意调节')
    
    # 日主建议
    overall = rizhu_result.get('overall', 'neutral')
    if overall == 'harmonious':
        suggestions.append('日主相生，天然有默契，感情容易升温')
    elif overall == 'challenging':
        suggestions.append('日主相克，需要更多耐心和包容，学会换位思考')
    
    # 夫妻星建议（仅情侣合婚）
    if hepan_type == 'couple' and spouse_star_result:
        details = spouse_star_result.get('details', [])
        if details:
            has_spouse_star = any(d.get('positive') for d in details if '妻星' in d.get('desc', '') or '夫星' in d.get('desc', ''))
            if has_spouse_star:
                suggestions.append('命中见对方夫妻星，缘分注定，感情发展顺利')
    
    # 根据合盘类型给出特定建议
    if hepan_type == 'couple':
        if scores.get('total', 0) >= 70:
            suggestions.append('整体契合度高，适合走进婚姻，建议珍惜这份缘分')
        elif scores.get('total', 0) < 50:
            suggestions.append('婚姻需要经营，建议多关注对方的优点，共同努力')
    else:  # business
        if scores.get('total', 0) >= 70:
            suggestions.append('合作契合度高，适合长期商业合作')
        elif scores.get('total', 0) < 50:
            suggestions.append('商业合作需谨慎，建议明确分工，建立良好的沟通机制')
    
    return suggestions


def calculate_hepan(
    sizhu_a: Dict,
    sizhu_b: Dict,
    hepan_type: str = 'couple',
    gender_a: str = '男',
    gender_b: str = '女'
) -> Dict[str, Any]:
    """
    计算两个命盘的合盘匹配度
    
    Args:
        sizhu_a: 命盘A的四柱数据
        sizhu_b: 命盘B的四柱数据
        hepan_type: 合盘类型 ('couple' | 'business')
        gender_a: 命盘A性别
        gender_b: 命盘B性别
    
    Returns:
        合盘分析结果
    """
    logger.info(f"开始计算合盘，类型: {hepan_type}")
    
    # 获取天干地支
    gans_a, zhis_a = get_all_gan_zhi(sizhu_a)
    gans_b, zhis_b = get_all_gan_zhi(sizhu_b)
    
    # 1. 地支关系分析
    di_zhi_result = analyze_di_zhi_he_chong(zhis_a, zhis_b)
    
    # 2. 天干合化分析
    tian_gan_result = analyze_tian_gan_he(gans_a, gans_b)
    
    # 3. 五行互补分析
    wuxing_result = analyze_wuxing_match(sizhu_a, sizhu_b)
    
    # 4. 日主关系分析
    rizhu_result = analyze_rizhu_relation(sizhu_a, sizhu_b)
    
    # 5. 夫妻星匹配分析（情侣合婚专用）
    spouse_star_result = None
    if hepan_type == 'couple':
        spouse_star_result = analyze_spouse_star_match(sizhu_a, sizhu_b, gender_a, gender_b)
    
    # 6. 计算评分
    scores = calculate_hepan_score(
        di_zhi_result, tian_gan_result, wuxing_result, rizhu_result, 
        spouse_star_result, hepan_type
    )
    
    # 7. 生成建议
    suggestions = generate_suggestions(
        scores, di_zhi_result, wuxing_result, rizhu_result, 
        spouse_star_result, hepan_type
    )
    
    result = {
        'di_zhi_relation': di_zhi_result,
        'tian_gan_relation': tian_gan_result,
        'wuxing_match': wuxing_result,
        'rizhu_relation': rizhu_result,
        'scores': scores,
        'suggestions': suggestions,
        'hepan_type': hepan_type,
        'gender_a': gender_a,
        'gender_b': gender_b,
    }
    
    # 添加夫妻星分析结果（仅情侣合婚）
    if spouse_star_result:
        result['spouse_star_match'] = spouse_star_result
    
    return result