# Organización y conservación

La raíz sigue siendo la ubicación de `main.py`, `bootstrap.py` y `envolventes.workspace.json`. El EXE instalado y `_internal/` permanecen juntos. Los documentos y fotografías originales conservan su ubicación porque las exportaciones registran sus huellas desde la raíz.

## Contenido versionado

| Ubicación | Contenido |
|---|---|
| Raíz | README, historial, contribución, dependencias, puntos de entrada y reglas Git |
| `src/` | Todos los módulos Python vigentes e históricos |
| `tests/` | Suite de pruebas; artefactos generados excluidos |
| `tools/` | Compilación, pruebas, inspección, QA y lanzadores |
| `examples/` | Dos proyectos actuales listos para abrir |
| `data/proyecto_inicial.json` | Condiciones históricas de la tarea Cessna |
| `docs/` | Documentación actual, manual de Niu y referencias numéricas |
| `docs/imagenes/` | Captura propia de la interfaz |
| `.github/workflows/` | Pruebas y compilación manual de Windows |

## Contenido conservado únicamente en la estación local

| Ubicación | Motivo de conservación local |
|---|---|
| `.runtime/`, `.venv/` | Paquetes, cachés, temporales y registros reproducibles |
| `Envolventes_de_Vuelo.exe`, `_internal/` | Distribución binaria ya instalada |
| `aplicacion/` | Compilaciones anteriores y destinos nuevos |
| `archivo_desarrollo/` | Copias de código, documentación y distribuciones previas |
| `outputs/` | Entregas, exportaciones, OCR y evidencia completa de QA |
| `data/recuperaciones/` | Ediciones y recuperaciones del propietario |
| `tests/artifacts/` | Archivos generados por pruebas |
| PDF/JPG originales y `sources/niu_pages/` | Bibliografía, imágenes y OCR; se documentan sin redistribuir escaneos |
| `.vscode/` | Configuración específica de la estación |
| Registros de instalación en `docs/` | Rutas absolutas, inventarios y resultados de instalaciones locales |
| Manuales y entregas históricos | Historial de trabajo con referencias específicas de la estación original |
| `sources/registro_fuentes.md` | Registro histórico de inspección; bibliografía pública en `docs/FUENTES.md` |
| `tools/try_render_docx.py` | Auxiliar histórico vinculado al runtime de la estación original |

`.gitignore` controla su incorporación al historial y no los elimina. Los motores e interfaces históricos permanecen en el código porque permiten abrir y comprobar proyectos previos. No se mueven los originales que forman parte de las rutas de ejecución o de registro de huellas.

Antes de actualizar el README se conservó su contenido anterior junto con huellas de EXE, fuentes PDF y fotografías en `archivo_desarrollo/antes_github_20261024_094048/`. Los archivos añadidos proporcionan índices y ejemplos sin reorganizar dependencias internas de la aplicación.

Para futuras actualizaciones, use destinos nuevos y compare las huellas de los archivos esenciales. No borre versiones, pruebas, respaldos ni recuperaciones sin permiso específico del propietario.
