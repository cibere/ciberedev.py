import logging
import logging.handlers
import os
import shutil
from argparse import Namespace
from pathlib import Path

try:
    import pdoc
    import pdoc.cli
except ImportError:
    raise RuntimeError("'pdoc3' must be installed")
try:
    import ciberedev
except ImportError:
    raise RuntimeError("'ciberedev' must be installed")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

args = Namespace(
    modules=["ciberedev"],
    config=["show_source_code=False"],
    filter=None,
    force=False,
    html=True,
    pdf=False,
    html_dir=None,
    output_dir=None,
    html_no_source=False,
    overwrite=False,
    external_links=False,
    template_dir=None,
    link_prefix=None,
    close_stdin=False,
    http="",
    skip_errors=False,
)
pdoc.cli.main(args)

MODULES_TO_REMOVE = ["http.html"]
LATEST_DOCS_PATH = "docs/latest"

if not os.path.exists(LATEST_DOCS_PATH):
    os.makedirs(LATEST_DOCS_PATH)


def format_page(page):
    fp = f"html/ciberedev/{page}"

    if page in MODULES_TO_REMOVE:
        logger.info(f"Skipping {page}...")
        return
    logger.info(f"Starting to format {page}")

    with open(fp, "r") as file:
        html = file.read()

    html = html.replace('<meta name="generator" content="pdoc 0.10.0" />', "")
    html = html.replace(
        """cibere.dev python wrapper
~~~~~~~~~~~~~~~~~~~
A basic wrapper cibere.dev""",
        "A basic wrapper cibere.dev",
    )
    html = html.replace(
        '<p>Generated by <a href="https://pdoc3.github.io/pdoc" title="pdoc: Python API documentation generator"><cite>pdoc</cite> 0.10.0</a>.</p>',
        """
<a href="https://github.com/cibere/ciberedev.py"><img style="height: 15px; width: 15px;"
src="https://github.com/favicon.ico"></a>
<a href="https://discord.com/invite/pP4mKKbRvk"><img style="height: 15px; width: 15px;"
src="https://clipground.com/images/discord-icon-png-4.png"></a>""",
    )
    html = html.replace(
        '<h1 class="title">Package <code>ciberedev</code></h1>',
        '<h1 class="title"><code>ciberedev.py</code></h1>',
    )

    name = fp.split("/")[-1]

    with open(f"{LATEST_DOCS_PATH}/{name}", "w+") as file:
        file.write(html)

    logger.info(f"Finished formatting {name}")


logger.info("Starting Formatting")
for file in Path("html/ciberedev").glob("**/*.html"):
    fp = str(file)
    name = fp.split("\\")[-1]
    format_page(name)

logger.info("Explicitly formatting index page")
with open(f"{LATEST_DOCS_PATH}/index.html", "r") as f:
    html = f.read()

html = html.replace(
    """
<div class="desc"></div>
</dd>
<dt><code class="name"><a title="ciberedev.http" href="http.html">ciberedev.http</a></code></dt>
<dd>""",
    "",
)

html = html.replace(
    """\n<li><code><a title="ciberedev.http" href="http.html">ciberedev.http</a></code></li>""",
    "",
)


with open(f"{LATEST_DOCS_PATH}/index.html", "w") as f:
    f.write(html)

logger.info(f"Finished Index Page")

shutil.rmtree("html")
logger.info(f"Removed old html folder")

logger.info(f"Finished")