import os
import re
from html import escape

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.util.osutil import relative_uri


class simulation_card(nodes.General, nodes.Element):
    pass


class simulation(nodes.General, nodes.Element):
    pass


DEMOS_DIR = os.path.join('_extra', 'demos')


# -- CSS scoping
#
# The simulation renders in a shadow root. In a shadow root, ":root", "html"
# and "body" do not match, so the rules that use them are changed to match the
# shadow host (":host") and the element that replaces <body> (".sim-body").

# At-rules that contain rules. The content of all other at-rules (for example,
# @font-face and @keyframes) does not change.
_NESTING_AT_RULES = ('@media', '@supports', '@layer', '@container', '@document')


def _split_selectors(prelude):
    parts, depth, start = [], 0, 0
    for i, ch in enumerate(prelude):
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
        elif ch == ',' and depth == 0:
            parts.append(prelude[start:i])
            start = i + 1
    parts.append(prelude[start:])
    return [p.strip() for p in parts if p.strip()]


def _scope_selector(sel):
    m = re.match(r'(?::root|html)((?:\[[^\]]+\])*)(?=$|[\s>+~.:#])', sel)
    if not m:
        m = re.match(r'((?:\[[^\]]+\])+)(?=$|[\s>+~])', sel)
    if m:
        attrs = m.group(1)
        sel = (f':host({attrs})' if attrs else ':host') + sel[m.end():]
    return re.sub(r'(^|[\s>+~])body(?=$|[\s>+~.:#\[])', r'\1.sim-body', sel)


def _scope_prelude(prelude):
    prelude = re.sub(r'/\*.*?\*/', '', prelude, flags=re.S)
    return ', '.join(_scope_selector(s) for s in _split_selectors(prelude))


def scope_css(css):
    out, stack, start, i, n = [], [], 0, 0, len(css)
    while i < n:
        ch = css[i]
        if css.startswith('/*', i):
            end = css.find('*/', i + 2)
            i = n if end < 0 else end + 2
            continue
        if ch in '"\'':
            j = i + 1
            while j < n and css[j] != ch:
                j += 2 if css[j] == '\\' else 1
            i = j + 1
            continue
        if ch == '{':
            prelude = css[start:i]
            if stack and stack[-1] in ('decl', 'raw'):
                stack.append(stack[-1])
                out.append(prelude + '{')
            elif prelude.strip().startswith('@'):
                nesting = re.sub(r'/\*.*?\*/', '', prelude, flags=re.S).strip().startswith(_NESTING_AT_RULES)
                stack.append('nest' if nesting else 'raw')
                out.append(prelude + '{')
            else:
                stack.append('decl')
                out.append(_scope_prelude(prelude) + ' {')
            start = i + 1
        elif ch == '}':
            out.append(css[start:i + 1])
            if stack:
                stack.pop()
            start = i + 1
        elif ch == ';' and (not stack or stack[-1] == 'nest'):
            out.append(css[start:i + 1])
            start = i + 1
        i += 1
    out.append(css[start:])
    return ''.join(out)


# -- Simulation page parsing

def _stylesheets(head):
    links = re.findall(r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*>', head)
    hrefs = (re.search(r'href=["\']([^"\']+)["\']', link) for link in links)
    return [h.group(1) for h in hrefs if h and not re.match(r'[a-z]+:|/', h.group(1))]


def _scoped_name(href):
    root, ext = os.path.splitext(href)
    return f'{root}.scoped{ext}'


def parse_simulation(path):
    with open(path, encoding='utf-8') as f:
        page = f.read()
    head = page[:page.find('<body')]
    body_tag = re.search(r'<body([^>]*)>', page)
    body = page[body_tag.end():page.rfind('</body>')]
    body_class = re.search(r'class=["\']([^"\']*)["\']', body_tag.group(1))
    script_re = re.compile(r'<script\b[^>]*>(.*?)</script>', re.S)
    return {
        'stylesheets': [_scoped_name(h) for h in _stylesheets(head)],
        'style': scope_css('\n'.join(re.findall(r'<style\b[^>]*>(.*?)</style>', head, re.S))),
        'body': script_re.sub('', body),
        'body_class': body_class.group(1) if body_class else '',
        # Only the scripts in <body>. The theme script in <head> is replaced by
        # simulations.js, which makes the simulation follow the docs theme.
        'script': '\n;\n'.join(script_re.findall(body)),
    }


def _uri(translator, path):
    """Return the URI of an output file (for example, a file in html_extra_path),
    relative to the current page, for the html and dirhtml builders."""
    builder = translator.builder
    return relative_uri(builder.get_target_uri(builder.current_docname), path)


class SimulationCardDirective(Directive):
    """Card with a screenshot that links to a simulation page."""
    has_content = False
    option_spec = {
        'title': directives.unchanged_required,
        'doc': directives.unchanged_required,
        'image': directives.unchanged_required,
        'description': directives.unchanged,
    }

    def run(self):
        env = self.state.document.settings.env
        doc = directives.path(self.options['doc'])
        # Resolve the target document relative to the current document.
        base = env.docname.rsplit('/', 1)[0] + '/' if '/' in env.docname else ''
        node = simulation_card()
        node['title'] = self.options['title']
        node['doc'] = doc.lstrip('/') if doc.startswith('/') else base + doc
        node['image'] = self.options['image'].lstrip('/')
        node['description'] = self.options.get('description', '')
        return [node]


class SimulationDirective(Directive):
    """Simulation from docs/source/_extra/demos/<name>, shown inline in the page."""
    required_arguments = 1

    def run(self):
        env = self.state.document.settings.env
        name = directives.path(self.arguments[0])
        path = os.path.join(env.srcdir, DEMOS_DIR, name, 'index.html')
        if not os.path.isfile(path):
            raise self.error(f'Simulation not found: {path}')
        env.note_dependency(path)
        node = simulation()
        node['name'] = name
        for key, value in parse_simulation(path).items():
            node[key] = value
        return [node]


def visit_simulation_card(self, node):
    link = self.builder.get_relative_uri(self.builder.current_docname, node['doc'])
    image = _uri(self, node['image'])
    title = escape(node['title'])
    description = escape(node['description'])
    self.body.append(f'''
<a class="simulation-card" href="{link}">
    <img class="simulation-card__image" src="{image}" alt="{title} screenshot" loading="lazy">
    <span class="simulation-card__title">{title}</span>
    <span class="simulation-card__description">{description}</span>
</a>
''')
    raise nodes.SkipNode


def visit_simulation(self, node):
    name = node['name']
    base = f'demos/{name}/'
    links = ''.join(f'<link rel="stylesheet" href="{_uri(self, base + href)}">'
                    for href in node['stylesheets'])
    host_id = f'simulation-{name}'
    self.body.append(f'''
<div class="simulation" id="{host_id}"><template>{links}<style>{node['style']}</style>
<div class="sim-body {escape(node['body_class'])}">{node['body']}</div></template></div>
<script src="{_uri(self, '_static/js/simulations.js')}"></script>
<script>
mountSimulation("{host_id}", function (document) {{
{node['script']}
}});
</script>
<p class="simulation__open"><a href="{_uri(self, base + 'index.html')}" target="_blank" rel="noopener">Open full screen</a></p>
''')
    raise nodes.SkipNode


def write_scoped_stylesheets(app, exception):
    """Write the scoped copy of each simulation stylesheet to the output."""
    if exception or app.builder.format != 'html':
        return
    demos = os.path.join(app.srcdir, DEMOS_DIR)
    if not os.path.isdir(demos):
        return
    for name in sorted(os.listdir(demos)):
        page = os.path.join(demos, name, 'index.html')
        if not os.path.isfile(page):
            continue
        with open(page, encoding='utf-8') as f:
            head = f.read().split('<body', 1)[0]
        for href in _stylesheets(head):
            src = os.path.join(demos, name, href)
            if not os.path.isfile(src):
                continue
            dst = os.path.join(app.outdir, 'demos', name, _scoped_name(href))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(src, encoding='utf-8') as f:
                css = scope_css(f.read())
            with open(dst, 'w', encoding='utf-8') as f:
                f.write(css)


def skip(self, node):
    raise nodes.SkipNode


def setup(app):
    app.add_node(simulation_card, html=(visit_simulation_card, None),
                 latex=(skip, None), text=(skip, None), man=(skip, None), texinfo=(skip, None))
    app.add_node(simulation, html=(visit_simulation, None),
                 latex=(skip, None), text=(skip, None), man=(skip, None), texinfo=(skip, None))
    app.add_directive('simulation-card', SimulationCardDirective)
    app.add_directive('simulation', SimulationDirective)
    app.connect('build-finished', write_scoped_stylesheets)
    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
