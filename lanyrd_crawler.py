import urllib2, threading
import lxml, time, sys
from sys import stdout
from lxml import html
from threading import Thread
#=====================================#
# List of conferences : writefile.txt #
# Every conference on new line with   #
# tab separated values		      #
# [0] = conference name		      #
# [1] = date			      #
# [2] = location		      #
# [3] = url			      #
# [4] = speakers		      #
#=====================================#
# Crawler class			      #
#======================================================================#
class Crawler(threading.Thread):
#======================================================================#
	def __init__(self, conf_url, thread_id, writefile, lock):
		threading.Thread.__init__(self)
		self.conf_url = conf_url
		self.thread_id = thread_id
		self.writefile = writefile
		self.lock = lock#Lock()
#======================================================================#
# Crawls the actual conference link and parses data from it and	       #
# writes onto a file						       #
#======================================================================#
	def crawl_conf(self, url):
		try:
			global conf_counter, debug_flag, thread_flag, limit_flag, limit_count

			if limit_flag:
				if conf_counter >= limit_count:
					#raise KeyboardInterrupt()
					writefile.close()
					print "\n\n"+"="*23+"Thank You For Using Lanyrd Crawler"+"="*23
					print separator
					sys.exit("UserInterrupt:Exiting")

			#Opening conference page for parsing
			content = urllib2.urlopen(url).read()
			html = lxml.html.fromstring(content)

			#Check if conference country is USA
			country = html.xpath('//span[@class="place-context"]/a')[0].text
			if country.lower() <> "United States".lower():
				return

			#Extracting conference Summary
			conf_name = html.xpath('//div[@class="primary"]/h1[@class="summary"]')[0].text

			#Extracting conference Date
			start_day = html.xpath('//abbr[@class="dtstart"]/span[@class="day"]')[0].text
			end_day = html.xpath('//abbr[@class="dtend"]/span[@class="day"]')[0].text
			month = html.xpath('//abbr[@class="dtend"]/span[@class="month"]')[0].text
			year = html.xpath('//abbr[@class="dtend"]/span[@class="year"]')[0].text
			date = start_day + " - " + end_day + " " + month + " " + year

			#Extracting conference location
			place = html.xpath('//p[@class="prominent-place"]/a[@class="sub-place"]')[0].text

			#Extracting conference url
			conf_url = html.xpath('//a[@class="icon url website"]')[0].get("href")

			#Extracting Keywords (Tags)
			keywords = []
			k = 0
			flag = True
			while flag:
				try:
					keyword = html.xpath('//div[@id="tagblock"]/ul[@class="tags inline-wrap-tags"]/li/a')[k].text
					keywords.append(keyword.strip())
					k += 1
				except IndexError as ie:
					flag = False
					if debug_flag:
						print "Exception in crawl_conf while retrieveing keywords : " + str(ie)
			keywords = list(set(keywords))

			#Extracting list of speakers in conference
			speakers = []
			c = 0
			flag = True
			while flag:
				try:
					people = html.xpath('//ul[@class="people"]/li/span[@class="name"]/a')[c].text
					speakers.append(people)
					c += 1
				except IndexError as ie:
					flag = False
					if debug_flag:
						print "Exception in crawl_conf while retrieveing speakers : " + str(ie)
			speakers = list(set(speakers))

			conf_list = {}
			conf_list[conf_name] = [date, place, conf_url, speakers]

			conf_counter += 1
			
			if print_flag:
				stdout.write("\rConferences Saved : %i" % (conf_counter))
				stdout.flush()
			else:
				print conf_counter,
				
			if thread_flag:
				self.lock.acquire()
			self.writefile.write(str(conf_name) + delimiter + str(date) + delimiter + str(place) + delimiter + str(conf_url) + delimiter + str(keywords) + delimiter + str(speakers)+"\n")
			if thread_flag:
				self.lock.release()

		except KeyboardInterrupt:
			writefile.close()
			print "\n\n"+"="*23+"Thank You For Using Lanyrd Crawler"+"="*23
			print separator
			sys.exit("UserInterrupt:Exiting")
		except Exception as e:
			if debug_flag:
				print "Exception in crawl_conf : " + str(e)
#======================================================================#
# Run(named as run, in case user wants multithreading) method for      #
# further extraction of links					       #
#======================================================================#
	def run(self):
		try:
			global debug_flag, thread_flag, limit_flag, limit_count
			url = self.conf_url

			#Opening intermediate xml page which contains links to conferences
			content = urllib2.urlopen(url).read()
			html = lxml.html.fromstring(content)
			loc = html.xpath('//loc')

			for url in loc:
				self.crawl_conf(url.text)
				if thread_flag:
					time.sleep(5)

		except KeyboardInterrupt:
			writefile.close()
			print "\n\n"+"="*23+"Thank You For Using Lanyrd Crawler"+"="*23
			print separator
			sys.exit("UserInterrupt:Exiting")
		except Exception as e:
			if debug_flag:
				print "Exception in run : " + str(e)
#======================================================================#
# Crawl method to extract conference links from xml for further parsing#
#======================================================================#
def start_crawl():
	try:
		global writefile, debug_flag, thread_flag, limit_flag, limit_count
		lock = threading.Lock()

		xml_links = []
		content = urllib2.urlopen('http://lanyrd.com/sitemap.xml').read()
		html = lxml.html.fromstring(content)
		loc = html.xpath('//loc')
		for i in loc:
			if i.text.count('conferences'):
				xml_links.append(i.text.strip())

		threads = []
		thread_id = 0
		for url in xml_links:#[:1]:
			thread = Crawler(url, thread_id, writefile, lock)
			if thread_flag == False:
				thread.run()
			else:
				thread.start()
				threads.append(thread)
				thread_id += 1

		if thread_flag:
		#Waiting for all threads to get completed
			for th in threads:
				th.join(5)

		writefile.close()
	except KeyboardInterrupt:
		writefile.close()
		print "\n\n"+"="*23+"Thank You For Using Lanyrd Crawler"+"="*23
		print separator
		sys.exit("UserInterrupt:Exiting")
	except Exception as e:
		if debug_flag:
			print "Exception in crawl : " + str(e)
#======================================================================#
# Main method : Program execution starts here			       #
#======================================================================#
def main():
	global debug_flag, thread_flag, limit_flag, limit_count
	print separator
	print "="*33+"LANYRD CRAWLER"+"="*33
	print separator + "\n"
	debug_choice = raw_input("Run in debug mode(y/n) : ")
	if debug_choice == "y" or debug_choice == "Y":
		debug_flag = True

	threading_choice = raw_input("Run in multi-threading mode(y/n) : ")
	if threading_choice == "y" or debug_choice == "Y":
		thread_flag = True

	limit_choice = raw_input("Limit crawl by number of conferences(y/n) : ")
	if limit_choice == "y" or debug_choice == "Y":
		limit_flag = True

	if limit_flag:
		limit_count = int(raw_input("Enter number of conference to crawl : "))

	print "\nPress Ctrl + c to interrupt and stop crawling\n"
	print "Conferences Saved : ",
	start_crawl()

	print "\n\n"+"="*23+"Thank You For Using Lanyrd Crawler"+"="*23
	print "\n" + separator
#======================================================================#
#GLOBAL VARIABLES													   #
#======================================================================#
writefile = open('conferences.txt', 'w+')
separator = "="*80

#MODIFY THIS STRING TO CHANGE DELIMITER CHARACTER FOR OUTPUT FILE
#THE OUTPUT FILE IS TAB SEPARATED BY DEFAULT
delimiter = '\t'

debug_flag = False
thread_flag = False
limit_flag = False
print_flag = False
if sys.platform.find("linux") == 0:
	print_flag = True
	
limit_count = 0
conf_counter = 0
conf_list = []
#======================================================================#
if __name__ == "__main__":
	main()
#======================================================================#
