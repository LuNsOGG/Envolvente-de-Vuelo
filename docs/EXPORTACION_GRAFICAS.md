# Exportación de gráficas · versión 4.3

Por solicitud del usuario, Exportar se simplifica a tres gráficas de la condición seleccionada: maniobras, ráfagas y combinado, cada una en PNG y SVG. No genera PDF, DOCX, CSV, JSON, MATLAB, portadas ni dibujos adicionales de Niu. Guardar sigue conservando el proyecto JSON.

La opción Comparar con tesis publicada también se respeta al exportar. El progreso y la cancelación siguen disponibles. Una cancelación conserva los archivos que ya se hayan escrito y puede dejar menos de seis imágenes; no se borran entregas anteriores.

La ventana ya no muestra los selectores de reportes ni el botón Portada. El procedimiento A3/A4 sigue disponible para consulta independiente. Los campos antiguos de proyectos y los generadores históricos se conservan para abrir archivos y reproducir etapas previas; no participan en el botón Exportar.

El Live Script Cessna y el archivo LaTeX para Overleaf se entregan aparte. El Live Script usa el formato oficial de texto de Live Editor (.m), disponible desde MATLAB R2025a, con secciones, texto y ecuaciones. Contiene todo el cálculo y las tres gráficas; no necesita archivos de datos ni funciones propias. Para usar el peso del capítulo 1.9 se cambia W de 4000 a 4631 lbf.

La ejecución nativa del Live Script sigue bloqueada en esta estación por el error 5201 de servicios MathWorks. La revisión de sintaxis y el contraste numérico con el motor se registran por separado; no se presentan como una ejecución nativa aprobada.

Los puntos 22, 23 y 24 siguen pendientes.

## Comprobación

La suite aprobó 152 pruebas. Se comprobó el EXE instalado con salida 0 y exportación real de ambos ejemplos: exactamente seis archivos por exportación. Se verificaron las 1256 dependencias de la distribución y se preservó la instalación anterior. [Registro](exportacion_graficas_validacion.json).

Las ecuaciones del Live Script se contrastaron con todas las curvas e intersecciones del motor para 4000 y 4631 lbf; la diferencia máxima fue 3.6e-15. MLint R2025a terminó sin diagnósticos. Esta comparación independiente no sustituye la ejecución nativa en MATLAB. El código LaTeX se revisó en estructura, ecuaciones y valores; no se compiló aquí porque no hay motor TeX instalado.

## Comprobación

La suite aprobó 152 pruebas. Se comprobó el EXE instalado con salida 0 y exportación real de ambos ejemplos: exactamente seis archivos por exportación. Se verificaron las 1256 dependencias de la distribución y se preservó la instalación anterior. [Registro](exportacion_graficas_validacion.json).

Las ecuaciones del Live Script se contrastaron con todas las curvas e intersecciones del motor para 4000 y 4631 lbf; la diferencia máxima fue 3.6e-15. MLint R2025a terminó sin diagnósticos. Esta comparación independiente no sustituye la ejecución nativa en MATLAB. El código LaTeX se revisó en estructura, ecuaciones y valores; no se compiló aquí porque no hay motor TeX instalado.
