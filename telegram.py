import feedparser
import logging
import sqlite3
import dateutil.parser
import os
import queue
from telegram.ext import Updater, CommandHandler

rss_dict = {}
q1 = queue.Queue(30) # queue configured as first in first out
q1.put('')

Token = os.environ.get('tg_bot_token')
channel = os.environ.get('tg_push_channel')

delay = 60

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


# SQLITE
def sqlite_connect():
    global conn
    conn = sqlite3.connect('feed.db', check_same_thread=False)


def sqlite_load_all():
    sqlite_connect()
    c = conn.cursor()
    c.execute('SELECT * FROM feed')
    rows = c.fetchall()
    conn.close()
    return rows

# name: name of the feed, link: link to the feed, last: last entry in the feed
# basically not needed
def sqlite_write(name, link, last):
    sqlite_connect()
    c = conn.cursor()
    q = [(name), (link), (last)]
    c.execute('''INSERT INTO feed('name','link','last') VALUES(?,?,?)''', q)
    conn.commit()


# RSS________________________________________
def rss_load():
    # if the dict is not empty, empty it.
    if bool(rss_dict):
        rss_dict.clear()

    for row in sqlite_load_all():
        rss_dict[row[0]] = (row[1], row[2])


def rss_monitor(bot, job):
    for name, url_list in rss_dict.items():
        # error prevention
        rss_d  = feedparser.parse(url_list[0])
        entries = rss_d.entries
        
        # sorting feed entries by published time
        def get_published(entries):
            return entries.get('published')
        entries.sort(key=get_published, reverse=True)

        # when newer entry is found, update database
        if (url_list[1] != entries[0]['link']):
            conn = sqlite3.connect('feed.db')
            q = [(str(entries[0]['link'])), (url_list[0])]
            c = conn.cursor()
            # c.execute('''INSERT INTO feed('name','link','last') VALUES(?,?,?)''', q)
            c.execute('''UPDATE feed set last = ? WHERE link=?''', q)
            conn.commit()
            conn.close()
            rss_load()
            
            # load a few additional entries as there may be new entries with older publish time.
            for n in range(0,3):
                # bot.send_message(chat_id=chatid, text=entries[0]['link'])

                # check for repeated entry by title
                # if entry of new title is found, push to channel
                if (entries[n]['title'] not in list(q1.queue)):
                    published = dateutil.parser.parse(entries[n]['published'])
                    tag = '#' + entries[n]['link'].partition("co.nz/")[2].partition("/")[0].title().replace('-','')
                    bot.send_message(chat_id=channel, text=('<b>' + entries[n]['title'] + '</b> \n' + tag + '\n' + entries[n]['summary'] + ' <a href="' + entries[n]['link'] + '">read more</a> \n' + published.strftime("%d %b %Y %H:%M")), parse_mode='HTML')
                    # add entry to queue
                    if(q1.full()):
                        q1.get()
                        q1.put(entries[n]['title'])
                    else:
                        q1.put(entries[n]['title'])


def init_sqlite():
    conn = sqlite3.connect('feed.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE feed (name text, link text, last text, time datetime default current_timestamp)''')
    # add feed to subscribe, with first argument as name, second argument as url to feed
    # f = ['<name>', '<feed_url>']
    c.execute('''INSERT INTO feed('name', 'link') VALUES (?,?)''',f)
    print('added feed: ')
    print(f)
    conn.commit()
    conn.close()

def main():
    updater = Updater(token=Token)
    job_queue = updater.job_queue
    dp = updater.dispatcher

    # try to create a database if missing
    try:
        init_sqlite()
    except sqlite3.OperationalError:
        print('resume with exisiting feeds')
        pass

    rss_load()
    job_queue.run_repeating(rss_monitor, delay)

    updater.start_polling()
    updater.idle()
    conn.close()


if __name__ == '__main__':
    main()
