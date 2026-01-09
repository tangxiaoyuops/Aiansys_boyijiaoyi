"""
从网页抓取《黄帝内经》完整文本
尝试从公开的古籍网站获取
"""
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
import time

project_root = Path(__file__).parent.parent
raw_dir = project_root / "data" / "huangdi_neijing" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def try_download_from_gitee():
    """尝试从Gitee获取"""
    urls = [
        'https://gitee.com/garychowcmu/ChineseText/raw/master/黄帝内经/素问.txt',
        'https://gitee.com/garychowcmu/ChineseText/raw/master/黄帝内经/灵枢.txt',
    ]
    
    results = {}
    for url in urls:
        try:
            print(f"尝试Gitee: {url}")
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200 and len(resp.text) > 1000:
                filename = 'suwen.txt' if '素问' in url else 'lingshu.txt'
                filepath = raw_dir / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(resp.text)
                print(f"[成功] {filename}: {len(resp.text)} 字符")
                results[filename] = True
            else:
                print(f"[失败] 状态码: {resp.status_code}")
        except Exception as e:
            print(f"[失败] {e}")
        time.sleep(1)
    
    return results


def create_extended_content():
    """创建扩展内容（基于现有示例扩展）"""
    print("\n正在扩展现有内容...")
    
    # 读取现有文件
    suwen_sample = raw_dir / "suwen_sample.txt"
    lingshu_sample = raw_dir / "lingshu_sample.txt"
    
    if suwen_sample.exists():
        with open(suwen_sample, 'r', encoding='utf-8') as f:
            suwen_content = f.read()
        
        # 添加更多篇目（基于常见结构）
        additional_suwen = """

## 第十三篇 移精变气论

黄帝问曰：余闻古之治病，惟其移精变气，可祝由而已。今世治病，毒药治其内，针石治其外，或愈或不愈，何也？

岐伯对曰：往古人居禽兽之间，动作以避寒，阴居以避暑，内无眷慕之累，外无伸宦之形，此恬淡之世，邪不能深入也。故毒药不能治其内，针石不能治其外，故可移精祝由而已。

当今之世不然，忧患缘其内，苦形伤其外，又失四时之从，逆寒暑之宜，贼风数至，虚邪朝夕，内至五藏骨髓，外伤空窍肌肤，所以小病必甚，大病必死，故祝由不能已也。

## 第十四篇 汤液醪醴论

黄帝问曰：为五谷汤液及醪醴奈何？

岐伯对曰：必以稻米，炊之稻薪，稻米者完，稻薪者坚。

帝曰：何以然？

岐伯曰：此得天地之和，高下之宜，故能至完，伐取得时，故能至坚也。

帝曰：上古圣人作汤液醪醴，为而不用何也？

岐伯曰：自古圣人之作汤液醪醴者，以为备耳！夫上古作汤液，故为而弗服也。中古之世，道德稍衰，邪气时至，服之万全。

帝曰：今之世不必已何也？

岐伯曰：当今之世，必齐毒药攻其中，镵石针艾治其外也。

## 第十五篇 玉版论要

黄帝问曰：余闻揆度奇恒，所指不同，用之奈何？

岐伯对曰：揆度者，度病之浅深也。奇恒者，言奇病也。请言道之至数，五色脉变，揆度奇恒，道在于一。

神转不回，回则不转，乃失其机。至数之要，迫近以微，著之玉版，命曰合玉机。

容色见上下左右，各在其要。其色见浅者，汤液主治，十日已。其见深者，必齐主治，二十一日已。其见大深者，醪酒主治，百日已。色夭面脱，不治，百日尽已。

脉短气绝死，病温虚甚死。

色见上下左右，各在其要。上为逆，下为从。女子右为逆，左为从；男子左为逆，右为从。易，重阳死，重阴死。

阴阳反他，治在权衡相夺，奇恒事也，揆度事也。

## 第十六篇 诊要经终论

黄帝问曰：诊要何如？

岐伯对曰：正月二月，天气始方，地气始发，人气在肝。三月四月，天气正方，地气定发，人气在脾。五月六月，天气盛，地气高，人气在头。七月八月，阴气始杀，人气在肺。九月十月，阴气始冰，地气始闭，人气在心。十一月十二月，冰复，地气合，人气在肾。

故春刺散俞，及与分理，血出而止，甚者传气，间者环也。夏刺络俞，见血而止，尽气闭环，痛病必下。秋刺皮肤，循理，上下同法，神变而止。冬刺俞窍于分理，甚者直下，间者散下。

春夏秋冬，各有所刺，法其所在。

春刺夏分，脉乱气微，入淫骨髓，病不能愈，令人不嗜食，又且少气。春刺秋分，筋挛，逆气环为咳嗽，病不愈，令人时惊，又且哭。春刺冬分，邪气著藏，令人胀，病不愈，又且欲言语。

夏刺春分，病不愈，令人解堕。夏刺秋分，病不愈，令人心中欲无言，惕惕如人将捕之。夏刺冬分，病不愈，令人少气，时欲怒。

秋刺春分，病不已，令人惕然欲有所为，起而忘之。秋刺夏分，病不已，令人益嗜卧，又且善梦。秋刺冬分，病不已，令人洒洒时寒。

冬刺春分，病不已，令人欲卧不能眠，眠而有见。冬刺夏分，病不愈，气上，发为诸痹。冬刺秋分，病不已，令人善渴。

凡刺胸腹者，必避五藏。中心者环死，中脾者五日死，中肾者七日死，中肺者五日死，中鬲者，皆为伤中，其病虽愈，不过一岁必死。

刺避五藏者，知逆从也。所谓从者，鬲与脾肾之处，不知者反之。

刺胸腹者，必以布憿著之，乃从单布上刺，刺之不愈复刺。

刺针必肃，刺肿摇针，经刺勿摇，此刺之道也。

帝曰：愿闻十二经脉之终奈何？

岐伯曰：太阳之脉，其终也，戴眼反折瘛疭，其色白，绝汗乃出，出则死矣。少阳终者，耳聋，百节皆纵，目睘绝系，绝系一日半死，其死也色先青白，乃死矣。阳明终者，口目动作，善惊妄言，色黄，其上下经盛，不仁，则终矣。少阴终者，面黑齿长而垢，腹胀闭，上下不通而终矣。太阴终者，腹胀闭不得息，善噫善呕，呕则逆，逆则面赤，不逆则上下不通，不通则面黑皮毛焦而终矣。厥阴终者，中热嗌干，善溺心烦，甚则舌卷卵上缩而终矣。此十二经之所败也。

"""
        
        extended_suwen = suwen_content + additional_suwen
        
        suwen_file = raw_dir / "suwen.txt"
        with open(suwen_file, 'w', encoding='utf-8') as f:
            f.write(extended_suwen)
        print(f"[扩展] 素问已扩展: {suwen_file.stat().st_size} bytes")
    
    if lingshu_sample.exists():
        with open(lingshu_sample, 'r', encoding='utf-8') as f:
            lingshu_content = f.read()
        
        additional_lingshu = """

## 第十三篇 经筋

足太阳之筋，起于足小指上，结于踝，邪上结于膝，其下循足外踝，结于踵，上循跟，结于腘；其别者，结于踹外，上腘中内廉，与腘中并上结于臀，上挟脊上项；其支者，别入结于舌本；其直者，结于枕骨，上头下颜，结于鼻；其支者，为目上网，下结于頄；其支者，从腋后外廉，结于肩髃；其支者，入腋下，上出缺盆，上结于完骨；其支者，出缺盆，邪上出于頄。其病小指支，跟肿痛，腘挛，脊反折，项筋急，肩不举，腋支，缺盆中纽痛，不可左右摇。治在燔针劫刺，以知为数，以痛为输，名曰仲春痹也。

足少阳之筋，起于小指次指，上结外踝，上循胫外廉，结于膝外廉；其支者，别起外辅骨，上走髀，前者结于伏兔之上，后者结于尻；其直者，上乘䏚季胁，上走腋前廉，系于膺乳，结于缺盆；直者，上出腋，贯缺盆，出太阳之前，循耳后，上额角，交巅上，下走颔，上结于頄；支者，结于目眦为外维。其病小指次指支转筋，引膝外转筋，膝不可屈伸，腘筋急，前引髀，后引尻，即上乘䏚季胁痛，上引缺盆膺乳颈，维筋急，从左之右，右目不开，上过右角，并蹻脉而行，左络于右，故伤左角，右足不用，命曰维筋相交。治在燔针劫刺，以知为数，以痛为输，名曰孟春痹也。

足阳明之筋，起于中三指，结于跗上，邪外上加于辅骨，上结于膝外廉，直上结于髀枢，上循胁，属脊；其直者，上循骭，结于膝；其支者，结于外辅骨，合少阳；其直者，上循伏兔，上结于髀，聚于阴器，上腹而布，至缺盆而结，上颈，上挟口，合于頄，下结于鼻，上合于太阳，太阳为目上网，阳明为目下网；其支者，从颊结于耳前。其病足中指支，胫转筋，脚跳坚，伏兔转筋，髀前肿，㿉疝，腹筋急，引缺盆及颊，卒口僻，急者目不合，热则筋纵，目不开。颊筋有寒，则急引颊移口；有热则筋弛纵缓，不胜收故僻。治之以马膏，膏其急者，以白酒和桂，以涂其缓者，以桑钩钩之，即以生桑灰置之坎中，高下以坐等，以膏熨急颊，且饮美酒，噉美炙肉，不饮酒者，自强也，为之三拊而已。治在燔针劫刺，以知为数，以痛为输，名曰季春痹也。

## 第十四篇 骨度

黄帝问于伯高曰：脉度言经脉之长短，何以立之？

伯高曰：先度其骨节之大小广狭长短，而脉度定矣。

黄帝曰：愿闻众人之度。人长七尺五寸者，其骨节之大小长短各几何？

伯高曰：头之大骨围二尺六寸，胸围四尺五寸，腰围四尺二寸。发所覆者，颅至项尺二寸。发以下至颐长一尺，君子终折。

结喉以下至缺盆中长四寸。缺盆以下至𩩲𩨗长九寸，过则肺大，不满则肺小。𩩲𩨗以下至天枢长八寸，过则胃大，不及则胃小。天枢以下至横骨长六寸半，过则回肠广长，不满则狭短。横骨长六寸半。横骨上廉以下至内辅之上廉长一尺八寸。内辅之上廉以下至下廉长三寸半。内辅下廉下至内踝长一尺三寸。内踝以下至地长三寸。膝腘以下至附属长一尺六寸。附属以下至地长三寸。故骨围大则太过，小则不及。

角以下至柱骨长一尺。行腋中不见者长四寸。腋以下至季胁长一尺二寸。季胁以下至髀枢长六寸。髀枢以下至膝中长一尺九寸。膝以下至外踝长一尺六寸。外踝以下至京骨长三寸。京骨以下至地长一寸。

耳后当完骨者广九寸。耳前当耳门者广一尺三寸。两颧之间相去七寸。两乳之间广九寸半。两髀之间广六寸半。

足长一尺二寸，广四寸半。肩至肘长一尺七寸；肘至腕长一尺二寸半；腕至中指本节长四寸；本节至其末长四寸半。

项发以下至背骨长二寸半，膂骨以下至尾骶二十一节长三尺，上节长一寸四分分之一，奇分在下，故上七节至于膂骨九寸八分分之七。此众人骨之度也，所以立经脉之长短也。是故视其经脉之在于身也，其见浮而坚，其见明而大者，多血；细而沉者，多气也。

"""
        
        extended_lingshu = lingshu_content + additional_lingshu
        
        lingshu_file = raw_dir / "lingshu.txt"
        with open(lingshu_file, 'w', encoding='utf-8') as f:
            f.write(extended_lingshu)
        print(f"[扩展] 灵枢已扩展: {lingshu_file.stat().st_size} bytes")


def main():
    print("=" * 70)
    print("《黄帝内经》完整文本获取工具")
    print("=" * 70)
    print()
    
    # 尝试从Gitee获取
    print("步骤1: 尝试从Gitee获取...")
    gitee_results = try_download_from_gitee()
    
    # 如果失败，扩展现有内容
    if not gitee_results.get('suwen.txt') or not gitee_results.get('lingshu.txt'):
        print("\n步骤2: 扩展现有内容...")
        create_extended_content()
    
    print()
    print("=" * 70)
    print("完成")
    print("=" * 70)
    
    suwen_file = raw_dir / "suwen.txt"
    lingshu_file = raw_dir / "lingshu.txt"
    
    if suwen_file.exists():
        print(f"素问: {suwen_file.stat().st_size} bytes")
    if lingshu_file.exists():
        print(f"灵枢: {lingshu_file.stat().st_size} bytes")
    
    print("\n提示: 如需更完整的内容，请手动下载完整文本")
    print("参考: data/huangdi_neijing/raw/获取完整文本说明.md")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

