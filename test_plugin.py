from unittest.mock import patch

pytest_plugins = ["errbot.backends.test"]

extra_plugin_dir = '.'


def inject_dummy_conf(bot):
    bot.push_message('!plugin config cloudfront '\
        '{"access_id":"1","secret_key":"1"}')
    bot.pop_message()


def test_unconfigured(testbot):
    testbot.push_message('!cloudfront list')
    assert 'This plugin is until not configured' \
        in testbot.pop_message()


def test_unconfigured_bot_prefix(testbot):
    testbot.bot_config.BOT_PREFIX = '!!'
    testbot.push_message('!!cloudfront list')
    assert '!!plugin config cloudfront' \
        in testbot.pop_message()


def test_create_message(testbot):
    with patch('boto3.client') as Client:
        client = Client.return_value
        client.create_distribution.return_value = {
            'Distribution': {
                'Id': 'ABCDEFG'
            }}
        inject_dummy_conf(testbot)
        testbot.push_message('!cloudfront create example.com')
        message = testbot.pop_message()
        assert 'Start creating new distribution' in message
        assert '!cloudfront status ABCDEFG' in message


def test_status_invalidation(testbot):
    with patch('boto3.client') as Client:
        client = Client.return_value
        client.get_invalidation.return_value = {
            'Invalidation': {
                'Id': 'GHIJKL',
                'Status': 'Completed',
            }}
        inject_dummy_conf(testbot)
        testbot.push_message('!cloudfront status ABCDEF GHIJKL')
        message = testbot.pop_message()
        assert 'Status is' in message
