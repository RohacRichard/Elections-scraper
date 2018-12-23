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

	table_ID = ["t1", "t2", "t3"]

	for table in table_ID:
		td_header = ("{0}sa1 {0}sb1".format(table))

		for td in soup.find_all("td", {"class":"cislo", "headers":td_header}):

			for a in td.contents:
				new_link = "https://volby.cz/pls/ps2017nss/{}".format(a["href"])

				# A check whether there is a same URL already in list.
				if new_link not in generated_links:
					generated_links.append(new_link)
				else:
					continue

	return generated_links


def create_header(soup):
	"""Function creates header, takes soup as argument."""

	# Defined header, to which we will append polit. parties.
	header = ["Code", "Location", "Registered", "Envelopes", "Valid"]

	# The empty class attribute fixes problem with empty table row.
	party_name_1 = soup.find_all("td", {"class":"", "headers":"t1sa1 t1sb2"})
	for name_1 in party_name_1:
		header.append(name_1.contents[0])

	party_name_2 = soup.find_all("td", {"class":"", "headers":"t2sa1 t2sb2"})
	for name_2 in party_name_2:
		header.append(name_2.contents[0])	

	return header


def get_code(link):
	"""Gets the code of municipality from URL, takes gen. link as argument."""

	# Had to help myself here a bit with RegEx module.
	for index, position in enumerate(re.finditer("=", link)):
		if index == 2:
			equals_index = position.start()
			return link[equals_index + 1:equals_index + 7]


def get_name(soup):
	"""Gets the municipality name, takes soup as argument."""

	location_div = soup.find_all("div", {"id":"publikace", "class":"topline"})
	location_h3 = location_div[0].find_all("h3")
	location = ((location_h3[2].contents))[0].strip()
	return location[6:]


def get_voter_info(soup):
	"""Gets info about voters in municipality, takes soup as argument."""

	voters_table = soup.find("table", {"id":"ps311_t1"})
	voters_tr = voters_table.find_all("tr")

	voter_info = []

	for index, voters_td in enumerate(voters_tr[2].find_all("td")):
		if index == 3:
			voter_info.append((voters_td.contents)[0].strip())
		elif index == 4:
			voter_info.append((voters_td.contents)[0].strip())
		elif index == 7:
			voter_info.append((voters_td.contents)[0].strip())

	return voter_info


def get_votes(soup):
	"""Gets info votes for polit. parties, takes soup as argument."""

	votes_info = []

	party_votes_1 = soup.find_all("td", {"class":"cislo", "headers":"t1sa2 t1sb3"})
	for votes_1 in party_votes_1:
		votes_info.append(votes_1.contents[0])

	party_votes_2 = soup.find_all("td", {"class":"cislo", "headers":"t2sa2 t2sb3"})
	for votes_2 in party_votes_2:
		votes_info.append(votes_2.contents[0])

	return votes_info


def process_links(generated_link):
	"""Scrapes and parses generated links.
	Takes the list of generated links as argument."""

	# In this list assemble the final table of data and header.
	final_table = []

	for loop, link in enumerate(generated_link):	

		request = requests.get(link)
		soup = BS(request.text, "html.parser")

		# I assign return of function get_name to variable to avoid calling it twice.
		municip_name = get_name(soup)
		print("Scraping municipality: {}".format(municip_name))

		row = []

		# In first loop we create the header with polit. parties.
		if loop == 0:
			final_table.append(create_header(soup))

		# Function calls other functions to assemble the row.
		row.append(get_code(link))
		row.append(municip_name)

		# Here we have lists as function returns, so we have to unpack them.
		for voter_data in get_voter_info(soup):
			row.append(voter_data)

		for votes_data in get_votes(soup):
			row.append(votes_data)

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


def main():
	"""The main function, contains all other functions.
	Takes no arguments."""
	
	greeting()

	# The link with desired district.
	base_link = input("\nPlease enter the base link: ")

	# A filename input system.
	file_name = input("Please enter the name of csv file to be created: ")
	print()

	while os.path.exists(file_name+".csv"):
		overwrite = input("This file already exists! Overwrite? Y/N ")

		if overwrite.lower() == "y":
			print()
			break

		elif overwrite.lower() == "n":
			print()
			file_name = input("Please enter the name of csv file to be created: ")
			print()

		else:
			print("Invalid action. Enter only Y or N.")
			continue

	links = generate_links(base_link)
	proc_links = process_links(links)
	record_data(proc_links, file_name)

	print("="*66)
	print("Finished! You should find your csv file inside current directory.")
	print("Thanks for using my elections scraper, have a nice day :)")
	print("="*66)


main()