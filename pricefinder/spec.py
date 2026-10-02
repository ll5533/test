"""상품 제목에서 규격(용량·수량)을 읽어내고, 사용자가 고른 규격과 정확히 같은지 판정한다.

원칙: 애매하면 제외한다. 엉뚱한 규격이 섞이는 것이 하나 빠지는 것보다 나쁘다.
"""
import re
from dataclasses import dataclass

MEASURE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(kg|ml|liter|l|리터|g|롤|매)(?![a-z])")
COUNT_RE = re.compile(r"(\d+)\s*(개입|개|팩|입|ea|병|통|봉지|봉|캔|박스|세트|pack|p)(?![a-z])")
MULT_AFTER_RE = re.compile(r"(?:kg|ml|liter|l|리터|g|롤|매)\s*[x×*]\s*(\d+)(?![\d.]|\s*(?:kg|ml|l|g))")
MULT_BEFORE_RE = re.compile(r"(\d+)\s*[x×*]\s*\d+(?:\.\d+)?\s*(?:kg|ml|liter|l|리터|g|롤|매)")
# 묶음·증정·옵션 선택형 상품은 가격이 어떤 규격을 가리키는지 알 수 없다.
AMBIGUOUS_RE = re.compile(r"증정|사은품|덤|\d\s*\+\s*\d|랜덤|혼합|mix|택\s*1|옵션|선택")

UNIT_ALIASES = {"리터": "l", "liter": "l"}


@dataclass(frozen=True)
class Spec:
    size: float  # 한 개의 크기 (ml, g, 롤, 매 기준)
    unit: str  # "ml" | "g" | "롤" | "매"
    count: int  # 몇 개 묶음인지

    @property
    def total(self) -> float:
        return self.size * self.count


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"(?<=\d),(?=\d{3})", "", text)  # 1,000ml -> 1000ml
    return text


def _to_base(value: float, unit: str) -> tuple[float, str]:
    unit = UNIT_ALIASES.get(unit, unit)
    if unit == "l":
        return round(value * 1000, 6), "ml"
    if unit == "kg":
        return round(value * 1000, 6), "g"
    return round(value, 6), unit


def parse_spec(title: str):
    """제목에서 규격을 읽는다. 읽을 수 없거나 애매하면 (None, 사유)를 돌려준다."""
    text = _normalize(title)
    if AMBIGUOUS_RE.search(text):
        return None, "묶음/증정/옵션 상품"

    measures = {_to_base(float(v), u) for v, u in MEASURE_RE.findall(text)}
    if not measures:
        return None, "용량 표기를 찾지 못함"
    if len(measures) > 1:
        return None, "서로 다른 용량이 함께 표기됨"
    size, unit = next(iter(measures))

    counts = {int(n) for n, _ in COUNT_RE.findall(text)}
    counts |= {int(n) for n in MULT_AFTER_RE.findall(text)}
    counts |= {int(n) for n in MULT_BEFORE_RE.findall(text)}
    if len(counts) > 1:
        return None, "서로 다른 수량이 함께 표기됨"
    count = counts.pop() if counts else 1
    return Spec(size, unit, count), ""


def parse_wanted(size_text: str, count: int) -> Spec:
    """사용자가 입력한 '1000ml' 같은 문자열을 Spec으로 바꾼다."""
    spec, reason = parse_spec(size_text)
    if spec is None:
        raise ValueError(f"규격을 이해하지 못했습니다: {size_text!r} ({reason})")
    return Spec(spec.size, spec.unit, count)
