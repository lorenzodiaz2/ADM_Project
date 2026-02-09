from pathlib import Path
import shutil

BASE = "https://lorenzodiaz2.github.io/ADM_Project"

MAPPING = {
    "roma":   {"pub": "Q30284569", "area": "Q220"},
    "milano": {"pub": "Q106225029", "area": "Q490"},
}

DOCS = Path("docs")
DATASET_DIR = DOCS / "dataset"


def _find_single_md(folder: Path) -> Path:
    mds = list(folder.glob("*.md"))
    if not mds:
        raise FileNotFoundError(f"No .md found in {folder}")
    return mds[0]


def _new_dataset_folder(pub: str, area: str) -> Path:
    return DATASET_DIR / "wd" / pub / "wd" / area


def _rewrite_links(text: str, slug: str, pub: str, area: str) -> str:
    # aggiorna solo i link principali (se nel markdown li hai scritti)
    old_dataset = f"{BASE}/dataset/{slug}/"
    new_dataset = f"{BASE}/dataset/wd/{pub}/wd/{area}/"
    text = text.replace(old_dataset, new_dataset)

    # template stop/route se presenti come testo
    text = text.replace(f"{BASE}/resources/stop/{slug}:", f"{BASE}/resources/stop/wd/{pub}/wd/{area}/")
    text = text.replace(f"{BASE}/resources/route/{slug}:", f"{BASE}/resources/route/wd/{pub}/wd/{area}/")

    return text


def _write_redirect(old_folder: Path, target_url: str) -> None:
    # GitHub Pages/Jekyll: index.md con HTML va benissimo
    content = "\n".join([
        "---",
        "layout: default",
        "---",
        f'<meta http-equiv="refresh" content="0; url={target_url}">',
        f'<link rel="canonical" href="{target_url}">',
        "",
        f"If you are not redirected, open: {target_url}",
        "",
    ])
    (old_folder / "index.md").write_text(content, encoding="utf-8")


def main():
    for slug, info in MAPPING.items():
        pub = info["pub"]
        area = info["area"]

        old_folder = DATASET_DIR / slug
        old_md = _find_single_md(old_folder)
        old_text = old_md.read_text(encoding="utf-8")

        new_folder = _new_dataset_folder(pub, area)
        new_folder.mkdir(parents=True, exist_ok=True)

        new_text = _rewrite_links(old_text, slug, pub, area)
        (new_folder / "index.md").write_text(new_text, encoding="utf-8")

        # opzionale: rimpiazza la vecchia pagina con redirect
        target = f"{BASE}/dataset/wd/{pub}/wd/{area}/"
        _write_redirect(old_folder, target)

        print(f"OK: {slug} -> {new_folder}/index.md")

    print("Done.")


if __name__ == "__main__":
    main()
