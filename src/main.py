"""전체 뉴스레터 파이프라인 실행 진입점."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# src/ 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from collect import collect
from filter import filter_and_curate
from format import format_output
from generate import generate
from send import send_gmail

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def parse_args():
    parser = argparse.ArgumentParser(description="Claude Code 뉴스레터 생성 파이프라인")
    parser.add_argument("--date", help="기준 날짜 YYYY-MM-DD (기본: 오늘)")
    parser.add_argument(
        "--step",
        choices=["collect", "filter", "generate", "format"],
        help="특정 단계만 실행",
    )
    parser.add_argument("--test", action="store_true", help="테스트 모드 (mock 데이터 사용)")
    parser.add_argument("--send", metavar="EMAIL", help="생성 후 지정 이메일로 발송")
    return parser.parse_args()


def main():
    args = parse_args()

    # 날짜 결정
    if args.date:
        date_str = args.date
    else:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    root = Path(__file__).parent.parent
    output_base = Path(os.environ.get("OUTPUT_DIR", "output"))
    if not output_base.is_absolute():
        output_base = root / output_base
    output_dir = output_base / date_str
    template_dir = root / "templates"
    lang = os.environ.get("NEWSLETTER_LANG", "ko")

    print(f"\n{'='*50}")
    print(f"  Claude Code 뉴스레터 파이프라인")
    print(f"  날짜: {date_str}  |  언어: {lang}  |  테스트: {args.test}  |  발송: {args.send or '없음'}")
    print(f"  출력: {output_dir}")
    print(f"{'='*50}\n")

    step = args.step

    # ---------- 1단계: 수집 ----------
    if step in (None, "collect"):
        print("[1/4] 콘텐츠 수집 중...")
        raw_items = collect(output_dir, test_mode=args.test)
        print(f"  → {len(raw_items)}개 수집 완료\n")
    else:
        raw_file = output_dir / "raw.json"
        if not raw_file.exists():
            print(f"[오류] raw.json 없음: {raw_file}")
            sys.exit(1)
        raw_items = json.loads(raw_file.read_text())

    if step == "collect":
        print("✅ 수집 단계 완료")
        return

    # ---------- 2단계: 필터링 ----------
    if step in (None, "filter"):
        print("[2/4] 필터링 & 분류 중...")
        curated = filter_and_curate(raw_items, output_dir)
        print(f"  → {curated['total_curated']}개 큐레이션 완료\n")
    else:
        curated_file = output_dir / "curated.json"
        if not curated_file.exists():
            print(f"[오류] curated.json 없음: {curated_file}")
            sys.exit(1)
        curated = json.loads(curated_file.read_text())

    if step == "filter":
        print("✅ 필터링 단계 완료")
        return

    # ---------- 3단계: 본문 생성 ----------
    if step in (None, "generate"):
        print("[3/4] 본문 생성 중...")
        content_md = generate(curated, output_dir, lang=lang)
        print(f"  → 본문 생성 완료 ({len(content_md)}자)\n")
    else:
        content_file = output_dir / "content.md"
        if not content_file.exists():
            print(f"[오류] content.md 없음: {content_file}")
            sys.exit(1)
        content_md = content_file.read_text()

    if step == "generate":
        print("✅ 본문 생성 단계 완료")
        return

    # ---------- 4단계: 포맷 변환 ----------
    if step in (None, "format"):
        print("[4/4] HTML / TXT 변환 중...")
        summary = format_output(content_md, curated, output_dir, template_dir)
        print()

    # ---------- 이메일 발송 ----------
    if args.send:
        print(f"[+] 이메일 발송 중 → {args.send}")
        send_gmail(output_dir, to_email=args.send)
        print()

    # ---------- 최종 결과 ----------
    print(f"{'='*50}")
    print(f"  ✅ 파이프라인 완료!")
    print(f"  출력 디렉토리: {output_dir}")
    for fname in ["email.html", "email.txt", "summary.json", "content.md"]:
        fpath = output_dir / fname
        if fpath.exists():
            size = fpath.stat().st_size
            print(f"    📄 {fname} ({size:,} bytes)")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
