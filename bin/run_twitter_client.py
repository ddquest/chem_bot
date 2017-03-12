import configparser
import tweepy
import time
import tempfile
import os

from chem_bot import SmilesEncoder


def get_auth():
    config = configparser.ConfigParser()
    config.read('twitter.token')
    auth = tweepy.OAuthHandler(
        config.get('tokens', 'consumer_key'),
        config.get('tokens', 'consumer_secret'))
    auth.set_access_token(
        config.get('tokens', 'access_token'),
        config.get('tokens', 'access_token_secret'))
    return tweepy.API(auth)


def oauth(auth):
    try:
        redirect_url = auth.get_authorization_url()
        print('Get authorized PIN code from url.')
        print(redirect_url)
        pin = input('PIN:')
        auth.get_access_token(pin)
        print('access_token:', auth.access_token)
        print('access_token_secret:', auth.access_token_secret)
    except tweepy.TweepError:
        raise Exception('Error! Failed to get request token.')


def reply(api, smiles, screen_name):
    """Tweet chem graph to user"""
    print('smiles: {0}'.format(smiles))
    tweet = '@{0}'.format(screen_name)

    encoder = SmilesEncoder(smiles)
    png_binary = encoder.to_png()
    if hasattr(encoder, 'canvas'):
        image = tempfile.TemporaryFile()
        image.write(png_binary)
        image.seek(0)
        api.update_with_media(
            filename='{0}.png'.format(smiles),
            status=tweet,
            file=image)
    else:
        print('Encoding error')
        tweet += (
            u' すまない。どうやらこのSMILESは上手く変換できなかったようだ。')
        api.update_status(tweet)


def _tweet_test(api, smiles, screen_name):
    return api.update_status('tes')


def get_config():
    config = configparser.ConfigParser()
    config.read('twitter.config')
    return config


class Listner(tweepy.StreamListener):
    """Streaming time-line."""
    def __init__(self, api=None):
        super().__init__(api)

    def on_status(self, status):
        print('----------')
        print('id: {0} >>> {1}'.format(status.id, status.text))

        self.command_prefix = config.get('general', 'command_prefix')
        self.command_prefix = self.command_prefix
        if str(status.text).startswith(self.command_prefix):
            smiles = str(status.text).lstrip(self.command_prefix)
            reply(api, smiles, status.author.screen_name)
        return True


def _main():
    global api
    global config
    api = get_auth()
    config = get_config()
#    oauth(api.auth)
    
    stream = tweepy.Stream(api.auth, Listner(), secure=True)
    while True:
        try:
            stream.userstream()
        except Exception:
            time.sleep(60)
            stream = tweepy.Stream(api.auth, Listner(), secure=True)

if __name__ == '__main__':
    _main()
