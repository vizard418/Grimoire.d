/* =============================================================================
* Title: Test inicial evaluacion de salud en instancia SQL Server
* Author: Gonza Vizard
* Date: 23 sept 2026
============================================================================= */

/*------------------------------------------------------------------------------
Herramienta Sqlcmd GO for Linux. La contraseña corresponde a la variable
de entorno en ~/.bash_profile
$> sqlcmd -S tcp:[host_addr],[port] -U [user] -P [passwd] -v SQLCMDFORMAT=ascii \
-W -i sqlserver-health.sql | tee [instancename_health].txt
------------------------------------------------------------------------------*/

select @@version;

-- Sesiones activas y bloqueos
select 
    sys.dm_exec_sessions.session_id as 'SESION ID',
    sys.dm_exec_sessions.login_name as 'USUARIO',
    sys.dm_exec_sessions.program_name as 'APLICACION',
    db_name(sys.dm_exec_requests.database_id) as 'BASE DE DATOS',
    sys.dm_exec_requests.status as 'ESTADO',
    sys.dm_exec_requests.command as 'COMANDO',
    sys.dm_exec_requests.cpu_time as 'CPU (ms)',
    sys.dm_exec_requests.blocking_session_id as 'BLOQUEADO POR',
    sys.dm_exec_requests.wait_type as 'TIPO DE ESPERA'
from sys.dm_exec_sessions
inner join sys.dm_exec_requests on sys.dm_exec_sessions.session_id = sys.dm_exec_requests.session_id
where sys.dm_exec_sessions.is_user_process = 1;

-- Memoria disponible
select 
    total_physical_memory_kb / 1024 as 'MEMORIA TOTAL (MB)',
    available_physical_memory_kb / 1024 as 'MEMORIA DISPONIBLE (MB)'
from sys.dm_os_sys_memory;

-- Estres de CPU reciente
select 
    top 5
    cast(record as xml).value('(./Record/@id)[1]', 'int') as 'REGISTRO ID',
    cast(record as xml).value('(./Record/SchedulerMonitorEvent/SystemHealth/SystemIdle)[1]', 'int') as 'INACTIVIDAD CPU (%)',
    cast(record as xml).value('(./Record/SchedulerMonitorEvent/SystemHealth/ProcessUtilization)[1]', 'int') as 'USO SQL (%)',
    concat(
        (ms_ticks - cast(record as xml).value('(./Record/@time)[1]', 'bigint')) / 1000 / 3600, 'h ',
        ((ms_ticks - cast(record as xml).value('(./Record/@time)[1]', 'bigint')) / 1000 % 3600) / 60, 'm ',
        (ms_ticks - cast(record as xml).value('(./Record/@time)[1]', 'bigint')) / 1000 % 60, 's'
    ) as 'ANTIGUEDAD'
from sys.dm_os_ring_buffers
cross join sys.dm_os_sys_info
where ring_buffer_type = N'RING_BUFFER_SCHEDULER_MONITOR'
    and record like '%<SystemHealth>%';

-- Espacio en disco y volumenes
select 
    distinct
    volume_mount_point as 'VOLUMEN MONTADO',
    total_bytes / 1024 / 1024 / 1024 as 'TOTAL (GB)',
    available_bytes / 1024 / 1024 / 1024 as 'DISPONIBLE (GB)',
    cast((total_bytes - available_bytes) * 100.0 / total_bytes as decimal(5,2))
        as 'PORCENTAJE USADO (%)'
from sys.master_files
cross apply sys.dm_os_volume_stats(database_id, file_id);

/* -----------------------------------------------------------------------------
IMPORTANTE: No olvidar cambiar contexto a DB para analizar fragmentacion
------------------------------------------------------------------------------*/

-- Indicador de porcentaje de fragmentacion sobre la DB actual
select 
    db_name() as 'DATABASE',
    avg(avg_fragmentation_in_percent) as 'FRAGMENTACION PROMEDIO (%)',
    count(*) as 'TOTAL DE INDICES ESCANEADOS'
from sys.dm_db_index_physical_stats(db_id(), null, null, null, 'LIMITED');
