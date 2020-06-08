import os
import sys
import requests
import bs4
import time
import argparse
from threading import Timer

class RepeatingTimer(Timer): 
    def run(self):
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)

def cur_time():
    return time.asctime(time.localtime(time.time()))

def download_from_bing(args, image_name):
    url = 'https://cn.bing.com/'
    soup = bs4.BeautifulSoup(requests.get(url).text, 'html.parser')
    bg = soup.find('div', id='bgImgProgLoad')
    tmp = bg['data-ultra-definition-src']
    if args.resolution == '3840x2160':
        tmp = tmp.replace('1920', '3840').replace('1080', '2160')
    img_url = url + tmp

    # download
    img = requests.get(img_url, stream=True)
    with open('imgs/{}.jpeg'.format(image_name), 'wb') as f:
        for chunk in img.iter_content(chunk_size=32):
                f.write(chunk)
    f.close()

def update(args):
    update = False
    image_name = 'background'
    while not update:
        print("[{}] It's time to update wallpaper.".format(cur_time()))
        try:
            download_from_bing(args, image_name)
            abs_path = os.path.join(os.getcwd(), 'imgs/{}.jpeg'.format(image_name))
            os.system('osascript -e "tell application \\"Finder\\" to set desktop picture to POSIX file \\"{}\\""'.format(abs_path))
            update = True
            print('[{}] Success to update wallpaper.'.format(cur_time()))
        except Exception:
            print('[{}] Failed to update wallpaper.'.format(cur_time()))
            time.sleep(300)
            print('Retry...')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=6)
    parser.add_argument('--resolution', type=str, default='1920x1080')
    args = parser.parse_args()
    t = RepeatingTimer(3600*args.interval, update, (args,))
    t.start()
