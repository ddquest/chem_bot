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


__CONFIG_FILE__ = 'twitter.config'


def oauth(auth, config):
    if auth.access_token == '':
        try:
            redirect_url = auth.get_authorization_url()
            print('Get authorized PIN code from url.')
            print(redirect_url)
            pin = input('PIN: ')
            auth.get_access_token(pin)
            config.set('tokens', 'access_token', auth.access_token)
            config.set(
                'tokens', 'access_token_secret', auth.access_token_secret)
            with open(__CONFIG_FILE__, 'w') as f:
                config.write(f)
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
    config.read(__CONFIG_FILE__)
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
        self.hashtag = config.get('general', 'hashtag')
        self.bot_id = config.get('general', 'bot_id')
        self.hashtag_len = len(self.hashtag)
        self.iupac_trigger_pattern = re.compile(
            r'{1}.*{2}'.format(self.bot_id, self.iupac_prefix))
        self.smiles_trigger_pattern = re.compile(
            r'{1}.*{2}'.format(self.bot_id, self.smiles_prefix))

    def on_status(self, status):
        command_prefix = status.text.split(':')[0]
        reply_users = (
            [status.author.screen_name] +
            self.get_mention_users(status._json))
        if re.search(iupac_trigger_pattern, command_prefix.lower()):
        #if str(command_prefix.lower()).find(self.iupac_prefix) != -1:
            print(
                '[CATCH] @{0} >>> {1}'
                .format(status.author.screen_name, status.text))
            iupac = status.text.split(
                ':')[1] \
                .lstrip(' ').replace('\n', '').replace('\r', '')
            if self.check_ascii(iupac):
                smiles, error = chem_bot.util.converter.iupac_to_smiles(
                    iupac, self.opsin)
            else:
                smiles = ''
                error = iupac

            if smiles == '':
                self.reply_iupac_convert_error(
                    error, status.id, reply_users)
                print('[BOT] Error: {0}'.format(error))
            else:
                self.reply_with_png(
                    api,
                    smiles,
                    status.id,
                    reply_users,
                    descriptor_type='IUPAC名',
                    with_smiles=True)
            print('[BOT] continue streaming...')

        if re.search(smiles_trigger_pattern, command_prefix.lower()):
        #if str(command_prefix.lower()).find(self.smiles_prefix) != -1:
            print(
                '[CATCH] @{0} >>> {1}'
                .format(status.author.screen_name, status.text))
            command = status.text.split(':')[1].lstrip(' ')
            smiles, option_d = self.parse_tweet_command(command)
            self.reply_with_png(
                api,
                smiles,
                status.id,
                reply_users,
                option_d=option_d)
            print('[BOT] continue streaming...')

        return True

    def tweet_mention_formatter(self, screen_names):
        return ' '.join(['@{0}'.format(x) for x in screen_names])

    def get_mention_users(self, data):
        """Parse json from Twitter api data.

        Returns:
            screen_names: list
        """
        return [x['screen_name'] for x in data['entities']['user_mentions']]

    def parse_tweet_command(self, command):
        """Parse command into SMILES/IUPAC and options.

        If command not has any options, return (smile/iupac, None)
        """
        try:
            discriptor, trail_line = re.split(r',[ ]*| +', command, maxsplit=1)
        except ValueError:
            discriptor = command.replace('\n', '').replace('\r', '')
            return discriptor, None

        discriptor = command.replace('\n', '').replace('\r', '')
        options = re.split(r', *', trail_line)
        option_d = dict([re.split(r': *', x) for x in options])
        return discriptor, option_d

    def reply_iupac_convert_error(self, error, s_id, screen_names):
        """Tweet for reply about iupac convert error."""
        print('[BOT] IUPAC conversion error')
        tweet = self.tweet_mention_formatter(screen_names)
        return self.tweet_error_message(
            tweet + 'すまない。私の化学目録に「{0}」という文字は無かった。'
            .format(error), s_id)

    def reply_with_png(self, api, smiles,
                       s_id, screen_names, option_d=None,
                       descriptor_type='SMILES', with_smiles=False):
        """Tweet chem graph to user"""
        print('[SMILES]: {0}'.format(smiles))
        tweet = self.tweet_mention_formatter(screen_names)

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

        if with_smiles:
            tweet = '{0} "{1}"'.format(tweet, smiles)

        try:
            api.update_with_media(
                filename='{0}.png'.format(smiles),
                status=self.add_hashtag(tweet),
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

    def add_hashtag(self, line):
        """Add Twitter hashtag after line."""
        if len(line) + self.hashtag_len + 1 > 140:
            return line[:-self.hashtag_len+4] + '... ' + self.hashtag
        else:
            return line + ' ' + self.hashtag


def _main():
    global config
    global api
    api, config = get_config()
    oauth(api.auth, config)
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
