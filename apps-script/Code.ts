/// <reference types="google-apps-script" />

/**
 * CotizaSalud.cl — Backend de cotizaciones (Google Apps Script)
 *
 * Guarda los leads en la planilla "LeadsWeb":
 * https://docs.google.com/spreadsheets/d/14LiY2PQUtkN8CaomnkZTxG9uPrRzz5tmEzw2UOaPT-k/edit
 *
 * Qué hace:
 *  1) Recibe cada cotización enviada desde index_13.html (fetch POST).
 *  2) La guarda como una fila nueva en la hoja "LeadsWeb".
 *  3) Envía un correo de confirmación al cliente.
 *  4) Envía un correo de notificación a la ejecutiva (correo parametrizado
 *     en la hoja "Config", NO hardcodeado).
 *
 * Despliegue: Extensiones > Apps Script > pegar/subir este código (transpilado
 * a .gs vía clasp) > Implementar > Aplicación web > Ejecutar como "Yo",
 * Acceso "Cualquier usuario". Ver README de despliegue entregado aparte.
 */

const TARGET_SPREADSHEET_ID = '14LiY2PQUtkN8CaomnkZTxG9uPrRzz5tmEzw2UOaPT-k';
const SHEET_COTIZACIONES = 'LeadsWeb';
const SHEET_CONFIG = 'Config';

const COTIZACIONES_HEADERS = [
  'Fecha',
  'Origen',
  'Nombre',
  'Teléfono',
  'Correo',
  'Sistema de salud',
  'Plan de interés',
  'Mensaje',
  'Estado',
] as const;

interface CotizacionInput {
  origen?: string;
  nombre?: string;
  telefono?: string;
  email?: string;
  sistema?: string;
  interes?: string;
  mensaje?: string;
}

interface ConfigValues {
  adminEmail: string;
  remitenteNombre: string;
  asuntoCliente: string;
  asuntoAdmin: string;
  celular: string;
}

const CONFIG_DEFAULTS: ConfigValues = {
  adminEmail: 'lorenasotomayor75@gmail.cl',
  remitenteNombre: 'CotizaSalud.cl — Bupa Seguros',
  asuntoCliente: 'Tu cotización de seguro de salud Bupa',
  asuntoAdmin: 'Nueva cotización recibida en CotizaSalud.cl',
  celular: '+56 9 1234 5678',
};

/**
 * Punto de entrada HTTP. El frontend hace POST con body en texto plano
 * (Content-Type: text/plain) para evitar el preflight CORS que Apps Script
 * no soporta bien.
 */
function doPost(e: GoogleAppsScript.Events.DoPost): GoogleAppsScript.Content.TextOutput {
  try {
    const raw = e && e.postData && e.postData.contents ? e.postData.contents : '{}';
    const input = JSON.parse(raw) as CotizacionInput;

    if (!input.nombre || !input.email) {
      return jsonResponse({ ok: false, error: 'Faltan campos obligatorios: nombre y email.' });
    }

    const config = getConfig();
    appendCotizacion(input);
    sendClientEmail(input, config);
    sendAdminEmail(input, config);

    return jsonResponse({ ok: true });
  } catch (err) {
    return jsonResponse({ ok: false, error: String(err) });
  }
}

/**
 * Permite verificar que el despliegue está activo abriendo la URL en el
 * navegador, y expone el celular de contacto (parametrizado en la hoja
 * "Config") para que el frontend arme los links de WhatsApp dinámicamente.
 */
function doGet(): GoogleAppsScript.Content.TextOutput {
  const config = getConfig();
  return jsonResponse({
    ok: true,
    service: 'CotizaSalud cotizaciones',
    status: 'online',
    celular: config.celular,
    ejecutiva: getEjecutiva(),
  });
}

/**
 * Lee la primera fila de datos de la hoja "Ejecutivos" y la devuelve como
 * objeto usando la fila 1 como nombres de columna (tal cual estén escritos
 * en el Sheet), para que el frontend muestre nombre/cargo/teléfono sin
 * datos hardcodeados. Por ahora se usa solo una ejecutiva (la primera fila).
 */
function getEjecutiva(): Record<string, string> | null {
  const ss = getTargetSpreadsheet();
  const sheet = ss.getSheetByName('Ejecutivos');
  if (!sheet || sheet.getLastRow() < 2) return null;

  const values = sheet.getDataRange().getValues() as string[][];
  const headers = values[0].map((h) => (h || '').toString().trim());
  const row = values[1];

  const obj: Record<string, string> = {};
  headers.forEach((header, i) => {
    if (header) obj[header] = (row[i] === undefined || row[i] === null) ? '' : row[i].toString();
  });
  return obj;
}

function jsonResponse(body: Record<string, unknown>): GoogleAppsScript.Content.TextOutput {
  return ContentService.createTextOutput(JSON.stringify(body)).setMimeType(
    ContentService.MimeType.JSON
  );
}

function appendCotizacion(input: CotizacionInput): void {
  const sheet = getOrCreateCotizacionesSheet();
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

function sendClientEmail(input: CotizacionInput, config: ConfigValues): void {
  const nombre = input.nombre || 'Cliente';
  const bodyLines = [
    `Hola ${nombre},`,
    '',
    'Gracias por cotizar tu seguro de salud con nosotros. Recibimos tus datos y te contactaremos en menos de 24 horas con una propuesta personalizada.',
    '',
    'Resumen de tu solicitud:',
    `- Sistema de salud: ${input.sistema || 'No indicado'}`,
    `- Plan de interés: ${input.interes || 'No indicado'}`,
    input.mensaje ? `- Mensaje: ${input.mensaje}` : '',
    '',
    'Si tienes urgencia, puedes escribirnos directo por WhatsApp.',
    '',
    'Saludos,',
  ].filter((line) => line !== '');

  const ejecutiva = getEjecutiva();
  const plainSignature = ejecutiva && ejecutiva['nombre'] ? ejecutiva['nombre'] : config.remitenteNombre;
  const body = bodyLines.concat(plainSignature).join('\n');

  const htmlBody =
    '<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#0A2A43;line-height:1.55;">' +
    bodyLines.map((line) => (line === '' ? '<br>' : `<p style="margin:0 0 4px;">${line}</p>`)).join('') +
    buildSignatureHtml(ejecutiva, config) +
    '</div>';

  const logoBlob = Utilities.newBlob(
    Utilities.base64Decode(BUPA_LOGO_BASE64),
    'image/png',
    'bupa-logo.png'
  );

  MailApp.sendEmail({
    to: input.email as string,
    subject: config.asuntoCliente,
    body,
    htmlBody,
    name: config.remitenteNombre,
    inlineImages: { bupaLogo: logoBlob },
  });
}

/**
 * Firma en HTML para el correo del cliente, con los datos de la ejecutiva
 * (hoja "Ejecutivos") y el logo de Bupa embebido. El handle de Instagram se
 * lee de la columna "instagram" del Sheet; si está vacía, usa un valor por
 * defecto para no dejar la firma sin ese dato.
 */
function buildSignatureHtml(
  ejecutiva: Record<string, string> | null,
  config: ConfigValues
): string {
  const nombre = (ejecutiva && ejecutiva['nombre']) || config.remitenteNombre;
  const cargo = (ejecutiva && ejecutiva['cargo']) || '';
  const correo = (ejecutiva && ejecutiva['correo']) || config.adminEmail;
  const telefono = (ejecutiva && ejecutiva['telefono']) || config.celular;
  const instagram = (ejecutiva && ejecutiva['instagram']) || 'bupa_lorena_sotomayor';
  const waDigits = telefono.toString().replace(/[^0-9]/g, '');

  return `
    <table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;margin-top:22px;padding-top:14px;border-top:2px solid #0079C8;max-width:340px;">
      <tr><td style="font-weight:bold;font-size:15px;color:#0A2A43;padding-bottom:2px;">${nombre}</td></tr>
      ${cargo ? `<tr><td style="font-size:11px;letter-spacing:.06em;color:#0079C8;font-weight:bold;padding-bottom:10px;">${cargo.toUpperCase()}</td></tr>` : ''}
      <tr><td style="font-size:13px;color:#4C6478;padding:3px 0;">✉️&nbsp; <a href="mailto:${correo}" style="color:#4C6478;text-decoration:none;">${correo}</a></td></tr>
      <tr><td style="font-size:13px;color:#25D366;padding:3px 0;">💬&nbsp; <a href="https://wa.me/${waDigits}" style="color:#25D366;text-decoration:none;">${telefono}</a></td></tr>
      <tr><td style="padding:12px 0 10px;"><img src="cid:bupaLogo" width="88" alt="Bupa Seguros" style="display:block;border:0;"></td></tr>
      <tr><td style="font-size:13px;color:#C13584;padding:3px 0;">📷&nbsp; <a href="https://instagram.com/${instagram}" style="color:#C13584;text-decoration:none;">${instagram}</a></td></tr>
    </table>
  `;
}

function sendAdminEmail(input: CotizacionInput, config: ConfigValues): void {
  const body = [
    'Se recibió una nueva cotización desde CotizaSalud.cl:',
    '',
    `Nombre: ${input.nombre || ''}`,
    `Teléfono: ${input.telefono || ''}`,
    `Correo: ${input.email || ''}`,
    `Sistema de salud: ${input.sistema || ''}`,
    `Plan de interés: ${input.interes || ''}`,
    `Mensaje: ${input.mensaje || ''}`,
    `Origen: ${input.origen || 'formulario'}`,
    `Fecha: ${new Date().toLocaleString('es-CL')}`,
  ].join('\n');

  MailApp.sendEmail({
    to: config.adminEmail,
    subject: config.asuntoAdmin,
    body,
    name: config.remitenteNombre,
  });
}

/**
 * Lee la hoja "Config" (clave en columna A, valor en columna B) y arma la
 * configuración efectiva. Si falta una clave, cae al valor por defecto —
 * así el correo de destino admin siempre es el parametrizado en el Sheet.
 */
function getConfig(): ConfigValues {
  const sheet = getOrCreateConfigSheet();
  const values = sheet.getDataRange().getValues() as string[][];
  const map: Record<string, string> = {};
  values.slice(1).forEach((row) => {
    const key = (row[0] || '').toString().trim().toLowerCase();
    const value = (row[1] || '').toString().trim();
    if (key) map[key] = value;
  });

  const ejecutiva = getEjecutiva();

  return {
    adminEmail: (ejecutiva && ejecutiva['correo']) || map['adminemail'] || CONFIG_DEFAULTS.adminEmail,
    remitenteNombre: map['remitentenombre'] || CONFIG_DEFAULTS.remitenteNombre,
    asuntoCliente: map['asuntocliente'] || CONFIG_DEFAULTS.asuntoCliente,
    asuntoAdmin: map['asuntoadmin'] || CONFIG_DEFAULTS.asuntoAdmin,
    celular: (ejecutiva && ejecutiva['telefono']) || map['celular'] || CONFIG_DEFAULTS.celular,
  };
}

function getTargetSpreadsheet(): GoogleAppsScript.Spreadsheet.Spreadsheet {
  return SpreadsheetApp.openById(TARGET_SPREADSHEET_ID);
}

function getOrCreateCotizacionesSheet(): GoogleAppsScript.Spreadsheet.Sheet {
  const ss = getTargetSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_COTIZACIONES);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_COTIZACIONES);
  }
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(COTIZACIONES_HEADERS as unknown as string[]);
    sheet.getRange(1, 1, 1, COTIZACIONES_HEADERS.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function getOrCreateConfigSheet(): GoogleAppsScript.Spreadsheet.Sheet {
  const ss = getTargetSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_CONFIG);
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

/**
 * Ejecutar UNA VEZ manualmente desde el editor de Apps Script (▶ Run > setup)
 * para crear las hojas "Cotizaciones" y "Config" con sus encabezados.
 */
function setup(): void {
  getOrCreateCotizacionesSheet();
  getOrCreateConfigSheet();
}
