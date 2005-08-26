<?xml version="1.0"?>
<rss version="2.0">
 <channel><?cs
  if:project.name.encoded ?>
   <title><?cs var:project.name.encoded ?>: <?cs var:title ?></title><?cs
  else ?>
   <title><?cs var:title ?></title><?cs
  /if ?>
  <link><?cs var:base_host ?><?cs var:trac.href.timeline ?></link>
  <description>Trac Timeline</description>
  <language>en-us</language>
  <generator>Trac v<?cs var:trac.version ?></generator>
  <image>
   <title><?cs var:project.name.encoded ?></title>
   <url><?cs if:!header_logo.src_abs ?><?cs var:base_host ?><?cs /if ?><?cs
    var:header_logo.src ?></url>
   <link><?cs var:base_host ?><?cs var:trac.href.timeline ?></link>
  </image><?cs
  each:event = timeline.events ?>
   <item>
    <title><?cs var:event.title ?></title><?cs
    if:event.author.email ?>
     <author><?cs var:event.author.email ?></author><?cs
    /if ?>
    <pubDate><?cs var:event.date ?></pubDate>
    <link><?cs var:event.href ?></link>
    <description><?cs var:event.message ?></description>
   </item><?cs
  /each ?>
 </channel>
</rss>
