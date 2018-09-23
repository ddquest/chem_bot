from twython import Twython
from twython.exceptions import TwythonAuthError, TwythonRateLimitError


def oauth(config):
    if config.access_token == '' or config.access_token_secret == '':
        try:
            t = Twython(config.consumer_key, config.consumer_secret)
            print('Get authorized PIN code from url.')
            print(t.authenticate_url())
            auth_tokens = t.get_authentication_tokens(input('PIN: '))
            config.access_token = auth_tokens['oauth_token']
            config.access_token_secret = auth_tokens['oauth_token_secret']
            config.save()
        except TwythonAuthError as e:
            raise RuntimeError(
                'invalid consumer_key and/or consumer_key_secret')
        except TwythonRateLimitError:
            raise RuntimeError('Reached to API access limit')

    try:
        t = Twython(
            config.consumer_key,
            config.consumer_secret,
            config.access_token,
            config.access_token_secret,
        )

        auth = t.get_authentication_tokens()
        confirme = auth['oauth_callback_confirmed']
        print(f'oauth confirmation: {confirme}')
        return t
    except TwythonAuthError as e:
        raise RuntimeError('invalid keys')
    except TwythonRateLimitError:
        raise RuntimeError('Reached to API access limit')
