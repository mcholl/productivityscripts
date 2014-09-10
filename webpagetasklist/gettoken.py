import dropbox

# Get your app key and secret from the Dropbox developer website
app_key = 'aw3h72pdp23v2ub'
app_secret = '09hr83aj0gf15dv'

flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

# Have the user sign in and authorize this token
authorize_url = flow.start()
print '1. Go to: ' + authorize_url
print '2. Click "Allow" (you might have to log in first)'
print '3. Copy the authorization code.'
code = raw_input("Enter the authorization code here: ").strip()

# This will fail if the user enters an invalid authorization code
access_token, user_id = flow.finish(code)

print "User Id is "+user_id
print "Access Token is "+access_token
