import os
import shutil

import yaml
import jinja2

THIS_FOLDER = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
TEMPLATE_FOLDER = THIS_FOLDER + '/templates'
TEMPLATE_MKDOCS_YAML = TEMPLATE_FOLDER + '/mkdocs.yml'
BIGFUNCTIONS_FOLDER = 'bigfunctions'
TABLES_FOLDER = 'data'
BOOKMARKLET_DOC = open(f'{TEMPLATE_FOLDER}/bookmarklet_doc.md', encoding='utf-8').read()

if not os.path.isfile('README.md'):
    print('INFO: CREATING A README.md FILE IN CURRENT DIRECTORY WHICH WILL BE THE ROOT CONTENT OF THE WEBSITE')
    open('README.md', 'w', encoding='utf-8').write('# Hello from README!')

if not os.path.isdir('site'):
    print('INFO: CREATING site FOLDER in CURRENT DIRECTORY WHICH WILL CONTAIN WEBSITE MATERIAL...')
    shutil.copytree(TEMPLATE_FOLDER + '/site', 'site')

if not os.path.isdir('bigfunctions'):
    os.makedirs('bigfunctions')

if not os.path.isdir('data'):
    os.makedirs('data')

def get_bigfunctions():
    bigfunctions = []
    for filename in sorted(os.listdir(BIGFUNCTIONS_FOLDER)):
        if not filename.endswith('.yaml'):
            continue
        conf = yaml.safe_load(open(f'{BIGFUNCTIONS_FOLDER}/{filename}', encoding='utf-8').read())
        assert isinstance(conf, dict), f'Could not load yaml config of bigfunction `{filename}`'
        name = filename.replace('.yaml', '')
        conf['name'] = name
        if 'template' in conf or conf.get('output', {}).get('name') == 'html':
            conf['description'] += '\n\n' + BOOKMARKLET_DOC
        bigfunctions.append(conf)
    return bigfunctions


def get_tables():
    tables = []
    for filename in sorted(os.listdir(TABLES_FOLDER)):
        if not filename.endswith('.yaml'):
            continue
        conf = yaml.safe_load(open(f'{TABLES_FOLDER}/{filename}', encoding='utf-8').read())
        assert isinstance(conf, dict), f'Could not load yaml config of table `{filename}`'
        name = filename.replace('.yaml', '')
        conf['name'] = name
        tables.append(conf)
    return tables


BIGFUNCTIONS = get_bigfunctions()
TABLES = get_tables()


CONF = yaml.safe_load(open(f'site/mkdocs.yml', encoding='utf-8').read())



class BasePage:

    name = ''

    def __init__(self, project, dataset):
        self.project = project
        self.datasets = [f'{project}.{d.strip()}' for d in dataset.split(',')]
        if len(self.datasets) > 3:
            self.datasets = self.datasets[:3] + [f'{project}.your_region2']

    def generate(self):
        context = self.get_context()
        context['project'] = self.project
        context['datasets'] = self.datasets
        template = f'{TEMPLATE_FOLDER}/{self.name}.md'
        content = jinja2.Template(open(template, encoding='utf-8').read()).render(**context)
        with open(f'{self.name}/README.md', 'w', encoding='utf-8') as out:
            out.write(content)

    def get_context(self):
        raise NotImplementedError()


class BigFunctionsPage(BasePage):

    name = 'bigfunctions'

    def get_context(self):
        categories = CONF['bigfunctions_categories']
        for category in categories:
            category['bigfunctions'] = [bigfunction for bigfunction in BIGFUNCTIONS if bigfunction['category'] == category['name']]
        categories = [category for category in categories if category['bigfunctions']]
        return {
            'repo_url': CONF['repo_url'],
            'categories': categories,
        }

class TablesPage(BasePage):

    name = 'data'

    def get_context(self):
        return {
            'tables': TABLES,
            'repo_url': CONF['repo_url'],
        }


def generate_doc(project, dataset):
    BigFunctionsPage(project, dataset).generate()
    TablesPage(project, dataset).generate()


if __name__ == '__main__':
    generate_doc('bigfunctions', 'eu,us,europe_west1,foo')