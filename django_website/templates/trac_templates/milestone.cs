<?cs set:html.stylesheet = 'css/roadmap.css' ?>
<?cs include:"header.cs"?>
<?cs include:"macros.cs"?>

<div id="ctxtnav" class="nav">
 <ul>
  <?cs if:milestone.href.edit ?><li class="first"><a href="<?cs
    var:milestone.href.edit ?>">Edit Milestone Info</a></li><?cs /if ?>
  <?cs if:milestone.href.delete ?><li class="last"><a href="<?cs
    var:milestone.href.delete ?>">Delete Milestone</a></li><?cs /if ?>
 </ul>
</div>

<div id="content" class="milestone">
 <?cs if:milestone.mode == "new" ?>
 <h1>New Milestone</h1>
 <?cs elif:milestone.mode == "edit" ?>
 <h1>Edit Milestone <?cs var:milestone.name ?></h1>
 <?cs elif:milestone.mode == "delete" ?>
 <h1>Delete Milestone <?cs var:milestone.name ?></h1>
 <?cs else ?>
 <h1>Milestone <?cs var:milestone.name ?></h1>
 <form action="#stats" id="prefs" method="get">
  <div>
   <label for="by">View status by</label>
   <select id="by" name="by"><?cs each:group = milestone.stats.available_groups ?>
    <option<?cs
      if:milestone.stats.grouped_by == group?> selected="selected"<?cs
      /if ?>><?cs var:group ?></option>
   <?cs /each ?></select>
   <div>
    <input name="showempty" id="showempty" type="checkbox"<?cs
       if:milestone.stats.show_empty ?> checked="checked"<?cs /if ?>>
    <label for="showempty">Show groups with no assigned tickets</label>
   </div>
   <div class="buttons">
    <input type="submit" value="Update" />
   </div>
  </div>
 </form>
 <?cs /if ?>

 <?cs if:milestone.mode == "edit" || milestone.mode == "new" ?>
  <script type="text/javascript">
    addEvent(window, 'load', function() {
      document.getElementById('name').focus() }
    );
  </script>
  <form id="edit" action="<?cs var:cgi_location ?>" method="post">
   <input type="hidden" name="mode" value="milestone" />
   <input type="hidden" name="id" value="<?cs var:milestone.name ?>" />
   <input type="hidden" name="action" value="commit_changes" />
   <div class="field">
    <label for="name">Name of the milestone:</label><br />
    <input type="text" id="name" name="name" size="32" value="<?cs
      var:milestone.name ?>" />
   </div>
   <div class="field">
    <label for="datemode">Completion date:</label><br />
    <select name="datemode" id="datemode"
        onchange="enableControl('date',this.value=='manual');
                  if (this.value=='manual') document.getElementById('date').focus();">
     <option value="manual">Set manually</option>
     <option value="now">Mark as completed now</option>
    </select>
    <input type="text" id="date" name="date" size="8" value="<?cs
      var:milestone.date ?>" title="Format: <?cs var:milestone.date_hint ?>" />
    <label for="date"><em>Format: <?cs var:milestone.date_hint ?></em></label>
   </div>
   <div class="field">
    <fieldset class="iefix">
     <label for="descr">Description (you may use <a tabindex="42" href="<?cs
       var:trac.href.wiki ?>/WikiFormatting">WikiFormatting</a> here):</label>
     <p><textarea id="descr" name="descr" rows="12" cols="80"><?cs
       var:milestone.descr_source ?></textarea></p>
     <?cs call:wiki_toolbar('descr') ?>
    </fieldset>
   </div>
   <div class="buttons">
    <?cs if:milestone.mode == "new"
     ?><input type="submit" name="save" value="Add Milestone" /><?cs
    else
     ?><input type="submit" name="save" value="Save Changes" /><?cs
    /if ?>
    <input type="submit" name="cancel" value="Cancel" />
   </div>
  </form>
 <?cs elif:milestone.mode == "delete" ?>
  <form action="<?cs var:cgi_location ?>" method="post">
   <input type="hidden" name="mode" value="milestone" />
   <input type="hidden" name="id" value="<?cs var:milestone.name ?>" />
   <input type="hidden" name="action" value="confirm_delete" />
   <p><strong>Are you sure you want to delete this milestone?</strong></p>
   <input type="checkbox" id="retarget" name="retarget" checked="checked"
       onclick="enableControl('target', this.checked)"/>
   <label for="target">Retarget associated tickets to milestone</label>
   <select name="target" id="target">
    <option value="">None</option><?cs
     each:other = milestones ?><?cs if:other != milestone.name ?>
      <option><?cs var:other ?></option><?cs 
     /if ?><?cs /each ?>
   </select>
   <div class="buttons">
    <input type="submit" name="cancel" value="Cancel" />
    <input type="submit" name="delete" value="Delete Milestone" />
   </div>
  </form>
 <?cs else ?>
  <em class="date"><?cs if:milestone.date ?>
   <?cs var:milestone.date ?><?cs else ?>No date set<?cs /if ?>
  </em>
  <div class="descr"><?cs var:milestone.descr ?></div>
 <?cs /if ?>

 <?cs if:milestone.mode == "view" ?>
 <h2 class="stats">Status by <?cs var:milestone.stats.grouped_by ?></h2>
 <table class="listing" id="stats"
   summary="Shows the milestone completion status grouped by <?cs
     var:milestone.stats.grouped_by ?>">
  <thead><tr>
   <th class="name" rowspan="2"><?cs var:milestone.stats.grouped_by ?></th>
   <th class="tickets" scope="col" colspan="2">Tickets</th>
   <th class="progress" rowspan="2">Percent Resolved</th>
  </tr><tr>
   <th class="open" scope="col">Active</th>
   <th class="closed" scope="col">Closed</th>
  </tr></thead>
  <?cs if:len(milestone.stats.groups) ?><tbody>
   <?cs each:group = milestone.stats.groups ?>
    <tr class="<?cs if:name(group) % 2 ?>odd<?cs else ?>even<?cs /if ?>">
     <th class="name" scope="row"><a href="<?cs
       var:group.queries.all_tickets ?>"><?cs var:group.name ?></a></th>
     <td class="open tickets"><a href="<?cs
       var:group.queries.active_tickets ?>"><?cs
       var:group.active_tickets ?></a></td>
     <td class="closed tickets"><a href="<?cs
       var:group.queries.closed_tickets ?>"><?cs
       var:group.closed_tickets ?></a></td>
     <td class="progress">
      <?cs if:#group.total_tickets ?>
       <div class="progress" style="width: <?cs
         var:#group.percent_total * #80 / #100 ?>%"><div style="width: <?cs
         var:#group.percent_complete ?>%"></div>
       </div>
       <p class="percent"><?cs var:#group.percent_complete ?>%</p>
      <?cs /if ?>
     </td>
    </tr>
   <?cs /each ?>
  </tbody><?cs /if ?>
  <tbody class="totals"><tr>
   <th class="name" scope="row"><a href="<?cs
     var:milestone.queries.all_tickets ?>">Total</a></th>
   <td class="open tickets"><a href="<?cs
     var:milestone.queries.active_tickets ?>"><?cs
     var:milestone.stats.active_tickets ?></a></td>
   <td class="closed tickets"><a href="<?cs
     var:milestone.queries.closed_tickets ?>"><?cs
     var:milestone.stats.closed_tickets ?></a></td>
   <td class="progress">
    <?cs if:#milestone.stats.total_tickets ?>
     <div class="progress" style="width: 80%">
      <div style="width: <?cs var:#milestone.stats.percent_complete ?>%"></div>
     </div>
     <p class="percent"><?cs var:#milestone.stats.percent_complete ?>%</p>
    <?cs /if ?>
   </td>
  </tr></tbody>
 </table><?cs /if ?>

 <div id="help">
  <strong>Note:</strong> See <a href="<?cs
    var:trac.href.wiki ?>/TracRoadmap">TracRoadmap</a> for help on using the roadmap.
 </div>

</div>
<?cs include:"footer.cs"?>
