<%doc>
	Site Root Page
</%doc>
<%inherit file="base.mako"/>

## Head Resources
<%def name="heading()">
    <style type="text/css">
##        @import url("${h.url_for('/css/??.css')}");
    </style>
</%def>

## Body 
<div id="content">
    <h2>Evasion Web</h2>
    <div>
        Did you set <b><em>web_modules</em></b> in your configuration?
    </div>
</div>

<%def name="foot()">
</%def>

