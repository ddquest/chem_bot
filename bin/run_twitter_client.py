import configparser
import re
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
            command = str(status.text).lstrip(self.command_prefix).lstrip(' ')
            smiles, option_d = self.parse_tweet_command(command)
            self.reply_with_png(
                api,
                smiles,
                status.id,
                status.author.screen_name,
                option_d=option_d)
        return True

    def parse_tweet_command(self, command):
        """Parse command into SMILES and options.

        If command not has any options, return (smiles, None)
        """
        try:
            smiles, trail_line = re.split(r',[ ]*| +', command, maxsplit=1)
        except ValueError:
            return command, None

        options = re.split(r', *', trail_line)
        option_d = dict([re.split(r': *', x) for x in options])
        return smiles, option_d

    def reply_with_png(self, api, smiles, s_id, screen_name, option_d=None):
        """Tweet chem graph to user"""
        print('smiles: {0}'.format(smiles))
        tweet = '@{0}'.format(screen_name)

        if self.check_ascii(smiles):
            encoder = SmilesEncoder(smiles)
        else:
            tweet += u' おや、SMILESに使えない文字が入っているようだ。'
            try:
                api.update_status(self.string_trimmer(tweet), s_id)
            except tweepy.error.TweepError as e:
                print('Error: {0}'.format(e))
            return False

        if encoder.mol is None:
            print('Encoding error for [ {0} ]'.format(smiles))
            tweet += (
                u' すまない。このSMILESは上手く変換できなかったようだ。')
            tweet += '"{0}"'.format(smiles)
            try:
                api.update_status(self.string_trimmer(tweet), s_id)
            except tweepy.error.TweepError as e:
                print('Error: {0}'.format(e))
            return False

        png_binary = encoder.to_png()
        image = tempfile.TemporaryFile()
        image.write(png_binary)
        image.seek(0)
        try:
            api.update_with_media(
                filename='{0}.png'.format(smiles),
                status=self.string_trimmer(tweet),
                in_reply_to_status_id=s_id,
                file=image)
        except Exception as e:
            print(e)
        return True

    def check_ascii(self, smiles):
        """Except multibyte characters in strings."""
        try:
            smiles.encode('ascii')
            return True
        except UnicodeEncodeError:
            return False

    def string_trimmer(self, line):
        """Wrap end of strings to under 140 characters."""
        if len(line) > 140:
            return line[:137] + '...'
        else:
            return line


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
