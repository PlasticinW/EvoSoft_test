from playwright.sync_api import sync_playwright
#
# Внимание! Данное решение основано на перехвате xhr запросов с применением playwright
#
def scrape_profile(url) -> dict:
    _xhr_calls = []

    def find_field(data, target_field):
        if isinstance(data, dict):
            if target_field in data:
                return data[target_field]
            for key in data:
                result = find_field(data[key], target_field)
                if result is not None:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = find_field(item, target_field)
                if result is not None:
                    return result
        return None

    def intercept_response(response):
        # необходимая дата находится в файле UserTweets... .json
        # используем эту функцию чтобы перехватить xhr запрос
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
        return response

    # данные на x.com подгружаются динамически, поэтому нужен какой-то браузер вроде selenium или playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, proxy={"server": "http://168.81.65.213:8000"})
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # перехватываем xhr запросы:
        page.on("response", intercept_response)
        # переходим на страничку твитера Илона Маска и ждём её загрузки
        page.goto(url, timeout=90000)
        page.wait_for_selector("[data-testid='primaryColumn']")

        # находим json-файл UserTweets здесь у нас хранится вся необходимая дата, тут мы можем найти entryId
        # в этом поле хранятся конечные ссылки на твиты, а также поля full_text в которых хранится текст твитов
        tweet_calls = [f for f in _xhr_calls if "UserTweets" in f.url]
        for xhr in tweet_calls:
            data = xhr.json()
            result = []
            entries = find_field(data, 'entries')
            for entry in entries:
                entry_id = entry.get('entryId')
                full_text = find_field(entry, 'full_text')
                if full_text is None:
                    full_text = 'Null'
                result.append((entry_id, full_text))
    return result



if __name__ == "__main__":
    tweets = scrape_profile("https://x.com/Elonmusk")
    print("Последние 10 твитов Илона Маска: ")
    for i in range(10):
        print(f"{i+1}: ", tweets[i][1])