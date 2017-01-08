# Coursera Dump

Script gets URLs of some random [coursera](https://www.coursera.org/) learning courses pages from [coursera-xml-feed](https://www.coursera.org/sitemap~www~courses.xml), parses them for getting courses information and then outputs all data to xlsx file to desired folder. 

## Requirements
<b>Requests</b> is used  for getting web pages, <b>lxml</b> for parsing xml,  
 <b>BeautifulSoup4</b> for parsing html and <b>openpyxl</b> for xlsx file outputting.   

## Installing
`git clone 
https://github.com/Beastrock/10_coursera.git`  
`pip install -r requirements.txt`

## Launching
`python coursera.py [--courses COURSES] [--output OUTPUT]`  

`--courses`  - random courses amount for to get information about, default value is 20.  

`--output` - absolute folder filepath for outputted file. If the argument is not specified,  
the output file will be put in the script's folder.  

Launching example:  
`python coursera.py --courses 5 --output B:/courses_information`


# Project Goals

The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org)
