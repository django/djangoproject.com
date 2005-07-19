<?cs def:hdf_select(options, name, selected) ?>
 <select size="1" id="<?cs var:name ?>" name="<?cs var:name ?>"><?cs
  each:option = options ?><?cs
   if option.name == $selected ?>
    <option selected="selected"><?cs var:option.name ?></option><?cs
   else ?>
    <option><?cs var:option.name ?></option><?cs
   /if ?><?cs
  /each ?>
 </select><?cs
/def?>

<?cs def:hdf_select_multiple(options, name, size) ?>
 <select size="<?cs var:size ?>" id="<?cs var:name ?>" name="<?cs
   var:name ?>" multiple="multiple"><?cs
  each:option = options ?>
   <option<?cs if:option.selected ?> selected="selected"<?cs /if ?>><?cs
    var:option.name ?></option><?cs
  /each ?>
 </select><?cs
/def ?>

<?cs def:browser_path_links(path, file) ?><?cs
 set:first = #1 ?>
 <h1><?cs
  each:part = path ?><?cs
   set:last = name(part) == len(path) - #1 ?><a<?cs 
   if:first ?> class="first" title="Go to root directory"<?cs 
    set:first = #0 ?><?cs 
   else ?> title="Go to directory"<?cs
   /if ?> href="<?cs var:part.url ?>"><?cs var:part ?></a><?cs
   if:file.filename || !last ?><span class="sep">/</span><?cs /if ?><?cs 
 /each ?><?cs
 if:file.filename ?><span class="filename"><?cs var:file.filename ?></span><?cs
 /if ?></h1>
<?cs /def ?>

<?cs def:diff_display(change, style) ?><?cs
 if:style == 'sidebyside' ?><?cs
  each:block = change.blocks ?><?cs
   if:block.type == 'unmod' ?><tbody class="unmod"><?cs
    each:line = block.base.lines ?><tr>
     <th class="base"><?cs var:#block.base.offset + name(line) + 1 ?></th>
     <td class="base"><span><?cs var:line ?></span>&nbsp;</td>
     <th class="chg"><?cs var:#block.changed.offset + name(line) + 1 ?></th>
     <td class="chg"><span><?cs var:line ?></span>&nbsp;</td>
    </tr><?cs /each ?>
   </tbody><?cs
   elif:block.type == 'mod' ?><tbody class="mod"><?cs
    if:len(block.base.lines) >= len(block.changed.lines) ?><?cs
     each:line = block.base.lines ?><tr>
      <th class="base"><?cs var:#block.base.offset + name(line) + 1 ?></th>
      <td class="base"><?cs var:line ?>&nbsp;</td><?cs
      if:len(block.changed.lines) >= name(line) + 1 ?><?cs
       each:changedline = block.changed.lines ?><?cs
        if:name(changedline) == name(line) ?>
         <th class="chg"><?cs var:#block.changed.offset + name(changedline) + 1 ?></th>
         <td class="chg"><?cs var:changedline ?>&nbsp;</td><?cs
        /if ?><?cs
       /each ?><?cs
      else ?>
       <th class="chg">&nbsp;</th>
       <td class="chg">&nbsp;</td><?cs
      /if ?>
     </tr><?cs /each ?><?cs
    else ?><?cs
     each:line = block.changed.lines ?><tr><?cs
      if:len(block.base.lines) >= name(line) + 1 ?><?cs
       each:baseline = block.base.lines ?><?cs
        if:name(baseline) == name(line) ?>
         <th class="base"><?cs var:#block.base.offset + name(baseline) + 1 ?></th>
         <td class="base"><?cs var:baseline ?>&nbsp;</td><?cs
        /if ?><?cs
       /each ?><?cs
      else ?>
       <th class="base">&nbsp;</th>
       <td class="base">&nbsp;</td><?cs
      /if ?>
      <th class="chg"><?cs var:#block.changed.offset + name(line) + 1 ?></th>
      <td class="chg"><?cs var:line ?>&nbsp;</td>
     </tr><?cs /each ?><?cs
    /if ?>
   </tbody><?cs
   elif:block.type == 'add' ?><tbody class="add"><?cs
    each:line = block.changed.lines ?><tr>
     <th class="base">&nbsp;</th>
     <td class="base">&nbsp;</td>
     <th class="chg"><?cs var:#block.changed.offset + name(line) + 1 ?></th>
     <td class="chg"><ins><?cs var:line ?></ins>&nbsp;</td>
    </tr><?cs /each ?><?cs
   elif:block.type == 'rem' ?><tbody class="rem"><?cs
    each:line = block.base.lines ?><tr>
     <th class="base"><?cs var:#block.base.offset + name(line) + 1 ?></th>
     <td class="base"><del><?cs var:line ?></del>&nbsp;</td>
     <th class="chg">&nbsp;</th>
     <td class="chg">&nbsp;</td>
    </tr><?cs /each ?><?cs
   /if ?>
  </tbody><?cs
  /each ?><?cs
 else ?><?cs
  each:block = change.blocks ?>
   <?cs if:block.type == 'unmod' ?><tbody class="unmod"><?cs
    each:line = block.base.lines ?><tr>
     <th class="base"><?cs var:#block.base.offset + name(line) + #1 ?></th>
     <th class="chg"><?cs var:#block.changed.offset + name(line) + #1 ?></th>
     <td class="base"><span><?cs var:line ?></span>&nbsp;</td>
    </tr><?cs /each ?>
   </tbody>
   <?cs elif:block.type == 'mod' ?><tbody class="mod"><?cs
    each:line = block.base.lines ?><tr class="<?cs
      if:name(line) == 0 ?>first<?cs /if ?>">
     <th class="base"><?cs var:#block.base.offset + name(line) + #1 ?></th>
     <th class="chg">&nbsp;</th>
     <td class="base"><?cs var:line ?>&nbsp;</td>
    </tr><?cs /each ?><?cs
    each:line = block.changed.lines ?><tr class="<?cs
      if:name(line) + 1 == len(block.changed.lines) ?> last<?cs /if ?>">
     <th class="base">&nbsp;</th>
     <th class="chg"><?cs var:#block.changed.offset + name(line) + #1 ?></th>
     <td class="chg"><?cs var:line ?>&nbsp;</td>
    </tr><?cs /each ?>
   </tbody>
   <?cs elif:block.type == 'add' ?><tbody class="add"><?cs
    each:line = block.changed.lines ?><tr class="<?cs
      if:name(line) == 0 ?>first<?cs /if ?><?cs
      if:name(line) + 1 == len(block.changed.lines) ?> last ?><?cs /if ?>">
     <th class="base">&nbsp;</th>
     <th class="chg"><?cs var:#block.changed.offset + name(line) + #1 ?></th>
     <td class="chg"><ins><?cs var:line ?></ins>&nbsp;</td>
    </tr><?cs /each ?>
   </tbody>
   <?cs elif:block.type == 'rem' ?><tbody class="rem"><?cs
    each:line = block.base.lines ?><tr class="<?cs
      if:name(line) == 0 ?>first<?cs /if ?><?cs
      if:name(line) + 1 == len(block.base.lines) ?> last ?><?cs /if ?>">
     <th class="base"><?cs var:#block.base.offset + name(line) + 1 ?></th>
     <th class="chg">&nbsp;</th>
     <td class="base"><del><?cs var:line ?></del>&nbsp;</td>
    </tr><?cs /each ?>
   </tbody>
   <?cs /if ?><?cs
  /each ?><?cs
 /if ?><?cs
/def ?>

<?cs def:session_name_email() ?><?cs
  if trac.authname != "anonymous" ?><?cs 
     var:trac.authname ?><?cs 
  elif trac.session.var.name && trac.session.var.email ?><?cs
     var:trac.session.var.name ?> &lt;<?cs var:trac.session.var.email ?>&gt;<?cs 
  elif !trac.session.var.name && trac.session.var.email ?><?cs 
     var:trac.session.var.email ?><?cs 
  else ?><?cs
     var:trac.authname ?><?cs 
  /if ?><?cs
  /def ?>

<?cs def:ticket_custom_props(ticket) ?><?cs
 each c=ticket.custom ?>
  <div class="field custom_<?cs var c.name ?>"><?cs
   if c.type == 'text' || c.type == 'select' ?>
    <label for="custom_<?cs var c.name ?>"><?cs alt c.label ?><?cs
      var c.name ?><?cs /alt ?></label>:<?cs
   /if ?><?cs
   if c.type == 'text' ?>
    <input type="text" id="custom_<?cs var c.name ?>" name="custom_<?cs
      var c.name ?>" value="<?cs var c.value ?>" /><?cs
   elif c.type == 'textarea' ?>
    <label for="custom_<?cs var c.name ?>"><?cs alt c.label ?><?cs
      var c.name ?><?cs /alt ?></label>:<br />
    <textarea cols="<?cs alt c.width ?>60<?cs /alt ?>" rows="<?cs
      alt c.height ?>12<?cs /alt ?>" name="custom_<?cs var c.name ?>"><?cs
      var c.value ?></textarea><?cs
   elif c.type == 'checkbox' ?>
    <input type="hidden" name="checkbox_<?cs var c.name ?>" value="custom_<?cs
      var c.name ?>" />
    <input type="checkbox" id="custom_<?cs var c.name ?>" name="custom_<?cs
      var c.name ?>" value="1" <?cs if c.selected ?>checked="checked"<?cs /if ?> />
    <label for="custom_<?cs var c.name ?>"><?cs alt c.label ?><?cs
      var c.name ?><?cs /alt ?></label><?cs
   elif c.type == 'select' ?>
    <select name="custom_<?cs var c.name ?>"><?cs each v = c.option ?>
     <option <?cs if v.selected ?>selected="selected"<?cs /if ?>><?cs
       var v ?></option><?cs /each ?>
    </select><?cs
   elif c.type == 'radio' ?>
    <fieldset class="radio">
     <legend><?cs alt c.label ?><?cs var c.name ?><?cs /alt ?>:</legend><?cs
     each v = c.option ?>
      <input type="radio" id="custom_<?cs var c.name ?>_<?cs
        var v ?>" name="custom_<?cs var c.name ?>"<?cs
        if v.selected ?> checked="checked"<?cs /if ?> value="<?cs var v ?>"/>
      <label for="custom_<?cs var c.name ?>_<?cs var v ?>"><?cs
        var v ?></label><?cs
     /each ?>
    </fieldset><?cs
   /if ?>
  </div><?cs
 /each ?><?cs
/def ?>

<?cs def:wiki_toolbar(textarea_id) ?>
<script type='text/javascript'>
 addWikiFormattingToolbar(document.getElementById("<?cs var:textarea_id ?>"));
</script>
<?cs /def ?>
