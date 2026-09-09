# BILYARD CLUB — Railway 5 files

Web-version: 5 ta BILLIARD + 3 ta TENNIS.

- Real-time timer: sahifa avtomatik refresh qilmaydi; vaqt server start timestampidan hisoblanadi.
- Tugatishda chek: stol va shu sessiya oralig‘idagi mahsulotlar jami ko‘rsatiladi.
- Sozlamalar: stol narxi, mahsulot qo‘shish/o‘chirish/narxini o‘zgartirish, klub nomi, oboy, kirish va admin paroli.
- SQLite baza avtomatik yaratiladi.

Railway start command: `gunicorn main:app --bind 0.0.0.0:$PORT`
