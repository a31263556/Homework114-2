#負責從 books.com.tw 搜尋 LLM，勾選圖書(BKA)分類、翻頁
#擷取書名、作者、價格、連結，回傳


from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


BASE_URL = "https://www.books.com.tw/"
SEARCH_KEYWORD = "LLM"


def create_driver(headless: bool = True) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # 避免被偵測
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver


def _try_click_category(driver) -> None:
    wait = WebDriverWait(driver, 10)
    try:
        chk = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='BKA']"))
        )
        driver.execute_script("arguments[0].click();", chk)
        return
    except Exception:
        pass

    driver.get("https://search.books.com.tw/search/query/key/LLM/cat/BKA")



def _extract_books_from_page(driver) -> List[Dict]:
    results = []
    items = driver.find_elements(By.CSS_SELECTOR, "div.table-td[id^='prod-itemlist-']")

    for item in items:
        try:
            title_el = item.find_element(By.CSS_SELECTOR, "h4 a")
            title = title_el.get_attribute("title") or title_el.text.strip()
            link = title_el.get_attribute("href")

            try:
                author = item.find_element(By.CSS_SELECTOR, "p.author").text.strip()
            except NoSuchElementException:
                author = ""

            try:
                price_elements = item.find_elements(By.CSS_SELECTOR, "ul.price b")
                if price_elements:
                    price_text = price_elements[-1].text.strip()
                    price_num = int("".join(filter(str.isdigit, price_text))) if price_text else None
                else:
                    price_text = item.find_element(By.CSS_SELECTOR, "ul.price").text.strip()
                    price_num = int("".join(filter(str.isdigit, price_text))) if price_text else None

            except NoSuchElementException:
                price_num = None

            results.append({
                "title": title,
                "author": author,
                "price": price_num,
                "link": link,
            })
        except NoSuchElementException:
            continue
        except Exception as e:
            print(f"處理項目時發生錯誤: {e}")
            continue

    return results



def scrape_books(max_pages: int = 50, headless: bool = True) -> List[Dict]:
    driver = create_driver(headless=headless)
    all_books: List[Dict] = []

    try:
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 15)

        search_box = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#key"))
        )
        search_box.clear()
        search_box.send_keys(SEARCH_KEYWORD)
        search_box.send_keys(Keys.ENTER)

        _try_click_category(driver)

        try:
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-td[id^='prod-itemlist-'] h4 a"))
            )
        except TimeoutException:
            print("Error: 網頁載入逾時，找不到任何書籍列表。")
            print(f"當前網址 (Current URL): {driver.current_url}")
            return []

        # 翻頁
        for page_num in range(max_pages):
            page_books = _extract_books_from_page(driver)
            all_books.extend(page_books)

            try:
                first_book_on_page = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-td[id^='prod-itemlist-'] h4 a"))
                )

                next_btn = driver.find_element(By.CSS_SELECTOR, "a.next")

                driver.execute_script("arguments[0].click();", next_btn)
                wait.until(EC.staleness_of(first_book_on_page))

            except NoSuchElementException:
                break
            except TimeoutException:
                print("翻頁時等待逾時。")
                break

    except Exception as e:
        print(f"爬蟲執行期間發生未預期的錯誤: {e}")

    finally:
        driver.quit()

    return all_books