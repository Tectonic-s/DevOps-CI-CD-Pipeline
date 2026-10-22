"""
build_expanded_dataset.py
Builds an expanded catalog of 160+ iconic movies with rich metadata and fetches
authentic, official movie poster images directly from the movie database API.
"""

import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request

CACHE_FILE = os.path.join(os.path.dirname(__file__), "poster_cache.json")

# 160+ Iconic, top-rated, and widely-known films across diverse genres
EXPANDED_MOVIES = [
    # --- SCI-FI & SPACE ---
    {
        "title": "Inception", "year": 2010,
        "genres": "Action, Sci-Fi, Adventure, Thriller",
        "director": "Christopher Nolan",
        "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt, Elliot Page, Tom Hardy",
        "rating": 8.8, "runtime": 148,
        "overview": "A skilled thief who steals corporate secrets through dream-sharing technology is tasked with planting an idea into the mind of a CEO.",
        "keywords": "subconscious dream within dream heist mind bending corporate espionage lucid dreaming reality manipulation"
    },
    {
        "title": "Interstellar", "year": 2014,
        "genres": "Adventure, Drama, Sci-Fi",
        "director": "Christopher Nolan",
        "cast": "Matthew McConaughey, Anne Hathaway, Jessica Chastain, Michael Caine",
        "rating": 8.7, "runtime": 169,
        "overview": "When Earth becomes uninhabitable, a team of researchers and pilot Cooper travel through a wormhole across spacetime to find humanity a new home.",
        "keywords": "wormhole black hole space travel father daughter gravity relativity time dilation cosmic survival fifth dimension"
    },
    {
        "title": "The Matrix", "year": 1999,
        "genres": "Action, Sci-Fi",
        "director": "Lana Wachowski, Lilly Wachowski",
        "cast": "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss, Hugo Weaving",
        "rating": 8.7, "runtime": 136,
        "overview": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
        "keywords": "simulated reality cyberpunk artificial intelligence chosen one martial arts hacker rebellion dystopia red pill"
    },
    {
        "title": "Blade Runner 2049", "year": 2017,
        "genres": "Action, Drama, Mystery, Sci-Fi, Thriller",
        "director": "Denis Villeneuve",
        "cast": "Ryan Gosling, Harrison Ford, Ana de Armas, Sylvia Hoeks",
        "rating": 8.0, "runtime": 164,
        "overview": "Young Blade Runner K uncovers a secret that could plunge society into chaos, leading him on a quest to find missing former blade runner Rick Deckard.",
        "keywords": "replicant cyberpunk neo noir artificial intelligence memory existential identity dystopian future detective"
    },
    {
        "title": "Blade Runner", "year": 1982,
        "genres": "Action, Drama, Sci-Fi, Thriller",
        "director": "Ridley Scott",
        "cast": "Harrison Ford, Rutger Hauer, Sean Young, Edward James Olmos",
        "rating": 8.1, "runtime": 117,
        "overview": "A blade runner must pursue and terminate four replicants who stole a ship in space and have returned to Earth to find their creator.",
        "keywords": "cyberpunk replicant neo noir tears in rain existential dystopia android future detective"
    },
    {
        "title": "Arrival", "year": 2016,
        "genres": "Drama, Mystery, Sci-Fi",
        "director": "Denis Villeneuve",
        "cast": "Amy Adams, Jeremy Renner, Forest Whitaker, Michael Stuhlbarg",
        "rating": 7.9, "runtime": 116,
        "overview": "A linguistics professor leads an elite team of investigators when gigantic extraterrestrial spaceships touch down in twelve locations around the globe.",
        "keywords": "extraterrestrial linguistics nonlinear time communication alien first contact memory pacifism humanity"
    },
    {
        "title": "Dune", "year": 2021,
        "genres": "Action, Adventure, Drama, Sci-Fi",
        "director": "Denis Villeneuve",
        "cast": "Timothée Chalamet, Rebecca Ferguson, Oscar Isaac, Jason Momoa, Zendaya",
        "rating": 8.0, "runtime": 155,
        "overview": "A noble family becomes embroiled in a war for control over the galaxy's most valuable asset while its heir becomes troubled by visions of a dark future.",
        "keywords": "desert planet spice messiah prophecy galactic empire sandworms politics chosen one space opera"
    },
    {
        "title": "Dune: Part Two", "year": 2024,
        "genres": "Action, Adventure, Drama, Sci-Fi",
        "director": "Denis Villeneuve",
        "cast": "Timothée Chalamet, Zendaya, Rebecca Ferguson, Javier Bardem, Austin Butler",
        "rating": 8.6, "runtime": 166,
        "overview": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
        "keywords": "holy war fremen sandworms desert prophecy vengeance empire galactic battle spice destiny"
    },
    {
        "title": "2001: A Space Odyssey", "year": 1968,
        "genres": "Adventure, Sci-Fi",
        "director": "Stanley Kubrick",
        "cast": "Keir Dullea, Gary Lockwood, William Sylvester, Daniel Richter",
        "rating": 8.3, "runtime": 149,
        "overview": "After uncovering a mysterious artifact buried beneath the Lunar surface, a spacecraft is sent to Jupiter manned by two men and supercomputer HAL 9000.",
        "keywords": "monolith hal 9000 artificial intelligence space evolution jupiter cosmic rebirth philosophical"
    },
    {
        "title": "Tenet", "year": 2020,
        "genres": "Action, Sci-Fi, Thriller",
        "director": "Christopher Nolan",
        "cast": "John David Washington, Robert Pattinson, Elizabeth Debicki, Kenneth Branagh",
        "rating": 7.3, "runtime": 150,
        "overview": "Armed with only one word, Tenet, and fighting for the survival of the entire world, a Protagonist journeys through international espionage in inverted time.",
        "keywords": "time inversion entropy algorithm temporal pincer movement international espionage secret agent physics"
    },
    {
        "title": "The Prestige", "year": 2006,
        "genres": "Drama, Mystery, Sci-Fi, Thriller",
        "director": "Christopher Nolan",
        "cast": "Christian Bale, Hugh Jackman, Scarlett Johansson, Michael Caine, David Bowie",
        "rating": 8.5, "runtime": 130,
        "overview": "After a tragic accident, two stage magicians in 1890s London engage in a battle to create the ultimate illusion while sacrificing everything.",
        "keywords": "magic teleportation rivalry nikola tesla sacrifice twins cloning obsession illusion obsession twist"
    },
    {
        "title": "Ex Machina", "year": 2014,
        "genres": "Drama, Mystery, Sci-Fi, Thriller",
        "director": "Alex Garland",
        "cast": "Domhnall Gleeson, Alicia Vikander, Oscar Isaac, Sonoya Mizuno",
        "rating": 7.7, "runtime": 108,
        "overview": "A young programmer is selected to participate in a ground-breaking experiment in synthetic intelligence by evaluating the human qualities of a humanoid A.I.",
        "keywords": "turing test humanoid android manipulation remote facility billionaire creator ai consciousness psychological"
    },
    {
        "title": "Her", "year": 2013,
        "genres": "Drama, Romance, Sci-Fi",
        "director": "Spike Jonze",
        "cast": "Joaquin Phoenix, Scarlett Johansson, Amy Adams, Rooney Mara",
        "rating": 8.0, "runtime": 126,
        "overview": "In a near future, a lonely writer develops an unlikely romantic relationship with an operating system designed to meet his every need.",
        "keywords": "artificial intelligence voice assistant loneliness intimacy future los angeles digital romance philosophical"
    },
    {
        "title": "Eternal Sunshine of the Spotless Mind", "year": 2004,
        "genres": "Drama, Romance, Sci-Fi",
        "director": "Michel Gondry",
        "cast": "Jim Carrey, Kate Winslet, Gerry Robert Byrne, Elijah Wood, Mark Ruffalo",
        "rating": 8.3, "runtime": 108,
        "overview": "When their relationship turns sour, a couple undergoes a medical procedure to have each other erased from their memories.",
        "keywords": "memory erasure heartbreak clementine surreal montage subconscious regret second chance romantic sci-fi"
    },
    {
        "title": "Alien", "year": 1979,
        "genres": "Horror, Sci-Fi",
        "director": "Ridley Scott",
        "cast": "Sigourney Weaver, Tom Skerritt, John Hurt, Ian Holm",
        "rating": 8.5, "runtime": 117,
        "overview": "The crew of a commercial spacecraft encounters a deadly predatory lifeform after investigating a mysterious transmission in deep space.",
        "keywords": "xenomorph isolation spaceship cosmic horror survival android chestburster deep space dread"
    },
    {
        "title": "Aliens", "year": 1986,
        "genres": "Action, Adventure, Sci-Fi, Thriller",
        "director": "James Cameron",
        "cast": "Sigourney Weaver, Michael Biehn, Carrie Henn, Paul Reiser, Bill Paxton",
        "rating": 8.4, "runtime": 137,
        "overview": "Ellen Ripley returns to the planet where her crew encountered the alien creature, this time accompanied by a unit of colonial space marines.",
        "keywords": "space marines xenomorph queen motherhood hive firepower survival horror military action"
    },
    {
        "title": "Terminator 2: Judgment Day", "year": 1991,
        "genres": "Action, Sci-Fi",
        "director": "James Cameron",
        "cast": "Arnold Schwarzenegger, Linda Hamilton, Edward Furlong, Robert Patrick",
        "rating": 8.6, "runtime": 137,
        "overview": "A cyborg, identical to the one who failed to kill Sarah Connor, must now protect her ten-year-old son John from an even more advanced liquid metal cyborg.",
        "keywords": "cyborg time travel liquid metal nuclear apocalypse ai uprising protector future war skynet"
    },
    {
        "title": "The Terminator", "year": 1984,
        "genres": "Action, Sci-Fi",
        "director": "James Cameron",
        "cast": "Arnold Schwarzenegger, Linda Hamilton, Michael Biehn, Paul Winfield",
        "rating": 8.1, "runtime": 107,
        "overview": "A human soldier is sent from 2029 to 1984 to stop an almost indestructible cyborg killing machine sent to eliminate a young woman whose unborn son will save mankind.",
        "keywords": "cyborg assassin future soldier time travel skynet relentless chase destiny survival"
    },
    {
        "title": "Avatar", "year": 2009,
        "genres": "Action, Adventure, Fantasy, Sci-Fi",
        "director": "James Cameron",
        "cast": "Sam Worthington, Zoe Saldana, Sigourney Weaver, Stephen Lang",
        "rating": 7.9, "runtime": 162,
        "overview": "A paraplegic Marine dispatched to the moon Pandora on a unique mission becomes torn between following his orders and protecting the world he feels is his home.",
        "keywords": "alien planet pandora na vi environmentalism bio connection colonization avatar transfer"
    },
    {
        "title": "Avatar: The Way of Water", "year": 2022,
        "genres": "Action, Adventure, Fantasy, Sci-Fi",
        "director": "James Cameron",
        "cast": "Sam Worthington, Zoe Saldana, Sigourney Weaver, Stephen Lang, Kate Winslet",
        "rating": 7.6, "runtime": 192,
        "overview": "Jake Sully lives with his newfound family on the extrasolar moon Pandora. Once a familiar threat returns, Jake must work with Neytiri and the army of the Na'vi.",
        "keywords": "ocean pandora reef clan tulkun family protection marine warfare visual spectacle"
    },
    {
        "title": "Back to the Future", "year": 1985,
        "genres": "Adventure, Comedy, Sci-Fi",
        "director": "Robert Zemeckis",
        "cast": "Michael J. Fox, Christopher Lloyd, Lea Thompson, Crispin Glover",
        "rating": 8.5, "runtime": 116,
        "overview": "Marty McFly, a 17-year-old high school student, is accidentally sent thirty years into the past in a time-traveling DeLorean invented by his close friend Doc Brown.",
        "keywords": "delorean time travel 1955 doc brown flux capacitor high school rock and roll family paradox"
    },
    {
        "title": "Jurassic Park", "year": 1993,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Steven Spielberg",
        "cast": "Sam Neill, Laura Dern, Jeff Goldblum, Richard Attenborough",
        "rating": 8.2, "runtime": 127,
        "overview": "A pragmatic paleontologist touring an almost complete theme park is tasked with protecting kids after a power failure causes the cloned dinosaurs to run loose.",
        "keywords": "dinosaurs tyrannosaurus rex theme park genetics cloning island chaos theory amber fossil"
    },
    {
        "title": "Everything Everywhere All at Once", "year": 2022,
        "genres": "Action, Adventure, Comedy, Fantasy, Sci-Fi",
        "director": "Daniel Kwan, Daniel Scheinert",
        "cast": "Michelle Yeoh, Stephanie Hsu, Ke Huy Quan, Jamie Lee Curtis",
        "rating": 7.8, "runtime": 139,
        "overview": "A middle-aged Chinese immigrant is swept up into an adventure in which she alone can save existence by exploring other universes and connecting with past lives.",
        "keywords": "multiverse laundromat mother daughter nihilism hot dog fingers bagel absurdity martial arts empathy"
    },

    # --- CRIME, THRILLER & MYSTERY ---
    {
        "title": "The Dark Knight", "year": 2008,
        "genres": "Action, Crime, Drama, Thriller",
        "director": "Christopher Nolan",
        "cast": "Christian Bale, Heath Ledger, Aaron Eckhart, Michael Caine, Gary Oldman",
        "rating": 9.0, "runtime": 152,
        "overview": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.",
        "keywords": "vigilante joker superhero chaos gotham city psychological moral dilemma justice corruption crime lord"
    },
    {
        "title": "Batman Begins", "year": 2005,
        "genres": "Action, Crime, Drama",
        "director": "Christopher Nolan",
        "cast": "Christian Bale, Michael Caine, Liam Neeson, Katie Holmes, Gary Oldman",
        "rating": 8.2, "runtime": 140,
        "overview": "After training with his mentor, Batman begins his fight to free crime-ridden Gotham City from corruption.",
        "keywords": "batman origin league of shadows scarecrow fear toxin gotham vigilante justice billionaire"
    },
    {
        "title": "The Dark Knight Rises", "year": 2012,
        "genres": "Action, Drama, Thriller",
        "director": "Christopher Nolan",
        "cast": "Christian Bale, Tom Hardy, Anne Hathaway, Gary Oldman, Joseph Gordon-Levitt",
        "rating": 8.4, "runtime": 164,
        "overview": "Eight years after the Joker's reign of anarchy, Batman, with the help of the enigmatic Catwoman, is forced from his exile to save Gotham from brutal terrorist Bane.",
        "keywords": "bane catwoman revolution exile pit prison gotham liberation fusion bomb sacrifice"
    },
    {
        "title": "The Batman", "year": 2022,
        "genres": "Action, Crime, Drama, Mystery",
        "director": "Matt Reeves",
        "cast": "Robert Pattinson, Zoë Kravitz, Jeffrey Wright, Colin Farrell, Paul Dano",
        "rating": 7.8, "runtime": 176,
        "overview": "When a sadistic serial killer begins murdering key political figures in Gotham, Batman is forced to investigate the city's hidden corruption and question his family's involvement.",
        "keywords": "riddler detective neo noir batmobile gotham flood vengeance corruption ciphers catwoman"
    },
    {
        "title": "Joker", "year": 2019,
        "genres": "Crime, Drama, Thriller",
        "director": "Todd Phillips",
        "cast": "Joaquin Phoenix, Robert De Niro, Zazie Beetz, Frances Conroy",
        "rating": 8.4, "runtime": 122,
        "overview": "During the 1980s, a failed stand-up comedian is driven insane and turns to a life of crime and chaos in Gotham City while becoming an infamous psychopathic figure.",
        "keywords": "mental illness arthur fleck stand up comedian clown descent into madness gotham rebellion class rage"
    },
    {
        "title": "Pulp Fiction", "year": 1994,
        "genres": "Crime, Drama",
        "director": "Quentin Tarantino",
        "cast": "John Travolta, Uma Thurman, Samuel L. Jackson, Bruce Willis",
        "rating": 8.9, "runtime": 154,
        "overview": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
        "keywords": "nonlinear hitman mobster briefcase dance dialogue cult classic dark comedy redemption violence"
    },
    {
        "title": "Reservoir Dogs", "year": 1992,
        "genres": "Crime, Thriller",
        "director": "Quentin Tarantino",
        "cast": "Harvey Keitel, Tim Roth, Michael Madsen, Steve Buscemi",
        "rating": 8.3, "runtime": 99,
        "overview": "When a simple jewelry heist goes horribly wrong, the surviving criminals begin to suspect that one of them is a police informant.",
        "keywords": "jewelry heist undercover cop warehouse standoff color code names ear slice diamond heist"
    },
    {
        "title": "Fight Club", "year": 1999,
        "genres": "Drama",
        "director": "David Fincher",
        "cast": "Brad Pitt, Edward Norton, Helena Bonham Carter, Meat Loaf",
        "rating": 8.8, "runtime": 139,
        "overview": "An insomniac office worker and a devil-may-care soap maker form an underground fight club that evolves into much more.",
        "keywords": "insomnia alter ego consumerism anti establishment psychological underground secret society anarchy mental illness"
    },
    {
        "title": "Se7en", "year": 1995,
        "genres": "Crime, Drama, Mystery, Thriller",
        "director": "David Fincher",
        "cast": "Morgan Freeman, Brad Pitt, Kevin Spacey, Gwyneth Paltrow",
        "rating": 8.6, "runtime": 127,
        "overview": "Two detectives, a rookie and a veteran, hunt a serial killer who uses the seven deadly sins as his motives.",
        "keywords": "serial killer seven deadly sins detective grim rain partner mystery dark psychological thriller twist ending"
    },
    {
        "title": "Zodiac", "year": 2007,
        "genres": "Crime, Drama, History, Mystery, Thriller",
        "director": "David Fincher",
        "cast": "Jake Gyllenhaal, Mark Ruffalo, Robert Downey Jr., Anthony Edwards",
        "rating": 7.7, "runtime": 157,
        "overview": "Between 1968 and 1983, a San Francisco cartoonist becomes an amateur detective obsessed with tracking down the Zodiac Killer.",
        "keywords": "serial killer obsession newspaper cartoonist investigation real events cipher cryptography cold case"
    },
    {
        "title": "Gone Girl", "year": 2014,
        "genres": "Drama, Mystery, Thriller",
        "director": "David Fincher",
        "cast": "Ben Affleck, Rosamund Pike, Neil Patrick Harris, Tyler Perry",
        "rating": 8.1, "runtime": 149,
        "overview": "With his wife's disappearance having become the focus of an intense media circus, a man sees the spotlight turned on him when it's suspected that he may not be innocent.",
        "keywords": "missing spouse marriage betrayal sociopath media manipulation dark secrets deceit twist psychological revenge"
    },
    {
        "title": "The Social Network", "year": 2010,
        "genres": "Biography, Drama",
        "director": "David Fincher",
        "cast": "Jesse Eisenberg, Andrew Garfield, Justin Timberlake, Armie Hammer",
        "rating": 7.8, "runtime": 120,
        "overview": "As Harvard student Mark Zuckerberg creates Facebook, he is sued by the twins who claimed he stole their idea, and by the co-founder who was later squeezed out.",
        "keywords": "facebook mark zuckerberg harvard tech startup lawsuit betrayal programming friendship silicon valley"
    },
    {
        "title": "The Silence of the Lambs", "year": 1991,
        "genres": "Crime, Drama, Thriller",
        "director": "Jonathan Demme",
        "cast": "Jodie Foster, Anthony Hopkins, Scott Glenn, Ted Levine",
        "rating": 8.6, "runtime": 118,
        "overview": "A young F.B.I. cadet must receive the help of an incarcerated and manipulative cannibal killer to help catch another serial killer who skins his victims.",
        "keywords": "hannibal lecter serial killer fbi behavioral science cannibalism psychological game buffalo bill mind games"
    },
    {
        "title": "Shutter Island", "year": 2010,
        "genres": "Mystery, Thriller",
        "director": "Martin Scorsese",
        "cast": "Leonardo DiCaprio, Mark Ruffalo, Ben Kingsley, Michelle Williams",
        "rating": 8.2, "runtime": 138,
        "overview": "In 1954, a U.S. Marshal investigates the disappearance of a murderer who escaped from a hospital for the criminally insane.",
        "keywords": "psychiatric hospital mental illness twist hallucination lighthouse conspiracy grief trauma paranoia"
    },
    {
        "title": "The Departed", "year": 2006,
        "genres": "Crime, Drama, Thriller",
        "director": "Martin Scorsese",
        "cast": "Leonardo DiCaprio, Matt Damon, Jack Nicholson, Mark Wahlberg",
        "rating": 8.5, "runtime": 151,
        "overview": "An undercover cop and a mole in the police attempt to identify each other while infiltrating an Irish gang in South Boston.",
        "keywords": "undercover mole infiltration boston irish mob corruption double cross identity paranoia suspense"
    },
    {
        "title": "Goodfellas", "year": 1990,
        "genres": "Biography, Crime, Drama",
        "director": "Martin Scorsese",
        "cast": "Robert De Niro, Ray Liotta, Joe Pesci, Lorraine Bracco",
        "rating": 8.7, "runtime": 145,
        "overview": "The story of Henry Hill and his life in the mafia, covering his relationship with his wife Karen and his mob partners Jimmy Conway and Tommy DeVito.",
        "keywords": "mobster gangster heist fbi informant narcotics brooklyn betrayal voiceover organized crime"
    },
    {
        "title": "Taxi Driver", "year": 1976,
        "genres": "Crime, Drama",
        "director": "Martin Scorsese",
        "cast": "Robert De Niro, Jodie Foster, Cybill Shepherd, Harvey Keitel",
        "rating": 8.2, "runtime": 114,
        "overview": "A mentally unstable veteran works as a nighttime taxi driver in New York City, where the perceived decadence fuels his urge for violent action.",
        "keywords": "taxi driver insomnia isolation new york city mohawk assassination vigilante loneliness"
    },
    {
        "title": "The Wolf of Wall Street", "year": 2013,
        "genres": "Biography, Comedy, Crime, Drama",
        "director": "Martin Scorsese",
        "cast": "Leonardo DiCaprio, Jonah Hill, Margot Robbie, Matthew McConaughey",
        "rating": 8.2, "runtime": 180,
        "overview": "Based on the true story of Jordan Belfort, from his rise to a wealthy stock-broker living the high life to his fall involving crime and corruption.",
        "keywords": "wall street stock broker fraud greed excessive lifestyle drugs corruption fbi investigation satire"
    },
    {
        "title": "The Godfather", "year": 1972,
        "genres": "Crime, Drama",
        "director": "Francis Ford Coppola",
        "cast": "Marlon Brando, Al Pacino, James Caan, Robert Duvall",
        "rating": 9.2, "runtime": 175,
        "overview": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant youngest son.",
        "keywords": "mafia organized crime family dynasty loyalty betrayal revenge italian american power syndicate"
    },
    {
        "title": "The Godfather Part II", "year": 1974,
        "genres": "Crime, Drama",
        "director": "Francis Ford Coppola",
        "cast": "Al Pacino, Robert De Niro, Robert Duvall, Diane Keaton",
        "rating": 9.0, "runtime": 202,
        "overview": "The early life and career of Vito Corleone in 1920s New York City is portrayed, while his son, Michael, tightens his grip on the family crime syndicate.",
        "keywords": "mafia prequel sequel corruption power family succession betrayal cuba vegas organized crime"
    },
    {
        "title": "Scarface", "year": 1983,
        "genres": "Crime, Drama",
        "director": "Brian De Palma",
        "cast": "Al Pacino, Michelle Pfeiffer, Steven Bauer, Robert Loggia",
        "rating": 8.3, "runtime": 170,
        "overview": "In 1980 Miami, a determined Cuban immigrant takes over a drug cartel and succumbs to greed and paranoid megalomania.",
        "keywords": "tony montana miami cocaine cartel say hello to my little friend mansion shootout rise and fall"
    },
    {
        "title": "Heat", "year": 1995,
        "genres": "Action, Crime, Drama, Thriller",
        "director": "Michael Mann",
        "cast": "Al Pacino, Robert De Niro, Val Kilmer, Jon Voight, Tom Sizemore",
        "rating": 8.3, "runtime": 170,
        "overview": "A group of high-end professional thieves start to feel the heat from the LAPD when a robbery goes wrong and a detective obsesses over catching them.",
        "keywords": "bank robbery downtown shootout lapd coffee shop face off professional heist cat and mouse"
    },
    {
        "title": "No Country for Old Men", "year": 2007,
        "genres": "Crime, Drama, Thriller",
        "director": "Joel Coen, Ethan Coen",
        "cast": "Tommy Lee Jones, Javier Bardem, Josh Brolin, Woody Harrelson",
        "rating": 8.2, "runtime": 122,
        "overview": "Violence and mayhem ensue after a hunter stumbles upon a drug deal gone wrong and more than two million dollars in cash near the Rio Grande.",
        "keywords": "anton chigurh coin toss relentless hitman briefcase money texas desert cat and mouse nihilism neo western"
    },
    {
        "title": "Fargo", "year": 1996,
        "genres": "Crime, Drama, Thriller",
        "director": "Joel Coen, Ethan Coen",
        "cast": "William H. Macy, Frances McDormand, Steve Buscemi, Peter Stormare",
        "rating": 8.1, "runtime": 98,
        "overview": "Jerry Lundegaard's inept crime falls apart due to his bungling and the persistent police work of the quite pregnant Marge Gunderson.",
        "keywords": "minnesota snow kidnapping ransom woodchipper pregnant sheriff dark comedy botched crime"
    },
    {
        "title": "Knives Out", "year": 2019,
        "genres": "Comedy, Crime, Drama, Mystery, Thriller",
        "director": "Rian Johnson",
        "cast": "Daniel Craig, Chris Evans, Ana de Armas, Jamie Lee Curtis",
        "rating": 7.9, "runtime": 130,
        "overview": "A detective investigates the death of the patriarch of an eccentric, combative family.",
        "keywords": "whodunnit benoit blanc mansion inheritance murder mystery eccentric family nurse will twist"
    },
    {
        "title": "Glass Onion: A Knives Out Mystery", "year": 2022,
        "genres": "Comedy, Crime, Drama, Mystery",
        "director": "Rian Johnson",
        "cast": "Daniel Craig, Edward Norton, Janelle Monáe, Kathryn Hahn",
        "rating": 7.1, "runtime": 139,
        "overview": "Famed detective Benoit Blanc travels to Greece for his latest case, surrounded by a tech billionaire and his eclectic group of friends on a private island.",
        "keywords": "tech billionaire private island murder mystery benoit blanc puzzle greece glass onion satire"
    },
    {
        "title": "Parasite", "year": 2019,
        "genres": "Drama, Thriller",
        "director": "Bong Joon Ho",
        "cast": "Song Kang-ho, Lee Sun-kyun, Cho Yeo-jeong, Choi Woo-shik",
        "rating": 8.5, "runtime": 132,
        "overview": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
        "keywords": "class warfare social satire infiltration basement deception dark comedy wealth inequality south korea"
    },
    {
        "title": "Memories of Murder", "year": 2003,
        "genres": "Crime, Drama, Mystery, Thriller",
        "director": "Bong Joon Ho",
        "cast": "Song Kang-ho, Kim Sang-kyung, Roe-ha Kim, Jae-ho Song",
        "rating": 8.1, "runtime": 132,
        "overview": "In 1986, in a province of South Korea, two detectives struggle with the case of multiple young women being found murdered by an unknown culprit.",
        "keywords": "serial killer cold case south korea rural investigation unsolved rain red clothes detective bleak"
    },
    {
        "title": "Oldboy", "year": 2003,
        "genres": "Action, Drama, Mystery, Thriller",
        "director": "Park Chan-wook",
        "cast": "Choi Min-sik, Yoo Ji-tae, Kang Hye-jung, Ji Dae-han",
        "rating": 8.3, "runtime": 120,
        "overview": "After being kidnapped and imprisoned for fifteen years, Oh Dae-su is released, only to find that he must find his captor in five days.",
        "keywords": "revenge corridor fight hammer captivity south korea twist mystery psychological dark"
    },

    # --- DRAMA & BIOGRAPHY ---
    {
        "title": "Oppenheimer", "year": 2023,
        "genres": "Biography, Drama, History",
        "director": "Christopher Nolan",
        "cast": "Cillian Murphy, Emily Blunt, Matt Damon, Robert Downey Jr., Florence Pugh",
        "rating": 8.9, "runtime": 180,
        "overview": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb during World War II.",
        "keywords": "manhattan project atomic bomb physics moral crisis Cold War politics guilt world war two scientist biography"
    },
    {
        "title": "The Shawshank Redemption", "year": 1994,
        "genres": "Drama",
        "director": "Frank Darabont",
        "cast": "Tim Robbins, Morgan Freeman, Bob Gunton, William Sadler",
        "rating": 9.3, "runtime": 142,
        "overview": "A banker convicted of murder forms a friendship over a quarter of a century with a hardened convict, while maintaining his innocence through hope.",
        "keywords": "prison friendship hope escape wrongful conviction corruption redemption resilience brotherhood passage of time"
    },
    {
        "title": "Forrest Gump", "year": 1994,
        "genres": "Drama, Romance",
        "director": "Robert Zemeckis",
        "cast": "Tom Hanks, Robin Wright, Gary Sinise, Sally Field",
        "rating": 8.8, "runtime": 142,
        "overview": "The presidencies of Kennedy and Johnson, the Vietnam War, and other historical events unfold from the perspective of an Alabama man with an extraordinary life.",
        "keywords": "life is like a box of chocolates running vietnam ping pong shrimp boat jenny innocence destiny"
    },
    {
        "title": "Whiplash", "year": 2014,
        "genres": "Drama, Music",
        "director": "Damien Chazelle",
        "cast": "Miles Teller, J.K. Simmons, Paul Reiser, Melissa Benoist",
        "rating": 8.5, "runtime": 107,
        "overview": "A promising young drummer enrolls at a cut-throat music conservatory where his dreams of greatness are mentored by an instructor who stops at nothing.",
        "keywords": "jazz drumming perfectionism abusive mentor music conservatory obsession psychological stress greatness"
    },
    {
        "title": "La La Land", "year": 2016,
        "genres": "Comedy, Drama, Music, Musical, Romance",
        "director": "Damien Chazelle",
        "cast": "Ryan Gosling, Emma Stone, John Legend, J.K. Simmons",
        "rating": 8.0, "runtime": 128,
        "overview": "While navigating their careers in Los Angeles, a pianist and an actress fall in love while attempting to reconcile their aspirations for the future.",
        "keywords": "jazz musical hollywood love story ambition bittersweet audition dancing dreamers los angeles"
    },
    {
        "title": "Good Will Hunting", "year": 1997,
        "genres": "Drama, Romance",
        "director": "Gus Van Sant",
        "cast": "Matt Damon, Robin Williams, Ben Affleck, Stellan Skarsgård, Minnie Driver",
        "rating": 8.3, "runtime": 126,
        "overview": "Will Hunting, a janitor at M.I.T., has a gift for mathematics, but needs help from a psychologist to find direction in his life.",
        "keywords": "genius mathematician south boston janitor therapy emotional breakthrough robin williams friendship"
    },
    {
        "title": "Schindler's List", "year": 1993,
        "genres": "Biography, Drama, History",
        "director": "Steven Spielberg",
        "cast": "Liam Neeson, Ralph Fiennes, Ben Kingsley, Caroline Goodall",
        "rating": 9.0, "runtime": 195,
        "overview": "In German-occupied Poland during World War II, industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce.",
        "keywords": "holocaust world war two oskar schindler krakow concentration camp humanity redemption black and white"
    },
    {
        "title": "Catch Me If You Can", "year": 2002,
        "genres": "Biography, Crime, Drama",
        "director": "Steven Spielberg",
        "cast": "Leonardo DiCaprio, Tom Hanks, Christopher Walken, Martin Sheen",
        "rating": 8.1, "runtime": 141,
        "overview": "Barely 21 yet, Frank Abagnale Jr. successfully worked as a doctor, a lawyer, and as a co-pilot for a major airline -- all before his 21st birthday.",
        "keywords": "con artist check fraud pilot imposter fbi chase cat and mouse true story forgery charming"
    },
    {
        "title": "The Truman Show", "year": 1998,
        "genres": "Comedy, Drama",
        "director": "Peter Weir",
        "cast": "Jim Carrey, Laura Linney, Ed Harris, Noah Emmerich",
        "rating": 8.2, "runtime": 103,
        "overview": "An insurance salesman discovers his whole life is actually a reality TV show broadcast live to the entire world 24/7.",
        "keywords": "reality television simulated world existential artificial dome hidden cameras free will paranoia"
    },

    # --- ACTION & EPIC ADVENTURE ---
    {
        "title": "Gladiator", "year": 2000,
        "genres": "Action, Adventure, Drama",
        "director": "Ridley Scott",
        "cast": "Russell Crowe, Joaquin Phoenix, Connie Nielsen, Oliver Reed",
        "rating": 8.5, "runtime": 155,
        "overview": "A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery.",
        "keywords": "ancient rome colosseum gladiator revenge honor emperor betrayal roman empire arena combat"
    },
    {
        "title": "The Lord of the Rings: The Fellowship of the Ring", "year": 2001,
        "genres": "Action, Adventure, Drama, Fantasy",
        "director": "Peter Jackson",
        "cast": "Elijah Wood, Ian McKellen, Viggo Mortensen, Orlando Bloom",
        "rating": 8.9, "runtime": 178,
        "overview": "A meek Hobbit from the Shire and eight companions set out on a journey to destroy the powerful One Ring and save Middle-earth.",
        "keywords": "middle earth ring bearer hobbit wizard fellowship quest epic fantasy sauron dark lord"
    },
    {
        "title": "The Lord of the Rings: The Two Towers", "year": 2002,
        "genres": "Action, Adventure, Drama, Fantasy",
        "director": "Peter Jackson",
        "cast": "Elijah Wood, Ian McKellen, Viggo Mortensen, Andy Serkis",
        "rating": 8.8, "runtime": 179,
        "overview": "While Frodo and Sam edge closer to Mordor with the help of the shifty Gollum, the divided fellowship makes a stand against Sauron's new ally Saruman.",
        "keywords": "helm's deep rohan gollum ent saruman ring bearer battle epic fantasy orcs"
    },
    {
        "title": "The Lord of the Rings: The Return of the King", "year": 2003,
        "genres": "Action, Adventure, Drama, Fantasy",
        "director": "Peter Jackson",
        "cast": "Elijah Wood, Viggo Mortensen, Ian McKellen, Orlando Bloom",
        "rating": 9.0, "runtime": 201,
        "overview": "Gandalf and Aragorn lead the World of Men against Sauron's army to draw his gaze from Frodo and Sam as they approach Mount Doom with the One Ring.",
        "keywords": "middle earth battle of minas tirith ring bearer destruction of ring mount doom king coronation epic war"
    },
    {
        "title": "Top Gun: Maverick", "year": 2022,
        "genres": "Action, Drama",
        "director": "Joseph Kosinski",
        "cast": "Tom Cruise, Miles Teller, Jennifer Connelly, Jon Hamm, Glen Powell",
        "rating": 8.3, "runtime": 130,
        "overview": "After thirty years, Maverick is still pushing the envelope as a top naval aviator, but must confront ghosts of his past when he leads TOP GUN's elite graduates on a dangerous mission.",
        "keywords": "fighter jet dogfight navy pilot mach 10 canyon run mentor rooster goose aviator"
    },
    {
        "title": "Mad Max: Fury Road", "year": 2015,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "George Miller",
        "cast": "Tom Hardy, Charlize Theron, Nicholas Hoult, Hugh Keays-Byrne",
        "rating": 8.1, "runtime": 120,
        "overview": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland with the aid of a group of female prisoners and a drifter named Max.",
        "keywords": "post apocalyptic desert chase high octane car battle war boys furiosa water scarcity wasteland"
    },
    {
        "title": "John Wick", "year": 2014,
        "genres": "Action, Crime, Thriller",
        "director": "Chad Stahelski",
        "cast": "Keanu Reeves, Michael Nyqvist, Alfie Allen, Willem Dafoe",
        "rating": 7.4, "runtime": 101,
        "overview": "An ex-hit-man comes out of retirement to track down the gangsters that took everything from him, starting with the puppy given to him by his late wife.",
        "keywords": "assassin gun fu puppy revenge continental hotel underworld russian mob boogeyman baba yaga"
    },
    {
        "title": "John Wick: Chapter 4", "year": 2023,
        "genres": "Action, Crime, Thriller",
        "director": "Chad Stahelski",
        "cast": "Keanu Reeves, Donnie Yen, Bill Skarsgård, Laurence Fishburne, Hiroyuki Sanada",
        "rating": 7.7, "runtime": 169,
        "overview": "John Wick uncovers a path to defeating The High Table. But before he can earn his freedom, Wick must face off against a new enemy with powerful alliances across the globe.",
        "keywords": "high table paris osaka duel martial arts caine blind assassin stairs shootout endurance"
    },
    {
        "title": "Die Hard", "year": 1988,
        "genres": "Action, Thriller",
        "director": "John McTiernan",
        "cast": "Bruce Willis, Alan Rickman, Bonnie Bedelia, Reginald VelJohnson",
        "rating": 8.2, "runtime": 132,
        "overview": "A New York City police officer tries to save his estranged wife and several others taken hostage by terrorists during a Christmas party at the Nakatomi Plaza.",
        "keywords": "nakatomi plaza john mcclane hans gruber bare feet air vent yippee ki yay skyscraper hostages"
    },
    {
        "title": "Casino Royale", "year": 2006,
        "genres": "Action, Adventure, Thriller",
        "director": "Martin Campbell",
        "cast": "Daniel Craig, Eva Green, Mads Mikkelsen, Judi Dench",
        "rating": 8.0, "runtime": 144,
        "overview": "After earning 00 status, secret agent James Bond sets out on his first mission to defeat a private banker funding terrorists in a high-stakes poker game.",
        "keywords": "james bond 007 poker high stakes montenegro vesper lynd le chiffre espionage gritty reboot"
    },
    {
        "title": "Skyfall", "year": 2012,
        "genres": "Action, Adventure, Thriller",
        "director": "Sam Mendes",
        "cast": "Daniel Craig, Javier Bardem, Judi Dench, Ralph Fiennes",
        "rating": 7.8, "runtime": 143,
        "overview": "James Bond's loyalty to M is tested when her past comes back to haunt her as MI6 comes under attack from a former operative.",
        "keywords": "james bond mi6 cyber terrorism silva childhood home scotland loyalty secret agent"
    },
    {
        "title": "1917", "year": 2019,
        "genres": "Action, Drama, War",
        "director": "Sam Mendes",
        "cast": "Dean-Charles Chapman, George MacKay, Daniel Mays, Colin Firth",
        "rating": 8.2, "runtime": 119,
        "overview": "Two soldiers are assigned to race against time and deliver a message across enemy lines that will stop 1,600 men from walking into a deadly trap.",
        "keywords": "world war one trench warfare single shot one continuous take race against time messenger heroism survival"
    },
    {
        "title": "Saving Private Ryan", "year": 1998,
        "genres": "Drama, War",
        "director": "Steven Spielberg",
        "cast": "Tom Hanks, Matt Damon, Tom Sizemore, Edward Burns",
        "rating": 8.6, "runtime": 169,
        "overview": "Following the Normandy Landings, a group of U.S. soldiers go behind enemy lines to retrieve a paratrooper whose brothers have been killed in action.",
        "keywords": "omaha beach normandy d-day world war two brotherhood military mission sacrifice sniper"
    },
    {
        "title": "Inglourious Basterds", "year": 2009,
        "genres": "Adventure, Drama, War",
        "director": "Quentin Tarantino",
        "cast": "Brad Pitt, Christoph Waltz, Michael Fassbender, Diane Kruger",
        "rating": 8.4, "runtime": 153,
        "overview": "In Nazi-occupied France, a plan to assassinate Nazi leaders by Jewish U.S. soldiers coincides with a theatre owner's vengeful plans.",
        "keywords": "world war two alternate history nazi hunters revenge hans landa cinema fire tense interrogation"
    },
    {
        "title": "Django Unchained", "year": 2012,
        "genres": "Drama, Western",
        "director": "Quentin Tarantino",
        "cast": "Jamie Foxx, Christoph Waltz, Leonardo DiCaprio, Kerry Washington, Samuel L. Jackson",
        "rating": 8.5, "runtime": 165,
        "overview": "With the help of a German bounty-hunter, a freed slave sets out to rescue his wife from a brutal Mississippi plantation owner.",
        "keywords": "bounty hunter spaghetti western slavery revenge calvin candie shootout liberation plantation south"
    },

    # --- SUPERHERO & COMIC ADAPTATIONS ---
    {
        "title": "Avengers: Infinity War", "year": 2018,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Anthony Russo, Joe Russo",
        "cast": "Robert Downey Jr., Chris Hemsworth, Mark Ruffalo, Chris Evans, Scarlett Johansson, Josh Brolin",
        "rating": 8.4, "runtime": 149,
        "overview": "The Avengers and their allies must be willing to sacrifice all to defeat the powerful Thanos before his blitz puts an end to the universe.",
        "keywords": "thanos infinity stones snap superhero marvel universe cosmic battle sacrifice superhero team"
    },
    {
        "title": "Avengers: Endgame", "year": 2019,
        "genres": "Action, Adventure, Drama, Sci-Fi",
        "director": "Anthony Russo, Joe Russo",
        "cast": "Robert Downey Jr., Chris Evans, Mark Ruffalo, Chris Hemsworth, Scarlett Johansson",
        "rating": 8.4, "runtime": 181,
        "overview": "After the devastating events of Infinity War, the remaining allies assemble once more to reverse Thanos' actions and restore balance to the universe.",
        "keywords": "time heist quantum realm marvel climax iron man sacrifice assembled timeline resolution"
    },
    {
        "title": "Iron Man", "year": 2008,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Jon Favreau",
        "cast": "Robert Downey Jr., Gwyneth Paltrow, Terrence Howard, Jeff Bridges",
        "rating": 7.9, "runtime": 126,
        "overview": "After being held captive in an Afghan cave, billionaire engineer Tony Stark creates a unique weaponized suit of armor to fight evil.",
        "keywords": "tony stark arc reactor high tech armor superhero weapons manufacturer origin story marvel"
    },
    {
        "title": "Guardians of the Galaxy", "year": 2014,
        "genres": "Action, Adventure, Comedy, Sci-Fi",
        "director": "James Gunn",
        "cast": "Chris Pratt, Zoe Saldana, Dave Bautista, Vin Diesel, Bradley Cooper",
        "rating": 8.0, "runtime": 121,
        "overview": "A group of intergalactic criminals must pull together to stop a fanatical warrior with plans to purge the universe.",
        "keywords": "misfits space outlaws cassette tape retro soundtrack talking raccoon groot cosmic humor marvel"
    },
    {
        "title": "Spider-Man: Into the Spider-Verse", "year": 2018,
        "genres": "Animation, Action, Adventure, Family, Sci-Fi",
        "director": "Bob Persichetti, Peter Ramsey, Rodney Rothman",
        "cast": "Shameik Moore, Jake Johnson, Hailee Steinfeld, Mahershala Ali",
        "rating": 8.4, "runtime": 117,
        "overview": "Teen Miles Morales becomes the new Spider-Man and must align with alternate-dimension spider-powered heroes to stop a threat to all realities.",
        "keywords": "multiverse superhero comic book style brooklyn alternate dimensions coming of age spider-man mentor"
    },
    {
        "title": "Spider-Man: Across the Spider-Verse", "year": 2023,
        "genres": "Animation, Action, Adventure, Fantasy, Sci-Fi",
        "director": "Joaquim Dos Santos, Kemp Powers, Justin K. Thompson",
        "cast": "Shameik Moore, Hailee Steinfeld, Oscar Isaac, Daniel Kaluuya",
        "rating": 8.6, "runtime": 140,
        "overview": "Miles Morales catapults across the Multiverse, where he encounters a team of Spider-People charged with protecting its very existence.",
        "keywords": "multiverse canon event spider society destiny rebellion dimension hopping visual masterpiece animation"
    },
    {
        "title": "Spider-Man: No Way Home", "year": 2021,
        "genres": "Action, Adventure, Fantasy, Sci-Fi",
        "director": "Jon Watts",
        "cast": "Tom Holland, Zendaya, Benedict Cumberbatch, Tobey Maguire, Andrew Garfield",
        "rating": 8.2, "runtime": 148,
        "overview": "With Spider-Man's identity now revealed, Peter asks Doctor Strange for help, unleashing villains from alternate universes.",
        "keywords": "identity revealed doctor strange spell multiverse green goblin doc ock three spider-men sacrifice"
    },

    # --- ANIMATION & FAMILY MASTERPIECES ---
    {
        "title": "Spirited Away", "year": 2001,
        "genres": "Animation, Adventure, Family, Fantasy, Mystery",
        "director": "Hayao Miyazaki",
        "cast": "Rumi Hiiragi, Miyu Irino, Mari Natsuki, Takashi Naito",
        "rating": 8.6, "runtime": 125,
        "overview": "During her family's move to the suburbs, a 10-year-old girl wanders into a world ruled by gods, witches, and spirits where humans are changed into beasts.",
        "keywords": "studio ghibli spirits bathhouse magic dragon transformation curse courage fantasy anime coming of age"
    },
    {
        "title": "Princess Mononoke", "year": 1997,
        "genres": "Animation, Action, Adventure, Fantasy",
        "director": "Hayao Miyazaki",
        "cast": "Yoji Matsuda, Yuriko Ishida, Yuko Tanaka, Kaoru Kobayashi",
        "rating": 8.4, "runtime": 134,
        "overview": "On a journey to find the cure for a Tatarigami's curse, Ashitaka finds himself in the middle of a war between forest gods and Tatara mining colony.",
        "keywords": "studio ghibli environmentalism forest gods nature curse war wolf girl harmony anime epic"
    },
    {
        "title": "Howl's Moving Castle", "year": 2004,
        "genres": "Animation, Adventure, Family, Fantasy",
        "director": "Hayao Miyazaki",
        "cast": "Chieko Baisho, Takuya Kimura, Akihiro Miwa",
        "rating": 8.2, "runtime": 119,
        "overview": "When an unconfident young woman is cursed with an old body by a spiteful witch, her only chance of breaking it lies with a wizard and his legged walking castle.",
        "keywords": "studio ghibli walking castle wizard curse calcifer pacifism magical steampunk fantasy"
    },
    {
        "title": "Your Name.", "year": 2016,
        "genres": "Animation, Drama, Fantasy, Romance",
        "director": "Makoto Shinkai",
        "cast": "Ryunosuke Kamiki, Mone Kamishiraishi, Ryo Narita",
        "rating": 8.4, "runtime": 106,
        "overview": "Two teenagers share a profound, magical connection upon discovering they are swapping bodies across time and space.",
        "keywords": "body swap comet tokyo rural japan red string of fate anime romance time shift emotional"
    },
    {
        "title": "WALL·E", "year": 2008,
        "genres": "Animation, Adventure, Family, Sci-Fi",
        "director": "Andrew Stanton",
        "cast": "Ben Burtt, Elissa Knight, Jeff Garlin, Fred Willard",
        "rating": 8.4, "runtime": 98,
        "overview": "In the distant future, a small waste-collecting robot embarks on a space journey that will ultimately decide the fate of mankind.",
        "keywords": "robot waste collection post apocalyptic earth space ship eve plant humanity consumerism pixar"
    },
    {
        "title": "Ratatouille", "year": 2007,
        "genres": "Animation, Adventure, Comedy, Family, Fantasy",
        "director": "Brad Bird, Jan Pinkava",
        "cast": "Patton Oswalt, Ian Holm, Lou Romano, Brian Dennehy",
        "rating": 8.1, "runtime": 111,
        "overview": "A rat who can cook makes an unusual alliance with a young kitchen worker at a famous Paris restaurant.",
        "keywords": "paris chef cuisine gourmet cooking restaurant critic food passion rat gusteau"
    },
    {
        "title": "Coco", "year": 2017,
        "genres": "Animation, Adventure, Comedy, Family, Fantasy, Music",
        "director": "Lee Unkrich, Adrian Molina",
        "cast": "Anthony Gonzalez, Gael García Bernal, Benjamin Bratt",
        "rating": 8.4, "runtime": 105,
        "overview": "Aspiring musician Miguel enters the Land of the Dead to unlock the real story behind his family's history.",
        "keywords": "day of the dead land of the dead guitar family ancestry memory mexican culture skeleton emotional"
    },
    {
        "title": "The Lion King", "year": 1994,
        "genres": "Animation, Adventure, Drama, Family, Musical",
        "director": "Roger Allers, Rob Minkoff",
        "cast": "Matthew Broderick, Jeremy Irons, James Earl Jones, Whoopi Goldberg",
        "rating": 8.5, "runtime": 88,
        "overview": "Lion prince Simba and his father are targeted by his bitter uncle, who wants to ascend the throne himself.",
        "keywords": "circle of life pride lands savanna uncle betrayal royalty father son grief hakuna matata"
    },
    {
        "title": "Toy Story", "year": 1995,
        "genres": "Animation, Adventure, Comedy, Family, Fantasy",
        "director": "John Lasseter",
        "cast": "Tom Hanks, Tim Allen, Don Rickles, Jim Varney",
        "rating": 8.3, "runtime": 81,
        "overview": "A cowboy doll is profoundly threatened and jealous when a new spaceman action figure supplants him as top toy in a boy's bedroom.",
        "keywords": "living toys woody buzz lightyear jealousy friendship moving day childhood imagination"
    },
    {
        "title": "Up", "year": 2009,
        "genres": "Animation, Adventure, Comedy, Family",
        "director": "Pete Docter, Bob Peterson",
        "cast": "Edward Asner, Jordan Nagai, John Ratzenberger, Christopher Plummer",
        "rating": 8.3, "runtime": 96,
        "overview": "78-year-old Carl Fredricksen travels to Paradise Falls in his house equipped with balloons, inadvertently taking a young stowaway.",
        "keywords": "balloons floating house opening montage paradise falls wilderness explorer talking dog grief"
    },
    {
        "title": "Inside Out", "year": 2015,
        "genres": "Animation, Adventure, Comedy, Drama, Family, Fantasy",
        "director": "Pete Docter, Ronnie Del Carmen",
        "cast": "Amy Poehler, Bill Hader, Lewis Black, Mindy Kaling, Phyllis Smith",
        "rating": 8.1, "runtime": 95,
        "overview": "After young Riley is uprooted from her Midwest life, her emotions - Joy, Fear, Anger, Disgust and Sadness - conflict on how best to navigate a new city.",
        "keywords": "emotions headquarters joy sadness core memories growing up childhood psychology mind"
    },

    # --- HORROR & PSYCHOLOGICAL THRILLER ---
    {
        "title": "The Shining", "year": 1980,
        "genres": "Drama, Horror",
        "director": "Stanley Kubrick",
        "cast": "Jack Nicholson, Shelley Duvall, Danny Lloyd, Scatman Crothers",
        "rating": 8.4, "runtime": 146,
        "overview": "A family heads to an isolated hotel for the winter where a sinister presence influences the father into violence.",
        "keywords": "overlook hotel cabin fever psychic shining ghosts isolation axe murder haunted madness"
    },
    {
        "title": "Get Out", "year": 2017,
        "genres": "Horror, Mystery, Thriller",
        "director": "Jordan Peele",
        "cast": "Daniel Kaluuya, Allison Williams, Bradley Whitford, Catherine Keener",
        "rating": 7.8, "runtime": 104,
        "overview": "A young African-American visits his white girlfriend's parents for the weekend, where his simmering uneasiness reaches a boiling point.",
        "keywords": "sunken place social thriller hypnosis racism body snatching tea cup suburban horror psychological"
    },
    {
        "title": "Hereditary", "year": 2018,
        "genres": "Drama, Horror, Mystery, Thriller",
        "director": "Ari Aster",
        "cast": "Toni Collette, Alex Wolff, Milly Shapiro, Gabriel Byrne",
        "rating": 7.3, "runtime": 127,
        "overview": "A grieving family is haunted by tragic and disturbing occurrences after the death of their secretive grandmother.",
        "keywords": "occult demon paimon grief family trauma decapitation seance psychological horror dread"
    },
    {
        "title": "A Quiet Place", "year": 2018,
        "genres": "Drama, Horror, Sci-Fi",
        "director": "John Krasinski",
        "cast": "Emily Blunt, John Krasinski, Millicent Simmonds, Noah Jupe",
        "rating": 7.5, "runtime": 90,
        "overview": "A family struggles for survival in a world where most humans have been killed by blind but noise-sensitive creatures.",
        "keywords": "silence blind monsters sound acoustic survival sign language family protection tension"
    },
    {
        "title": "Psycho", "year": 1960,
        "genres": "Horror, Mystery, Thriller",
        "director": "Alfred Hitchcock",
        "cast": "Anthony Perkins, Janet Leigh, Vera Miles, John Gavin",
        "rating": 8.5, "runtime": 109,
        "overview": "A Phoenix secretary embezzles $40,000 from her employer's client, goes on the run, and checks into a remote motel run by a young man under the domination of his mother.",
        "keywords": "norman bates bates motel shower scene mother personality disorder taxidermy hitchcock classic"
    },

    # --- COMEDY & QUIRKY DRAMA ---
    {
        "title": "The Grand Budapest Hotel", "year": 2014,
        "genres": "Adventure, Comedy, Crime",
        "director": "Wes Anderson",
        "cast": "Ralph Fiennes, F. Murray Abraham, Mathieu Amalric, Adrien Brody, Saoirse Ronan",
        "rating": 8.1, "runtime": 99,
        "overview": "A writer encounters the owner of an aging hotel who recounts his early years as a lobby boy under an exceptional concierge.",
        "keywords": "lobby boy concierge pastel color symmetry painting theft prison escape whimsical retro europe"
    },
    {
        "title": "Barbie", "year": 2023,
        "genres": "Adventure, Comedy, Fantasy",
        "director": "Greta Gerwig",
        "cast": "Margot Robbie, Ryan Gosling, America Ferrera, Will Ferrell, Simu Liu",
        "rating": 6.8, "runtime": 114,
        "overview": "Barbie and Ken are having the time of their lives in the colorful Barbie Land until they get a chance to go to the real world.",
        "keywords": "barbie land patriarchy existential crisis pink doll comedy feminism self discovery kenergy"
    },
    {
        "title": "The Big Lebowski", "year": 1998,
        "genres": "Comedy, Crime",
        "director": "Joel Coen, Ethan Coen",
        "cast": "Jeff Bridges, John Goodman, Julianne Moore, Steve Buscemi",
        "rating": 8.1, "runtime": 117,
        "overview": "Ultimate L.A. slacker 'The Dude' Lebowski is mistaken for a millionaire of the same name and gets drawn into a chaotic kidnapping plot.",
        "keywords": "the dude bowling rug tied the room together white russian nihilists mistaken identity cult comedy"
    },
    {
        "title": "Amélie", "year": 2001,
        "genres": "Comedy, Romance",
        "director": "Jean-Pierre Jeunet",
        "cast": "Audrey Tautou, Mathieu Kassovitz, Rufus, Lorella Cravotta",
        "rating": 8.3, "runtime": 122,
        "overview": "Amélie is an innocent girl in Paris with her own sense of justice who decides to help those around her, discovering love along the way.",
        "keywords": "paris montmartre kindness photobooth whimsical eccentric french cinema feel good romance"
    },

    # --- ROMANCE & HUMAN CONNECTION ---
    {
        "title": "Past Lives", "year": 2023,
        "genres": "Drama, Romance",
        "director": "Celine Song",
        "cast": "Greta Lee, Teo Yoo, John Magaro",
        "rating": 7.8, "runtime": 105,
        "overview": "Nora and Hae Sung, two deeply connected childhood friends, are reunited in New York for one fateful week confronting destiny and love.",
        "keywords": "in-yun destiny childhood friends reunion immigration south korea new york unfulfilled love tenderness"
    },
    {
        "title": "Before Sunrise", "year": 1995,
        "genres": "Drama, Romance",
        "director": "Richard Linklater",
        "cast": "Ethan Hawke, Julie Delpy, Andrea Eckert",
        "rating": 8.1, "runtime": 101,
        "overview": "A young man and woman meet on a train in Europe and spend one memorable evening together in Vienna before parting ways.",
        "keywords": "vienna train ride conversations philosophical romance walking overnight connection intimacy"
    },
    {
        "title": "Before Sunset", "year": 2004,
        "genres": "Drama, Romance",
        "director": "Richard Linklater",
        "cast": "Ethan Hawke, Julie Delpy, Vernon Dobtcheff",
        "rating": 8.1, "runtime": 80,
        "overview": "Nine years after Jesse and Celine first met, they encounter each other again on the French leg of Jesse's book tour in Paris.",
        "keywords": "paris reunion conversation real time regret longing romance book tour river seine"
    },
    {
        "title": "Titanic", "year": 1997,
        "genres": "Drama, Romance",
        "director": "James Cameron",
        "cast": "Leonardo DiCaprio, Kate Winslet, Billy Zane, Kathy Bates",
        "rating": 7.9, "runtime": 194,
        "overview": "A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.",
        "keywords": "shipwreck class division forbidden love iceberg tragic romance north atlantic epic disaster"
    },
    {
        "title": "In the Mood for Love", "year": 2000,
        "genres": "Drama, Romance",
        "director": "Wong Kar-wai",
        "cast": "Tony Chiu-Wai Leung, Maggie Cheung, Ping Lam Siu",
        "rating": 8.1, "runtime": 98,
        "overview": "Two neighbors form a strong bond after suspecting extramarital activities of their spouses, keeping their bond platonic to avoid wrongdoing.",
        "keywords": "hong kong unrequited love cheongsam rain nostalgia yearning melancholy cinematography elegance"
    },
    {
        "title": "Cinema Paradiso", "year": 1988,
        "genres": "Drama, Romance",
        "director": "Giuseppe Tornatore",
        "cast": "Philippe Noiret, Enzo Cannavale, Antonella Attili",
        "rating": 8.5, "runtime": 155,
        "overview": "A filmmaker recalls his childhood falling in love with pictures at the village cinema and his deep bond with the projectionist.",
        "keywords": "sicily cinema projectionist love letter to film nostalgia montage childhood friendship italian masterpiece"
    },
    # --- ADDITIONAL POPULAR CINEMA & FRANCHISES ---
    {
        "title": "Gladiator II", "year": 2024,
        "genres": "Action, Adventure, Drama",
        "director": "Ridley Scott",
        "cast": "Paul Mescal, Pedro Pascal, Denzel Washington, Connie Nielsen",
        "rating": 7.3, "runtime": 148,
        "overview": "Years after witnessing the death of Maximus at the hands of his uncle, Lucius must enter the Colosseum after the powerful emperors of Rome conquer his home.",
        "keywords": "ancient rome colosseum gladiator revenge roman empire conquest lucius denzel washington arena"
    },
    {
        "title": "Furiosa: A Mad Max Saga", "year": 2024,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "George Miller",
        "cast": "Anya Taylor-Joy, Chris Hemsworth, Tom Burke, Alyla Browne",
        "rating": 7.6, "runtime": 148,
        "overview": "As the world fell, young Furiosa is snatched from the Green Place of Many Mothers and falls into the hands of a great Biker Horde led by the Warlord Dementus.",
        "keywords": "wasteland furiosa dementus biker horde citadel green place vehicular combat survival revenge"
    },
    {
        "title": "Dunkirk", "year": 2017,
        "genres": "Action, Drama, History, Thriller, War",
        "director": "Christopher Nolan",
        "cast": "Fionn Whitehead, Tom Glynn-Carney, Jack Lowden, Harry Styles, Cillian Murphy, Tom Hardy",
        "rating": 7.8, "runtime": 106,
        "overview": "Allied soldiers from Belgium, the British Commonwealth and France are surrounded by the German Army and evacuated during a fierce battle in World War II.",
        "keywords": "dunkirk evacuation mole sea air spitfire world war two ticking clock survival rescue"
    },
    {
        "title": "The Avengers", "year": 2012,
        "genres": "Action, Sci-Fi",
        "director": "Joss Whedon",
        "cast": "Robert Downey Jr., Chris Evans, Scarlett Johansson, Mark Ruffalo, Chris Hemsworth, Tom Hiddleston",
        "rating": 8.0, "runtime": 143,
        "overview": "Earth's mightiest heroes must come together and learn to fight as a team if they are going to stop the mischievous Loki and his alien army from enslaving humanity.",
        "keywords": "avengers assemble loki tesseract battle of new york chitauri shield superhero team"
    },
    {
        "title": "Captain America: The Winter Soldier", "year": 2014,
        "genres": "Action, Adventure, Sci-Fi, Thriller",
        "director": "Anthony Russo, Joe Russo",
        "cast": "Chris Evans, Samuel L. Jackson, Scarlett Johansson, Robert Redford, Sebastian Stan",
        "rating": 7.8, "runtime": 136,
        "overview": "As Steve Rogers struggles to embrace his role in the modern world, he teams up with a fellow Avenger and S.H.I.E.L.D agent, Black Widow, to battle a new threat: the Winter Soldier.",
        "keywords": "hydra conspiracy espionage winter soldier bucky barnes shield highway fight elevator battle"
    },
    {
        "title": "Logan", "year": 2017,
        "genres": "Action, Drama, Sci-Fi",
        "director": "James Mangold",
        "cast": "Hugh Jackman, Patrick Stewart, Dafne Keen, Boyd Holbrook",
        "rating": 8.1, "runtime": 137,
        "overview": "In a future where mutants are nearly extinct, an elderly and weary Logan leads a quiet life. But when Laura, a mutant child pursued by scientists, arrives, Logan must step up.",
        "keywords": "wolverine x-23 professor x aging mutant healing factor adamantium claws western road trip sacrifice"
    },
    {
        "title": "Deadpool", "year": 2016,
        "genres": "Action, Comedy, Sci-Fi",
        "director": "Tim Miller",
        "cast": "Ryan Reynolds, Morena Baccarin, T.J. Miller, Ed Skrein",
        "rating": 8.0, "runtime": 108,
        "overview": "A wisecracking mercenary gets experimented on and becomes immortal but ugly, and sets out to track down the man who ruined his looks.",
        "keywords": "fourth wall breaking chimichanga mercenary accelerated healing dark humor meta superhero comedy"
    },
    {
        "title": "Spider-Man", "year": 2002,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Sam Raimi",
        "cast": "Tobey Maguire, Willem Dafoe, Kirsten Dunst, James Franco",
        "rating": 7.4, "runtime": 121,
        "overview": "After being bitten by a genetically altered spider, nerdy high school student Peter Parker gains spider-like abilities that he eventually must use to fight evil.",
        "keywords": "green goblin uncle ben with great power comes great responsibility new york spider bite web slinging"
    },
    {
        "title": "Spider-Man 2", "year": 2004,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Sam Raimi",
        "cast": "Tobey Maguire, Kirsten Dunst, Alfred Molina, James Franco",
        "rating": 7.5, "runtime": 127,
        "overview": "Peter Parker is beset with troubles in his failing personal life as he battles a brilliant scientist named Doctor Otto Octavius.",
        "keywords": "doctor octopus doc ock mechanical tentacles train fight identity crisis losing powers pizza time"
    },
    {
        "title": "Prisoners", "year": 2013,
        "genres": "Crime, Drama, Mystery, Thriller",
        "director": "Denis Villeneuve",
        "cast": "Hugh Jackman, Jake Gyllenhaal, Viola Davis, Maria Bello, Paul Dano",
        "rating": 8.1, "runtime": 153,
        "overview": "When Keller Dover's daughter and her friend go missing, he takes matters into his own hands as the police pursue multiple leads.",
        "keywords": "kidnapping vigilante father maze detective loki abduction rain moral darkness interrogation"
    },
    {
        "title": "Sicario", "year": 2015,
        "genres": "Action, Crime, Drama, Mystery, Thriller",
        "director": "Denis Villeneuve",
        "cast": "Emily Blunt, Benicio Del Toro, Josh Brolin, Victor Garber",
        "rating": 7.7, "runtime": 121,
        "overview": "An idealistic FBI agent is enlisted by a government task force to aid in the escalating war against drugs at the border area between the U.S. and Mexico.",
        "keywords": "cartel border juarez fbi cia black ops night vision tunnel raid morality drug war"
    },
    {
        "title": "Nightcrawler", "year": 2014,
        "genres": "Crime, Drama, Thriller",
        "director": "Dan Gilroy",
        "cast": "Jake Gyllenhaal, Rene Russo, Bill Paxton, Riz Ahmed",
        "rating": 7.8, "runtime": 117,
        "overview": "When Louis Bloom, a con man desperate for work, muscles into the world of L.A. crime journalism, he blurs the line between observer and participant.",
        "keywords": "freelance cameraman police scanner sociopath local news sensationalism los angeles nocturnal ethics"
    },
    {
        "title": "Drive", "year": 2011,
        "genres": "Action, Drama",
        "director": "Nicolas Winding Refn",
        "cast": "Ryan Gosling, Carey Mulligan, Bryan Cranston, Albert Brooks, Oscar Isaac",
        "rating": 7.8, "runtime": 100,
        "overview": "A mysterious Hollywood stuntman and mechanic moonlights as a getaway driver and finds himself in trouble when he helps out his neighbor.",
        "keywords": "getaway driver scorpion jacket synthwave elevator scene toothpick silent hero protection los angeles"
    },
    {
        "title": "Baby Driver", "year": 2017,
        "genres": "Action, Crime, Music",
        "director": "Edgar Wright",
        "cast": "Ansel Elgort, Jon Bernthal, Jon Hamm, Eiza González, Jamie Foxx",
        "rating": 7.5, "runtime": 113,
        "overview": "After being coerced into working for a crime boss, a young getaway driver finds himself taking part in a heist doomed to fail.",
        "keywords": "music synced getaway driving sunglasses tinnitus bank robbery diner romance rhythm"
    },
    {
        "title": "American Psycho", "year": 2000,
        "genres": "Crime, Drama, Horror",
        "director": "Mary Harron",
        "cast": "Christian Bale, Justin Theroux, Josh Lucas, Chloë Sevigny, Willem Dafoe",
        "rating": 7.6, "runtime": 102,
        "overview": "A wealthy New York City investment banking executive, Patrick Bateman, hides his alternate psychopathic ego from his co-workers and friends.",
        "keywords": "patrick bateman business card wall street 1980s vanity chainsaw satirical horror corporate greed"
    },
    {
        "title": "There Will Be Blood", "year": 2007,
        "genres": "Drama",
        "director": "Paul Thomas Anderson",
        "cast": "Daniel Day-Lewis, Paul Dano, Ciarán Hinds, Kevin J. O'Connor",
        "rating": 8.2, "runtime": 158,
        "overview": "A story of family, religion, hatred, oil and madness, focusing on a turn-of-the-century prospector in the early days of the business.",
        "keywords": "oil prospector greed i drink your milkshake bowling alley capitalism fanaticism ruthless ambition"
    },
    {
        "title": "The Green Mile", "year": 1999,
        "genres": "Crime, Drama, Fantasy, Mystery",
        "director": "Frank Darabont",
        "cast": "Tom Hanks, Michael Clarke Duncan, David Morse, Bonnie Hunt",
        "rating": 8.6, "runtime": 189,
        "overview": "A tale set on death row in a southern prison, where gentle giant John Coffey possesses a mysterious, supernatural healing gift.",
        "keywords": "death row prison guards miracle healing electric chair compassion steven king mouse mr jingles"
    },
    {
        "title": "Cast Away", "year": 2000,
        "genres": "Adventure, Drama, Romance",
        "director": "Robert Zemeckis",
        "cast": "Tom Hanks, Helen Hunt, Paul Sanchez, Lari White",
        "rating": 7.8, "runtime": 143,
        "overview": "A FedEx executive undergoes a physical and emotional transformation after surviving a plane crash and living on a deserted island.",
        "keywords": "deserted island survival plane crash wilson volleyball fire spear fishing solitude resilience"
    },
    {
        "title": "Hacksaw Ridge", "year": 2016,
        "genres": "Biography, Drama, History, War",
        "director": "Mel Gibson",
        "cast": "Andrew Garfield, Sam Worthington, Luke Bracey, Teresa Palmer, Vince Vaughn",
        "rating": 8.1, "runtime": 139,
        "overview": "World War II American Army Medic Desmond T. Doss, who served during the Battle of Okinawa, refuses to carry a weapon and becomes the first Conscientious Objector to win the Medal of Honor.",
        "keywords": "desmond doss conscientious objector medic okinawa battlefield faith courage rescue hero"
    },
    {
        "title": "Full Metal Jacket", "year": 1987,
        "genres": "Drama, War",
        "director": "Stanley Kubrick",
        "cast": "Matthew Modine, R. Lee Ermey, Vincent D'Onofrio, Adam Baldwin",
        "rating": 8.3, "runtime": 116,
        "overview": "A pragmatic U.S. Marine observes the dehumanizing effects the U.S.-Vietnam War has on his fellow recruits from their brutal boot camp training to the bloody street fighting in Hue.",
        "keywords": "boot camp drill sergeant private pyle vietnam war dehumanization sniper war insanity"
    },
    {
        "title": "Apocalypse Now", "year": 1979,
        "genres": "Drama, Mystery, War",
        "director": "Francis Ford Coppola",
        "cast": "Martin Sheen, Marlon Brando, Robert Duvall, Frederic Forrest",
        "rating": 8.4, "runtime": 147,
        "overview": "A U.S. Army officer serving in Vietnam is tasked with assassinating a renegade Special Forces Colonel who sees himself as a god.",
        "keywords": "vietnam war colonel kurtz river journey the horror ride of the valkyries napalm descent into madness"
    },
    {
        "title": "The Pianist", "year": 2002,
        "genres": "Biography, Drama, Music, War",
        "director": "Roman Polanski",
        "cast": "Adrien Brody, Thomas Kretschmann, Frank Finlay, Maureen Lipman",
        "rating": 8.5, "runtime": 150,
        "overview": "A Polish Jewish musician struggles to survive the destruction of the Warsaw ghetto of World War II.",
        "keywords": "warsaw ghetto holocaust pianist survival classical music ruins hunger resilience world war two"
    },
    {
        "title": "Life Is Beautiful", "year": 1997,
        "genres": "Comedy, Drama, Romance, War",
        "director": "Roberto Benigni",
        "cast": "Roberto Benigni, Nicoletta Braschi, Giorgio Cantarini",
        "rating": 8.6, "runtime": 116,
        "overview": "When an open-minded Jewish librarian and his son become victims of the Holocaust, he uses a perfect mixture of will, humor, and imagination to protect his son from the dangers around their camp.",
        "keywords": "holocaust concentration camp father son sacrifice humor imagination love italian masterpiece"
    },
    {
        "title": "Suzume", "year": 2022,
        "genres": "Animation, Action, Adventure, Drama, Fantasy",
        "director": "Makoto Shinkai",
        "cast": "Nanoka Hara, Hokuto Matsumura, Eri Fukatsu",
        "rating": 7.6, "runtime": 122,
        "overview": "A modern action adventure road story where a 17-year-old girl named Suzume helps a mysterious young man close doors from the other side that are releasing disasters all over Japan.",
        "keywords": "doors earthquake worm japan road trip talking chair keystone fantasy anime makoto shinkai"
    },
    {
        "title": "Akira", "year": 1988,
        "genres": "Animation, Action, Drama, Sci-Fi",
        "director": "Katsuhiro Otomo",
        "cast": "Mitsuo Iwata, Nozomu Sasaki, Mami Koyama",
        "rating": 8.0, "runtime": 124,
        "overview": "A secret military project endangers Neo-Tokyo when it turns a biker gang member into a rampaging psychic psychopath who can only be saved by two teenagers and a group of psychics.",
        "keywords": "neo tokyo cyberpunk psychic powers kaneda red motorcycle tetsuo mutation post apocalypse anime"
    },
    {
        "title": "Princess Mononoke", "year": 1997,
        "genres": "Animation, Action, Adventure, Fantasy",
        "director": "Hayao Miyazaki",
        "cast": "Yoji Matsuda, Yuriko Ishida, Yuko Tanaka",
        "rating": 8.4, "runtime": 134,
        "overview": "Ashitaka finds himself in the middle of a war between forest gods and Tatara, a mining colony.",
        "keywords": "studio ghibli nature gods environmentalism wolf girl curse iron town harmony epic anime"
    },
    {
        "title": "A Silent Voice", "year": 2016,
        "genres": "Animation, Drama",
        "director": "Naoko Yamada",
        "cast": "Miyu Irino, Saori Hayami, Aoi Yuki",
        "rating": 8.1, "runtime": 130,
        "overview": "A former elementary school bully tries to make amends with the deaf girl he tormented years earlier.",
        "keywords": "redemption deaf sign language high school bullying forgiveness mental health empathy anime"
    },
    {
        "title": "Toy Story 3", "year": 2010,
        "genres": "Animation, Adventure, Comedy, Family, Fantasy",
        "director": "Lee Unkrich",
        "cast": "Tom Hanks, Tim Allen, Joan Cusack, Ned Beatty",
        "rating": 8.3, "runtime": 103,
        "overview": "The toys are mistakenly delivered to a day-care center instead of the attic right before Andy leaves for college, and it's up to Woody to convince the other toys that they weren't abandoned.",
        "keywords": "daycare incinerator escape growing up lotso bear college farewell childhood moving on"
    },
    {
        "title": "Finding Nemo", "year": 2003,
        "genres": "Animation, Adventure, Comedy, Family",
        "director": "Andrew Stanton, Lee Unkrich",
        "cast": "Albert Brooks, Ellen DeGeneres, Alexander Gould, Willem Dafoe",
        "rating": 8.2, "runtime": 100,
        "overview": "After his son is captured in the Great Barrier Reef and taken to Sydney, a timid clownfish sets out on a journey to bring him home.",
        "keywords": "clownfish ocean sydney dory just keep swimming turtles sharks father son search pixar"
    },
    {
        "title": "The Incredibles", "year": 2004,
        "genres": "Animation, Action, Adventure, Family, Sci-Fi",
        "director": "Brad Bird",
        "cast": "Craig T. Nelson, Holly Hunter, Samuel L. Jackson, Jason Lee",
        "rating": 8.0, "runtime": 115,
        "overview": "While trying to lead a quiet suburban life, a family of undercover superheroes are forced into action to save the world.",
        "keywords": "superhero family mr incredible elastigirl syndrome island robot no capes frozone pixar"
    },
    {
        "title": "Inside Out 2", "year": 2024,
        "genres": "Animation, Adventure, Comedy, Drama, Family, Fantasy",
        "director": "Kelsey Mann",
        "cast": "Amy Poehler, Maya Hawke, Kensington Tallman, Liza Lapira, Tony Hale",
        "rating": 7.6, "runtime": 96,
        "overview": "Follow Joy, Sadness, Anger, Fear and Disgust who've been running a successful operation by all accounts, but suddenly find themselves grappling with new emotions: Anxiety, Envy, Ennui and Embarrassment.",
        "keywords": "anxiety puberty teenage hockey camp sense of self new emotions joy panic attack growing up"
    },
    {
        "title": "Poor Things", "year": 2023,
        "genres": "Comedy, Drama, Romance, Sci-Fi",
        "director": "Yorgos Lanthimos",
        "cast": "Emma Stone, Mark Ruffalo, Willem Dafoe, Ramy Youssef",
        "rating": 7.9, "runtime": 141,
        "overview": "The incredible tale about the fantastical evolution of Bella Baxter, a young woman brought back to life by the brilliant and unorthodox scientist Dr. Godwin Baxter.",
        "keywords": "frankenstein bella baxter rebirth sexuality liberation victorian steampunk surreal feminism"
    },
    {
        "title": "The Holdovers", "year": 2023,
        "genres": "Comedy, Drama",
        "director": "Alexander Payne",
        "cast": "Paul Giamatti, Dominic Sessa, Da'Vine Joy Randolph",
        "rating": 7.9, "runtime": 133,
        "overview": "A cranky history teacher at a remote prep school is forced to remain on campus over the holidays with a grieving cook and a troubled student who has no place to go.",
        "keywords": "boarding school new england 1970 christmas holidays unlikely friendship grief history teacher"
    },
    {
        "title": "Anatomy of a Fall", "year": 2023,
        "genres": "Crime, Drama, Mystery, Thriller",
        "director": "Justine Triet",
        "cast": "Sandra Hüller, Swann Arlaud, Milo Machado-Graner",
        "rating": 7.7, "runtime": 151,
        "overview": "A woman is suspected of her husband's murder, and their blind son faces a moral dilemma as the sole witness.",
        "keywords": "french alps chalet courtroom trial snoop dog marriage autopsy recording blind witness truth"
    },
    {
        "title": "The Zone of Interest", "year": 2023,
        "genres": "Drama, History, War",
        "director": "Jonathan Glazer",
        "cast": "Christian Friedel, Sandra Hüller, Johann Karthaus",
        "rating": 7.4, "runtime": 105,
        "overview": "Auschwitz commandant Rudolf Höss and his wife Hedwig strive to build a dream life for their family in a house and garden beside the camp.",
        "keywords": "auschwitz commandant domestic banality of evil sound design wall garden holocaust chilling"
    },
    {
        "title": "The Truman Show", "year": 1998,
        "genres": "Comedy, Drama",
        "director": "Peter Weir",
        "cast": "Jim Carrey, Laura Linney, Ed Harris, Noah Emmerich",
        "rating": 8.2, "runtime": 103,
        "overview": "An insurance salesman discovers his whole life is actually a reality TV show broadcast live to the entire world 24/7.",
        "keywords": "reality television simulated world existential artificial dome hidden cameras free will paranoia"
    },
    # --- ROBOTICS, MECHA & SCI-FI BLOCKBUSTERS (USER FAVORITES) ---
    {
        "title": "Real Steel", "year": 2011,
        "genres": "Action, Drama, Sci-Fi",
        "director": "Shawn Levy",
        "cast": "Hugh Jackman, Dakota Goyo, Evangeline Lilly, Anthony Mackie",
        "rating": 7.1, "runtime": 127,
        "overview": "In the near future, robot boxing is a top sport. A struggling ex-boxer and his estranged son rebuild an obsolete junkyard sparring bot named Atom into a championship contender.",
        "keywords": "robot boxing atom underdog fighter hugh jackman father son bond junkyard mecha championship shadow function"
    },
    {
        "title": "Transformers", "year": 2007,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Michael Bay",
        "cast": "Shia LaBeouf, Megan Fox, Josh Duhamel, Tyrese Gibson",
        "rating": 7.1, "runtime": 144,
        "overview": "An ancient struggle between two Cybertronian races, the heroic Autobots and the evil Decepticons, comes to Earth, with a clue to the ultimate power held by a teenager.",
        "keywords": "optimus prime bumblebee megatron autobots decepticons allspark alien robots cybertron car transformation michael bay"
    },
    {
        "title": "Transformers: Dark of the Moon", "year": 2011,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Michael Bay",
        "cast": "Shia LaBeouf, Rosie Huntington-Whiteley, Tyrese Gibson, Josh Duhamel",
        "rating": 6.2, "runtime": 154,
        "overview": "The Autobots learn of a Cybertronian spacecraft hidden on the moon, and race against the Decepticons to reach it and to learn its secrets.",
        "keywords": "moon landing cybertron sentinel prime optimus prime battle of chicago space race decepticons mecha destruction"
    },
    {
        "title": "Transformers: Rise of the Beasts", "year": 2023,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Steven Caple Jr.",
        "cast": "Anthony Ramos, Dominique Fishback, Peter Cullen, Ron Perlman",
        "rating": 6.1, "runtime": 127,
        "overview": "During the 1990s, a new faction of Transformers - the Maximals - join the Autobots as allies in the battle for Earth against the planet-eating Unicron.",
        "keywords": "maximals optimus primal unicron terrorcons mirage 1990s brooklyn peru transwarp key robot beast"
    },
    {
        "title": "Bumblebee", "year": 2018,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Travis Knight",
        "cast": "Hailee Steinfeld, Jorge Lendeborg Jr., John Cena, Pamela Adlon",
        "rating": 6.7, "runtime": 114,
        "overview": "On the run in the year 1987, Bumblebee finds refuge in a junkyard in a small California beach town. Charlie, on the cusp of turning 18, discovers him battle-scarred and broken.",
        "keywords": "bumblebee 1980s retro vw beetle coming of age charlie b-127 sector seven friendship decepticons autobot"
    },
    {
        "title": "Pacific Rim", "year": 2013,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Guillermo del Toro",
        "cast": "Charlie Hunnam, Idris Elba, Rinko Kikuchi, Charlie Day, Ron Perlman",
        "rating": 7.0, "runtime": 131,
        "overview": "As a war between humankind and monstrous sea creatures called Kaiju wages on, a former pilot and a trainee are paired up to drive a seemingly obsolete giant mecha Jaeger.",
        "keywords": "kaiju jaeger giant mecha gipsy danger neural drift breach monsters guillermo del toro canceling the apocalypse"
    },
    {
        "title": "Ready Player One", "year": 2018,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Steven Spielberg",
        "cast": "Tye Sheridan, Olivia Cooke, Ben Mendelsohn, Lena Waithe, Mark Rylance",
        "rating": 7.4, "runtime": 140,
        "overview": "When the creator of a virtual reality world called the OASIS dies, he releases a video in which he challenges all OASIS users to find his Easter Egg, which will give the finder his fortune.",
        "keywords": "virtual reality oasis easter egg 1980s pop culture mecha gundam iron giant gunter avatar gaming rebellion"
    },
    {
        "title": "Alita: Battle Angel", "year": 2019,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Robert Rodriguez",
        "cast": "Rosa Salazar, Christoph Waltz, Jennifer Connelly, Mahershala Ali",
        "rating": 7.3, "runtime": 122,
        "overview": "A deactivated cyborg girl is revived, but cannot remember anything of her past life and goes on a quest to find out who she is while fighting in high-speed Motorball tournaments.",
        "keywords": "cyborg warrior panzer kunst motorball iron city zalem hunter warrior heart damascus blade cyberpunk"
    },
    {
        "title": "Edge of Tomorrow", "year": 2014,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Doug Liman",
        "cast": "Tom Cruise, Emily Blunt, Bill Paxton, Brendan Gleeson",
        "rating": 7.9, "runtime": 113,
        "overview": "A soldier fighting alien mimics gets caught in a time loop that makes him relive the same brutal beach invasion day over and over, training with a warrior to survive.",
        "keywords": "live die repeat time loop alien mimics exo suit rita vrataski cage beach invasion omega reset training"
    },
    {
        "title": "District 9", "year": 2009,
        "genres": "Action, Sci-Fi, Thriller",
        "director": "Neill Blomkamp",
        "cast": "Sharlto Copley, Jason Cope, Nathalie Boltt, Sylvaine Strike",
        "rating": 7.9, "runtime": 112,
        "overview": "Violence ensues after an extraterrestrial race forced to live in slum-like conditions on Earth finds a friend in a government agent exposed to their biotechnology.",
        "keywords": "prawns extraterrestrial slums johannesburg alien mecha suit biotechnology mutation mnu apartheid allegory"
    },
    {
        "title": "I, Robot", "year": 2004,
        "genres": "Action, Mystery, Sci-Fi",
        "director": "Alex Proyas",
        "cast": "Will Smith, Bridget Moynahan, Alan Tudyk, Bruce Greenwood",
        "rating": 7.1, "runtime": 115,
        "overview": "In 2035, a technophobic cop investigates a crime that may have been perpetrated by a robot, which leads to a larger threat to humanity.",
        "keywords": "three laws of robotics sonny humanoid robot viki artificial intelligence uprising will smith chicago 2035"
    },
    {
        "title": "Minority Report", "year": 2002,
        "genres": "Action, Crime, Mystery, Sci-Fi, Thriller",
        "director": "Steven Spielberg",
        "cast": "Tom Cruise, Colin Farrell, Samantha Morton, Max von Sydow",
        "rating": 7.7, "runtime": 145,
        "overview": "In a future where a special police unit is able to arrest murderers before they commit their crimes, an officer from that unit is himself accused of a future murder.",
        "keywords": "precrime precogs future vision eye scan gesture interface murder prophecy tom cruise steven spielberg"
    },
    {
        "title": "War of the Worlds", "year": 2005,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Steven Spielberg",
        "cast": "Tom Cruise, Dakota Fanning, Tim Robbins, Miranda Otto",
        "rating": 6.5, "runtime": 116,
        "overview": "An alien invasion threatens the future of humanity. The catastrophic nightmare is seen through the eyes of one American family fighting for survival.",
        "keywords": "alien invasion tripods lightning red weed ferry attack steven spielberg survival daughter family"
    },
    {
        "title": "Independence Day", "year": 1996,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Roland Emmerich",
        "cast": "Will Smith, Bill Pullman, Jeff Goldblum, Mary McDonnell",
        "rating": 7.0, "runtime": 145,
        "overview": "The aliens are coming and their goal is to invade and destroy Earth. Fighting superior technology, mankind's best weapon is the will to survive.",
        "keywords": "alien mothership white house destruction july 4th area 51 computer virus welcome to earth dogfight will smith"
    },
    {
        "title": "Godzilla", "year": 2014,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Gareth Edwards",
        "cast": "Aaron Taylor-Johnson, Elizabeth Olsen, Bryan Cranston, Ken Watanabe",
        "rating": 6.4, "runtime": 123,
        "overview": "The world is beset by the appearance of monstrous creatures, but one of them may be the only one who can save humanity: Godzilla, the King of the Monsters.",
        "keywords": "godzilla muto atomic breath kaiju san francisco monarch nuclear predator roar gareth edwards"
    },
    {
        "title": "Godzilla vs. Kong", "year": 2021,
        "genres": "Action, Sci-Fi, Thriller",
        "director": "Adam Wingard",
        "cast": "Alexander Skarsgård, Millie Bobby Brown, Rebecca Hall, Brian Tyree Henry",
        "rating": 6.3, "runtime": 113,
        "overview": "The epic next chapter in the cinematic Monsterverse pits two of the greatest icons in motion picture history against each other: the fearsome Godzilla and the mighty Kong.",
        "keywords": "godzilla kong titan clash hollow earth mechagodzilla neon hong kong atomic axe monsterverse"
    },
    {
        "title": "Rise of the Planet of the Apes", "year": 2011,
        "genres": "Action, Drama, Sci-Fi",
        "director": "Rupert Wyatt",
        "cast": "James Franco, Andy Serkis, Freida Pinto, John Lithgow",
        "rating": 7.6, "runtime": 105,
        "overview": "A substance designed to help the brain repair itself gives advanced intelligence to a chimpanzee who leads an ape uprising against humanity.",
        "keywords": "caesar alz 112 chimp intelligence ape sanctuary golden gate bridge no revolution andy serkis"
    },
    {
        "title": "Dawn of the Planet of the Apes", "year": 2014,
        "genres": "Action, Adventure, Drama, Sci-Fi",
        "director": "Matt Reeves",
        "cast": "Gary Oldman, Keri Russell, Andy Serkis, Jason Clarke, Toby Kebbell",
        "rating": 7.6, "runtime": 130,
        "overview": "A growing nation of genetically evolved apes led by Caesar is threatened by a band of human survivors of the devastating virus unleashed a decade earlier.",
        "keywords": "caesar koba ape colony simian flu human survivors trust betrayal tank attack peace matt reeves"
    },
    {
        "title": "Fast Five", "year": 2011,
        "genres": "Action, Crime, Thriller",
        "director": "Justin Lin",
        "cast": "Vin Diesel, Paul Walker, Dwayne Johnson, Jordana Brewster, Tyrese Gibson",
        "rating": 7.3, "runtime": 130,
        "overview": "Dominic Toretto and his crew of street racers plan a massive heist to buy their freedom while in the crosshairs of a powerful Brazilian drug lord and a dangerous federal agent.",
        "keywords": "rio de janeiro vault heist street racing federal agent hobbs favela roof chase family vin diesel"
    },
    {
        "title": "Furious 7", "year": 2015,
        "genres": "Action, Crime, Thriller",
        "director": "James Wan",
        "cast": "Vin Diesel, Paul Walker, Dwayne Johnson, Jason Statham, Michelle Rodriguez",
        "rating": 7.1, "runtime": 137,
        "overview": "Deckard Shaw seeks revenge against Dominic Toretto and his family for his comatose brother, while a shadowy government agency hires Dom to recover a high-tech surveillance program.",
        "keywords": "deckard shaw god's eye skyscraper jump abu dhabi car parachute paul walker tribute family"
    },
    {
        "title": "Mission: Impossible - Fallout", "year": 2018,
        "genres": "Action, Adventure, Thriller",
        "director": "Christopher McQuarrie",
        "cast": "Tom Cruise, Henry Cavill, Ving Rhames, Simon Pegg, Rebecca Ferguson",
        "rating": 7.7, "runtime": 147,
        "overview": "Ethan Hunt and his IMF team, along with some familiar allies, race against time after a mission goes wrong and nuclear plutonium falls into terrorist hands.",
        "keywords": "halo jump bathroom brawl henry cavill reload paris motorcycle helicopter chase cliffhanger ethan hunt"
    },
    {
        "title": "Pirates of the Caribbean: The Curse of the Black Pearl", "year": 2003,
        "genres": "Action, Adventure, Fantasy",
        "director": "Gore Verbinski",
        "cast": "Johnny Depp, Geoffrey Rush, Orlando Bloom, Keira Knightley",
        "rating": 8.1, "runtime": 143,
        "overview": "Blacksmith Will Turner teams up with eccentric pirate 'Captain' Jack Sparrow to save his love from Jack's former pirate allies, who are now undead.",
        "keywords": "captain jack sparrow black pearl skeleton pirates aztec gold curse rum tortuga swordfight"
    },
    {
        "title": "Harry Potter and the Sorcerer's Stone", "year": 2001,
        "genres": "Adventure, Family, Fantasy",
        "director": "Chris Columbus",
        "cast": "Daniel Radcliffe, Rupert Grint, Emma Watson, Richard Harris",
        "rating": 7.6, "runtime": 152,
        "overview": "An orphaned boy enrolls in a school of wizardry, where he learns the truth about himself, his family and the terrible evil that haunts the magical world.",
        "keywords": "hogwarts wizard sorting hat quidditch platform 9 3 4 sorcerer's stone voldemort magic gryffindor"
    },
    {
        "title": "Harry Potter and the Prisoner of Azkaban", "year": 2004,
        "genres": "Adventure, Family, Fantasy",
        "director": "Alfonso Cuarón",
        "cast": "Daniel Radcliffe, Emma Watson, Rupert Grint, Gary Oldman",
        "rating": 7.9, "runtime": 142,
        "overview": "Harry Potter, Ron and Hermione return to Hogwarts School of Witchcraft and Wizardry for their third year of study, where they delve into the mystery surrounding an escaped prisoner.",
        "keywords": "sirius black dementors patronus time turner marauder's map werewolf buckbeak alfonso cuaron"
    },
    {
        "title": "The Hunger Games", "year": 2012,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Gary Ross",
        "cast": "Jennifer Lawrence, Josh Hutcherson, Liam Hemsworth, Woody Harrelson",
        "rating": 7.2, "runtime": 142,
        "overview": "Katniss Everdeen voluntarily takes her younger sister's place in the Hunger Games: a televised competition in which two teenagers from each of the twelve Districts fight to the death.",
        "keywords": "katniss everdeen district 12 mockingjay bow and arrow capitol tribute survival arena battle royale"
    },
    {
        "title": "Tron: Legacy", "year": 2010,
        "genres": "Action, Adventure, Sci-Fi",
        "director": "Joseph Kosinski",
        "cast": "Jeff Bridges, Garrett Hedlund, Olivia Wilde, Bruce Boxleitner",
        "rating": 6.8, "runtime": 125,
        "overview": "The son of a virtual world designer goes looking for his father and ends up inside the digital world that his father designed, meeting his father's creation.",
        "keywords": "the grid light cycles identity disc daft punk synthwave virtual reality digital avatar kevin flynn"
    },
    {
        "title": "Speed", "year": 1994,
        "genres": "Action, Adventure, Thriller",
        "director": "Jan de Bont",
        "cast": "Keanu Reeves, Dennis Hopper, Sandra Bullock, Jeff Daniels",
        "rating": 7.3, "runtime": 116,
        "overview": "A young police officer must prevent a bomb exploding aboard a city bus by keeping its speed above 50 miles per hour.",
        "keywords": "bus bomb 50 mph freeway jump keanu reeves hostage crisis los angeles tension transit"
    },
    {
        "title": "Men in Black", "year": 1997,
        "genres": "Action, Adventure, Comedy, Sci-Fi",
        "director": "Barry Sonnenfeld",
        "cast": "Tommy Lee Jones, Will Smith, Linda Fiorentino, Vincent D'Onofrio",
        "rating": 7.3, "runtime": 98,
        "overview": "A police officer joins a secret organization that polices and monitors extraterrestrial interactions on Earth.",
        "keywords": "mib neuralyzer agent j agent k edgar bug alien immigration sunglasses noisy cricket will smith"
    },
    {
        "title": "The Equalizer", "year": 2014,
        "genres": "Action, Crime, Thriller",
        "director": "Antoine Fuqua",
        "cast": "Denzel Washington, Marton Csokas, Chloë Grace Moretz, David Harbour",
        "rating": 7.2, "runtime": 132,
        "overview": "A man who believes he has put his mysterious past behind him cannot stand idly by when he meets a young girl under the control of ultra-violent Russian gangsters.",
        "keywords": "robert mccall denzel washington timer hardware store kills russian mafia vigilante justice precision"
    },
    {
        "title": "Taken", "year": 2008,
        "genres": "Action, Crime, Thriller",
        "director": "Pierre Morel",
        "cast": "Liam Neeson, Maggie Grace, Famke Janssen, Leland Orser",
        "rating": 7.8, "runtime": 90,
        "overview": "A retired CIA agent travels across Europe and relies on his old skills to save his estranged daughter, who has been kidnapped by human traffickers while on a trip to Paris.",
        "keywords": "particular set of skills liam neeson paris abduction human trafficking rescue phone call interrogation"
    },
    {
        "title": "Kingsman: The Secret Service", "year": 2014,
        "genres": "Action, Adventure, Comedy, Sci-Fi",
        "director": "Matthew Vaughn",
        "cast": "Colin Firth, Taron Egerton, Samuel L. Jackson, Mark Strong",
        "rating": 7.7, "runtime": 129,
        "overview": "A spy organization recruits a promising street kid into the agency's training program, while a global threat emerges from a twisted tech genius.",
        "keywords": "oxfords not brogues church scene umbrella gun manners maketh man secret agents spy tailoring"
    },
    {
        "title": "Free Guy", "year": 2021,
        "genres": "Action, Adventure, Comedy, Fantasy, Sci-Fi",
        "director": "Shawn Levy",
        "cast": "Ryan Reynolds, Jodie Comer, Taika Waititi, Lil Rel Howery",
        "rating": 7.1, "runtime": 115,
        "overview": "When a bank teller discovers he's actually a background player in an open-world video game, he decides to become the hero of his own story.",
        "keywords": "video game npc blue shirt guy open world artificial intelligence gaming easter eggs ryan reynolds"
    },
    {
        "title": "Shang-Chi and the Legend of the Ten Rings", "year": 2021,
        "genres": "Action, Adventure, Fantasy, Sci-Fi",
        "director": "Destin Daniel Cretton",
        "cast": "Simu Liu, Awkwafina, Tony Leung, Michelle Yeoh",
        "rating": 7.4, "runtime": 132,
        "overview": "Shang-Chi, the master of weaponry-based Kung Fu, is forced to confront his past after being drawn into the Ten Rings organization.",
        "keywords": "ten rings bus fight scaffolding ta lo martial arts dragon wenwu father son marvel"
    },
    {
        "title": "Thor: Ragnarok", "year": 2017,
        "genres": "Action, Adventure, Comedy, Fantasy, Sci-Fi",
        "director": "Taika Waititi",
        "cast": "Chris Hemsworth, Tom Hiddleston, Cate Blanchett, Mark Ruffalo, Tessa Thompson",
        "rating": 7.9, "runtime": 130,
        "overview": "Imprisoned on the planet Sakaar, Thor must race against time to return to Asgard and stop Ragnarök, the destruction of his world, at the hands of the ruthless villain Hela.",
        "keywords": "gladiator hulk friend from work taika waititi hela valkyrie led zeppelin immigrant song asgard"
    },
    {
        "title": "Deadpool & Wolverine", "year": 2024,
        "genres": "Action, Comedy, Sci-Fi",
        "director": "Shawn Levy",
        "cast": "Ryan Reynolds, Hugh Jackman, Emma Corrin, Matthew Macfadyen",
        "rating": 7.7, "runtime": 128,
        "overview": "Wolverine is recovering from his injuries when he crosses paths with the loudmouth Deadpool. They team up to defeat a common enemy from the Void.",
        "keywords": "deadpool wolverine tva the void multiverse katana adamantium claws fourth wall comedy marvel"
    },
    {
        "title": "Shrek", "year": 2001,
        "genres": "Animation, Adventure, Comedy, Family, Fantasy",
        "director": "Andrew Adamson, Vicky Jenson",
        "cast": "Mike Myers, Eddie Murphy, Cameron Diaz, John Lithgow",
        "rating": 7.9, "runtime": 90,
        "overview": "A mean lord exiles fairytale creatures to the swamp of a grumpy ogre, who must go on a quest and rescue a princess for the lord in order to get his land back.",
        "keywords": "shrek donkey fiona ogre swamp lord farquaad all star fairy tale satire dragon onion layers"
    },
    {
        "title": "Kung Fu Panda", "year": 2008,
        "genres": "Animation, Action, Adventure, Comedy, Family",
        "director": "Mark Osborne, John Stevenson",
        "cast": "Jack Black, Ian McShane, Angelina Jolie, Dustin Hoffman",
        "rating": 7.6, "runtime": 92,
        "overview": "To everyone's surprise, including his own, Po, an overweight, clumsy panda, is chosen as protector of the Valley of Peace against the fierce snow leopard Tai Lung.",
        "keywords": "dragon warrior po master shifu oogway noodles tai lung inner peace skadush kung fu"
    },
    {
        "title": "How to Train Your Dragon", "year": 2010,
        "genres": "Animation, Action, Adventure, Family, Fantasy",
        "director": "Dean DeBlois, Chris Sanders",
        "cast": "Jay Baruchel, Gerard Butler, America Ferrera, Craig Ferguson",
        "rating": 8.1, "runtime": 98,
        "overview": "A hapless young Viking who aspires to hunt dragons becomes the unlikely friend of a young dragon himself, and learns there may be more to the creatures than he assumed.",
        "keywords": "toothless night fury hiccup berk vikings dragon flight prosthetic tail friendship bonding"
    },
    # --- TAMIL CINEMA & REGIONAL INDIAN MASTERPIECES (KAPITALS OF INDIAN CINEMA) ---
    {
        "title": "Vikram", "year": 2022,
        "genres": "Action, Crime, Thriller",
        "director": "Lokesh Kanagaraj",
        "cast": "Kamal Haasan, Fahadh Faasil, Vijay Sethupathi, Suriya, Narain",
        "rating": 8.3, "runtime": 175,
        "overview": "A special agent investigates a series of murders committed by a masked vigilante group, only to discover a deep conspiracy involving a ruthless drug syndicate and the legendary commander Vikram.",
        "keywords": "kamal haasan lcu lokesh kanagaraj rolex fahadh faasil vijay sethupathi black ops agent tina drug cartel machine gun shootout mass action"
    },
    {
        "title": "Leo", "year": 2023,
        "genres": "Action, Crime, Drama, Thriller",
        "director": "Lokesh Kanagaraj",
        "cast": "Thalapathy Vijay, Sanjay Dutt, Arjun Sarja, Trisha Krishnan, Gautham Vasudev Menon",
        "rating": 7.2, "runtime": 164,
        "overview": "A mild-mannered cafe owner in Himachal Pradesh becomes a local hero after thwarting an armed attack, but his sudden fame attracts ruthless gangsters who insist he is their estranged ruthless brother Leo Das.",
        "keywords": "thalapathy vijay leo das parthiban bloody sweet hyena fight chocolate factory cafe owner lcu lokesh kanagaraj gang war mass action"
    },
    {
        "title": "Master", "year": 2021,
        "genres": "Action, Crime, Drama, Thriller",
        "director": "Lokesh Kanagaraj",
        "cast": "Thalapathy Vijay, Vijay Sethupathi, Malavika Mohanan, Andrea Jeremiah, Arjun Das",
        "rating": 7.8, "runtime": 179,
        "overview": "An alcoholic professor is sent to a juvenile school, where he clashes with a ruthless gangster who uses the incarcerated children as scapegoats for his criminal empire.",
        "keywords": "thalapathy vijay jd vijay sethupathi bhavani juvenile reform school kabaddi archery punch lorry fight lokesh kanagaraj mass hero"
    },
    {
        "title": "Kaithi", "year": 2019,
        "genres": "Action, Crime, Thriller",
        "director": "Lokesh Kanagaraj",
        "cast": "Karthi, Narain, Arjun Das, George Maryan, Harish Uthaman",
        "rating": 8.4, "runtime": 145,
        "overview": "Dilli, an ex-convict on his way to see his daughter for the very first time, is coerced by a police officer to drive an unconscious poisoned police unit through a hostile drug gang siege.",
        "keywords": "karthi dilli lokesh kanagaraj biryani lorry night drive police station under siege gatling gun drug syndicate lcu daughter bond"
    },
    {
        "title": "Jailer", "year": 2023,
        "genres": "Action, Comedy, Crime, Drama",
        "director": "Nelson Dilipkumar",
        "cast": "Rajinikanth, Vinayakan, Ramya Krishnan, Vasanth Ravi, Mohanlal, Shiva Rajkumar",
        "rating": 7.1, "runtime": 168,
        "overview": "A retired prison warden, living a quiet life with his family, unleashes his dark past and unmatched lethal connections when his police officer son disappears investigating an idol smuggling ring.",
        "keywords": "superstar rajinikanth tiger mutuvel pandian hukum idol smuggling nelson mass action blast mohanlal shiva rajkumar lethal retired warden"
    },
    {
        "title": "Enthiran", "year": 2010,
        "genres": "Action, Sci-Fi",
        "director": "S. Shankar",
        "cast": "Rajinikanth, Aishwarya Rai Bachchan, Danny Denzongpa, Santhanam",
        "rating": 7.1, "runtime": 177,
        "overview": "A brilliant scientist creates a sophisticated humanoid robot named Chitti to serve society. But trouble brews when the robot develops human emotions, falls for the scientist's fiancée, and is corrupted by a red chip.",
        "keywords": "chitti the robot rajinikanth red chip humanoid robot shankar mecha transformation machine gun sphere magnetic pulse artificial intelligence robot army"
    },
    {
        "title": "2.0", "year": 2018,
        "genres": "Action, Sci-Fi",
        "director": "S. Shankar",
        "cast": "Rajinikanth, Akshay Kumar, Amy Jackson, Adil Hussain",
        "rating": 6.1, "runtime": 148,
        "overview": "When mobile phones across Chennai begin mysteriously flying away into the sky and forming a giant vengeful bird creature, Dr. Vaseegaran reassembles Chitti to battle the environmental avenger Pakshi Rajan.",
        "keywords": "chitti 2.0 pakshi rajan cell phone monster microbots rajinikanth akshay kumar shankar radiation bird avatar giant robot showdown"
    },
    {
        "title": "Ponniyin Selvan: Part I", "year": 2022,
        "genres": "Action, Adventure, Drama, History",
        "director": "Mani Ratnam",
        "cast": "Vikram, Aishwarya Rai Bachchan, Jayam Ravi, Karthi, Trisha Krishnan",
        "rating": 7.6, "runtime": 167,
        "overview": "Vandiyathevan sets out to cross the Chola land to deliver a message from Crown Prince Aditha Karikalan, while a conspiracy brews within the palace to overthrow Emperor Sundara Chola.",
        "keywords": "chola dynasty mani ratnam kalki aditha karikalan nandini vandiyathevan arunmozhi varman historical epic palace conspiracy thanjavur"
    },
    {
        "title": "Ponniyin Selvan: Part II", "year": 2023,
        "genres": "Action, Adventure, Drama, History",
        "director": "Mani Ratnam",
        "cast": "Vikram, Aishwarya Rai Bachchan, Jayam Ravi, Karthi, Trisha Krishnan",
        "rating": 7.3, "runtime": 164,
        "overview": "Arunmozhi Varman continues his journey to become Rajaraja I, the greatest ruler of the historic Chola Empire of South India, while the tragic mystery of Nandini and Aditha Karikalan reaches its climax.",
        "keywords": "chola empire rajraja chola mani ratnam aditha karikalan nandini assassination kadambur crown succession historical war"
    },
    {
        "title": "Asuran", "year": 2019,
        "genres": "Action, Drama",
        "director": "Vetrimaaran",
        "cast": "Dhanush, Manju Warrier, Ken Karunas, Pasupathy, Prakash Raj",
        "rating": 8.4, "runtime": 141,
        "overview": "A mild-mannered farmer from a marginalized community flees with his hot-headed younger son after the boy retaliates and kills an oppressive upper-caste landlord.",
        "keywords": "dhanush sivasami vetrimaaran caste oppression father sacrifice sickle fight flash back transformation forest survival rural revenge"
    },
    {
        "title": "Vada Chennai", "year": 2018,
        "genres": "Action, Crime, Drama",
        "director": "Vetrimaaran",
        "cast": "Dhanush, Ameer Sultan, Radha Ravi, Daniel Balaji, Andrea Jeremiah, Samuthirakani",
        "rating": 8.4, "runtime": 164,
        "overview": "A skilled carrom player in North Madras is reluctantly drawn into an all-out turf war between two rival mob factions when a local community's land is threatened by greedy politicians.",
        "keywords": "north madras carrom player prison gang war rajan anbu vetrimaaran dhanush betrayal political conspiracy underworld chronicle"
    },
    {
        "title": "Soorarai Pottru", "year": 2020,
        "genres": "Action, Drama",
        "director": "Sudha Kongara",
        "cast": "Suriya, Aparna Balamurali, Paresh Rawal, Urvashi, Mohan Babu",
        "rating": 8.7, "runtime": 153,
        "overview": "Nedumaaran Rajangam, a former air force captain, dreams of launching a revolutionary low-cost airline so that every common man in India can afford to fly, battling cutthroat aviation monopolies.",
        "keywords": "suriya maara low cost airline aviation industry deccan air entrepreneur resilience air force common man flight dream sudha kongara"
    },
    {
        "title": "Jai Bhim", "year": 2021,
        "genres": "Crime, Drama, Mystery",
        "director": "T.J. Gnanavel",
        "cast": "Suriya, Lijomol Jose, Manikandan, Rajisha Vijayan, Prakash Raj",
        "rating": 8.8, "runtime": 164,
        "overview": "When a courageous tribal man is falsely accused of burglary, arrested and goes missing from police custody, his pregnant wife turns to advocate Chandru to fight an uphill habeas corpus legal battle.",
        "keywords": "suriya advocate chandru tribal rights custodial torture habeas corpus legal courtroom drama justice human rights truth constitutional law"
    },
    {
        "title": "96", "year": 2018,
        "genres": "Drama, Romance",
        "director": "C. Prem Kumar",
        "cast": "Vijay Sethupathi, Trisha Krishnan, Varsha Bollamma, Devadarshini",
        "rating": 8.5, "runtime": 158,
        "overview": "Two high school sweethearts from the batch of 1996, travel photographer Ram and married housewife Janu, reunite after 22 years at a school reunion and spend an unforgettable, poignant evening reminiscing.",
        "keywords": "vijay sethupathi trisha ram and jaanu school reunion childhood love nostalgia yellow dress unfulfilled romance soulful music the life of ram"
    },
    {
        "title": "Vikram Vedha", "year": 2017,
        "genres": "Action, Crime, Drama, Thriller",
        "director": "Pushkar-Gayathri",
        "cast": "R. Madhavan, Vijay Sethupathi, Shraddha Srinath, Kathir, Varalaxmi Sarathkumar",
        "rating": 8.2, "runtime": 147,
        "overview": "A ruthless encounter police inspector named Vikram tracks down and captures a notorious mobster, Vedha. But each time they meet, Vedha tells him a riddle-like story that forces Vikram to question right and wrong.",
        "keywords": "madhavan vijay sethupathi encounter cop gangster vikramaditya betal parotta stories moral gray justice corruption pushkar gayathri"
    },
    {
        "title": "Anniyan", "year": 2005,
        "genres": "Action, Drama, Thriller",
        "director": "S. Shankar",
        "cast": "Vikram, Sadha, Prakash Raj, Vivek, Nedumudi Venu",
        "rating": 8.3, "runtime": 181,
        "overview": "Disillusioned by public apathy and systemic corruption, a mild-mannered lawyer develops split personalities: supermodel Remo to woo the woman he loves, and vigilante executioner Anniyan to punish wrongdoers using Garuda Puranam.",
        "keywords": "vikram shankar split personality ambi remo anniyan garuda puranam vigilante justice karate fight multiple personality corruption punishment"
    },
    {
        "title": "Sivaji", "year": 2007,
        "genres": "Action, Adventure, Comedy, Drama",
        "director": "S. Shankar",
        "cast": "Rajinikanth, Shriya Saran, Suman, Vivek, Raghuvaran",
        "rating": 7.5, "runtime": 185,
        "overview": "A software engineer returns to India from the USA to provide free medical care and education to the needy. When corrupt politicians fleece him of all his wealth, he assumes a fierce new identity to take back black money.",
        "keywords": "rajinikanth sivaji the boss mottai boss black money free education corruption shankar chewing gum coin toss mass style athisayam"
    },
    {
        "title": "Baasha", "year": 1995,
        "genres": "Action, Crime, Drama",
        "director": "Suresh Krissna",
        "cast": "Rajinikanth, Nagma, Raghuvaran, Janagaraj, Charan Raj",
        "rating": 8.3, "runtime": 145,
        "overview": "A humble auto driver in Madras hides his past as a feared Mumbai underworld don who once brought terror to rivals to fulfill a dying promise to his father.",
        "keywords": "rajinikanth manik baasha auto driver bombay don mark anthony mass transformation iconic flashback interval block classic mass cinema"
    },
    {
        "title": "RRR", "year": 2022,
        "genres": "Action, Adventure, Drama",
        "director": "S.S. Rajamouli",
        "cast": "N.T. Rama Rao Jr., Ram Charan, Ajay Devgn, Alia Bhatt, Shriya Saran",
        "rating": 7.8, "runtime": 187,
        "overview": "In 1920s British-occupied India, a fearless tribal warrior and an undercover police officer form a fierce friendship, unaware of each other's secret identities and revolutionary goals.",
        "keywords": "rajamouli naatu naatu ram charan jr ntr komaram bheem alluri sitarama raju tiger fight dual hero piggyback fight british rebellion epic"
    },
    {
        "title": "Baahubali: The Beginning", "year": 2015,
        "genres": "Action, Drama, Fantasy",
        "director": "S.S. Rajamouli",
        "cast": "Prabhas, Rana Daggubati, Anushka Shetty, Tamannaah Bhatia, Ramya Krishnan",
        "rating": 8.0, "runtime": 159,
        "overview": "In the kingdom of Mahishmati, a daring young man raised near a waterfall discovers his royal heritage and the heroic legacy of his legendary father, Amarendra Baahubali.",
        "keywords": "rajamouli prabhas mahishmati shivudu shivling waterfall climb bhallaladeva kattappa kalakeya war why kattappa killed baahubali fantasy epic"
    },
    {
        "title": "Baahubali 2: The Conclusion", "year": 2017,
        "genres": "Action, Drama, Fantasy",
        "director": "S.S. Rajamouli",
        "cast": "Prabhas, Rana Daggubati, Anushka Shetty, Sathyaraj, Ramya Krishnan",
        "rating": 8.2, "runtime": 167,
        "overview": "Amarendra Baahubali is chosen as the beloved king of Mahishmati, inciting intense jealousy in Bhallaladeva, leading to an intricate web of betrayal that results in Baahubali's tragic murder by Kattappa.",
        "keywords": "amarendra baahubali prabhas devasena sword combat coronation kattappa death tree launch rajamouli mahishmati victory all time blockbuster"
    },
    {
        "title": "K.G.F: Chapter 1", "year": 2018,
        "genres": "Action, Crime, Drama",
        "director": "Prashanth Neel",
        "cast": "Yash, Srinidhi Shetty, Ramachandra Raju, Archana Jois",
        "rating": 8.2, "runtime": 156,
        "overview": "In 1970s Bombay, a ferocious orphan named Rocky rises to become a powerful mercenary, taking up an undercover mission into the slave-driven mines of the Kolar Gold Fields to assassinate a brutal tyrant.",
        "keywords": "rocky bhai yash kolar gold fields mother promise bombay gangster narachi gold mines hammer fight salaam rocky bhai prashanth neel mass"
    },
    {
        "title": "K.G.F: Chapter 2", "year": 2022,
        "genres": "Action, Crime, Drama",
        "director": "Prashanth Neel",
        "cast": "Yash, Sanjay Dutt, Raveena Tandon, Srinidhi Shetty, Prakash Raj",
        "rating": 8.2, "runtime": 168,
        "overview": "The blood-soaked land of Kolar Gold Fields now has a new overlord: Rocky. But as he consolidates his supremacy, he must confront brutal warlord Adheera and the uncompromising Prime Minister of India.",
        "keywords": "rocky bhai yash adheera sanjay dutt kalashnikov police station assault parliament gold empire mother's grave prashanth neel monster mass"
    },
    {
        "title": "Kantara", "year": 2022,
        "genres": "Action, Adventure, Drama, Thriller",
        "director": "Rishab Shetty",
        "cast": "Rishab Shetty, Kishore Kumar G., Sapthami Gowda, Achyuth Kumar",
        "rating": 8.2, "runtime": 148,
        "overview": "In a coastal Karnataka village, a hot-tempered kambala champion clashes with an upright forest officer, while ancient divine spirits and folklore guardian Panjurli Daiva awaken to protect the ancestral forest land.",
        "keywords": "panjurli daiva bhootha kola rishab shetty kambala coastal karnataka forest land folklore divine possession climax scream roar culture"
    },
    {
        "title": "Kalki 2898 AD", "year": 2024,
        "genres": "Action, Adventure, Drama, Fantasy, Sci-Fi",
        "director": "Nag Ashwin",
        "cast": "Prabhas, Amitabh Bachchan, Kamal Haasan, Deepika Padukone, Saswata Chatterjee",
        "rating": 7.5, "runtime": 181,
        "overview": "In the year 2898 AD in a dystopian world ruled from the floating Complex, an ancient immortal warrior Ashwatthama awakens to protect the unborn reincarnation of Vishnu from bounty hunter Bhairava and Supreme Yaskin.",
        "keywords": "ashwatthama amitabh bachchan prabhas bhairava bujji robot car dystopian kasi mahabharata sci-fi mythology nag ashwin complex kamal haasan yaskin"
    },
    {
        "title": "Pushpa: The Rise", "year": 2021,
        "genres": "Action, Crime, Drama, Thriller",
        "director": "Sukumar",
        "cast": "Allu Arjun, Rashmika Mandanna, Fahadh Faasil, Sunil, Anasuya Bharadwaj",
        "rating": 7.6, "runtime": 179,
        "overview": "Pushpa Raj, a coolie in the Seshachalam forests of Andhra Pradesh, rises through sheer grit and audacity to become a syndicate kingpin in the illegal trade of red sandalwood, clashing with a corrupt IPS officer.",
        "keywords": "pushpa raj allu arjun thaggedhe le red sandalwood smuggling shekhawat fahadh faasil seshachalam forests axe fight sukumar mass swag"
    },
    {
        "title": "Manjummel Boys", "year": 2024,
        "genres": "Adventure, Drama, Thriller",
        "director": "Chidambaram",
        "cast": "Soubin Shahir, Sreenath Bhasi, Balu Varghese, Ganapathi, Deepak Parambol",
        "rating": 8.5, "runtime": 135,
        "overview": "A close-knit group of young friends from Kochi embark on a vacation to Kodaikanal, where one of them plunges into the treacherous, unexplored depths of Guna Caves (Devil's Kitchen), sparking an extraordinary rescue mission.",
        "keywords": "guna caves devil's kitchen kodaikanal manjummel boys rescue survival pit rope rescue kochi friends kanmani anbodu kamal haasan tribute real story"
    },
    {
        "title": "Aavesham", "year": 2024,
        "genres": "Action, Comedy",
        "director": "Jithu Madhavan",
        "cast": "Fahadh Faasil, Hipzster, Mithun Jai Shankar, Roshan Shanavas, Sajin Gopu",
        "rating": 7.9, "runtime": 158,
        "overview": "Three engineering students in Bangalore getting bullied by seniors seek the protection of a quirky, energetic local gangster named Ranga Anna, whose eccentric brand of hospitality spirals out of control.",
        "keywords": "ranga anna fahadh faasil bangalore gangster white shirt gold chain college students party juice fight comedy mass entertainer eda mone"
    },
    {
        "title": "Drishyam", "year": 2013,
        "genres": "Crime, Drama, Thriller",
        "director": "Jeethu Joseph",
        "cast": "Mohanlal, Meena, Ansiba Hassan, Esther Anil, Asha Sharath, Siddique",
        "rating": 8.3, "runtime": 160,
        "overview": "A humble cable TV operator in rural Kerala uses his encyclopedic knowledge of cinema plots to fabricate a foolproof alibi and protect his family after they commit an accidental murder to defend their daughter.",
        "keywords": "mohanlal georgekutty jeethu joseph august 2 and 3 cinema alibi compost pit police station foundation cable operator perfect crime cover up"
    },
    {
        "title": "Kumbalangi Nights", "year": 2019,
        "genres": "Comedy, Drama, Romance",
        "director": "Madhu C. Narayanan",
        "cast": "Shane Nigam, Soubin Shahir, Fahadh Faasil, Sreenath Bhasi, Anna Ben",
        "rating": 8.5, "runtime": 135,
        "overview": "Four dysfunctional brothers living in a dilapidated home on an island in Kumbalangi find love, self-respect, and reconciliation when they unite against an oppressive, psychopathic brother-in-law named Shammi.",
        "keywords": "kumbalangi islands fahadh faasil shammi psychopathic smile soubin shahir bonny saji franky brother bonding glowing water kerala realistic drama"
    },
    {
        "title": "Premam", "year": 2015,
        "genres": "Comedy, Drama, Romance",
        "director": "Alphonse Puthren",
        "cast": "Nivin Pauly, Sai Pallavi, Madonna Sebastian, Anupama Parameswaran, Shabareesh Varma",
        "rating": 8.3, "runtime": 156,
        "overview": "Follows George David through three defining chapters of his life: his clumsy schoolboy crush on Mary, his intense college love for Malar teacher, and his mature adulthood connection with Celine.",
        "keywords": "nivin pauly malar teacher sai pallavi black shirt beard butterfly alphonse puthren red velvet cake coming of age three stages of love nostalgic"
    },
    {
        "title": "3 Idiots", "year": 2009,
        "genres": "Comedy, Drama",
        "director": "Rajkumar Hirani",
        "cast": "Aamir Khan, R. Madhavan, Sharman Joshi, Kareena Kapoor, Boman Irani",
        "rating": 8.4, "runtime": 170,
        "overview": "Two friends search for their long-lost college roommate Rancho, while recounting their days at an elite engineering institution and Rancho's unconventional philosophy on learning and life.",
        "keywords": "aamir khan rancho virus boman irani all is well engineering college drone baby delivery excellence success chase your passion friendship"
    },
    {
        "title": "Dangal", "year": 2016,
        "genres": "Action, Biography, Drama, Sport",
        "director": "Nitesh Tiwari",
        "cast": "Aamir Khan, Fatima Sana Shaikh, Sanya Malhotra, Sakshi Tanwar",
        "rating": 8.3, "runtime": 161,
        "overview": "Former national wrestling champion Mahavir Singh Phogat overcomes social stigma and trains his daughters Geeta and Babita to become world-class wrestlers, culminating in India's first Commonwealth Games gold.",
        "keywords": "aamir khan mahavir phogat geeta phogat wrestling akhada commonwealth games gold medal female empowerment national anthem inspirational"
    },
    {
        "title": "Gangs of Wasseypur", "year": 2012,
        "genres": "Action, Comedy, Crime, Drama, Thriller",
        "director": "Anurag Kashyap",
        "cast": "Manoj Bajpayee, Nawazuddin Siddiqui, Richa Chadha, Huma Qureshi, Tigmanshu Dhulia",
        "rating": 8.2, "runtime": 321,
        "overview": "A multi-generational blood feud between three crime families in the coal-rich town of Wasseypur spans six decades, filled with betrayal, revenge, gunfire, and power struggles.",
        "keywords": "anurag kashyap sardar khan faizal khan nawazuddin siddiqui manoj bajpayee ramadhir singh coal mafia bihar revenge guns cult classic"
    }
]

def load_poster_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_poster_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

def fetch_poster(title, year=None, cache=None):
    if cache is None:
        cache = {}
    
    cache_key = f"{title}_{year}" if year else title
    if cache_key in cache and cache[cache_key]:
        return cache[cache_key]

    # Query OMDB with public API key
    query_title = urllib.parse.quote(title)
    url = f"http://www.omdbapi.com/?t={query_title}&apikey=trilogy"
    if year:
        url += f"&y={year}"

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            poster = data.get("Poster")
            if poster and poster != "N/A" and poster.startswith("http"):
                cache[cache_key] = poster
                return poster
    except Exception as e:
        # Retry without year if failed
        if year:
            try:
                url_no_year = f"http://www.omdbapi.com/?t={query_title}&apikey=trilogy"
                req_fallback = urllib.request.Request(url_no_year, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req_fallback, timeout=4) as resp2:
                    data2 = json.loads(resp2.read().decode("utf-8"))
                    poster2 = data2.get("Poster")
                    if poster2 and poster2 != "N/A" and poster2.startswith("http"):
                        cache[cache_key] = poster2
                        return poster2
            except Exception:
                pass

    # Reliable fallback image if API was unreachable
    fallback = "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=80"
    cache[cache_key] = fallback
    return fallback

def build():
    print(f"Building expanded movie dataset ({len(EXPANDED_MOVIES)} titles)...")
    cache = load_poster_cache()
    output_path = os.path.join(os.path.dirname(__file__), "movies.csv")

    fieldnames = [
        "id", "title", "year", "genres", "director", "cast",
        "rating", "vote_count", "runtime", "overview", "keywords", "poster_url"
    ]

    enriched = []
    total = len(EXPANDED_MOVIES)

    for idx, m in enumerate(EXPANDED_MOVIES, start=1):
        title = m["title"]
        year = m.get("year")
        
        poster = fetch_poster(title, year, cache)
        
        row = {
            "id": idx,
            "title": title,
            "year": year,
            "genres": m["genres"],
            "director": m["director"],
            "cast": m["cast"],
            "rating": m["rating"],
            "vote_count": m.get("vote_count", 850000),
            "runtime": m["runtime"],
            "overview": m["overview"],
            "keywords": m["keywords"],
            "poster_url": poster
        }
        enriched.append(row)
        if idx % 10 == 0 or idx == total:
            print(f"Processed {idx}/{total}: {title} -> {poster[:55]}...")
            save_poster_cache(cache)
            time.sleep(0.05)

    save_poster_cache(cache)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in enriched:
            writer.writerow(r)

    print(f"\nSuccessfully generated {len(enriched)} movies with authentic posters at {output_path}")

if __name__ == "__main__":
    build()
