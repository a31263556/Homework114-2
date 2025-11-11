#app.py
#CLI 主程式
#1. 更新資料庫（爬取 + 寫入 SQLite）
#2. 查詢資料庫
#3. 離開
from typing import List, Tuple
from scraper import scrape_books
from database import init_db, insert_books, search_by_title, search_by_author


def print_menu() -> None:
    print("\n=== 博客來 LLM 書籍查詢系統 ===")
    print("1. 更新書籍資料庫")
    print("2. 查詢書籍")
    print("3. 離開")


def print_search_menu() -> None:
    print("\n--- 查詢選單 ---")
    print("a. 依書名查詢")
    print("b. 依作者查詢")
    print("c. 返回主選單")


def show_results(rows: List[Tuple]) -> None:
    if not rows:
        print("查無資料。")
        return

    for title, author, price, link in rows:
        print(f"書名: {title}")
        print(f"作者: {author}")
        print(f"價格: {price}")
        print(f"連結: {link}")
        print("-" * 40)


def update_database() -> None:
    print("正在爬取資料，請稍候...")
    # vvv 確保 headless 是 False vvv
    books = scrape_books(headless=False)
    print(f"共擷取 {len(books)} 筆資料。")

    inserted = insert_books(books)
    print(f"成功新增 {inserted} 筆資料。")


def main() -> None:
    init_db()
    while True:
        print_menu()
        choice = input("請輸入選項：").strip()

        if choice == "1":
            update_database()

        elif choice == "2":
            while True:
                print_search_menu()
                sub = input("請輸入選項：").strip().lower()

                if sub == "a":
                    keyword = input("輸入書名關鍵字：").strip()
                    rows = search_by_title(keyword)
                    show_results(rows)

                elif sub == "b":
                    keyword = input("輸入作者關鍵字：").strip()
                    rows = search_by_author(keyword)
                    show_results(rows)

                elif sub == "c":
                    break

                else:
                    print("選項錯誤，請重新輸入。")

        elif choice == "3":
            print("結束")
            break

        else:
            print("選項錯誤，請重新輸入。")


if __name__ == "__main__":
    main()
