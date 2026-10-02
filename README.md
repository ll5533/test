# pricefinder (시제품)

품목 · 제조사 · 규격 · 개수를 입력하면, 그 규격과 정확히 일치하는 상품만 최저가순으로 보여줍니다.
애매한 상품(증정, 옵션 택1, 서로 다른 용량 병기)은 섞이지 않도록 제외합니다.

    python3 -m pricefinder 우유 매일 1L --show-excluded
    python3 -m pricefinder 햇반 CJ 210g 12
    python3 -m unittest discover -s tests -t .

현재는 `data/sample_listings.json`의 가상 데이터로 규격 필터만 검증합니다.
쇼핑몰 연동과 제휴 링크는 아직 없습니다.

알려진 한계: 같은 제조사의 다른 제품(예: 상하목장 유기농 우유, 햇반 현미밥)은 제목에 품목 단어가 있으면 함께 나옵니다.
