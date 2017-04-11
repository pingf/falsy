import json

from falsy.netboy.fetch import get_boy, post_boy
from falsy.netboy.run import run

if __name__ == "__main__":
    payload = [
        {
            "url": "http://172.30.0.77:8003/v1/validate",
            "postfields": {
                "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE0OTE4ODg2ODQsImNvZGVfaWQiOiJjYWYwZTZlOC0wYTEzLTExZTctOTVhNy0xYzg3MmM3MTBhNDgifQ.SkwAtOX8JW4ZRb2S4cftg7PGveU21DZKzlrBYRK6S9I"
            }
        }
    ]
    ress = run(post_boy(payload))
    for res in ress:
        if res is None:
            print('res is None')
            continue
        print(json.dumps(res, indent=2))
# print(json.dumps(res, indent=2))
# if __name__ == "__main__":
#     urls = [
#         # {
#         #     'url': 'http://louisville.bncollege.com/',
#         #     'url': 'http://case.bncollege.com/',
#         #     'noprogress': False,
#         #     'useragent': 'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
#         #     'cookiejar': 'aa.lwp',
#         #     'cookiefile': 'aa.lwp',
#         # },
#         {
#             'url': 'http://www.douban.com',
#             'dns_servers': '114.114.114.114'
#         },
#         # {
#         #     'url': 'http://www.google.com',
#         #     'dns_servers': '8.8.8.8'
#         # },
#     ]
#     ress=run(get_boy(urls))
#     for res in ress:
#         if res is None:
#             print('res is None')
#             continue
#         res['data'] = res['data'][:80]
#         print(json.dumps(res, indent=2))
