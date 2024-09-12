import requests
import json

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
    'X-Guest-Token': '1834255090783248771',
}

#Вся сложность скрапинга x.com состоит в том, что файлы подгружаются динамически, не получается парсить голый html,
#приходится искать нужные данные в подгружаемых файлах, мне удалось найти такой json файл, в котором находится по сути вся страница
#далее переходим по этому файлу, для этого понадобятся данные аутентификации - json_header, а также proxies, на которые пришлось потратить 100р))))

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
