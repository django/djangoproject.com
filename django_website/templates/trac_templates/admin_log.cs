<h2>Logging Configuration</h2>

<form class="mod" id="modlog" method="post">
 <div class="field">
  <label>Type:<br />
   <select id="log_type" name="log_type"><?cs
    each:type = admin.log.types ?><option value="<?cs var:type.name ?>"<?cs
     if:type.selected ?> selected="selected"<?cs /if ?><?cs
     if:type.disabled ?> disabled="disabled"<?cs /if ?>><?cs
     var:type.label ?></option><?cs
    /each ?></select>
  </label>
 </div>
 <div class="field">
  <label>Log level:<br />
   <select id="log_level" name="log_level"><?cs
    each:level = admin.log.levels ?><option<?cs
     if:level == admin.log.level ?> selected="selected"<?cs /if?>><?cs
     var:level ?></option><?cs
    /each ?></select>
  </label>
 </div>
 <div class="field">
  <label>Log file:<br />
   <input type="text" id="log_file" name="log_file" size="48" value="<?cs
     var:admin.log.file ?>"/>
  </label>
  <p class="help">If you specify a relative path, the log file will be stored
  inside the <code>log</code> directory of the project environment (<code><?cs
  var:admin.log.dir ?></code>).</p>
 </div>
 <script type="text/javascript">
   var logType = document.getElementById("log_type");
   var enableLevelAndFile = function() {
     enableControl("log_level", log_type.selectedIndex > 0);
     enableControl("log_file",
       log_type.options[log_type.selectedIndex].value == "file");
   };
   addEvent(window, "load", enableLevelAndFile);
   addEvent(log_type, "change", enableLevelAndFile);
 </script>
 <div class="buttons">
  <input type="submit" value="Apply changes">
 </div>
 <p class="help">You may need to restart the server for these changes to take
 effect.</p>
</form>
