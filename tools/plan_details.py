"""Datos detallados de cada plan, tomados de las fichas comerciales de Bupa Seguros.

Solo contiene lo que aparece en los PDF oficiales (carpeta planes/, no publicada).
Si Bupa cambia una ficha, se edita aqui y se vuelve a correr build_pages.py.
"""

# Planes que no estaban en el sitio original. Se agregan a index_13.html (fichas)
# y tienen su propia pagina. Los datos de plan salen de aqui.
NEW_PLANS = {
    'proteccion-70-25': dict(
        name='+ Protección 70/25', tag='Exclusivo Fonasa',
        feats=['70% hospitalario y 25% ambulatorio, sin deducible',
               'Extensión catastrófica hasta UF 9.500',
               'Incluye seguro de vida por muerte accidental (UF 500)'],
        price_label='Tope anual', price='UF 500 /año',
        img='images/plans/proteccion-70-70.jpg', eyebrow='Exclusivo Fonasa',
        blurb='70% de cobertura hospitalaria y 25% ambulatoria, sin deducible, con extensión catastrófica hasta UF 9.500 y seguro de vida incluido.'),
    'cuidado-total-80': dict(
        name='Cuidado Total 80', tag='Libre elección · Isapre o Fonasa',
        feats=['80% de bonificación en clínicas de libre elección',
               'Consultas y videoconsultas ilimitadas',
               'Incluye maternidad, salud mental y urgencias'],
        price_label='Tope anual', price='UF 600 /año',
        img='images/plans/cuidado-total-70.jpg', eyebrow='Mayor cobertura',
        blurb='80% de bonificación en clínicas de libre elección, consultas ilimitadas y cobertura hasta UF 600 al año.'),
    'bupa-60-mas': dict(
        name='Bupa 60+', tag='Desde los 60 años · Isapre o Fonasa',
        feats=['70% de cobertura en consultas, exámenes y kinesiología',
               'Sin declaración de salud, sin deducible y sin bonificación mínima',
               'Orientación médica telefónica 24/7 con opción de ambulancia'],
        price_label='Desde', price='UF 1,03 /mes',
        img='images/plans/adulto-mayor.jpg', eyebrow='Desde los 60 años',
        blurb='70% de cobertura para mayores de 60 años, sin declaración de salud ni deducible, con tope anual de UF 200.'),
    'mi-dental-integramedica': dict(
        name='Mi Dental IntegraMédica 65%', tag='Plan dental · Sin sistema previsional',
        feats=['1 limpieza dental anual con costo $0',
               '65% de descuento en todos los tratamientos IntegraMédica',
               'Sin declaración de salud ni deducible; cubre preexistencias'],
        price_label='Descuento', price='65% dcto.',
        img='images/plans/integramedica-100.jpg', eyebrow='Plan dental',
        blurb='Limpieza dental anual a costo $0 y 65% de descuento en todos los tratamientos de la red dental IntegraMédica.'),
}

SALCOBRAND_CT = ('Descuentos en medicamentos ambulatorios en Salcobrand: con receta, 50% en genéricos y 30% en marca; '
                 'sin receta, 15% en genéricos y 10% en marca. Tope mensual de $25.000 por asegurado.')
DENTAL_RED = ('Beneficios dentales en la red de centros dentales IntegraMédica: control preventivo, consulta de diagnóstico '
              'y 1 limpieza bucal al año sin costo, y 62% a 65% de descuento sobre el arancel IntegraMédica en el resto de las prestaciones.')
DENTAL_62 = '62% de descuento en todo el arancel dental de IntegraMédica.'


def _ct(pct, tope, consulta, proc_ev, proc_yr, prev_ev):
    return dict(
        pol='POL320220083',
        rows=[
            ('Consultas médicas y de especialidad (incluye urgencia)', '%s%% · hasta UF %s por consulta' % (pct, consulta)),
            ('Exámenes de laboratorio e imagenología', '%s%% · sin tope' % pct),
            ('Procedimientos diagnósticos y terapéuticos', '%s%% · UF %s por evento · UF %s al año' % (pct, proc_ev, proc_yr)),
            ('Exámenes preventivos (mamografía, antígeno prostático, PAP)', '%s%% · UF %s por evento · UF 2 al año' % (pct, prev_ev)),
            ('Hospitalización y cirugías', '%s%% · día cama sin tope' % pct),
            ('Maternidad (parto, cesárea y complicaciones del embarazo)', '%s%%' % pct),
            ('Salud mental ambulatoria (psicología y psiquiatría)', 'Incluida'),
            ('Tope anual por beneficiario', 'UF %s' % tope),
        ],
        requisitos=[
            'Estar afiliado a Isapre o a Fonasa (tramos B, C o D).',
            'Completar la solicitud de incorporación con declaración de salud de todo el grupo familiar.',
            'Titular: desde los 18 años y hasta 75 años y 364 días al ingresar; sin límite de edad de permanencia.',
            'Dependientes (cónyuge o conviviente civil, hijos, padres, hermanos, abuelos, nietos, tíos, sobrinos, suegros y amigos): '
            'desde los 14 días de vida hasta 75 años y 364 días.',
        ],
        condiciones=[
            'Deducible de UF 1 al año por beneficiario, con un máximo de UF 3 por grupo familiar. Es $0 si te atiendes en la red de prestadores con convenio Bupa (Red Preferente, Red 1 y Red 2).',
            'Bonificación mínima (BMI): 50% para Isapre y 25% para Fonasa. Si tu sistema previsional aporta menos que eso, el seguro calcula sobre el costo directo descontando ese porcentaje.',
            'El seguro opera en exceso de tu Isapre o Fonasa: los gastos que tu sistema previsional no bonifica no tienen cobertura.',
            'En la red Bupa la cobertura aumenta: +12% en laboratorio e imagenología de IntegraMédica y +10% en laboratorio, imagenología, día cama, pabellón y servicios hospitalarios en Clínica Bupa Santiago, Reñaca y Antofagasta.',
            'Cobertura en el extranjero solo por accidente, con una permanencia de hasta 30 días.',
            'Cirugía bariátrica (con IMC de 40 o más), maxilofacial no accidental, septoplastía funcional, disforia de género y reducción mamaria tienen cobertura desde el primer año de vigencia.',
        ],
        adicionales=[SALCOBRAND_CT, DENTAL_RED],
        exclusiones=[
            'Medicamentos e insumos en la atención de urgencia.',
            'Psicología y psiquiatría en las consultas ilimitadas (la salud mental tiene su propia cobertura).',
            'Gastos que tu Isapre o Fonasa no bonifica.',
            'Otras exclusiones según las condiciones generales de la póliza (POL320220083).',
        ],
        ded='UF 1 al año por beneficiario (máx. UF 3 por grupo familiar); $0 en la red con convenio Bupa',
        edades='Titular de 18 a 75 años y 364 días; sin límite de permanencia',
    )


DETAIL = {}
DETAIL['cuidado-total-70'] = _ct(70, '400', '1', '0,5', '7', '0,5')
DETAIL['cuidado-total-60'] = _ct(60, '250', '0,6', '0,3', '5', '0,3')
DETAIL['cuidado-total-80'] = _ct(80, '600', '1,3', '0,7', '10', '0,7')

DETAIL['seguro-catastrofico'] = dict(
    pol='POL320260105',
    rows=[
        ('Cobertura', 'Hasta 100% sobre las prestaciones que cubre tu Isapre o Fonasa'),
        ('Prestaciones sin cobertura previsional', '50% para afiliados a Isapre y 25% para afiliados a Fonasa'),
        ('Tope por evento', 'UF 30.000 hasta los 69 años · UF 5.000 desde los 70 años'),
        ('Duración del evento', '3 años'),
        ('Deducible por evento', 'UF 100 hasta los 65 años · UF 200 desde los 66 años'),
        ('Deducible $0', 'Cáncer primario, infarto al miocardio, trasplante de órganos mayores, accidente vascular encefálico y apendicitis'),
        ('Carencia', 'Sin carencia en prestadores Bupa · 60 días desde el inicio de la vigencia en otros prestadores'),
        ('Dónde atenderte', 'Libre elección: tú eliges el centro médico o la clínica'),
    ],
    tarifas=dict(
        title='Tarifa mensual por edad',
        head=('Edad', 'Tarifa mensual'),
        rows=[('0 a 17 años', 'UF 0,25'), ('18 a 25 años', 'UF 0,39'), ('26 a 35 años', 'UF 0,49'),
              ('36 a 45 años', 'UF 0,64'), ('46 a 55 años', 'UF 0,91'), ('56 a 59 años', 'UF 1,26'),
              ('60 a 64 años', 'UF 1,81'), ('65 a 70 años', 'UF 1,95'), ('71 a 75 años', 'UF 3,21')],
        note='Tarifas brutas mensuales en UF, con recaudación anticipada de prima. La edad se calcula al inicio de la vigencia.',
    ),
    requisitos=[
        'Estar afiliado a Isapre o a Fonasa (tramos B, C o D).',
        'Declaración personal de salud (DPS) aprobada.',
        'Titular: desde los 18 años y hasta 75 años y 364 días al ingresar; sin límite de edad de permanencia.',
        'Dependientes (cónyuge o conviviente civil, hijos, padre y madre): desde los 14 días de vida hasta 75 años y 364 días.',
    ],
    condiciones=[
        'Es un seguro de libre elección: cubre prestaciones no cubiertas por tu Isapre o Fonasa y se activa ante enfermedades, accidentes y tratamientos oncológicos de alto costo.',
        'Cubre hospitalización (día cama, servicios hospitalarios, honorarios), cirugía ambulatoria, consultas, exámenes, imagenología, quimioterapia, radioterapia, kinesiología y rehabilitación, traslado en ambulancia y prótesis y órtesis.',
        'La cobertura de medicamentos ambulatorios con receta se activa una vez cubierto el deducible: 50% para Isapre y 25% para Fonasa.',
    ],
    adicionales=[
        'Telemedicina Bupa para videoconsultas generales y de especialidad en IntegraMédica, desde la Sucursal virtual de bupaseguros.cl.',
        'Servicios digitales de bienestar: rutinas de ejercicio, guías nutricionales, meditación y orientación de síntomas.',
    ],
    exclusiones=[
        'Preexistencias no declaradas, o declaradas y excluidas expresamente en la póliza.',
        'Parto normal y cesárea; aborto involuntario y complicaciones del embarazo o del parto cuando el embarazo comenzó antes de la vigencia.',
        'Hospitalización por causas psiquiátricas y enfermedades psicológicas y psiquiátricas.',
        'Tratamientos de fertilidad, infertilidad y esterilidad.',
        'Cirugías o tratamientos con fines estéticos, salvo que se deban a una lesión accidental; cirugía bariátrica con IMC menor a 40; reducción o aumento mamario y rinoplastía.',
        'Estudios y tratamientos por talla baja, gigantismo y hormonas del crecimiento.',
        'SIDA o cualquier cuadro causado o favorecido por el virus VIH, sus consecuencias y complicaciones.',
        'Otras exclusiones según las condiciones generales de la póliza (POL320260105).',
    ],
    ded='UF 100 por evento (UF 200 desde los 66 años); $0 en 5 patologías graves',
    edades='Titular de 18 a 75 años y 364 días; sin límite de permanencia',
)

_PROT_ADIC = [DENTAL_62,
              'Seguro de vida por muerte accidental: indemnización de UF 500 a los beneficiarios designados en la solicitud.']
_PROT_REQ = [
    'Pertenecer al sistema previsional de salud Fonasa.',
    'Completar la solicitud de incorporación con declaración de salud de todo el grupo familiar.',
    'Titular: desde los 18 años y hasta 75 años y 364 días al ingresar; sin límite de edad de permanencia.',
    'Dependientes (cónyuge o conviviente civil, hijos, padres, hermanos, abuelos, nietos, tíos, sobrinos, suegros y amigos): '
    'desde los 14 días de vida hasta 75 años y 364 días.',
]


def _prot(hosp, amb, promo_txt, ded_txt):
    return dict(
        pol='POL320220199',
        rows=[
            ('Seguro Base de Salud', 'Tope anual por beneficiario de UF 500'),
            ('Hospitalización y cirugías', '%s%% sobre el copago' % hosp),
            ('Atención ambulatoria (consultas, exámenes, imagenología, procedimientos)', '%s%% sobre el copago' % amb),
            ('Consultas de urgencia', 'Incluidas (en Clínica Bupa Santiago)'),
            ('Maternidad, oncología, prótesis y órtesis, ambulancia terrestre (hasta 50 km)', 'Incluidas'),
            ('Extensión catastrófica', '100% sobre el copago hasta UF 9.500 al año, una vez consumido el tope base'),
            ('Muerte accidental', 'Indemnización de UF 500'),
            ('Dónde se usa', 'Clínica Bupa Santiago y toda la red nacional de IntegraMédica'),
        ],
        requisitos=_PROT_REQ,
        condiciones=[
            ded_txt,
            promo_txt,
            'En prestaciones convenidas entre los prestadores del plan y Fonasa, el seguro bonifica como complemento a la cobertura de Fonasa; en las no convenidas, actúa sobre el valor acordado entre Bupa Seguros y el prestador.',
            'El seguro opera en exceso del sistema previsional, de Bienestar u otro seguro adicional.',
            'Para prestaciones convenidas con Fonasa, la atención se hace con Bono PAD y después se pide el reembolso del copago a la compañía; las urgencias vitales en Clínica Bupa Santiago se reembolsan con PAE.',
        ],
        adicionales=_PROT_ADIC,
        exclusiones=['Exclusiones y demás condiciones según la póliza POL320220199.'],
        ded='UF 0,5 al año ambulatorio y UF 5 al año hospitalario, por beneficiario',
        edades='Titular de 18 a 75 años y 364 días; sin límite de permanencia',
    )


_PROMO_VIGENTE = 'Promoción vigente: seguro sin deducible. Sin la promoción, el deducible es de UF 0,5 al año por beneficiario en cobertura ambulatoria y UF 5 al año en cobertura hospitalaria y cirugías.'
_DED_PROMO = 'Sin deducible con la promoción vigente (sin ella: UF 0,5 ambulatorio y UF 5 hospitalario al año)'

DETAIL['proteccion-80-70'] = _prot(80, 70, _PROMO_VIGENTE,
    'Deducible: UF 0,5 al año por beneficiario en cobertura ambulatoria y UF 5 al año en cobertura hospitalaria y cirugías.')
DETAIL['proteccion-80-70']['ded'] = _DED_PROMO
DETAIL['proteccion-70-25'] = _prot(70, 25, _PROMO_VIGENTE,
    'Deducible: UF 0,5 al año por beneficiario en cobertura ambulatoria y UF 5 al año en cobertura hospitalaria y cirugías.')
DETAIL['proteccion-70-25']['ded'] = _DED_PROMO
DETAIL['proteccion-70-70'] = _prot(70, 70,
    'Promoción vigente en la ficha comercial: si contratas hasta el 31 de diciembre de 2026, tu seguro queda sin deducible.',
    'Deducible: UF 0,5 al año por beneficiario en cobertura ambulatoria y UF 5 al año en cobertura hospitalaria y cirugías.')
DETAIL['proteccion-70-70']['ded'] = 'UF 0,5 ambulatorio y UF 5 hospitalario al año; sin deducible si contratas hasta el 31/12/2026'

DETAIL['proteccion-ambulatorio-70'] = dict(
    pol='POL320240029',
    rows=[
        ('Cobertura', '70% sobre el copago en atención ambulatoria'),
        ('Consultas de medicina general', 'Presenciales y videoconsultas ilimitadas'),
        ('Consultas médicas de especialidad', 'Presenciales ilimitadas (no cubre psicología ni psiquiatría)'),
        ('Exámenes', 'Laboratorio e imagenología simples y complejos'),
        ('Procedimientos', 'Diagnósticos y terapéuticos simples y complejos'),
        ('Urgencia ambulatoria', 'Incluida; si la atención deriva en una hospitalización, ninguna prestación de ese evento queda cubierta'),
        ('Tope anual por beneficiario', 'UF 250'),
        ('Dónde se usa', 'Clínica Bupa Santiago y toda la red nacional de IntegraMédica'),
    ],
    requisitos=[
        'Pertenecer al sistema previsional de salud Fonasa.',
        'Completar la solicitud de incorporación con declaración de salud de todo el grupo familiar.',
        'Titular: desde los 18 años y hasta 75 años y 364 días al ingresar; sin límite de edad de permanencia.',
        'Dependientes (cónyuge o conviviente civil, hijos, padres, hermanos, abuelos, nietos, tíos, sobrinos y suegros): desde los 14 días de vida hasta 75 años y 364 días.',
    ],
    condiciones=[
        'Deducible de UF 0,5 al año por beneficiario en cobertura ambulatoria.',
        'En prestaciones convenidas entre los prestadores del plan y Fonasa, el seguro bonifica como complemento a la cobertura de Fonasa; en las no convenidas, actúa sobre el valor acordado entre Bupa Seguros y el prestador.',
        'No incluye insumos ni medicamentos.',
        'El seguro opera en exceso del sistema previsional, de Bienestar u otro seguro adicional.',
    ],
    adicionales=[DENTAL_62],
    exclusiones=[
        'Hospitalización y cirugías: este plan no tiene cobertura hospitalaria.',
        'Psicología y psiquiatría.',
        'Insumos y medicamentos.',
        'Otras exclusiones según las condiciones generales de la póliza (POL320240029).',
    ],
    ded='UF 0,5 al año por beneficiario',
    edades='Titular de 18 a 75 años y 364 días; sin límite de permanencia',
)

DETAIL['multisalud'] = dict(
    pol='POL320230458',
    rows=[
        ('Seguro Base de Salud', 'Tope anual por beneficiario de UF 1.500'),
        ('Red preferente', '90% hospitalario y cirugías · 70% ambulatorio'),
        ('Red 1', '80% hospitalario y cirugías · 60% ambulatorio'),
        ('Red 2', '50% hospitalario y cirugías · 50% ambulatorio'),
        ('Consultas de medicina general', 'Presenciales y videoconsultas ilimitadas'),
        ('Salud mental ambulatoria (psicología y psiquiatría)', 'Hasta UF 0,5 por prestación y UF 5 al año'),
        ('Extensión catastrófica', 'En 2 capas, hasta UF 7.500 al año: capa 1 hasta UF 2.500 y capa 2 hasta UF 5.000 adicionales'),
        ('Cobertura de la extensión catastrófica', '100% en red preferente · 90% en Red 1 · no aplica en Red 2'),
    ],
    requisitos=[
        'Pertenecer a Fonasa, tramos B, C o D.',
        'Completar la solicitud de incorporación con declaración de salud de todo el grupo familiar.',
        'Titular: desde los 18 años y hasta 75 años y 364 días al ingresar; sin límite de edad de permanencia.',
        'Dependientes (cónyuge o conviviente civil, hijos, padres, hermanos, abuelos, nietos, tíos, sobrinos, suegros y amigos): desde los 14 días de vida hasta 75 años y 364 días.',
    ],
    condiciones=[
        'Opera con 3 redes de prestadores privados en la Región Metropolitana y en las principales regiones. La cobertura cambia según la red, y la compañía puede modificar los prestadores de cada una.',
        'Deducible: UF 1 al año por beneficiario en cobertura ambulatoria y UF 5 al año en cobertura hospitalaria, maternidad, oncología, prótesis, salud mental y traslado.',
        'La compañía reembolsa o paga prestaciones sobre las que se aplica el arancel Fonasa (MLE).',
        'El seguro opera en exceso del sistema previsional, de Bienestar u otro seguro adicional.',
        'Cirugía bariátrica (con IMC de 40 o más), rinolaringológica, reducción mamaria, láser ocular y reasignación de sexo tienen cobertura desde el primer año de vigencia.',
    ],
    adicionales=[DENTAL_62],
    exclusiones=[
        'Atenciones fuera de la red de prestadores del plan.',
        'Otras exclusiones según las condiciones generales de la póliza (POL320230458).',
    ],
    ded='UF 1 ambulatorio y UF 5 hospitalario al año, por beneficiario',
    edades='Titular de 18 a 75 años y 364 días; sin límite de permanencia',
)

DETAIL['complementa'] = dict(
    pol='POL320260033',
    rows=[
        ('Cómo funciona', 'Cubre el copago en la misma proporción que tu plan de Isapre (si tu plan cubre 80%, Complementa cubre 80% de tu copago)'),
        ('Hospitalización y cirugías', 'Libre elección, excepto Clínica Universidad de los Andes, Clínica Las Condes y Clínica Alemana'),
        ('Maternidad, procedimientos y cobertura oncológica', 'Incluidos'),
        ('Atención ambulatoria', 'Consultas y videoconsultas, exámenes, imagenología, cirugía ambulatoria, kinesiología, fonoaudiología y salud mental; exclusiva en prestadores Bupa'),
        ('Deducible y bonificación mínima', 'Sin deducible y sin BMI'),
        ('Tope anual por beneficiario', 'UF 500'),
    ],
    requisitos=[
        'Estar y permanecer afiliado a Isapre durante toda la vigencia del seguro. No cubre a afiliados a Fonasa.',
        'Completar la solicitud de incorporación con declaración de salud de todo el grupo familiar.',
        'Titular: desde los 18 años y hasta 70 años y 364 días al ingresar; sin límite de edad de permanencia.',
        'Dependientes (cónyuge o conviviente civil, hijos, padres, hermanos, abuelos, nietos, tíos, primos, sobrinos, suegros y amigos): desde los 14 días de vida hasta 70 años y 364 días.',
    ],
    condiciones=[
        'Si tu Isapre no bonifica una prestación, el seguro tampoco la cubre.',
        'La cobertura ambulatoria es exclusiva en Clínica Bupa Santiago, Clínica Bupa Reñaca y los centros médicos IntegraMédica.',
        'El seguro opera en exceso de tu Isapre, de Bienestar u otro seguro adicional.',
        'Cirugía bariátrica (con IMC de 40 o más), maxilofacial no accidental, rinolaringológica, reasignación de sexo, vasectomía y reducción mamaria tienen cobertura desde el primer año de vigencia.',
        'Cirugía láser ocular para miopía, hipermetropía y astigmatismo con más de 5 dioptrías en cada ojo.',
    ],
    adicionales=[],
    exclusiones=[
        'Afiliados a Fonasa u otros sistemas previsionales distintos de Isapre.',
        'Hospitalizaciones en Clínica Universidad de los Andes, Clínica Las Condes y Clínica Alemana.',
        'Otras exclusiones según las condiciones generales de la póliza (POL320260033).',
    ],
    ded='Sin deducible y sin bonificación mínima (BMI)',
    edades='Titular de 18 a 70 años y 364 días; sin límite de permanencia',
)

DETAIL['integramedica-100'] = dict(
    pol=None,
    rows=[
        ('Cobertura', '100% sobre el copago, después de aplicar tu Isapre o Fonasa y cualquier otro seguro vigente'),
        ('Consultas médicas', 'Medicina general y de especialidad (no incluye psiquiatría ni psicología) y nutricionista con prescripción médica'),
        ('Exámenes', 'Laboratorio y anatomía patológica; radiografías, ecografías y ecotomografías'),
        ('Con carencia de 4 meses', 'Scanner (TAC), resonancia magnética, procedimientos diagnósticos y terapéuticos y kinesiología'),
        ('Kinesiología', 'Hasta 12 sesiones al año (incluye sesión de evaluación)'),
        ('Tope anual por beneficiario', 'UF 60'),
        ('Dónde se usa', 'Centros médicos IntegraMédica del país; la bonificación es en línea mediante el sistema I-Med'),
    ],
    requisitos=[
        'Estar afiliado a Isapre o a Fonasa (grupos B, C y D).',
        'No requiere declaración de salud y cubre preexistencias.',
        'Contratante: desde los 18 años y hasta 64 años y 364 días al ingresar; permanencia hasta 74 años y 364 días.',
        'Beneficiarios dependientes: desde el nacimiento hasta 64 años y 364 días; no necesitan tener un vínculo familiar con el contratante.',
    ],
    condiciones=[
        'Sin deducible.',
        'Las prestaciones cubiertas por el plan que no tengan cobertura de tu sistema previsional se bonifican al 50%.',
        'La cobertura se basa en la oferta de servicios médicos disponibles en los centros IntegraMédica del país.',
        'El plan opera presentando la cédula de identidad en el centro médico. Los menores de 18 años deben ir acompañados por un adulto.',
        'Si contratas entre el 1 y el 30 del mes, la vigencia comienza el primer día hábil del mes siguiente.',
    ],
    adicionales=[
        'Descuentos en medicamentos en compras presenciales en Salcobrand: con receta, 50% en genéricos y 20% en marca; sin receta, 15% en genéricos y 10% en marca. Tope mensual de $15.000 por beneficiario.',
    ],
    exclusiones=[
        'Prestaciones de salud mental.',
        'Cirugía oftalmológica.',
        'Fonoaudiología, terapia ocupacional y psicopedagogía.',
        'Dermoestética.',
        'Insumos, medicamentos y ortopedia.',
        'Cualquier prestación que no forme parte de la oferta de IntegraMédica.',
    ],
    ded='Sin deducible',
    edades='Contratante de 18 a 64 años y 364 días; permanencia hasta 74 años y 364 días',
)

DETAIL['adulto-mayor-integramedica-70'] = dict(
    pol=None,
    rows=[
        ('Cobertura', '70% en atenciones médicas dentro de la red de centros médicos IntegraMédica'),
        ('Consultas', 'Medicina general y especialidad, presenciales y por videoconsulta (no incluye psicología ni psiquiatría)'),
        ('Exámenes', 'Laboratorio, imagenología simple y compleja, exámenes diagnósticos de alta complejidad, PCR Covid-19 y papanicolaou (PAP)'),
        ('Tope por beneficiario', 'UF 25'),
        ('Rescate de riesgo vital', 'Unidad Coronaria Móvil: asistencia telefónica y envío de ambulancia, 24/7 en todo el territorio nacional'),
    ],
    requisitos=[
        'Estar afiliado a Isapre o a Fonasa.',
        'Cubre enfermedades preexistentes (sin preexistencias).',
        'Ingreso desde los 60 años y hasta 84 años y 364 días; permanencia hasta 99 años y 364 días.',
        'Puedes contratarlo para ti, tu cónyuge, pareja, hijos, padres, abuelos, familiares e incluso amigos, siempre que cumplan los requisitos de contratación.',
    ],
    condiciones=[
        'Las coberturas se aplican en línea mediante el sistema de huella I-Med.',
        'La cobertura aplica en la red de centros médicos IntegraMédica.',
    ],
    adicionales=[
        'Descuentos en farmacias Salcobrand para medicamentos con y sin receta, genéricos y de marca, además de productos para el adulto mayor especificados en el contrato.',
    ],
    exclusiones=[
        'Psicología y psiquiatría en las consultas.',
        'Atenciones fuera de la red de centros médicos IntegraMédica.',
    ],
    ded=None,
    edades='Ingreso de 60 a 84 años y 364 días; permanencia hasta 99 años y 364 días',
)

DETAIL['bupa-60-mas'] = dict(
    pol='POL320260183',
    rows=[
        ('Cobertura', '70% sobre el copago en atenciones ambulatorias, de urgencia y hospitalizaciones derivadas de urgencia traumatológica'),
        ('Atención ambulatoria', 'Consultas médicas generales y de especialidad (presenciales o por telemedicina; no incluye psicología ni psiquiatría), consulta de urgencia, exámenes de laboratorio e imagenología, procedimientos diagnósticos y kinesiología'),
        ('Kinesiología', 'Hasta 10 sesiones al año'),
        ('Con carencia (se activan desde el 4.º mes)', 'Scanner, resonancia magnética y anatomía patológica; hospitalización derivada de urgencia traumatológica; prótesis y órtesis (hasta UF 50) y ambulancia terrestre (hasta UF 10)'),
        ('Exámenes preventivos', 'Costo $0'),
        ('Tope anual por asegurado', 'UF 200'),
        ('Dónde se usa', 'Clínica Bupa Santiago, Clínica Bupa Reñaca y toda la red nacional de IntegraMédica'),
    ],
    tarifas=dict(
        title='Tarifa mensual por edad',
        head=('Edad', 'Tarifa mensual'),
        rows=[('60 a 64 años', 'UF 1,03'), ('65 a 70 años', 'UF 1,16'), ('71 a 75 años', 'UF 1,23'),
              ('76 a 80 años', 'UF 1,38'), ('81 años en adelante', 'UF 1,67')],
        note='Tarifas brutas mensuales en UF, con recaudación anticipada de prima. La edad se calcula al inicio de la vigencia.',
    ),
    requisitos=[
        'Pertenecer al sistema previsional de Isapre o Fonasa.',
        'Sin declaración de salud.',
        'Titular o dependiente: desde los 60 años y hasta 84 años y 364 días al ingresar; sin límite de edad de permanencia.',
        'Dependientes: cónyuge, conviviente civil, padre, madre y abuelos. Permite contratación para terceros.',
    ],
    condiciones=[
        'Sin bonificación mínima (BMI) y sin deducible.',
        'Cuando la prestación tiene bonificación de Fonasa o de Isapre, el seguro opera como complemento de esa cobertura.',
        'Afiliados a Fonasa: si la prestación no tiene bonificación de Fonasa, el seguro igualmente puede darle cobertura según las condiciones, porcentajes y topes del plan.',
        'Afiliados a Isapre: la prestación debe contar antes con cobertura de la Isapre para que el seguro opere.',
        'La cobertura de prótesis, órtesis y ambulancia solo aplica cuando nace directamente de una urgencia traumatológica cubierta, atendida en la red de prestadores y con derivación hospitalaria del médico tratante.',
    ],
    adicionales=[
        'Descuentos sobre el copago final: 15% en consultas generales y de especialidad, 20% en exámenes de laboratorio y 25% en imagenología.',
        '65% de descuento sobre el arancel de IntegraMédica.',
        'Descuentos en farmacias Salcobrand: con receta, 60% en genéricos y 40% en marca; sin receta, 15% en genéricos y 10% en marca.',
        'Orientación y asistencia médica telefónica 24/7 con opción de ambulancia ante emergencias de riesgo vital, y atención preferencial en línea o presencial.',
        'Beneficios recreativos en línea y presenciales (BondUP).',
    ],
    exclusiones=[
        'Psicología y psiquiatría.',
        'Hospitalización que no derive de una urgencia traumatológica.',
        'Otras exclusiones según las condiciones generales de la póliza (POL320260183).',
    ],
    ded='Sin deducible y sin bonificación mínima (BMI)',
    edades='Ingreso de 60 a 84 años y 364 días; sin límite de permanencia',
)

DETAIL['mi-dental-integramedica'] = dict(
    pol=None,
    rows=[
        ('Descuento', '65% sobre el arancel IntegraMédica en todos los tratamientos dentales'),
        ('Costo $0', '1 limpieza dental anual (evaluación, destartraje y profilaxis); higiene y profilaxis en niños, 1 al año'),
        ('Radiografías diagnósticas dentales', 'Bitewing bilateral (1 al año) y retroalveolar (4 placas al año)'),
        ('Bonificación', 'En línea mediante I-Med'),
        ('Dónde se usa', 'Centros médicos con clínica dental de la red IntegraMédica'),
    ],
    requisitos=[
        'No requiere pertenecer a ningún sistema previsional.',
        'Sin declaración de salud; cubre preexistencias.',
        'Contratante: desde los 18 años. Ingreso hasta 89 años y 364 días; permanencia hasta 99 años y 364 días.',
        'Beneficiarios: desde el nacimiento hasta 89 años y 364 días, sin necesidad de vínculo familiar con el contratante. Permite contratación para terceros y suscripción digital.',
    ],
    condiciones=[
        'Sin deducible. Plan anualmente renovable.',
        'El beneficio dental parte desde el segundo mes de vigencia.',
        'Agenda y confirma disponibilidad de atención antes de asistir.',
        'Las radiografías diagnósticas que ya hayas pagado no se reembolsan.',
        'La red IntegraMédica está en Santiago, Copiapó, La Serena, Viña del Mar, Rancagua, Talca y Concepción.',
    ],
    adicionales=[
        'Descuentos en farmacias Salcobrand: con receta, 50% en genéricos y 20% en marca (tope mensual de $20.000); sin receta, 15% en genéricos y 10% en marca (tope mensual de $15.000).',
        '12% de descuento en accesorios dentales (cepillos, enjuagues y pastas dentales).',
    ],
    exclusiones=[
        'Es un plan dental: no cubre atenciones médicas ni hospitalización.',
        'Tratamientos fuera de la red dental IntegraMédica.',
    ],
    ded='Sin deducible',
    edades='Contratante desde los 18 años; ingreso hasta 89 años y 364 días',
)

# Pymes: la ficha disponible es una cotizacion a medida para una empresa, no un folleto.
# No se publica nada de ella.
DETAIL['pymes-70-smart'] = None
