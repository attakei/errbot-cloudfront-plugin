import textwrap
from errbot import BotPlugin, botcmd, arg_botcmd, webhook


class Cloudfront(BotPlugin):
    """
    Control CloudFront
    """
    def _not_configured(self):
        message = """\
            This plugin is until not configured.
            Please call `!plugin config cloudfront` to read format,
            And set your configurations.
            """
        return textwrap.dedent(message)

    def get_configuration_template(self):
        """
        Defines the configuration structure this plugin supports

        You should delete it if your plugin doesn't use any configuration like this
        """
        return {
            'access_id': None,
            'secret_key': None,
        }

    @botcmd(split_args_with=None)
    def cloudfront_list(self, message, args):
        """Display knwon CloudFront edges"""
        # if not self.config:
        #     return self._not_configured()
        # if not self.config.get('access_id', None) \
        #     or not self.config.get('secret_key', None):
        #     return self._not_configured()
        if not self.config \
                or not self.config.get('access_id', None) \
                or not self.config.get('secret_key', None):
            return self._not_configured()
        return "Example"
