import os
import praw # reddit API Wrapper
from urllib.error import URLError, HTTPError
import urllib.request as web
import urllib.request as req
import shutil # shell utilities
import colorama #https://pypi.org/project/colorama/
from colorama import Fore, Style
from PIL import Image
from InstagramAPI import InstagramAPI #https://github.com/LevPasha/Instagram-API-python
import time
import argparse
import requests
import json

def reformat_Image(ImageFilePath):
    image = Image.open(ImageFilePath, 'r')
    image_size = image.size
    width = image_size[0]
    height = image_size[1]

    if(width != height):
        bigside = width if width > height else height

        background = Image.new('RGB', (bigside, bigside), (255, 255, 255))
        offset = (int(round(((bigside - width) / 2), 0)), int(round(((bigside - height) / 2),0)))

        background.paste(image, offset)
        background.save('LastPost.jpg')
        print(Fore.GREEN + "The Image has been resized")

    else:
        print(Fore.LIGHTYELLOW_EX + "The image is already a square")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--subredditname', action="store", dest="subredditname", help='Your Subreddit name')
    parser.add_argument('--upvotes', action="store", dest="upvotes", help='The minimum required upvotes of a post to get posted', type=int)
    parser.add_argument('--subredditsearchlimit', action="store", dest="subredditsearchlimit", help='The number of sorted by hot posts that will get included on the search', type=int)
    parser.add_argument('--timebetween', action="store", dest="timebetween", help='The time between posts in seconds', type=int)
    parser.add_argument('--username', action="store", dest="username", help='Your IG Username')
    parser.add_argument('--password', action="store", dest="password", help='Your IG Password')
    parser.add_argument('--captionhastags', action="store", dest="captionhastags", help='Your IG Post hastags')
    parser.add_argument('--commentpost', action="store", dest="comment_post", help='Comment after posting the image? (y/n)')
    parser.add_argument('--rclientid', action="store", dest="rclientid", help='Your Reddit App Client ID')
    parser.add_argument('--rclientsecret', action="store", dest="rclientsecret", help='Your Reddit App Client Secret')
    parser.add_argument('--rusername', action="store", dest="rusername", help='Your Reddit Username')
    parser.add_argument('--rpassword', action="store", dest="rpassword", help='Your Reddit Password')
    parser.add_argument('--ruseragent', action="store", dest="ruseragent", help='Your user agent for reddit (put something random)')
    args = parser.parse_args()
    return args

def instagram_post(path, title, submID, hastag):
    caption = "{} \n{}".format(title, hastag)
    try:
        insta.uploadPhoto(path, caption=caption)
        print(Fore.GREEN + "Succesfully uploaded {}".format(submID))
    except:
        print(Fore.RED + "Instagram upload has failed.")

def instagram_comment(self, mediaID, commentText):
    data = json.dumps({'_uuid': self.uuid,
            '_uid': self.username_id,
            '_csrftoken': self.token,
            'comment_text': commentText})
    return self.SendRequest('media/' + str(mediaID) + '/comment/', self.generateSignature(data))

def instagram_getLastPostID(insta, user):
    InstagramAPI.searchUsername(insta, user)
    info = insta.LastJson
    username_id = info['user']['pk']
    user_posts = InstagramAPI.getUserFeed(insta, username_id)
    info = insta.LastJson
    return info['items'][0]['id']

def main(upvotes, _captionhastags, insta, subreddit, subredditname, insta_username, comment_post):
    current_dir = os.getcwd()

    dir_path = os.path.join(current_dir,subredditname) #Makes path where posts will be downloaded by joining current_dir and subreddit_name
    if not os.path.exists(dir_path):
        os.mkdir(dir_path) #If dir_path doesnt exist

    colorama.init(autoreset = True) #Initialise Colorama

    postsDownloaded = 0

    for submission in subreddit:
        if not submission.stickied and submission.score > upvotes and not submission.is_self:
            try:
                filePath = os.path.join(dir_path, "{}.jpg".format(submission.id)) #Create image path
            except:
                print(Fore.RED + "Couldn't make filepath, skipping...")
                continue
            if os.path.exists(filePath): #if we already downloaded the file
                postsDownloaded += 1
                continue
            else:
                try:
                    r = requests.get(submission.url, stream=True)
                    if r.status_code == 200:
                        with open(filePath, 'wb') as f:
                            r.raw.decode_content = True
                            shutil.copyfileobj(r.raw, f)
                    else:
                        print("Error while requesting the URL")

                    print(Fore.YELLOW + "{} posts have been skipped.".format(postsDownloaded))
                    print(Fore.GREEN + "[{} ({})] with {} upvotes has been downloaded.  URL => {}".format(submission.title, submission.id, submission.score, submission.url))
                    reformat_Image(filePath)
                    instagram_post("LastPost.jpg", submission.title, submission.id, _captionhastags)

                    if comment_post == "y" or comment_post == "yes":
                        instagram_comment(insta, instagram_getLastPostID(insta, insta_username), "Post had [{}] upvotes. [URL -> {}]".format(str(submission.score), submission.url))

                    break
                except:
                    print(Fore.RED + "Couldn't request the image, skipping...")
                    continue


if __name__ == '__main__':
    args = parse_args()
    reddit = praw.Reddit(
        client_id = args.rclientid,
        client_secret = args.rclientsecret,
        username = args.rusername,
        password = args.rpassword,
        user_agent = args.ruseragent)

    try:
        subreddit = reddit.subreddit(args.subredditname).hot(limit=args.subredditsearchlimit) #Create a subreddit object
    except:
        print(Fore.RED + "Couldn't create subreddit object")

    insta = InstagramAPI(args.username, args.password)
    try:
        insta.login()
    except:
        print(Fore.RED + "Instagram Login has failed.")
    while True:
        main(args.upvotes, args.captionhastags, insta, subreddit, args.subredditname, args.username, args.comment_post)
        os.system('timeout {}'.format(args.timebetween))
