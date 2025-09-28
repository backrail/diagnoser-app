# Deploy & Embed (Quick)

## 1) Deploy (Render)
- New Web Service -> Python
- Build: `pip install -r requirements_deploy.txt`
- Start: `gunicorn diagnoser_starter.app:app --bind 0.0.0.0:8000 --workers 2`
- Env:
  - `BLOG_PARENT_ORIGINS`: `https://kaeruhakaeru.com/`
  - `SECRET_KEY`: 任意の長いランダム文字列（自動生成でもOK）

## 2) Seed (neutral demo)
Render の Shell で一度だけ:
```
export FLASK_APP=diagnoser_starter.app
flask seed_demo
```

## 3) Embed (Blog)
```html
<div style="aspect-ratio: 16/9; max-width: 1000px; margin: 0 auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
  <iframe
    src="https://<your-service>.onrender.com/"
    title="診断アプリ"
    loading="lazy"
    style="width:100%; height:100%; border:0;"
    allow="clipboard-write; fullscreen"
    referrerpolicy="strict-origin-when-cross-origin">
  </iframe>
</div>
<p style="text-align:center; margin-top:8px;">
  開かない/見づらい場合は
  <a href="https://<your-service>.onrender.com/" target="_blank" rel="noopener">新しいタブで開く</a>
</p>
```
