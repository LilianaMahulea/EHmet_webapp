import math

FIB4_VERSION = 'EHMET-FIB4-1.1'
RCV_SELECTOR_VERSION = 'EHMET-RCV-SELECTOR-1.1'

def calculate_bmi(weight_kg, height_cm):
    if weight_kg is None or height_cm is None or weight_kg <= 0 or height_cm <= 0:
        return None
    return round(weight_kg / ((height_cm / 100.0) ** 2), 2)

def calculate_non_hdl(total_chol, hdl):
    if total_chol is None or hdl is None or total_chol < 0 or hdl < 0:
        return None
    return round(total_chol - hdl, 1)

def calculate_fib4(age, ast, alt, platelets):
    if None in (age, ast, alt, platelets):
        return None
    if age <= 0 or ast < 0 or alt <= 0 or platelets <= 0:
        return None
    return round((age * ast) / (platelets * math.sqrt(alt)), 2)

def fib4_category(value, age=None):
    if value is None:
        return 'No calculable'
    if age is not None and age >= 65:
        if value < 2.0: return 'Bajo'
        if value <= 2.67: return 'Intermedio'
        return 'Elevado'
    if value < 1.3: return 'Bajo'
    if value <= 2.67: return 'Intermedio'
    return 'Elevado'

def cv_algorithm_selector(age, diabetes, established_cvd=False, egfr=None):
    if established_cvd:
        return {'algorithm':'No aplicar SCORE2','message':'Enfermedad cardiovascular establecida: no debe estratificarse exclusivamente mediante SCORE2.'}
    if egfr is not None and egfr < 30:
        return {'algorithm':'No aplicar SCORE2 de forma aislada','message':'eGFR <30 mL/min/1,73m²: valorar el riesgo según la guía correspondiente.'}
    if diabetes == 'DM2':
        return {'algorithm':'SCORE2-Diabetes','message':'Si cumple criterios, utilizar SCORE2-Diabetes; requiere variables específicas de diabetes.'}
    if diabetes == 'DM1':
        return {'algorithm':'Valoración específica DM1','message':'SCORE2-Diabetes está diseñado para DM2; aplicar estratificación específica según guía.'}
    if age is None:
        return {'algorithm':'Pendiente','message':'Falta la edad.'}
    if 40 <= age <= 69:
        return {'algorithm':'SCORE2','message':'España corresponde a la región SCORE2 de bajo riesgo.'}
    if age >= 70:
        return {'algorithm':'SCORE2-OP','message':'Utilizar SCORE2-OP en personas de 70 años o más.'}
    return {'algorithm':'Fuera de rango SCORE2','message':'SCORE2 estándar no está validado para este rango de edad.'}

def validate_clinical(d):
    w=[]
    age=d.get('age'); sbp=d.get('sbp'); dbp=d.get('dbp'); tc=d.get('total_chol'); hdl=d.get('hdl'); alt=d.get('alt'); p=d.get('platelets')
    if age is not None and not (18 <= age <= 120): w.append('Edad fuera de rango plausible.')
    if sbp is not None and dbp is not None and sbp < dbp: w.append('La PAS es inferior a la PAD.')
    if alt is not None and alt <= 0: w.append('ALT debe ser >0 para calcular FIB-4.')
    if p is not None and p <= 0: w.append('Las plaquetas deben ser >0 para calcular FIB-4.')
    if tc is not None and hdl is not None and hdl > tc: w.append('HDL mayor que colesterol total: revisar datos/unidades.')
    return w
