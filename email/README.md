# Gmail Invoice Checker

Revisa tu Gmail una vez al día, detecta correos de facturas/consumo/gastos,
extrae los montos mencionados y los envía por POST (JSON) a un servidor REST
tuyo.

## 1. Obtener credenciales de Google (una sola vez)

1. Ve a https://console.cloud.google.com/ y crea un proyecto nuevo (o usa uno existente).
2. En "APIs y servicios" → "Biblioteca", busca **Gmail API** y actívala.
3. En "APIs y servicios" → "Pantalla de consentimiento OAuth":
   - Tipo de usuario: **Externo** (si es tu cuenta personal).
   - Completa nombre de la app, correo de soporte, etc. (valores mínimos, no importa mucho para uso personal).
   - En "Usuarios de prueba", agrega tu propio correo de Gmail.
4. En "Credenciales" → "Crear credenciales" → **ID de cliente de OAuth**:
   - Tipo de aplicación: **Aplicación de escritorio**.
   - Descarga el archivo JSON generado.
5. Renombra ese archivo a `credentials.json` y colócalo en esta misma carpeta.

La primera vez que ejecutes el script, se abrirá una ventana del navegador
pidiéndote iniciar sesión y autorizar el acceso (solo lectura a Gmail). Luego
se genera `token.json`, que se reutiliza automáticamente después — no vuelves
a tener que loguearte.

> Nota: si tu máquina no tiene entorno gráfico/navegador (por ejemplo, un
> servidor remoto), corre el script la primera vez en tu laptop, y luego
> copia el `token.json` generado al servidor.

## 2. Instalar dependencias

```bash
cd gmail-invoice-checker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Configurar

Edita `config.json`:

- `rest_endpoint`: la URL de tu servidor que recibirá los datos (POST JSON).
- `gmail_query`: query de búsqueda de Gmail (puedes ajustar las palabras clave,
  agregar remitentes específicos con `from:`, etc.). Por defecto busca en las
  últimas 24 horas.
- `max_results`: tope de correos a revisar por ejecución.

## 4. Probar manualmente

```bash
source venv/bin/activate
python3 gmail_invoice_checker.py
```

Revisa `gmail_invoice_checker.log` para ver qué encontró y si el envío al
servidor REST fue exitoso.

### Formato del JSON que se envía a tu servidor

```json
{
  "message_id": "18d4f2a1b3c9e8f0",
  "subject": "Tu factura de electricidad está lista",
  "sender": "Empresa Eléctrica <no-reply@empresa.com>",
  "date": "Mon, 28 Jul 2026 09:15:00 -0600",
  "snippet": "Tu consumo de este mes fue de...",
  "amounts_detected": ["45.30"],
  "checked_at": "2026-07-29T04:00:00+00:00"
}
```

`amounts_detected` es una lista porque un correo puede mencionar varios
montos (ej. subtotal, impuestos, total). Tu servidor decide cómo
interpretarlos.

## 5. Automatizar (systemd, recomendado sobre cron)

```bash
# Copia los archivos de servicio, ajustando TU_USUARIO y las rutas
sudo cp gmail-invoice-checker.service /etc/systemd/system/
sudo cp gmail-invoice-checker.timer /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable --now gmail-invoice-checker.timer

# Verificar que quedó programado
systemctl list-timers | grep gmail-invoice-checker
```

Esto corre el script todos los días a las 22:00 (ajustable en el `.timer`).

### Alternativa con cron

```bash
crontab -e
```

Agrega:

```
0 22 * * * cd /home/TU_USUARIO/gmail-invoice-checker && venv/bin/python3 gmail_invoice_checker.py
```

## Notas

- El script usa scope de **solo lectura** (`gmail.readonly`) — no puede
  borrar ni modificar tus correos.
- Guarda los IDs de correos ya procesados en `seen_ids.json` para no
  reenviar el mismo correo dos veces si corres el script más de una vez
  el mismo día.
- La detección de montos es por expresiones regulares (busca símbolos de
  moneda y palabras como "total", "monto", "a pagar"). Es un punto de partida
  razonable pero no perfecto — revisa el log de vez en cuando y ajusta el
  regex en `gmail_invoice_checker.py` (función `extract_amounts`) si notas
  que se le escapan casos de tus proveedores habituales.
- Si más adelante quieres pasar a notificación en tiempo real (vía Google
  Cloud Pub/Sub) en lugar de revisión diaria, es un cambio de arquitectura
  más grande — avísame y lo armamos aparte.
