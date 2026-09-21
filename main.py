import os,csv,io,uuid,secrets
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import FastAPI,Request,HTTPException
from fastapi.responses import HTMLResponse,RedirectResponse,StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from openpyxl import Workbook
from database import SessionLocal,Assessment
from clinical import calculate_bmi,calculate_non_hdl,calculate_fib4,fib4_category,cv_algorithm_selector,validate_clinical,FIB4_VERSION,RCV_SELECTOR_VERSION

BASE=Path(__file__).resolve().parent
APP_USERNAME=os.getenv('APP_USERNAME','ehmet')
APP_PASSWORD=os.getenv('APP_PASSWORD','cambiar-esta-clave')
SESSION_SECRET=os.getenv('SESSION_SECRET','dev-secret-change-me')
app=FastAPI(title='ehMET')
app.add_middleware(SessionMiddleware,secret_key=SESSION_SECRET,https_only=os.getenv('ENVIRONMENT','development')=='production',same_site='lax',max_age=28800)
app.mount('/static',StaticFiles(directory=BASE/'static'),name='static')
templates=Jinja2Templates(directory=BASE/'templates')

class AssessmentIn(BaseModel):
    age:Optional[int]=None; sex:Optional[str]=None; weight:Optional[float]=None; height:Optional[float]=None; waist:Optional[float]=None
    sbp:Optional[float]=None; dbp:Optional[float]=None; smoking:Optional[str]=None; antihypertensive:bool=False; established_cvd:bool=False
    diabetes:Optional[str]='No'; diabetes_years:Optional[float]=None; age_diabetes_dx:Optional[float]=None; hba1c:Optional[float]=None
    total_chol:Optional[float]=None; hdl:Optional[float]=None; ldl:Optional[float]=None; triglycerides:Optional[float]=None; lipid_lowering:bool=False
    creatinine:Optional[float]=None; egfr:Optional[float]=None; ast:Optional[float]=None; alt:Optional[float]=None; platelets:Optional[float]=None; ggt:Optional[float]=None
    cv_risk:Optional[float]=None; cv_risk_category:Optional[str]=None; cv_risk_source:Optional[str]=None
    site_code:Optional[str]=None; professional_code:Optional[str]=None; notes:Optional[str]=None

def auth(request):
    if not request.session.get('authenticated'): raise HTTPException(401,'No autenticado')
def asdict(a): return {c.name:getattr(a,c.name) for c in a.__table__.columns}

@app.get('/health')
def health(): return {'status':'ok'}
@app.get('/login',response_class=HTMLResponse)
def login_page(request:Request):
    if request.session.get('authenticated'): return RedirectResponse('/',303)
    return templates.TemplateResponse('login.html',{'request':request,'error':None})
@app.post('/login',response_class=HTMLResponse)
async def login(request:Request):
    f=await request.form(); u=str(f.get('username','')); p=str(f.get('password',''))
    if secrets.compare_digest(u,APP_USERNAME) and secrets.compare_digest(p,APP_PASSWORD):
        request.session['authenticated']=True; return RedirectResponse('/',303)
    return templates.TemplateResponse('login.html',{'request':request,'error':'Usuario o contraseña incorrectos.'},status_code=401)
@app.post('/logout')
def logout(request:Request): request.session.clear(); return RedirectResponse('/login',303)
@app.get('/',response_class=HTMLResponse)
def home(request:Request):
    if not request.session.get('authenticated'): return RedirectResponse('/login',303)
    return templates.TemplateResponse('index.html',{'request':request})
@app.post('/api/assessments')
def create(data:AssessmentIn,request:Request):
    auth(request); d=data.model_dump(); bmi=calculate_bmi(data.weight,data.height); nonhdl=calculate_non_hdl(data.total_chol,data.hdl)
    f4=calculate_fib4(data.age,data.ast,data.alt,data.platelets); fcat=fib4_category(f4,data.age); sel=cv_algorithm_selector(data.age,data.diabetes,data.established_cvd,data.egfr)
    r=Assessment(anonymous_id=f'EHMET-{datetime.now().year}-{uuid.uuid4().hex[:10].upper()}',created_at=datetime.now(),age=data.age,sex=data.sex,weight=data.weight,height=data.height,bmi=bmi,waist=data.waist,sbp=data.sbp,dbp=data.dbp,smoking=data.smoking,antihypertensive=data.antihypertensive,established_cvd=data.established_cvd,diabetes=data.diabetes,diabetes_years=data.diabetes_years,age_diabetes_dx=data.age_diabetes_dx,hba1c=data.hba1c,total_chol=data.total_chol,hdl=data.hdl,ldl=data.ldl,non_hdl=nonhdl,triglycerides=data.triglycerides,lipid_lowering=data.lipid_lowering,creatinine=data.creatinine,egfr=data.egfr,ast=data.ast,alt=data.alt,platelets=data.platelets,ggt=data.ggt,fib4=f4,fib4_category=fcat,fib4_version=FIB4_VERSION,cv_algorithm=sel['algorithm'],cv_risk=data.cv_risk,cv_risk_category=data.cv_risk_category,cv_risk_source=data.cv_risk_source,rcv_version=RCV_SELECTOR_VERSION,site_code=data.site_code,professional_code=data.professional_code,notes=data.notes)
    with SessionLocal() as db: db.add(r); db.commit(); db.refresh(r); out=asdict(r)
    out['cv_selector_message']=sel['message']; out['warnings']=validate_clinical(d); return out
@app.get('/api/assessments')
def listing(request:Request):
    auth(request)
    with SessionLocal() as db: return [asdict(x) for x in db.query(Assessment).order_by(Assessment.id.desc()).limit(1000).all()]
@app.delete('/api/assessments/{anonymous_id}')
def delete(anonymous_id:str,request:Request):
    auth(request)
    with SessionLocal() as db:
        r=db.query(Assessment).filter(Assessment.anonymous_id==anonymous_id).first()
        if not r: raise HTTPException(404,'Registro no encontrado')
        db.delete(r); db.commit()
    return {'ok':True}
@app.get('/api/stats')
def stats(request:Request):
    auth(request)
    with SessionLocal() as db: rows=db.query(Assessment).all()
    n=len(rows)
    if not n:return {'n':0}
    def mean(attr,subset=None):
        src=rows if subset is None else subset; vals=[getattr(r,attr) for r in src if getattr(r,attr) is not None]
        return round(sum(vals)/len(vals),2) if vals else None
    fib={}; diabetes=obesity=smoker=0
    for r in rows:
        fib[r.fib4_category or 'Sin dato']=fib.get(r.fib4_category or 'Sin dato',0)+1
        diabetes+=1 if r.diabetes in ('DM1','DM2') else 0; obesity+=1 if r.bmi is not None and r.bmi>=30 else 0; smoker+=1 if r.smoking=='Actual' else 0
    dm=[r for r in rows if r.diabetes in ('DM1','DM2')]
    return {'n':n,'mean_age':mean('age'),'mean_bmi':mean('bmi'),'mean_ldl':mean('ldl'),'mean_hba1c_diabetes':mean('hba1c',dm),'diabetes_pct':round(100*diabetes/n,1),'obesity_pct':round(100*obesity/n,1),'current_smoker_pct':round(100*smoker/n,1),'fib4_categories':fib}
def export_rows():
    with SessionLocal() as db:return [asdict(x) for x in db.query(Assessment).order_by(Assessment.id).all()]
@app.get('/export/csv')
def csv_export(request:Request):
    auth(request); rows=export_rows()
    if not rows: raise HTTPException(404,'No hay registros')
    fields=[k for k in rows[0] if k!='id']; s=io.StringIO(); w=csv.DictWriter(s,fieldnames=fields); w.writeheader(); [w.writerow({k:r[k] for k in fields}) for r in rows]
    return StreamingResponse(io.BytesIO(s.getvalue().encode('utf-8-sig')),media_type='text/csv',headers={'Content-Disposition':'attachment; filename="ehmet_export.csv"'})
@app.get('/export/xlsx')
def xlsx_export(request:Request):
    auth(request); rows=export_rows()
    if not rows: raise HTTPException(404,'No hay registros')
    fields=[k for k in rows[0] if k!='id']; wb=Workbook(); ws=wb.active; ws.title='ehMET'; ws.append(fields)
    for r in rows: ws.append([r[k] for k in fields])
    b=io.BytesIO(); wb.save(b); b.seek(0)
    return StreamingResponse(b,media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':'attachment; filename="ehmet_export.xlsx"'})
