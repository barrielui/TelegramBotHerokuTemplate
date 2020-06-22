import feedparser
import logging
import dateutil.parser
import os
import queue
from telegram.ext import Updater, CommandHandler

rss_dict = {}
# declare FIFO queue to store existing feeds
q1 = queue.Queue(20) # check maximum number of entries of your feed
q1.put('') 

Token = os.environ.get('tg_bot_token')
channel1 = os.environ.get('tg_push_channel1')
channel2 = os.environ.get('tg_push_channel2')
channel3 = os.environ.get('tg_push_channel3')
channel4 = os.environ.get('tg_push_channel4')

public_channel = [channel1, channel2]
private_channel= [channel3, channel4]
delay = 300

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


def rss_monitor(bot, job):
    for name, url_list in rss_dict.items():
        rss_d  = feedparser.parse(url_list[0])
        entries = rss_d.entries
        
        # sorting feed entries by published time
        # skip if the feed you follow do not sort publish time correctly
        def get_published(entries):
            return entries.get('published')
        entries.sort(key=get_published, reverse=True)
     
        # monitor the top 5 entries in reverse order (old entries is sent first)
        for n in range(5, -1., -1):
            # bot.send_message(chat_id=chatid, text=entries[0]['link'])

            # check for repeated entry by link
            if ((entries[n]['link'] not in list(q1.queue)) and q1.full()):
                published = dateutil.parser.parse(entries[n]['published'])

                # Create tag for message by link pattern
                # Pattern example: (domain).com/<tag>/(article_id_)
                # Tag example: life-style -> #LifeStyle
                tag = '#' + entries[n]['link'].partition("com/")[2].partition("/")[0].title().replace('-','')
                msg = '<b>' + name + ': ' + entries[n]['title'] + '</b> \n' + tag + '\n' + entries[n]['summary'] + ' <a href="' + entries[n]['link'] + '">read more</a> \n' + published.strftime("%d %b %Y %H:%M")

                # Example of differentiating message pattern for public and private channels
                for channel in public_channel:
                    bot.send_message(chat_id=channel, text=(msg), parse_mode='HTML', disable_web_page_preview= 'True')
                for channel in private_channel:
                    bot.send_message(chat_id=channel3, text=(msg), parse_mode='HTML')
                # add entry to queue
                q1.get()
                q1.put(entries[n]['title'])

            if (not q1.full()):
                print('feeding queue ' + str(n))
                q1.put(entries[n]['link'])


def init():
    rss_dict['Reddit'] = 'https://www.reddit.com/r/funny/.rss'
    # Multiple feeds in single script is supported.  Please change the range below manually
    
    # test printing feed
    entries = feedparser.parse(rss_dict['Stuff']).entries
    print("Try to fetch rss feeds from " + str(rss_dict['Stuff']))
    
    # sorting feed entries by published time
    def get_published(entries):
        return entries.get('published')
    entries.sort(key=get_published, reverse=True)
    
    for n in range(19, -1, -1):  #entries list starts from 0

        # check for repeated entry by link
        # if entry of new title is found, push to channel
        if ((entries[n]['link'] not in list(q1.queue)) and q1.full()):
            print('Sending initial message ' + str(entries[n]['title']))
        if (not q1.full()):
            print('feeding queue ' + str(n))
            q1.put(entries[n]['link'])
    
    
def main():
    updater = Updater(token=Token)
    job_queue = updater.job_queue
    dp = updater.dispatcher

    init()

    rss_load()
    job_queue.run_repeating(rss_monitor, delay)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
