BEGIN;
INSERT INTO aggregator_feedtype (name, slug, can_self_add) 
    VALUES ('Blog feed', 'feed', true);
ALTER TABLE aggregator_feeds 
    ADD COLUMN feed_type_id INTEGER NULL 
    REFERENCES aggregator_feedtype (id) DEFERRABLE INITIALLY DEFERRED;
UPDATE aggregator_feeds 
    SET feed_type_id = (SELECT id FROM aggregator_feedtype WHERE slug = 'feed');
COMMIT;

-- Can't alter the column in the same transaction as inserting data pointing to it.

BEGIN;
ALTER TABLE aggregator_feeds ALTER COLUMN feed_type_id SET NOT NULL;
COMMIT;

