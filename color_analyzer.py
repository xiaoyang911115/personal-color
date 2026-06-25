"""
个人色彩诊断核心分析模块 (Personal Color Analysis)
韩国12型体系：春亮/春净/春柔、夏柔/夏净/夏亮、秋柔/秋净/秋深、冬净/冬深/冬亮
"""

import numpy as np
from PIL import Image, ImageStat
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict
import colorsys
import math

# ─── 标准色卡定义 ───
# 用户拍照时需在屏幕上显示此色卡，放在脸旁一起拍
REFERENCE_COLOR_CARD = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "neutral_gray": (128, 128, 128),
    "warm_beige": (221, 192, 162),
    "cool_pink": (220, 170, 185),
    "warm_yellow": (255, 220, 100),
    "cool_blue": (100, 149, 237),
    "true_red": (220, 50, 50),
    "light_gray": (200, 200, 200),
    "dark_gray": (60, 60, 60),
}

# 12型色彩推荐色卡（每个类型的标志色和推荐色）
COLOR_RECOMMENDATIONS = {
    "spring_light": {
        "name": "🌸 春亮型 (Spring Light)",
        "name_kr": "봄 라이트",
        "description": "温暖而明亮，给人轻盈柔和的感觉。适合带黄调的浅色系。",
        "best_colors": [
            "#F5D5B8", "#F4C2A3", "#FFDAB9", "#FFF0C4", "#E8D5B7",
            "#D4E4BC", "#B5D8CC", "#C9E4DE", "#A8D8B9", "#F7E8C8",
            "#FDDCB5", "#FFE4B5", "#FAEBD7", "#FFEFD5", "#E6E6B3"
        ],
        "worst_colors": [
            "#000000", "#1C1C1C", "#4A0E4E", "#8B0000", "#191970",
            "#000080", "#2F1B41", "#003153", "#800020", "#0C090A"
        ],
        "lipstick": ["珊瑚粉 #FF7F7F", "杏桃色 #FFB07C", "奶茶色 #D2A582"],
        "hair_color": ["浅棕 #A67B5B", "蜂蜜茶 #C49A6C", "亚麻金 #D4B895"],
        "style": "温柔甜美、韩系清新风，适合蕾丝、棉麻材质，浅色系单品",
        "celebrities": ["IU", "秀智", "林允儿"],
        "keywords": ["轻盈", "柔和", "温暖", "甜美", "少女感"],
    },
    "spring_clear": {
        "name": "🌸 春净型 (Spring Clear)",
        "name_kr": "봄 클리어",
        "description": "温暖而鲜明，色彩清澈透亮。适合高饱和的暖色系。",
        "best_colors": [
            "#FF6B6B", "#FF8C42", "#FFD700", "#FF9F43", "#00B894",
            "#FDCB6E", "#FFB142", "#FF5252", "#E17055", "#FAB1A0",
            "#55E6C1", "#2ED573", "#7BED9F", "#00D2D3", "#1E90FF"
        ],
        "worst_colors": [
            "#808080", "#A9A9A9", "#696969", "#BDB76B", "#8B7355",
            "#6B4226", "#5C4033", "#556B2F", "#4A4A4A", "#2F2F2F"
        ],
        "lipstick": ["正红 #E74C3C", "亮橘 #FF6B35", "珊瑚橘 #FF6F61"],
        "hair_color": ["亮棕 #B8860B", "红棕 #A0522D", "黑茶 #3E2723"],
        "style": "活力鲜明、色彩碰撞，适合对比色搭配，运动休闲混搭",
        "celebrities": ["Lisa", "宣美", "李孝利"],
        "keywords": ["鲜明", "活力", "对比", "高饱和", "青春"],
    },
    "spring_soft": {
        "name": "🌸 春柔型 (Spring Soft)",
        "name_kr": "봄 소프트",
        "description": "温暖而柔和，介于春与秋之间。适合带灰调的暖色系。",
        "best_colors": [
            "#E8C9A0", "#DDB8A0", "#C9A98C", "#D4C5B9", "#C4B7A6",
            "#BFA98A", "#D2B48C", "#C4AE8D", "#DEB887", "#CDAA7D",
            "#A3C1AD", "#B0C4B1", "#A8C3A6", "#C5D5CB", "#9BB5A4"
        ],
        "worst_colors": [
            "#000000", "#FF1493", "#00FF00", "#FF0000", "#0000FF",
            "#FF00FF", "#00FFFF", "#8A2BE2", "#FFD700", "#DC143C"
        ],
        "lipstick": ["豆沙色 #C0604F", "干枯玫瑰 #B76E79", "裸粉 #D4A5A5"],
        "hair_color": ["灰棕 #8B7D6B", "奶茶棕 #C4A882", "冷棕 #9B8A7A"],
        "style": "温柔知性、莫兰迪色系，适合针织、丝绒材质，同色系叠穿",
        "celebrities": ["孔晓振", "郑裕美", "金高银"],
        "keywords": ["柔和", "灰调", "知性", "自然", "高级感"],
    },
    "summer_soft": {
        "name": "☀️ 夏柔型 (Summer Soft)",
        "name_kr": "여름 소프트",
        "description": "冷调而柔和，颜色带有灰雾感。适合低饱和冷色系。",
        "best_colors": [
            "#B8C9E8", "#C5D5E8", "#D5C4E0", "#E0D0E8", "#D4C5D9",
            "#C8B8D0", "#B4C4D8", "#A8B8C8", "#D0D8E8", "#C0C8D8",
            "#D8C8D8", "#E8D8E8", "#C4C8D4", "#B0B8C8", "#D0D0E0"
        ],
        "worst_colors": [
            "#FF6600", "#FFA500", "#FFD700", "#FF4500", "#CC5500",
            "#8B4500", "#D2691E", "#FF8C00", "#FF7F50", "#F4A460"
        ],
        "lipstick": ["玫瑰粉 #E8A0B4", "莓果色 #C08090", "藕粉 #D4B8C0"],
        "hair_color": ["灰紫 #8B7D8B", "冷棕 #A09080", "黑茶 #3E3232"],
        "style": "优雅温婉、低饱和同色系，适合雪纺、丝绸材质，法式简约风",
        "celebrities": ["孙艺珍", "金泰梨", "韩志旼"],
        "keywords": ["优雅", "灰雾感", "低饱和", "温婉", "法式"],
    },
    "summer_clear": {
        "name": "☀️ 夏净型 (Summer Clear)",
        "name_kr": "여름 클리어",
        "description": "冷调而鲜明，色彩清爽通透。适合中等饱和的冷色系。",
        "best_colors": [
            "#6C5CE7", "#A29BFE", "#74B9FF", "#0984E3", "#00CEC9",
            "#81ECEC", "#55EFC4", "#00B894", "#DFE6E9", "#74B9FF",
            "#6C5CE7", "#A29BFE", "#FDCB6E", "#E17055", "#636E72"
        ],
        "worst_colors": [
            "#8B4513", "#A0522D", "#CD853F", "#D2691E", "#8B7355",
            "#6B4226", "#556B2F", "#808000", "#9B870C", "#B8860B"
        ],
        "lipstick": ["玫红 #E91E63", "葡萄紫 #9C27B0", "桃粉 #FF80AB"],
        "hair_color": ["冷黑 #1A1A2E", "灰蓝 #6C7A8D", "灰紫 #8E7B8E"],
        "style": "清爽利落、蓝粉撞色，适合牛仔、西装面料，都市简约风",
        "celebrities": ["郑秀晶", "裴秀智（冷调时）", "李圣经"],
        "keywords": ["清爽", "通透", "都市", "简约", "干练"],
    },
    "summer_light": {
        "name": "☀️ 夏亮型 (Summer Light)",
        "name_kr": "여름 라이트",
        "description": "冷调而明亮，颜色柔和轻盈。适合浅冷色调。",
        "best_colors": [
            "#E8F0F8", "#D8E8F0", "#F0E8F8", "#E8E0F0", "#F8E8F0",
            "#E0F0F0", "#F0F0F8", "#D8E0F0", "#E8F0E8", "#F8F0E8",
            "#E0E8F0", "#F0E8E8", "#D8D8F0", "#E8E8F8", "#F0F0F8"
        ],
        "worst_colors": [
            "#8B4513", "#A0522D", "#CD853F", "#D2691E", "#8B0000",
            "#800000", "#A52A2A", "#B22222", "#8B7355", "#6B4226"
        ],
        "lipstick": ["樱花粉 #FFB7C5", "浅粉 #FFD1DC", "裸粉 #E8C8C8"],
        "hair_color": ["灰金 #C8C0B0", "浅冷棕 #B8A898", "银灰 #C0C0C0"],
        "style": "仙女梦幻、浅色系公主风，适合纱裙、蕾丝，轻复古少女风",
        "celebrities": ["金裕贞", "金所泫", "文佳煐"],
        "keywords": ["轻盈", "梦幻", "少女", "仙女", "浅色"],
    },
    "autumn_soft": {
        "name": "🍂 秋柔型 (Autumn Soft)",
        "name_kr": "가을 소프트",
        "description": "暖调而柔和，颜色温润。适合低饱和暖色系。",
        "best_colors": [
            "#C4A882", "#B8956A", "#D2B48C", "#C9A96E", "#BFA98A",
            "#A0906E", "#B8A080", "#C4AE8D", "#D4C4A8", "#C8B898",
            "#A89878", "#B8A888", "#C8B080", "#D0B898", "#B8A070"
        ],
        "worst_colors": [
            "#FF00FF", "#00FF00", "#0000FF", "#00FFFF", "#FF1493",
            "#FF0000", "#FFD700", "#00BFFF", "#FF4500", "#8A2BE2"
        ],
        "lipstick": ["砖红 #A0522D", "脏橘 #C07030", "枫叶红 #C04030"],
        "hair_color": ["深棕 #5C4033", "焦糖 #A67B5B", "巧克力 #3E2723"],
        "style": "复古文艺、大地色系，适合灯芯绒、皮革，英伦复古风",
        "celebrities": ["金泰梨", "金多美", "申惠善"],
        "keywords": ["复古", "温润", "大地色", "文艺", "质感"],
    },
    "autumn_clear": {
        "name": "🍂 秋净型 (Autumn Clear)",
        "name_kr": "가을 클리어",
        "description": "暖调而鲜明，色彩饱和浓郁。适合高饱和暖色系。",
        "best_colors": [
            "#D2691E", "#CD853F", "#B8860B", "#DAA520", "#B87333",
            "#CC5500", "#C35817", "#E2725B", "#8B4513", "#A0522D",
            "#C41E3A", "#9B111E", "#DC143C", "#FF4500", "#CC3333"
        ],
        "worst_colors": [
            "#E0FFFF", "#F0F8FF", "#F5FFFA", "#F0FFF0", "#FFF5EE",
            "#F8F8FF", "#FFFAFA", "#FDF5E6", "#FFFAF0", "#FFFFF0"
        ],
        "lipstick": ["铁锈红 #8B3A3A", "番茄红 #FF4D4D", "酒红 #722F37"],
        "hair_color": ["深红棕 #8B4513", "黑茶 #2C1810", "焦糖棕 #A0522D"],
        "style": "华丽浓烈、撞色搭配，适合丝绒、缎面，复古华丽风",
        "celebrities": ["Jennie", "Jisoo", "韩素希"],
        "keywords": ["浓郁", "华丽", "高饱和", "复古", "气场"],
    },
    "autumn_deep": {
        "name": "🍂 秋深型 (Autumn Deep)",
        "name_kr": "가을 딥",
        "description": "暖调而深沉，颜色浓郁厚重。适合深暖色系。",
        "best_colors": [
            "#4A3728", "#3E2723", "#5C4033", "#4E342E", "#3E2723",
            "#5D4037", "#4E342E", "#6D4C41", "#3E2723", "#4A3728",
            "#2C1810", "#3B1F0B", "#4A2C17", "#5C3A21", "#6B4226"
        ],
        "worst_colors": [
            "#FFB6C1", "#FFC0CB", "#FFE4E1", "#FFF0F5", "#FFD1DC",
            "#F0F8FF", "#E0FFFF", "#F5FFFA", "#FFE4E1", "#FFEFD5"
        ],
        "lipstick": ["深酒红 #4A0E17", "巧克力 #3E2723", "深豆沙 #8B5A5A"],
        "hair_color": ["黑棕 #1C0E07", "深摩卡 #3E2723", "黑茶 #1A0A00"],
        "style": "成熟稳重、深色系质感，适合羊毛、皮草，高级低调风",
        "celebrities": ["全智贤", "金惠秀", "李英爱"],
        "keywords": ["深沉", "稳重", "质感", "成熟", "低调奢华"],
    },
    "winter_clear": {
        "name": "❄️ 冬净型 (Winter Clear)",
        "name_kr": "겨울 클리어",
        "description": "冷调而鲜明，高对比度。适合纯正冷色和强对比搭配。",
        "best_colors": [
            "#000000", "#FFFFFF", "#FF0000", "#0000FF", "#FF00FF",
            "#00FF00", "#FFFF00", "#00FFFF", "#8A2BE2", "#DC143C",
            "#FF1493", "#00BFFF", "#FFD700", "#FF4500", "#32CD32"
        ],
        "worst_colors": [
            "#D2B48C", "#C4A882", "#DEB887", "#CDAA7D", "#BFA98A",
            "#C9A96E", "#B8956A", "#A0906E", "#D4C4A8", "#C8B898"
        ],
        "lipstick": ["正红 #CC0000", "玫红 #FF0066", "紫红 #800080"],
        "hair_color": ["纯黑 #0A0A0A", "蓝黑 #0A0A1A", "冷黑 #111122"],
        "style": "强烈对比、黑白配，适合皮革、亮片，前卫摩登风",
        "celebrities": ["Karina", "Winter", "华莎"],
        "keywords": ["高对比", "鲜明", "冷艳", "前卫", "气场女王"],
    },
    "winter_deep": {
        "name": "❄️ 冬深型 (Winter Deep)",
        "name_kr": "겨울 딥",
        "description": "冷调而深沉，颜色深邃浓郁。适合深冷色系。",
        "best_colors": [
            "#0C090A", "#1C1C1C", "#2C2C3E", "#1A1A2E", "#16213E",
            "#0F3460", "#1A1A40", "#2C1810", "#3B1F0B", "#1B0F30",
            "#0C0032", "#190033", "#000033", "#001A33", "#003333"
        ],
        "worst_colors": [
            "#FFDAB9", "#FFE4B5", "#FFEFD5", "#FAEBD7", "#F5DEB3",
            "#FFF8DC", "#FFE4C4", "#FFEBCD", "#F5DEB3", "#FAF0E6"
        ],
        "lipstick": ["深酒红 #4A0010", "黑莓 #2C0014", "暗紫 #3A0030"],
        "hair_color": ["纯黑 #050505", "深蓝黑 #050515", "冷黑 #0A0A15"],
        "style": "暗黑高级、深邃神秘，适合皮质、毛呢，暗黑系高级感",
        "celebrities": ["Nana", "郑秀晶（深调）", "徐贤"],
        "keywords": ["深邃", "神秘", "暗黑", "高级", "冷艳"],
    },
    "winter_light": {
        "name": "❄️ 冬亮型 (Winter Light)",
        "name_kr": "겨울 라이트",
        "description": "冷调而明亮，高对比但色彩偏浅。适合冷调浅色+深色对比。",
        "best_colors": [
            "#FFFFFF", "#F8F8FF", "#F0F8FF", "#E8E8F8", "#F0F0F8",
            "#E0E8F8", "#D8E0F0", "#F8F0F8", "#E8F0F8", "#F0E8F8",
            "#E0F0F8", "#D8E8F8", "#E8E0F0", "#F8E8F0", "#F0F0F8"
        ],
        "worst_colors": [
            "#8B4513", "#A0522D", "#D2691E", "#B8860B", "#CD853F",
            "#8B7355", "#6B4226", "#556B2F", "#808000", "#9B870C"
        ],
        "lipstick": ["冷粉 #FF80AB", "莓粉 #E06090", "浅紫粉 #D8A0C0"],
        "hair_color": ["浅金灰 #D0C8C0", "银灰 #C8C8C8", "冷亚麻 #C0B8B0"],
        "style": "清冷仙气、黑白灰极简，适合西装、衬衫，高级性冷淡风",
        "celebrities": ["裴珠泫", "金智媛", "韩素希（冷调时）"],
        "keywords": ["清冷", "仙气", "极简", "高级", "冷白皮"],
    },
}


@dataclass
class SkinAnalysis:
    """肤色分析结果"""
    h: float  # 色相 0-360
    s: float  # 饱和度 0-100
    v: float  # 明度 0-100
    r: int
    g: int
    b: int
    lab_l: float = 0
    lab_a: float = 0
    lab_b: float = 0


@dataclass
class PersonalColorResult:
    """个人色彩诊断完整结果"""
    season_type: str  # 12型 key
    warm_cool: str  # "warm" / "cool" / "neutral"
    saturation_level: str  # "soft" / "medium" / "clear"
    brightness_level: str  # "light" / "medium" / "deep"
    confidence: float  # 置信度 0-1
    skin_analysis: SkinAnalysis
    questionnaire_scores: Dict[str, float]
    final_score: Dict[str, float]
    recommendations: Dict


def rgb_to_hsv(r, g, b):
    """RGB 转 HSV"""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360, s * 100, v * 100


def rgb_to_lab(r, g, b):
    """简化 RGB → CIE Lab（近似转换）"""
    # 先转 XYZ
    r, g, b = r / 255.0, g / 255.0, b / 255.0

    def linearize(c):
        if c > 0.04045:
            return ((c + 0.055) / 1.055) ** 2.4
        return c / 12.92

    r, g, b = linearize(r), linearize(g), linearize(b)
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505

    # XYZ → Lab (D65)
    xn, yn, zn = 0.95047, 1.0, 1.08883

    def f(t):
        delta = 6 / 29
        if t > delta ** 3:
            return t ** (1 / 3)
        return t / (3 * delta ** 2) + 4 / 29

    l = 116 * f(y / yn) - 16
    a = 500 * (f(x / xn) - f(y / yn))
    b_val = 200 * (f(y / yn) - f(z / zn))
    return l, a, b_val


def extract_skin_color(image: Image.Image, face_region: Optional[Tuple[int, int, int, int]] = None) -> SkinAnalysis:
    """
    从图片中提取肤色

    Args:
        image: PIL Image 对象
        face_region: (x, y, w, h) 面部区域，None 则使用图片中心区域

    Returns:
        SkinAnalysis 对象
    """
    img = image.convert("RGB")
    w, h = img.size

    if face_region:
        x, y, fw, fh = face_region
        crop = img.crop((x, y, x + fw, y + fh))
    else:
        # 默认取图片中心 40% 区域作为面部区域
        margin_w, margin_h = int(w * 0.3), int(h * 0.3)
        crop = img.crop((margin_w, margin_h, w - margin_w, h - margin_h))

    # 转为 numpy 数组
    pixels = np.array(crop)

    # 过滤掉过亮和过暗的像素（排除高光和阴影）
    brightness = np.mean(pixels, axis=2)
    mask = (brightness > 40) & (brightness < 240)

    if np.sum(mask) < 100:
        # 如果过滤后像素太少，用全部像素
        filtered = pixels.reshape(-1, 3)
    else:
        filtered = pixels[mask]

    # 计算中位数（比均值更能抵抗极端值）
    median_r = int(np.median(filtered[:, 0]))
    median_g = int(np.median(filtered[:, 1]))
    median_b = int(np.median(filtered[:, 2]))

    h, s, v = rgb_to_hsv(median_r, median_g, median_b)
    l_val, a_val, b_val = rgb_to_lab(median_r, median_g, median_b)

    return SkinAnalysis(
        h=round(h, 1),
        s=round(s, 1),
        v=round(v, 1),
        r=median_r,
        g=median_g,
        b=median_b,
        lab_l=round(l_val, 1),
        lab_a=round(a_val, 1),
        lab_b=round(b_val, 1),
    )


def detect_color_card_correction(image: Image.Image) -> Optional[Dict[str, Tuple[float, float, float]]]:
    """
    检测色卡并计算颜色校正向量。
    返回每个色块的偏差向量 {(r_diff, g_diff, b_diff), ...}，失败返回 None
    """
    # 简化版：在图片四角和中心区域采样，与标准色卡比对
    # 实际应用中需要用户标记色卡位置，这里做简化处理
    # 返回 None 表示未检测到色卡，使用无校正分析
    return None


def analyze_warm_cool(skin: SkinAnalysis) -> Tuple[str, float]:
    """
    基于肤色 HSV 分析冷暖调

    Returns:
        (warm/cool/neutral, confidence)
    """
    h = skin.h
    a_val = skin.lab_a  # 正值偏红(暖)，负值偏绿(冷)
    b_val = skin.lab_b  # 正值偏黄(暖)，负值偏蓝(冷)

    # 色相判断
    h_score = 0
    if h < 25 or h > 335:
        h_score = 1.0  # 强烈暖调
    elif 25 <= h < 45:
        h_score = 0.6  # 偏暖
    elif 45 <= h < 60:
        h_score = 0.2  # 微暖
    elif 180 <= h < 280:
        h_score = -0.7  # 冷调
    elif 280 <= h <= 335:
        h_score = -0.4  # 偏冷
    else:
        h_score = 0  # 中性

    # Lab a* 判断（红/绿轴）
    lab_score = 0
    if a_val > 5:
        lab_score = 0.5
    elif a_val < -3:
        lab_score = -0.5

    # Lab b* 判断（黄/蓝轴）
    lab_b_score = 0
    if b_val > 8:
        lab_b_score = 0.5
    elif b_val < -5:
        lab_b_score = -0.5

    total = h_score * 0.5 + lab_score * 0.25 + lab_b_score * 0.25
    confidence = min(abs(total) * 1.5, 1.0)

    if total > 0.2:
        return "warm", confidence
    elif total < -0.2:
        return "cool", confidence
    return "neutral", 0.3


def analyze_saturation(skin: SkinAnalysis) -> Tuple[str, float]:
    """分析饱和度水平 → soft/medium/clear"""
    s = skin.s
    if s < 12:
        return "soft", 0.9
    elif s < 22:
        return "soft", 0.6
    elif s < 35:
        return "medium", 0.6
    elif s < 50:
        return "clear", 0.6
    else:
        return "clear", 0.9


def analyze_brightness(skin: SkinAnalysis) -> Tuple[str, float]:
    """分析明度水平 → light/medium/deep"""
    v = skin.v
    if v > 75:
        return "light", 0.9
    elif v > 60:
        return "light", 0.55
    elif v > 40:
        return "medium", 0.6
    elif v > 25:
        return "deep", 0.55
    else:
        return "deep", 0.9


def questionnaire_to_scores(answers: Dict[str, str]) -> Dict[str, float]:
    """
    将问卷答案转为分数

    问卷问题：
    - q1_vein: 手腕血管颜色 → blue_purple / green / both
    - q2_jewelry: 更适合的首饰 → silver / gold / both
    - q3_sun: 晒太阳后 → red_first / tan_direct / both
    - q4_lipstick: 更适合的口红 → pink_berry / coral_orange / both
    - q5_white: 白纸对比 → pinkish / yellowish / neither
    - q6_foundation: 粉底液色调 → cool / warm / neutral
    - q7_eyes_hair: 瞳孔和发色 → dark_clear / soft_brown / light
    - q8_style: 喜欢的穿搭风格 → vivid / soft / dark / light
    """
    scores = {
        "warm_score": 0.0,
        "cool_score": 0.0,
        "soft_score": 0.0,
        "clear_score": 0.0,
        "light_score": 0.0,
        "deep_score": 0.0,
    }

    weights = {
        "q1_vein": 1.5, "q2_jewelry": 1.5, "q3_sun": 1.0,
        "q4_lipstick": 1.2, "q5_white": 1.0, "q6_foundation": 1.5,
        "q7_eyes_hair": 0.8, "q8_style": 0.5,
    }

    # 冷暖判断
    for q, warm_ans, cool_ans, weight in [
        ("q1_vein", "green", "blue_purple", 1.5),
        ("q2_jewelry", "gold", "silver", 1.5),
        ("q3_sun", "tan_direct", "red_first", 1.0),
        ("q4_lipstick", "coral_orange", "pink_berry", 1.2),
        ("q5_white", "yellowish", "pinkish", 1.0),
        ("q6_foundation", "warm", "cool", 1.5),
    ]:
        ans = answers.get(q, "")
        if ans == warm_ans:
            scores["warm_score"] += weight
        elif ans == cool_ans:
            scores["cool_score"] += weight
        elif ans == "both":
            scores["warm_score"] += weight * 0.4
            scores["cool_score"] += weight * 0.4

    # 饱和度判断（净/柔）
    for q, clear_ans, soft_ans, weight in [
        ("q7_eyes_hair", "dark_clear", "soft_brown", 0.8),
        ("q8_style", "vivid", "soft", 0.5),
    ]:
        ans = answers.get(q, "")
        if ans == clear_ans:
            scores["clear_score"] += weight
        elif ans == soft_ans:
            scores["soft_score"] += weight

    # 明度判断（亮/深）
    for q, light_ans, deep_ans, weight in [
        ("q7_eyes_hair", "light", "dark_clear", 0.8),
        ("q8_style", "light", "dark", 0.5),
    ]:
        ans = answers.get(q, "")
        if ans == light_ans:
            scores["light_score"] += weight
        elif ans == deep_ans:
            scores["deep_score"] += weight

    return scores


def determine_season_type(
    skin: SkinAnalysis,
    questionnaire_answers: Dict[str, str],
    skin_weight: float = 0.4,
    question_weight: float = 0.5,
    vein_weight: float = 0.1,
) -> PersonalColorResult:
    """
    综合判断 12 型季节类型

    Args:
        skin: 肤色分析结果
        questionnaire_answers: 问卷答案字典
        skin_weight: 肤色分析权重
        question_weight: 问卷权重
        vein_weight: 血管检测权重

    Returns:
        PersonalColorResult
    """
    # 肤色分析
    warm_cool, wc_conf = analyze_warm_cool(skin)
    saturation, sat_conf = analyze_saturation(skin)
    brightness, bri_conf = analyze_brightness(skin)

    # 问卷分析
    q_scores = questionnaire_to_scores(questionnaire_answers)

    # 血管检测（简化：来自问卷 q1）
    vein = questionnaire_answers.get("q1_vein", "")
    vein_warm = 0.0
    vein_cool = 0.0
    if vein == "green":
        vein_warm = 1.0
    elif vein == "blue_purple":
        vein_cool = 1.0
    elif vein == "both":
        vein_warm = 0.5
        vein_cool = 0.5

    # 综合分数
    total_warm = (1.0 if warm_cool == "warm" else (0.5 if warm_cool == "neutral" else 0.0))
    total_cool = (1.0 if warm_cool == "cool" else (0.5 if warm_cool == "neutral" else 0.0))

    # 加权合并
    skin_warm = total_warm * wc_conf
    skin_cool = total_cool * wc_conf

    q_max = max(q_scores["warm_score"], q_scores["cool_score"], 1)
    q_warm_norm = q_scores["warm_score"] / q_max if q_max > 0 else 0.5
    q_cool_norm = q_scores["cool_score"] / q_max if q_max > 0 else 0.5

    combined_warm = skin_warm * skin_weight + q_warm_norm * question_weight + vein_warm * vein_weight
    combined_cool = skin_cool * skin_weight + q_cool_norm * question_weight + vein_cool * vein_weight

    is_warm = combined_warm >= combined_cool

    # 综合饱和度和明度
    combined_soft = (1.0 if saturation == "soft" else 0) * sat_conf * skin_weight + \
                     (q_scores["soft_score"] / max(q_scores["soft_score"] + q_scores["clear_score"], 1)) * question_weight
    combined_clear = (1.0 if saturation == "clear" else 0) * sat_conf * skin_weight + \
                      (q_scores["clear_score"] / max(q_scores["soft_score"] + q_scores["clear_score"], 1)) * question_weight

    combined_light = (1.0 if brightness == "light" else 0) * bri_conf * skin_weight + \
                      (q_scores["light_score"] / max(q_scores["light_score"] + q_scores["deep_score"], 1)) * question_weight
    combined_deep = (1.0 if brightness == "deep" else 0) * bri_conf * skin_weight + \
                     (q_scores["deep_score"] / max(q_scores["light_score"] + q_scores["deep_score"], 1)) * question_weight

    # 确定亚型
    is_soft = combined_soft > combined_clear
    is_light = combined_light > combined_deep
    is_clear = combined_clear > combined_soft
    is_deep = combined_deep > combined_light

    # 映射到 12 型
    if is_warm:
        if is_light:
            season = "spring_light"
        elif is_clear:
            season = "spring_clear"
        else:
            season = "spring_soft"
    else:
        if is_soft:
            if is_light:
                season = "summer_light"
            elif is_clear:
                season = "summer_clear"
            else:
                season = "summer_soft"
        elif is_deep:
            season = "winter_deep" if not is_warm else "autumn_deep"
        elif is_clear:
            season = "winter_clear" if not is_warm else "autumn_clear"
        elif is_light:
            season = "winter_light"
        else:
            season = "summer_soft" if not is_warm else "autumn_soft"

    # 如果是暖调，修正秋/冬歧义
    if is_warm:
        if is_deep:
            season = "autumn_deep"
        elif is_clear:
            season = "autumn_clear"
        elif is_soft and not is_light:
            season = "autumn_soft"

    # 置信度计算
    confidence = (wc_conf * skin_weight + 0.7 * question_weight + 0.5 * vein_weight)

    rec = COLOR_RECOMMENDATIONS.get(season, COLOR_RECOMMENDATIONS["spring_light"])

    return PersonalColorResult(
        season_type=season,
        warm_cool="warm" if is_warm else "cool",
        saturation_level="soft" if is_soft else ("clear" if is_clear else "medium"),
        brightness_level="light" if is_light else ("deep" if is_deep else "medium"),
        confidence=round(confidence, 2),
        skin_analysis=skin,
        questionnaire_scores=q_scores,
        final_score={
            "warm": round(combined_warm, 3),
            "cool": round(combined_cool, 3),
            "soft": round(combined_soft, 3),
            "clear": round(combined_clear, 3),
            "light": round(combined_light, 3),
            "deep": round(combined_deep, 3),
        },
        recommendations=rec,
    )


def analyze_image(image_path: str, questionnaire_answers: Dict[str, str],
                  face_region: Optional[Tuple[int, int, int, int]] = None) -> PersonalColorResult:
    """
    分析一张照片并返回完整诊断结果

    Args:
        image_path: 图片路径
        questionnaire_answers: 问卷答案
        face_region: 可选的面部区域 (x, y, w, h)

    Returns:
        PersonalColorResult
    """
    img = Image.open(image_path)
    skin = extract_skin_color(img, face_region)
    return determine_season_type(skin, questionnaire_answers)
