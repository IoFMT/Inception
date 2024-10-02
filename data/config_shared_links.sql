-- This script creates the 'config_shared_links' table in the 'public' schema if it does not already exist.
-- The table stores shared link configurations with the following columns:
-- - api_key: A varchar(20) that serves as part of the primary key.
-- - id: A varchar(50) that serves as part of the primary key.
-- - link_name: A nullable varchar(100) for the name of the link.
-- - url: A nullable varchar(255) for the URL of the link.
-- The primary key is a composite key consisting of 'api_key' and 'id'.
-- Additionally, the script sets the owner of the table to 'iofmtadm' and grants all permissions on the table to 'iofmtadm'.

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