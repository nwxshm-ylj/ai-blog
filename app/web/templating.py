from __future__ import annotations

from fastapi.templating import Jinja2Templates

from app.web.flash import get_flashed_messages
from app.web.i18n import get_lang, switch_lang_url, translate, url_with_lang
from app.web.security import csrf_token

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["current_lang"] = get_lang
templates.env.globals["switch_lang_url"] = switch_lang_url
templates.env.globals["t"] = translate
templates.env.globals["url_with_lang"] = url_with_lang
templates.env.globals["csrf_token"] = csrf_token
templates.env.globals["get_flashed_messages"] = get_flashed_messages
