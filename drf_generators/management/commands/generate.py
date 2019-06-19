import sys

from django.core.management.base import AppCommand, CommandError
from drf_generators.generators import *
import django


class Command(AppCommand):
    help = 'Generates DRF API Views and Serializers for a Django app'

    args = "[appname ...]"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('-f', '--format', dest='format',
                            default='viewset',
                            help='view format (default: viewset)'),

        parser.add_argument('-d', '--depth', dest='depth', default=0,
                            help='serialization depth'),

        parser.add_argument('--force', dest='force', action='store_true',
                            help='force overwrite files'),

        parser.add_argument('--serializers', dest='serializers',
                            action='store_true',
                            help='generate serializers only'),

        parser.add_argument('--views', dest='views', action='store_true',
                            help='generate views only'),

        parser.add_argument('--urls', dest='urls', action='store_true',
                            help='generate urls only'),

        parser.add_argument('--models', dest='models', default='', 
                            help='comma separated list of models to use'),

        parser.add_argument('--serializers-file', dest='serializer-file', default='serializers.py',
                            help='output file for serializers'),

        parser.add_argument('--view-file', dest='view-file', default='views.py', 
                            help='output file for views'),

        parser.add_argument('--url-file', dest='url-file', default='urls.py', 
                            help='output file for urls'),

    def handle_app_config(self, app_config, **options):
        if app_config.models_module is None:
            raise CommandError('You must provide an app to generate an API')

        if sys.version_info[0] != 3 or sys.version_info[1] < 4:
            raise CommandError('Python 3.4 or newer is required')

        if django.VERSION[1] == 7:
            force = options['force'] if 'force' in options else False
            format = options['format'] if 'format' in options else None
            depth = options['depth'] if 'depth' in format else 0
            if 'serializers' in options:
                serializers = options['serializers']
            else:
                serializers = False
            views = options['views'] if 'views' in options else False
            urls = options['urls'] if 'urls' in options else False
            models = [m for m in options['models'].split(',')  if m] if 'models' in options else []
            serializer_file = options['serializer-file'] if 'serializer-file' in options else 'serializers.py'
            view_file = options['view-file'] if 'view-file' in options else 'views.py'
            url_file = options['url-file'] if 'url-file' in options else 'urls.py'

        elif django.VERSION[1] >= 8 or django.VERSION[0] == 2:
            force = options['force']
            format = options['format']
            depth = options['depth']
            serializers = options['serializers']
            views = options['views']
            urls = options['urls']
            models = [m for m in options['models'].split(',') if m]
            serializer_file = options['serializer-file']
            view_file = options['view-file']
            url_file = options['url-file']
        else:
            raise CommandError('You must be using Django 1.7, 1.8 or 1.9')

        if format == 'viewset':
            generator = ViewSetGenerator(app_config, force, models)
        elif format == 'apiview':
            generator = APIViewGenerator(app_config, force, models)
        elif format == 'function':
            generator = FunctionViewGenerator(app_config, force, models)
        elif format == 'modelviewset':
            generator = ModelViewSetGenerator(app_config, force, models)
        else:
            message = '\'%s\' is not a valid format. ' % options['format']
            message += '(viewset, modelviewset, apiview, function)'
            raise CommandError(message)

        if serializers:
            result = generator.generate_serializers(depth, serializer_file)
        elif views:
            result = generator.generate_views(view_file)
        elif urls:
            result = generator.generate_urls(url_file)
        else:
            result = generator.generate_serializers(depth) + '\n'
            result += generator.generate_views() + '\n'
            result += generator.generate_urls()

        print(result)
