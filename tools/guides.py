"""Guias de contenido (articulos). Cada una usa solo datos de las fichas comerciales de Bupa
o definiciones generales; las cifras de los planes salen de plan_details.py.

Se generan en /guias/<slug>/ con build_pages.py. La guia 'isapre-vs-fonasa...' vive en build_pages.py.
"""
import html as _h

from plan_details import DETAIL

PUBLISHED = '2026-10-20'


def _e(t):
    return _h.escape(t, quote=False)


def _table(head, rows):
    th = ''.join('<th>%s</th>' % _e(h) for h in head)
    body = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % c for c in r) for r in rows)
    return '<div class="table-scroll"><table class="cmp-table"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (th, body)


def _bul(items):
    return '<ul class="bullets">%s</ul>' % ''.join('<li>%s</li>' % i for i in items)


def _fill(tmpl, **kw):
    for k, v in kw.items():
        tmpl = tmpl.replace('[[%s]]' % k, v)
    assert '[[' not in tmpl, 'marcador sin reemplazar'
    return tmpl


def _plan(slug, label):
    return '<a href="/planes/%s/">%s</a>' % (slug, label)


_TARIFAS_CAT = DETAIL['seguro-catastrofico']['tarifas']['rows']
_TARIFAS_60 = DETAIL['bupa-60-mas']['tarifas']['rows']

# ---------------------------------------------------------------------------------------------
# 1) Seguro catastrofico
# ---------------------------------------------------------------------------------------------
CATASTROFICO_BODY = '''
<p>Una cirugía compleja, un tratamiento oncológico o una hospitalización larga pueden costar mucho más de lo que tu Isapre o Fonasa cubren. El seguro catastrófico existe para ese tipo de eventos: no está pensado para la consulta del día a día, sino para protegerte cuando el gasto se dispara.</p>

<h2>Qué es y cómo funciona</h2>
<p>Un seguro catastrófico es un seguro complementario de salud que se activa ante enfermedades, accidentes y tratamientos oncológicos de alto costo. En el caso del [[cat]], la cobertura es de libre elección: tú eliges el centro médico o la clínica donde atenderte.</p>
[[funciona]]
<p>Funciona sobre lo que cubre tu sistema previsional: cubre hasta el 100% de las prestaciones que tu Isapre o Fonasa cubren, y para las prestaciones que tu sistema no cubre, el seguro aporta el 50% (Isapre) o el 25% (Fonasa). Antes de que el seguro pague, se descuenta un deducible por evento.</p>

<h2>Las cifras del Seguro Bupa Catastrófico</h2>
[[cifras]]

<h2>Cuánto cuesta por edad</h2>
<p>La tarifa depende de la edad al inicio de la vigencia y se expresa en UF mensuales:</p>
[[tarifas]]
<p class="article-meta">Tarifas brutas mensuales en UF, con recaudación anticipada de prima. Revisa los valores vigentes al cotizar.</p>

<h2>Cuándo puede convenirte</h2>
[[conviene]]

<h2>Cuándo puede no ser suficiente</h2>
[[noconviene]]

<h2>Qué no cubre</h2>
[[excl]]

<h2>Catastrófico frente a otros seguros</h2>
<p>No son excluyentes: cada uno cumple un rol distinto.</p>
[[comparacion]]

<h2>Requisitos para contratarlo</h2>
[[req]]

<p>Tu sistema previsional puede tener sus propias coberturas para enfermedades graves (por ejemplo GES o CAEC); revisa tu plan o tu contrato para ver cómo se combinan con el seguro.</p>
'''


def _catastrofico():
    d = DETAIL['seguro-catastrofico']
    cifras = _table(('Concepto', 'Detalle'), [(_e(a), _e(b)) for a, b in d['rows']])
    funciona = ''
    tarifas = _table(('Edad', 'Tarifa mensual'), [(_e(a), _e(b)) for a, b in _TARIFAS_CAT])
    conviene = _bul([
        'Quieres protegerte de un gasto muy alto sin contratar un seguro de cobertura completa.',
        'Ya estás conforme con tu Isapre o Fonasa para el uso habitual y buscas una capa adicional para eventos graves.',
        'Tienes un presupuesto acotado: la tarifa parte desde UF 0,39 al mes para adultos de 18 a 25 años.',
        'Buscas libertad para elegir la clínica donde atenderte.',
    ])
    noconviene = _bul([
        'Si quieres cubrir consultas, exámenes y procedimientos habituales, mira ' + _plan('cuidado-total-70', 'Cuidado Total') + ' o, si eres de Fonasa, ' + _plan('proteccion-70-70', '+ Protección') + '.',
        'Si estás planeando un embarazo: el parto normal, la cesárea y las complicaciones del embarazo no están cubiertos.',
        'Si buscas cobertura de hospitalización por causas psiquiátricas: está excluida.',
        'Si tienes enfermedades preexistentes: las no declaradas, o declaradas y excluidas en la póliza, no tienen cobertura.',
    ])
    excl = _bul([_e(x) for x in d['exclusiones'][:-1]])
    comparacion = _table(('Seguro', 'Para qué sirve', 'Tope'), [
        (_plan('seguro-catastrofico', 'Catastrófico'), 'Eventos de alto costo, libre elección', 'UF 30.000 por evento (hasta los 69 años)'),
        (_plan('cuidado-total-70', 'Cuidado Total 70'), 'Uso habitual y hospitalización, libre elección', 'UF 400 al año por beneficiario'),
        (_plan('proteccion-70-70', '+ Protección 70/70'), 'Base de salud más extensión catastrófica (solo Fonasa)', 'UF 500 de base y hasta UF 9.500 de extensión catastrófica'),
        (_plan('multisalud', 'MultiSalud'), 'Base de salud y extensión catastrófica en 3 redes (Fonasa B, C o D)', 'UF 1.500 de base y hasta UF 7.500 de extensión catastrófica'),
    ])
    req = _bul([_e(x) for x in d['requisitos']])
    return _fill(CATASTROFICO_BODY, **dict(cat=_plan('seguro-catastrofico', 'Seguro Bupa Catastrófico'), funciona=funciona,
                                    cifras=cifras, tarifas=tarifas, conviene=conviene, noconviene=noconviene,
                                    excl=excl, comparacion=comparacion, req=req))


CATASTROFICO_FAQ = [
    ('¿Qué es un seguro catastrófico de salud?',
     'Es un seguro complementario que se activa ante enfermedades, accidentes y tratamientos oncológicos de alto costo. No está pensado para las atenciones habituales, sino para eventos graves.'),
    ('¿Cuánto cubre el Seguro Bupa Catastrófico?',
     'Hasta el 100% de las prestaciones que cubre tu Isapre o Fonasa, y 50% (Isapre) o 25% (Fonasa) de las que tu sistema no cubre. El tope por evento es de UF 30.000 hasta los 69 años y de UF 5.000 desde los 70 años.'),
    ('¿Tiene deducible el Seguro Bupa Catastrófico?',
     'Sí: UF 100 por evento hasta los 65 años y UF 200 desde los 66 años. Es $0 para 5 patologías: cáncer primario, infarto al miocardio, trasplante de órganos mayores, accidente vascular encefálico y apendicitis.'),
    ('¿Cuánto cuesta el Seguro Bupa Catastrófico?',
     'La tarifa mensual depende de la edad: parte en UF 0,25 para menores de 18 años y UF 0,39 de 18 a 25 años, y llega a UF 3,21 entre los 71 y 75 años.'),
    ('¿Quién puede contratar el Seguro Bupa Catastrófico?',
     'Afiliados a Isapre o a Fonasa (tramos B, C o D), con declaración personal de salud aprobada. El titular puede ingresar desde los 18 hasta los 75 años y 364 días, y no hay límite de edad de permanencia.'),
]

# ---------------------------------------------------------------------------------------------
# 2) Adultos mayores y preexistencias
# ---------------------------------------------------------------------------------------------
ADULTOS_BODY = '''
<p>Después de los 60 años, contratar un seguro de salud se vuelve más difícil: hay límites de edad de ingreso, la tarifa sube con los años y muchas personas ya tienen alguna enfermedad diagnosticada. Esta guía explica qué opciones existen y cómo funcionan las enfermedades preexistentes.</p>

<h2>Qué es una enfermedad preexistente</h2>
<p>Es una enfermedad o condición que ya tenías diagnosticada antes de contratar el seguro. Muchos seguros piden que la declares en la <strong>declaración personal de salud (DPS)</strong> al ingresar. Lo que ocurra con ella depende del producto: en algunos se cubre, en otros puede quedar excluida de la póliza, y en otros no se pide declaración alguna.</p>
<p>Por eso conviene declarar con veracidad. Por ejemplo, en el Seguro Catastrófico las preexistencias no declaradas, o declaradas y excluidas expresamente en la póliza, no tienen cobertura.</p>

<h2>Seguros que puede contratar un adulto mayor</h2>
<p>Estos son los planes que revisamos según la edad de ingreso y lo que piden sobre salud:</p>
[[tabla]]
<p class="article-meta">Edades de ingreso del contratante según las fichas comerciales de Bupa Seguros.</p>

<h2>Dos planes pensados para mayores de 60</h2>
<h3>[[am]]</h3>
<p>Cubre el 70% en consultas, exámenes de laboratorio e imagenología, con un tope por beneficiario de UF 25, en la red de centros médicos IntegraMédica. Cubre enfermedades preexistentes e incluye rescate de riesgo vital 24/7 en todo el país. Ingreso desde los 60 hasta los 84 años y 364 días, con permanencia hasta los 99 años y 364 días.</p>
<h3>[[m60]]</h3>
<p>Cubre el 70% de las atenciones ambulatorias, de urgencia y hospitalizaciones derivadas de urgencia traumatológica, con un tope anual de UF 200. No pide declaración de salud, no tiene deducible y no exige bonificación mínima. Ingreso desde los 60 hasta los 84 años y 364 días, sin límite de edad de permanencia.</p>
<p>Su tarifa mensual depende de la edad:</p>
[[tarifas]]
<p class="article-meta">Tarifas brutas mensuales en UF, con recaudación anticipada de prima.</p>

<h2>Si tienes preexistencias</h2>
<p>Estas son las alternativas que no piden declaración de salud o que cubren preexistencias:</p>
[[bul1]]

<h2>Qué mirar antes de contratar</h2>
[[bul2]]

<p>Si quieres, te ayudo a comparar las opciones según tu edad y tu situación de salud, sin costo.</p>
'''


def _adultos():
    tabla = _table(('Plan', 'Ingreso del contratante', 'Declaración de salud y preexistencias'), [
        (_plan('adulto-mayor-integramedica-70', 'Adulto Mayor IntegraMédica 70'), 'De 60 a 84 años y 364 días', 'Cubre enfermedades preexistentes'),
        (_plan('bupa-60-mas', 'Bupa 60+'), 'De 60 a 84 años y 364 días', 'No pide declaración de salud'),
        (_plan('mi-dental-integramedica', 'Mi Dental IntegraMédica 65%'), 'De 18 hasta 89 años y 364 días', 'No pide declaración de salud; cubre preexistencias'),
        (_plan('integramedica-100', 'IntegraMédica 100%'), 'De 18 a 64 años y 364 días', 'No pide declaración de salud; cubre preexistencias'),
        (_plan('cuidado-total-70', 'Cuidado Total 60, 70 y 80'), 'De 18 a 75 años y 364 días', 'Con declaración de salud'),
        (_plan('seguro-catastrofico', 'Catastrófico'), 'De 18 a 75 años y 364 días', 'Con declaración personal de salud aprobada'),
        (_plan('complementa', 'Complementa (solo Isapre)'), 'De 18 a 70 años y 364 días', 'Con declaración de salud'),
    ])
    tarifas = _table(('Edad', 'Tarifa mensual'), [(_e(a), _e(b)) for a, b in _TARIFAS_60])
    bul1 = _bul([
        _plan('adulto-mayor-integramedica-70', 'Adulto Mayor IntegraMédica 70') + ': cubre enfermedades preexistentes.',
        _plan('bupa-60-mas', 'Bupa 60+') + ': sin declaración de salud.',
        _plan('integramedica-100', 'IntegraMédica 100%') + ': sin declaración de salud y cubre preexistencias, pero solo permite ingresar hasta los 64 años y 364 días.',
        _plan('mi-dental-integramedica', 'Mi Dental IntegraMédica 65%') + ': plan dental sin declaración de salud y sin necesidad de pertenecer a Isapre o Fonasa.',
    ])
    bul2 = _bul([
        'La <strong>edad máxima de ingreso</strong>: si ya pasaste el límite de un plan, no puedes contratarlo.',
        'La <strong>edad de permanencia</strong>: algunos planes dejan de cubrirte a cierta edad (IntegraMédica 100% hasta los 74 años y 364 días) y otros no tienen límite.',
        'Qué <strong>prestadores</strong> cubre: varios de estos planes funcionan solo en la red IntegraMédica y en las Clínicas Bupa.',
        'Los <strong>topes y carencias</strong>: por ejemplo, en Bupa 60+ scanner, resonancia y hospitalización derivada de urgencia traumatológica se activan desde el cuarto mes.',
        'Cómo <strong>sube la tarifa</strong> con la edad.',
        'Si tienes Isapre, revisa que la prestación tenga bonificación de tu Isapre para que el seguro opere.',
    ])
    return _fill(ADULTOS_BODY, **dict(tabla=tabla, am='Adulto Mayor IntegraMédica 70', m60='Bupa 60+', tarifas=tarifas, bul1=bul1, bul2=bul2))


ADULTOS_FAQ = [
    ('¿Desde qué edad se puede contratar un seguro para adultos mayores?',
     'Adulto Mayor IntegraMédica 70 y Bupa 60+ se pueden contratar desde los 60 años y hasta los 84 años y 364 días.'),
    ('¿Hay seguros de salud que no pidan declaración de salud?',
     'Sí. Bupa 60+, IntegraMédica 100% y Mi Dental IntegraMédica 65% no piden declaración de salud.'),
    ('¿Qué seguro cubre enfermedades preexistentes?',
     'Adulto Mayor IntegraMédica 70, IntegraMédica 100% y Mi Dental IntegraMédica 65% cubren enfermedades preexistentes. En los seguros que piden declaración de salud, las preexistencias pueden quedar excluidas según la póliza.'),
    ('¿Cuánto cuesta Bupa 60+?',
     'La tarifa mensual va de UF 1,03 entre los 60 y 64 años hasta UF 1,67 desde los 81 años.'),
    ('¿IntegraMédica 100% sirve para mayores de 65 años?',
     'No para contratarlo: el contratante puede ingresar hasta los 64 años y 364 días, y la permanencia llega hasta los 74 años y 364 días.'),
]

# ---------------------------------------------------------------------------------------------
# 3) Copago
# ---------------------------------------------------------------------------------------------
COPAGO_BODY = '''
<p>Tener Isapre o Fonasa no significa no pagar nada cuando te atiendes: casi siempre queda una diferencia entre lo que cuesta la atención y lo que tu sistema cubre. Esa diferencia es el <strong>copago</strong>, y es la que más pesa en el bolsillo.</p>

<h2>Qué es el copago</h2>
<p>El copago es la parte de una prestación de salud que paga el afiliado: el valor total de la atención menos lo que bonifica tu Isapre o Fonasa. Si una consulta cuesta $50.000 y tu sistema aporta $15.000, tu copago es de $35.000.</p>

<h2>De qué depende</h2>
[[depende]]

<h2>Un ejemplo con números</h2>
<p>La ficha del plan Cuidado Total 60 muestra cómo opera el seguro sobre el copago de una consulta médica de $50.000, con una bonificación mínima de Isapre de 50%:</p>
[[ejemplo]]
<p class="article-meta">Ejemplo de la ficha comercial de Bupa Cuidado Total 60 (reembolso del 60%). Si el aporte de tu Isapre es menor al 50%, el seguro calcula sobre el costo de la prestación descontando ese porcentaje. Las condiciones exactas dependen del plan.</p>

<h2>Cómo reducir tu copago</h2>
[[reducir]]

<h2>Seguros que actúan sobre el copago</h2>
[[tabla]]

<p>Un seguro complementario no reemplaza a tu Isapre o Fonasa: opera después de ellos y en exceso de su cobertura, por lo que los gastos que tu sistema previsional no bonifica no tienen cobertura. Antes de contratar, revisa deducibles, topes y qué prestadores incluye.</p>
'''


def _copago():
    depende = _bul([
        'El <strong>porcentaje de cobertura</strong> de tu plan de Isapre o el tramo de tu Fonasa.',
        'Si el prestador tiene <strong>convenio</strong> con tu sistema previsional o es de libre elección.',
        'Los <strong>topes</strong> de tu plan para cada tipo de prestación.',
        'El <strong>deducible</strong> y la bonificación mínima, si contratas un seguro complementario.',
    ])
    ejemplo = _table(('Concepto', 'Caso A: tu Isapre aporta 30%', 'Caso B: tu Isapre aporta 60%'), [
        ('Costo de la consulta', '$50.000', '$50.000'),
        ('Aporte de la Isapre', '$15.000 (30%)', '$30.000 (60%)'),
        ('Tu copago antes del seguro', '$35.000', '$20.000'),
        ('Base del seguro para el reembolso', '$25.000', '$20.000'),
        ('Reembolso del seguro (60%)', '$15.000', '$12.000'),
        ('<strong>Copago final</strong>', '<strong>$20.000</strong>', '<strong>$8.000</strong>'),
    ])
    reducir = _bul([
        'Atiéndete en <strong>prestadores con convenio</strong> de tu Isapre o Fonasa cuando puedas: suelen tener una cobertura mayor.',
        'Contrata un <strong>seguro complementario</strong> que opere sobre el copago. Por ejemplo, ' + _plan('complementa', 'Bupa Complementa') + ' cubre el copago en la misma proporción que tu plan de Isapre.',
        'Usa la <strong>red del seguro</strong>. En ' + _plan('cuidado-total-70', 'Cuidado Total') + ' el deducible es $0 en la red de prestadores con convenio Bupa, y la cobertura sube +10% en Clínica Bupa Santiago, Reñaca y Antofagasta, y +12% en laboratorio e imagenología de IntegraMédica.',
        'Si te atiendes siempre en IntegraMédica, ' + _plan('integramedica-100', 'IntegraMédica 100%') + ' cubre el 100% sobre el copago de las atenciones ambulatorias, con un tope anual de UF 60.',
        'Si eres de Fonasa y usas sobre todo la atención ambulatoria, ' + _plan('proteccion-ambulatorio-70', '+ Protección Ambulatorio 70') + ' cubre el 70% del copago, con consultas y videoconsultas de medicina general ilimitadas.',
        'Aprovecha las <strong>videoconsultas</strong> incluidas en varios planes para consultas que no requieren examen físico.',
        'Antes de contratar, revisa el <strong>deducible</strong>, los <strong>topes</strong> y las <strong>carencias</strong> de cada plan.',
    ])
    tabla = _table(('Plan', 'Para quién', 'Cómo actúa sobre el copago'), [
        (_plan('complementa', 'Complementa'), 'Afiliados a Isapre', 'Cubre el copago en la misma proporción que tu plan de Isapre; sin deducible; tope UF 500'),
        (_plan('integramedica-100', 'IntegraMédica 100%'), 'Isapre y Fonasa (B, C y D)', '100% sobre el copago ambulatorio en IntegraMédica; tope UF 60'),
        (_plan('proteccion-ambulatorio-70', '+ Protección Ambulatorio 70'), 'Fonasa', '70% sobre el copago ambulatorio; tope UF 250'),
        (_plan('proteccion-80-70', '+ Protección 80/70'), 'Fonasa', '80% hospitalario y 70% ambulatorio sobre el copago; tope UF 500'),
        (_plan('cuidado-total-70', 'Cuidado Total 70'), 'Isapre y Fonasa (B, C y D)', '70% de bonificación en libre elección; tope UF 400'),
    ])
    return _fill(COPAGO_BODY, **dict(depende=depende, ejemplo=ejemplo, reducir=reducir, tabla=tabla))


COPAGO_FAQ = [
    ('¿Qué es el copago en salud?',
     'Es la parte de una prestación que paga el afiliado: el valor total de la atención menos lo que bonifica su Isapre o Fonasa.'),
    ('¿Un seguro complementario elimina el copago?',
     'No lo elimina, pero lo reduce. El seguro opera después de tu Isapre o Fonasa, con sus propios porcentajes, topes y deducible, y no cubre lo que tu sistema previsional no bonifica.'),
    ('¿Qué seguro cubre el copago de mi Isapre?',
     'Bupa Complementa cubre el copago en la misma proporción que tu plan de Isapre, sin deducible, con un tope anual de UF 500. Es exclusivo para afiliados a Isapre.'),
    ('¿Qué es el deducible?',
     'Es el monto que pagas tú antes de que el seguro comience a reembolsar. En Cuidado Total es de UF 1 al año por beneficiario, con un máximo de UF 3 por grupo familiar, y es $0 en la red de prestadores con convenio Bupa.'),
]


GUIDES = [
    dict(slug='seguro-catastrofico-cuando-conviene',
         title='Seguro catastrófico de salud: cuándo conviene',
         h1='Seguro catastrófico de salud: qué cubre y cuándo conviene',
         desc='Qué es un seguro catastrófico, cuánto cubre, cuánto cuesta por edad y en qué casos conviene. Con datos del Seguro Bupa Catastrófico.',
         body=_catastrofico, faqs=CATASTROFICO_FAQ, related=['seguro-catastrofico', 'cuidado-total-70', 'proteccion-70-70'],
         image='images/plans/catastrofico.jpg'),
    dict(slug='seguro-salud-adultos-mayores-preexistencias',
         title='Seguro de salud para adultos mayores y preexistencias',
         h1='Seguro de salud para adultos mayores y enfermedades preexistentes',
         desc='Qué seguros de salud puede contratar un adulto mayor en Chile, desde qué edad, y cómo funcionan las enfermedades preexistentes y la declaración de salud.',
         body=_adultos, faqs=ADULTOS_FAQ, related=['adulto-mayor-integramedica-70', 'bupa-60-mas', 'integramedica-100'],
         image='images/plans/adulto-mayor.jpg'),
    dict(slug='copago-salud-como-reducirlo',
         title='Qué es el copago en salud y cómo reducirlo',
         h1='Qué es el copago en salud y cómo reducirlo',
         desc='Qué es el copago, por qué lo pagas aunque tengas Isapre o Fonasa y cómo reducirlo con convenios, redes y un seguro complementario. Con un ejemplo.',
         body=_copago, faqs=COPAGO_FAQ, related=['complementa', 'integramedica-100', 'cuidado-total-70'],
         image='images/plans/cuidado-total-60.jpg'),
]
