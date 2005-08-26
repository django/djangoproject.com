<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
	<head>
		<meta http-equiv="Content-type" content="text/html; charset=utf-8" />
		<meta http-equiv="Content-Language" content="en-us" />

		<title>Django | Code <?cs if:title ?>| <?cs var:title ?><?cs /if ?></title>

		<meta name="ROBOTS" content="ALL" />
		<meta http-equiv="imagetoolbar" content="no" />
		<meta name="MSSmartTagsPreventParsing" content="true" />
		<meta name="Copyright" content="This site's design and contents Copyright (c) 2005  World Online." />
		<!-- (c) Copyright 2005 World Online All Rights Reserved. -->

		<meta name="keywords" content="Python, Django, framework, open-source" />
		<meta name="description" content="Django is a high-level Python Web framework that encourages rapid development and clean, pragmatic design." />

        <?cs each:rel = links ?>
        <?cs each:link = rel ?>
        <link rel="<?cs var:name(rel) ?>"
              href="<?cs var:link.href ?>"
              <?cs if:link.title ?>title="<?cs var:link.title ?>"<?cs /if ?>
              <?cs if:link.type ?>type="<?cs var:link.type ?>"<?cs /if ?> />
        <?cs /each ?>
        <?cs /each ?>

        <style type="text/css">
         <?cs if:html.stylesheet ?>@import url(http://media.djangoproject.com/trac/<?cs
           var:html.stylesheet ?>);<?cs /if ?>
         <?cs include "site_css.cs" ?>
        </style>
        <script src="<?cs var:htdocs_location ?>trac.js" type="text/javascript"></script>

		<link href="http://media.djangoproject.com/trac/css/trac.css" rel="stylesheet" type="text/css" media="all" />
		<link href="http://media.djangoproject.com/css/base.css" rel="stylesheet" type="text/css" media="all" />

    </head>

	<body id="code">

	<div id="container">
		<div id="header">
			<h1 id="logo"><a href="http://www.djangoproject.com/"><img src="http://media.djangoproject.com/img/site/hdr_logo.gif" alt="Django" /></a></h1>
			<ul id="nav-global">
				<li id="nav-homepage"><a href="http://www.djangoproject.com/">Home</a></li>
				<li id="nav-download"><a href="http://www.djangoproject.com/download/">Download</a></li>
				<li id="nav-documentation"><a href="http://www.djangoproject.com/documentation/">Documentation</a></li>
				<li id="nav-weblog"><a href="http://www.djangoproject.com/weblog/">Weblog</a></li>
				<li id="nav-community"><a href="http://www.djangoproject.com/community/">Community</a></li>
				<li id="nav-code"><a href="http://code.djangoproject.com/">Code</a></li>
			</ul>
		</div>
		<!-- END Header -->
		<div id="billboard"><h2><a href="http://code.djangoproject.com/">Code</a></h2></div>
		<div id="columnwrap">

		<div id="content-main">

        <?cs def:navlink(text, href, id, aclname, accesskey) ?><?cs
         if $aclname ?><li><a href="<?cs var:href ?>"<?cs
          if $id == $trac.active_module ?> class="active"<?cs
          /if ?><?cs
          if:$accesskey!="" ?> accesskey="<?cs var:$accesskey ?>"<?cs
          /if ?>><?cs var:text ?></a></li><?cs
         /if ?><?cs
        /def ?>

         <form id="search" action="<?cs var:trac.href.search ?>" method="get">
          <?cs if:trac.acl.SEARCH_VIEW ?><div>
           <label for="proj-search">Search:</label>
           <input type="text" id="proj-search" name="q" size="10" value="" />
           <input type="submit" value="Search" />
           <input type="hidden" name="wiki" value="on" />
           <input type="hidden" name="changeset" value="on" />
           <input type="hidden" name="ticket" value="on" />
          </div><?cs /if ?>
         </form>

        <?cs def:nav(items) ?><?cs
         if:len(items) ?><ul><?cs
          set:idx = 0 ?><?cs
          set:max = len(items) - 1 ?><?cs
          each:item = items ?><?cs
           set:first = idx == 0 ?><?cs
           set:last = idx == max ?><li<?cs
           if:first || last || item.active ?> class="<?cs
            if:item.active ?>active<?cs /if ?><?cs
            if:item.active && (first || last) ?> <?cs /if ?><?cs
            if:first ?>first<?cs /if ?><?cs
            if:(item.active || first) && last ?> <?cs /if ?><?cs
            if:last ?>last<?cs /if ?>"<?cs
           /if ?>><?cs var:item ?></li><?cs
           set:idx = idx + 1 ?><?cs
          /each ?></ul><?cs
         /if ?><?cs
        /def ?>
        
        <div id="mainnav" class="nav"><?cs call:nav(chrome.nav.mainnav) ?></div>
        <div id="main">
