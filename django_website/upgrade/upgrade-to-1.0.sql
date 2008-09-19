begin;
delete from django_admin_log;
delete from comments_freecomment where content_type_id = 13;

INSERT INTO django_comments
    (content_type_id, object_pk, site_id, user_name, user_email, user_url,
    comment, submit_date, ip_address, is_public, is_removed)
SELECT
    content_type_id, object_id, site_id, person_name, '', '', comment,
    submit_date, ip_address, is_public, approved
FROM comments_freecomment;

drop table comments_freecomment;
drop table comments_comment cascade;

commit;