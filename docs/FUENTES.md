# Fuentes y trazabilidad

## Libro de referencia

Michael Chun-Yung Niu, *Airframe Structural Design*, segunda edición indicada en el escaneo, capítulo 3, **Aircraft Loads**. La página legal del archivo original muestra copyright de 1988 y segunda impresión de enero de 1989; se conserva esa información sin inferir otra fecha de edición.

- Ráfagas cuasiestáticas: páginas impresas 43–45, ecuaciones 3.4.1–3.4.5.
- Ejemplo 2 de §3.11: páginas impresas 74–77, figuras 3.11.4–3.11.7.
- El archivo local `Chapter3.pdf` tiene 69 páginas que corresponden a las páginas impresas 21–89. No use esa numeración como índice directo del PDF completo.

SHA256 de `Chapter3.pdf`: `9ABF17EE98FCA8EAE9E97060606AD74869AAFC3A32624C9D1F819C6E5F8DCA4A`.

Los archivos `Chapter3.pdf` y `Airframe Structural Design, M. Chun-Yung 2a Ed (1).pdf`, sus páginas renderizadas y el OCR se conservan localmente. El repositorio documenta sus resultados y referencias sin incluir los escaneos. La interfaz y los dos ejemplos no requieren esos archivos para calcular.

## Datos de la hoja Excel

Las fotografías locales `308aa1a8-3551-4e50-a2fb-7b7e27fd85c9.jpg` y `cd1a2819-dc32-4a24-b668-615ca1cc63e5.jpg` son la fuente de las lecturas del Ejemplo 1. Las unidades interpretadas, las hipótesis y las lecturas originales se conservan en los parámetros JSON. CN−=−1.35 y las intensidades de ráfaga 50/25 ft/s no se presentan como datos medidos de esas fotografías.

## Normativa histórica

Estas fuentes oficiales corresponden a la edición de 2016 del CFR y se utilizan como referencia histórica de ecuaciones y construcción de diagramas; su presencia no demuestra aplicabilidad a una aeronave concreta.

- [14 CFR Part 23, Appendix A, 2016](https://www.govinfo.gov/content/pkg/CFR-2016-title14-vol1/pdf/CFR-2016-title14-vol1-part23-appA.pdf).
- [§23.333, Flight envelope](https://www.govinfo.gov/content/pkg/CFR-2016-title14-vol1/pdf/CFR-2016-title14-vol1-sec23-333.pdf).
- [§23.335, Design airspeeds](https://www.govinfo.gov/content/pkg/CFR-2016-title14-vol1/pdf/CFR-2016-title14-vol1-sec23-335.pdf).
- [§23.337, Limit maneuvering load factors](https://www.govinfo.gov/content/pkg/CFR-2016-title14-vol1/pdf/CFR-2016-title14-vol1-sec23-337.pdf).
- [§23.341, Gust load factors](https://www.govinfo.gov/content/pkg/CFR-2016-title14-vol1/pdf/CFR-2016-title14-vol1-sec23-341.pdf).
- [NASA NTRS, NACA-TR-1206](https://ntrs.nasa.gov/search.jsp?R=19930090988), referencia complementaria de la formulación revisada de ráfagas.

## Incertidumbres conservadas

La tesis *Diseño de la caja de torsión de una aeronave cuatriplaza* y la variante exacta del Cessna del ejercicio inicial siguen pendientes. Las lecturas por Mach del Ejemplo 2 incluyen aproximaciones documentadas. Los productos nₙWₙ y nᵤWᵤ de las fotografías no se corrigen silenciosamente para hacerlos coincidir.

La posible relación c=S/b del Ejemplo 1 no está confirmada. No se utiliza para afirmar el cumplimiento geométrico del apéndice A. El registro histórico local `sources/registro_fuentes.md` localiza otras figuras revisadas del libro; las páginas de visor que allí aparecen corresponden al PDF completo original.
