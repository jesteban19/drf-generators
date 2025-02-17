from django.template import Template, Context
import os.path

from drf_generators.templates.serializer import SERIALIZER
from drf_generators.templates.apiview import API_URL, API_VIEW
from drf_generators.templates.viewset import VIEW_SET_URL, VIEW_SET_VIEW
from drf_generators.templates.function import FUNCTION_URL, FUNCTION_VIEW
from drf_generators.templates.modelviewset import MODEL_URL, MODEL_VIEW

__all__ = ['BaseGenerator', 'APIViewGenerator', 'ViewSetGenerator',
           'FunctionViewGenerator', 'ModelViewSetGenerator']


class BaseGenerator(object):

    def __init__(self, app_config, force, models):
        self.app_config = app_config
        self.force = force
        self.app = app_config.models_module
        self.name = app_config.name
        self.serializer_template = Template(SERIALIZER)
        self.models = self.get_model_names(models)
        self.serializers = self.get_serializer_names()
        #self.view_template = Template(API_VIEW)
        #self.url_template = Template(API_URL)

    def generate_serializers(self, depth, filename):
        content = self.serializer_content(depth)
        if self.write_file(content, filename):
            return '  - writing %s' % filename
        else:
            return 'Serializer generation cancelled'

    def generate_views(self, filename):
        content = self.view_content()
        if self.write_file(content, filename):
            return '  - writing %s' % filename
        else:
            return 'View generation cancelled'

    def generate_urls(self, filename):
        content = self.url_content()
        if self.write_file(content, filename):
            return '  - writing %s' % filename
        else:
            return 'Url generation cancelled'

    def serializer_content(self, depth):
        context = Context({'app': self.name, 'models': self.models,
                           'depth': depth})
        return self.serializer_template.render(context)

    def view_content(self):
        context = Context({'app': self.name, 'models': self.models,
                           'serializers': self.serializers})
        return self.view_template.render(context)

    def url_content(self):
        context = Context({'app': self.name, 'models': self.models})
        return self.url_template.render(context)

    def get_model_names(self, models):
        if models:
            return [m.__name__ for m in self.app_config.get_models() if m.__name__ in models]
        else:
            return [m.__name__ for m in self.app_config.get_models()]

    def get_serializer_names(self):
        return [m + 'Serializer' for m in self.models]

    def write_file(self, content, filename):
        name = os.path.join(os.path.dirname(self.app.__file__), filename)
        if os.path.exists(name) and not self.force:
            msg = "Are you sure you want to overwrite %s? (y/n): " % filename
            prompt = input  # python3
            response = prompt(msg)
            if response != "y":
                return False
        new_file = open(name, 'w+')
        new_file.write(content)
        new_file.close()
        return True


class APIViewGenerator(BaseGenerator):

    def __init__(self, app_config, force, models):
        self.view_template = Template(API_VIEW)
        self.url_template = Template(API_URL)
        super(APIViewGenerator, self).__init__(app_config, force, models)


class ViewSetGenerator(BaseGenerator):

    def __init__(self, app_config, force, models):
        self.view_template = Template(VIEW_SET_VIEW)
        self.url_template = Template(VIEW_SET_URL)
        super(ViewSetGenerator, self).__init__(app_config, force, models)


class FunctionViewGenerator(BaseGenerator):

    def __init__(self, app_config, force, models):
        self.view_template = Template(FUNCTION_VIEW)
        self.url_template = Template(FUNCTION_URL)
        super(FunctionViewGenerator, self).__init__(app_config, force, models)


class ModelViewSetGenerator(BaseGenerator):

    def __init__(self, app_config, force, models):
        self.view_template = Template(MODEL_VIEW)
        self.url_template = Template(MODEL_URL)
        super(ModelViewSetGenerator, self).__init__(app_config, force, models)
