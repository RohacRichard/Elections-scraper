import requests
from bs4 import BeautifulSoup as BS
import re
import os
import csv


def greeting():
	"""Greets the user. Takes no arguments."""
	print()
	print("="*46)
	print("Hello, welcome to my elections scraper project.")
	print("="*46)


def generate_links(base_link):
	"""Generates links with the results of municipalities to iterate over.
	Takes the base link from user input as argument"""

	generated_links = []

	request = requests.get(base_link)
	soup = BS(request.text, "html.parser")

	for link in soup.find_all('a', href=True):

		if "vyber" in link["href"]:
			new_link = "https://volby.cz/pls/ps2017nss/{}".format(link["href"])

			# There can be a same URL more than once on a page.
			# This way it is prevented from appending URL that's already in list.
			if new_link not in generated_links:
				generated_links.append(new_link)
			else:
				continue

	return generated_links


def process_links(generated_link):
	"""Scrapes and parses generated links.
	Takes the list of generated links as argument."""

	# Defined header, to which we will append polit. parties.
	header = ["Code", "Location", "Registered", "Envelopes", "Valid"]

	# Here we assemble the final table of data and header.
	final_table = []

	for loop, link in enumerate(generated_link, 1):

		print("Scraping link number: {}".format(loop))

		request = requests.get(link)
		soup = BS(request.text, "html.parser")

		row = []

		# Getting the code of municipality from URL.
		# Had to help myself here a bit with RE module.

		for index, position in enumerate(re.finditer("=", link)):
			if index == 2:
				equals_index = position.start()
				row.append(link[equals_index + 1:equals_index + 7])

		# Getting the municipality name.

		location_div = soup.find_all("div", {"id":"publikace", "class":"topline"})
		location_h3 = location_div[0].find_all("h3")
		location = ((location_h3[2].contents))[0].strip()
		row.append(location[6:])

		# Getting the info about voters in municipality.

		voters_table = soup.find("table", {"id":"ps311_t1"})
		voters_tr = voters_table.find_all("tr")

		for index, voters_td in enumerate(voters_tr[2].find_all("td")):
			if index == 3:
				row.append((voters_td.contents)[0].strip())
			elif index == 4:
				row.append((voters_td.contents)[0].strip())
			elif index == 7:
				row.append((voters_td.contents)[0].strip())

		# Getting info about polit. parties and votes for them.

		# There are two columns with different identification,
		# thus the script below has to do the same thing twice.

		if loop == 1:
			party_name_1 = soup.find_all("td", {"headers":"t1sa1 t1sb2"})
			for name_1 in party_name_1:
				header.append(name_1.contents[0])

			party_name_2 = soup.find_all("td", {"headers":"t2sa1 t2sb2"})
			for name_2 in party_name_2:
				header.append(name_2.contents[0])

			final_table.append(header)

		party_votes_1 = soup.find_all("td", {"headers":"t1sa2 t1sb3"})
		for votes_1 in party_votes_1:
			row.append(votes_1.contents[0])

		party_votes_2 = soup.find_all("td", {"headers":"t2sa2 t2sb3"})
		for votes_2 in party_votes_2:
			row.append(votes_2.contents[0])

		final_table.append(row)

	return final_table


def record_data(processed_data, file_name):
	"""Writes the data into a csv file.
	Takes two arguments, generated list of lists 
	and file name from user input."""

	with open(file_name + ".csv", "w", newline='') as file:
		writer = csv.writer(file)
		writer.writerows(processed_data)
		file.close()


greeting()

# The link with desired district.
base_link = input("\nPlease enter the base link: ")

# A fool-proof filename input system.
name_check = True
while name_check:
	file_name = input("Please enter the name of csv file to be created: ")
	print()

	if os.path.exists(file_name+".csv"):
		overwrite_check = True

		while overwrite_check:
			overwrite = input("This file already exists! Overwrite? Y/N ")

			if overwrite.lower() == "y":
				print()
				name_check = False
				overwrite_check = False

			elif overwrite.lower() == "n":
				print()
				overwrite_check = False

			else:
				print("Invalid action. Enter only Y or N.")
				continue

	else:
		name_check = False


links = generate_links(base_link)
proc_links = process_links(links)
record_data(proc_links, file_name)


print("="*66)
print("Finished! You should find your csv file inside current directory.")
print("Thanks for using my elections scraper, have a nice day :)")
print("="*66)
