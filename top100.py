import praw, os, datetime, csv, requests, sys

reddit = praw.Reddit(client_id='eWIiJMi5pa8ckg',
                     client_secret='c8H1KKCjpy-e5y-5I38b9pWMsjU',
                     password='projectsuserpassword',
                     user_agent='top100 script by /u/projectsuser',
                     username='projectsuser')

"""
create a directory if it doesn't already exist
in a way that avoids race conditions
"""
def ensure_dir(dirname):
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

"""
append the metadata from submission s to the outfile as csv
"""
def save_metadata(s, outfile):
    with open(outfile, "a") as f:
        w = csv.writer(f, delimiter=',')
        w.writerow([s.title,
                    s.score,
                    datetime.datetime.fromtimestamp(s.created),
                    s.author.name,
                    s.shortlink])

"""
download a url as a file
"""
def download_file(url, outfile):
    response = requests.get(url)
    if response.status_code != 200:
        print("There was an error downloading the file from: " + url)
        return
    with open(outfile, 'wb') as f:
        for chunk in response.iter_content(4096):
            f.write(chunk)

"""
 download the top count posts from the given subreddit
"""
def save_top(subname, count):

    # create folder named for the subreddit plus timestamp
    dirname = subname + str(datetime.datetime.today())[:19]
    ensure_dir(dirname)

    # get the top posts
    sub = reddit.subreddit(subname)
    posts = sub.top(limit=count)

    # save the post content and metadata
    rank = 1
    for submission in posts:
        outfile = dirname+"/"+str(rank)
        if "https://www.reddit.com" in submission.url:
            # it's a text post
            with open(outfile+".md", "w") as f:
                f.write("# "+submission.title+"\n"+submission.selftext)
        else:
            url = submission.url
            if "imgur.com" in url and "i.imgur.com" not in url:
                # process as imgur album or page
                if "/a/" not in url:
                    pass
            # handle gfycat
            else:
                # try downloading the url as a an image
                extension = url.split(".")[-1]
                download_file(url, outfile+'.'+extension)
            # it's a link, check if it's to a known file host
            # if not to known host: continue
            pass
        save_metadata(submission, dirname+'/metadata.csv')
        rank += 1
        """
        if text post: save to RANKING.md
        if image/video: save to RANKING.EXTENSION
            hosts to handle:
                imgur
                gfycat
                i.reddituploads.com
        append to metadata file:
          link: submission.shortlink

        """


    # download each post into a file and append to the metadata file

"""
how to download images/videos:

    gfycat:
        https://gfycat.com/cajax/get/GFYNAME is a json containing links,
          look for "mp4Url" then download that file

    imgur:
        what to do about albums?
            make a folder?
        if no /a/:


    i.reddituploads.com/i.redd.it:
        the file is the url of the submission

    if don't recognize:
        try just saving the url of the submission as a file
        also parse the file extension from the last chars of the url
            after a period
"""

i = 1
while (i < len(sys.argv)):
    save_top(sys.argv[i], 25)
    i += 1
