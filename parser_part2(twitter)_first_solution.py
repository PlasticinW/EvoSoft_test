import requests
import re
import json
from playwright.sync_api import sync_playwright

#
# Внимание! Данное решение основано на мысли получения токена authorization, а затем и X-Guest-Token'а
# Однако X-Guest-Token оказывается неверным
#

#функция для получения токенов авторизации и гостя
def get_tokens(tweet_url, proxies):

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, proxy={"server": "http://168.81.65.213:8000"})
        page = browser.new_page()
        page.goto(tweet_url, timeout=90000)
        head_content = page.query_selector('head').inner_html()
        browser.close()

    html = requests.get(tweet_url, proxies=proxies)
    print(html.text)
    assert html.status_code == 200, f'Failed to get tweet page.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Status code: {html.status_code}.  Tweet url: {tweet_url}'

    mainjs_url = re.findall(r'https://abs.twimg.com/responsive-web/client-web/main.[^\.]+.js', head_content)

    assert mainjs_url is not None and len(
        mainjs_url) > 0, f'Failed to find main.js file.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Tweet url: {tweet_url}'

    mainjs_url = mainjs_url[0]

    mainjs = requests.get(mainjs_url, proxies=proxies)

    assert mainjs.status_code == 200, f'Failed to get main.js file.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Status code: {mainjs.status_code}.  Tweet url: {tweet_url}'

    bearer_token = re.findall(r'AAAAAAAAA[^"]+', mainjs.text)

    assert bearer_token is not None and len(
        bearer_token) > 0, f'Failed to find bearer token.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Tweet url: {tweet_url}, main.js url: {mainjs_url}'

    bearer_token = bearer_token[-1]
    
    # получаем x-guest-token
    with requests.Session() as s:
 
        s.headers.update({
            "user-agent":	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 OPR/112.0.0.0 (Edition Yx GX)",
            "accept":	"*/*",
            "accept-language":	"ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "accept-encoding":	"gzip, deflate, br, zstd",
            "authorization":	f"Bearer {bearer_token}",
            })

        s.proxies.update(proxies)

        # активируем bearer token и получаем x-guest-token
        guest_token = s.post(
            "https://api.twitter.com/1.1/guest/activate.json").json()["guest_token"]

    assert guest_token is not None, f'Failed to find guest token.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Tweet url: {tweet_url}, main.js url: {mainjs_url}'

    return bearer_token, guest_token

#функция для рекурсивного поиска необходимого поля в json файле
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

#функция извлечения ссылок на твиты и их текстов 
def extract_entry_ids_and_texts():
    with open("tweeter.json", 'r') as file:
        data = json.load(file)
    
    result = []
    entries = find_field(data, 'entries')
    for entry in entries:
        entry_id = entry.get('entryId')
        full_text = find_field(entry, 'full_text')
        if full_text is None:
            full_text = 'Null'
        result.append((entry_id, full_text))
    
    return result

url = "https://api.x.com/graphql/E3opETHurmVJflFsUBVuUQ/UserTweets?variables=%7B%22userId%22%3A%2244196397%22%2C%22count%22%3A20%2C%22includePromotedContent%22%3Atrue%2C%22withQuickPromoteEligibilityTweetFields%22%3Atrue%2C%22withVoice%22%3Atrue%2C%22withV2Timeline%22%3Atrue%7D&features=%7B%22rweb_tipjar_consumption_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22communities_web_enable_tweet_community_results_fetch%22%3Atrue%2C%22c9s_tweet_anatomy_moderator_badge_enabled%22%3Atrue%2C%22articles_preview_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22responsive_web_twitter_article_tweet_consumption_enabled%22%3Atrue%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22creator_subscriptions_quote_tweet_preview_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C%22rweb_video_timestamps_enabled%22%3Atrue%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22longform_notetweets_inline_media_enabled%22%3Atrue%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D&fieldToggles=%7B%22withArticlePlainText%22%3Afalse%7D"
access_token = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

proxies = {
    'http': 'http://168.81.65.213:8000',
    'https': 'http://168.81.65.213:8000',
}

headers = {
    'Authorization': f'Bearer {access_token}',
}

json_header = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': "application/json",
    'X-Guest-Token': '1835076136734183873',
}
#
#Вся сложность скрапинга x.com состоит в том, что файлы подгружаются динамически, не получается парсить голый html,
#приходится искать нужные данные в подгружаемых файлах, мне удалось найти такой json файл, в котором находится по сути вся страница
#далее переходим по этому файлу, для этого понадобятся данные аутентификации - json_header, а также proxies, на которые пришлось потратить 100р))))

auth, x_guest = get_tokens('https://x.com/Elonmusk/', proxies)
print(auth)
print(x_guest)

#response = requests.post('https://x.com/Elonmusk/', proxies=proxies)
#for header, value in response.headers.items():
#    print(f'{header}: {value}')
#    print()


response = requests.get(url, headers=json_header, proxies=proxies).json()

data = json.dumps(response, sort_keys=True, indent=4)

#записываем json в файл
with open("tweeter.json", "w", encoding='utf-8') as file:
    file.write(data)

#считываем его (в общем и целом в этом нет необходимости, просто пока писал код, комментировал ту часть, в которой отправляю запрос на получение
# этого json файла)
with open("tweeter.json", "r") as file:
    json_text = file.read()

data = json.loads(json_text)

tweets_urls = []
print('список 10 последних твитов Илона Маска: ')
res = extract_entry_ids_and_texts()
for i in range(10):
    #в json файле ссылки на страницы твитов можно найти в поле "entryId", но оно имеет следующий вид:
    # "entryId": "tweet-1833745060812509589", поэтому нужно рассплитить строку
    str_url = res[i][0].split("-")
    #Здесь сплитить пришлось потому что в поле "full_text" иногда кроме текста твитов хранились ссылки на сторонний контент, например картинок. 
    str_text = res[i][1].split("http")
    #tweets_urls.append(f"https://x.com/elonmusk/status/{str_url[1]}")
    #print('Ссылка на твит: ')
    #print(tweets_urls[i])
    print(f'Tweet {i+1}: ', str_text[0])

