# - Coding UTF8 -
#
# Networked Decision Making
# Development Sites (source code): http://github.com/DonaldMcC/gdms
#
# Demo Sites (Pythonanywhere)
#   http://netdecisionmaking.com/nds/
#   http://netdecisionmaking.com/gdmsdemo/
#
# License Code: MIT
# License Content: Creative Commons Attribution 3.0
#
# Also visit: www.web2py.com
# or Groups: http://groups.google.com/group/web2py
# For details on the web framework used for this development
#
# With thanks to Guido, Massimo and many other that make this sort of thing
# much easier than it used to be

# This is still inelegant but it only runs once so it will do for now
# Lets change to a 2 dim list
# need to pip install pycountry and incf.countryutils before this code will work

import pycountry


@auth.requires_membership('manager')
def countries():
    for country in pycountry.countries:
        try:
            if db(db.country.country_name == country.name).isempty():
                db.country.insert(country_name=country.name)
        except KeyError as e:
            print('IKeyError - reason "%s"' % str(e))
    return locals()


@auth.requires_membership('manager')
def subdivns():
    for country in pycountry.countries:
        try:
            arscountry = db(db.country.country_name == country.name).select().first()
            subdivn = pycountry.subdivisions.get(country_code=country.alpha_2)
            for x in subdivn:
                if db(db.subdivision.subdiv_name == x.name).isempty():
                    db.subdivision.insert(subdiv_name=x.name, country=country.name, countryid =arscountry.id)
        except KeyError as e:
            print('I got a KeyError - reason "%s"' % str(e))
    return locals()
