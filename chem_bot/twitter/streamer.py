import re
import tempfile
import traceback
from twython import TwythonStreamer
from twython.exceptions import TwythonError

import chem_bot


class Streamer(TwythonStreamer):

    def __init__(self, api, config):
        super(Streamer, self).__init__(
            api.app_key, api.app_secret,
            api.oauth_token, api.oauth_token_secret)
        self.api = api
        self.config = config
        self.opsin = self.config.opsin
        self.reply_hashtag = self.config.hashtag
        self.hashtag_list = self.config.filter_hashtags.strip('.')
        self.reply_hashtag_len = len(self.reply_hashtag)

    def check_hashtags(self, hashtags):
        tags = []
        for tag_info in hashtags:
            tag = tag_info['text']
            if tag in self.hashtag_list:
                tags.append(tag)

        if len(tags) >= 1:
            return tags[0]
        else:
            return False

    def tweet_mention_formatter(self, screen_name, user_mentions):
        if len(user_mentions) <= 1:
            return f'@{screen_name}'
        else:
            return ' '.join(
                ['@{0}'.format(x) for x in user_mentions['screen_name']])

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
        chem_str = re.sub(r'#\w+', '', command)
        chem_str = chem_str.replace('\n', '').replace('\r', '').strip()
        return chem_str

    def reply_iupac_convert_error(self, iupac, id, screen_name, user_mentions):
        """Tweet for reply about iupac convert error."""
        print('[BOT] IUPAC conversion error')
        tweet = self.tweet_mention_formatter(screen_name, user_mentions)
        return self.tweet_error_message(
            tweet + 'すまない。私の化学目録に「{0}」という文字は無かった。'
            .format(iupac), id)

    def reply_with_png(self, smi,
                       id, screen_name, user_mentions, option_d=None,
                       descriptor_type='SMILES', with_smiles=False):
        """Tweet chem graph to user"""
        print('[SMILES]: {0}'.format(smi))
        tweet = self.tweet_mention_formatter(screen_name, user_mentions)

        if smi == '':
            tweet += (
                '{0}を入力し忘れていないか確認してもらえないだろうか。'
                .format(descriptor_type))
            return self.tweet_error_message(tweet, id)

        if self.check_ascii(smi):
            encoder = chem_bot.SmilesEncoder(smi)
        else:
            tweet += ' おや、SMILESに使えない文字が入っているようだ。'
            return self.tweet_error_message(tweet, id)

        if encoder.mol is None:
            print('Encoding error for [ {0} ]'.format(smi))
            tweet += (
                ' すまない。この{0}は上手く変換できなかったようだ。'
                .format(descriptor_type))
            tweet += '"{0}"'.format(smi)
            return self.tweet_error_message(tweet, id)

        png_binary = encoder.to_png()
        image = tempfile.TemporaryFile()
        image.write(png_binary)
        image.seek(0)

        if with_smiles:
            tweet = '{0} "{1}"'.format(tweet, smi)

        try:
            response = self.api.upload_media(media=image)
            self.api.update_status(
                status=self.add_hashtag(tweet),
                media_ids=[response['media_id']],
                in_reply_to_status_id=id,
            )
        except Exception as e:
            print(e)
        return True

    def tweet_error_message(self, tweet, s_id):
            try:
                self.api.update_status(
                    status=self.string_trimmer(tweet),
                    in_reply_to_status_id=s_id)
            except TwythonError as e:
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
        if len(line) + self.reply_hashtag_len + 1 > 140:
            return (
                line[:- self.reply_hashtag_len + 4]
                + '... ' + self.reply_hashtag)
        else:
            return line + ' ' + self.reply_hashtag

    def reply_for_iupac(self, iupac, data):
        if self.check_ascii(iupac):
            print(f'[IUPAC]: {iupac}')
            smi, error = chem_bot.util.converter.iupac_to_smiles(
                iupac, self.opsin)
        else:
            smi = ''

        if smi == '':
            self.reply_iupac_convert_error(
                iupac=iupac,
                id=data['id'],
                screen_name=data['user']['screen_name'],
                user_mentions=data['entities']['user_mentions'],
            )
            return print('[BOT] Error: {0}'.format(error))

        self.reply_with_png(
            smi=smi,
            id=data['id'],
            screen_name=data['user']['screen_name'],
            user_mentions=data['entities']['user_mentions'],
            descriptor_type='IUPAC NAME',
            with_smiles=True)
        print('[BOT] continue streaming...')

    def reply_for_smiles(self, smi, data):
        self.reply_with_png(
            smi=smi,
            id=data['id'],
            screen_name=data['user']['screen_name'],
            user_mentions=data['entities']['user_mentions'],
            descriptor_type='SMILES',
            with_smiles=True)
        print('[BOT] continue streaming...')

    def on_error(self, status_code, data):
        print(status_code)

    def on_success(self, data):
        if 'text' in data:
            hashtags = data['entities']['hashtags']
            chem_str_type = self.check_hashtags(hashtags)
            text = data['text']
            # import pprint
            # pprint.pprint(data, indent=2)
        else:
            return

        if chem_str_type:
            chem_str = self.parse_tweet_command(text)
        else:
            print(f'invalid hashtags: {hashtags}, continue...')
            return

        if chem_str_type == 'iupac':
            try:
                self.reply_for_iupac(chem_str, data)
            except Exception:
                traceback.print_exc()

        if chem_str_type == 'smiles':
            try:
                self.reply_for_smiles(chem_str, data)
            except Exception:
                traceback.print_exc()
