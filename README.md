# Grimoire
Una coleccion de scripts utilitarios disenados para automatizar tareas comunes de desarrollo y administracion. Cada script representa una "habilidad" o tecnica independiente.

## Instalacion y Configuracion
Para utilizar los scripts de manera global desde cualquier terminal, se recomienda agregarlos al `PATH` del sistema o configurar un alias en tu archivo de perfil (por ejemplo, `~/.bash_profile` o `~/.bashrc`):

alias zoltraak="python3 /ruta/a/tu/repositorio/Grimoire.d/zoltraak.py"

## Scripts disponibles
| Script | Habilidad | Descripcion |
| :--- | :--- | :--- |
| `zoltraak.py` | Extraccion de Contexto | Parsea un directorio y genera un resumen estructurado de los archivos para alimentar a una IA. |
| `revelio.sql` | Diagnostico SQL Server | Ejecuta una evaluacion inicial de salud en instancias SQL Server (sesiones, memoria, CPU y espacio). |

---

## Uso de Zoltraak
`zoltraak.py` permite filtrar que archivos incluir en el resumen mediante flags combinables.

**Sintaxis:**
zoltraak /ruta/al/directorio --python --js --md

## Uso de Revelio (SQL Server Health)
`revelio.sql` esta pensado para ser ejecutado con la herramienta `sqlcmd` ante incidentes de rendimiento o bloqueos en la base de datos.

**Sintaxis:**
sqlcmd -S tcp:[host_addr],[port] -U [user] -P [passwd] -v SQLCMDFORMAT=ascii -W -i revelio.sql | tee [instancename_health].txt
