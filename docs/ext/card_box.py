from docutils import nodes
from docutils.parsers.rst import Directive, directives

class CardBoxDirective(Directive):
    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'link': directives.unchanged,
        'text': directives.unchanged,
        'image': directives.path,
    }

    def run(self):
        link = self.options.get('link', '')
        text = self.options.get('text', '')
        image = self.options.get('image', '')

        image_html = f'<img src="{image}" class="btn-icon">' if image else ''
        dark_image_html = f'<img src="{image.replace(".svg", "_white.svg")}" class="btn-icon">' if image else ''

        html = f'''
<a class="card-box" href="{link}">
    <span class="light-mode">{image_html}</span>
    <span class="dark-mode">{dark_image_html}</span>
    {text}
</a>
'''
        raw_node = nodes.raw('', html, format='html')
        return [raw_node]

def setup(app):
    app.add_directive('card-box', CardBoxDirective)