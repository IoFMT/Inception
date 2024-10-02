/*

This script creates the `sfg20_data` table in the `public` schema if it does not already exist. 
The table includes the following columns:
- `user_id`: Text, nullable
- `sharelink_id`: Text, nullable
- `schedule_id`: Text, nullable
- `type`: Text, nullable
- `data`: Text, nullable

Additionally, the script sets the owner of the table to `iofmtadm` and grants all permissions on the table to `iofmtadm`.
*/
CREATE TABLE IF NOT EXISTS public.sfg20_data (
	user_id text NULL,
	sharelink_id text NULL,
	schedule_id text NULL,
	"type" text NULL,
	"data" text NULL
);

-- Permissions

ALTER TABLE public.sfg20_data OWNER TO iofmtadm;
GRANT ALL ON TABLE public.sfg20_data TO iofmtadm;