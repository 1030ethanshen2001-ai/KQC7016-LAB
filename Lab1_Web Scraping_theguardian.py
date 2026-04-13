import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# ==========================================================
# PART 1: Initialization (初始化)
# ==========================================================
#print("Starting the scraper...")
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # 如果需要静默运行，请取消注释
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

URL = "https://www.theguardian.com/football/ng-interactive/2025/dec/16/the-100-best-male-footballers-in-the-world-2025"
driver.get(URL)
time.sleep(5)

# ==========================================================
# PART 2: Auto-Scrolling (自动滚动加载)
# ==========================================================
print("🔎Scrolling down to load all player data...")
for i in range(15):
    driver.execute_script("window.scrollBy(0, 1200);")
    time.sleep(1)

# ==========================================================
# PART 3: Data Extraction (数据提取与清洗)
# ==========================================================
soup = BeautifulSoup(driver.page_source, "html.parser")
# 根据卫报结构定位球员卡片容器
players_items = soup.select('.gv-list-entry')

all_results = []

for item in players_items:
    try:
        # 提取原始标题（通常是 "1Ousmane Dembélé"）
        raw_title = item.select_one('.gv-list-title').get_text(strip=True)

        # 使用正则表达式分离数字和名字
        # ^(\d+) 匹配开头的数字，(.*) 匹配后面所有内容
        match = re.match(r'^(\d+)(.*)', raw_title)

        if match:
            rank = match.group(1)  # 序号: "1"
            name = match.group(2).strip()  # 名字: "Ousmane Dembélé"
        else:
            rank = "N/A"
            name = raw_title

        # 提取球队信息 (从对应的 span 中获取)
        # 注意：卫报的结构中，Team 往往在 gv-list-club 类的最后一个 span
        team_element = item.select_one('.gv-list-club')
        team = team_element.find_all('span')[-1].get_text(strip=True) if team_element else "Unknown Team"

        # 提取位置信息
        pos_element = item.select_one('.gv-list-position')
        position = pos_element.find_all('span')[-1].get_text(strip=True) if pos_element else "N/A"

        all_results.append({
            "rank": rank,
            "name": name,
            "team": team,
            "position": position
        })
    except Exception:
        continue

# ==========================================================
# PART 4: Formatted Output (格式化输出)
# ==========================================================
print(f"\n ⚽️Successfully scraped {len(all_results)} players.")
print("-" * 100)
# 表头
print(f"{'Rank':<8}{'Player Name':<25} | {'Team / Nationality':<35} | {'Position'}")
print("-" * 100)

for p in all_results:
    # {p['rank']:<8} 会在序号后留出足够空间，确保与名字之间有明显间距
    # {p['name']:<25} 确保名字列宽度一致，使后面的分隔符 | 垂直对齐
    print(f"{p['rank']:<8}{p['name']:<25} | {p['team']:<35} | {p['position']}")

# ==========================================================
# PART 5: Specific Filter (筛选巴塞罗那球员)
# ==========================================================
target_club = "Barcelona"
# 使用列表推导式筛选出所有效力于巴萨的球员
barca_players = [p for p in all_results if target_club in p['team']]

print("\n" + "=" * 100)
print(f"Players from {target_club}")
print("=" * 100)

if barca_players:
    # 打印表头
    print(f"{'Rank':<8}{'Player Name':<25} | {'Team / Nationality':<35} | {'Position'}")
    print("-" * 100)
    # 打印筛选结果
    for p in barca_players:
        print(f"{p['rank']:<8}{p['name']:<25} | {p['team']:<35} | {p['position']}")
    print("-" * 100)
    print(f"Total 🔵🔴⚽{target_club} players found: {len(barca_players)}")
else:
    print(f"No players from {target_club}🔵🔴⚽ were found in the top 100 list.")
driver.quit()