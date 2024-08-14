def count_char_frequency(input_string):
    # Create an empty dictionary to store character frequencies
    frequency_dict = {}

    # Iterate over each character in the string
    for char in input_string:
        # If the character is already in the dictionary, increment its count
        if char in frequency_dict:
            frequency_dict[char] += 1
        # Otherwise, add the character to the dictionary with a count of 1
        else:
            frequency_dict[char] = 1

    return frequency_dict

# Get input from user
input_string = input("\n If input string is the contents of a file,\n What is the files path? \n Otherwise input string here. \n ")
try:
    with open(input_string, 'r') as file:
        input_string = file.read()
except FileNotFoundError:
    print(f"Error: The file at {input_string} was not found.")
    print(" Assuming input is the desired input_string ")

    # Get the frequency of each character
frequency = count_char_frequency(input_string)

    # Print the frequency of each character
for char, count in frequency.items():
    print(f"Character: '{char}', Frequency: {count}")
