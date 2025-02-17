from pathlib import Path
from typing import Dict

from starlite import Starlite, Template, TemplateConfig, get
from starlite.template.jinja import JinjaTemplateEngine


def my_template_function(ctx: Dict) -> str:
    return ctx.get("my_context_key", "nope")


def register_template_callables(engine: JinjaTemplateEngine) -> None:
    engine.register_template_callable(
        key="check_context_key",
        template_callable=my_template_function,
    )


template_path = Path(__file__).parent / "templates"
template_config = TemplateConfig(
    directory=template_path,
    engine=JinjaTemplateEngine,
    engine_callback=register_template_callables,
)


@get("/")
def index() -> Template:
    return Template(name="index.html.jinja2")


app = Starlite(
    route_handlers=[index],
    template_config=template_config,
)
