from falsy.netboy.fetch import boy
from falsy.netboy.run import run

if __name__ == "__main__":
    urls = [
        {
            'url': 'http://www.rndj.com',
            'noprogress': False
        },
        # {
        #     'url': 'http://www.douban.com'
        # }
    ]
    run(boy(urls))
