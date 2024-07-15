from datetime import date

months = {
    'January': 1,
    'Jan': 1,
    'Febuary': 2,
    'Feb': 2,
    'March': 3,
    'Mar': 3,
    'April': 4,
    'Apr': 4,
    'May': 5,
    'June': 6,
    'Jun': 6,
    'July': 7,
    'Jul': 7,
    'August': 8,
    'Aug': 8,
    'September': 9,
    'Sep': 9,
    'October': 10,
    'Oct': 10,
    'November': 11,
    'Nov': 11,
    'December': 12,
    'Dec': 12
    }

name = input(" What is your name? ")

YOB = int(input("What is your year of birth? "))

MOB_input = input("What is your month of birth? ").title()
MOB = months.get(MOB_input, None)

if MOB is None:
    print("Invalid month entered. Please enter valid month")
else:
    current_date = date.today()
    age = current_date.year - YOB
    if current_date.month < MOB:
        age -= 1

print(f"Thank you for your input {name}, Your age is currently {age}. ")
