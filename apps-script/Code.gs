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
  });
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
  var lines = [
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
    config.remitenteNombre,
  ].filter(function (line) { return line !== ''; });

  MailApp.sendEmail({
    to: input.email,
    subject: config.asuntoCliente,
    body: lines.join('\n'),
    name: config.remitenteNombre,
  });
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

  return {
    adminEmail: map['adminemail'] || CONFIG_DEFAULTS.adminEmail,
    remitenteNombre: map['remitentenombre'] || CONFIG_DEFAULTS.remitenteNombre,
    asuntoCliente: map['asuntocliente'] || CONFIG_DEFAULTS.asuntoCliente,
    asuntoAdmin: map['asuntoadmin'] || CONFIG_DEFAULTS.asuntoAdmin,
    celular: map['celular'] || CONFIG_DEFAULTS.celular,
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
