import configparser
import tempfile
import textwrap
import time
import tweepy

from chem_bot import SmilesEncoder


def oauth(auth):
    if auth.access_token == '':
        try:
            redirect_url = auth.get_authorization_url()
            print('Get authorized PIN code from url.')
            print(redirect_url)
            pin = input('PIN:')
            auth.get_access_token(pin)
            print('access_token:', auth.access_token)
            print('access_token_secret:', auth.access_token_secret)
            return auth
        except tweepy.TweepError:
            raise Exception(textwrap.dedent("""\
                Error: Failed to get request token.
                Please check [twitter.config].\
                """))
    else:
        return auth


def _tweet_test(api, smiles, screen_name):
    return api.update_status('tes')


def get_config():
    config = configparser.ConfigParser()
    config.read('twitter.config')
    auth = tweepy.OAuthHandler(
        config.get('tokens', 'consumer_key'),
        config.get('tokens', 'consumer_secret'))
    auth.set_access_token(
        config.get('tokens', 'access_token'),
        config.get('tokens', 'access_token_secret'))
    return tweepy.API(auth), config


class Listner(tweepy.StreamListener):
    """Streaming time-line."""
    def __init__(self, api=None):
        super().__init__(api)

    def on_status(self, status):
        print('[catch] id: {0} >>> {1}'.format(status.id, status.text))

        self.command_prefix = config.get('general', 'command_prefix')
        self.command_prefix = self.command_prefix
        if str(status.text).startswith(self.command_prefix):
            smiles = str(status.text).lstrip(self.command_prefix)
            self.reply(api, smiles, status.author.screen_name)
        return True

    def reply(self, api, smiles, screen_name):
        """Tweet chem graph to user"""
        print('smiles: {0}'.format(smiles))
        tweet = '@{0}'.format(screen_name)

        encoder = SmilesEncoder(smiles)
        if encoder.mol is None:
            print('Encoding error for [ {0} ]'.format(smiles))
            tweet += (
                u' すまない。どうやらこのSMILESは上手く変換できなかったようだ。')
            tweet += '"{0}"'.format(smiles)
            api.update_status(tweet)

        png_binary = encoder.to_png()
        image = tempfile.TemporaryFile()
        image.write(png_binary)
        image.seek(0)
        api.update_with_media(
            filename='{0}.png'.format(smiles),
            status=tweet,
            file=image)


def _main():
    global config
    global api
    api, config = get_config()
    oauth(api.auth)
    print('OAuth [ OK ]')
    print('start streaming...')
    stream = tweepy.Stream(api.auth, Listner(), secure=True)
    while True:
        try:
            stream.userstream()
        except Exception:
            time.sleep(60)
            stream = tweepy.Stream(api.auth, Listner(), secure=True)


if __name__ == '__main__':
    _main()
