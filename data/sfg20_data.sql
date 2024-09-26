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