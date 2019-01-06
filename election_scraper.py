import requests
from bs4 import BeautifulSoup as BS
import os
import csv


def greeting():
	"""Greets the user. Takes no arguments."""
	print()
	print("="*46)
	print("Hello, welcome to my elections scraper project.")
	print("="*46)


def generate_links(td_header, soup):
	"""Generates links with the results of municipalities to iterate over.
	Takes the headers and generated soup as arguments."""

	generated_links = []

	for td in soup.find_all("td", {"class":"cislo", "headers":td_header}):
		new_link = "https://volby.cz/pls/ps2017nss/{}".format(td.find("a")["href"])

		# A check whether there is a same URL already in list.
		if new_link not in generated_links: 
			generated_links.append(new_link)

	return generated_links


def get_code(td_header, soup):
	"""Gets the code of municipality.
	Takes the headers and generated soup as arguments."""

	generated_codes = []

	for td in soup.find_all("td", {"class":"cislo", "headers":td_header}):
		muni_code = (td.find("a").contents)[0]

		# A check whether there is a same code already in list.
		if muni_code not in generated_codes: 
			generated_codes.append(muni_code)

	return generated_codes


def get_name(soup):
	"""Gets the municipality name, takes soup as argument."""

	td_header = ["t1sa1 t1sb2", "t2sa1 t2sb2", "t3sa1 t3sb2"]

	generated_names = [td.contents[0] for td 
					   in soup.find_all("td", {"headers":td_header})]

	return generated_names


def base_link_ops(base_link):
	"""A function to contain all operations regarding user-provided link.
	Takes the base link as argument."""

	response = requests.get(base_link)
	soup = BS(response.text, "html.parser")

	td_header = ["t1sa1 t1sb1", "t2sa1 t2sb1", "t3sa1 t3sb1"]

	links = generate_links(td_header, soup)
	codes = get_code(td_header, soup)
	names = get_name(soup)

	return links, codes, names


def create_header(soup):
	"""Function creates header, takes soup as argument."""

	# Defined header, to which we will append polit. parties.
	header = ["Code", "Location", "Registered", "Envelopes", "Valid"]
	td_header = ["t1sa1 t1sb2", "t2sa1 t2sb2"]

	# The empty class attribute fixes problem with empty table row.
	party_name = soup.find_all("td", {"class":"", "headers":td_header})

	party_name_list = [name.contents[0] for name in party_name]	

	return header + party_name_list


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
	"""Gets info about votes for polit. parties, takes soup as argument."""

	td_header = ["t1sa2 t1sb3", "t2sa2 t2sb3"]

	party_votes = soup.find_all("td", {"class":"cislo", "headers":td_header})

	party_votes_list = [votes.contents[0] for votes in party_votes]	

	return party_votes_list


def process_links(base_link, generated_link, codes, names):
	"""Scrapes and parses generated links.
	Takes the base link and base_link_ops function returns as arguments."""

	# In this list we assemble the final table of data and header.
	final_table = []

	for loop, link in enumerate(generated_link):	

		response = requests.get(link)
		soup = BS(response.text, "html.parser")
 
		print("Scraping municipality: {}".format(names[loop]))

		row = []

		# In first loop we create the header with polit. parties.
		if loop == 0:
			final_table.append(create_header(soup))

		row.append(codes[loop])
		row.append(names[loop])

		voter_info_list = [voter_info for voter_info in get_voter_info(soup)]

		votes_data_list = [votes_data for votes_data in get_votes(soup)]

		final_table.append(row + voter_info_list + votes_data_list)

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

	ops_return = base_link_ops(base_link)

	proc_links = process_links(base_link, 
							   ops_return[0], 
							   ops_return[1], 
							   ops_return[2]
							   )

	record_data(proc_links, file_name)

	print("="*66)
	print("Finished! You should find your csv file inside current directory.")
	print("Thanks for using my elections scraper, have a nice day :)")
	print("="*66)


main()
