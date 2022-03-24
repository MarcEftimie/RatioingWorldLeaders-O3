import requests
import csv
from bearer_token import token

bearer_token = token

search_url = "https://api.twitter.com/2/tweets/search/recent"

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, param):
    response = requests.get(url, auth=bearer_oauth, params=param)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def organize_data(response_dict):
    tweet_id = []
    author_id = []
    retweet_count = []
    like_count = []
    text = []

    for tweet in response_dict["data"]:
        tweet_id.append(tweet["id"])
        author_id.append(tweet["author_id"])
        retweet_count.append(tweet["public_metrics"]["retweet_count"])
        like_count.append(tweet["public_metrics"]["like_count"])
        text.append(tweet["text"])
    
    username = []
    followers_count = []

    for user in response_dict["includes"]["users"]:
        username.append(user["username"])
        followers_count.append(user["public_metrics"]["followers_count"])

    return [tweet_id, author_id, retweet_count, like_count, text, username, followers_count]

def create_query_params(next_token):
    query_params = {'query': 'Joe Biden -is:retweet', 'max_results': 10, 'tweet.fields': "author_id,public_metrics", 'expansions': 'author_id', 'user.fields': 'public_metrics', 'next_token': next_token}
    return query_params

def main():
    organized_data = []
    tweet_id = []
    author_id = []
    retweet_count = []
    like_count = []
    text = []
    username = []
    followers_count = []
    next_token = None

    for _ in range(3):
        json_response = connect_to_endpoint(search_url, create_query_params(next_token))
        organized_data = organize_data(json_response)
        next_token = json_response["meta"]["next_token"]
        tweet_id += organized_data[0]
        author_id += organized_data[1]
        retweet_count += organized_data[2]
        like_count += organized_data[3]
        text += organized_data[4]
        username += organized_data[5]
        followers_count += organized_data[6]
    with open('tweets.csv', 'w') as csvfile:
        fieldnames = ['tweet_id', 'author_id', 'retweet_count', 'like_count', 'text', 'username', 'followers_count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for i in range(0, len(tweet_id)):
            writer.writerow({'tweet_id': tweet_id[i],'author_id': author_id[i], 'retweet_count': retweet_count[i], 'like_count': like_count[i], 'text': text[i], 'username': username[i], 'followers_count': followers_count[i]})

if __name__ == "__main__":
    main()