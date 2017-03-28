from falsy.netboy.fetch import fetch
from falsy.netboy.run import run

if __name__ == "__main__":
    urls = [
        {
            'url': 'http://www.baidu.com'
        },
        {
            'url': 'http://www.douban.com'
        }
    ]
    run(fetch(urls))
