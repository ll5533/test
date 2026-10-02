"""품목 + 제조사 + 규격 + 수량으로 정확히 일치하는 상품만 골라 최저가순으로 보여준다."""
import argparse
import json
from pathlib import Path

from .spec import Spec, parse_spec, parse_wanted

DEFAULT_DATA = Path(__file__).resolve().parent.parent / "data" / "sample_listings.json"


def search(listings, item: str, brand: str, wanted: Spec):
    """(일치 목록 가격순, 제외 목록[(상품, 사유)])를 돌려준다."""
    matched, excluded = [], []
    for listing in listings:
        title = listing["title"].lower()
        if item.lower() not in title or brand.lower() not in title:
            continue  # 다른 품목·제조사는 '제외'가 아니라 검색 대상 밖
        spec, reason = parse_spec(listing["title"])
        if spec is None:
            excluded.append((listing, reason))
        elif spec != wanted:
            excluded.append((listing, f"규격 불일치({_fmt(spec)})"))
        else:
            matched.append(listing)
    matched.sort(key=lambda x: x["price"])
    return matched, excluded


def _fmt(spec: Spec) -> str:
    size = int(spec.size) if spec.size == int(spec.size) else spec.size
    return f"{size}{spec.unit} x {spec.count}"


def main(argv=None):
    p = argparse.ArgumentParser(description="규격이 정확히 일치하는 최저가 찾기")
    p.add_argument("item", help="품목 (예: 우유)")
    p.add_argument("brand", help="제조사 (예: 매일)")
    p.add_argument("size", help="한 개 규격 (예: 1000ml, 1L, 210g)")
    p.add_argument("count", type=int, nargs="?", default=1, help="개수 (기본 1)")
    p.add_argument("--data", default=str(DEFAULT_DATA))
    p.add_argument("--show-excluded", action="store_true", help="제외된 상품과 사유 표시")
    args = p.parse_args(argv)

    wanted = parse_wanted(args.size, args.count)
    listings = json.loads(Path(args.data).read_text(encoding="utf-8"))
    matched, excluded = search(listings, args.item, args.brand, wanted)

    print(f"[{args.brand} {args.item} {_fmt(wanted)}] 일치 {len(matched)}건")
    for m in matched:
        print(f"  {m['price']:>7,}원  {m['mall']:<8} {m['title']}  {m['url']}")
    if args.show_excluded:
        print(f"\n제외 {len(excluded)}건")
        for listing, reason in excluded:
            print(f"  - {listing['title']}  → {reason}")


if __name__ == "__main__":
    main()
