"""Famous quotes: investing, AI, discipline, focus, and New York City."""
import random
from datetime import date

QUOTES = [
    # ---------- Investing & Wall Street ----------
    {"text": "The stock market is a device for transferring money from the impatient to the patient.", "author": "Warren Buffett", "tag": "finance"},
    {"text": "Price is what you pay. Value is what you get.", "author": "Warren Buffett", "tag": "finance"},
    {"text": "Risk comes from not knowing what you're doing.", "author": "Warren Buffett", "tag": "finance"},
    {"text": "Someone's sitting in the shade today because someone planted a tree a long time ago.", "author": "Warren Buffett", "tag": "finance"},
    {"text": "The best investment you can make is in yourself.", "author": "Warren Buffett", "tag": "grind"},
    {"text": "Go to bed smarter than when you woke up.", "author": "Charlie Munger", "tag": "grind"},
    {"text": "The big money is not in the buying and selling, but in the waiting.", "author": "Charlie Munger", "tag": "finance"},
    {"text": "The first rule of compounding: never interrupt it unnecessarily.", "author": "Charlie Munger", "tag": "finance"},
    {"text": "Pain + Reflection = Progress.", "author": "Ray Dalio", "tag": "grind"},
    {"text": "He who lives by the crystal ball will eat shattered glass.", "author": "Ray Dalio", "tag": "finance"},
    {"text": "Know what you own, and know why you own it.", "author": "Peter Lynch", "tag": "finance"},
    {"text": "The four most dangerous words in investing are: 'this time it's different.'", "author": "Sir John Templeton", "tag": "finance"},
    {"text": "Work with the smartest people you can, hopefully smarter than you.", "author": "Jim Simons", "tag": "finance"},
    {"text": "Money never sleeps, pal.", "author": "Gordon Gekko, Wall Street", "tag": "nyc"},
    {"text": "Play long-term games with long-term people.", "author": "Naval Ravikant", "tag": "finance"},
    {"text": "Learn to sell. Learn to build. If you can do both, you will be unstoppable.", "author": "Naval Ravikant", "tag": "grind"},
    {"text": "Compound yourself.", "author": "Sam Altman", "tag": "grind"},
    {"text": "Work like there is someone working 24 hours a day to take it all away from you.", "author": "Mark Cuban", "tag": "grind"},
    # ---------- AI, tech & science ----------
    {"text": "AI is the new electricity.", "author": "Andrew Ng", "tag": "ai"},
    {"text": "Neural net training fails silently.", "author": "Andrej Karpathy", "tag": "ai"},
    {"text": "What I cannot create, I do not understand.", "author": "Richard Feynman", "tag": "ai"},
    {"text": "All models are wrong, but some are useful.", "author": "George Box", "tag": "ai"},
    {"text": "In God we trust. All others must bring data.", "author": "W. Edwards Deming", "tag": "ai"},
    {"text": "The best way to predict the future is to invent it.", "author": "Alan Kay", "tag": "ai"},
    {"text": "Software is eating the world.", "author": "Marc Andreessen", "tag": "ai"},
    {"text": "I wish upon you ample doses of pain and suffering.", "author": "Jensen Huang", "tag": "grind"},
    {"text": "When something is important enough, you do it even if the odds are not in your favor.", "author": "Elon Musk", "tag": "grind"},
    {"text": "Stay hungry, stay foolish.", "author": "Steve Jobs", "tag": "grind"},
    {"text": "Your time is limited, so don't waste it living someone else's life.", "author": "Steve Jobs", "tag": "grind"},
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs", "tag": "grind"},
    {"text": "Focus is a matter of deciding what things you're not going to do.", "author": "John Carmack", "tag": "focus"},
    # ---------- Discipline & the grind ----------
    {"text": "Rest at the end, not in the middle.", "author": "Kobe Bryant", "tag": "focus"},
    {"text": "Everything negative - pressure, challenges - is all an opportunity for me to rise.", "author": "Kobe Bryant", "tag": "grind"},
    {"text": "Don't count the days, make the days count.", "author": "Muhammad Ali", "tag": "grind"},
    {"text": "I hated every minute of training, but I said, 'Don't quit. Suffer now and live the rest of your life as a champion.'", "author": "Muhammad Ali", "tag": "focus"},
    {"text": "I fear not the man who has practiced 10,000 kicks once, but I fear the man who has practiced one kick 10,000 times.", "author": "Bruce Lee", "tag": "focus"},
    {"text": "The successful warrior is the average man, with laser-like focus.", "author": "Bruce Lee", "tag": "focus"},
    {"text": "The last three or four reps is what makes the muscle grow.", "author": "Arnold Schwarzenegger", "tag": "focus"},
    {"text": "Discipline equals freedom.", "author": "Jocko Willink", "tag": "focus"},
    {"text": "You do not rise to the level of your goals. You fall to the level of your systems.", "author": "James Clear", "tag": "focus"},
    {"text": "The ability to perform deep work is becoming increasingly rare at exactly the same time it is becoming increasingly valuable in our economy.", "author": "Cal Newport", "tag": "focus"},
    {"text": "Amateurs sit and wait for inspiration, the rest of us just get up and go to work.", "author": "Stephen King", "tag": "focus"},
    {"text": "We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "author": "Will Durant", "tag": "focus"},
    {"text": "Hard work beats talent when talent doesn't work hard.", "author": "Tim Notke", "tag": "grind"},
    {"text": "Be so good they can't ignore you.", "author": "Steve Martin", "tag": "grind"},
    {"text": "Time is the scarcest resource and unless it is managed nothing else can be managed.", "author": "Peter Drucker", "tag": "focus"},
    {"text": "Either you run the day, or the day runs you.", "author": "Jim Rohn", "tag": "focus"},
    {"text": "Champions keep playing until they get it right.", "author": "Billie Jean King", "tag": "grind"},
    {"text": "A year from now you may wish you had started today.", "author": "Karen Lamb", "tag": "grind"},
    {"text": "It always seems impossible until it's done.", "author": "Nelson Mandela", "tag": "grind"},
    {"text": "Grit is passion and perseverance for very long-term goals.", "author": "Angela Duckworth", "tag": "grind"},
    {"text": "Fortune favors the bold.", "author": "Virgil", "tag": "grind"},
    # ---------- New York City ----------
    {"text": "If I can make it there, I'll make it anywhere.", "author": "Frank Sinatra, New York, New York", "tag": "nyc"},
    {"text": "Concrete jungle where dreams are made of, there's nothing you can't do.", "author": "Jay-Z & Alicia Keys, Empire State of Mind", "tag": "nyc"},
    {"text": "I'm not a businessman, I'm a business, man.", "author": "Jay-Z", "tag": "nyc"},
    {"text": "One belongs to New York instantly, one belongs to it as much in five minutes as in five years.", "author": "Thomas Wolfe", "tag": "nyc"},
    {"text": "New York is the only real city-city.", "author": "Truman Capote", "tag": "nyc"},
    {"text": "Wall Street is the only place that people ride to in a Rolls-Royce to get advice from those who take the subway.", "author": "Warren Buffett", "tag": "nyc"},
]

BREAK_TIPS = [
    "Stand up. Walk to the window. Look at something 20 feet away for 20 seconds.",
    "Drink a full glass of water. Your brain is 75% water.",
    "10 push-ups or 20 squats. Blood flow = focus.",
    "No phone scrolling. Let your brain consolidate what you just learned.",
    "Close your eyes and recall the 3 key ideas from the last session.",
    "Stretch your neck, shoulders and wrists. Analysts' posture is real.",
    "Breathe: 4 seconds in, 7 hold, 8 out. Repeat 4 times.",
]


def quote_for(key, tags=None):
    """Stable quote per key per day, so it doesn't change on every rerun."""
    pool = [q for q in QUOTES if not tags or q["tag"] in tags] or QUOTES
    rnd = random.Random(f"{date.today().isoformat()}::{key}")
    return rnd.choice(pool)


def quote_of_the_day():
    return quote_for("quote-of-the-day")


def rotating_quote(slot, tags=None):
    """Quote that changes every time `slot` changes (e.g. every 5 minutes)."""
    pool = [q for q in QUOTES if not tags or q["tag"] in tags] or QUOTES
    return pool[slot % len(pool)]


def break_tip(slot):
    return BREAK_TIPS[slot % len(BREAK_TIPS)]