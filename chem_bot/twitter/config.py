import toml

__CONFIG_FILE__ = '.twitter.toml'


class Config(object):

    def __init__(self, config_file=__CONFIG_FILE__):
        self.config_file = config_file

    def load(self):
        with open(self.config_file, 'r') as f:
            data = toml.load(f)
            self.bot_id = data['general']['bot_id']
            self.opsin = data['general']['opsin']
            self.hashtag = data['general']['hashtag']
            self.viewer_url = data['general']['viewer_url']
            self.consumer_key = data['tokens']['consumer_key']
            self.consumer_secret = data['tokens']['consumer_secret']
            self.oauth_token = data['tokens']['oauth_token']
            self.oauth_token_secret = data['tokens']['oauth_token_secret']
            self.query = data['filter']['query']
            self.filter_follow = data['filter']['follow']
            self.filter_hashtags = data['filter']['hashtags']
            self.data = data
            return self.data

    def save(self):
        with open(self.config_file, 'w') as f:
            self.data['general']['bot_id'] = self.bot_id
            self.data['general']['opsin'] = self.opsin
            self.data['general']['hashtag'] = self.hashtag
            self.data['tokens']['consumer_key'] = self.consumer_key
            self.data['tokens']['consumer_secret'] = self.consumer_secret
            self.data['tokens']['oauth_token'] = self.oauth_token
            self.data['tokens']['oauth_token_secret'] = self.oauth_token_secret
            self.data['filter']['query'] = self.query
            self.data['filter']['follow'] = self.filter_follow
            self.data['filter']['hashtags'] = self.filter_hashtags
            toml.dump(self.data, f)
