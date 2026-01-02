import re
from datetime import datetime
from pathlib import Path

from bs4.element import Tag
from jinja2 import Template

from utilits import get_index_soup, translator


class InternalHdd:
    def __init__(self):
        self.title = "傳統內接硬碟HDD"
        self.tag = self.get_tag()
        self.optgroups = self.get_optgroups()
        self.options = self.get_options()

    # # 嚴謹查詢
    # def get_tag(self):
    #     soup = get_index_soup(is_coolpc_having_fucking_garbage_html=True)
        
    #     # 查看 HTML 結構
    #     # print(soup)
    #     # print("-----------------------------------------------------------------")
        
    #     title_tag = soup.find(text=self.title)
        
    #     # 確認 title_tag 是否找到
    #     # print("Title tag found:", title_tag)
    #     # print("-----------------------------------------------------------------")

    #     if title_tag is None:
    #         raise ValueError(f"無法在 HTML 中找到標題 '{self.title}'，請檢查內容或標題拼寫是否正確。")
    #     tag: Tag = title_tag.parent
    #     return tag

    # 模糊查詢
    def get_tag(self):
        soup = get_index_soup(is_coolpc_having_fucking_garbage_html=True)
        
        # 查看 HTML 結構
        # print(soup)
        # print("-----------------------------------------------------------------")
        
        # 在所有 <td> 標籤中尋找指定標題 (模糊查詢)
        title_td = None
        for td in soup.find_all("td", class_="t"):
            if self.title in td.text:  # 使用 in 檢查是否包含關鍵字
                title_td = td
                break
        
        # 確認 title_tag 是否找到
        # print("Title tag found:", title_tag)
        # print("-----------------------------------------------------------------")
        
        if title_td is None:
            raise ValueError(f"無法找到包含 '{self.title}' 的 <td> 標籤，請檢查標題內容。")
        
        tag: Tag = title_td.parent  # title_td.parent 應該會是包含所有選項的 <tr> 標籤
        return tag


    def get_optgroups(self):
        optgroups = self.tag.find_all("optgroup")
        return optgroups

    def get_options(self):
        options = list()
        for group in self.optgroups:
            subtitle = group["label"]
            for option_tag in group.find_all("option"):
                if option_tag.has_attr("disabled"):
                    continue
                a_option = InternalHddOption(self.title, subtitle, option_tag.text)
                options.append(a_option)
        return options


class InternalHddOption:
    def __init__(self, title: str, subtitle: str, describe: str):
        self.title = title
        self.subtitle = subtitle
        self.describe = describe
        self.brand = self.get_brand()
        self.size = self.get_size()
        self.series = self.get_series()
        self.memory = self.get_memory()
        self.model = self.get_model()
        self.rpm = self.get_rpm()
        self.warranty = self.get_warranty()
        self.price = self.get_price()
        self.cp_value = self.get_cp_value()

    def get_brand(self):
        brand = self.describe.split()[0]
        return brand

    def get_size(self):
        match = re.search(r"(\d+)(TB|G)", self.describe)
        size = match.group(1)
        size = int(size)
        unit = match.group(2)
        if "G" == unit:
            size /= 1000
        return size

    def get_series(self):
        # match = re.search(r"(?<=【)[\w ]+(?=】)", self.describe) # 正則表達
        match = re.search(r"(?<=【)[^】]+", self.describe)
        if not match:
            return None
        series = match.group()
        return series

    def get_memory(self):
        match = re.search(r"(?<=\()?\d+(?=MB?)", self.describe)
        if not match:
            return None
        memory = match.group()
        return memory

    def get_model(self):
        match = re.search(r"(?<=\()(\w|^/)+(?=\))", self.describe)
        if not match:
            return None
        model = match.group()
        return model

    def get_rpm(self):
        # match = re.search(r"(?<=/)\d+(?=轉/)", self.describe) # 舊
        match = re.search(r"(?<=/)\d+(?=轉)", self.describe)
        if not match:
            return None
        rpm = match.group()
        return int(rpm)

    def get_warranty(self):
        match = re.search(r"(?<=/)\w(?=年)", self.describe)
        if not match:
            return None
        warranty = match.group()
        return translator[warranty]

    # # 僅用原價 (不判斷漲、特價)
    # def get_price(self):
    #     match = re.search(r"(?<=\$)(\d+)", self.describe)
    #     price = match.group()
    #     return int(price)

    # 使用實際價格
    def get_price(self):
        # 匹配箭頭後的價格，提取箭頭後的數字
        match = re.search(r"\$[\d,]+(?:↘|↗)\$([\d,]+)", self.describe)
        #match = re.search(r"\$([\d,]+)(?:↘|↗)\$([\d,]+)", self.describe)
        if match:
            price = match.group(1)  # 取箭頭後的價格
            return int(price)
        else:
            # 如果沒有箭頭，則返回原價格
            match = re.search(r"(?<=\$)(\d+)", self.describe)
            if match:
                price = match.group(1)
                return int(price)
            else:
                # 如果沒有找到任何價格
                return None


    def get_cp_value(self):
        # return self.size * 1_000_000 / self.price # 舊版CP值
        # return self.price / self.size * 1_000_000 # MB計算
        # return self.price / self.size * 1_000 # GB計算
        return self.price / self.size * 1 # TB 計算


def save_to_html(options: list):

    # 程序根目錄
    base_path = Path(__file__).resolve().parent.parent

    # 檢查目錄是否存在，若不存在則建立
    folder_path = base_path / "res" / "html"
    if not folder_path.exists():
        folder_path.mkdir(parents=True)

    # 讀取 jinja2 後渲染
    template_path = base_path / "templates" / "internal-hdd.jinja2"
    content = template_path.read_text(encoding='utf-8')
    template = Template(content)

    # 渲染 HTML
    html = template.render(items=options, update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # 儲存 HTML檔案
    path = base_path / "res" / "html" / "internal-hdd.html"
    path.write_text(html, encoding='utf-8')


if __name__ == '__main__':
    x = InternalHdd()
    save_to_html(x.options)
