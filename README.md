# 原價屋簡單爬蟲

目前僅實現爬取傳統內接硬碟資料，並轉成簡單篩選網頁，包含每T價格比較。


## 使用方法 (擇一)

1. 運行 internal_hdd.py
```shell script
python internal_hdd.py
```
2. 直接雙擊 Run.bat (Windows)

## Path

- 結果網頁
    - res/html/internal-hdd-{yyyymmdd}.html

## 未來更新
1. 使用現代化UI框架美化模板
2. 建立.sh 用於 Linux 定時運行

## 更新紀錄
v260102
1. 優化保固邏輯 - 自適應多位數、更新 utilits
2. 優化保存檔案 - 檔案保存Html+日期
3. 優化批次啟動 - 自適應Html日期

v241115
1. 優化查找邏輯 -【精確】改為【模糊查詢】
2. 優化價格邏輯 - 漲跌幅、防止報錯
3. 優化檔案路徑 - 防止報錯
4. 優化模板顯示 - 合適大小、None優化
5. 新增批次啟動 - 運行後啟動腳本
