#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import re
import tempfile
import textwrap
import time
import tweepy

import chem_bot
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
        self.iupac_prefix = config.get('general', 'iupac_prefix')
        self.smiles_prefix = config.get('general', 'smiles_prefix')
        self.opsin = config.get('general', 'opsin')

    def on_status(self, status):
        if str(status.text).startswith(self.iupac_prefix):
            print(
                '[CATCH] @{0} >>> {1}'
                .format(status.author.screen_name, status.text))
            iupac = status.text.split(self.iupac_prefix)[1].lstrip(' ')
            if self.check_ascii(iupac):
                smiles, error = chem_bot.util.converter.iupac_to_smiles(
                    iupac, self.opsin)
            else:
                smiles = ''
                error = iupac

            if smiles == '':
                self.reply_iupac_convert_error(
                    error, status.id, status.author.screen_name)
                print('[BOT] Error: {0}'.format(error))
            else:
                self.reply_with_png(
                    api,
                    smiles,
                    status.id,
                    status.author.screen_name,
                    descriptor_type='IUPAC名')
            print('[BOT] continue streaming...')

        if str(status.text).startswith(self.smiles_prefix):
            print(
                '[CATCH] @{0} >>> {1}'
                .format(status.author.screen_name, status.text))
            command = status.text.split(self.smiles_prefix)[1].lstrip(' ')
            smiles, option_d = self.parse_tweet_command(command)
            self.reply_with_png(
                api,
                smiles,
                status.id,
                status.author.screen_name,
                option_d=option_d)
            print('[BOT] continue streaming...')

        return True

    def parse_tweet_command(self, command):
        """Parse command into SMILES/IUPAC and options.

        If command not has any options, return (smile/iupac, None)
        """
        try:
            discriptor, trail_line = re.split(r',[ ]*| +', command, maxsplit=1)
        except ValueError:
            return command, None

        options = re.split(r', *', trail_line)
        option_d = dict([re.split(r': *', x) for x in options])
        return discriptor, option_d

    def reply_iupac_convert_error(self, error, s_id, screen_name):
        """Tweet for reply about iupac convert error."""
        print('[BOT] IUPAC conversion error')
        tweet = '@{0} '.format(screen_name)
        return self.tweet_error_message(
            tweet + 'すまない。私の化学目録に「{0}」という文字は無かった。'
            .format(error), s_id)

    def reply_with_png(self, api, smiles,
                       s_id, screen_name, option_d=None,
                       descriptor_type='SMILES'):
        """Tweet chem graph to user"""
        print('[SMILES]: {0}'.format(smiles))
        tweet = '@{0}'.format(screen_name)

        if smiles == '':
            tweet += (
                '{0}を入力し忘れていないか確認してもらえないだろうか。'
                .format(descriptor_type))
            return self.tweet_error_message(tweet, s_id)

        if self.check_ascii(smiles):
            encoder = SmilesEncoder(smiles)
        else:
            tweet += ' おや、SMILESに使えない文字が入っているようだ。'
            return self.tweet_error_message(tweet, s_id)

        if encoder.mol is None:
            print('Encoding error for [ {0} ]'.format(smiles))
            tweet += (
                ' すまない。この{0}は上手く変換できなかったようだ。'
                .format(descriptor_type))
            tweet += '"{0}"'.format(smiles)
            return self.tweet_error_message(tweet, s_id)

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

    def tweet_error_message(self, tweet, s_id):
            try:
                api.update_status(self.string_trimmer(tweet), s_id)
            except tweepy.error.TweepError as e:
                print('Error: {0}'.format(e))
            return False

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
    print('[BOT] OAuth is OK')
    print('[BOT] start streaming...')
    stream = tweepy.Stream(api.auth, Listner(), secure=True)
    while True:
        try:
            stream.userstream()
        except Exception:
            time.sleep(60)
            stream = tweepy.Stream(api.auth, Listner(), secure=True)


if __name__ == '__main__':
    _main()
