import datetime
import textwrap
from errbot import BotPlugin, botcmd, arg_botcmd
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

    @arg_botcmd('distribution_id', type=str)
    def cloudfront_invalidate(self, message, distribution_id):
        """Invalidate all caches from specified distribution."""
        if not self.config \
                or not self.config.get('access_id', None) \
                or not self.config.get('secret_key', None):
            return self._not_configured()
        client = self._init_client()
        result = client.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'CallerReference': '{}-{}'.format(
                    distribution_id,
                    datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
                ),
                'Paths': {
                    'Quantity': 1,
                    'Items': ['/*'],
                }
            })
        invalidate_id = result['Invalidation']['Id']
        message = """
            Start invalidation for {}
            Call `!cloudfront status {} {}` to check invaliation status
            """.format(
                distribution_id, distribution_id, invalidate_id
            )
        return textwrap.dedent(message)

    @arg_botcmd('invalidation_id', type=str)
    @arg_botcmd('distribution_id', type=str)
    def cloudfront_status(self, message, distribution_id, invalidation_id):
        """Check status of specified invalidation."""
        if not self.config \
                or not self.config.get('access_id', None) \
                or not self.config.get('secret_key', None):
            return self._not_configured()
        client = self._init_client()
        result = client.get_invalidation(
            DistributionId=distribution_id, Id=invalidation_id)
        return "Status is '{}'".format(result['Invalidation']['Status'])
