# Operación y diagnóstico de servidores

## Disponibilidad y monitoreo

Definí qué significa que el servicio esté disponible desde la perspectiva de una persona usuaria. Un proceso activo o un servidor que responde al ping puede seguir sin entregar la funcionalidad esperada. Combiná comprobaciones de estado con una operación representativa, como consultar un recurso de solo lectura en una interfaz autorizada. Registrá el tiempo de respuesta, los códigos de error y el porcentaje de operaciones concluidas.

Distinguí una caída completa de una degradación, de un fallo limitado a una zona y de una dependencia que no responde. Compará el monitoreo de la aplicación con el del host, la red y los servicios de respaldo. Las alarmas deben incluir el servicio, el recurso afectado, el umbral y el período de evaluación. Usá umbrales y duración acordes con la línea base para evitar que un pico breve produzca una alerta que oculte incidentes sostenidos.

## Recursos del sistema

Ante consumo alto de CPU, identificá si la carga es sostenida, qué procesos la concentran y si coincide con tráfico, despliegues o trabajos programados. Revisá el tiempo de espera de E/S para distinguir demanda de cómputo de actividad de disco. Contrastá el resultado con la latencia y el volumen de solicitudes. Revisá el límite de CPU asignado si la aplicación ejecuta dentro de un contenedor o máquina virtual.

En memoria, observá la memoria disponible, la paginación y las terminaciones por falta de memoria. El uso de memoria para caché es un comportamiento normal mientras pueda recuperarse cuando una aplicación lo requiere. Una aplicación que crece sin estabilizarse y obliga a paginar merece una investigación; registrá las tendencias por proceso y correlacionalas con la carga y los ciclos de trabajo.

Para almacenamiento, monitoreá capacidad libre, velocidad de crecimiento, latencia de E/S y errores de escritura del volumen de la aplicación. Revisá si la rotación de registros y los trabajos programados respetan sus políticas. Para red, medí errores de interfaz, conexiones activas y tiempos hacia dependencias. Usá la misma ventana de observación para todas las señales antes de decidir cuál es causa y cuál es consecuencia.

## Mantenimiento preventivo

Planificá los cambios sobre una ventana aprobada, con responsables, copias comprobadas y un procedimiento de reversión. Capturá el estado previo de la aplicación y de sus dependencias. Si existe redundancia, intervení una unidad por vez cuando el procedimiento lo permita y verificá el servicio entre etapas. Mantené un inventario de componentes y registrá la versión o configuración que queda activa.

Después del mantenimiento, verificá el resultado desde el host y desde un cliente representativo. Compará métricas y registros con la línea base y confirmá que se restablecieron los trabajos programados y los respaldos. Si se observaron errores nuevos, aplicá el criterio de reversión acordado en vez de acumular cambios sin aislar la causa.

## Protocolo de incidentes

Cuando varias instancias atienden el mismo servicio, compará la tasa de errores por instancia y el estado que informa el balanceador. Una comprobación de salud demasiado superficial puede mantener en rotación un host que falla al consultar una dependencia. Si el procedimiento permite retirarlo, verificá primero la capacidad de las instancias restantes y observá las conexiones que siguen abiertas durante el drenaje. Antes de reincorporarlo, ejecutá una operación representativa y confirmá que sus métricas vuelvan a la distribución habitual. Si se mantiene fuera de servicio, registrá la capacidad remanente y el criterio para escalar.

Registrá la hora de inicio, el síntoma, los servicios afectados y el impacto. Identificá una persona responsable de coordinar la respuesta y comunicá un próximo plazo de actualización. Antes de reiniciar, preservá los eventos y métricas necesarios para investigar. Verificá cambios recientes, dependencias y estado de los recursos. Aislá una hipótesis por vez y documentá la verificación asociada.

Priorizá recuperar el servicio con un cambio autorizado, reversible cuando sea posible y de alcance acotado. Comprobá la recuperación con la misma medición que señaló el incidente y observá el servicio durante un período razonable. En el cierre, registrá la causa confirmada, el cambio aplicado y las acciones preventivas con responsables. Si la causa sigue abierta, dejá consignadas las hipótesis descartadas y la evidencia que aún falta.
