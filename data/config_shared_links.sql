CREATE TABLE IF NOT EXISTS public.config_shared_links (
	api_key varchar(20) NOT NULL,
	id varchar(50) NOT NULL,
	link_name varchar(100) NULL,
	url varchar(255) NULL,
	CONSTRAINT config_shared_links_pk PRIMARY KEY (api_key, id)
);

-- Permissions

ALTER TABLE public.config_shared_links OWNER TO iofmtadm;
GRANT ALL ON TABLE public.config_shared_links TO iofmtadm;