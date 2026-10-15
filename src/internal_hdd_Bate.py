import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from utilitsBate import get_index_soup, to_int

log = logging.getLogger(__name__)

NUM = r"[0-9一二三四五六七八九十]+"
RE_SIZE     = re.compile(r"(\d+(?:\.\d+)?)\s*(TB|T|GB|G)\b", re.I)
RE_SERIES   = re.compile(r"【([^】]+)】")
RE_CACHE    = re.compile(r"(\d+)\s*MB?\b", re.I)
RE_MODEL    = re.compile(r"[｛{(（]\s*([A-Za-z0-9][A-Za-z0-9\-_/]*)\s*[｝})）]")
RE_RPM      = re.compile(r"(\d+)\s*轉")
RE_WARRANTY = re.compile(rf"/\s*({NUM})\s*年") # 第一個 /N年
RE_EXTRA    = re.compile(rf"保\s*({NUM})\s*年") # 保N年 如 Rescue 資料救援
RE_PRICE    = re.compile(r"\$\s*([\d,]+)")
IGNORE_TAGS = {"限搭機", "限搭"}


@dataclass
class InternalHddOption:
    title: str
    subtitle: str
    describe: str

    def __post_init__(self):
        d = self.describe
        self.brand = d.split()[0] if d.split() else None
        self.size = self._size(d) # TB
        self.series = self._series(d)
        self.memory = self._int(RE_CACHE, d) # MB
        self.model = (m.group(1) if (m := RE_MODEL.search(d)) else None)
        self.rpm = self._int(RE_RPM, d)
        self.warranty = self._num(RE_WARRANTY, d)
        self.extra_service = self._num(RE_EXTRA, d) # Rescue 年數
        self.price = self._price(d)
        self.cp_value = (round(self.price / self.size, 2)
                         if self.price and self.size else None) # 元 / TB

    @staticmethod
    def _int(rx, text) -> Optional[int]:
        m = rx.search(text)
        return int(m.group(1)) if m else None

    @staticmethod
    def _num(rx, text) -> Optional[int]:
        m = rx.search(text)
        return to_int(m.group(1)) if m else None

    @staticmethod
    def _size(text) -> Optional[float]:
        m = RE_SIZE.search(text)
        if not m:
            return None
        value, unit = float(m.group(1)), m.group(2).upper()
        return value if unit.startswith("T") else value / 1000

    @staticmethod
    def _series(text) -> Optional[str]:
        for tag in RE_SERIES.findall(text):
            if tag not in IGNORE_TAGS:
                return tag
        return None

    @staticmethod
    def _price(text) -> Optional[int]:
        prices = RE_PRICE.findall(text)
        return int(prices[-1].replace(",", "")) if prices else None   # 取最後一個 實際價格


class InternalHdd:
    def __init__(self, title="傳統內接硬碟HDD"):
        self.title = title
        self.tag = self._get_tag()
        self.options = self._get_options()

    def _get_tag(self):
        soup = get_index_soup(fix_optgroup=True)
        for td in soup.find_all("td", class_="t"):
            if self.title in td.get_text():
                return td.parent
        raise ValueError(f"找不到包含 '{self.title}' 的 <td class='t'>")

    def _get_options(self):
        options = []
        for group in self.tag.find_all("optgroup"):
            subtitle = group.get("label", "")
            for opt in group.find_all("option"):
                if opt.has_attr("disabled"):
                    continue
                try:
                    options.append(InternalHddOption(self.title, subtitle, opt.get_text()))
                except Exception:
                    log.exception("解析失敗，已略過: %s", opt.get_text())
        return options


def save_to_html(options: list):
    base = Path(__file__).resolve().parent.parent
    out_dir = base / "res" / "html"
    out_dir.mkdir(parents=True, exist_ok=True)

    env = Environment(loader=FileSystemLoader(base / "templates"),
                      autoescape=select_autoescape(["html", "jinja2"]))
    html = env.get_template("internal-hdd.jinja2").render(
        items=options, update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    (out_dir / f"internal-hdd-{datetime.now():%Y%m%d}.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    save_to_html(InternalHdd().options)