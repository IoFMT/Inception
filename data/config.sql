CREATE TABLE IF NOT EXISTS public.config (
	api_key varchar(20) NOT NULL,
	customer_name varchar(255) NOT NULL,
	access_token varchar(255) NOT NULL,
	shared_links text NULL,
	sfg_environment varchar(20) NULL,
	CONSTRAINT config_pkey PRIMARY KEY (api_key)
);

-- Permissions

ALTER TABLE public.config OWNER TO iofmtadm;
GRANT ALL ON TABLE public.config TO iofmtadm;