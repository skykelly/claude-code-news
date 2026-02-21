"""이메일 발송 모듈 - Gmail SMTP."""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


def send_gmail(output_dir: Path, to_email: str) -> bool:
    """Gmail SMTP로 뉴스레터 발송. to_email은 쉼표로 구분된 복수 주소 허용."""
    gmail_user = os.environ.get("GMAIL_USER", "").strip()
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()

    if not gmail_user or not gmail_app_password:
        print("  [send] GMAIL_USER 또는 GMAIL_APP_PASSWORD 미설정")
        return False

    html_file = output_dir / "email.html"
    txt_file = output_dir / "email.txt"

    if not html_file.exists():
        print(f"  [send] email.html 없음: {html_file}")
        return False

    html_body = html_file.read_text()
    txt_body = txt_file.read_text() if txt_file.exists() else ""

    # 쉼표로 구분된 수신자 목록 파싱
    recipients = [addr.strip() for addr in to_email.split(",") if addr.strip()]

    # 날짜 추출 (디렉토리명)
    date_str = output_dir.name
    subject = f"[Claude Code 뉴스레터] {date_str}"

    # MIME 구성
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = ", ".join(recipients)

    if txt_body:
        msg.attach(MIMEText(txt_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # 발송
    print(f"  [send] {gmail_user} → {recipients} 발송 중...")
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(gmail_user, gmail_app_password)
            smtp.sendmail(gmail_user, recipients, msg.as_bytes())
        print(f"  [send] ✅ 발송 완료 → {', '.join(recipients)}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("  [send] ❌ 인증 실패 - Gmail 앱 비밀번호를 확인하세요")
        return False
    except Exception as e:
        print(f"  [send] ❌ 발송 실패: {e}")
        return False
