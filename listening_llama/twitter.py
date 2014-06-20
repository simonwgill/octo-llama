from twython import Twython

TWITTER_API_KEY = "emuanjY83cDBsPbXSSTu2qgU6"
TWITTER_API_SECRET = "zKBCdu7F5Pb8qrWuMPJfEfZ6GK2PbetydA2UdEII0Qt51aIJzz"

#twitter = Twython(TWITTER_API_KEY, TWITTER_API_SECRET, oauth_version=2)
ACCESS_TOKEN = "260543066-jtV6jrii3KBXeWODha4agymIIYzlHPnLNPqnI11M"
ACCESS_TOKEN_SECRET = "EF3VWX7NOA8iJuJMFm8eQ0W7TdDYR4bKyP0fDBL89kxDc"

twitter = Twython(TWITTER_API_KEY, TWITTER_API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

#print twitter.get_place_trends(id='12602192')
print twitter.get_place_trends(id='23424975')
