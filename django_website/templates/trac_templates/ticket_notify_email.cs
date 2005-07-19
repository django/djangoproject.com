<?cs var:$email.ticket_body_hdr ?>
<?cs var:$email.ticket_props ?><?cs 
if:$ticket.new ?>
<?cs var:$ticket.description ?>
<?cs else ?><?cs 
 if:$email.changes_body ?>
Changes (by <?cs var:$ticket.change.author ?>):

<?cs var:$email.changes_body ?><?cs
 /if ?><?cs 
var:$email.changes_descr 
?><?cs if:$ticket.change.comment.newvalue ?>
Comment<?cs 
 if:!$email.changes_body ?> (by <?cs 
   var:$ticket.change.comment.author ?>)<?cs /if ?>:

<?cs var:$ticket.change.comment.newvalue ?>
<?cs /if ?><?cs 
/if ?>
-- 
Ticket URL: <<?cs var:$ticket.link ?>>
<?cs var:$project.name ?> <<?cs var:$project.url ?>>
<?cs var:$project.descr ?>