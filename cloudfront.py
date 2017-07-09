from errbot import BotPlugin, botcmd, arg_botcmd, webhook


class Cloudfront(BotPlugin):
    """
    Control CloudFront
    """

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
        # TODO: Implement it
        return "Example"
