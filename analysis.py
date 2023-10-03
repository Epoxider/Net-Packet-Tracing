import pandas as pd

df = pd.read_csv('youtube_route.csv')

# sum up the total distance traveled
total_distance = df['distance_miles'].sum()
print(f'Total distance traveled: {total_distance} miles')

# get the average distance traveled per hop
avg_distance = df['distance_miles'].mean()
print(f'Average distance traveled per hop: {avg_distance} miles')

# get the average time per hop
avg_time = df['avg_ms'].mean()
print(f'Average time per hop: {avg_time} ms')

# print the set of cities in order of visit
cities = df['city'].tolist()
print(f'Cities visited: {cities}')

# print the set of countries
countries = set(df['country'])
print(f'Countries visited: {countries}')

# print the set of organizations
organizations = set(df['org'])
print(f'Organizations visited: {organizations}')


