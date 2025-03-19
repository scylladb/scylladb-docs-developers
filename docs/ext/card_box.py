from docutils import nodes
from docutils.parsers.rst import Directive, directives

class CardBoxDirective(Directive):
    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'link': directives.unchanged,
        'title': directives.unchanged,
        'image': directives.path,
        'description': directives.unchanged,
    }

    def run(self):
        link = self.options.get('link', '')
        title = self.options.get('title', '')
        image = self.options.get('image', '')
        description = self.options.get('description', '')

        image_html = f'<img src="{image}" class="btn-icon">' if image else ''
        dark_image_html = f'<img src="{image.replace(".svg", "_white.svg")}" class="btn-icon">' if image else ''
        description_html = f'<div class="description">{description}</div>' if description else ''

        html = f'''
<a class="card-box" href="{link}">
    <div class="light-mode">
        {image_html}
        <span class="title">{title}</span>
    </div>
    <div class="dark-mode">
        {dark_image_html}
        <span class="title">{title}</span>
    </div>
    {description_html}
</a>
'''
        raw_node = nodes.raw('', html, format='html')
        return [raw_node]

def setup(app):
    app.add_directive('card-box', CardBoxDirective)
    app.add_config_value('card_box_config', {}, 'env')
    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }