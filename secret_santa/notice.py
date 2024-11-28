import jinja2 as j2
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT_DIR / "templates"
print(TEMPLATES_DIR)

DEFAULT_PLAIN_TEMPLATE = "message.j2"
DEFAULT_EMAIL_TEMPLATE = "email.html.j2"

class GiftNotice:
    env = j2.Environment(loader=j2.FileSystemLoader(TEMPLATES_DIR), autoescape=j2.select_autoescape())
        
    @classmethod
    def plain_text_template(cls, template: str = DEFAULT_PLAIN_TEMPLATE) -> j2.Template:
        return cls.env.get_template(template)
    
    @classmethod
    def email_template(cls, template: str = DEFAULT_EMAIL_TEMPLATE) -> j2.Template:
        return cls.env.get_template(template)