<h2>Manage Plugins</h2>

<form id="addplug" class="addnew" method="post" enctype="multipart/form-data">
 <fieldset>
  <legend>Install Plugin:</legend>
  <div class="field">
   <label>File: <input type="file" name="egg_file"<?cs
     if:admin.readonly ?> disabled="disabled"<?cs /if ?> /></label>
  </div>
  <p class="help"><?cs
   if:admin.readonly ?>The web server does not have sufficient permissions to
    store files in the environment plugins directory.<?cs
   else ?>
    Upload a plugin packaged as Python egg.<?cs
   /if ?></p>
  <div class="buttons">
   <input type="submit" name="install" value="Install"<?cs
     if:admin.readonly ?> disabled="disabled"<?cs /if ?> />
  </div>
 </fieldset>
</form>

<script type="text/javascript" src="<?cs
  var:chrome.href ?>/admin/js/admin.js"></script><?cs
 each:plugin = admin.plugins ?><form method="post"><div class="plugin">
 <h3 id="no<?cs var:name(plugin) ?>"><?cs
   var:plugin.name ?> <?cs var:plugin.version ?></h3>
 <div class="uninstall buttons">
  <input type="hidden" name="plugin_filename" value="<?cs
    var:plugin.plugin_filename ?>" />
  <input type="submit" name="uninstall" value="Uninstall"<?cs
   if:plugin.readonly ?> disabled="disabled"<?cs /if ?> />
 </div>
 <p class="summary"><?cs var:plugin.info.summary ?></p><?cs
 if:plugin.info.home_page || plugin.info.author || plugin.info.author_email ?>
  <dl class="info"><?cs
   if:plugin.info.author || plugin.info.author_email ?>
    <dt>Author:</dt>
    <dd><?cs
    if:plugin.info.author_email ?><a href="mailto:<?cs
     var:plugin.info.author_email ?>"><?cs alt:plugin.info.author ?><?cs
      var:plugin.info.author_email ?><?cs /alt ?></a><?cs
    else ?><?cs var:plugin.info.author ?><?cs
    /if ?></dd><?cs
   /if ?><?cs
   if:plugin.info.home_page ?>
    <dt>Home page:</dt>
    <dd><a onclick="window.open(this.href); return false" href="<?cs
      var:plugin.info.home_page ?>"><?cs var:plugin.info.home_page ?></a></dt><?cs
   /if ?><?cs
   if:plugin.info.license ?>
    <dt>License:</dt>
    <dd><?cs var:plugin.info.license ?></dd><?cs
   /if ?>
  </dl><?cs
 /if ?><table class="listing"><thead>
   <tr><th>Component</th><th class="sel">Enabled</th></tr>
  </thead><tbody><?cs
  each:component = plugin.components ?><tr>
   <td class="name" title="<?cs var:component.description ?>"><?cs
    var:component.name ?><p class="module"><?cs var:component.module ?></p></td>
   <td class="sel"><?cs
    if:!component.required ?><input type="hidden" name="component" value="<?cs
     var:component.module ?>.<?cs var:component.name ?>" /><?cs
    /if ?><input type="checkbox" name="enable" value="<?cs
     var:component.module ?>.<?cs var:component.name ?>"<?cs 
     if:component.enabled ?> checked="checked"<?cs
     /if ?><?cs
     if:component.required ?> disabled="disabled"<?cs
     /if ?> /></td>
  </tr><?cs
  /each ?></tbody>
 </table>
 <div class="update buttons">
  <input type="hidden" name="plugin" value="<?cs var:name(plugin) ?>" />
  <input type="submit" name="update" value="Apply changes" />
 </div></div><script type="text/javascript">
   enableFolding("no<?cs var:name(plugin) ?>");
 </script></form><?cs
 /each ?>
