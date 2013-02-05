--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: attachment; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE attachment (
    type text NOT NULL,
    id text NOT NULL,
    filename text NOT NULL,
    size integer,
    "time" bigint,
    description text,
    author text,
    ipnr text
);


ALTER TABLE public.attachment OWNER TO "code.djangoproject";

--
-- Name: auth_cookie; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE auth_cookie (
    cookie text NOT NULL,
    name text NOT NULL,
    ipnr text NOT NULL,
    "time" integer
);


ALTER TABLE public.auth_cookie OWNER TO "code.djangoproject";

--
-- Name: cache; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE cache (
    id integer NOT NULL,
    generation integer,
    key text
);


ALTER TABLE public.cache OWNER TO "code.djangoproject";

--
-- Name: component; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE component (
    name text NOT NULL,
    owner text,
    description text
);


ALTER TABLE public.component OWNER TO "code.djangoproject";

--
-- Name: enum; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE enum (
    type text NOT NULL,
    name text NOT NULL,
    value text
);


ALTER TABLE public.enum OWNER TO "code.djangoproject";

--
-- Name: milestone; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE milestone (
    name text NOT NULL,
    due bigint,
    completed bigint,
    description text
);


ALTER TABLE public.milestone OWNER TO "code.djangoproject";

--
-- Name: node_change; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE node_change (
    repos integer NOT NULL,
    rev text NOT NULL,
    path text NOT NULL,
    node_type text,
    change_type text NOT NULL,
    base_path text,
    base_rev text
);


ALTER TABLE public.node_change OWNER TO "code.djangoproject";

--
-- Name: permission; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE permission (
    username text NOT NULL,
    action text NOT NULL
);


ALTER TABLE public.permission OWNER TO "code.djangoproject";

--
-- Name: report; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE report (
    id integer NOT NULL,
    author text,
    title text,
    query text,
    description text
);


ALTER TABLE public.report OWNER TO "code.djangoproject";

--
-- Name: report_id_seq; Type: SEQUENCE; Schema: public; Owner: code.djangoproject
--

CREATE SEQUENCE report_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.report_id_seq OWNER TO "code.djangoproject";

--
-- Name: report_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: code.djangoproject
--

ALTER SEQUENCE report_id_seq OWNED BY report.id;


--
-- Name: repository; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE repository (
    id integer NOT NULL,
    name text NOT NULL,
    value text
);


ALTER TABLE public.repository OWNER TO "code.djangoproject";

--
-- Name: revision; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE revision (
    repos integer NOT NULL,
    rev text NOT NULL,
    "time" bigint,
    author text,
    message text
);


ALTER TABLE public.revision OWNER TO "code.djangoproject";

--
-- Name: session; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE session (
    sid text NOT NULL,
    authenticated integer NOT NULL,
    last_visit integer
);


ALTER TABLE public.session OWNER TO "code.djangoproject";

--
-- Name: session_attribute; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE session_attribute (
    sid text NOT NULL,
    authenticated integer NOT NULL,
    name text NOT NULL,
    value text
);


ALTER TABLE public.session_attribute OWNER TO "code.djangoproject";

--
-- Name: spamfilter_bayes; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE spamfilter_bayes (
    word text NOT NULL,
    nspam integer,
    nham integer
);


ALTER TABLE public.spamfilter_bayes OWNER TO "code.djangoproject";

--
-- Name: spamfilter_log; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE spamfilter_log (
    id integer NOT NULL,
    "time" integer,
    path text,
    author text,
    authenticated integer,
    ipnr text,
    headers text,
    content text,
    rejected integer,
    karma integer,
    reasons text
);


ALTER TABLE public.spamfilter_log OWNER TO "code.djangoproject";

--
-- Name: spamfilter_log_id_seq; Type: SEQUENCE; Schema: public; Owner: code.djangoproject
--

CREATE SEQUENCE spamfilter_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.spamfilter_log_id_seq OWNER TO "code.djangoproject";

--
-- Name: spamfilter_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: code.djangoproject
--

ALTER SEQUENCE spamfilter_log_id_seq OWNED BY spamfilter_log.id;


--
-- Name: system; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE system (
    name text NOT NULL,
    value text
);


ALTER TABLE public.system OWNER TO "code.djangoproject";

--
-- Name: ticket; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE ticket (
    id integer NOT NULL,
    type text,
    "time" bigint,
    changetime bigint,
    component text,
    severity text,
    priority text,
    owner text,
    reporter text,
    cc text,
    version text,
    milestone text,
    status text,
    resolution text,
    summary text,
    description text,
    keywords text
);


ALTER TABLE public.ticket OWNER TO "code.djangoproject";

--
-- Name: ticket_change; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE ticket_change (
    ticket integer NOT NULL,
    "time" bigint NOT NULL,
    author text,
    field text NOT NULL,
    oldvalue text,
    newvalue text
);


ALTER TABLE public.ticket_change OWNER TO "code.djangoproject";

--
-- Name: ticket_custom; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE ticket_custom (
    ticket integer NOT NULL,
    name text NOT NULL,
    value text
);


ALTER TABLE public.ticket_custom OWNER TO "code.djangoproject";

--
-- Name: ticket_id_seq; Type: SEQUENCE; Schema: public; Owner: code.djangoproject
--

CREATE SEQUENCE ticket_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.ticket_id_seq OWNER TO "code.djangoproject";

--
-- Name: ticket_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: code.djangoproject
--

ALTER SEQUENCE ticket_id_seq OWNED BY ticket.id;


--
-- Name: version; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE version (
    name text NOT NULL,
    "time" bigint,
    description text
);


ALTER TABLE public.version OWNER TO "code.djangoproject";

--
-- Name: watchlist; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE watchlist (
    wluser text NOT NULL,
    realm text NOT NULL,
    resid text NOT NULL,
    lastvisit bigint
);


ALTER TABLE public.watchlist OWNER TO "code.djangoproject";

--
-- Name: watchlist_settings; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE watchlist_settings (
    wluser text NOT NULL,
    name text NOT NULL,
    type text,
    settings text
);


ALTER TABLE public.watchlist_settings OWNER TO "code.djangoproject";

--
-- Name: wiki; Type: TABLE; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE TABLE wiki (
    name text NOT NULL,
    version integer NOT NULL,
    "time" bigint,
    author text,
    ipnr text,
    text text,
    comment text,
    readonly integer
);


ALTER TABLE public.wiki OWNER TO "code.djangoproject";

--
-- Name: id; Type: DEFAULT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE report ALTER COLUMN id SET DEFAULT nextval('report_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE spamfilter_log ALTER COLUMN id SET DEFAULT nextval('spamfilter_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ticket ALTER COLUMN id SET DEFAULT nextval('ticket_id_seq'::regclass);


--
-- Name: attachment_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY attachment
    ADD CONSTRAINT attachment_pk PRIMARY KEY (type, id, filename);


--
-- Name: auth_cookie_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY auth_cookie
    ADD CONSTRAINT auth_cookie_pk PRIMARY KEY (cookie, ipnr, name);


--
-- Name: cache_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY cache
    ADD CONSTRAINT cache_pkey PRIMARY KEY (id);


--
-- Name: component_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY component
    ADD CONSTRAINT component_pkey PRIMARY KEY (name);


--
-- Name: enum_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY enum
    ADD CONSTRAINT enum_pk PRIMARY KEY (type, name);


--
-- Name: milestone_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY milestone
    ADD CONSTRAINT milestone_pkey PRIMARY KEY (name);


--
-- Name: node_change_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY node_change
    ADD CONSTRAINT node_change_pk PRIMARY KEY (repos, rev, path, change_type);


--
-- Name: permission_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY permission
    ADD CONSTRAINT permission_pk PRIMARY KEY (username, action);


--
-- Name: report_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY report
    ADD CONSTRAINT report_pkey PRIMARY KEY (id);


--
-- Name: repository_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY repository
    ADD CONSTRAINT repository_pk PRIMARY KEY (id, name);


--
-- Name: revision_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY revision
    ADD CONSTRAINT revision_pk PRIMARY KEY (repos, rev);


--
-- Name: session_attribute_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY session_attribute
    ADD CONSTRAINT session_attribute_pk PRIMARY KEY (sid, authenticated, name);


--
-- Name: session_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY session
    ADD CONSTRAINT session_pk PRIMARY KEY (sid, authenticated);


--
-- Name: spamfilter_bayes_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY spamfilter_bayes
    ADD CONSTRAINT spamfilter_bayes_pkey PRIMARY KEY (word);


--
-- Name: spamfilter_log_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY spamfilter_log
    ADD CONSTRAINT spamfilter_log_pkey PRIMARY KEY (id);


--
-- Name: ticket_change_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY ticket_change
    ADD CONSTRAINT ticket_change_pk PRIMARY KEY (ticket, "time", field);


--
-- Name: ticket_custom_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY ticket_custom
    ADD CONSTRAINT ticket_custom_pk PRIMARY KEY (ticket, name);


--
-- Name: ticket_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY ticket
    ADD CONSTRAINT ticket_pkey PRIMARY KEY (id);


--
-- Name: version_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY version
    ADD CONSTRAINT version_pkey PRIMARY KEY (name);


--
-- Name: watchlist_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY watchlist
    ADD CONSTRAINT watchlist_pk PRIMARY KEY (wluser, realm, resid);


--
-- Name: watchlist_settings_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY watchlist_settings
    ADD CONSTRAINT watchlist_settings_pk PRIMARY KEY (wluser, name);


--
-- Name: wiki_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject; Tablespace:
--

ALTER TABLE ONLY wiki
    ADD CONSTRAINT wiki_pk PRIMARY KEY (name, version);


--
-- Name: node_change_repos_rev_idx; Type: INDEX; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE INDEX node_change_repos_rev_idx ON node_change USING btree (repos, rev);


--
-- Name: revision_repos_time_idx; Type: INDEX; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE INDEX revision_repos_time_idx ON revision USING btree (repos, "time");


--
-- Name: session_authenticated_idx; Type: INDEX; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE INDEX session_authenticated_idx ON session USING btree (authenticated);


--
-- Name: session_last_visit_idx; Type: INDEX; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE INDEX session_last_visit_idx ON session USING btree (last_visit);


--
-- Name: ticket_change_ticket_idx; Type: INDEX; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE INDEX ticket_change_ticket_idx ON ticket_change USING btree (ticket);


--
-- Name: ticket_change_time_idx; Type: INDEX; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE INDEX ticket_change_time_idx ON ticket_change USING btree ("time");


--
-- Name: ticket_status_idx; Type: INDEX; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE INDEX ticket_status_idx ON ticket USING btree (status);


--
-- Name: ticket_time_idx; Type: INDEX; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE INDEX ticket_time_idx ON ticket USING btree ("time");


--
-- Name: wiki_time_idx; Type: INDEX; Schema: public; Owner: code.djangoproject; Tablespace:
--

CREATE INDEX wiki_time_idx ON wiki USING btree ("time");


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

