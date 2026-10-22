"""Story content for OurWorld: townsfolk, chapters, quests, dialogue, stickers.

Pure data (no pygame). Rules that use it live in core/story.py.

Premise: Willowby used to glow every autumn at the Festival of Lights, when the
great Wish Lantern on Lantern Hill was lit. One year the lantern went dark, and
the town slowly got sleepy and gray. You and your pet have just moved in.
Mayor Maple believes the lantern runs on friendship: help each of the six
townsfolk and they will each give you a Spark. Six Sparks relight the lantern.

Text placeholders: {pet} = the pet's name.
"""

TOWN = "Willowby"

# --------------------------------------------------------------- townsfolk
# kind drives the code-drawn sprite (see sprites/npc_sprite.py)
NPCS = {
    "mayor":  {"name": "Mayor Maple", "kind": "tortoise", "color": (120, 170, 90),
               "location": "town_square", "title": "the town's kind old mayor"},
    "sweetie": {"name": "Sweetie", "kind": "bunny", "color": (250, 170, 200),
                "location": "sweeties_candy_shop", "title": "runs the candy shop"},
    "gen":    {"name": "Gen", "kind": "hedgehog", "color": (170, 120, 80),
               "location": "gens_garden", "title": "the gardener"},
    "pete":   {"name": "Pixel Pete", "kind": "raccoon", "color": (140, 140, 160),
               "location": "arcade", "title": "arcade champion (retired)"},
    "quack":  {"name": "Captain Quack", "kind": "duck", "color": (250, 240, 200),
               "location": "pond", "title": "keeper of the pond"},
    "olive":  {"name": "Olive", "kind": "owl", "color": (150, 110, 170),
               "location": "library", "title": "the librarian"},
    "coco":   {"name": "Coco", "kind": "cat", "color": (240, 160, 90),
               "location": "spa", "title": "spa owner"},
    "fern":   {"name": "Fern", "kind": "fox", "color": (230, 120, 60),
               "location": "willow_woods", "title": "explorer and sticker collector"},
}

# ---------------------------------------------------------------- chapters
START_UNLOCKED = ("home", "backyard", "park", "town_square")

CHAPTERS = [
    {"id": 1, "title": "A Sleepy Town",
     "summary": "You just moved to Willowby. Everything is gray and quiet. Meet the Mayor.",
     "unlock": ["sweeties_candy_shop", "gens_garden"], "outro": "ch1_end"},
    {"id": 2, "title": "Sweet and Green",
     "summary": "Sweetie and Gen have lost their sparkle. Can you cheer them up?",
     "unlock": ["arcade", "pond"], "outro": "ch2_end"},
    {"id": 3, "title": "Fun and Splash",
     "summary": "The arcade is silent and the pond is empty. Bring back the fun!",
     "unlock": ["library", "spa", "willow_woods"], "outro": "ch3_end"},
    {"id": 4, "title": "Quiet and Cozy",
     "summary": "Olive lost a book, and Coco has nobody to pamper.",
     "unlock": ["lantern_hill"], "outro": "ch4_end"},
    {"id": 5, "title": "Festival of Lights",
     "summary": "Six Sparks are glowing. Climb Lantern Hill and light the Wish Lantern!",
     "unlock": [], "outro": None},
]
FINAL_CHAPTER = 5
SPARKS_NEEDED = 6

# ----------------------------------------------------------------- quests
# step: {"event": "<kind>:<key>", "count": n, "text": ...}
#   key "*" matches anything; optional "at": location; optional "min_score".
# step: {"cond": "bond"|"stickers"|"sparks", "count": n, "text": ...}
# "auto": accepted without talking; "auto_turn_in": rewarded the moment it's done.
QUESTS = {
    "welcome": {
        "chapter": 1, "giver": "mayor", "title": "Hello, Willowby!", "auto": True,
        "desc": "Settle in, then say hi to Mayor Maple in the Town Square.",
        "steps": [
            {"event": "care:feed", "count": 1, "text": "Feed {pet}"},
            {"event": "care:play", "count": 1, "text": "Play with {pet}"},
            {"event": "travel:town_square", "count": 1, "text": "Walk to the Town Square"},
        ],
        "reward": {"coins": 20, "sticker": "town_key", "bond": 15},
    },
    "park_laughs": {
        "chapter": 1, "giver": "mayor", "title": "Laughter in the Park", "after": ["welcome"],
        "desc": "The park has been so quiet. Fill it with giggles!",
        "steps": [
            {"event": "care:play", "at": "park", "count": 2, "text": "Play at the Park"},
            {"event": "care:rest", "at": "home", "count": 1, "text": "Take a cozy nap at Home"},
        ],
        "reward": {"coins": 15, "sticker": "picnic", "bond": 15},
    },
    "sweet_tooth": {
        "chapter": 2, "giver": "sweetie", "title": "A Sweet Hello",
        "desc": "Nobody visits Sweetie's shop anymore. Be her first customer in ages!",
        "steps": [
            {"event": "buy:*", "at": "sweeties_candy_shop", "count": 2, "text": "Buy 2 treats at Sweetie's"},
            {"event": "care:feed", "count": 1, "text": "Share a snack with {pet}"},
        ],
        "reward": {"coins": 10, "spark": "sweet", "sticker": "lollipop", "bond": 20},
    },
    "green_thumb": {
        "chapter": 2, "giver": "gen", "title": "Green Thumbs",
        "desc": "Gen wants to see a garden bloom again. Plant seeds and grow them.",
        "steps": [
            {"event": "plant:*", "count": 2, "text": "Plant 2 seeds in the Backyard"},
            {"event": "harvest:*", "count": 2, "text": "Harvest 2 grown plants"},
        ],
        "reward": {"items": {"flower_seeds": 2}, "spark": "bloom", "sticker": "sprout", "bond": 20},
        "gift": {"flower_seeds": 2},   # given when accepted, so nobody gets stuck
    },
    "arcade_champ": {
        "chapter": 3, "giver": "pete", "title": "Insert Coin",
        "desc": "Pixel Pete wants to hear the arcade beep and boop again.",
        "steps": [
            {"event": "game:*", "count": 2, "text": "Play 2 arcade games"},
            {"event": "game:*", "min_score": 40, "count": 1, "text": "Score 40+ in any game"},
        ],
        "reward": {"coins": 25, "spark": "joy", "sticker": "joystick", "bond": 20},
    },
    "duck_day": {
        "chapter": 3, "giver": "quack", "title": "Splash Day",
        "desc": "Captain Quack misses swimmers. Make some waves!",
        "steps": [
            {"event": "place:swim", "count": 2, "text": "Swim at Sunny Pond twice"},
            {"event": "care:play", "at": "pond", "count": 1, "text": "Play on the beach"},
        ],
        "reward": {"coins": 15, "spark": "splash", "sticker": "shell", "bond": 20},
    },
    "lost_book": {
        "chapter": 4, "giver": "olive", "title": "The Lost Storybook",
        "desc": "Olive's favorite storybook blew away into Willow Woods.",
        "steps": [
            {"event": "place:explore", "count": 1, "text": "Search Willow Woods for the book"},
            {"event": "place:read", "count": 2, "text": "Read stories at the Library"},
        ],
        "reward": {"coins": 15, "spark": "wisdom", "sticker": "storybook", "bond": 20},
    },
    "spa_day": {
        "chapter": 4, "giver": "coco", "title": "Bubble Trouble",
        "desc": "Coco's spa is spotless and empty. Treat {pet} to a spa day!",
        "steps": [
            {"event": "place:pamper", "count": 1, "text": "Get pampered at the Spa"},
            {"event": "care:clean", "count": 1, "text": "Give {pet} a bath"},
        ],
        "reward": {"coins": 20, "spark": "calm", "sticker": "bubbles", "bond": 20},
        "gift": {"coins": 18},          # first pamper is on the house
    },
    "fern_hunt": {
        "chapter": 4, "giver": "fern", "title": "Sticker Scout", "side": True,
        "desc": "Fern collects stickers. Find some in the woods and show her!",
        "steps": [
            {"event": "place:explore", "count": 3, "text": "Explore Willow Woods 3 times"},
            {"cond": "stickers", "count": 8, "text": "Own 8 stickers"},
        ],
        "reward": {"coins": 30, "sticker": "fox", "bond": 10},
    },
    "light_lantern": {
        "chapter": 5, "giver": "mayor", "title": "Light the Wish Lantern", "auto_turn_in": True,
        "desc": "Climb Lantern Hill with all six Sparks and best-friend-level love.",
        "steps": [
            {"cond": "bond", "count": 4, "text": "Reach Bond level 4 with {pet}"},
            {"event": "travel:lantern_hill", "count": 1, "text": "Climb Lantern Hill"},
            {"event": "place:light", "count": 1, "text": "Light the Wish Lantern"},
        ],
        "reward": {"coins": 50, "sticker": "lantern", "bond": 30},
    },
    "festival_prep": {
        "chapter": 5, "giver": "mayor", "title": "Dress Up Your Home", "side": True,
        "desc": "Everyone decorates for the festival. Will you?",
        "steps": [{"event": "decorate:*", "count": 1, "text": "Decorate your home with flowers"}],
        "reward": {"coins": 20, "sticker": "bunting", "bond": 10},
    },
}
QUEST_ORDER = list(QUESTS)

SPARKS = {
    "sweet": ("Sweet Spark", (250, 140, 190)), "bloom": ("Bloom Spark", (120, 210, 110)),
    "joy": ("Joy Spark", (250, 200, 70)), "splash": ("Splash Spark", (90, 180, 240)),
    "wisdom": ("Wisdom Spark", (170, 120, 220)), "calm": ("Calm Spark", (250, 170, 120)),
}

# --------------------------------------------------------------- stickers
# shape + color are drawn in code (ui/icons.py sticker()).
STICKERS = {
    "town_key": ("Key to Willowby", "key", (240, 200, 70)),
    "picnic": ("Picnic Blanket", "check", (230, 80, 90)),
    "lollipop": ("Swirly Lollipop", "swirl", (250, 120, 180)),
    "sprout": ("Tiny Sprout", "leaf", (90, 190, 90)),
    "joystick": ("Golden Joystick", "star", (250, 200, 60)),
    "shell": ("Pond Shell", "shell", (250, 200, 180)),
    "storybook": ("Storybook", "book", (150, 100, 190)),
    "bubbles": ("Bubble Bath", "bubbles", (140, 210, 250)),
    "fox": ("Fern's Fox Badge", "fox", (230, 120, 60)),
    "lantern": ("Wish Lantern", "lantern", (255, 190, 80)),
    "bunting": ("Festival Bunting", "flag", (120, 170, 250)),
    # found while exploring Willow Woods
    "acorn": ("Lucky Acorn", "acorn", (170, 110, 60)),
    "mushroom": ("Spotty Mushroom", "mushroom", (230, 70, 70)),
    "feather": ("Blue Feather", "feather", (90, 150, 240)),
    "pinecone": ("Pinecone", "pinecone", (140, 90, 50)),
    "ladybug": ("Ladybug", "ladybug", (220, 50, 50)),
    "rainbow": ("Rainbow Leaf", "leaf", (250, 150, 60)),
    "firefly": ("Firefly", "star", (220, 250, 120)),
    "daily_star": ("Daily Star", "star", (120, 220, 250)),
    # round 4: calendar events, weekly challenge, fishing
    "pumpkin": ("Fair Pumpkin", "pumpkin", (240, 130, 40)),
    "snowman": ("Snow Pal", "snowman", (150, 190, 230)),
    "egg": ("Painted Egg", "egg", (250, 150, 200)),
    "sun": ("Summer Sun", "sun", (250, 200, 50)),
    "trophy": ("Weekly Champ", "trophy", (240, 190, 50)),
    "angler": ("Ace Angler", "fish", (90, 160, 230)),
}
EVENT_STICKERS = ["pumpkin", "snowman", "egg", "sun"]
WOODS_STICKERS = ["acorn", "mushroom", "feather", "pinecone", "ladybug", "rainbow", "firefly"]

# ---------------------------------------------------------------- bond
BOND_LEVELS = [0, 25, 60, 110, 180, 270, 380, 520]
BOND_TITLES = ["New Friends", "Pals", "Buddies", "Best Buddies", "Super Pals",
               "Soul Pals", "Legendary Pals", "Forever Friends"]
BOND_XP = {"care": 2, "place": 3, "game": 2, "buy": 1, "plant": 2, "harvest": 2,
           "decorate": 5, "travel": 0, "fish": 2, "furnish": 1}

# ------------------------------------------------------------ daily wishes
# Unlocked once the arcade opens (chapter 3+). 3 per calendar day.
DAILY_POOL = [
    {"id": "feed3", "event": "care:feed", "count": 3, "text": "Feed {pet} 3 times", "needs": "home"},
    {"id": "play_park", "event": "care:play", "at": "park", "count": 2, "text": "Play at the Park twice", "needs": "park"},
    {"id": "swim", "event": "place:swim", "count": 1, "text": "Go for a swim", "needs": "pond"},
    {"id": "games2", "event": "game:*", "count": 2, "text": "Play 2 arcade games", "needs": "arcade"},
    {"id": "harvest", "event": "harvest:*", "count": 1, "text": "Harvest a plant", "needs": "backyard"},
    {"id": "read", "event": "place:read", "count": 1, "text": "Read a story", "needs": "library"},
    {"id": "explore", "event": "place:explore", "count": 2, "text": "Explore the woods twice", "needs": "willow_woods"},
    {"id": "treat", "event": "buy:*", "count": 1, "text": "Buy something nice", "needs": "sweeties_candy_shop"},
    {"id": "clean2", "event": "care:clean", "count": 2, "text": "Bath time, twice", "needs": "home"},
    {"id": "score60", "event": "game:*", "min_score": 60, "count": 1, "text": "Score 60+ in a game", "needs": "arcade"},
]
DAILY_COUNT = 3
DAILY_REWARD = {"coins": 15, "bond": 5}
DAILY_ALL_BONUS = {"coins": 20, "sticker": "daily_star"}

# --------------------------------------------------------------- dialogue
# Each entry: list of (speaker, text). speaker: npc id, "pet", or "" (narrator).
DIALOGUE = {
    "intro": [
        ("", "Welcome to Willowby! You and {pet} just moved into a little house here."),
        ("", "Long ago, the Wish Lantern on Lantern Hill lit up the whole town every autumn."),
        ("", "But the lantern went dark, and Willowby got sleepy and gray."),
        ("pet", "{pet} looks around and wiggles. This place needs some fun!"),
        ("", "Take care of {pet}, then walk to the Town Square to meet the Mayor."),
        ("", "Tip: press X (Shift / I) to open your Journal any time."),
    ],
    "welcome_done": [
        ("mayor", "Oh my! New neighbors! I am Mayor Maple. Slowly... but warmly... welcome."),
        ("mayor", "See that dark hill? The Wish Lantern runs on friendship, you know."),
        ("mayor", "Help six friends in town, and each will give you a Spark."),
        ("mayor", "Six Sparks will light the lantern again. Here's the Key to Willowby!"),
    ],
    "park_laughs_offer": [
        ("mayor", "Before anything else... the park. It hasn't heard a giggle in years."),
        ("mayor", "Play there a little, and then rest at home. A good day needs both."),
    ],
    "park_laughs_busy": [("mayor", "Play at the Park, then nap at home. No rush. I never rush.")],
    "park_laughs_done": [
        ("mayor", "I heard laughing all the way from here! My shell is tingling."),
        ("mayor", "You're ready to meet more folks. Sweetie's shop and Gen's Garden are open!"),
    ],
    "ch1_end": [
        ("", "Chapter 1 complete! New places on the map: Sweetie's and Gen's Garden."),
        ("", "Chapter 2: Sweet and Green begins."),
    ],
    "sweet_tooth_offer": [
        ("sweetie", "A customer?! Oh! Hi! Sorry, I haven't seen anyone in forever."),
        ("sweetie", "Would you buy two treats? It would make my whole week!"),
    ],
    "sweet_tooth_busy": [("sweetie", "Two treats, and share a snack with {pet}! Yum yum!")],
    "sweet_tooth_done": [
        ("sweetie", "My shop feels alive again! Thank you, thank you!"),
        ("sweetie", "Here, take this. It's warm and pink... a Sweet Spark!"),
    ],
    "green_thumb_offer": [
        ("gen", "Hmph. Nothing grows when nobody's around to see it."),
        ("gen", "Here are two seeds, free. Plant them in your backyard."),
        ("gen", "Come back when you've harvested two plants. They grow while you play."),
    ],
    "green_thumb_busy": [("gen", "Plant, wait, harvest. Plants don't like to be rushed. Neither do I.")],
    "green_thumb_done": [
        ("gen", "Well, look at that. Real flowers. I might even... smile."),
        ("gen", "*smiles* Take the Bloom Spark. And a few more seeds."),
    ],
    "ch2_end": [
        ("", "Chapter 2 complete! The Arcade and Sunny Pond are open."),
        ("", "Chapter 3: Fun and Splash begins."),
    ],
    "arcade_champ_offer": [
        ("pete", "Psst. Kid. You hear that? Nothing. No beeps. No boops."),
        ("pete", "Play two games, and score 40 or more in one. Show me you've got it!"),
    ],
    "arcade_champ_busy": [("pete", "Two games, one score of 40+. Any cabinet. I believe in you!")],
    "arcade_champ_done": [
        ("pete", "HIGH SCORE! Oh, I've missed that sound."),
        ("pete", "You earned this Joy Spark, champ. Don't spend it all at once!"),
    ],
    "duck_day_offer": [
        ("quack", "Ahoy! Captain Quack here. My pond's been lonelier than a lost sock."),
        ("quack", "Swim twice and play on the beach. Make some waves!"),
    ],
    "duck_day_busy": [("quack", "Two swims and some beach games, matey! Splish splash!")],
    "duck_day_done": [
        ("quack", "Now THAT is a proper splash! The ducklings are cheering!"),
        ("quack", "Here's a Splash Spark. Found it at the bottom of the pond."),
    ],
    "ch3_end": [
        ("", "Chapter 3 complete! The Library, the Spa and Willow Woods are open."),
        ("", "Chapter 4: Quiet and Cozy begins."),
    ],
    "lost_book_offer": [
        ("olive", "Hoo... hello. Sorry, I'm a little sad today."),
        ("olive", "The wind blew my favorite storybook into Willow Woods."),
        ("olive", "Could you look for it? And maybe read a few stories with me after?"),
    ],
    "lost_book_busy": [("olive", "The book is somewhere in Willow Woods. Then let's read together!")],
    "lost_book_done": [
        ("olive", "My book! You found it! Hoo-ray!"),
        ("olive", "Reading together is the best. Please take this Wisdom Spark."),
    ],
    "spa_day_offer": [
        ("coco", "Welcome, darling! My spa is sparkling... and totally empty. Meow."),
        ("coco", "Here's 18 coins so {pet}'s first pampering is my treat. And a bath, too!"),
    ],
    "spa_day_busy": [("coco", "One pampering, one bath. Fluffy and fabulous!")],
    "spa_day_done": [
        ("coco", "Look at that shine! {pet} is simply glowing."),
        ("coco", "Speaking of glowing... here is a Calm Spark."),
    ],
    "fern_hunt_offer": [
        ("fern", "Hey! I'm Fern. I find stickers hidden all over these woods!"),
        ("fern", "Explore three times and get your collection to eight. Then show me!"),
    ],
    "fern_hunt_busy": [("fern", "Keep exploring! Stickers hide under leaves and logs.")],
    "fern_hunt_done": [
        ("fern", "Eight stickers! You're a real scout now."),
        ("fern", "Take my Fox Badge. Only the best scouts get one!"),
    ],
    "ch4_end": [
        ("", "Chapter 4 complete! You have all six Sparks."),
        ("", "Lantern Hill is open. Chapter 5: Festival of Lights begins!"),
    ],
    "light_lantern_offer": [
        ("mayor", "Six Sparks! I knew you could do it."),
        ("mayor", "The lantern listens to friendship. Make sure you and {pet} are very close."),
        ("mayor", "Then climb Lantern Hill and light it. The whole town will be watching!"),
    ],
    "light_lantern_busy": [("mayor", "Bond level 4, then Lantern Hill. Slowly, steadily... you've got this.")],
    "festival_prep_offer": [("mayor", "Oh, and everyone dresses up for the festival. Decorate your home!")],
    "festival_prep_busy": [("mayor", "Five flowers make a lovely decoration. Grow some in your backyard.")],
    "festival_prep_done": [("mayor", "Your home looks wonderful! Here's some bunting. Very festive.")],
    "ending": [
        ("", "The six Sparks float up into the Wish Lantern..."),
        ("", "...and it bursts into warm golden light!"),
        ("", "All over Willowby, windows light up. Music starts. Everybody comes outside."),
        ("mayor", "The Festival of Lights is back! And it's all thanks to you and {pet}."),
        ("sweetie", "Free lollipops for everyone!"),
        ("pete", "Best. Night. Ever."),
        ("pet", "{pet} does a happy spin under the lantern."),
        ("", "Willowby is awake again. But there is always more to do..."),
        ("", "New: Daily Wishes! Check your Journal each day for things townsfolk would love."),
    ],
    # idle chatter (rotates)
    "mayor_idle": [[("mayor", "Willowby wasn't built in a day. Neither was my shell.")],
                   [("mayor", "Remember to rest. Even mayors need naps.")]],
    "sweetie_idle": [[("sweetie", "Candy apples are crunchy AND fruity. Best of both!")],
                     [("sweetie", "Come back any time! Sweet dreams!")]],
    "gen_idle": [[("gen", "Sunflowers take longer, but they pay better.")],
                 [("gen", "Water? Nah. Patience is the secret.")]],
    "pete_idle": [[("pete", "Tip: in Pet Pairs, remember where you saw things. Duh.")],
                  [("pete", "Brick Bop tip: hit the ball with the edge of the paddle to aim!")]],
    "quack_idle": [[("quack", "A clean pet is a happy pet. A wet pet is a happier pet!")],
                   [("quack", "The sand gets everywhere. EVERYWHERE.")]],
    "olive_idle": [[("olive", "A story a day keeps the grumpies away.")],
                   [("olive", "Shh... the books are sleeping. Just kidding! Hoo hoo.")]],
    "coco_idle": [[("coco", "Self-care is pet-care, darling.")],
                  [("coco", "Purr. Everything is better after a bubble bath.")]],
    "fern_idle": [[("fern", "Some stickers only show up after lots of exploring!")],
                  [("fern", "I once found a firefly sticker. It glowed for a week!")]],
    "post_idle": [[("", "{name} smiles. \"The whole town feels brighter now!\"")]],
    "locked": [("", "That place is still sleepy. Keep helping the townsfolk to wake it up!")],
}

# growth stage dialogue (round 4)
from .pets import GROW_DIALOGUE as _GROW  # noqa: E402
for _k, _v in _GROW.items():
    DIALOGUE["grow_" + _k] = _v

# furniture handed over with some quest rewards (round 4, core/furniture.py)
from .furniture import QUEST_FURNITURE as _QF  # noqa: E402
for _q, _f in _QF.items():
    QUESTS[_q]["reward"]["furniture"] = _f
