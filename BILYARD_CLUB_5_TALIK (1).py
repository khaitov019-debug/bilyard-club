import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import sqlite3, os, shutil
from datetime import datetime, timedelta

BASE=os.path.dirname(os.path.abspath(__file__))
DB=os.path.join(BASE,"billiard_club.db")
IMG=os.path.join(BASE,"product_images")
os.makedirs(IMG,exist_ok=True)
db=sqlite3.connect(DB)
db.row_factory=sqlite3.Row

db.executescript("""
CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY,v TEXT);
CREATE TABLE IF NOT EXISTS tables(id INTEGER PRIMARY KEY,typ TEXT,no INTEGER,price REAL,active INTEGER DEFAULT 0,started TEXT);
CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,cat TEXT,size TEXT,price REAL,cost REAL,image TEXT,active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS sales(id INTEGER PRIMARY KEY AUTOINCREMENT,typ TEXT,tab_no INTEGER,product_id INTEGER,name TEXT,size TEXT,cat TEXT,qty INTEGER,total REAL,cost REAL,created TEXT);
CREATE TABLE IF NOT EXISTS sessions(id INTEGER PRIMARY KEY AUTOINCREMENT,typ TEXT,tab_no INTEGER,started TEXT,ended TEXT,seconds INTEGER,total REAL);
""")
for k,v in {"club":"BILYARD CLUB","login":"","admin":"","bg":""}.items():
    db.execute("INSERT OR IGNORE INTO settings VALUES(?,?)",(k,v))
for i in range(1,6): db.execute("INSERT OR IGNORE INTO tables(id,typ,no,price) VALUES(?,?,?,?)",(i,"BILLIARD",i,30000))
for i in range(1,4): db.execute("INSERT OR IGNORE INTO tables(id,typ,no,price) VALUES(?,?,?,?)",(100+i,"TENNIS",i,20000))
if db.execute("SELECT COUNT(*) FROM products").fetchone()[0]==0:
    products=[
    ("Suv","Ichimlik","0.5L",3000,0),("Suv","Ichimlik","1L",5000,0),("Suv","Ichimlik","1.5L",7000,0),("Suv","Ichimlik","2L",9000,0),
    ("Coca-Cola","Ichimlik","0.5L",7000,0),("Coca-Cola","Ichimlik","1L",11000,0),("Coca-Cola","Ichimlik","1.5L",15000,0),("Coca-Cola","Ichimlik","2L",19000,0),
    ("Fanta","Ichimlik","0.5L",7000,0),("Fanta","Ichimlik","1L",11000,0),("Fanta","Ichimlik","1.5L",15000,0),("Fanta","Ichimlik","2L",19000,0),
    ("Sprite","Ichimlik","0.5L",7000,0),("Sprite","Ichimlik","1L",11000,0),("Sprite","Ichimlik","1.5L",15000,0),("Sprite","Ichimlik","2L",19000,0),
    ("Pepsi","Ichimlik","0.5L",7000,0),("Pepsi","Ichimlik","1L",11000,0),("Pepsi","Ichimlik","1.5L",15000,0),("Pepsi","Ichimlik","2L",19000,0),
    ("Chips","Gazak","",10000,4000),("Suxarik","Gazak","",8000,3000),("Shokolad","Gazak","",10000,5000),("Yong'oq","Gazak","",15000,8000),
    ("Pullik tayoqcha","Tayoqcha","",5000,0)]
    db.executemany("INSERT INTO products(name,cat,size,price,cost,image) VALUES(?,?,?,?,?,?)",[(a,b,c,d,e,"") for a,b,c,d,e in products])
db.commit()

def get(k):
    r=db.execute("SELECT v FROM settings WHERE k=?",(k,)).fetchone()
    return r["v"] if r else ""
def put(k,v):
    db.execute("INSERT OR REPLACE INTO settings VALUES(?,?)",(k,str(v)));db.commit()
def money(x): return f"{x:,.0f} so'm".replace(","," ")
def now(): return datetime.now()
def secs(r): return int((now()-datetime.fromisoformat(r["started"])).total_seconds()) if r["active"] and r["started"] else 0
def clock(s): return f"{s//3600:02d}:{s%3600//60:02d}:{s%60:02d}"

root=tk.Tk();root.title("BILYARD CLUB");root.geometry("1500x900");root.configure(bg="#071017")
top=tk.Frame(root,bg="#03070a");top.pack(fill="x")
main=tk.Frame(root,bg="#071017");main.pack(fill="both",expand=True)

def clear():
    for w in main.winfo_children(): w.destroy()
def btn(p,t,c,w=18,b="#173044"):
    return tk.Button(p,text=t,command=c,width=w,height=2,bg=b,fg="white",activebackground="#e5b83b",
                     activeforeground="black",font=("Segoe UI",10,"bold"),relief="flat",cursor="hand2")

def admin_ok():
    p=get("admin")
    if not p:
        messagebox.showwarning("Admin","Admin paroli hali o'rnatilmagan. Sozlamalardan qo'ying.");return False
    return simpledialog.askstring("Admin","Admin paroli:",show="*")==p

def start(tid):
    r=db.execute("SELECT * FROM tables WHERE id=?",(tid,)).fetchone()
    if not r["active"]:
        db.execute("UPDATE tables SET active=1,started=? WHERE id=?",(now().isoformat(),tid));db.commit()
    home()

def finish(tid):
    r=db.execute("SELECT * FROM tables WHERE id=?",(tid,)).fetchone()
    if not r["active"]: return
    s=secs(r); total=s/3600*r["price"]
    db.execute("INSERT INTO sessions(typ,tab_no,started,ended,seconds,total) VALUES(?,?,?,?,?,?)",
               (r["typ"],r["no"],r["started"],now().isoformat(),s,total))
    prod=db.execute("SELECT COALESCE(SUM(total),0)x FROM sales WHERE typ=? AND tab_no=? AND created>=?",
                    (r["typ"],r["no"],r["started"])).fetchone()["x"]
    db.execute("UPDATE tables SET active=0,started=NULL WHERE id=?",(tid,));db.commit()
    messagebox.showinfo("Tugadi",f"{r['typ']} {r['no']}\nVaqt: {clock(s)}\nStol: {money(total)}\nMahsulot: {money(prod)}\nJAMI: {money(total+prod)}")
    home()

def add_sale(p,typ,no):
    db.execute("INSERT INTO sales(typ,tab_no,product_id,name,size,cat,qty,total,cost,created) VALUES(?,?,?,?,?,?,?,?,?,?)",
               (typ,no,p["id"],p["name"],p["size"],p["cat"],1,p["price"],p["cost"],now().isoformat()))
    db.commit()

def menu(typ=None,no=None):
    w=tk.Toplevel(root);w.title("MENYU");w.geometry("1100x750");w.configure(bg="#071017")
    tk.Label(w,text="🥤 ICHIMLIKLAR  🍫 GAZAKLAR  🎱 TAYOQCHA",bg="#071017",fg="#e5b83b",font=("Segoe UI",22,"bold")).pack(pady=10)
    area=tk.Frame(w,bg="#071017");area.pack(fill="both",expand=True,padx=15)
    rows=db.execute("SELECT * FROM products WHERE active=1 ORDER BY cat,name,size").fetchall()
    for i,p in enumerate(rows):
        f=tk.Frame(area,bg="#142531",bd=1,relief="solid");f.grid(row=i//5,column=i%5,padx=6,pady=6,sticky="nsew")
        if p["image"] and os.path.exists(p["image"]):
            try:
                im=tk.PhotoImage(file=p["image"])
                lab=tk.Label(f,image=im,bg="#142531");lab.image=im;lab.pack(pady=4)
            except: pass
        tk.Label(f,text=f"{p['name']} {p['size']}\n{money(p['price'])}",bg="#142531",fg="white",font=("Segoe UI",11,"bold")).pack()
        if typ:
            btn(f,"➕ OLISH",lambda pp=p:add_sale(pp,typ,no),14,"#1c7fb5").pack(pady=5)
    for c in range(5): area.grid_columnconfigure(c,weight=1)
    btn(w,"✖ CHIQISH",w.destroy,18,"#a83232").pack(pady=10)

def table_window(tid):
    r=db.execute("SELECT * FROM tables WHERE id=?",(tid,)).fetchone()
    w=tk.Toplevel(root);w.title(f"{r['typ']} {r['no']}");w.geometry("800x650");w.configure(bg="#071017")
    def refresh():
        if not w.winfo_exists(): return
        for x in w.winfo_children(): x.destroy()
        rr=db.execute("SELECT * FROM tables WHERE id=?",(tid,)).fetchone()
        tk.Label(w,text=f"{rr['typ']} {rr['no']}",bg="#071017",fg="#e5b83b",font=("Segoe UI",28,"bold")).pack(pady=15)
        tk.Label(w,text="🔴 BAND" if rr["active"] else "🟢 BO'SH",bg="#071017",fg="#e33" if rr["active"] else "#19b968",font=("Segoe UI",17,"bold")).pack()
        tk.Label(w,text=clock(secs(rr)),bg="#071017",fg="white",font=("Consolas",42,"bold")).pack(pady=8)
        row=tk.Frame(w,bg="#071017");row.pack(pady=10)
        if rr["active"]: btn(row,"⏹ TUGATISH",lambda:(w.destroy(),finish(tid)),18,"#a83232").pack(side="left",padx=5)
        else: btn(row,"▶ BAND QILISH",lambda:(w.destroy(),start(tid)),18,"#1c9b57").pack(side="left",padx=5)
        btn(row,"🥤 MENYU",lambda:menu(rr["typ"],rr["no"]),18,"#1c7fb5").pack(side="left",padx=5)
        btn(row,"✖ CHIQISH",w.destroy,18,"#555").pack(side="left",padx=5)
        if rr["active"]: w.after(1000,refresh)
    refresh()

def card(p,r):
    f=tk.Frame(p,bg="#3d1e24" if r["active"] else "#142531",bd=2,relief="solid");f.pack(fill="x",padx=5,pady=5)
    tk.Label(f,text=f"{r['typ']} {r['no']}",bg=f["bg"],fg="#e5b83b",font=("Segoe UI",15,"bold")).pack(pady=3)
    tk.Label(f,text=clock(secs(r)),bg=f["bg"],fg="white",font=("Consolas",19,"bold")).pack()
    btn(f,"KIRISH",lambda tid=r["id"]:table_window(tid),15,"#1c7fb5").pack(pady=3)
    btn(f,"⏹ TUGATISH" if r["active"] else "▶ BAND QILISH",lambda tid=r["id"]:finish(tid) if r["active"] else start(tid),15,"#a83232" if r["active"] else "#1c9b57").pack(pady=3)

def home():
    clear()
    bg=get("bg")
    if bg and os.path.exists(bg):
        try:
            im=tk.PhotoImage(file=bg);lab=tk.Label(main,image=im);lab.image=im;lab.place(relwidth=1,relheight=1);lab.lower()
        except: pass
    tk.Label(main,text=get("club"),bg="#071017",fg="#e5b83b",font=("Segoe UI",30,"bold")).pack(pady=10)
    area=tk.Frame(main,bg="#071017");area.pack(fill="both",expand=True,padx=12)
    l=tk.Frame(area,bg="#071017");l.pack(side="left",fill="y",padx=7)
    c=tk.Frame(area,bg="#071017");c.pack(side="left",fill="both",expand=True,padx=7)
    r=tk.Frame(area,bg="#071017");r.pack(side="right",fill="y",padx=7)
    tk.Label(l,text="🏓 3 TA TENNIS",bg="#071017",fg="#e5b83b",font=("Segoe UI",16,"bold")).pack()
    for x in db.execute("SELECT * FROM tables WHERE typ='TENNIS' ORDER BY no"):card(l,x)
    tk.Label(c,text="🎱 5 TA BILLIARD",bg="#071017",fg="#e5b83b",font=("Segoe UI",16,"bold")).pack()
    g=tk.Frame(c,bg="#071017");g.pack(fill="x")
    for i,x in enumerate(db.execute("SELECT * FROM tables WHERE typ='BILLIARD' ORDER BY no")):
        q=tk.Frame(g,bg="#071017");q.grid(row=i//2,column=i%2,sticky="nsew");card(q,x)
    g.grid_columnconfigure(0,weight=1);g.grid_columnconfigure(1,weight=1)
    tk.Label(r,text="🥤 MENYU",bg="#071017",fg="#e5b83b",font=("Segoe UI",16,"bold")).pack()
    btn(r,"🥤 MENYU OCHISH",menu,18,"#1c7fb5").pack(pady=10)
    btn(r,"📊 TARIX",reports,18).pack(pady=5)
    btn(r,"⚙ SOZLAMALAR",settings,18).pack(pady=5)

def reports():
    clear();tk.Label(main,text="📊 TARIX / HISOBOT",bg="#071017",fg="#e5b83b",font=("Segoe UI",28,"bold")).pack(pady=15)
    box=tk.Frame(main,bg="#071017");box.pack(fill="both",expand=True,padx=40)
    def show(kind):
        for x in box.winfo_children():x.destroy()
        n=now()
        if kind=="day": s=n.replace(hour=0,minute=0,second=0,microsecond=0)
        elif kind=="week": s=(n-timedelta(days=n.weekday())).replace(hour=0,minute=0,second=0,microsecond=0)
        else: s=n.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        si=s.isoformat(); ei=n.isoformat()
        a=db.execute("SELECT COALESCE(SUM(total),0)x FROM sessions WHERE ended>=? AND ended<=?",(si,ei)).fetchone()["x"]
        b=db.execute("SELECT COALESCE(SUM(total),0)x,COALESCE(SUM(cost),0)c FROM sales WHERE created>=? AND created<=?",(si,ei)).fetchone()
        vals=[("JAMI SAVDO",a+b["x"]),("SOF FOYDA",a+b["x"]-b["c"]),
              ("BILLIARD",db.execute("SELECT COUNT(*)x FROM sessions WHERE typ='BILLIARD' AND ended>=? AND ended<=?",(si,ei)).fetchone()["x"]),
              ("TENNIS",db.execute("SELECT COUNT(*)x FROM sessions WHERE typ='TENNIS' AND ended>=? AND ended<=?",(si,ei)).fetchone()["x"]),
              ("SUV SOTILDI",db.execute("SELECT COALESCE(SUM(qty),0)x FROM sales WHERE name='Suv' AND created>=? AND created<=?",(si,ei)).fetchone()["x"]),
              ("SNEYK SOTILDI",db.execute("SELECT COALESCE(SUM(qty),0)x FROM sales WHERE cat='Gazak' AND created>=? AND created<=?",(si,ei)).fetchone()["x"])]
        for n,v in vals:
            text=money(v) if isinstance(v,(int,float)) and n in ("JAMI SAVDO","SOF FOYDA") else f"{v} ta"
            tk.Label(box,text=f"{n}: {text}",bg="#142531",fg="white",anchor="w",padx=20,font=("Segoe UI",15,"bold")).pack(fill="x",pady=5)
    for t,k in [("KUNLIK","day"),("HAFTALIK","week"),("OYLIK","month")]: btn(main,t,lambda kk=k:show(kk),15).pack(side="left",padx=5,pady=5)
    show("day")

def choose_product():
    rows=db.execute("SELECT * FROM products WHERE active=1 ORDER BY id").fetchall()
    q=simpledialog.askstring("Mahsulot", "\n".join(f"{x['id']} - {x['name']} {x['size']}" for x in rows)+"\n\nID:")
    try:return db.execute("SELECT * FROM products WHERE id=?",(int(q),)).fetchone()
    except:return None

def product_image():
    if not admin_ok():return
    p=choose_product()
    if not p:return
    f=filedialog.askopenfilename(filetypes=[("Rasm","*.png *.gif *.jpg *.jpeg")])
    if f:
        dst=os.path.join(IMG,f"product_{p['id']}"+os.path.splitext(f)[1]);shutil.copy2(f,dst)
        db.execute("UPDATE products SET image=? WHERE id=?",(dst,p["id"]));db.commit();messagebox.showinfo("Tayyor","Rasm saqlandi.")

def background():
    if not admin_ok():return
    f=filedialog.askopenfilename(filetypes=[("Rasm","*.png *.gif *.jpg *.jpeg")])
    if f:
        dst=os.path.join(BASE,"club_background"+os.path.splitext(f)[1]);shutil.copy2(f,dst);put("bg",dst);home()

def edit_price():
    if not admin_ok():return
    p=choose_product()
    if p:
        q=simpledialog.askstring("Narx","Yangi narx:",initialvalue=str(p["price"]))
        try:db.execute("UPDATE products SET price=? WHERE id=?",(float(q),p["id"]));db.commit()
        except:pass

def remove_product():
    if not admin_ok():return
    p=choose_product()
    if p: db.execute("UPDATE products SET active=0 WHERE id=?",(p["id"],));db.commit()

def settings():
    if not admin_ok():return
    clear();tk.Label(main,text="⚙ SOZLAMALAR",bg="#071017",fg="#e5b83b",font=("Segoe UI",28,"bold")).pack(pady=10)
    nb=tk.Frame(main,bg="#071017");nb.pack(fill="both",expand=True,padx=30)
    # Nom va parollar
    tk.Label(nb,text="Klub nomi",bg="#071017",fg="white").pack(pady=5)
    e=tk.Entry(nb,width=35);e.insert(0,get("club"));e.pack()
    btn(nb,"NOMNI SAQLASH",lambda:put("club",e.get()),22).pack(pady=5)
    btn(nb,"🖼 OBOY RASMINI O'ZGARTIRISH",background,30,"#1c7fb5").pack(pady=5)
    btn(nb,"🖼 MAHSULOT RASMINI O'ZGARTIRISH",product_image,32,"#1c7fb5").pack(pady=5)
    btn(nb,"💰 MAHSULOT NARXINI O'ZGARTIRISH",edit_price,32).pack(pady=5)
    btn(nb,"🗑 MAHSULOTNI OLIB TASHLASH",remove_product,32,"#a83232").pack(pady=5)
    tk.Label(nb,text="Stol narxlari",bg="#071017",fg="#e5b83b",font=("Segoe UI",16,"bold")).pack(pady=15)
    for i,r in enumerate(db.execute("SELECT * FROM tables ORDER BY typ,no")):
        row=tk.Frame(nb,bg="#071017");row.pack(pady=2)
        tk.Label(row,text=f"{r['typ']} {r['no']}",width=18,bg="#071017",fg="white").pack(side="left")
        en=tk.Entry(row,width=12);en.insert(0,r["price"]);en.pack(side="left")
        btn(row,"SAQLASH",lambda tid=r["id"],ee=en:save_table_price(tid,ee),10).pack(side="left",padx=5)
    btn(nb,"🔐 KIRISH PAROLINI O'RNATISH",lambda:set_password("login"),30).pack(pady=12)
    btn(nb,"🔑 ADMIN PAROLINI O'RNATISH",lambda:set_password("admin"),30).pack(pady=5)

def save_table_price(tid,e):
    try:db.execute("UPDATE tables SET price=? WHERE id=?",(float(e.get()),tid));db.commit()
    except:messagebox.showerror("Xato","Narx noto'g'ri.")

def set_password(k):
    q=simpledialog.askstring("Parol","Yangi parol:",show="*")
    if q is not None:put(k,q)

for t,c in [("🏠 BOSH SAHIFA",home),("🥤 MENYU",menu),("📊 TARIX",reports),("⚙ SOZLAMALAR",settings)]:
    btn(top,t,c,18).pack(side="left",padx=4,pady=8)

def alarm():
    for r in db.execute("SELECT * FROM tables WHERE active=1"):
        if secs(r)>0 and secs(r)//3600>0 and secs(r)%3600<2: root.bell()
    root.after(60000,alarm)

if get("login"):
    if not (simpledialog.askstring("Kirish","Parol:",show="*")==get("login")):
        root.destroy()
home();alarm()
root.protocol("WM_DELETE_WINDOW",lambda:(db.commit(),db.close(),root.destroy()))
root.mainloop()
