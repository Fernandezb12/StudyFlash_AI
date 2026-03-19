# StudyFlash AI

StudyFlash AI es una aplicación de escritorio para Windows orientada a productividad de estudio y simulacros autorizados. Mantiene la arquitectura modular original, se ejecuta en segundo plano con bandeja del sistema, registra una hotkey global y ahora prioriza un flujo más preciso: captura focalizada, OCR mejorado, parser más limpio y OpenAI API como motor principal de respuesta.

> **Uso ético:** esta herramienta es para estudio personal, práctica autorizada, PDFs, bancos de preguntas y simulacros permitidos. No incluye evasión de SAFE Exam Browser, ocultamiento de procesos, borrado de rastros, evasión de detección ni automatización de fraude académico.

---

## Qué cambió en esta versión

- OCR más robusto con preprocesado por etapas: escala de grises, autocontraste, redimensionado 2x, sharpen, binarización y limpieza opcional con OpenCV.
- Parser reestructurado para eliminar ruido típico del navegador, ignorar URLs y botones irrelevantes, y detectar opciones multilínea con más robustez.
- Integración con la librería oficial moderna de OpenAI usando Responses API y salida JSON estructurada.
- Motor de respuesta principal basado en OpenAI con fallback local sencillo si la API falla.
- Popup compacto, blanco y legible, mostrando solo respuesta y explicación por defecto.
- Más configuración desde UI: OpenAI, confianza mínima, modo de captura, región manual y preferencia de mostrar pregunta.

---

## Arquitectura actual

```text
studyflash_ai/
├── app/
│   ├── main.py
│   ├── controller.py
│   ├── config.py
│   ├── hotkeys.py
│   ├── screen_capture.py
│   ├── ocr_engine.py
│   ├── question_parser.py
│   ├── answer_engine.py
│   ├── llm_client.py
│   ├── prompt_templates.py
│   ├── popup_window.py
│   ├── tray_app.py
│   ├── settings_window.py
│   ├── startup_manager.py
│   ├── history_store.py
│   └── utils.py
├── assets/
├── tests/
├── requirements.txt
├── README.md
├── .env.example
└── run.py
```

---

## Requisitos

- Python 3.11+
- Windows 10/11 recomendado
- Tesseract OCR instalado
- Dependencias de `requirements.txt`
- Variable de entorno `OPENAI_API_KEY` si deseas usar OpenAI como motor principal

---

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Instalar Tesseract

Instala Tesseract OCR y, si hace falta, configura la ruta desde la ventana de ajustes:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

También conviene instalar los idiomas español e inglés para usar `spa+eng`.

---

## Configurar `OPENAI_API_KEY`

### PowerShell

```powershell
$env:OPENAI_API_KEY="tu_api_key"
python run.py
```

### CMD

```cmd
set OPENAI_API_KEY=tu_api_key
python run.py
```

### Persistente en Windows

```powershell
setx OPENAI_API_KEY "tu_api_key"
```

La app **no** guarda la API key en `config.json`. Solo guarda el nombre de la variable de entorno, por defecto `OPENAI_API_KEY`.

---

## Ejecutar la app

```bash
python run.py
```

Al iniciarse:

- queda residente en la bandeja del sistema,
- mantiene la hotkey global,
- abre el popup solo cuando disparas el flujo OCR,
- puede usar OpenAI si `openai_enabled` e `internet_enabled` están activos y la variable de entorno existe.

---

## Cómo activar el modo API / internet

Desde **Abrir configuración** en la bandeja puedes controlar:

- `openai_enabled`: activa OpenAI como motor principal,
- `internet_enabled`: permite llamadas API,
- `openai_model`: modelo a usar, por defecto `gpt-4o-mini`,
- `min_confidence`: umbral bajo el cual la respuesta se convierte en **No concluyente**.

Si la API falla o no está configurada, la app usa un fallback local simple para no romper el flujo.

---

## Ajustar la región de captura

La precisión mejora mucho si capturas solo la zona útil.

En configuración puedes elegir:

- `region`: captura una región manual `x,y,w,h`,
- `full_screen`: captura pantalla completa.

Recomendación:

- usa `region` para centrarte solo en la pregunta y sus opciones,
- evita capturar barras del navegador, menús y widgets laterales,
- ajusta la región si ves ruido OCR repetido.

---

## Interpretar el popup

El nuevo popup muestra por defecto solo:

- **Respuesta**
- **Explicación**
- botón **Aceptar**

Opcionalmente puedes activar **Mostrar pregunta** desde configuración.

Reglas del resultado:

- si la confianza es suficiente, verás una respuesta breve,
- si la confianza es baja, verás **No concluyente**,
- la explicación está limitada a un máximo de dos líneas.

---

## Uso desde bandeja

El menú de bandeja incluye:

- **Abrir configuración**
- **Activar/desactivar hotkey**
- **Ejecutar prueba OCR**
- **Ver historial reciente**
- **Iniciar con Windows**
- **Salir**

La app sigue usando el registro del usuario actual para el arranque automático en Windows:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
```

---

## Logging y depuración

Se registran logs para depurar:

- texto OCR crudo y limpio,
- pregunta interpretada,
- opciones detectadas,
- tipo de pregunta,
- fuente usada (`openai:*` o `fallback`),
- confianza final.

Para pruebas controladas:

1. activa **Usar imagen de prueba**,
2. indica una imagen de ejemplo,
3. ejecuta **Ejecutar prueba OCR** desde bandeja.

---

## Empaquetado con PyInstaller

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name "StudyFlash AI" run.py
```

Si agregas recursos propios:

```bash
pyinstaller --noconfirm --windowed --name "StudyFlash AI" --add-data "assets;assets" run.py
```

---

## Tests

```bash
python -m pytest tests
```

---

## Límites éticos

StudyFlash AI no debe usarse para:

- evadir SAFE Exam Browser,
- ocultar procesos,
- borrar rastros,
- evitar detección,
- automatizar fraude académico en sistemas restringidos.

La arquitectura y la documentación están orientadas a un uso legítimo de estudio y simulacro autorizado.
