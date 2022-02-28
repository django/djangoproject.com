--
-- PostgreSQL database dump
--

-- Dumped from database version 10.20
-- Dumped by pg_dump version 10.20

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner:
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: attachment; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.attachment (
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
-- Name: auth_cookie; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.auth_cookie (
    cookie text NOT NULL,
    name text NOT NULL,
    ipnr text NOT NULL,
    "time" integer
);


ALTER TABLE public.auth_cookie OWNER TO "code.djangoproject";

--
-- Name: cache; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.cache (
    id integer NOT NULL,
    generation integer,
    key text
);


ALTER TABLE public.cache OWNER TO "code.djangoproject";

--
-- Name: component; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.component (
    name text NOT NULL,
    owner text,
    description text
);


ALTER TABLE public.component OWNER TO "code.djangoproject";

--
-- Name: enum; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.enum (
    type text NOT NULL,
    name text NOT NULL,
    value text
);


ALTER TABLE public.enum OWNER TO "code.djangoproject";

--
-- Name: milestone; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.milestone (
    name text NOT NULL,
    due bigint,
    completed bigint,
    description text
);


ALTER TABLE public.milestone OWNER TO "code.djangoproject";

--
-- Name: node_change; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.node_change (
    id integer NOT NULL,
    repos integer,
    rev text,
    path text,
    node_type text,
    change_type text,
    base_path text,
    base_rev text
);


ALTER TABLE public.node_change OWNER TO "code.djangoproject";

--
-- Name: node_change_id_seq; Type: SEQUENCE; Schema: public; Owner: code.djangoproject
--

CREATE SEQUENCE public.node_change_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.node_change_id_seq OWNER TO "code.djangoproject";

--
-- Name: node_change_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: code.djangoproject
--

ALTER SEQUENCE public.node_change_id_seq OWNED BY public.node_change.id;


--
-- Name: notify_subscription; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.notify_subscription (
    id integer NOT NULL,
    "time" bigint,
    changetime bigint,
    class text,
    sid text,
    authenticated integer,
    distributor text,
    format text,
    priority integer,
    adverb text
);


ALTER TABLE public.notify_subscription OWNER TO "code.djangoproject";

--
-- Name: notify_subscription_id_seq; Type: SEQUENCE; Schema: public; Owner: code.djangoproject
--

CREATE SEQUENCE public.notify_subscription_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notify_subscription_id_seq OWNER TO "code.djangoproject";

--
-- Name: notify_subscription_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: code.djangoproject
--

ALTER SEQUENCE public.notify_subscription_id_seq OWNED BY public.notify_subscription.id;


--
-- Name: notify_watch; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.notify_watch (
    id integer NOT NULL,
    sid text,
    authenticated integer,
    class text,
    realm text,
    target text
);


ALTER TABLE public.notify_watch OWNER TO "code.djangoproject";

--
-- Name: notify_watch_id_seq; Type: SEQUENCE; Schema: public; Owner: code.djangoproject
--

CREATE SEQUENCE public.notify_watch_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notify_watch_id_seq OWNER TO "code.djangoproject";

--
-- Name: notify_watch_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: code.djangoproject
--

ALTER SEQUENCE public.notify_watch_id_seq OWNED BY public.notify_watch.id;


--
-- Name: permission; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.permission (
    username text NOT NULL,
    action text NOT NULL
);


ALTER TABLE public.permission OWNER TO "code.djangoproject";

--
-- Name: report; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.report (
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

CREATE SEQUENCE public.report_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.report_id_seq OWNER TO "code.djangoproject";

--
-- Name: report_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: code.djangoproject
--

ALTER SEQUENCE public.report_id_seq OWNED BY public.report.id;


--
-- Name: repository; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.repository (
    id integer NOT NULL,
    name text NOT NULL,
    value text
);


ALTER TABLE public.repository OWNER TO "code.djangoproject";

--
-- Name: revision; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.revision (
    repos integer NOT NULL,
    rev text NOT NULL,
    "time" bigint,
    author text,
    message text
);


ALTER TABLE public.revision OWNER TO "code.djangoproject";

--
-- Name: session; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.session (
    sid text NOT NULL,
    authenticated integer NOT NULL,
    last_visit integer
);


ALTER TABLE public.session OWNER TO "code.djangoproject";

--
-- Name: session_attribute; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.session_attribute (
    sid text NOT NULL,
    authenticated integer NOT NULL,
    name text NOT NULL,
    value text
);


ALTER TABLE public.session_attribute OWNER TO "code.djangoproject";

--
-- Name: spamfilter_bayes; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.spamfilter_bayes (
    word text NOT NULL,
    nspam integer,
    nham integer
);


ALTER TABLE public.spamfilter_bayes OWNER TO "code.djangoproject";

--
-- Name: spamfilter_log; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.spamfilter_log (
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
    reasons text,
    request text
);


ALTER TABLE public.spamfilter_log OWNER TO "code.djangoproject";

--
-- Name: spamfilter_log_id_seq; Type: SEQUENCE; Schema: public; Owner: code.djangoproject
--

CREATE SEQUENCE public.spamfilter_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.spamfilter_log_id_seq OWNER TO "code.djangoproject";

--
-- Name: spamfilter_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: code.djangoproject
--

ALTER SEQUENCE public.spamfilter_log_id_seq OWNED BY public.spamfilter_log.id;


--
-- Name: spamfilter_report; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.spamfilter_report (
    id integer NOT NULL,
    entry text,
    headers text,
    author text,
    authenticated integer,
    comment text,
    "time" integer
);


ALTER TABLE public.spamfilter_report OWNER TO "code.djangoproject";

--
-- Name: spamfilter_report_id_seq; Type: SEQUENCE; Schema: public; Owner: code.djangoproject
--

CREATE SEQUENCE public.spamfilter_report_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.spamfilter_report_id_seq OWNER TO "code.djangoproject";

--
-- Name: spamfilter_report_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: code.djangoproject
--

ALTER SEQUENCE public.spamfilter_report_id_seq OWNED BY public.spamfilter_report.id;


--
-- Name: spamfilter_statistics; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.spamfilter_statistics (
    strategy text NOT NULL,
    action text NOT NULL,
    data text NOT NULL,
    status text NOT NULL,
    delay double precision,
    delay_max double precision,
    delay_min double precision,
    count integer,
    external integer,
    "time" integer
);


ALTER TABLE public.spamfilter_statistics OWNER TO "code.djangoproject";

--
-- Name: system; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.system (
    name text NOT NULL,
    value text
);


ALTER TABLE public.system OWNER TO "code.djangoproject";

--
-- Name: ticket; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.ticket (
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
-- Name: ticket_change; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.ticket_change (
    ticket integer NOT NULL,
    "time" bigint NOT NULL,
    author text,
    field text NOT NULL,
    oldvalue text,
    newvalue text
);


ALTER TABLE public.ticket_change OWNER TO "code.djangoproject";

--
-- Name: ticket_custom; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.ticket_custom (
    ticket integer NOT NULL,
    name text NOT NULL,
    value text
);


ALTER TABLE public.ticket_custom OWNER TO "code.djangoproject";

--
-- Name: ticket_id_seq; Type: SEQUENCE; Schema: public; Owner: code.djangoproject
--

CREATE SEQUENCE public.ticket_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ticket_id_seq OWNER TO "code.djangoproject";

--
-- Name: ticket_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: code.djangoproject
--

ALTER SEQUENCE public.ticket_id_seq OWNED BY public.ticket.id;


--
-- Name: version; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.version (
    name text NOT NULL,
    "time" bigint,
    description text
);


ALTER TABLE public.version OWNER TO "code.djangoproject";

--
-- Name: watchlist; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.watchlist (
    wluser text NOT NULL,
    realm text NOT NULL,
    resid text NOT NULL,
    lastvisit bigint
);


ALTER TABLE public.watchlist OWNER TO "code.djangoproject";

--
-- Name: watchlist_settings; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.watchlist_settings (
    wluser text NOT NULL,
    name text NOT NULL,
    type text,
    settings text
);


ALTER TABLE public.watchlist_settings OWNER TO "code.djangoproject";

--
-- Name: wiki; Type: TABLE; Schema: public; Owner: code.djangoproject
--

CREATE TABLE public.wiki (
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
-- Name: node_change id; Type: DEFAULT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.node_change ALTER COLUMN id SET DEFAULT nextval('public.node_change_id_seq'::regclass);


--
-- Name: notify_subscription id; Type: DEFAULT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.notify_subscription ALTER COLUMN id SET DEFAULT nextval('public.notify_subscription_id_seq'::regclass);


--
-- Name: notify_watch id; Type: DEFAULT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.notify_watch ALTER COLUMN id SET DEFAULT nextval('public.notify_watch_id_seq'::regclass);


--
-- Name: report id; Type: DEFAULT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.report ALTER COLUMN id SET DEFAULT nextval('public.report_id_seq'::regclass);


--
-- Name: spamfilter_log id; Type: DEFAULT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.spamfilter_log ALTER COLUMN id SET DEFAULT nextval('public.spamfilter_log_id_seq'::regclass);


--
-- Name: spamfilter_report id; Type: DEFAULT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.spamfilter_report ALTER COLUMN id SET DEFAULT nextval('public.spamfilter_report_id_seq'::regclass);


--
-- Name: ticket id; Type: DEFAULT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.ticket ALTER COLUMN id SET DEFAULT nextval('public.ticket_id_seq'::regclass);


--
-- Data for Name: attachment; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: auth_cookie; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: cache; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: component; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: enum; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: milestone; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: node_change; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: notify_subscription; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: notify_watch; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: permission; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: report; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: repository; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: revision; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: session; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: session_attribute; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: spamfilter_bayes; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: spamfilter_log; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: spamfilter_report; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: spamfilter_statistics; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: system; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--

INSERT INTO public.system (name, value) VALUES ('database_version', '41');
INSERT INTO public.system (name, value) VALUES ('spamfilter_version', '4');


--
-- Data for Name: ticket; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: ticket_change; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: ticket_custom; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: version; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: watchlist; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: watchlist_settings; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Data for Name: wiki; Type: TABLE DATA; Schema: public; Owner: code.djangoproject
--



--
-- Name: node_change_id_seq; Type: SEQUENCE SET; Schema: public; Owner: code.djangoproject
--

SELECT pg_catalog.setval('public.node_change_id_seq', 1, false);


--
-- Name: notify_subscription_id_seq; Type: SEQUENCE SET; Schema: public; Owner: code.djangoproject
--

SELECT pg_catalog.setval('public.notify_subscription_id_seq', 1, false);


--
-- Name: notify_watch_id_seq; Type: SEQUENCE SET; Schema: public; Owner: code.djangoproject
--

SELECT pg_catalog.setval('public.notify_watch_id_seq', 1, false);


--
-- Name: report_id_seq; Type: SEQUENCE SET; Schema: public; Owner: code.djangoproject
--

SELECT pg_catalog.setval('public.report_id_seq', 1, false);


--
-- Name: spamfilter_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: code.djangoproject
--

SELECT pg_catalog.setval('public.spamfilter_log_id_seq', 1, false);


--
-- Name: spamfilter_report_id_seq; Type: SEQUENCE SET; Schema: public; Owner: code.djangoproject
--

SELECT pg_catalog.setval('public.spamfilter_report_id_seq', 1, false);


--
-- Name: ticket_id_seq; Type: SEQUENCE SET; Schema: public; Owner: code.djangoproject
--

SELECT pg_catalog.setval('public.ticket_id_seq', 1, false);


--
-- Name: attachment attachment_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.attachment
    ADD CONSTRAINT attachment_pk PRIMARY KEY (type, id, filename);


--
-- Name: auth_cookie auth_cookie_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.auth_cookie
    ADD CONSTRAINT auth_cookie_pk PRIMARY KEY (cookie, ipnr, name);


--
-- Name: cache cache_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.cache
    ADD CONSTRAINT cache_pkey PRIMARY KEY (id);


--
-- Name: component component_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.component
    ADD CONSTRAINT component_pkey PRIMARY KEY (name);


--
-- Name: enum enum_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.enum
    ADD CONSTRAINT enum_pk PRIMARY KEY (type, name);


--
-- Name: milestone milestone_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.milestone
    ADD CONSTRAINT milestone_pkey PRIMARY KEY (name);


--
-- Name: node_change node_change_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.node_change
    ADD CONSTRAINT node_change_pkey PRIMARY KEY (id);


--
-- Name: notify_subscription notify_subscription_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.notify_subscription
    ADD CONSTRAINT notify_subscription_pkey PRIMARY KEY (id);


--
-- Name: notify_watch notify_watch_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.notify_watch
    ADD CONSTRAINT notify_watch_pkey PRIMARY KEY (id);


--
-- Name: permission permission_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT permission_pk PRIMARY KEY (username, action);


--
-- Name: report report_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.report
    ADD CONSTRAINT report_pkey PRIMARY KEY (id);


--
-- Name: repository repository_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.repository
    ADD CONSTRAINT repository_pk PRIMARY KEY (id, name);


--
-- Name: revision revision_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.revision
    ADD CONSTRAINT revision_pk PRIMARY KEY (repos, rev);


--
-- Name: session_attribute session_attribute_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.session_attribute
    ADD CONSTRAINT session_attribute_pk PRIMARY KEY (sid, authenticated, name);


--
-- Name: session session_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.session
    ADD CONSTRAINT session_pk PRIMARY KEY (sid, authenticated);


--
-- Name: spamfilter_bayes spamfilter_bayes_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.spamfilter_bayes
    ADD CONSTRAINT spamfilter_bayes_pkey PRIMARY KEY (word);


--
-- Name: spamfilter_log spamfilter_log_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.spamfilter_log
    ADD CONSTRAINT spamfilter_log_pkey PRIMARY KEY (id);


--
-- Name: spamfilter_report spamfilter_report_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.spamfilter_report
    ADD CONSTRAINT spamfilter_report_pkey PRIMARY KEY (id);


--
-- Name: spamfilter_statistics spamfilter_statistics_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.spamfilter_statistics
    ADD CONSTRAINT spamfilter_statistics_pk PRIMARY KEY (strategy, action, data, status);


--
-- Name: ticket_change ticket_change_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.ticket_change
    ADD CONSTRAINT ticket_change_pk PRIMARY KEY (ticket, "time", field);


--
-- Name: ticket_custom ticket_custom_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.ticket_custom
    ADD CONSTRAINT ticket_custom_pk PRIMARY KEY (ticket, name);


--
-- Name: ticket ticket_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.ticket
    ADD CONSTRAINT ticket_pkey PRIMARY KEY (id);


--
-- Name: version version_pkey; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.version
    ADD CONSTRAINT version_pkey PRIMARY KEY (name);


--
-- Name: watchlist watchlist_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.watchlist
    ADD CONSTRAINT watchlist_pk PRIMARY KEY (wluser, realm, resid);


--
-- Name: watchlist_settings watchlist_settings_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.watchlist_settings
    ADD CONSTRAINT watchlist_settings_pk PRIMARY KEY (wluser, name);


--
-- Name: wiki wiki_pk; Type: CONSTRAINT; Schema: public; Owner: code.djangoproject
--

ALTER TABLE ONLY public.wiki
    ADD CONSTRAINT wiki_pk PRIMARY KEY (name, version);


--
-- Name: node_change_repos_path_rev_idx; Type: INDEX; Schema: public; Owner: code.djangoproject
--

CREATE INDEX node_change_repos_path_rev_idx ON public.node_change USING btree (repos, path, rev);


--
-- Name: node_change_repos_rev_path_idx; Type: INDEX; Schema: public; Owner: code.djangoproject
--

CREATE INDEX node_change_repos_rev_path_idx ON public.node_change USING btree (repos, rev, path);


--
-- Name: notify_subscription_class_idx; Type: INDEX; Schema: public; Owner: code.djangoproject
--

CREATE INDEX notify_subscription_class_idx ON public.notify_subscription USING btree (class);


--
-- Name: notify_subscription_sid_authenticated_idx; Type: INDEX; Schema: public; Owner: code.djangoproject
--

CREATE INDEX notify_subscription_sid_authenticated_idx ON public.notify_subscription USING btree (sid, authenticated);


--
-- Name: notify_watch_class_realm_target_idx; Type: INDEX; Schema: public; Owner: code.djangoproject
--

CREATE INDEX notify_watch_class_realm_target_idx ON public.notify_watch USING btree (class, realm, target);


--
-- Name: notify_watch_sid_authenticated_class_idx; Type: INDEX; Schema: public; Owner: code.djangoproject
--

CREATE INDEX notify_watch_sid_authenticated_class_idx ON public.notify_watch USING btree (sid, authenticated, class);


--
-- Name: revision_repos_time_idx; Type: INDEX; Schema: public; Owner: code.djangoproject
--

CREATE INDEX revision_repos_time_idx ON public.revision USING btree (repos, "time");


--
-- Name: session_authenticated_idx; Type: INDEX; Schema: public; Owner: code.djangoproject
--

CREATE INDEX session_authenticated_idx ON public.session USING btree (authenticated);


--
-- Name: session_last_visit_idx; Type: INDEX; Schema: public; Owner: code.djangoproject
--

CREATE INDEX session_last_visit_idx ON public.session USING btree (last_visit);


--
-- Name: ticket_change_ticket_idx; Type: INDEX; Schema: public; Owner: code.djangoproject
--

CREATE INDEX ticket_change_ticket_idx ON public.ticket_change USING btree (ticket);


--
-- Name: ticket_change_time_idx; Type: INDEX; Schema: public; Owner: code.djangoproject
--

CREATE INDEX ticket_change_time_idx ON public.ticket_change USING btree ("time");


--
-- Name: ticket_status_idx; Type: INDEX; Schema: public; Owner: code.djangoproject
--

CREATE INDEX ticket_status_idx ON public.ticket USING btree (status);


--
-- Name: ticket_time_idx; Type: INDEX; Schema: public; Owner: code.djangoproject
--

CREATE INDEX ticket_time_idx ON public.ticket USING btree ("time");


--
-- Name: wiki_time_idx; Type: INDEX; Schema: public; Owner: code.djangoproject
--

CREATE INDEX wiki_time_idx ON public.wiki USING btree ("time");


--
-- PostgreSQL database dump complete
--

