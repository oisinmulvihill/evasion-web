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
    <h2>Default Webadmin</h2>
    <div>
        <em>Did you set webadmin_modules in your configuration?</em>
    </div>
</div>

<%def name="foot()">
</%def>

