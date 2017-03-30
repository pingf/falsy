import json

from falsy.netboy.fetch import boy
from falsy.netboy.run import run

if __name__ == "__main__":
    urls = [
        # {
        #     'url': 'http://louisville.bncollege.com/',
        #     'url': 'http://case.bncollege.com/',
        #     'noprogress': False,
        #     'useragent': 'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
        #     'cookiejar': 'aa.lwp',
        #     'cookiefile': 'aa.lwp',
        # },
        {
            'url': 'http://www.baidu.com',
            'dns_servers': '114.114.114.114'
        },
        # {
        #     'url': 'http://www.google.com',
        #     'dns_servers': '8.8.8.8'
        # },
    ]
    ress=run(boy(urls))
    for res in ress:
        if res is None:
            print('res is None')
            continue
        res['data'] = res['data'][:80]
        print(json.dumps(res, indent=2))
