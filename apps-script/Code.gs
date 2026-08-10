/**
 * CotizaSalud.cl — Backend de cotizaciones (Google Apps Script)
 *
 * Versión lista para copiar y pegar directamente en el editor de Apps Script
 * (Extensiones > Apps Script). Es el mismo código que Code.ts, sin tipos,
 * porque el editor del navegador solo ejecuta JavaScript.
 *
 * Si prefieres mantener el código en TypeScript, usa Code.ts + clasp
 * (ver instrucciones aparte) en vez de este archivo.
 */

var TARGET_SPREADSHEET_ID = '14LiY2PQUtkN8CaomnkZTxG9uPrRzz5tmEzw2UOaPT-k';
var SHEET_COTIZACIONES = 'LeadsWeb';
var SHEET_CONFIG = 'Config';

var COTIZACIONES_HEADERS = [
  'Fecha',
  'Origen',
  'Nombre',
  'Teléfono',
  'Correo',
  'Sistema de salud',
  'Plan de interés',
  'Mensaje',
  'Estado',
];

var CONFIG_DEFAULTS = {
  adminEmail: 'lorenasotomayor75@gmail.cl',
  remitenteNombre: 'CotizaSalud.cl — Bupa Seguros',
  asuntoCliente: 'Tu cotización de seguro de salud Bupa',
  asuntoAdmin: 'Nueva cotización recibida en CotizaSalud.cl',
  celular: '+56 9 1234 5678',
};

function doPost(e) {
  try {
    var raw = e && e.postData && e.postData.contents ? e.postData.contents : '{}';
    var input = JSON.parse(raw);

    if (!input.nombre || !input.email) {
      return jsonResponse({ ok: false, error: 'Faltan campos obligatorios: nombre y email.' });
    }

    var config = getConfig();
    appendCotizacion(input);
    sendClientEmail(input, config);
    sendAdminEmail(input, config);

    return jsonResponse({ ok: true });
  } catch (err) {
    return jsonResponse({ ok: false, error: String(err) });
  }
}

function doGet() {
  var config = getConfig();
  return jsonResponse({
    ok: true,
    service: 'CotizaSalud cotizaciones',
    status: 'online',
    celular: config.celular,
    ejecutiva: getEjecutiva(),
  });
}

function getEjecutiva() {
  var ss = getTargetSpreadsheet();
  var sheet = ss.getSheetByName('Ejecutivos');
  if (!sheet || sheet.getLastRow() < 2) return null;

  var values = sheet.getDataRange().getValues();
  var headers = values[0].map(function (h) { return (h || '').toString().trim(); });
  var row = values[1];

  var obj = {};
  headers.forEach(function (header, i) {
    if (header) obj[header] = (row[i] === undefined || row[i] === null) ? '' : row[i].toString();
  });
  return obj;
}

function jsonResponse(body) {
  return ContentService.createTextOutput(JSON.stringify(body)).setMimeType(
    ContentService.MimeType.JSON
  );
}

function appendCotizacion(input) {
  var sheet = getOrCreateCotizacionesSheet();
  sheet.appendRow([
    new Date(),
    input.origen || 'formulario',
    input.nombre || '',
    input.telefono || '',
    input.email || '',
    input.sistema || '',
    input.interes || '',
    input.mensaje || '',
    'Nueva',
  ]);
}

function sendClientEmail(input, config) {
  var nombre = input.nombre || 'Cliente';
  var bodyLines = [
    'Hola ' + nombre + ',',
    '',
    'Gracias por cotizar tu seguro de salud con nosotros. Recibimos tus datos y te contactaremos en menos de 24 horas con una propuesta personalizada.',
    '',
    'Resumen de tu solicitud:',
    '- Sistema de salud: ' + (input.sistema || 'No indicado'),
    '- Plan de interés: ' + (input.interes || 'No indicado'),
    input.mensaje ? '- Mensaje: ' + input.mensaje : '',
    '',
    'Si tienes urgencia, puedes escribirnos directo por WhatsApp.',
    '',
    'Saludos,',
  ].filter(function (line) { return line !== ''; });

  var ejecutiva = getEjecutiva();
  var plainSignature = (ejecutiva && ejecutiva['nombre']) ? ejecutiva['nombre'] : config.remitenteNombre;
  var body = bodyLines.concat(plainSignature).join('\n');

  var htmlBody =
    '<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#0A2A43;line-height:1.55;">' +
    bodyLines.map(function (line) {
      return line === '' ? '<br>' : '<p style="margin:0 0 4px;">' + line + '</p>';
    }).join('') +
    buildSignatureHtml(ejecutiva, config) +
    '</div>';

  var logoBlob = Utilities.newBlob(
    Utilities.base64Decode(BUPA_LOGO_BASE64),
    'image/png',
    'bupa-logo.png'
  );
  var instagramIconBlob = Utilities.newBlob(
    Utilities.base64Decode(INSTAGRAM_ICON_BASE64),
    'image/png',
    'instagram-icon.png'
  );

  MailApp.sendEmail({
    to: input.email,
    subject: config.asuntoCliente,
    body: body,
    htmlBody: htmlBody,
    name: config.remitenteNombre,
    inlineImages: { bupaLogo: logoBlob, instagramIcon: instagramIconBlob },
  });
}

function buildSignatureHtml(ejecutiva, config) {
  var nombre = (ejecutiva && ejecutiva['nombre']) || config.remitenteNombre;
  var cargo = (ejecutiva && ejecutiva['cargo']) || '';
  var correo = (ejecutiva && ejecutiva['correo']) || config.adminEmail;
  var telefono = (ejecutiva && ejecutiva['telefono']) || config.celular;
  var instagram = (ejecutiva && ejecutiva['instagram']) || 'bupa_lorena_sotomayor';
  var waDigits = telefono.toString().replace(/[^0-9]/g, '');

  return '' +
    '<table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;margin-top:22px;padding-top:14px;border-top:2px solid #0079C8;max-width:340px;">' +
    '<tr><td style="font-weight:bold;font-size:15px;color:#0A2A43;padding-bottom:2px;">' + nombre + '</td></tr>' +
    (cargo ? '<tr><td style="font-size:11px;letter-spacing:.06em;color:#0079C8;font-weight:bold;padding-bottom:10px;">' + cargo.toUpperCase() + '</td></tr>' : '') +
    '<tr><td style="font-size:13px;color:#4C6478;padding:3px 0;">✉️&nbsp; <a href="mailto:' + correo + '" style="color:#4C6478;text-decoration:none;">' + correo + '</a></td></tr>' +
    '<tr><td style="font-size:13px;color:#25D366;padding:3px 0;">💬&nbsp; <a href="https://wa.me/' + waDigits + '" style="color:#25D366;text-decoration:none;">' + telefono + '</a></td></tr>' +
    '<tr><td style="font-size:13px;color:#C13584;padding:3px 0;"><img src="cid:instagramIcon" width="16" height="16" alt="Instagram" style="vertical-align:middle;border:0;">&nbsp; <a href="https://instagram.com/' + instagram + '" style="color:#C13584;text-decoration:none;">' + instagram + '</a></td></tr>' +
    '<tr><td style="padding:12px 0 4px;"><img src="cid:bupaLogo" width="88" alt="Bupa Seguros" style="display:block;border:0;"></td></tr>' +
    '</table>';
}

function sendAdminEmail(input, config) {
  var body = [
    'Se recibió una nueva cotización desde CotizaSalud.cl:',
    '',
    'Nombre: ' + (input.nombre || ''),
    'Teléfono: ' + (input.telefono || ''),
    'Correo: ' + (input.email || ''),
    'Sistema de salud: ' + (input.sistema || ''),
    'Plan de interés: ' + (input.interes || ''),
    'Mensaje: ' + (input.mensaje || ''),
    'Origen: ' + (input.origen || 'formulario'),
    'Fecha: ' + new Date().toLocaleString('es-CL'),
  ].join('\n');

  MailApp.sendEmail({
    to: config.adminEmail,
    subject: config.asuntoAdmin,
    body: body,
    name: config.remitenteNombre,
  });
}

function getConfig() {
  var sheet = getOrCreateConfigSheet();
  var values = sheet.getDataRange().getValues();
  var map = {};
  values.slice(1).forEach(function (row) {
    var key = (row[0] || '').toString().trim().toLowerCase();
    var value = (row[1] || '').toString().trim();
    if (key) map[key] = value;
  });

  var ejecutiva = getEjecutiva();

  return {
    adminEmail: (ejecutiva && ejecutiva['correo']) || map['adminemail'] || CONFIG_DEFAULTS.adminEmail,
    remitenteNombre: map['remitentenombre'] || CONFIG_DEFAULTS.remitenteNombre,
    asuntoCliente: map['asuntocliente'] || CONFIG_DEFAULTS.asuntoCliente,
    asuntoAdmin: map['asuntoadmin'] || CONFIG_DEFAULTS.asuntoAdmin,
    celular: (ejecutiva && ejecutiva['telefono']) || map['celular'] || CONFIG_DEFAULTS.celular,
  };
}

function getTargetSpreadsheet() {
  return SpreadsheetApp.openById(TARGET_SPREADSHEET_ID);
}

function getOrCreateCotizacionesSheet() {
  var ss = getTargetSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_COTIZACIONES);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_COTIZACIONES);
  }
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(COTIZACIONES_HEADERS);
    sheet.getRange(1, 1, 1, COTIZACIONES_HEADERS.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function getOrCreateConfigSheet() {
  var ss = getTargetSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_CONFIG);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_CONFIG);
  }
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(['Clave', 'Valor']);
    sheet.appendRow(['AdminEmail', CONFIG_DEFAULTS.adminEmail]);
    sheet.appendRow(['RemitenteNombre', CONFIG_DEFAULTS.remitenteNombre]);
    sheet.appendRow(['AsuntoCliente', CONFIG_DEFAULTS.asuntoCliente]);
    sheet.appendRow(['AsuntoAdmin', CONFIG_DEFAULTS.asuntoAdmin]);
    sheet.appendRow(['Celular', CONFIG_DEFAULTS.celular]);
    sheet.getRange(1, 1, 1, 2).setFontWeight('bold');
    sheet.setFrozenRows(1);
    sheet.autoResizeColumns(1, 2);
  }
  return sheet;
}

function setup() {
  getOrCreateCotizacionesSheet();
  getOrCreateConfigSheet();
}
