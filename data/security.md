# Controles básicos de seguridad informática

## Identidad y autenticación

Asigná una cuenta individual a cada persona para que las acciones puedan atribuirse. Los servicios automatizados requieren identidades propias, con permisos específicos y credenciales administradas por separado. Mantené un inventario de responsables y revisá las cuentas cuando haya cambios de función o egresos. Evitá que las identidades técnicas se usen para accesos interactivos salvo que exista un procedimiento documentado.

Para contraseñas, promové frases largas y únicas y el uso de un gestor autorizado. Una clave reutilizada puede comprometer varios servicios si se filtra en uno de ellos. Los procesos de restablecimiento deben verificar la identidad por un canal aprobado y revocar las sesiones que corresponda. Una solicitud de restablecimiento inesperada merece revisión. No se deben compartir contraseñas por tickets, chats ni correo electrónico.

La autenticación multifactor combina factores, como algo que la persona conoce y un dispositivo que posee. Priorizá factores resistentes a la suplantación para cuentas con privilegios y accesos remotos cuando la plataforma los admita. Conservá métodos de recuperación bajo control y probalos con personal autorizado. Ante solicitudes repetidas de autorización que la persona no inició, indicá que deben rechazarse y reportarse. Revisá los registros de acceso y el estado de la cuenta antes de restablecer el factor.

## Control de accesos

Otorgá el nivel de acceso mínimo necesario y usá grupos o roles según tareas. Separá las cuentas administrativas de las cuentas de uso diario. Para altas y cambios de permisos, registrá quién solicitó el acceso, quién lo aprobó, el alcance asignado y la vigencia. Revisá a intervalos regulares los grupos privilegiados y los accesos temporales. Revocá los permisos cuando desaparezca la necesidad y verificá que la revocación se propague a los sistemas involucrados.

Al investigar un acceso denegado, verificá primero la identidad autenticada, los grupos efectivos y el recurso solicitado. Una diferencia entre permisos asignados y efectivos puede deberse a una sesión anterior o a una regla más restrictiva. Evaluá el cambio mínimo que resuelve el caso y comprobá tanto el acceso autorizado como la denegación a usuarios que deben seguir excluidos.

## Actualizaciones y prevención

Mantené un inventario de versiones y responsables. Priorizá las actualizaciones de seguridad según exposición, impacto y disponibilidad de mitigaciones. Probá los cambios en un entorno representativo y definí cómo recuperar el servicio si una actualización falla. Durante el despliegue verificá la versión instalada, el estado de los procesos, la conectividad necesaria y los indicadores de error. Registrá los equipos pendientes y el motivo del aplazamiento.

Combiná actualizaciones con copias verificadas, registro de eventos y revisión de accesos. Si se detecta un comportamiento anómalo, conservá fechas, alertas y registros asociados sin difundir información sensible. Seguí el procedimiento de escalamiento antes de aislar recursos compartidos, salvo que el protocolo habilite una contención inmediata. Tras la contención, revisá el alcance y mantené constancia de cada cambio. Validá la recuperación antes de cerrar el caso.

## Información en registros y tickets

Para reconstruir la secuencia de un incidente, correlacioná los eventos de identidad con los de la aplicación y del sistema que recibió la solicitud. Conservá la zona horaria y verificá la sincronización de los relojes antes de ordenar los eventos. Un cambio de permisos aprobado y un intento de acceso rechazado pueden aparecer próximos sin estar relacionados. Compará la cuenta, el recurso, el identificador de sesión y el resultado de cada operación disponible. Si hay un intervalo sin registros, anotá la ausencia y revisá el estado del colector o la política de retención antes de sacar conclusiones.

Adjuntá únicamente el detalle necesario para reproducir el diagnóstico. Eliminá contraseñas, claves API, códigos de recuperación y datos personales de capturas o reportes. Si se descubre una credencial en un registro, reportá la exposición y aplicá la rotación autorizada. Conservá la evidencia en el repositorio de incidentes definido por la organización y limitá su acceso al personal que la necesita.
