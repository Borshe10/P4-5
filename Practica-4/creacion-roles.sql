-- Revocar privilegios públicos por defecto sobre el esquema public
REVOKE ALL ON DATABASE restaurante_db FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;

-- Creación de los roles funcionales
CREATE ROLE rol_admin_restaurante NOLOGIN;
CREATE ROLE rol_app_restaurante NOLOGIN;
CREATE ROLE rol_consulta_restaurante NOLOGIN;

-- Privilegios para el rol de ADMINISTRACIÓN
GRANT CONNECT, CREATE, TEMPORARY ON DATABASE restaurante_db TO rol_admin_restaurante;
GRANT ALL PRIVILEGES ON SCHEMA public TO rol_admin_restaurante;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO rol_admin_restaurante;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO rol_admin_restaurante;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO rol_admin_restaurante;

-- Privilegios para el rol de APLICACIÓN (Mínimo privilegio operativo)
GRANT CONNECT, TEMPORARY ON DATABASE restaurante_db TO rol_app_restaurante;
GRANT USAGE ON SCHEMA public TO rol_app_restaurante;


GRANT SELECT, INSERT, UPDATE ON EMPLEADO, MESERO, CHEF, PLATILLO, ASIGNACION_CHEF_PLATILLO TO rol_app_restaurante;

-- Clientes y sus teléfonos: alta, consulta, edición y baja de teléfonos secundarios
GRANT SELECT, INSERT, UPDATE ON CLIENTE TO rol_app_restaurante;
GRANT SELECT, INSERT, UPDATE, DELETE ON TELEFONO_CLIENTE TO rol_app_restaurante;

-- Operaciones transaccionales: alta y actualización de pedidos/detalles (sin DELETE histórico)
GRANT SELECT, INSERT, UPDATE ON PEDIDO, DETALLE_PEDIDO TO rol_app_restaurante;

-- Permiso sobre secuencias SERIAL para poder insertar registros y sincronizar secuencias en poblar.py
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO rol_app_restaurante;

-- Privilegios para el rol de CONSULTA (Solo lectura)
GRANT CONNECT ON DATABASE restaurante_db TO rol_consulta_restaurante;
GRANT USAGE ON SCHEMA public TO rol_consulta_restaurante;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO rol_consulta_restaurante;

-- Creación de usuarios con credenciales 
CREATE USER usr_admin_restaurante WITH PASSWORD :'pass_admin' IN ROLE rol_admin_restaurante;
CREATE USER usr_app_restaurante WITH PASSWORD :'pass_app' IN ROLE rol_app_restaurante;
CREATE USER usr_consulta_restaurante WITH PASSWORD :'pass_consulta' IN ROLE rol_consulta_restaurante;