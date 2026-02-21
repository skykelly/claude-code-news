# 뉴스레터 이메일 발송 도구 및 방법

조사일: 2026-02-21

---

## 발송 서비스 비교

| 서비스 | 무료 한도 | 특징 | API 지원 |
|--------|-----------|------|----------|
| **Gmail SMTP** | 무제한 (일 500통) | 계정만 있으면 즉시 사용, 앱 비밀번호 필요 | SMTP |
| **Resend** | 3,000통/월 | 개발자 친화적 REST API | REST |
| **SendGrid** | 100통/일 | 강력한 분석, 대용량 | REST |
| **Mailchimp** | 500명/월 | UI 기반 관리, 자동화 강력 | REST |
| **Beehiiv** | 2,500명 | 뉴스레터 특화, 수익화 내장 | REST |
| **Substack** | 무제한 무료 | 커뮤니티 빌딩, 유료 구독 | - |

---

## Gmail SMTP 구현 (현재 사용 중)

### 설정

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(gmail_user, app_password)
    smtp.sendmail(from_addr, to_addr, msg.as_bytes())
```

### 필요 환경 변수

```
GMAIL_USER=lge.ksmc5@gmail.com
GMAIL_APP_PASSWORD=<16자리 앱 비밀번호>
NEWSLETTER_TO=ilse.lee@lge.com
```

### 앱 비밀번호 발급

1. https://myaccount.google.com/security → 2단계 인증 활성화
2. https://myaccount.google.com/apppasswords → 이름 입력 후 생성
3. 16자리 코드 복사 (공백 제거 후 사용)

---

## 주의사항

- Gmail SMTP: 하루 500통 한도, 스팸 필터에 걸릴 수 있음
- LGE 도메인 수신 시 스팸 폴더 확인 필요
- HTML 이메일: Jinja2 `autoescape=False` + `{{ content | safe }}` 필요
- MIME: `multipart/alternative` 로 HTML + plaintext 동시 첨부 권장

---

## 법적 요건

- 발신자 정보 명시 필수
- 구독 해지 링크 필수 (CAN-SPAM, GDPR)
- 개인 식별 정보 수집·보관 정책 필요
