-- Upgrade the DB from the version running on the old
-- djangoproject server to this new community version.

BEGIN;

-- If we don't do this then we can't do the final SET NOT NULL
-- step below in the same transaction.

SET CONSTRAINTS ALL IMMEDIATE;

-- Create the feed type table.
-- Same as running syncdb, but a little more visible.

CREATE TABLE "aggregator_feedtype" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(250) NOT NULL,
    "slug" varchar(250) NOT NULL,
    "can_self_add" boolean NOT NULL
);

-- Create the "blog post" feed type for the old entries in the DB.
-- This'll get smooshed by the fixture (community_seed.json),
-- but we need it here to move old data over cleanly.

INSERT INTO aggregator_feedtype (id, name, slug, can_self_add)
     VALUES (2, 'Community Blog Posts', 'community-blog-posts', 't');

-- Add the feed_type_id column to aggregator_feeds and update it
-- to point to the new feed type.

ALTER TABLE aggregator_feeds ADD COLUMN feed_type_id integer 
    REFERENCES aggregator_feedtype (id) DEFERRABLE INITIALLY DEFERRED;
UPDATE aggregator_feeds SET feed_type_id = 2;
ALTER TABLE aggregator_feeds ALTER COLUMN feed_type_id SET NOT NULL;

COMMIT;