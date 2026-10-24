# Contribuir al proyecto

Prepare Python 3.12 y las dependencias de `requirements-dev.txt` siguiendo [DESARROLLO.md](docs/DESARROLLO.md). Trabaje desde la raíz del proyecto.

1. Cree una rama para el cambio y describa el problema concreto.
2. Mantenga las ecuaciones en `src/calculations/`; interfaz, reportes y gráficas deben consumir el mismo resultado.
3. Declare fuente, unidad e hipótesis de cada parámetro. Diferencie CL de CN, peso de masa y pendiente por grado de pendiente por radián.
4. Ejecute `python -B tools/run_tests.py`. Para cambios del motor, contraste una condición independiente y verifique las curvas. Para cambios de empaquetado, compruebe el ejecutable recién generado.
5. Describa el comportamiento final, las pruebas y las limitaciones en el commit o pull request.

No borre archivos, resultados, respaldos ni dependencias sin permiso específico del propietario. Los guardados y exportaciones deben conservar versiones anteriores. No utilice `git clean`, `reset --hard`, limpiezas recursivas ni `PyInstaller --clean` en la carpeta de trabajo del propietario.

No suba entornos, recuperaciones de usuario, credenciales, libros escaneados ni exportaciones completas al historial Git. Una exclusión de `.gitignore` conserva el archivo local. No asigne una licencia al proyecto sin decisión de su propietario.

Las pruebas correspondientes a interfaces y motores históricos siguen siendo parte del proyecto; su presencia no los convierte en la interfaz predeterminada.
