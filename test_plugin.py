pytest_plugins = ["errbot.backends.test"]

extra_plugin_dir = '.'


def test_unconfigured(testbot):
    testbot.push_message('!cloudfront list')
    assert 'This plugin is until not configured' \
        in testbot.pop_message()


def test_unconfigured_bot_prefix(testbot):
    testbot.bot_config.BOT_PREFIX = '!!'
    testbot.push_message('!!cloudfront list')
    assert '!!plugin config cloudfront' \
        in testbot.pop_message()
