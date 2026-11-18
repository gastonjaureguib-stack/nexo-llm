# Diagnóstico de redes y conectividad

## Alcance de la incidencia

Identificá si la conexión lenta afecta a un equipo, a todos los equipos del mismo punto de acceso o a toda la sede. Anotá desde cuándo ocurre, si es constante y qué aplicaciones muestran el síntoma. Probá el mismo destino desde otro equipo y, si es posible, compará Wi-Fi con Ethernet. Si el rendimiento mejora al conectar un cable, concentrá el diagnóstico en la cobertura inalámbrica, las interferencias y la ocupación del canal. Antes de cambiar configuraciones compartidas, registrá los valores actuales y acordá una ventana si puede haber impacto.

## Configuración IP y DHCP

Revisá en la interfaz activa la dirección IP, la máscara o el prefijo, la puerta de enlace y los servidores DNS. La máscara permite determinar qué destinos pertenecen al segmento local. Para llegar a otra red, el equipo normalmente envía los paquetes a la puerta de enlace. Compará los parámetros con los de un dispositivo operativo del mismo segmento. Si la dirección IPv4 es autoconfigurada en el rango 169.254.0.0/16 o falta una puerta de enlace esperada, investigá la concesión DHCP, el segmento de la red y el enlace físico o inalámbrico.

DHCP entrega parámetros durante un período de concesión. Si un equipo pierde conectividad al renovar, revisá el alcance del servidor, la disponibilidad de direcciones y el reenvío entre segmentos. Una dirección duplicada puede causar fallos intermitentes aunque la configuración parezca correcta. Contrastá las concesiones y reservas con los equipos afectados. Evitá asignar una dirección al azar, ya que podría estar en uso o pertenecer al conjunto dinámico.

## DNS y pruebas por etapas

Probá el acceso a un servicio conocido de la red local, después a un destino autorizado por dirección IP y finalmente por nombre. Si funciona por IP pero falla por nombre, consultá explícitamente al resolvedor configurado y compará sus respuestas con las esperadas. Una respuesta inexistente y una consulta que vence tienen causas distintas. En el primer caso verificá el registro y la zona consultada. En el segundo, revisá el alcance del resolvedor y su disponibilidad. Si el problema afecta solo a un nombre interno, conservá la comprobación dentro de la red que sirve esa zona.

## Ancho de banda, latencia y pérdida

El ancho de banda indica la capacidad de transferencia de un enlace. La latencia mide el tiempo del recorrido y la pérdida mide el porcentaje de paquetes que no llegan. Son señales complementarias. Una descarga puede saturar el enlace mientras la red permanece conectada. El tiempo de respuesta puede empeorar sin que caiga el ancho de banda contratado, por ejemplo mientras se acumulan colas de tráfico bajo carga.

Para diagnosticar internet lento, compará el caudal y la latencia con el enlace en reposo y durante el problema. Usá destinos de prueba autorizados y medí primero la puerta de enlace, luego un destino externo conocido. Si la latencia o la pérdida empieza en el tramo local, revisá señal, cableado, errores de interfaz y congestión. Si el tramo local es estable pero el problema aparece en varios destinos externos, revisá el uso del enlace de salida y escalá al proveedor de conectividad con los horarios y las mediciones. Un equipo intermedio puede limitar sus respuestas de diagnóstico sin perjudicar el tránsito. Correlacioná el resultado con pruebas hacia el destino final.

## Cierre del incidente

Antes de escalar una degradación intermitente, anotá si la demora aparece al abrir la conexión o durante la transferencia. Una resolución DNS lenta puede demorar el inicio sin afectar una descarga en curso. Contrastá los tiempos de resolución con los de establecimiento de la conexión y los de descarga. Si solo falla una aplicación, compará con otro servicio del mismo segmento y revisá si ambos usan el mismo proxy o túnel. Registrá también si la incidencia coincide con cambios de ruta, saturación de un enlace compartido o el inicio de un respaldo. Separar estas etapas ayuda a elegir qué equipo debe continuar el diagnóstico.

Repetí la medición inicial después de cada cambio y conservá una comparación de resultados. Registrá el segmento, el enlace, los destinos, los horarios y las condiciones de carga. Si se normalizó el servicio, confirmalo con una persona afectada y dejá documentado qué cambio produjo la mejora.
