<?cs def:hdf_select(options, name, selected, optional) ?>
 <select size="1" id="<?cs var:name ?>" name="<?cs var:name ?>"><?cs
  if:optional ?><option></option><?cs /if ?><?cs
  each:option = options ?>
   <option<?cs if:option == selected ?> selected="selected"<?cs /if ?>><?cs 
     var:option ?></option><?cs
  /each ?>
 </select><?cs
/def?>

<?cs def:labelled_hdf_select(label, options, name, selected, optional) ?><?cs 
 if:len(options) > #0 ?>
  <label for="<?cs var:name ?>"><?cs var:label ?></label><?cs
   call:hdf_select(options, name, selected, optional) ?>
  </label>
  <br /><?cs
 /if ?><?cs
/def ?>

<?cs def:browser_path_links(path, file) ?><?cs
 set:first = #1 ?><?cs
  each:part = path ?><?cs
   set:last = name(part) == len(path) - #1 ?><a<?cs 
   if:first ?> class="first" title="Go to root directory"<?cs 
    set:first = #0 ?><?cs 
   else ?> title="View <?cs var:part.name ?>"<?cs
   /if ?> href="<?cs var:part.href ?>"><?cs var:part.name ?></a><?cs
   if:!last ?><span class="sep">/</span><?cs /if ?><?cs 
 /each ?><?cs
/def ?>

<?cs def:diff_line_class(block, line) ?><?cs
 set:first = name(line) == 0 ?><?cs
 set:last = name(line) + 1 == len(block.lines) ?><?cs
 if:first || last ?> class="<?cs
  if:first ?>first<?cs /if ?><?cs
  if:first && last ?> <?cs /if ?><?cs
  if:last ?>last<?cs /if ?>"<?cs
 /if ?><?cs
/def ?>

<?cs def:diff_display(diff, style) ?><?cs
 if:style == 'sidebyside' ?><?cs
  each:block = diff ?><?cs
   if:block.type == 'unmod' ?><tbody><?cs
    each:line = block.base.lines ?><tr><th><?cs
     var:#block.base.offset + name(line) + 1 ?></th><td class="l"><span><?cs
     var:line ?></span>&nbsp;</td><th><?cs
     var:#block.changed.offset + name(line) + 1 ?></th><td class="r"><span><?cs
     var:block.changed.lines[name(line)] ?></span>&nbsp;</td></tr><?cs
    /each ?></tbody><?cs
   elif:block.type == 'mod' ?><tbody class="mod"><?cs
    if:len(block.base.lines) >= len(block.changed.lines) ?><?cs
     each:line = block.base.lines ?><tr><th><?cs
      var:#block.base.offset + name(line) + 1 ?></th><td class="l"><?cs
      var:line ?>&nbsp;</td><?cs
      if:len(block.changed.lines) >= name(line) + 1 ?><?cs
       each:changedline = block.changed.lines ?><?cs
        if:name(changedline) == name(line) ?><th><?cs
         var:#block.changed.offset + name(changedline) + 1 ?></th><td class="r"><?cs
         var:changedline ?>&nbsp;</td><?cs
        /if ?><?cs
       /each ?><?cs
      else ?><th>&nbsp;</th><td class="r">&nbsp;</td><?cs
      /if ?></tr><?cs
     /each ?><?cs
    else ?><?cs
     each:line = block.changed.lines ?><tr><?cs
      if:len(block.base.lines) >= name(line) + 1 ?><?cs
       each:baseline = block.base.lines ?><?cs
        if:name(baseline) == name(line) ?><th><?cs
         var:#block.base.offset + name(baseline) + 1 ?></th><td class="l"><?cs
         var:baseline ?>&nbsp;</td><?cs
        /if ?><?cs
       /each ?><?cs
      else ?><th>&nbsp;</th><td class="l">&nbsp;</td><?cs
      /if ?>
      <th><?cs var:#block.changed.offset + name(line) + 1 ?></th>
      <td class="r"><?cs var:line ?>&nbsp;</td></tr><?cs
     /each ?><?cs
    /if ?></tbody><?cs
   elif:block.type == 'add' ?><tbody class="add"><?cs
    each:line = block.changed.lines ?><tr><th>&nbsp;</th><td class="l">&nbsp;</td><th><?cs
     var:#block.changed.offset + name(line) + 1 ?></th><td class="r"><ins><?cs
     var:line ?></ins>&nbsp;</td></tr><?cs
    /each ?><?cs
   elif:block.type == 'rem' ?><tbody class="rem"><?cs
    each:line = block.base.lines ?><tr><th><?cs
     var:#block.base.offset + name(line) + 1 ?></th><td class="l"><del><?cs
     var:line ?></del>&nbsp;</td><th>&nbsp;</th><td class="r">&nbsp;</td></tr><?cs
    /each ?><?cs
   /if ?></tbody><?cs
  /each ?><?cs
 else ?><?cs
  each:block = diff ?><?cs
   if:block.type == 'unmod' ?><tbody><?cs
    each:line = block.base.lines ?><tr><th><?cs
     var:#block.base.offset + name(line) + #1 ?></th><th><?cs
     var:#block.changed.offset + name(line) + #1 ?></th><td class="l"><span><?cs
     var:line ?></span>&nbsp;</td></tr><?cs
    /each ?></tbody><?cs
   elif:block.type == 'mod' ?><tbody class="mod"><?cs
    each:line = block.base.lines ?><tr<?cs
     if:name(line) == 0 ?> class="first"<?cs /if ?>><th><?cs
     var:#block.base.offset + name(line) + #1 ?></th><th>&nbsp;</th><td class="l"><?cs
     var:line ?>&nbsp;</td></tr><?cs
    /each ?><?cs
    each:line = block.changed.lines ?><tr<?cs
     if:name(line) + 1 == len(block.changed.lines) ?> class="last"<?cs /if ?>><th>&nbsp;</th><th><?cs
     var:#block.changed.offset + name(line) + #1 ?></th><td class="r"><?cs
     var:line ?>&nbsp;</td></tr><?cs
    /each ?></tbody><?cs
   elif:block.type == 'add' ?><tbody class="add"><?cs
    each:line = block.changed.lines ?><tr<?cs
     call:diff_line_class(block.changed, line) ?>><th>&nbsp;</th><th><?cs
     var:#block.changed.offset + name(line) + #1 ?></th><td class="r"><ins><?cs
     var:line ?></ins>&nbsp;</td></tr><?cs
    /each ?></tbody><?cs
   elif:block.type == 'rem' ?><tbody class="rem"><?cs
    each:line = block.base.lines ?><tr<?cs
     call:diff_line_class(block.base, line) ?>><th><?cs
     var:#block.base.offset + name(line) + 1 ?></th><th>&nbsp;</th><td class="l"><del><?cs
     var:line ?></del>&nbsp;</td></tr><?cs
    /each ?></tbody><?cs
   /if ?><?cs
  /each ?><?cs
 /if ?><?cs
/def ?><?cs

def:ticket_custom_props(ticket) ?><?cs
 each c=ticket.custom ?>
  <div class="field custom_<?cs var c.name ?>"><?cs
   if c.type == 'text' ?>
    <label>
     <?cs alt c.label ?><?cs var c.name ?><?cs /alt ?>:
     <input type="text" name="custom_<?cs var c.name ?>" value="<?cs var c.value ?>" />
    </label><?cs
   elif c.type == 'textarea' ?>
    <label>
     <?cs alt c.label ?><?cs var c.name ?><?cs /alt ?>:<br />
     <textarea cols="<?cs alt c.width ?>60<?cs /alt ?>" rows="<?cs
       alt c.height ?>12<?cs /alt ?>" name="custom_<?cs var c.name ?>"><?cs
       var c.value ?></textarea>
    </label><?cs
   elif c.type == 'checkbox' ?>
    <input type="hidden" name="checkbox_<?cs var c.name ?>" />
    <label>
     <input type="checkbox" name="custom_<?cs var c.name ?>" value="1"<?cs
       if c.selected ?> checked="checked"<?cs /if ?> />
     <?cs alt c.label ?><?cs var c.name ?><?cs /alt ?>
    </label><?cs
   elif c.type == 'select' ?>
    <label>
     <?cs alt c.label ?><?cs var c.name ?><?cs /alt ?>:
     <select name="custom_<?cs var c.name ?>"><?cs each v = c.option ?>
      <option<?cs if v.selected ?> selected="selected"<?cs /if ?>><?cs
        var v ?></option><?cs /each ?>
     </select>
    </label><?cs
   elif c.type == 'radio' ?>
    <fieldset class="radio">
     <legend><?cs alt c.label ?><?cs var c.name ?><?cs /alt ?>:</legend><?cs
     each v = c.option ?>
      <label><input type="radio" name="custom_<?cs var c.name ?>" value="<?cs
         var v ?>"<?cs if v.selected ?> checked="checked"<?cs /if ?> /> <?cs
         var v ?></label><?cs
     /each ?>
    </fieldset><?cs
   /if ?>
  </div><?cs
 /each ?><?cs
/def ?><?cs 

def:sortable_th(order, desc, class, title, href) ?>
 <th class="<?cs var:class ?><?cs if:order == class ?> <?cs if:desc ?>desc<?cs else ?>asc<?cs /if ?><?cs /if ?>">
  <a title="Sort by <?cs var:class ?><?cs if:order == class && !desc ?> (descending)<?cs /if ?>"
     href="<?cs var:href ?>?order=<?cs var:class ?><?cs if:order == class && !desc ?>&desc=1<?cs /if ?>"><?cs var:title ?></a>
 </th><?cs
/def ?>
