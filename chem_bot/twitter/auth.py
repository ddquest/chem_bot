from twython import Twython
from twython.exceptions import TwythonAuthError, TwythonRateLimitError


def oauth(config):
    if config.oauth_token == '' or config.oauth_token_secret == '':
        try:
            t = Twython(config.consumer_key, config.consumer_secret)
            print('Get authorized PIN code from url.')
            auth = t.get_authentication_tokens()
            t = Twython(
                config.consumer_key,
                config.consumer_secret,
                auth['oauth_token'],
                auth['oauth_token_secret'],
            )
            print(auth['auth_url'])
            final_auth = t.get_authorized_tokens(input('PIN: '))
            config.oauth_token = final_auth['oauth_token']
            config.oauth_token_secret = final_auth['oauth_token_secret']
            config.save()
            return t
        except TwythonAuthError as e:
            raise RuntimeError(
                'invalid consumer_key and/or consumer_key_secret')
        except TwythonRateLimitError:
            raise RuntimeError('Reached to API access limit')

    try:
        t = Twython(
            config.consumer_key,
            config.consumer_secret,
            config.oauth_token,
            config.oauth_token_secret,
        )

        auth = t.get_authentication_tokens()
        confirme = auth['oauth_callback_confirmed']
        print(f'oauth confirmation: {confirme}')
        return t
    except TwythonAuthError as e:
        raise RuntimeError('invalid keys')
    except TwythonRateLimitError:
        raise RuntimeError('Reached to API access limit')
