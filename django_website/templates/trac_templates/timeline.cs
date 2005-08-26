<?cs include "header.cs"?>

<div id="ctxtnav" class="nav"></div>

<div id="content" class="timeline">
<h1>Timeline</h1>

<form id="prefs" method="get" action="<?cs var:trac.href.timeline ?>">
 <div>
  <label>View changes from <input type="text" size="10" name="from" value="<?cs
    var:timeline.from ?>" /></label> and
  <label><input type="text" size="3" name="daysback" value="<?cs
    var:timeline.daysback ?>" /> days back</label>.
 </div>
 <fieldset><?cs
  each:filter = timeline.filters ?>
   <label><input type="checkbox" name="<?cs var:filter.name ?>"<?cs
     if:filter.enabled ?> checked="checked"<?cs /if ?> /> <?cs
     var:filter.label ?></label><?cs
  /each ?>
 </fieldset>
 <div class="buttons">
  <input type="submit" name="update" value="Update" />
 </div>
</form><?cs

def:day_separator(date) ?><?cs
 if:date != current_date ?><?cs
  if:current_date ?></dl><?cs /if ?><?cs
  set:current_date = date ?>
  <h2><?cs var:date ?>:</h2><dl><?cs
 /if ?><?cs
/def ?><?cs
each:event = timeline.events ?><?cs
 call:day_separator(event.date) ?><dt class="<?cs
 var:event.kind ?>"><a href="<?cs var:event.href ?>"><span class="time"><?cs
 var:event.time ?></span> <?cs var:event.title ?></a></dt><?cs
  if:event.message ?><dd class="<?cs var:event.kind ?>"><?cs
   var:event.message ?></dd><?cs
  /if ?><?cs
/each ?><?cs
if:len(timeline.events) ?></dl><?cs /if ?>

<div id="help">
 <hr />
 <strong>Note:</strong> See <a href="<?cs var:trac.href.wiki ?>/TracTimeline">TracTimeline</a> 
 for information about the timeline view.
</div>

</div>
<?cs include "footer.cs"?>
