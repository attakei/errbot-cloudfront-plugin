import datetime
import textwrap
from errbot import BotPlugin, botcmd, arg_botcmd
import boto3
# TODO: There are workaround import for https://github.com/errbotio/errbot/issues/1119
import re
from errbot.version import VERSION as ERRBOT_VERSION
from errbot.botplugin import BotPluginBase



AUTO_CHECK_INTERVAL = 60 * 1


class Cloudfront(BotPlugin):
    """
    Control CloudFront
    """
    def _not_configured(self):
        message = """
            This plugin is until not configured.
            Please call `{}plugin config cloudfront` to read format,
            And set your configurations.
            """
        return textwrap.dedent(message).format(self.bot_config.BOT_PREFIX)

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

    @arg_botcmd('origin', type=str)
    def cloudfront_create(self, message, origin):
        """Create new distribution."""
        client = self._init_client()
        result = client.create_distribution(DistributionConfig={
            'CallerReference': 'new_distribution-{}'.format(
                datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
            ),
            'Origins': {
                'Quantity': 1,
                'Items': [
                    {
                        'Id': 'Default',
                        'DomainName': origin,
                        'CustomOriginConfig': {
                            'HTTPPort': 80,
                            'HTTPSPort': 443,
                            'OriginProtocolPolicy': 'match-viewer'
                        }
                    }
                ]
            },
            'DefaultCacheBehavior': {
                'TargetOriginId': 'Default', 
                'ForwardedValues': {
                    'QueryString': False,
                    'Cookies': {'Forward': 'all'}
                },
                'TrustedSigners': {
                    'Enabled': False,
                    'Quantity': 0,
                },
                'ViewerProtocolPolicy': 'allow-all',
                'MinTTL': 0,
            },
            'Comment': origin,
            'Enabled': True,
        })
        distribution_id = result['Distribution']['Id']
        self.start_poller(
            interval=AUTO_CHECK_INTERVAL,
            method=self._motnitor_distribution,
            args=(distribution_id, str(message.frm))
        )
        message = """
            Start creating new distribution {}
            Call `{}cloudfront info {}` to check invaliation status
            """.format(
                origin,
                self.bot_config.BOT_PREFIX,
                distribution_id,
            )
        return textwrap.dedent(message)

    @arg_botcmd('distribution_id', type=str)
    def cloudfront_info(self, message, distribution_id):
        """Check status of specified invalidation."""
        if not self.config \
                or not self.config.get('access_id', None) \
                or not self.config.get('secret_key', None):
            return self._not_configured()
        client = self._init_client()
        result = client.get_distribution(Id=distribution_id)
        distribution = result['Distribution']
        message = """
        Distribution: {}
        - comment: {}
        - status: {}
        - endpoint: {}
        """.format(
            distribution['Id'],
            distribution['DistributionConfig']['Comment'],
            distribution['Status'],
            distribution['DomainName'],
        )
        return textwrap.dedent(message)

    def _motnitor_distribution(self, distibution_id, msg_from):
        """Check invalidation status(polling)."""
        client = self._init_client()
        result = client.get_distribution(Id=distibution_id)
        distribution = result['Distribution']
        status = distribution['Status']
        if status != 'Deployed':
            return
        if '/' in msg_from:
            send_id, memtion = msg_from.split('/')
            memtion = '@' + memtion
        else:
            send_id = memtion = msg_from
        message = """
        {} Distribution<{}> is ready!
        - endpoint: {}
        """.format(
            memtion,
            distribution['Id'],
            distribution['DomainName'],
        )
        send_to = self.build_identifier(send_id)
        self.send(send_to, textwrap.dedent(message))
        self.stop_poller(
            self._motnitor_distribution,
            (distibution_id, msg_from)
        )

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
        invalidation_id = result['Invalidation']['Id']
        self.start_poller(
            interval=AUTO_CHECK_INTERVAL,
            method=self._motnitor_invalidation,
            args=(distribution_id, invalidation_id, str(message.frm))
        )
        message = """
            Start invalidation for {}
            Call `{}cloudfront status {} {}` to check invaliation status
            """.format(
                distribution_id,
                self.bot_config.BOT_PREFIX,
                distribution_id,
                invalidation_id,
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

    def _motnitor_invalidation(self, distibution, invaliation, msg_from):
        """Check invalidation status(polling)."""
        client = self._init_client()
        result = client.get_invalidation(
            DistributionId=distibution, Id=invaliation)
        status = result['Invalidation']['Status']
        if status != 'Completed':
            return
        if '/' in msg_from:
            send_id, memtion = msg_from.split('/')
            memtion = '@' + memtion
        else:
            send_id = memtion = msg_from
        message = "{} Invalidation<{}> is finished!".format(
            memtion, invaliation
        )
        send_to = self.build_identifier(send_id)
        self.send(send_to, message)
        self.stop_poller(
            method=self._motnitor_invalidation,
            args=(distibution, invaliation, msg_from)
        )

    # TODO: There are workaround import for https://github.com/errbotio/errbot/issues/1119
    def stop_poller(self, method, args=None, kwargs=None):
        if re.match('^5\.1\.[0-9]+$', ERRBOT_VERSION):
            BotPluginBase.stop_poller(
                self, method, args=args, kwargs=kwargs)
        else:
            super().stop_poller(
                method, args=args, kwargs=kwargs)
