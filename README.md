# pricefinder

직접 등록한 상품 목록에서 품목 → 제조사 → 제품 → 규격 → 개수를 고르면, 정확히 일치하는 상품 하나와 구매 링크를 보여주는 정적 사이트입니다.
다른 용량은 처음부터 목록에 없으므로 섞이지 않습니다.

## 상품 추가하는 법

`data/catalog.json`에 항목을 추가합니다. 쿠팡 파트너스·네이버 쇼핑 커넥트에서 만든 제휴 링크를 `url`에 붙여 넣습니다. 링크가 비어 있으면 사이트에 "링크 준비 중"으로 표시됩니다.

    python3 -m pricefinder.catalog validate           # 등록 내용 점검 (규격과 상품명 불일치, 중복, http 링크 등)
    python3 -m pricefinder.catalog validate --strict  # 공개 전 점검: 빈 링크도 오류로 취급
    python3 -m pricefinder.catalog build              # docs/index.html 생성
    python3 -m unittest discover -s tests -t .        # 테스트

`docs/index.html`은 파일 하나로 완결되어 있어 GitHub Pages 등 어디에나 올릴 수 있습니다.
화면 하단에 제휴 활동 고지 문구가 들어 있으니 지우지 마세요.

## 참고: 규격 검색 시제품

`python3 -m pricefinder 우유 매일 1L --show-excluded` 는 쇼핑몰 상품 제목에서 규격을 읽어 정확히 일치하는 것만 거르는 초기 시제품입니다.
네이버 검색 API 약관 개정(쇼핑 API 종료, 수익 사이트 활용 제한)으로 자동 수집 방식은 접고, 규격 판독 코드는 상품 등록 검증에 재사용합니다.
