"""
Test data for BoardGameGeek API tests.

This module contains mock data used across multiple test files to simulate
responses from the BoardGameGeek API.
"""

MOCK_PLAYED_GAMES_XML = b"""
<items>
    <item objectid="1">
        <name>Game 1</name>
        <image>http://example.com/image1.jpg</image>
    </item>
    <item objectid="2">
        <name>Game 2</name>
        <image>http://example.com/image2.jpg</image>
    </item>
</items>
"""

# Mock response for a valid BGG user - based on actual API response
MOCK_VALID_USER_XML = b"""<?xml version="1.0" encoding="utf-8"?><user id="167477" name="otteydw" termsofuse="https://boardgamegeek.com/xmlapi/termsofuse">
<firstname value="Daniel" /> <lastname value="Ottey" /> <avatarlink value="https://cf.geekdo-static.com/avatars/avatar_id73634.jpg" /> <yearregistered value="2007" /> <lastlogin value="2025-02-21" /> <stateorprovince value="Pennsylvania" /> <country value="United States" /> <webaddress value="http://www.facebook.com/otteydw" /> <xboxaccount value="" /> <wiiaccount value="" /> <psnaccount value="" /> <battlenetaccount value="" /> <steamaccount value="" /> <traderating value="0" />
</user>"""

# Mock response for an invalid BGG user (HTML error page)
MOCK_INVALID_USER_HTML = """<!DOCTYPE html>
<html>
<head><title>BoardGameGeek</title></head>
<body>
<h1>It appears we're missing some bits</h1>
<p>We couldn't find the page you were looking for.</p>
</body>
</html>"""

# Mock response for a malformed XML
MOCK_MALFORMED_USER_XML = b"""<?xml version="1.0" encoding="utf-8"?><user
    <firstname value="Malformed"/>
    <lastname value="User"/>
</user>"""
