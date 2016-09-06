from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Genre, Subgenre, User

engine = create_engine('sqlite:///musicology.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()



# 1. Rock Genre and Subgenres
genre1 = Genre(user_id=1, name="Rock")

session.add(genre1)
session.commit()


subgenre1 = Subgenre(user_id=1, name="Hard Rock",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre1)

session.add(subgenre1)
session.commit()

subgenre2 = Subgenre(user_id=1, name="Rock & Roll",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre1)

session.add(subgenre2)
session.commit()

subgenre3 = Subgenre(user_id=1, name="Afro Punk",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre1)

session.add(subgenre3)
session.commit()

subgenre4 = Subgenre(user_id=1, name="Soft Rock",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre1)

session.add(subgenre4)
session.commit()


# 2. Classical Genre and Subgenres
genre2 = Genre(user_id=1, name="Classical Music")

session.add(genre2)
session.commit()


subgenre1 = Subgenre(user_id=1, name="Orchestral",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre2)

session.add(subgenre1)
session.commit()

subgenre2 = Subgenre(user_id=1, name="Opera",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre2)

session.add(subgenre2)
session.commit()

subgenre3 = Subgenre(user_id=1, name="Contemporary Classical",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre2)

session.add(subgenre3)
session.commit()

subgenre4 = Subgenre(user_id=1, name="Minimalism",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre2)

session.add(subgenre4)
session.commit()


# 3. Hip-Hop Genre and Subgenres
genre3 = Genre(user_id=1, name="Hip-Hop")

session.add(genre3)
session.commit()


subgenre1 = Subgenre(user_id=1, name="Alternative Rap",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre3)

session.add(subgenre1)
session.commit()

subgenre2 = Subgenre(user_id=1, name="Old School",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre3)

session.add(subgenre2)
session.commit()

subgenre3 = Subgenre(user_id=1, name="Underground Rap",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre3)

session.add(subgenre3)
session.commit()

subgenre4 = Subgenre(user_id=1, name="Turntablism",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre3)

session.add(subgenre4)
session.commit()

subgenre5 = Subgenre(user_id=1, name="Experimental",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre3)

session.add(subgenre5)
session.commit()


# 4. World Music Genre and Subgenres
genre4 = Genre(user_id=1, name="World Music")

session.add(genre4)
session.commit()


subgenre1 = Subgenre(user_id=1, name="Afro-Beat",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre4)

session.add(subgenre1)
session.commit()

subgenre2 = Subgenre(user_id=1, name="Calypso",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre4)

session.add(subgenre2)
session.commit()

subgenre3 = Subgenre(user_id=1, name="K-Pop",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre4)

session.add(subgenre3)
session.commit()

subgenre4 = Subgenre(user_id=1, name="Mbalax",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre4)

session.add(subgenre4)
session.commit()

subgenre5 = Subgenre(user_id=1, name="Zouk",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre4)

session.add(subgenre5)
session.commit()


# 5. Reggae Genre and Subgenres
genre5 = Genre(name="Reggae")

session.add(genre5)
session.commit()


subgenre1 = Subgenre(user_id=1, name="Dancehall",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre5)

session.add(subgenre1)
session.commit()

subgenre2 = Subgenre(user_id=1, name="Roots Reggae",
                     description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     genre=genre5)

session.add(subgenre2)
session.commit()


print "New music genres & subgenres added!"
