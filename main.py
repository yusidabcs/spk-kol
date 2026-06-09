from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db, init_db, KolKandidat, Kriteria, SesiKalkulasi, HasilRanking
from wsm import hitung_wsm, DEFAULT_BOBOT
from seed_data import seed

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed()
    yield

app = FastAPI(title="SPK KOL Instagram", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def render(request, name, ctx):
    """Cross-version compatible template rendering."""
    try:
        return templates.TemplateResponse(request, name, ctx)
    except (TypeError, AttributeError):
        ctx["request"] = request
        return templates.TemplateResponse(name, ctx)

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    total_kol = db.query(KolKandidat).count()
    total_sesi = db.query(SesiKalkulasi).count()
    niches = [r[0] for r in db.query(KolKandidat.niche).distinct().all()]
    last_sesi = db.query(SesiKalkulasi).order_by(SesiKalkulasi.id.desc()).first()
    preview = []
    if last_sesi:
        preview = db.query(HasilRanking).filter(
            HasilRanking.id_sesi == last_sesi.id
        ).order_by(HasilRanking.posisi).limit(5).all()
    return render(request, "dashboard.html", {
        "total_kol": total_kol, "total_sesi": total_sesi,
        "total_niche": len(niches), "niches": niches,
        "preview": preview, "last_sesi": last_sesi,
    })

@app.get("/kol", response_class=HTMLResponse)
def daftar_kol(request: Request, db: Session = Depends(get_db),
               niche: str = "Semua", q: str = "", sort: str = "followers", order: str = "desc"):
    niches = [r[0] for r in db.query(KolKandidat.niche).distinct().all()]
    query = db.query(KolKandidat)
    if niche != "Semua":
        query = query.filter(KolKandidat.niche == niche)
    if q:
        like = f"%{q}%"
        query = query.filter((KolKandidat.username.ilike(like)) | (KolKandidat.nama_lengkap.ilike(like)))
    sort_map = {
        "username": KolKandidat.username,
        "nama_lengkap": KolKandidat.nama_lengkap,
        "niche": KolKandidat.niche,
        "followers": KolKandidat.followers,
        "engagement_rate": KolKandidat.engagement_rate,
        "content_quality_score": KolKandidat.content_quality_score,
        "niche_relevance": KolKandidat.niche_relevance,
        "posting_consistency": KolKandidat.posting_consistency,
    }
    col = sort_map.get(sort, KolKandidat.followers)
    col = col.desc() if order == "desc" else col.asc()
    kol_list = query.order_by(col).all()
    return render(request, "kol_list.html", {
        "kol_list": kol_list, "niches": niches,
        "selected_niche": niche, "q": q, "sort": sort, "order": order,
    })

@app.get("/cari", response_class=HTMLResponse)
def cari(request: Request, db: Session = Depends(get_db),
         niche: str = "Semua", min_f: int = 0, max_f: int = 999999):
    kriteria = db.query(Kriteria).all()
    niches = [r[0] for r in db.query(KolKandidat.niche).distinct().all()]
    return render(request, "search.html", {
        "kriteria": kriteria, "niches": niches,
        "selected_niche": niche, "min_f": min_f, "max_f": max_f,
        "default_bobot": DEFAULT_BOBOT,
    })

@app.post("/hitung", response_class=HTMLResponse)
async def hitung(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    niche = form.get("niche", "Semua")
    min_f = int(form.get("min_followers", 0))
    max_f = int(form.get("max_followers", 999999))
    bobot = {
        "C1": float(form.get("C1", 0.35)),
        "C2": float(form.get("C2", 0.20)),
        "C3": float(form.get("C3", 0.20)),
        "C4": float(form.get("C4", 0.15)),
        "C5": float(form.get("C5", 0.10)),
    }
    total_w = sum(bobot.values())
    if abs(total_w - 1.0) > 0.01 and total_w > 0:
        bobot = {k: v/total_w for k, v in bobot.items()}

    query = db.query(KolKandidat)
    if niche != "Semua":
        query = query.filter(KolKandidat.niche == niche)
    query = query.filter(KolKandidat.followers >= min_f, KolKandidat.followers <= max_f)
    kol_objects = query.all()

    if not kol_objects:
        return RedirectResponse("/cari", status_code=302)

    kol_dicts = [{
        "id": k.id, "username": k.username, "niche": k.niche,
        "followers": k.followers, "avg_likes": k.avg_likes,
        "avg_comments": k.avg_comments, "engagement_rate": k.engagement_rate,
        "posting_consistency": k.posting_consistency,
        "content_quality_score": k.content_quality_score,
        "niche_relevance": k.niche_relevance,
        "instagram_url": k.instagram_url,
    } for k in kol_objects]

    hasil = hitung_wsm(kol_dicts, bobot)

    sesi = SesiKalkulasi(
        filter_niche=niche, filter_min_followers=min_f,
        filter_max_followers=max_f, bobot_json=bobot,
        jumlah_kandidat=len(hasil)
    )
    db.add(sesi)
    db.flush()

    for h in hasil:
        db.add(HasilRanking(
            id_sesi=sesi.id, id_kol=h["id"],
            username=h["username"], niche=h["niche"],
            followers=h["followers"], skor_total=h["skor_total"],
            posisi=h["posisi"],
            kontribusi_c1=h.get("kontribusi_c1", 0),
            kontribusi_c2=h.get("kontribusi_c2", 0),
            kontribusi_c3=h.get("kontribusi_c3", 0),
            kontribusi_c4=h.get("kontribusi_c4", 0),
            kontribusi_c5=h.get("kontribusi_c5", 0),
            r_c1=h.get("r_c1", 0), r_c2=h.get("r_c2", 0),
            r_c3=h.get("r_c3", 0), r_c4=h.get("r_c4", 0),
            r_c5=h.get("r_c5", 0),
        ))
    db.commit()

    kriteria = db.query(Kriteria).all()
    return render(request, "results.html", {
        "hasil": hasil, "sesi": sesi, "bobot": bobot,
        "kriteria": kriteria, "filter_niche": niche,
    })

@app.get("/detail/{username}", response_class=HTMLResponse)
def detail(request: Request, username: str, sesi_id: int = 0, db: Session = Depends(get_db)):
    kol = db.query(KolKandidat).filter(KolKandidat.username == username).first()
    ranking = None
    if sesi_id:
        ranking = db.query(HasilRanking).filter(
            HasilRanking.id_sesi == sesi_id,
            HasilRanking.username == username
        ).first()
    kriteria = db.query(Kriteria).all()
    return render(request, "detail.html", {
        "kol": kol, "ranking": ranking, "kriteria": kriteria,
        "sesi_id": sesi_id,
    })

@app.get("/riwayat", response_class=HTMLResponse)
def riwayat(request: Request, db: Session = Depends(get_db)):
    sesi_list = db.query(SesiKalkulasi).order_by(SesiKalkulasi.id.desc()).limit(20).all()
    return render(request, "riwayat.html", {"sesi_list": sesi_list})

@app.post("/riwayat/delete/{sesi_id}")
def hapus_sesi(sesi_id: int, db: Session = Depends(get_db)):
    db.query(HasilRanking).filter(HasilRanking.id_sesi == sesi_id).delete(synchronize_session=False)
    db.query(SesiKalkulasi).filter(SesiKalkulasi.id == sesi_id).delete(synchronize_session=False)
    db.commit()
    return RedirectResponse("/riwayat", status_code=303)

@app.post("/riwayat/delete-all")
def hapus_semua_sesi(db: Session = Depends(get_db)):
    db.query(HasilRanking).delete(synchronize_session=False)
    db.query(SesiKalkulasi).delete(synchronize_session=False)
    db.commit()
    return RedirectResponse("/riwayat", status_code=303)

@app.get("/hasil/{sesi_id}", response_class=HTMLResponse)
def lihat_hasil(request: Request, sesi_id: int, db: Session = Depends(get_db)):
    sesi = db.query(SesiKalkulasi).filter(SesiKalkulasi.id == sesi_id).first()
    hasil_rows = db.query(HasilRanking).filter(HasilRanking.id_sesi == sesi_id).order_by(HasilRanking.posisi).all()
    # Merge raw criterion values from KolKandidat (un-normalized C1-C5)
    usernames = [h.username for h in hasil_rows]
    kandidat_map = {
        k.username: k for k in db.query(KolKandidat).filter(KolKandidat.username.in_(usernames)).all()
    } if usernames else {}
    hasil = []
    for h in hasil_rows:
        k = kandidat_map.get(h.username)
        hasil.append({
            "username": h.username, "niche": h.niche,
            "followers": h.followers, "skor_total": h.skor_total, "posisi": h.posisi,
            "kontribusi_c1": h.kontribusi_c1, "kontribusi_c2": h.kontribusi_c2,
            "kontribusi_c3": h.kontribusi_c3, "kontribusi_c4": h.kontribusi_c4,
            "kontribusi_c5": h.kontribusi_c5,
            "r_c1": h.r_c1, "r_c2": h.r_c2, "r_c3": h.r_c3, "r_c4": h.r_c4, "r_c5": h.r_c5,
            "engagement_rate": k.engagement_rate if k else 0,
            "content_quality_score": k.content_quality_score if k else 0,
            "niche_relevance": k.niche_relevance if k else 0,
            "posting_consistency": k.posting_consistency if k else 0,
        })
    kriteria = db.query(Kriteria).all()
    bobot = sesi.bobot_json if sesi else DEFAULT_BOBOT
    return render(request, "results.html", {
        "hasil": hasil, "sesi": sesi, "bobot": bobot,
        "kriteria": kriteria, "filter_niche": sesi.filter_niche if sesi else "Semua",
    })

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    print("\n" + "=" * 50)
    print("  SPK Pemilihan KOL Instagram — F&B Bali")
    print("=" * 50)
    print(f"  Buka browser: http://localhost:{port}")
    print("=" * 50 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
