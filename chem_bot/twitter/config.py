import toml


__CONFIG_FILE__ = '.twitter.toml'


class Config(object):

    def __init__(self, config_file=__CONFIG_FILE__):
        self.config_file = config_file

    def load(self):
        with open(self.config_file, 'r') as f:
            data = toml.load(f)
            self.bot_id = data['general']['bot_id']
            self.iupac_prefix = data['general']['iupac_prefix']
            self.smiles_prefix = data['general']['smiles_prefix']
            self.opsin = data['general']['opsin']
            self.hashtag = data['general']['hashtag']
            self.consumer_key = data['tokens']['consumer_key']
            self.consumer_secret = data['tokens']['consumer_secret']
            self.access_token = data['tokens']['access_token']
            self.access_token_secret = data['tokens']['access_token_secret']
            self.query = data['filter']['query']
            self.filter_follow = data['filter']['follow']
            self.filter_hashtags = data['filter']['hashtags']
            self.data = data
            return self.data

    def save(self):
        with open(self.config_file, 'w') as f:
            toml.dump(self.data, f)
