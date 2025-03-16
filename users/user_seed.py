import random
from datetime import datetime, timedelta

from users.models import User


def random_date(start_year=1960, end_year=2010):
    """Generate a random birth date between start_year and end_year."""
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    random_days = random.randint(0, (end_date - start_date).days)
    return start_date + timedelta(days=random_days)


# Possible values for fields
provinces_cities = {
    "Ontario": ["Toronto", "Ottawa", "Mississauga"],
    "Quebec": ["Montreal", "Quebec City", "Laval"],
    "British Columbia": ["Vancouver", "Victoria", "Kelowna"],
    "Alberta": ["Calgary", "Edmonton", "Red Deer"],
    "Manitoba": ["Winnipeg", "Brandon", "Steinbach"],
    "Saskatchewan": ["Regina", "Saskatoon", "Moose Jaw"],
    "Nova Scotia": ["Halifax", "Sydney"],
    "New Brunswick": ["Fredericton", "Saint John", "Moncton"],
    "Newfoundland and Labrador": ["St. John's", "Corner Brook"],
    "Prince Edward Island": ["Charlottetown", "Summerside"],
    "Northwest Territories": ["Yellowknife"],
    "Yukon": ["Whitehorse"],
    "Nunavut": ["Iqaluit"]
}
expertise_levels = ["Beginner", "Intermediate", "Advanced"]
genres = ["Classical", "Jazz", "Blues", "Dance", "Rock", "Traditional",
          "Country", "Latin", "Pop", "EDM", "Experimental", "Funk"]
available_times = [
    "A light commitment for casual collaboration.",
    "A moderate commitment to maintain progress.",
    "A serious commitment to improve and prepare for performances.",
    "A highly dedicated, professional-level commitment."
]
own_song_choices = ["Yes", "No"]
academic_knowledge_choices = ["Yes", "No"]
clothing_styles = [
    "Classic and Formal", "Vintage-Inspired", "Sporty and Active",
    "Urban and Street Style", "Dark and Gothic"
]
instruments = ["Electric Guitar", "Saxophone", "Drums and Percussion", "Violin",
               "Acoustic Guitar", "Piano", "Cello", "Flute"]
genders = ["Male", "Female"]

# List of first and last names for random selection
first_names = ["John", "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "James", "Isabella"]
last_names = ["Smith", "Johnson", "Brown", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin"]


# Number of users to create
num_users = 300
users = []
counter = 1

for _ in range(num_users):
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    province = random.choice(list(provinces_cities.keys()))
    city = random.choice(provinces_cities[province])
    username = f"{first_name.lower()}{counter}"  # Ensure uniqueness
    counter += 1
    email = f"{username}@example.com"

    users.append(User(
        username=username,
        first_name=first_name,
        last_name=last_name,
        gender=random.choice(genders),
        birth_date=random_date().date(),
        province=province,
        city=city,
        level_of_expertise=random.choice(expertise_levels),
        favorite_genre=random.choice(genres),
        available_time=random.choice(available_times),
        own_song=random.choice(own_song_choices),
        academic_knowledge=random.choice(academic_knowledge_choices),
        preferred_clothing=random.choice(clothing_styles),
        preferred_instrument=random.choice(instruments),
        personality_social=random.choice(["E", "I"]),
        personality_detail=random.choice(["N", "S"]),
        decision_making=random.choice(["T", "F"]),
        planning_style=random.choice(["J", "P"])
    ))

# Bulk create users (faster performance)
User.objects.bulk_create(users)

# Set password separately to avoid hashing multiple times
for user in User.objects.all():
    user.set_password("test123")
    user.save()

print(f"{num_users} users have been created successfully.")
