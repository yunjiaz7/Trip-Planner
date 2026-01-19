"""
City Name Translator

Translates English city names to Chinese for Amap API compatibility.
Amap API requires Chinese city names for accurate results, especially for weather queries.
"""

# Common city name translations: English -> Chinese
CITY_NAME_MAP = {
    # Major cities
    "beijing": "北京",
    "shanghai": "上海",
    "guangzhou": "广州",
    "shenzhen": "深圳",
    "hangzhou": "杭州",
    "chengdu": "成都",
    "wuhan": "武汉",
    "xian": "西安",
    "nanjing": "南京",
    "tianjin": "天津",
    "chongqing": "重庆",
    "suzhou": "苏州",
    "dalian": "大连",
    "qingdao": "青岛",
    "xiamen": "厦门",
    "kunming": "昆明",
    "changsha": "长沙",
    "foshan": "佛山",
    "dongguan": "东莞",
    "zhengzhou": "郑州",
    "jinan": "济南",
    "hefei": "合肥",
    "nanchang": "南昌",
    "fuzhou": "福州",
    "shijiazhuang": "石家庄",
    "taiyuan": "太原",
    "haerbin": "哈尔滨",
    "changchun": "长春",
    "shenyang": "沈阳",
    "hohhot": "呼和浩特",
    "urumqi": "乌鲁木齐",
    "lanzhou": "兰州",
    "yinchuan": "银川",
    "xining": "西宁",
    "lhasa": "拉萨",
    "nanning": "南宁",
    "guiyang": "贵阳",
    "haikou": "海口",
    "sanya": "三亚",
    
    # Alternative spellings and common variations
    "peking": "北京",  # Old spelling
    "hong kong": "香港",
    "hongkong": "香港",
    "macau": "澳门",
    "macao": "澳门",
    "taipei": "台北",
    "kaohsiung": "高雄",
}


def translate_city_name(city_name: str) -> str:
    """
    Translate English city name to Chinese for Amap API compatibility.
    
    Args:
        city_name: City name in English or Chinese
        
    Returns:
        Chinese city name. If translation not found, returns original name.
        
    Examples:
        >>> translate_city_name("Beijing")
        '北京'
        >>> translate_city_name("上海")
        '上海'  # Already Chinese, returns as-is
        >>> translate_city_name("UnknownCity")
        'UnknownCity'  # Not found, returns original
    """
    if not city_name:
        return city_name
    
    # Normalize: lowercase and strip whitespace
    normalized = city_name.strip().lower()
    
    # If already Chinese (contains Chinese characters), return as-is
    if any('\u4e00' <= char <= '\u9fff' for char in city_name):
        return city_name
    
    # Look up in translation map
    translated = CITY_NAME_MAP.get(normalized)
    
    if translated:
        return translated
    
    # Try partial match (for cases like "Beijing City" -> "Beijing")
    for en_name, cn_name in CITY_NAME_MAP.items():
        if normalized.startswith(en_name) or en_name in normalized:
            return cn_name
    
    # If not found, return original (may still work for some APIs)
    # But log a warning for debugging
    print(f"⚠️  City name translation not found for: {city_name}, using original name")
    return city_name


def translate_city_name_safe(city_name: str, default: str = None) -> str:
    """
    Safe version of translate_city_name that returns a default if translation fails.
    
    Args:
        city_name: City name in English or Chinese
        default: Default city name to return if translation not found
        
    Returns:
        Chinese city name or default
    """
    translated = translate_city_name(city_name)
    
    # If translation didn't change and default is provided, use default
    if translated.lower() == city_name.lower() and default:
        return default
    
    return translated


def is_chinese_city_name(city_name: str) -> bool:
    """
    Check if city name is already in Chinese.
    
    Args:
        city_name: City name to check
        
    Returns:
        True if contains Chinese characters, False otherwise
    """
    if not city_name:
        return False
    return any('\u4e00' <= char <= '\u9fff' for char in city_name)


# For backward compatibility and convenience
def get_chinese_city_name(city_name: str) -> str:
    """
    Alias for translate_city_name for backward compatibility.
    
    Args:
        city_name: City name in English or Chinese
        
    Returns:
        Chinese city name
    """
    return translate_city_name(city_name)
