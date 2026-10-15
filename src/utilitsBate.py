import logging
from functools import lru_cache

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

log = logging.getLogger(__name__)

URL = "http://www.coolpc.com.tw/evaluate.php"
CN_DIGITS = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
             "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def to_int(text: str):
    """'3' / '三' / '十二' -> int，無法轉換回傳 None"""
    if text.isdigit():
        return int(text)
    if text in CN_DIGITS:
        return CN_DIGITS[text]
    if text.startswith("十") and text[1:] in CN_DIGITS:   # 十一~十九
        return 10 + CN_DIGITS[text[1:]]
    return None


def _session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=(500, 502, 503, 504))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    s.headers["User-Agent"] = "Mozilla/5.0 (price-crawler)"
    return s


@lru_cache(maxsize=2)
def get_index_soup(fix_optgroup: bool = False) -> BeautifulSoup:
    resp = _session().get(URL, timeout=15)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding      # 請實測確認編碼是否正確
    html = resp.text
    if fix_optgroup:
        html = html.replace("<OPTGROUP", "</OPTGROUP><OPTGROUP")
    return BeautifulSoup(html, "html.parser")