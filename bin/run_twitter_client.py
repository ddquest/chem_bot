#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from chem_bot import twitter as T


def _main():
    config = T.Config()
    config.load()
    api = T.oauth(config)
    stream = T.Streamer(api, config)
    stream.statuses.filter(track=config.query, follow=config.filter_follow)
    # stream.statuses.filter(track='twitter')


if __name__ == '__main__':
    _main()
