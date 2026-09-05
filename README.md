# 🧬 Suhail Therapeutic Testing System

تطبيق Streamlit لمحاكاة نموذج رياضي لاستجابة الورم.

> **تنبيه:** المشروع بحثي/تعليمي فقط، وليس أداة تشخيص أو وصف علاج طبي.

## الملفات

```text
suhail_tumor_simulation/
├── app.py
├── simulation.py
├── requirements.txt
├── render.yaml
├── README.md
├── .gitignore
└── .streamlit/
    └── config.toml
```

## تشغيل محلي

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud

1. ارفع الملفات إلى GitHub.
2. افتح Streamlit Community Cloud.
3. اختر الـ repository.
4. اجعل Main file هو `app.py`.
5. Deploy.

## Render

الملف `render.yaml` جاهز. يمكن أيضاً إنشاء Web Service يدوياً بهذه القيم:

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

## ملاحظات إصلاح

- إصلاح عدّ أيام الجرعات وعرض نقاط الجرعات من DataFrame.
- فلترة أيام الجرعات خارج مدة المحاكاة.
- استخدام `st.download_button` لتنزيل CSV / JSON / HTML.
- إضافة تنبيه واضح بأن المخرجات بحثية/تعليمية.
