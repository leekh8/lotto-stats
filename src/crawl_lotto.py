"""
동행복권 API로 로또 6/45 전체 회차 당첨번호를 수집해 CSV로 저장.
API: https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={회차}
"""

import time
import requests
import pandas as pd
from pathlib import Path

API_URL = "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={}"
OUTPUT = Path(__file__).parent.parent / "data" / "lotto.csv"
DELAY = 0.3  # 서버 부하 방지


def fetch_draw(drw_no: int) -> dict | None:
    try:
        res = requests.get(API_URL.format(drw_no), timeout=5)
        data = res.json()
        if data.get("returnValue") != "success":
            return None
        return {
            "drw_no": data["drwNo"],
            "date": data["drwNoDate"],
            "n1": data["drwtNo1"],
            "n2": data["drwtNo2"],
            "n3": data["drwtNo3"],
            "n4": data["drwtNo4"],
            "n5": data["drwtNo5"],
            "n6": data["drwtNo6"],
            "bonus": data["bnusNo"],
            "prize_1st": data["firstWinamnt"],
            "winners_1st": data["firstPrzwnerCo"],
        }
    except Exception:
        return None


def crawl(start: int = 1, end: int | None = None) -> pd.DataFrame:
    # end 미지정 시 최신 회차 자동 탐색
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
        if no % 100 == 0:
            print(f"  {no}회차 완료")
        time.sleep(DELAY)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    # 기존 파일 있으면 마지막 회차 이후부터만 수집
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
