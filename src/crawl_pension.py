"""
동행복권 API로 연금복권720 전체 회차 당첨번호를 수집해 CSV로 저장.
API: https://www.dhlottery.co.kr/common.do?method=getPension720Number&drwNo={회차}
1등: 조(1~5) + 번호(0000000~9999999) 7자리
"""

import time
import requests
import pandas as pd
from pathlib import Path

API_URL = "https://www.dhlottery.co.kr/common.do?method=getPension720Number&drwNo={}"
OUTPUT = Path(__file__).parent.parent / "data" / "pension720.csv"
DELAY = 0.3


def fetch_draw(drw_no: int) -> dict | None:
    try:
        res = requests.get(API_URL.format(drw_no), timeout=5)
        data = res.json()
        if data.get("returnValue") != "success":
            return None
        w = data.get("win720Num", {})
        return {
            "drw_no": data["drwNo"],
            "date": data["drwNoDate"],
            "group": w.get("grpNo"),       # 조
            "n1": w.get("no1"),
            "n2": w.get("no2"),
            "n3": w.get("no3"),
            "n4": w.get("no4"),
            "n5": w.get("no5"),
            "n6": w.get("no6"),
            "n7": w.get("no7"),
        }
    except Exception:
        return None


def crawl(start: int = 1, end: int | None = None) -> pd.DataFrame:
    if end is None:
        end = start
        while True:
            if fetch_draw(end + 1) is None:
                break
            end += 1
            time.sleep(DELAY)

    print(f"수집 범위: {start}~{end}회차")
    rows = []
    for no in range(start, end + 1):
        row = fetch_draw(no)
        if row:
            rows.append(row)
        if no % 50 == 0:
            print(f"  {no}회차 완료")
        time.sleep(DELAY)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    if OUTPUT.exists():
        existing = pd.read_csv(OUTPUT)
        last = int(existing["drw_no"].max())
        print(f"기존 데이터 {last}회차까지 존재 → 이후 회차만 수집")
        new_df = crawl(start=last + 1)
        if not new_df.empty:
            df = pd.concat([existing, new_df], ignore_index=True)
        else:
            df = existing
            print("새 회차 없음")
    else:
        df = crawl(start=1)

    df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print(f"저장 완료: {OUTPUT} ({len(df)}행)")
