# StudyFlash AI

StudyFlash AI es una aplicación de escritorio para Windows orientada a productividad de estudio. Se ejecuta en segundo plano, permanece en la bandeja del sistema, escucha una hotkey global configurable y, al activarse, captura pantalla, ejecuta OCR y muestra una respuesta breve con explicación en un popup pequeño y siempre visible.

> **Importante:** este proyecto está diseñado para estudio personal, prácticas permitidas, revisión de PDFs, bancos de preguntas y simulacros autorizados. No incluye evasión de sistemas de supervisión, bypass de navegadores seguros, ocultamiento, eliminación de rastros ni automatización de fraude académico.

---

## Características principales

- Inicio en segundo plano con icono en bandeja del sistema.
- Hotkey global configurable, por defecto `Ctrl + X`.
- Captura de pantalla completa o región configurable.
- OCR con `pytesseract`.
- Detección básica de preguntas abiertas, selección múltiple y verdadero/falso.
- Popup minimalista con:
  - pregunta detectada,
  - respuesta,
  - explicación,
  - confianza,
  - botón **Aceptar**.
- Configuración persistente en JSON.
- Historial local de consultas recientes.
- Integración de inicio automático con Windows mediante `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`.
- Arquitectura modular para reemplazar el motor demo por un motor LLM real en el futuro.

---

## Arquitectura

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

### Motores de respuesta

La app ya incluye una interfaz desacoplada:

- `BaseAnswerEngine`: contrato abstracto.
- `DemoAnswerEngine`: heurístico, listo para usar sin claves externas.
- `LLMAnswerEngine`: stub para integrar un proveedor real manteniendo la misma salida.

Cada respuesta devuelve:

- `answer`
- `explanation`
- `confidence`
- `question_type`

---

## Requisitos

- Python 3.11 o superior.
- Windows 10/11 recomendado.
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) instalado.
- Dependencias Python del archivo `requirements.txt`.

---

## Instalación

### 1. Clona o copia el proyecto

```bash
git clone <tu-repo>
cd StudyFlash_AI
```

### 2. Crea un entorno virtual

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instala dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Instala Tesseract

#### Opción recomendada en Windows

1. Descarga el instalador desde UB Mannheim o desde el proyecto oficial.
2. Durante la instalación, incluye los paquetes de idioma que necesites, por ejemplo español e inglés.
3. Toma nota de la ruta de instalación, normalmente:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

4. Puedes configurarla desde la ventana de ajustes de la aplicación si no está en `PATH`.

---

## Ejecución

```bash
python run.py
```

Al iniciarse:

- la aplicación **no cierra** al cerrar el popup,
- queda residente en la bandeja del sistema,
- registra la hotkey global configurada,
- solo muestra el popup cuando disparas el atajo o ejecutas una prueba OCR.

---

## Uso del icono de bandeja

El menú de bandeja incluye:

- **Abrir configuración**: edita hotkey, OCR, modo de captura y modo de respuesta.
- **Activar/desactivar hotkey**: suspende o reactiva la escucha global.
- **Ejecutar prueba OCR**: corre el flujo completo sin esperar otra captura manual.
- **Ver historial reciente**: muestra las últimas consultas almacenadas localmente.
- **Iniciar con Windows**: crea o elimina la entrada en el registro de usuario actual.
- **Salir**: detiene la hotkey, cierra la bandeja y termina el proceso.

---

## Configuración gráfica

La ventana de configuración permite cambiar sin editar código:

- hotkey global,
- estado de la hotkey,
- modo de respuesta (`breve`, `normal`, `explicativa`),
- captura por pantalla completa o región,
- región manual (`x,y,w,h`),
- monitor a capturar,
- idiomas OCR,
- ruta de `tesseract.exe`,
- inicio con Windows,
- modo depuración,
- imagen de prueba para OCR.

La configuración persistente se guarda en JSON en el perfil del usuario.

### Ubicación típica del archivo de configuración

En Windows:

```text
%APPDATA%\StudyFlash AI\config.json
```

El historial se guarda en:

```text
%APPDATA%\StudyFlash AI\history.json
```

---

## Hotkey global

Por defecto se usa `Ctrl + X`.

Puedes cambiarla por formatos compatibles con la librería `keyboard`, por ejemplo:

- `ctrl+shift+s`
- `alt+x`
- `f8`

Si la hotkey no funciona:

- prueba ejecutar la app con permisos adecuados,
- evita combinaciones reservadas por otras aplicaciones,
- confirma que el teclado del sistema no tenga un mapeo especial.

---

## Inicio con Windows

StudyFlash AI implementa una solución realista y mantenible basada en el registro del usuario actual:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
```

Desde la interfaz puedes activar o desactivar esta opción. Al activarla:

- se guarda la preferencia en `config.json`,
- se crea o actualiza el valor `StudyFlashAI`,
- la app intentará arrancar al iniciar sesión del usuario.

Si en el futuro prefieres usar el Startup folder, puedes extender `startup_manager.py`, pero el registro es la opción más simple de mantener para este caso.

---

## Probar OCR

Hay dos formas:

### Flujo real

1. Ejecuta la app.
2. Deja visible una pregunta en pantalla.
3. Presiona la hotkey configurada.
4. Revisa el popup generado.

### Flujo de depuración

1. Abre **Configuración**.
2. Activa **Usar imagen de prueba**.
3. Indica la ruta a una captura o imagen con texto.
4. Usa **Ejecutar prueba OCR** desde la bandeja.

Esto permite depurar OCR sin depender de una captura en vivo.

---

## Empaquetar a `.exe` con PyInstaller

### Instalar PyInstaller

```bash
pip install pyinstaller
```

### Comando base

```bash
pyinstaller --noconfirm --windowed --name "StudyFlash AI" run.py
```

### Con icono opcional

```bash
pyinstaller --noconfirm --windowed --name "StudyFlash AI" --icon assets/icon.ico run.py
```

### Incluyendo recursos extra

Si agregas iconos, plantillas u otros assets, puedes incluirlos así:

```bash
pyinstaller --noconfirm --windowed --name "StudyFlash AI" --icon assets/icon.ico --add-data "assets;assets" run.py
```

### Recomendaciones para distribución local

- prueba primero el ejecutable generado en `dist/StudyFlash AI/`,
- verifica que `tesseract.exe` esté instalado en el equipo de destino,
- confirma permisos de la hotkey global,
- distribuye junto con instrucciones claras de instalación de Tesseract.

---

## Límites éticos

StudyFlash AI **no debe** usarse para:

- evadir SAFE Exam Browser,
- ocultar procesos,
- comportarse de manera indetectable,
- eliminar rastros de actividad,
- engañar sistemas de supervisión,
- automatizar fraude académico.

El proyecto está intencionalmente centrado en apoyo de estudio autorizado y productividad personal.

---

## Errores comunes y soluciones

### 1. `TesseractNotFoundError`

Causa: Tesseract no está instalado o la ruta no está configurada.

Solución:

- instala Tesseract,
- agrega su carpeta al `PATH`, o
- define la ruta desde la configuración de la app.

### 2. La hotkey no responde

Causa probable:

- conflicto con otra app,
- permisos insuficientes,
- formato inválido de la combinación.

Solución:

- cambia la hotkey,
- reinicia la app,
- valida que la combinación esté bien escrita.

### 3. El OCR detecta texto incorrectamente

Causa probable:

- baja resolución,
- fuente pequeña,
- idioma OCR incompleto,
- captura demasiado grande.

Solución:

- captura una región más pequeña,
- usa imagen de mayor calidad,
- ajusta `ocr_language` a `spa`, `eng` o `spa+eng`.

### 4. No inicia con Windows

Causa probable:

- la entrada del registro no se escribió,
- se movió el ejecutable o el proyecto de carpeta,
- se empaquetó de forma distinta.

Solución:

- desactiva y vuelve a activar la opción,
- verifica la clave `Run` del usuario,
- evita mover el ejecutable final después de configurar autoarranque.

---

## Desarrollo y pruebas

### Ejecutar tests

```bash
pytest
```

### Extender el motor de respuestas

Puedes reemplazar `DemoAnswerEngine` por un motor real:

1. Implementa `LLMAnswerEngine.answer(...)`.
2. Devuelve siempre `AnswerResult`.
3. Mantén la separación entre OCR, parseo y generación de respuesta.
4. Añade autenticación y variables de entorno en caso necesario.

---

## Futuras mejoras sugeridas

- selección interactiva de región con overlay.
- mejores heurísticas de detección de pregunta.
- soporte opcional para OpenCV en preprocesado avanzado.
- integración con un LLM local o remoto.
- exportación de historial.
- iconos personalizados y temas claro/oscuro reales.
- ranking de confianza más sofisticado.
- tests de interfaz y de OCR con fixtures de imagen.

---

## Aviso final

Esta versión está lista para ejecutarse, probar OCR y servir como base sólida para una herramienta de estudio de escritorio en Windows. El motor de respuesta incluido es deliberadamente conservador y demostrativo; la arquitectura ya deja preparado el punto de integración para inteligencia artificial más avanzada sin mezclarla con la capa de UI ni con la lógica de captura.
