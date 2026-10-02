"""직접 등록한 상품 목록(data/catalog.json)을 검증하고 정적 사이트로 만든다.

    python3 -m pricefinder.catalog validate          # 등록 내용 점검
    python3 -m pricefinder.catalog validate --strict # 링크가 빈 상품도 오류로 취급 (공개 전 점검)
    python3 -m pricefinder.catalog build             # docs/index.html 생성
"""
import argparse
import json
import sys
from pathlib import Path

from .spec import Spec, parse_spec, parse_wanted

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "data" / "catalog.json"
TEMPLATE = ROOT / "site" / "template.html"
OUTPUT = ROOT / "docs" / "index.html"
REQUIRED = ("item", "brand", "variant", "size", "count", "name", "links")


def validate(products, strict=False):
    """오류 문장 목록을 돌려준다. 비어 있으면 통과."""
    errors, seen = [], {}
    for i, p in enumerate(products, 1):
        label = f"#{i} {p.get('name', '(이름 없음)')}"
        missing = [k for k in REQUIRED if k not in p]
        if missing:
            errors.append(f"{label}: 빠진 항목 {missing}")
            continue
        try:
            wanted = parse_wanted(p["size"], p["count"])
        except ValueError as e:
            errors.append(f"{label}: {e}")
            continue
        # 등록한 상품명에서 읽은 규격이 입력한 규격과 다르면 오등록이다.
        parsed, reason = parse_spec(p["name"])
        if parsed is None:
            errors.append(f"{label}: 상품명에서 규격을 읽지 못함({reason})")
        elif parsed != wanted:
            errors.append(f"{label}: 상품명 규격({parsed.size:g}{parsed.unit} x {parsed.count})과 "
                          f"입력 규격({wanted.size:g}{wanted.unit} x {wanted.count})이 다름")
        key = (p["item"], p["brand"], p["variant"], wanted)
        if key in seen:
            errors.append(f"{label}: #{seen[key]}와 같은 상품이 중복 등록됨")
        seen[key] = i
        if not p["links"]:
            errors.append(f"{label}: 링크가 하나도 없음")
        for link in p["links"]:
            url = link.get("url", "")
            if url and not url.startswith("https://"):
                errors.append(f"{label}: {link.get('mall')} 링크는 https:// 로 시작해야 함")
            if strict and not url:
                errors.append(f"{label}: {link.get('mall')} 링크가 비어 있음")
    return errors


def build(products, template=TEMPLATE, output=OUTPUT):
    data = json.dumps(products, ensure_ascii=False).replace("</", "<\\/")
    html = Path(template).read_text(encoding="utf-8").replace("__CATALOG__", data)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(html, encoding="utf-8")


def main(argv=None):
    p = argparse.ArgumentParser(description="상품 목록 검증 및 사이트 생성")
    p.add_argument("command", choices=["validate", "build"])
    p.add_argument("--strict", action="store_true")
    args = p.parse_args(argv)

    products = json.loads(CATALOG.read_text(encoding="utf-8"))
    errors = validate(products, strict=args.strict)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    if args.command == "build":
        build(products)
        print(f"{len(products)}개 상품으로 {OUTPUT.relative_to(ROOT)} 생성")
    else:
        print(f"{len(products)}개 상품 이상 없음")


if __name__ == "__main__":
    main()
