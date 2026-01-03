from playwright.sync_api import sync_playwright
import pandas as pd
import time
from datetime import datetime

URL = "https://www.nike.com/in/w/womens-shoes-5e1x6zy7ok"

def infer_gender(category):
    if not category:
        return "Unknown"
    cat = category.lower()
    if "women" in cat:
        return "Women"
    if "men" in cat:
        return "Men"
    return "Unisex"

def scrape_nike_womens_shoes():
    products = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        # Scroll to load all products
        last_height = 0
        while True:
            page.mouse.wheel(0, 3000)
            time.sleep(2)
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        cards = page.locator("div.product-card").all()

        for card in cards:
            try:
                name = card.locator("div.product-card__title").inner_text()
            except:
                name = None

            try:
                category = card.locator("div.product-card__subtitle").inner_text()
            except:
                category = None

            # ✅ FIXED PRICE EXTRACTION (handles missing / discounted prices)
            price = None
            try:
                price = card.locator("div.product-price").inner_text()
            except:
                try:
                    price = card.locator("div[data-test='product-price']").inner_text()
                except:
                    price = None

            try:
                product_url = card.locator("a").first.get_attribute("href")
                if product_url and product_url.startswith("/"):
                    product_url = "https://www.nike.com" + product_url
            except:
                product_url = None

            gender = infer_gender(category)
            has_price = "Yes" if price else "No"
            scraped_date = datetime.now().strftime("%Y-%m-%d")

            products.append({
                "Product Name": name,
                "Category": category,
                "Price": price,
                "Product URL": product_url,
                "Gender": gender,
                "Has Price": has_price,
                "Scraped Date": scraped_date
            })

        browser.close()

    df = pd.DataFrame(products)
    df.to_csv("nike_womens_shoes_final.csv", index=False)
    print(f"Scraped {len(df)} products and saved to nike_womens_shoes_final.csv")


if __name__ == "__main__":
    scrape_nike_womens_shoes()
