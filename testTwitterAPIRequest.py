import requests
import os
import json
import csv
import time
import dateutil.parser
import pandas as pd

def auth():
    return "AAAAAAAAAAAAAAAAAAAAAPLnaQEAAAAAnF0w6t7eNa40OIbvBh1MgJBSz5s%3DQY5HeeZPBjoYyiaRKVrVDO1gpRxydPeyAdTQ9cLcj5D6MKmbnh"

def create_headers(bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    return headers

def create_url(keyword, start_date, end_date, max_results = 10):
    search_url = "https://api.twitter.com/2/tweets/search/all"

    query_params = {
        'query': keyword,
        'start_time': start_date,
        'end_time': end_date,
        'max_results': max_results,
        'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
        'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
        'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
        'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
        'next_token': {}
    }
    return (search_url, query_params)

def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token
    response = requests.request("GET", url, headers=headers, params=params)
    print("Endpoint Response Code: "+str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json

def append_to_csv(json_response, fileName):
    counter = 0
    csvFile = open(fileName, "a", newline="", encoding='utf=8')
    csvWriter.writer(csvFile)
    for tweet in json_response['data']:
        author_id = tweet["author_id"]
        created_at = dateutil.parser.parse(tweet['created_at'])

        if 'geo' in tweet:
            geo = tweet['geo']['place_id']
        else:
            geo = " "
        tweet_id = tweet['id']
        lang = tweet['lang']

        retweet_count = tweet['public_metrics']['retweet_count']
        reply_count = tweet['public_metrics']['reply_count']
        like_count = tweet['public_metrics']['like_count']
        quote_count = tweet['public_metrics']['quote_count']

        source = tweet['source']
        text = tweet['text']

        res = [author_id, created_at, geo, tweet_id, lang, like_count, quote_count, reply_count, retweet_count, source, text]

        csvWriter.writerow(res)
        counter += 1

    csvFile.close()

    print("# of Tweets added from this response: ", counter)


bearer_token = auth()
headers = create_headers(bearer_token)
keyword = "Biden lang_en"
start_time = "2022-03-19T00:00:00.000Z"
end_time = "2022-03-21T00:00:00.000Z"
max_results = 15

url = create_url(keyword, start_time, end_time, max_results)
json_response = connect_to_endpoint(url[0], headers, url[1])

print(json.dumps(json_response, indent=4, sort_keys=True))

csvFile = open("data.csv", "a", newline="", encoding='utf-8')
csvWriter = csv.writer(csvFile)

csvWriter.writerow(['author id', 'created_at', 'geo', 'id', 'lang', 'like_count', 'quote_count', 'reply_count', 'retweet_count', 'source', 'tweet'])
csvFile.close()

count = 0
max_count = 100
flag = True
next_token = None
total_tweets = 0

while flag:
    if count >= max_count:
        break
    print("------------")
    print("Token: ", next_token)
    url = create_url(keyword, start_time, end_time, max_results)
    json_response = connect_to_endpoint(url[0], headers, url[1], next_token)
    result_count = json_response['meta']['result_count']

    if 'next_token' in json_response['meta']:
        next_token = json_response['meta']['next_token']
        print("Next Token: ", next_token)
        if result_count is not None and result_count > 0 and next_token is not None:
            print("Start Date: ", start_time)
            append_to_csv(json_response, "data.csv")
            count += result_count
            total_tweets += result_count
            print("Total # of Tweets added: ", total_tweets)
            print("-------------------")
            time.sleep(5)  
    else:
        if result_count is not None and result_count > 0:
            print("-------------------")
            print("Start Date: ", start_time)
            append_to_csv(json_response, "data.csv")
            count += result_count
            total_tweets += result_count
            print("Total # of Tweets added: ", total_tweets)
            print("-------------------")
            time.sleep(5)
        
        flag = False
        next_token = None
    time.sleep(5)
print("Total number of results: ", total_tweets)