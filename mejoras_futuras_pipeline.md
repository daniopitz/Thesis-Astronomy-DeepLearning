# Mejoras futuras para el pipeline de detección de FRBs (DRAFTS-UC/src)

Este documento propone mejoras priorizadas para el pipeline en `D:/Seba - Dev/DRAFTS-UC/src`, tomando como base lo actualmente implementado (ingesta FITS/Filterbank, downsampling, dedispersión incoherente CPU/GPU, detección por SNR y CenterNet, clasificación ResNet, visualización y chunking).

## 1) Mitigación de RFI (tiempo real y post-proceso)

- Zero-DM filter (con reversión segura a DMs bajos)
- IQRM (enmascaramiento robusto por bloques ~1 s)
- Spectral Kurtosis (SK) por canal/ventana
- Z-dot filter para rechazar derivas no astrofísicas
- Fase off-line con reportes de cobertura de máscara y métricas
- Implementación: módulo `preprocessing/rfi.py` con `apply_zero_dm`, `apply_iqrm`, `apply_spectral_kurtosis`, `apply_zdot`; hooks antes de dedispersión y logging estructurado

## 2) Dedispersión

- FDMT (Fourier-Domain MD Transform) en GPU (PyTorch/CUDA)
- Variantes aceleradas: tree/sub-band
- Ruta semicoherente opcional
- Implementación: `preprocessing/fdmt.py` (API alineada con `preprocessing/dedispersion.py`) y selector `config.DEDISP_KIND ∈ {incoherent, fdmt, tree, semi_coherent}`

## 3) Matched filtering y SNR

- Banco de anchos dinámico (µs–s), supresión de línea base y estimación robusta del ruido (MAD)
- Convolución en GPU (FFT/conv1d) para acelerar barridos de anchos
- Fusión de evidencias SNR + detector NN (candidatos híbridos)

## 4) Tamizado/agrupamiento (sifting/clustering)

- DBSCAN/HDBSCAN sobre (tiempo, DM, ancho) para consolidar triggers
- NMS transversal tiempo/DM para evitar duplicados entre ventanas
- Implementación: `analysis/trigger_clustering.py` → `cluster_triggers(trigs) -> groups`

## 5) Detección y clasificación (ML)

- Curvas precisión–recobrado por banda y umbrales calibrados
- Transfer learning por dominio y augmentations físicas
- Versionado/export de modelos y tests de deriva temporal

## 6) Triggers y alertas

- Emisión de VOEvent 2.0 (JSON/XML) con metadatos (t, DM, SNR, evidencia)
- Ring buffer de baseband (5–10 s) para “freeze & dump” tras trigger
- Rate limiting/backoff y colas (p.ej., Redis/Kafka)
- Implementación: `alerts/voevent.py` + hook en `core/detection_engine.py`

## 7) Transformadas de Radon y Hough

- Búsqueda de firmas lineales/curvas en tiempo–DM cuando el bow-tie pierde contraste (mm)
- Uso como voto adicional a SNR/NN (fusión de evidencias)
- Implementación: `analysis/radon_hough.py` y pruebas en subconjuntos

## 8) Exploración cuántica (I+D)

- Prototipos con frameworks cuánticos para subproblemas discretos
- Benchmarks sintéticos (no ruta operativa aún)

## 9) Observabilidad y calidad

- Métricas (Prometheus) y dashboards (Grafana): latencias, throughput, FP/FN
- Reportes por chunk/slice (CSV/Parquet) con trazabilidad

## 10) Reproducibilidad y datos

- Versionado de configuración y artefactos (MLflow/DVC)
- Manifiestos de datasets (catálogos públicos + sintéticos controlados)

## 11) Polarización y validación física

- Soporte/validación en Stokes (I/Q/U/V) para PSRFITS IQUV
- Validaciones espectrales/polarimétricas en candidatos fuertes

## 12) Compatibilidad futura (SKAO/ngVLA)

- Parametrización de anchos, DM y sampling; modularidad de backends
- Plan de escalado horizontal (sharding por DM/tiempo) y E/S eficiente

---

## Roadmap sugerido (prioridades)

- P0: RFI (Zero-DM, IQRM, SK) • Clustering/NMS • Alertas VOEvent
- P1: FDMT GPU • Matched filtering GPU • Observabilidad
- P2: Radon/Hough • Polarización avanzada • Reproducibilidad sólida
- P3: Semicoherente • Exploración cuántica (I+D)

## Indicadores de éxito

- −50% duplicados por DM tras clustering/NMS
- +20–40% throughput con FDMT/conv GPU al mismo presupuesto
- <10% falsos positivos manteniendo sensibilidad (FRB 121102 + sintéticos)
