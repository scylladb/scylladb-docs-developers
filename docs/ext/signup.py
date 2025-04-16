from docutils import nodes
from docutils.parsers.rst import Directive, directives

class SignupDirective(Directive):
    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'action': directives.unchanged,
        'title': directives.unchanged,
        'body': directives.unchanged,
        'placeholder': directives.unchanged,
        'button_text': directives.unchanged,
        'privacy_policy_url': directives.unchanged,
    }

    def run(self):
        action = self.options.get('action', '#')
        title = self.options.get('title', 'Sign up for our product updates')
        body = self.options.get('body', 'Stay ahead with the latest tutorials, guides, news and events from ScyllaDB.')
        placeholder = self.options.get('placeholder', 'Company Email *')
        button_text = self.options.get('button_text', 'Subscribe')
        privacy_policy_url = self.options.get('privacy_policy_url', '#')

        html = f'''
        <div class="topic-box__head" id="signup">
          <h1 class="topic-box__title">{title}</h1>
        </div>
        <div class="topic-box__body" id="signup_body">
          <p>{body}</p>
          <div class="docutils container">
            <form accept-charset="UTF-8" method="post" action="{action}" class="form" id="pardot-form" autocomplete="off">
              <p class="form-field email pd-text required">
                <input type="text" name="email" id="email" value="" class="text" size="30" maxlength="255" placeholder="{placeholder}" autocomplete="off">
              </p>
              <input type="hidden" name="utm_campaign" id="utm_campaign" value="">
              <input type="hidden" name="utm_medium" id="utm_medium" value="">
              <input type="hidden" name="utm_source" id="utm_source" value="">
              <input type="hidden" name="source_type" id="source_type" value="">
              <input type="hidden" name="latest_sfdc_campaign" id="latest_sfdc_campaign" value="">
              <input type="hidden" name="campaign_status" id="campaign_status" value="">
              <input type="hidden" name="_utf8" value="☃">
              <p class="submit">
                <input type="submit" accesskey="s" value="{button_text}">
              </p>
              <div class="onboard-form__field onboard-form__field--checkbox">
                <input name="opt_in_consent" id="opt_in_consent" type="checkbox" class="form-input" value="Yes">
                <label for="opt_in_consent">Yes, I wish to receive future informational and marketing communications from ScyllaDB, and I understand and agree to the <a href="{privacy_policy_url}"><b>privacy policy</b></a>.</label>
              </div>
            </form>
          </div>
        </div>
        <script>
            document.getElementById("pardot-form").addEventListener("submit", function(event) {{
                document.getElementById("pardot-form").style.display = "none";
                document.getElementById("signup").style.display = "none";
                document.getElementById("signup_body").style.display = "none";
                document.cookie = "formSubmitted=true; path=/; max-age=" + (60 * 60 * 24 * 365); // Cookie expires in 365 days
            }});

            window.addEventListener("load", function() {{
                if (document.cookie.split(";").some((item) => item.trim().startsWith("formSubmitted="))) {{
                    document.getElementById("pardot-form").style.display = "none";
                    document.getElementById("signup").style.display = "none";
                    document.getElementById("signup_body").style.display = "none";
                }}
            }});
        </script>
        '''
        raw_node = nodes.raw('', html, format='html')
        return [raw_node]

def setup(app):
    app.add_directive('signup', SignupDirective)
    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }