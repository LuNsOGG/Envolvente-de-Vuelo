# Desarrollo, pruebas y distribución

## Entorno nuevo

Plataforma comprobada: Windows, Python 3.12 de 64 bits. Ejecute desde la raíz:

```powershell
python -m venv .venv
$env:PIP_CACHE_DIR = "$PWD\.runtime\pip-cache"
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -B main.py
```

`requirements-app.txt` contiene las dependencias de la aplicación; `requirements-dev.txt` añade pytest, Pillow y PyInstaller. `requirements-sources.txt` añade PyMuPDF y OCR para inspecciones bibliográficas opcionales. El `requirements.txt` original se conserva como referencia del entorno anterior, que incluía herramientas auxiliares.

Las versiones están fijadas a las distribuciones instaladas en la entrega. Un clon necesita descargarlas de un índice de paquetes disponible. No se versionan los paquetes binarios locales.

En la estación original, `bootstrap.py` puede cargar `.runtime/packages` al ejecutar Python 3.12, incluso si se usa otro entorno. Para comprobar una instalación independiente utilice un clon nuevo sin esa carpeta; no borre la instalación existente para simularlo. Los lanzadores priorizan `.venv`, después el runtime de la estación original y finalmente `python` del PATH.

## Comandos

| Acción | Comando desde la raíz con el Python preparado |
|---|---|
| Abrir interfaz | `python -B main.py` |
| Ayuda | `python -B main.py --help` |
| Abrir proyecto | `python -B main.py --project examples/ejemplo_2.json` |
| Exportar condición activa | `python -B main.py --project examples/ejemplo_1.json --export` |
| Exportar todos los casos | `python -B main.py --project data/proyecto_inicial.json --all` |
| Elegir caso de un proyecto | `python -B main.py --project RUTA.json --case ID --export` |
| Dibujos explicativos históricos | `python -B main.py --project data/proyecto_inicial.json --niu` |
| Pruebas | `python -B tools/run_tests.py` |
| Comprobación numérica y persistencia | `python -B main.py --comprobar` |
| Comprobación GUI con exportaciones | `python -B main.py --comprobar-gui` |
| Compilar | `python -B tools/build_exe.py` |

Las rutas de proyectos deben quedar dentro de la raíz. La comprobación del EXE usa esos mismos argumentos: `Envolventes_de_Vuelo.exe --comprobar-gui`. El modo no gráfico no imprime el destino de su JSON de comprobación: consulte la carpeta nueva en `outputs/qa/niu_exe_*/`.

## Pruebas e integración continua

`tests/conftest.py` mantiene una sola QApplication y usa `QT_QPA_PLATFORM=offscreen`. Las pruebas verifican unidades, valores independientes, curvas e intersecciones, entradas inválidas, edición, guardado y reportes. Las pruebas de interfaces históricas se conservan.

El flujo `.github/workflows/pruebas.yml` ejecuta la suite y una comprobación numérica en Windows para cada push o pull request. Conserva los informes como artefactos cuando están disponibles. El resultado local y el de Actions se distinguen en [VALIDACION.md](VALIDACION.md).

Si necesita XML, cree un nombre nuevo para conservar informes anteriores:

```powershell
python -B -c "import bootstrap,pytest; raise SystemExit(pytest.main(['tests','-q','-p','no:cacheprovider','--junitxml=outputs/qa/pruebas_NUEVA_FECHA.xml']))"
```

No use un `--basetemp` existente ni comandos de limpieza automática sobre archivos del propietario.

## Compilar una distribución de Windows

`tools/build_exe.py` genera un destino nuevo bajo `aplicacion/version_FECHA_HORA/Envolventes_de_Vuelo/` y registros en `.runtime/builds/`. La compilación usa PyInstaller en modo `onedir`; no instala automáticamente el resultado sobre el EXE de la raíz. El inventario de binarios filtra las DLL ICU de Poppler antes de copiar para evitar el conflicto con Qt; no requiere borrar DLL de la instalación.

Para distribuir el resultado deben viajar juntos `Envolventes_de_Vuelo.exe` y `_internal/`. También pueden incluirse `envolventes.workspace.json`, `examples/` y los manuales. Colóquelos en una carpeta con permisos de escritura; la aplicación crea allí sus datos de trabajo. No es una distribución de archivo único.

El flujo manual **Compilar Windows**, disponible en Actions, instala el entorno, ejecuta pruebas, compila, comprueba el EXE y sube la carpeta completa como artefacto. Descargue y extraiga el ZIP antes de abrir la aplicación. El artefacto tiene retención limitada de GitHub; no se crea una Release permanente automáticamente.

Antes de sustituir una instalación local, archive juntos el EXE y `_internal/` anteriores en un destino nuevo y verifique su integridad. No elimine versiones previas sin autorización específica. Una modificación de documentación no exige recompilar el ejecutable existente.

## Herramientas auxiliares e históricas

| Herramienta | Requisito y alcance |
|---|---|
| `create_cases.py` | Genera el proyecto de la tarea inicial bajo un nombre libre |
| `inspect_sources.py` | Renderiza un PDF local `Airframe*.pdf`; `--ocr` requiere las dependencias opcionales |
| `inspect_sources.py --official` | Descarga las referencias oficiales históricas si no existen; requiere red |
| `qa_exports.py CARPETA` | Contrasta tablas y renderiza PDF de una exportación; requiere PyMuPDF/Pillow |
| `try_render_docx.py` (solo local) | Herramienta histórica ligada al runtime y al renderizador de la estación original; no se publica ni forma parte del flujo portable |
| `ui_smoke.py` | Comprobación histórica de interfaz; para la vigente use `--comprobar-gui` |

La aplicación no depende de OCR, de LibreOffice ni de los libros escaneados para arrancar o calcular. No se asegura compatibilidad de escritorio o empaquetado con Linux/macOS.
