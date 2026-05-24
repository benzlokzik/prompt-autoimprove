import shutil
from pathlib import Path


def on_post_build(config, **_kwargs) -> None:
    """MkDocs hooks for prompt-autoimprove docs build.

    `on_post_build` mirrors the root sitemap.xml into every directory that
    contains an index.html. Material 9.x always fetches sitemap.xml for
    prefetch; with an absolute https `site_url`, the dev server's URL
    resolution falls back to a page-relative path and produces 404 spam.
    Copying the root sitemap into every page dir kills the noise without
    changing the canonical sitemap that search engines crawl at the root.
    """
    site_dir = Path(config["site_dir"])
    root_sitemap = site_dir / "sitemap.xml"
    root_sitemap_gz = site_dir / "sitemap.xml.gz"
    if not root_sitemap.exists():
        return

    for index_html in site_dir.rglob("index.html"):
        page_dir = index_html.parent
        if page_dir == site_dir:
            continue
        target = page_dir / "sitemap.xml"
        if not target.exists():
            shutil.copy2(root_sitemap, target)
        target_gz = page_dir / "sitemap.xml.gz"
        if root_sitemap_gz.exists() and not target_gz.exists():
            shutil.copy2(root_sitemap_gz, target_gz)
