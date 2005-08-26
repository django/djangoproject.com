<?cs include:"header.cs" ?>
<?cs include:"macros.cs" ?>

<div id="ctxtnav" class="nav"><?cs
 if:query.report_href ?><ul>
  <li class="first"><a href="<?cs
    var:query.report_href ?>">Available Reports</a></li>
  <li class="last">Custom Query</li></ul><?cs
 /if ?>
</div>

<div id="content" class="query">
 <h1><?cs var:title ?> <span class="numrows">(<?cs alt:len(query.results) ?>No<?cs /alt ?> match<?cs
 if:len(query.results) != 1 ?>es<?cs /if ?>)</span></h1>

<form id="query" method="post" action="<?cs var:trac.href.query ?>">
 <fieldset id="filters">
  <legend>Filters</legend>
  <?cs def:checkbox_checked(constraint, option) ?><?cs
   each:value = constraint.values ?><?cs
    if:value == option ?> checked="checked"<?cs
    /if ?><?cs
   /each ?><?cs
  /def ?><?cs
  def:option_selected(constraint, option) ?><?cs
   each:value = constraint.values ?><?cs
    if:value == option ?> selected="selected"<?cs
    /if ?><?cs
   /each ?><?cs
  /def ?>
  <table summary="Query filters"><?cs each:field = query.fields ?><?cs
   each:constraint = query.constraints ?><?cs
    if:name(field) == name(constraint) ?>
     <tbody><tr class="<?cs var:name(field) ?>">
      <th scope="row"><label><?cs var:field.label ?></label></th><?cs
      if:field.type != "radio" ?>
       <td class="mode">
        <select name="<?cs var:name(field) ?>_mode"><?cs
         each:mode = query.modes[field.type] ?>
          <option value="<?cs var:mode.value ?>"<?cs
           if:mode.value == constraint.mode ?> selected="selected"<?cs
           /if ?>><?cs var:mode.name ?></option><?cs
         /each ?>
        </select>
       </td><?cs
      /if ?>
      <td class="filter"<?cs if:field.type == "radio" ?> colspan="2"<?cs /if ?>><?cs
       if:field.type == "select" ?><?cs
        each:value = constraint.values ?>
         <select name="<?cs var:name(constraint) ?>"><option></option><?cs
         each:option = field.options ?>
          <option<?cs if:option == value ?> selected="selected"<?cs /if ?>><?cs
            var:option ?></option><?cs
         /each ?></select><?cs
         if:name(value) != len(constraint.values) - 1 ?>
          </td>
          <td class="actions"><input type="submit" name="rm_filter_<?cs
             var:name(field) ?>_<?cs var:name(value) ?>" value="-" /></td>
         </tr><tr class="<?cs var:name(field) ?>">
          <th colspan="2"><label>or</label></th>
          <td class="filter"><?cs
         /if ?><?cs
        /each ?><?cs
       elif:field.type == "radio" ?><?cs
        each:option = field.options ?>
         <input type="checkbox" id="<?cs var:name(field) ?>_<?cs
           var:option ?>" name="<?cs var:name(field) ?>" value="<?cs
           var:option ?>"<?cs call:checkbox_checked(constraint, option) ?> />
         <label for="<?cs var:name(field) ?>_<?cs var:option ?>"><?cs
           alt:option ?>none<?cs /alt ?></label><?cs
        /each ?><?cs
       elif:field.type == "text" ?><?cs
        each:value = constraint.values ?>
        <input type="text" name="<?cs var:name(field) ?>" value="<?cs
          var:value ?>" size="42" /><?cs
         if:name(value) != len(constraint.values) - 1 ?>
          </td>
          <td class="actions"><input type="submit" name="rm_filter_<?cs
             var:name(field) ?>_<?cs var:name(value) ?>" value="-" /></td>
         </tr><tr class="<?cs var:name(field) ?>">
          <th colspan="2"><label>or</label></th>
          <td class="filter"><?cs
         /if ?><?cs
        /each ?><?cs
       /if ?>
      </td>
      <td class="actions"><input type="submit" name="rm_filter_<?cs
         var:name(field) ?><?cs
         if:field.type != 'radio' ?>_<?cs
          var:len(constraint.values) - 1 ?><?cs
         /if ?>" value="-" /></td>
     </tr></tbody><?cs /if ?><?cs
    /each ?><?cs
   /each ?>
   <tbody><tr class="actions">
    <td class="actions" colspan="4" style="text-align: right">
     <label for="add_filter">Add filter</label>&nbsp;
     <select name="add_filter" id="add_filter">
      <option></option><?cs
      each:field = query.fields ?>
       <option value="<?cs var:name(field) ?>"<?cs
         if:field.type == "radio" ?><?cs
          if:len(query.constraints[name(field)]) != 0 ?> disabled="disabled"<?cs
          /if ?><?cs
         /if ?>><?cs var:field.label ?></option><?cs
      /each ?>	
     </select>
     <input type="submit" name="add" value="+" />
    </td>
   </tr></tbody>
  </table>
 </fieldset>
 <p class="option">
  <label for="group">Group results by</label>
  <select name="group" id="group">
   <option></option><?cs
   each:field = query.fields ?><?cs
    if:field.type == 'select' || field.type == 'radio' ||
       name(field) == 'owner' ?>
     <option value="<?cs var:name(field) ?>"<?cs
       if:name(field) == query.group ?> selected="selected"<?cs /if ?>><?cs
       var:field.label ?></option><?cs
    /if ?><?cs
   /each ?>
  </select>
  <input type="checkbox" name="groupdesc" id="groupdesc"<?cs
    if:query.groupdesc ?> checked="checked"<?cs /if ?> />
  <label for="groupdesc">descending</label>
  <script type="text/javascript">
    var group = document.getElementById("group");
    var updateGroupDesc = function() {
      enableControl('groupdesc', group.selectedIndex > 0);
    }
    addEvent(window, 'load', updateGroupDesc);
    addEvent(group, 'change', updateGroupDesc);
  </script>
 </p>
 <p class="option">
  <input type="checkbox" name="verbose" id="verbose"<?cs
    if:query.verbose ?> checked="checked"<?cs /if ?> />
  <label for="verbose">Show full description under each result</label>
 </p>
 <div class="buttons">
  <input type="hidden" name="order" value="<?cs var:query.order ?>" />
  <?cs if:query.desc ?><input type="hidden" name="desc" value="1" /><?cs /if ?>
  <input type="submit" name="update" value="Update" />
 </div>
 <hr />
</form>
<script type="text/javascript" src="<?cs
  var:htdocs_location ?>js/query.js"></script>
<script type="text/javascript"><?cs set:idx = 0 ?>
 var properties={<?cs each:field = query.fields ?><?cs
  var:name(field) ?>:{type:"<?cs var:field.type ?>",label:"<?cs
  var:field.label ?>",options:[<?cs
   each:option = field.options ?>"<?cs var:option ?>"<?cs
    if:name(option) < len(field.options) -1 ?>,<?cs /if ?><?cs
   /each ?>]}<?cs
  set:idx = idx + 1 ?><?cs if:idx < len(query.fields) ?>,<?cs /if ?><?cs
 /each ?>};<?cs set:idx = 0 ?>
 var modes = {<?cs each:type = query.modes ?><?cs var:name(type) ?>:[<?cs
  each:mode = type ?>{text:"<?cs var:mode.name ?>",value:"<?cs var:mode.value ?>"}<?cs
   if:name(mode) < len(type) -1 ?>,<?cs /if ?><?cs
  /each ?>]<?cs
  set:idx = idx + 1 ?><?cs if:idx < len(query.modes) ?>,<?cs /if ?><?cs
 /each ?>};
 initializeFilters();
</script>

<?cs def:thead() ?>
 <thead><tr><?cs each:header = query.headers ?><?cs
  if:name(header) == 0 ?><?cs
   call:sortable_th(query.order, query.desc, 'id', 'ticket', query.href) ?><?cs
  else ?><?cs
   call:sortable_th(query.order, query.desc, header.name, header.name, query.href) ?><?cs
  /if ?>
 <?cs /each ?></tr></thead>
<?cs /def ?>

<?cs if:len(query.results) ?><?cs
 if:!query.group ?>
  <table class="listing tickets">
  <?cs call:thead() ?><tbody><?cs
 /if ?><?cs
 each:result = query.results ?><?cs
  if:result[query.group] != prev_group ?>
   <?cs if:prev_group ?></tbody></table><?cs /if ?>
   <h2><?cs
    each:field = query.fields ?><?cs
     if:name(field) == query.group ?><?cs
      var:field.label ?><?cs
     /if ?><?cs
    /each ?>: <?cs var:result[query.group] ?></h2>
   <table class="listing tickets">
   <?cs call:thead() ?><tbody><?cs
  /if ?>
  <tr class="<?cs
   if:name(result) % 2 ?>odd<?cs else ?>even<?cs /if ?> prio<?cs
   var:result.priority_value ?><?cs
   if:result.added ?> added<?cs /if ?><?cs
   if:result.changed ?> changed<?cs /if ?><?cs
   if:result.removed ?> removed<?cs /if ?>"><?cs
  each:header = query.headers ?><?cs
   if:name(header) == 0 ?><td class="id"><a href="<?cs
    var:result.href ?>" title="View ticket"><?cs var:result.id ?></a></td><?cs
   else ?><td class="<?cs var:header.name ?>"><?cs
     if:header.name == 'summary' ?><a href="<?cs
      var:result.href ?>" title="View ticket"><?cs
      var:result.summary ?></a><?cs
     else ?><span><?cs var:result[header.name] ?></span><?cs
     /if ?></td><?cs
   /if ?><?cs
  /each ?>
  <?cs if:query.verbose ?>
   </tr><tr class="fullrow"><td colspan="<?cs var:len(query.headers) ?>">
    <p class="meta">Reported by <strong><?cs var:result.reporter ?></strong>,
    <?cs var:result.time ?><?cs if:result.description ?>:<?cs /if ?></p>
    <?cs if:result.description ?><p><?cs var:result.description ?></p><?cs /if ?>
   </td>
  <?cs /if ?><?cs set:prev_group = result[query.group] ?>
 </tr><?cs /each ?>
</tbody></table><?cs
/if ?>

<div id="help">
 <strong>Note:</strong> See <a href="<?cs var:$trac.href.wiki ?>/TracQuery">TracQuery</a> 
 for help on using queries.
</div>

</div>
<?cs include:"footer.cs" ?>
