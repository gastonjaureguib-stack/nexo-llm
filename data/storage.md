# Diagnóstico y mantenimiento de almacenamiento

## Primeros pasos ante un disco lleno

Verificá qué volumen o punto de montaje quedó sin espacio antes de actuar. Compará espacio total, usado y disponible. En Linux podés consultar el espacio con `df -h` y los inodos con `df -i`. Un sistema con inodos agotados puede impedir crear archivos incluso cuando quedan bloques disponibles. En Windows, consultá el espacio libre del volumen afectado y revisá si se aplican cuotas al usuario o al servicio. Confirmá si el problema afecta escrituras, registros, bases de datos, respaldos o archivos temporales.

Identificá qué directorios crecieron y en qué momento. En Linux, `du -x -h --max-depth=1` permite inspeccionar el uso desde el montaje afectado sin recorrer otros sistemas de archivos. Si ese resultado no explica lo que informa `df`, revisá si un proceso mantiene abierto un archivo eliminado, si hay instantáneas que todavía conservan bloques o si existe espacio reservado. Compará el crecimiento con tareas recientes como rotación de logs, despliegues o exportaciones.

Liberá espacio con acciones aprobadas y de impacto acotado. Primero aplicá la política de rotación y retención de registros, mové exportaciones autorizadas a un destino con capacidad o quitá temporales cuya propiedad y vigencia estén verificadas. Evitá borrar datos activos, archivos que usa la base de datos o respaldos sujetos a retención. Si el volumen no permite recuperar margen suficiente, escalá para ampliar la capacidad según el procedimiento del sistema de archivos y del almacenamiento. Al terminar, comprobá espacio libre, escrituras y estado del servicio. Activá una alerta de crecimiento y documentá la causa para evitar recurrencias.

## HDD, SSD y sistemas de archivos

Los HDD usan partes mecánicas y suelen ofrecer mayor capacidad por costo. Los SSD usan memoria flash y suelen dar menor latencia en accesos aleatorios. Para elegir entre ellos, considerá patrón de escritura, capacidad, latencia y resistencia declarada por el fabricante. Un degradado en rendimiento no demuestra un fallo físico. Revisá la latencia de E/S, la cola, la tasa de errores del dispositivo y los eventos del sistema. También verificá si coincide con tareas de respaldo, análisis masivos o una reconstrucción del arreglo.

El sistema de archivos administra nombres, permisos y asignación de bloques. Formatear un volumen destruye el acceso normal a los datos existentes. Si aparecen errores de consistencia, preservá los datos y revisá los registros antes de ejecutar una reparación. Confirmá el procedimiento para ese sistema de archivos y si debe estar desmontado. Cuando hay indicios de fallo físico, priorizá una recuperación controlada y evitá someter el dispositivo a escrituras innecesarias.

## Copias de seguridad y recuperación

En volúmenes de bases de datos, distinguí el crecimiento de los archivos de datos del crecimiento de los registros de transacciones. Un registro que deja de truncarse puede señalar un respaldo fallido, una réplica atrasada o una transacción extensa. Consultá las métricas del motor antes de mover archivos. Si las mediciones muestran un aumento sostenido, estimá cuánto tiempo queda hasta agotar el margen con la tasa reciente y contrastá ese plazo con la próxima ventana de intervención. Cuando intervengan varios volúmenes, identificá cuál recibe las escrituras y cuáles contienen respaldos o archivos de recuperación.

Definí qué datos deben respaldarse, cuánto tiempo pueden perderse desde el último respaldo y en cuánto tiempo debe recuperarse el servicio. Separá las copias del volumen primario y protegé al menos una copia contra modificación accidental. Un arreglo redundante puede mitigar una falla de disco, pero replica borrados y cambios, por lo que se necesita un respaldo independiente.

Verificá que los trabajos terminen, que la copia se pueda leer y que existan pruebas periódicas de restauración. Para recuperar un archivo o una aplicación, identificá una versión anterior al incidente y restaurala primero en un destino controlado. Compará contenido y permisos, y validá la integridad con la persona responsable. En bases de datos, verificá la consistencia con el método de restauración propio del motor. Solo después promové los datos restaurados a la ubicación de servicio y registrá el punto de recuperación.
