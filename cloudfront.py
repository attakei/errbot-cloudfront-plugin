import textwrap
from errbot import BotPlugin, botcmd
import boto3


class Cloudfront(BotPlugin):
    """
    Control CloudFront
    """
    def _not_configured(self):
        message = """
            This plugin is until not configured.
            Please call `!plugin config cloudfront` to read format,
            And set your configurations.
            """
        return textwrap.dedent(message)

    def _init_client(self):
        """Return CloudFront client by boto3.

        This client is configuret by plugin configuration.
        """
        return boto3.client(
            'cloudfront',
            aws_access_key_id=self.config['access_id'],
            aws_secret_access_key=self.config['secret_key'],
        )

    def get_configuration_template(self):
        """
        Defines the configuration structure this plugin supports.
        """
        config = {
            'access_id': None,
            'secret_key': None,
        }
        return config

    @botcmd(split_args_with=None)
    def cloudfront_list(self, message, args):
        """Display knwon CloudFront edges."""
        if not self.config \
                or not self.config.get('access_id', None) \
                or not self.config.get('secret_key', None):
            return self._not_configured()
        client = self._init_client()
        result = client.list_distributions()
        if 'DistributionList' not in result:
            return "Client error"
        result = result['DistributionList']
        header = "Display {} items of distribution".format(result['Quantity'])
        if result['Quantity'] == 0:
            return header
        dists = "\n".join([
            "* {}: {}".format(
                dist['Id'],
                dist['Origins']['Items'][0]['DomainName'])
            for dist in result['Items']
        ])
        return "{}\n\n{}".format(header, dists)
