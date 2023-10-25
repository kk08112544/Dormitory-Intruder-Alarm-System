import datetime

# Get the current date and time
current_datetime = datetime.datetime.now()

# Format the datetime to include microseconds
formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

# Print the formatted datetime
print("Current Date and Time:", formatted_datetime)